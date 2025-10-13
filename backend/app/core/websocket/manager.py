import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from sqlalchemy.orm import Session

from app.api.users.model import User

from .auth import WebSocketAuth, websocket_auth
from .events import event_registry
from .exceptions import EventHandlingError
from .rooms import RoomManager

logger = logging.getLogger(__name__)

CONNECTION_STALE_SECONDS = 300


class ConnectionInfo:
    """Information about an active WebSocket connection."""

    def __init__(
        self,
        websocket: WebSocket,
        user: User,
        session_id: str,
        namespace: str,
        client_ip: str = 'unknown',
    ):
        self.websocket = websocket
        self.user = user
        self.session_id = session_id
        self.namespace = namespace
        self.client_ip = client_ip
        self.connected_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.rooms: Set[str] = set()
        self.metadata: Dict[str, Any] = {}

    @property
    def user_id(self) -> str:
        return str(self.user.id)

    @property
    def is_stale(self) -> bool:
        now = datetime.now(timezone.utc)
        return (now - self.last_activity).total_seconds() > CONNECTION_STALE_SECONDS

    def update_activity(self):
        self.last_activity = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'namespace': self.namespace,
            'client_ip': self.client_ip,
            'connected_at': self.connected_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'rooms': list(self.rooms),
        }


class WebSocketManager:
    """WebSocket connection manager."""

    def __init__(self, auth: Optional[WebSocketAuth] = None):
        self.auth = auth or websocket_auth
        self.room_manager = RoomManager()
        self.event_registry = event_registry

        self._connections: Dict[str, ConnectionInfo] = {}
        self._user_sessions: Dict[str, Set[str]] = {}
        self._namespace_sessions: Dict[str, Set[str]] = {}

        self._cleanup_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        self.cleanup_interval = 60
        self.heartbeat_interval = 30
        self.connection_timeout = 300

        self._stats = {
            'total_connections': 0,
            'current_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
        }

        self._started = False

    def _ensure_started(self):
        if not self._started:
            self._started = True
            try:
                loop = asyncio.get_running_loop()
                if self._cleanup_task is None:
                    self._cleanup_task = loop.create_task(self._cleanup_loop())
                if self._heartbeat_task is None:
                    self._heartbeat_task = loop.create_task(self._heartbeat_loop())
            except RuntimeError:
                pass

    async def _cleanup_loop(self):
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error in cleanup loop: {e}')

    async def _heartbeat_loop(self):
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeat_pings()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error in heartbeat loop: {e}')

    async def _cleanup_stale_connections(self):
        stale_sessions = [
            session_id
            for session_id, conn_info in self._connections.items()
            if conn_info.is_stale
        ]

        for session_id in stale_sessions:
            logger.info(f'Cleaning up stale connection: {session_id}')
            await self._disconnect_session(session_id, 'Connection timeout')

    async def _send_heartbeat_pings(self):
        ping_message = {
            'type': 'ping',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        failed_sessions = []
        for session_id, conn_info in self._connections.items():
            try:
                await conn_info.websocket.send_text(json.dumps(ping_message))
            except Exception:
                failed_sessions.append(session_id)

        for session_id in failed_sessions:
            await self._disconnect_session(session_id, 'Ping failed')

    def register_namespace_handler(self, namespace: str, handler):
        self.event_registry.register_handler(namespace, handler)
        logger.info(f'Handler registered for namespace: {namespace}')

    async def handle_connection(
        self,
        websocket: WebSocket,
        session: Session,
        namespace: str = 'default',
        session_id: Optional[str] = None,
    ):
        connection_info = None

        try:
            self._ensure_started()

            user = await self.auth.authenticate_websocket(websocket, session)
            await websocket.accept()

            if not session_id:
                session_id = str(uuid.uuid4())

            client_ip = self.auth._get_client_ip(websocket)

            connection_info = ConnectionInfo(
                websocket=websocket,
                user=user,
                session_id=session_id,
                namespace=namespace,
                client_ip=client_ip,
            )

            await self._register_connection(connection_info)
            await self._send_welcome_message(connection_info)
            await self._handle_message_loop(connection_info, session)

        except WebSocketException as e:
            logger.warning(f'WebSocket authentication failed: {e.reason}')
            try:
                await websocket.close(code=e.code, reason=e.reason)
            except Exception:
                pass

        except Exception as e:
            logger.error(f'WebSocket connection error: {e}', exc_info=True)
            try:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            except Exception:
                pass

        finally:
            if connection_info:
                await self._unregister_connection(connection_info)

    async def _register_connection(self, conn_info: ConnectionInfo):
        self._connections[conn_info.session_id] = conn_info

        user_id = conn_info.user_id
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = set()
        self._user_sessions[user_id].add(conn_info.session_id)

        if conn_info.namespace not in self._namespace_sessions:
            self._namespace_sessions[conn_info.namespace] = set()
        self._namespace_sessions[conn_info.namespace].add(conn_info.session_id)

        self._stats['total_connections'] += 1
        self._stats['current_connections'] += 1

        logger.info(
            f'WebSocket connected: {conn_info.session_id} (user: {user_id}, namespace: {conn_info.namespace})'
        )

    async def _unregister_connection(self, conn_info: ConnectionInfo):
        await self._disconnect_session(conn_info.session_id, 'Connection closed')

    async def _disconnect_session(self, session_id: str, reason: str = 'Disconnect'):
        conn_info = self._connections.get(session_id)
        if not conn_info:
            return

        try:
            await self._leave_all_rooms(conn_info)

            del self._connections[session_id]

            user_id = conn_info.user_id
            if user_id in self._user_sessions:
                self._user_sessions[user_id].discard(session_id)
                if not self._user_sessions[user_id]:
                    del self._user_sessions[user_id]

            if conn_info.namespace in self._namespace_sessions:
                self._namespace_sessions[conn_info.namespace].discard(session_id)
                if not self._namespace_sessions[conn_info.namespace]:
                    del self._namespace_sessions[conn_info.namespace]

            self._stats['current_connections'] -= 1

            logger.info(f'Session disconnected {session_id}: {reason}')

        except Exception as e:
            logger.error(f'Error during disconnect: {e}')

    async def _send_welcome_message(self, conn_info: ConnectionInfo):
        welcome_message = {
            'type': 'welcome',
            'session_id': conn_info.session_id,
            'namespace': conn_info.namespace,
            'user_id': conn_info.user_id,
            'server_time': datetime.now(timezone.utc).isoformat(),
            'supported_events': self.event_registry.get_all_event_types(),
        }

        await self._send_to_connection(conn_info, welcome_message)

    async def _handle_message_loop(self, conn_info: ConnectionInfo, session: Session):
        try:
            while True:
                try:
                    data = await conn_info.websocket.receive_text()
                    self._stats['messages_received'] += 1
                    conn_info.update_activity()
                except WebSocketDisconnect:
                    logger.info(f'WebSocket disconnected: {conn_info.session_id}')
                    break

                try:
                    await self._process_message(conn_info, data, session)
                except Exception as e:
                    logger.error(f'Error processing message: {e}', exc_info=True)
                    await self._send_error_response(conn_info, str(e), data)
                    self._stats['errors'] += 1

        except Exception as e:
            logger.error(f'Error in message loop: {e}', exc_info=True)

    async def _process_message(
        self, conn_info: ConnectionInfo, data: str, session: Session
    ):
        try:
            message_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise EventHandlingError(f'Invalid JSON: {e}')

        message_type = message_data.get('type')
        if not message_type:
            raise EventHandlingError('Message type is required')

        if message_type == 'ping':
            conn_info.update_activity()
            pong_response = {
                'type': 'pong',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
            if 'request_id' in message_data:
                pong_response['request_id'] = message_data['request_id']
            await self._send_to_connection(conn_info, pong_response)
            return

        elif message_type == 'pong':
            conn_info.update_activity()
            return

        elif message_type == 'join_room':
            await self._handle_join_room(conn_info, message_data, session)
            return

        elif message_type == 'leave_room':
            await self._handle_leave_room(conn_info, message_data)
            return

        handler = self.event_registry.get_handler(conn_info.namespace)
        if not handler:
            raise EventHandlingError(f'No handler for namespace: {conn_info.namespace}')

        response = await handler.handle_event(
            conn_info.websocket, conn_info.user, message_data
        )

        if response:
            await self._send_to_connection(conn_info, response.to_dict())

    async def _handle_join_room(
        self, conn_info: ConnectionInfo, message_data: Dict, session: Session
    ):
        room_id = message_data.get('room_id')
        room_type = message_data.get('room_type', 'general')

        if not room_id:
            raise EventHandlingError('room_id is required for join_room')

        success = await self.room_manager.join_room(
            user_id=conn_info.user_id,
            websocket=conn_info.websocket,
            user=conn_info.user,
            namespace=conn_info.namespace,
            room_type=room_type,
            room_id=room_id,
        )

        if success:
            conn_info.rooms.add(room_id)
            await self._send_to_connection(
                conn_info,
                {
                    'type': 'room_joined',
                    'room_id': room_id,
                    'room_type': room_type,
                    'success': True,
                },
            )
        else:
            await self._send_error_response(conn_info, f'Failed to join room: {room_id}')

    async def _handle_leave_room(self, conn_info: ConnectionInfo, message_data: Dict):
        room_id = message_data.get('room_id')
        room_type = message_data.get('room_type', 'general')

        if not room_id:
            raise EventHandlingError('room_id is required for leave_room')

        success = await self.room_manager.leave_room(
            conn_info.user_id, conn_info.namespace, room_type, room_id
        )

        if success:
            conn_info.rooms.discard(room_id)
            await self._send_to_connection(
                conn_info,
                {
                    'type': 'room_left',
                    'room_id': room_id,
                    'room_type': room_type,
                    'success': True,
                },
            )
        else:
            await self._send_error_response(
                conn_info, f'Failed to leave room: {room_id}'
            )

    async def _leave_all_rooms(self, conn_info: ConnectionInfo):
        rooms_to_leave = list(conn_info.rooms)

        for room_id in rooms_to_leave:
            for room_type in ['general', 'conversation', 'channel']:
                await self.room_manager.leave_room(
                    conn_info.user_id, conn_info.namespace, room_type, room_id
                )

        conn_info.rooms.clear()

    async def _send_to_connection(
        self, conn_info: ConnectionInfo, message: Dict[str, Any]
    ):
        try:
            message_str = json.dumps(message)
            await conn_info.websocket.send_text(message_str)
            self._stats['messages_sent'] += 1
        except Exception as e:
            logger.error(f'Failed to send message to {conn_info.session_id}: {e}')

    async def _send_error_response(
        self,
        conn_info: ConnectionInfo,
        error_message: str,
        original_data: Optional[str] = None,
    ):
        error_response = {
            'type': 'error',
            'error_message': error_message,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        if original_data:
            try:
                message_data = json.loads(original_data)
                if 'request_id' in message_data:
                    error_response['request_id'] = message_data['request_id']
            except (json.JSONDecodeError, TypeError):
                pass

        await self._send_to_connection(conn_info, error_response)

    async def broadcast_to_namespace(
        self,
        namespace: str,
        message: Dict[str, Any],
        exclude_users: Optional[Set[str]] = None,
    ) -> int:
        if namespace not in self._namespace_sessions:
            return 0

        session_ids = self._namespace_sessions[namespace].copy()
        successful_sends = 0

        for session_id in session_ids:
            conn_info = self._connections.get(session_id)
            if not conn_info:
                continue

            if exclude_users and conn_info.user_id in exclude_users:
                continue

            try:
                await self._send_to_connection(conn_info, message)
                successful_sends += 1
            except Exception as e:
                logger.error(f'Failed to broadcast to {session_id}: {e}')

        return successful_sends

    async def send_to_user(
        self, user_id: str, message: Dict[str, Any], namespace: Optional[str] = None
    ) -> int:
        if user_id not in self._user_sessions:
            return 0

        session_ids = self._user_sessions[user_id].copy()
        successful_sends = 0

        for session_id in session_ids:
            conn_info = self._connections.get(session_id)
            if not conn_info:
                continue

            if namespace and conn_info.namespace != namespace:
                continue

            try:
                await self._send_to_connection(conn_info, message)
                successful_sends += 1
            except Exception as e:
                logger.error(
                    f'Failed to send to user {user_id}, session {session_id}: {e}'
                )

        return successful_sends

    def get_connection_stats(self) -> Dict[str, Any]:
        namespace_stats = {
            namespace: len(session_ids)
            for namespace, session_ids in self._namespace_sessions.items()
        }

        return {
            **self._stats,
            'unique_users': len(self._user_sessions),
            'namespaces': namespace_stats,
            'room_stats': self.room_manager.get_room_stats(),
        }

    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        if user_id not in self._user_sessions:
            return []

        connections = []
        for session_id in self._user_sessions[user_id]:
            conn_info = self._connections.get(session_id)
            if conn_info:
                connections.append(conn_info.to_dict())

        return connections

    async def disconnect_user(
        self, user_id: str, reason: str = 'User disconnected'
    ) -> int:
        if user_id not in self._user_sessions:
            return 0

        session_ids = list(self._user_sessions[user_id])
        disconnected = 0

        for session_id in session_ids:
            await self._disconnect_session(session_id, reason)
            disconnected += 1

        return disconnected

    def __del__(self):
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()


websocket_manager = WebSocketManager()
