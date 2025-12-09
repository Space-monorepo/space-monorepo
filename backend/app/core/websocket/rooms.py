"""
Room management system for WebSocket communication.

This module provides a flexible room-based system for managing groups of
WebSocket connections. Rooms can represent conversations, communities,
notification groups, or any other logical grouping of users.

Key features:
- Hierarchical room structure (namespaces -> rooms -> connections)
- Efficient message broadcasting within rooms
- User presence tracking
- Room metadata and permissions
- Automatic cleanup of empty rooms
- Thread-safe operations
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import WebSocket

from app.api.users.model import User

from .exceptions import BroadcastError, RoomError

logger = logging.getLogger(__name__)


@dataclass
class UserConnection:
    """Represents a user's WebSocket connection within a room."""

    websocket: WebSocket
    user: User
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def user_id(self) -> str:
        """Get string representation of user ID."""
        return str(self.user.id)

    @property
    def user_name(self) -> str:
        """Get user's display name."""
        return self.user.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection info to dictionary."""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'joined_at': self.joined_at.isoformat(),
            'metadata': self.metadata,
        }


@dataclass
class RoomMetadata:
    """Metadata and configuration for a room."""

    room_id: str
    room_type: str
    namespace: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    max_connections: Optional[int] = None
    is_private: bool = False
    permissions: Dict[str, Any] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'room_id': self.room_id,
            'room_type': self.room_type,
            'namespace': self.namespace,
            'created_at': self.created_at.isoformat(),
            'max_connections': self.max_connections,
            'is_private': self.is_private,
            'permissions': self.permissions,
            'custom_data': self.custom_data,
        }


class Room:
    """
    Represents a room containing multiple WebSocket connections.

    A room is a logical grouping of WebSocket connections that can
    receive broadcast messages. Examples include chat conversations,
    community channels, or notification groups.
    """

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        room_id: str,
        room_type: str,
        namespace: str,
        max_connections: Optional[int] = None,
        is_private: bool = False,
        permissions: Optional[Dict[str, Any]] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ):
        self.metadata = RoomMetadata(
            room_id=room_id,
            room_type=room_type,
            namespace=namespace,
            max_connections=max_connections,
            is_private=is_private,
            permissions=permissions or {},
            custom_data=custom_data or {},
        )

        # Active connections: user_id -> UserConnection
        self._connections: Dict[str, UserConnection] = {}

        # Room event callbacks
        self._on_user_joined: Optional[Callable] = None
        self._on_user_left: Optional[Callable] = None
        self._on_message: Optional[Callable] = None

        # Thread safety
        self._lock = asyncio.Lock()

        logger.debug(f'Created room {room_id} in namespace {namespace}')

    @property
    def room_id(self) -> str:
        """Get room ID."""
        return self.metadata.room_id

    @property
    def namespace(self) -> str:
        """Get namespace."""
        return self.metadata.namespace

    @property
    def room_type(self) -> str:
        """Get room type."""
        return self.metadata.room_type

    @property
    def connection_count(self) -> int:
        """Get number of active connections."""
        return len(self._connections)

    @property
    def is_empty(self) -> bool:
        """Check if room has no connections."""
        return len(self._connections) == 0

    @property
    def user_ids(self) -> Set[str]:
        """Get set of connected user IDs."""
        return set(self._connections.keys())

    @property
    def users(self) -> List[User]:
        """Get list of connected users."""
        return [conn.user for conn in self._connections.values()]

    def set_event_callbacks(
        self,
        on_user_joined: Optional[Callable] = None,
        on_user_left: Optional[Callable] = None,
        on_message: Optional[Callable] = None,
    ):
        """Set event callback functions."""
        self._on_user_joined = on_user_joined
        self._on_user_left = on_user_left
        self._on_message = on_message

    async def add_connection(
        self, websocket: WebSocket, user: User, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a WebSocket connection to the room.

        Args:
            websocket: WebSocket connection
            user: User object
            metadata: Optional connection metadata

        Returns:
            True if added successfully, False if already exists or room full
        """
        async with self._lock:
            user_id = str(user.id)

            # Check if user already connected
            if user_id in self._connections:
                logger.warning(
                    f'User {user_id} already connected to room {self.room_id}'
                )
                return False

            # Check room capacity
            if (
                self.metadata.max_connections is not None
                and len(self._connections) >= self.metadata.max_connections
            ):
                logger.warning(f'Room {self.room_id} is at capacity')
                return False

            # Create connection
            connection = UserConnection(
                websocket=websocket, user=user, metadata=metadata or {}
            )

            self._connections[user_id] = connection

            logger.info(f'User {user_id} joined room {self.room_id}')

            # Trigger callback
            if self._on_user_joined:
                try:
                    await self._on_user_joined(self, connection)
                except Exception as e:
                    logger.error(f'Error in on_user_joined callback: {e}')

            return True

    async def remove_connection(self, user_id: str) -> bool:
        """
        Remove a WebSocket connection from the room.

        Args:
            user_id: User ID to remove

        Returns:
            True if removed, False if not found
        """
        async with self._lock:
            connection = self._connections.pop(user_id, None)

            if connection is None:
                return False

            logger.info(f'User {user_id} left room {self.room_id}')

            # Trigger callback
            if self._on_user_left:
                try:
                    await self._on_user_left(self, connection)
                except Exception as e:
                    logger.error(f'Error in on_user_left callback: {e}')

            return True

    def get_connection(self, user_id: str) -> Optional[UserConnection]:
        """Get connection for a specific user."""
        return self._connections.get(user_id)

    def has_user(self, user_id: str) -> bool:
        """Check if user is connected to this room."""
        return user_id in self._connections

    async def broadcast_message(
        self,
        message: Dict[str, Any],
        exclude_users: Optional[Set[str]] = None,
        include_users: Optional[Set[str]] = None,
    ) -> int:
        """
        Broadcast a message to all connections in the room.

        Args:
            message: Message dictionary to broadcast
            exclude_users: Set of user IDs to exclude from broadcast
            include_users: If set, only broadcast to these users

        Returns:
            Number of successful broadcasts

        Raises:
            BroadcastError: If broadcasting fails
        """
        if not self._connections:
            return 0

        exclude_users = exclude_users or set()

        # Determine target connections
        if include_users is not None:
            target_connections = {
                uid: conn
                for uid, conn in self._connections.items()
                if uid in include_users and uid not in exclude_users
            }
        else:
            target_connections = {
                uid: conn
                for uid, conn in self._connections.items()
                if uid not in exclude_users
            }

        if not target_connections:
            return 0

        # Prepare message
        try:
            message_str = json.dumps(message)
        except (TypeError, ValueError) as e:
            raise BroadcastError(f'Failed to serialize message: {e}')

        # Broadcast to connections
        successful_broadcasts = 0
        failed_connections = []

        for user_id, connection in target_connections.items():
            try:
                await connection.websocket.send_text(message_str)
                successful_broadcasts += 1
            except Exception as e:
                logger.error(f'Failed to send message to user {user_id}: {e}')
                failed_connections.append(user_id)

        # Clean up failed connections
        for user_id in failed_connections:
            await self.remove_connection(user_id)

        # Trigger message callback
        if self._on_message:
            try:
                await self._on_message(self, message, target_connections)
            except Exception as e:
                logger.error(f'Error in on_message callback: {e}')

        logger.debug(
            f'Broadcast to {successful_broadcasts}/{len(target_connections)} connections in room {self.room_id}'
        )

        return successful_broadcasts

    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to a specific user in the room.

        Args:
            user_id: Target user ID
            message: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        connection = self.get_connection(user_id)
        if not connection:
            return False

        try:
            message_str = json.dumps(message)
            await connection.websocket.send_text(message_str)
            return True
        except Exception as e:
            logger.error(f'Failed to send message to user {user_id}: {e}')
            await self.remove_connection(user_id)
            return False

    def get_room_info(self) -> Dict[str, Any]:
        """Get comprehensive room information."""
        return {
            'metadata': self.metadata.to_dict(),
            'connection_count': self.connection_count,
            'connections': [conn.to_dict() for conn in self._connections.values()],
        }


class RoomManager:
    """
    Manager for WebSocket rooms across different namespaces.

    This class provides centralized management of rooms, allowing different
    domains to create and manage their own rooms while sharing the same
    underlying infrastructure.
    """

    def __init__(self):
        # Hierarchical structure: namespace -> room_type -> room_id -> Room
        self._rooms: Dict[str, Dict[str, Dict[str, Room]]] = {}

        # User to room mappings for quick lookup: user_id -> set of (namespace, room_id)
        self._user_rooms: Dict[str, Set[tuple]] = {}

        # Room factory functions: room_type -> factory_function
        self._room_factories: Dict[str, Callable] = {}

        # Global event callbacks
        self._global_callbacks: Dict[str, List[Callable]] = {
            'room_created': [],
            'room_destroyed': [],
            'user_joined_room': [],
            'user_left_room': [],
        }

        # Cleanup configuration
        self._auto_cleanup = True
        self._cleanup_delay = 300  # 5 minutes

        # Thread safety
        self._lock = asyncio.Lock()

        logger.info('RoomManager initialized')

    def register_room_factory(self, room_type: str, factory: Callable) -> None:
        """Register a factory function for creating specific room types."""
        self._room_factories[room_type] = factory
        logger.debug(f'Registered room factory for type: {room_type}')

    def add_global_callback(self, event: str, callback: Callable) -> None:
        """Add a global callback for room events."""
        if event in self._global_callbacks:
            self._global_callbacks[event].append(callback)

    async def create_room(
        self, namespace: str, room_type: str, room_id: str, **kwargs
    ) -> Room:
        """
        Create a new room.

        Args:
            namespace: Namespace for the room (e.g., 'chat', 'notifications')
            room_type: Type of room (e.g., 'conversation', 'community_channel')
            room_id: Unique identifier for the room
            **kwargs: Additional room configuration

        Returns:
            Created Room instance

        Raises:
            RoomError: If room already exists or creation fails
        """
        async with self._lock:
            # Initialize namespace structure if needed
            if namespace not in self._rooms:
                self._rooms[namespace] = {}

            if room_type not in self._rooms[namespace]:
                self._rooms[namespace][room_type] = {}

            # Check if room already exists
            if room_id in self._rooms[namespace][room_type]:
                raise RoomError(
                    f'Room {room_id} already exists in {namespace}/{room_type}'
                )

            # Create room using factory or default
            if room_type in self._room_factories:
                room = await self._room_factories[room_type](
                    room_id=room_id, room_type=room_type, namespace=namespace, **kwargs
                )
            else:
                room = Room(
                    room_id=room_id, room_type=room_type, namespace=namespace, **kwargs
                )

            # Store room
            self._rooms[namespace][room_type][room_id] = room

            logger.info(f'Created room {room_id} in {namespace}/{room_type}')

            # Trigger global callbacks
            for callback in self._global_callbacks['room_created']:
                try:
                    await callback(room)
                except Exception as e:
                    logger.error(f'Error in room_created callback: {e}')

            return room

    async def get_room(
        self, namespace: str, room_type: str, room_id: str
    ) -> Optional[Room]:
        """Get an existing room."""
        return self._rooms.get(namespace, {}).get(room_type, {}).get(room_id)

    async def get_or_create_room(
        self, namespace: str, room_type: str, room_id: str, **kwargs
    ) -> Room:
        """Get existing room or create new one if it doesn't exist."""
        room = await self.get_room(namespace, room_type, room_id)
        if room is None:
            room = await self.create_room(namespace, room_type, room_id, **kwargs)
        return room

    async def destroy_room(
        self, namespace: str, room_type: str, room_id: str, force: bool = False
    ) -> bool:
        """
        Destroy a room and disconnect all users.

        Args:
            namespace: Room namespace
            room_type: Room type
            room_id: Room ID
            force: If True, destroy even if room has connections

        Returns:
            True if destroyed, False if not found or has connections
        """
        async with self._lock:
            room = await self.get_room(namespace, room_type, room_id)
            if not room:
                return False

            # Check if room has connections
            if not force and not room.is_empty:
                logger.warning(f'Cannot destroy room {room_id} with active connections')
                return False

            # Disconnect all users
            user_ids = list(room.user_ids)
            for user_id in user_ids:
                await self.leave_room(user_id, namespace, room_type, room_id)

            # Remove from storage
            del self._rooms[namespace][room_type][room_id]

            # Clean up empty structures
            if not self._rooms[namespace][room_type]:
                del self._rooms[namespace][room_type]
            if not self._rooms[namespace]:
                del self._rooms[namespace]

            logger.info(f'Destroyed room {room_id} in {namespace}/{room_type}')

            # Trigger global callbacks
            for callback in self._global_callbacks['room_destroyed']:
                try:
                    await callback(room)
                except Exception as e:
                    logger.error(f'Error in room_destroyed callback: {e}')

            return True

    async def join_room(  # noqa: PLR0913, PLR0917
        self,
        user_id: str,
        websocket: WebSocket,
        user: User,
        namespace: str,
        room_type: str,
        room_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        **room_kwargs,
    ) -> bool:
        """
        Add a user to a room.

        Args:
            user_id: User ID
            websocket: WebSocket connection
            user: User object
            namespace: Room namespace
            room_type: Room type
            room_id: Room ID
            metadata: Optional connection metadata
            **room_kwargs: Additional room creation parameters

        Returns:
            True if joined successfully
        """
        # Get or create room
        room = await self.get_or_create_room(
            namespace, room_type, room_id, **room_kwargs
        )

        # Add connection to room
        success = await room.add_connection(websocket, user, metadata)

        if success:
            # Track user's room membership
            if user_id not in self._user_rooms:
                self._user_rooms[user_id] = set()

            self._user_rooms[user_id].add((namespace, room_id))

            # Trigger global callbacks
            for callback in self._global_callbacks['user_joined_room']:
                try:
                    await callback(user, room)
                except Exception as e:
                    logger.error(f'Error in user_joined_room callback: {e}')

        return success

    async def leave_room(
        self, user_id: str, namespace: str, room_type: str, room_id: str
    ) -> bool:
        """Remove a user from a room."""
        room = await self.get_room(namespace, room_type, room_id)
        if not room:
            return False

        success = await room.remove_connection(user_id)

        if success:
            # Update user's room membership
            if user_id in self._user_rooms:
                self._user_rooms[user_id].discard((namespace, room_id))
                if not self._user_rooms[user_id]:
                    del self._user_rooms[user_id]

            # Trigger global callbacks
            for callback in self._global_callbacks['user_left_room']:
                try:
                    await callback(user_id, room)
                except Exception as e:
                    logger.error(f'Error in user_left_room callback: {e}')

            # Auto-cleanup empty rooms
            if self._auto_cleanup and room.is_empty:
                await self._schedule_room_cleanup(namespace, room_type, room_id)

        return success

    async def leave_all_rooms(self, user_id: str) -> int:
        """Remove user from all rooms."""
        if user_id not in self._user_rooms:
            return 0

        rooms_to_leave = list(self._user_rooms[user_id])
        count = 0

        for namespace, room_id in rooms_to_leave:
            # Find room type
            for room_type in self._rooms.get(namespace, {}):
                if room_id in self._rooms[namespace][room_type]:
                    if await self.leave_room(user_id, namespace, room_type, room_id):
                        count += 1
                    break

        return count

    def get_user_rooms(self, user_id: str) -> List[tuple]:
        """Get list of rooms user is connected to."""
        return list(self._user_rooms.get(user_id, set()))

    async def broadcast_to_room(  # noqa: PLR0913, PLR0917
        self,
        namespace: str,
        room_type: str,
        room_id: str,
        message: Dict[str, Any],
        exclude_users: Optional[Set[str]] = None,
        include_users: Optional[Set[str]] = None,
    ) -> int:
        """Broadcast message to a specific room."""
        room = await self.get_room(namespace, room_type, room_id)
        if not room:
            return 0

        return await room.broadcast_message(message, exclude_users, include_users)

    async def send_to_user(
        self,
        user_id: str,
        message: Dict[str, Any],
        namespace: Optional[str] = None,
        room_type: Optional[str] = None,
        room_id: Optional[str] = None,
    ) -> int:
        """
        Send message to a user across all their rooms or specific room.

        Returns number of successful sends.
        """
        if room_id and namespace and room_type:
            # Send to specific room
            room = await self.get_room(namespace, room_type, room_id)
            if room and await room.send_to_user(user_id, message):
                return 1
            return 0

        # Send to all user's rooms
        user_rooms = self.get_user_rooms(user_id)
        count = 0

        for ns, rid in user_rooms:
            for rtype in self._rooms.get(ns, {}):
                if rid in self._rooms[ns][rtype]:
                    room = self._rooms[ns][rtype][rid]
                    if await room.send_to_user(user_id, message):
                        count += 1
                    break

        return count

    def get_room_stats(self) -> Dict[str, Any]:
        """Get comprehensive room statistics."""
        total_rooms = 0
        total_connections = 0
        namespaces_stats = {}

        for namespace, room_types in self._rooms.items():
            namespace_rooms = 0
            namespace_connections = 0
            room_types_stats = {}

            for room_type, rooms in room_types.items():
                type_rooms = len(rooms)
                type_connections = sum(room.connection_count for room in rooms.values())

                room_types_stats[room_type] = {
                    'room_count': type_rooms,
                    'connection_count': type_connections,
                }

                namespace_rooms += type_rooms
                namespace_connections += type_connections

            namespaces_stats[namespace] = {
                'room_count': namespace_rooms,
                'connection_count': namespace_connections,
                'room_types': room_types_stats,
            }

            total_rooms += namespace_rooms
            total_connections += namespace_connections

        return {
            'total_rooms': total_rooms,
            'total_connections': total_connections,
            'total_users': len(self._user_rooms),
            'namespaces': namespaces_stats,
        }

    async def _schedule_room_cleanup(
        self, namespace: str, room_type: str, room_id: str
    ) -> None:
        """Schedule cleanup of empty room after delay."""
        if not self._auto_cleanup:
            return

        async def cleanup_task():
            await asyncio.sleep(self._cleanup_delay)

            room = await self.get_room(namespace, room_type, room_id)
            if room and room.is_empty:
                await self.destroy_room(namespace, room_type, room_id, force=True)

        # Schedule cleanup task
        asyncio.create_task(cleanup_task())

    @asynccontextmanager
    async def room_context(  # noqa: PLR0913, PLR0917
        self,
        user_id: str,
        websocket: WebSocket,
        user: User,
        namespace: str,
        room_type: str,
        room_id: str,
        **kwargs,
    ):
        """
        Context manager for automatic room join/leave.

        Usage:
            async with room_manager.room_context(user_id, ws, user, 'chat', 'conversation', 'conv_123'):
                # User is automatically joined to room
                await do_something()
                # User is automatically removed when context exits
        """
        joined = await self.join_room(
            user_id, websocket, user, namespace, room_type, room_id, **kwargs
        )

        if not joined:
            raise RoomError(f'Failed to join room {room_id}')

        try:
            yield await self.get_room(namespace, room_type, room_id)
        finally:
            await self.leave_room(user_id, namespace, room_type, room_id)
