"""
Centralized WebSocket manager for real-time communication.

This module provides the core WebSocket infrastructure that orchestrates
connections, events, rooms, and authentication across all domains in the
application. It serves as the single point of entry for all WebSocket
functionality.

Key responsibilities:
- Connection lifecycle management
- Event routing and handling
- Room management and broadcasting
- Authentication and authorization
- Monitoring and statistics
- Error handling and recovery
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from sqlalchemy.orm import Session

from app.api.users.model import User

from .auth import WebSocketAuth, websocket_auth
from .events import (
    EventHandler,
    event_registry,
)
from .exceptions import (
    EventHandlingError,
)
from .rooms import RoomManager

logger = logging.getLogger(__name__)


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
        """Get string representation of user ID."""
        return str(self.user.id)

    @property
    def is_stale(self) -> bool:
        """Check if connection appears to be stale."""
        now = datetime.now(timezone.utc)
        CONNECTION_STALE_SECONDS = 300
        return (
            now - self.last_activity
        ).total_seconds() > CONNECTION_STALE_SECONDS  # 5 minutes

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection info to dictionary."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'namespace': self.namespace,
            'client_ip': self.client_ip,
            'connected_at': self.connected_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'rooms': list(self.rooms),
            'metadata': self.metadata,
        }


class WebSocketManager:
    """
    Centralized WebSocket manager for the entire application.

    This class orchestrates all WebSocket functionality, providing a unified
    interface for different domains while maintaining separation of concerns
    through the namespace system.
    """

    def __init__(self, auth: Optional[WebSocketAuth] = None):
        # Core components
        self.auth = auth or websocket_auth
        self.room_manager = RoomManager()
        self.event_registry = event_registry

        # Connection tracking
        # session_id -> ConnectionInfo
        self._connections: Dict[str, ConnectionInfo] = {}

        # User mappings: user_id -> set of session_ids
        self._user_sessions: Dict[str, Set[str]] = {}

        # Namespace mappings: namespace -> set of session_ids
        self._namespace_sessions: Dict[str, Set[str]] = {}

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        # Configuration
        self.cleanup_interval = 60  # seconds
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 300  # seconds

        # Callbacks for lifecycle events
        self._connection_callbacks: Dict[str, List[Callable]] = {
            'on_connect': [],
            'on_disconnect': [],
            'on_error': [],
            'on_room_join': [],
            'on_room_leave': [],
        }

        # Statistics
        self._stats = {
            'total_connections': 0,
            'current_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
        }

        # Background tasks initialization (lazy)
        self._started = False

        logger.info('WebSocketManager initialized')

    def _ensure_started(self):
        """Ensure background tasks are started (lazy initialization)."""
        if not self._started:
            self._started = True
            try:
                loop = asyncio.get_running_loop()
                if not self._cleanup_task:
                    self._cleanup_task = loop.create_task(self._cleanup_loop())
                if not self._heartbeat_task:
                    self._heartbeat_task = loop.create_task(self._heartbeat_loop())
            except RuntimeError:
                # No running event loop, tasks will be started when needed
                pass

    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        self._ensure_started()

    async def _cleanup_loop(self):
        """Background task for cleaning up stale connections."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error in cleanup loop: {e}')

    async def _heartbeat_loop(self):
        """Background task for sending heartbeat pings."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeat_pings()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error in heartbeat loop: {e}')

    async def _cleanup_stale_connections(self):
        """Remove connections that appear to be stale."""
        stale_sessions = []

        for session_id, conn_info in self._connections.items():
            if conn_info.is_stale:
                stale_sessions.append(session_id)

        for session_id in stale_sessions:
            logger.info(f'Cleaning up stale connection: {session_id}')
            await self._disconnect_session(session_id, 'Connection timeout')

    async def _send_heartbeat_pings(self):
        """Send ping messages to all active connections."""
        ping_message = {
            'type': 'ping',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        failed_sessions = []
        for session_id, conn_info in self._connections.items():
            try:
                await conn_info.websocket.send_text(json.dumps(ping_message))
            except Exception as e:
                logger.warning(f'Failed to send ping to {session_id}: {e}')
                failed_sessions.append(session_id)

        # Clean up failed connections
        for session_id in failed_sessions:
            await self._disconnect_session(session_id, 'Ping failed')

    def register_namespace_handler(self, namespace: str, handler: EventHandler):
        """Register an event handler for a specific namespace."""
        self.event_registry.register_handler(namespace, handler)
        logger.info(f'Registered handler for namespace: {namespace}')

    def add_lifecycle_callback(self, event: str, callback: Callable):
        """Add a callback for connection lifecycle events."""
        if event in self._connection_callbacks:
            self._connection_callbacks[event].append(callback)

    async def handle_connection(
        self,
        websocket: WebSocket,
        session: Session,
        namespace: str = 'default',
        session_id: Optional[str] = None,
    ):
        """
        Main entry point for handling WebSocket connections.

        This method handles the complete lifecycle of a WebSocket connection,
        including authentication, event processing, and cleanup.

        Args:
            websocket: WebSocket connection
            session: Database session
            namespace: Application namespace (e.g., 'chat', 'notifications')
            session_id: Optional session identifier
        """
        connection_info = None

        try:
            # Ensure background tasks are started
            self._ensure_started()

            # Authenticate user
            user = await self.auth.authenticate_websocket(websocket, session)

            # Accept connection
            await websocket.accept()

            # Create connection info
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

            # Register connection
            await self._register_connection(connection_info)

            # Send welcome message
            await self._send_welcome_message(connection_info)

            # Handle messages
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
            # Always clean up connection
            if connection_info:
                await self._unregister_connection(connection_info)

    async def _register_connection(self, conn_info: ConnectionInfo):
        """Register a new connection."""
        # Store connection
        self._connections[conn_info.session_id] = conn_info

        # Update user sessions
        user_id = conn_info.user_id
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = set()
        self._user_sessions[user_id].add(conn_info.session_id)

        # Update namespace sessions
        if conn_info.namespace not in self._namespace_sessions:
            self._namespace_sessions[conn_info.namespace] = set()
        self._namespace_sessions[conn_info.namespace].add(conn_info.session_id)

        # Update statistics
        self._stats['total_connections'] += 1
        self._stats['current_connections'] += 1

        logger.info(
            f'Registered WebSocket connection: {conn_info.session_id} (user: {user_id}, namespace: {conn_info.namespace})'
        )

        # Trigger callbacks
        for callback in self._connection_callbacks['on_connect']:
            try:
                await callback(conn_info)
            except Exception as e:
                logger.error(f'Error in on_connect callback: {e}')

    async def _unregister_connection(self, conn_info: ConnectionInfo):
        """Unregister and clean up a connection."""
        await self._disconnect_session(conn_info.session_id, 'Connection closed')

    async def _disconnect_session(self, session_id: str, reason: str = 'Disconnect'):
        """Disconnect and clean up a specific session."""
        conn_info = self._connections.get(session_id)
        if not conn_info:
            return

        try:
            # Remove from all rooms
            await self._leave_all_rooms(conn_info)

            # Remove from tracking structures
            del self._connections[session_id]

            # Update user sessions
            user_id = conn_info.user_id
            if user_id in self._user_sessions:
                self._user_sessions[user_id].discard(session_id)
                if not self._user_sessions[user_id]:
                    del self._user_sessions[user_id]

            # Update namespace sessions
            if conn_info.namespace in self._namespace_sessions:
                self._namespace_sessions[conn_info.namespace].discard(session_id)
                if not self._namespace_sessions[conn_info.namespace]:
                    del self._namespace_sessions[conn_info.namespace]

            # Update statistics
            self._stats['current_connections'] -= 1

            logger.info(f'Disconnected session {session_id}: {reason}')

            # Trigger callbacks
            for callback in self._connection_callbacks['on_disconnect']:
                try:
                    await callback(conn_info, reason)
                except Exception as e:
                    logger.error(f'Error in on_disconnect callback: {e}')

        except Exception as e:
            logger.error(f'Error during disconnect cleanup: {e}')

    async def _send_welcome_message(self, conn_info: ConnectionInfo):
        """Send welcome message to newly connected client."""
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
        """Main message handling loop for a connection."""
        try:
            while True:
                # Receive message
                try:
                    data = await conn_info.websocket.receive_text()
                    self._stats['messages_received'] += 1
                    conn_info.update_activity()
                except WebSocketDisconnect:
                    logger.info(f'WebSocket disconnected: {conn_info.session_id}')
                    break

                # Process message
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
        """Process incoming WebSocket message."""
        try:
            message_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise EventHandlingError(f'Invalid JSON: {e}')

        message_type = message_data.get('type')
        if not message_type:
            raise EventHandlingError('Message type is required')

        # Handle built-in message types
        if message_type == 'ping':
            # Client sent ping, respond with pong
            conn_info.update_activity()
            pong_response = {
                'type': 'pong',
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
            # Include request_id if provided
            if 'request_id' in message_data:
                pong_response['request_id'] = message_data['request_id']
            await self._send_to_connection(conn_info, pong_response)
            return

        elif message_type == 'pong':
            # Client responded to ping
            conn_info.update_activity()
            return

        elif message_type == 'join_room':
            await self._handle_join_room(conn_info, message_data, session)
            return

        elif message_type == 'leave_room':
            await self._handle_leave_room(conn_info, message_data)
            return

        # Route to namespace-specific handler
        handler = self.event_registry.get_handler(conn_info.namespace)
        if not handler:
            raise EventHandlingError(f'No handler for namespace: {conn_info.namespace}')

        # Process event
        response = await handler.handle_event(
            conn_info.websocket, conn_info.user, message_data
        )

        # Send response if provided
        if response:
            await self._send_to_connection(conn_info, response.to_dict())

    async def _handle_join_room(
        self, conn_info: ConnectionInfo, message_data: Dict, session: Session
    ):
        """Handle room join request."""
        room_id = message_data.get('room_id')
        room_type = message_data.get('room_type', 'general')

        if not room_id:
            raise EventHandlingError('room_id is required for join_room')

        # Join room through room manager
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

            # Send confirmation
            await self._send_to_connection(
                conn_info,
                {
                    'type': 'room_joined',
                    'room_id': room_id,
                    'room_type': room_type,
                    'success': True,
                },
            )

            # Trigger callback
            for callback in self._connection_callbacks['on_room_join']:
                try:
                    await callback(conn_info, room_id, room_type)
                except Exception as e:
                    logger.error(f'Error in on_room_join callback: {e}')

        else:
            await self._send_error_response(conn_info, f'Failed to join room: {room_id}')

    async def _handle_leave_room(self, conn_info: ConnectionInfo, message_data: Dict):
        """Handle room leave request."""
        room_id = message_data.get('room_id')
        room_type = message_data.get('room_type', 'general')

        if not room_id:
            raise EventHandlingError('room_id is required for leave_room')

        # Leave room through room manager
        success = await self.room_manager.leave_room(
            conn_info.user_id, conn_info.namespace, room_type, room_id
        )

        if success:
            conn_info.rooms.discard(room_id)

            # Send confirmation
            await self._send_to_connection(
                conn_info,
                {
                    'type': 'room_left',
                    'room_id': room_id,
                    'room_type': room_type,
                    'success': True,
                },
            )

            # Trigger callback
            for callback in self._connection_callbacks['on_room_leave']:
                try:
                    await callback(conn_info, room_id, room_type)
                except Exception as e:
                    logger.error(f'Error in on_room_leave callback: {e}')

        else:
            await self._send_error_response(
                conn_info, f'Failed to leave room: {room_id}'
            )

    async def _leave_all_rooms(self, conn_info: ConnectionInfo):
        """Remove connection from all rooms."""
        rooms_to_leave = list(conn_info.rooms)

        for room_id in rooms_to_leave:
            # Try to find room in different types
            for room_type in ['general', 'conversation', 'channel']:  # Common types
                await self.room_manager.leave_room(
                    conn_info.user_id, conn_info.namespace, room_type, room_id
                )

        conn_info.rooms.clear()

    async def _send_to_connection(
        self, conn_info: ConnectionInfo, message: Dict[str, Any]
    ):
        """Send message to a specific connection."""
        try:
            message_str = json.dumps(message)
            await conn_info.websocket.send_text(message_str)
            self._stats['messages_sent'] += 1
        except Exception as e:
            logger.error(f'Failed to send message to {conn_info.session_id}: {e}')
            # Don't raise here as it might be called during cleanup

    async def _send_error_response(self, conn_info: ConnectionInfo, error_message: str, original_data: Optional[str] = None):
        """Send error response to connection."""
        error_response = {
            'type': 'error',
            'error_message': error_message,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        # Include request_id from original message if available
        if original_data:
            try:
                message_data = json.loads(original_data)
                if 'request_id' in message_data:
                    error_response['request_id'] = message_data['request_id']
            except (json.JSONDecodeError, TypeError):
                pass  # If we can't parse, just send error without request_id

        await self._send_to_connection(conn_info, error_response)

    # Public API methods

    async def broadcast_to_namespace(
        self,
        namespace: str,
        message: Dict[str, Any],
        exclude_users: Optional[Set[str]] = None,
    ) -> int:
        """Broadcast message to all connections in a namespace."""
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
        """Send message to all sessions of a specific user."""
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
        """Get comprehensive connection statistics."""
        namespace_stats = {}
        for namespace, session_ids in self._namespace_sessions.items():
            namespace_stats[namespace] = len(session_ids)

        return {
            **self._stats,
            'unique_users': len(self._user_sessions),
            'namespaces': namespace_stats,
            'room_stats': self.room_manager.get_room_stats(),
        }

    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all connections for a specific user."""
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
        """Disconnect all sessions for a specific user."""
        if user_id not in self._user_sessions:
            return 0

        session_ids = list(self._user_sessions[user_id])
        disconnected = 0

        for session_id in session_ids:
            await self._disconnect_session(session_id, reason)
            disconnected += 1

        return disconnected

    def __del__(self):
        """Cleanup when manager is destroyed."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
