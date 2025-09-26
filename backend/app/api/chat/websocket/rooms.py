"""
Chat-specific room management utilities for WebSocket conversations.

This module provides specialized room management functionality for chat
conversations, building on top of the centralized room system. It includes
conversation-specific room behaviors, permission checks, and utilities for
managing chat room lifecycle.

Key features:
- Conversation room factory for creating chat-specific rooms
- Permission validation for conversation access
- Conversation participant management
- Chat room metadata and configuration
- Integration with ChatService for business logic
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set
from uuid import UUID

from app.api.chat.service import ChatService
from app.api.users.model import User
from app.core.websocket.manager import websocket_manager
from app.core.websocket.rooms import Room, RoomManager

logger = logging.getLogger(__name__)


class ConversationRoom(Room):
    """
    Specialized room for chat conversations.

    Extends the base Room class with conversation-specific functionality
    like participant validation, message history access, and conversation
    state management.
    """

    def __init__(
        self,
        room_id: str,
        namespace: str = 'chat',
        conversation_id: Optional[UUID] = None,
        **kwargs,
    ):
        super().__init__(
            room_id=room_id,
            room_type='conversation',
            namespace=namespace,
            max_connections=10,  # Reasonable limit for conversation participants
            is_private=True,  # Conversations are private by default
            **kwargs,
        )

        # Conversation-specific attributes
        self.conversation_id = conversation_id or UUID(room_id)

        # Track conversation state
        self.conversation_metadata: Dict[str, Any] = {}
        self.last_message_time: Optional[datetime] = None
        self.active_typers: Set[str] = set()

        logger.debug(
            f'Created conversation room for conversation {self.conversation_id}'
        )

    async def validate_user_access(self, user: User, chat_service: ChatService) -> bool:
        """
        Validate that a user has access to this conversation.

        Args:
            user: User attempting to join
            chat_service: ChatService instance for validation

        Returns:
            True if user has access, False otherwise
        """
        try:
            # Use ChatService to validate conversation access
            conversation = chat_service.get_conversation(
                self.conversation_id, UUID(str(user.id))
            )
            return conversation is not None

        except Exception as e:
            logger.warning(
                f'Access validation failed for user {user.id} in conversation {self.conversation_id}: {e}'
            )
            return False

    def update_conversation_activity(self):
        """Update conversation activity timestamp."""
        self.last_message_time = datetime.now(timezone.utc)

    def add_typer(self, user_id: str):
        """Add user to active typers set."""
        self.active_typers.add(user_id)

    def remove_typer(self, user_id: str):
        """Remove user from active typers set."""
        self.active_typers.discard(user_id)

    def get_typing_users(self) -> Set[str]:
        """Get set of currently typing user IDs."""
        return self.active_typers.copy()

    def get_conversation_info(self) -> Dict[str, Any]:
        """Get conversation-specific room information."""
        base_info = self.get_room_info()

        conversation_info = {
            'conversation_id': str(self.conversation_id),
            'last_message_time': self.last_message_time.isoformat()
            if self.last_message_time
            else None,
            'active_typers': list(self.active_typers),
            'conversation_metadata': self.conversation_metadata,
        }

        base_info['conversation_info'] = conversation_info
        return base_info


class ChatRoomManager:
    """
    Manager for chat-specific room operations.

    This class provides utilities for managing chat rooms with conversation-specific
    logic, including room creation, participant management, and permission validation.
    """

    def __init__(self, room_manager: RoomManager):
        self.room_manager = room_manager

        # Register conversation room factory
        self.room_manager.register_room_factory(
            'conversation', self._create_conversation_room
        )

        # Chat-specific configuration
        self.max_conversation_participants = 2  # 1v1 conversations only
        self.conversation_timeout = 3600  # 1 hour of inactivity

        logger.info('ChatRoomManager initialized')

    async def _create_conversation_room(
        self,
        room_id: str,
        room_type: str,
        namespace: str,
        conversation_id: Optional[str] = None,
        **kwargs,
    ) -> ConversationRoom:
        """Factory method for creating conversation rooms."""

        # Convert conversation_id to UUID if provided as string
        conv_uuid = None
        if conversation_id:
            try:
                conv_uuid = UUID(conversation_id)
            except ValueError:
                conv_uuid = UUID(room_id)

        return ConversationRoom(
            room_id=room_id,
            namespace=namespace,
            conversation_id=conv_uuid,
            max_connections=self.max_conversation_participants,
            **kwargs,
        )

    async def join_conversation(
        self,
        user_id: str,
        websocket,
        user: User,
        conversation_id: UUID,
        chat_service: ChatService,
        **kwargs,
    ) -> bool:
        """
        Join a conversation room with validation.

        Args:
            user_id: User ID
            websocket: WebSocket connection
            user: User object
            conversation_id: Conversation UUID
            chat_service: ChatService for validation
            **kwargs: Additional room parameters

        Returns:
            True if successfully joined, False otherwise
        """
        try:
            room_id = str(conversation_id)

            # Get or create conversation room
            room = await self.room_manager.get_or_create_room(
                namespace='chat',
                room_type='conversation',
                room_id=room_id,
                conversation_id=str(conversation_id),
                **kwargs,
            )

            # Validate user access if this is a ConversationRoom
            if isinstance(room, ConversationRoom):
                if not await room.validate_user_access(user, chat_service):
                    logger.warning(
                        f'User {user_id} denied access to conversation {conversation_id}'
                    )
                    return False

            # Join the room
            success = await self.room_manager.join_room(
                user_id=user_id,
                websocket=websocket,
                user=user,
                namespace='chat',
                room_type='conversation',
                room_id=room_id,
            )

            if success and isinstance(room, ConversationRoom):
                # Update conversation metadata
                room.conversation_metadata['last_joined'] = datetime.now(
                    timezone.utc
                ).isoformat()
                logger.info(f'User {user_id} joined conversation {conversation_id}')

            return success

        except Exception as e:
            logger.error(f'Error joining conversation {conversation_id}: {e}')
            return False

    async def leave_conversation(self, user_id: str, conversation_id: UUID) -> bool:
        """
        Leave a conversation room.

        Args:
            user_id: User ID
            conversation_id: Conversation UUID

        Returns:
            True if successfully left, False otherwise
        """
        try:
            room_id = str(conversation_id)

            # Get room to clear typing indicators
            room = await self.room_manager.get_room('chat', 'conversation', room_id)
            if isinstance(room, ConversationRoom):
                room.remove_typer(user_id)

            # Leave the room
            success = await self.room_manager.leave_room(
                user_id=user_id,
                namespace='chat',
                room_type='conversation',
                room_id=room_id,
            )

            if success:
                logger.info(f'User {user_id} left conversation {conversation_id}')

            return success

        except Exception as e:
            logger.error(f'Error leaving conversation {conversation_id}: {e}')
            return False

    async def broadcast_to_conversation(
        self,
        conversation_id: UUID,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None,
    ) -> int:
        """
        Broadcast message to all participants in a conversation.

        Args:
            conversation_id: Conversation UUID
            message: Message to broadcast
            exclude_user: User ID to exclude from broadcast

        Returns:
            Number of successful broadcasts
        """
        try:
            room_id = str(conversation_id)
            exclude_users = {exclude_user} if exclude_user else None

            count = await self.room_manager.broadcast_to_room(
                namespace='chat',
                room_type='conversation',
                room_id=room_id,
                message=message,
                exclude_users=exclude_users,
            )

            # Update room activity if broadcast was successful
            if count > 0:
                room = await self.room_manager.get_room('chat', 'conversation', room_id)
                if isinstance(room, ConversationRoom):
                    room.update_conversation_activity()

            return count

        except Exception as e:
            logger.error(f'Error broadcasting to conversation {conversation_id}: {e}')
            return 0

    async def set_typing_status(
        self, user_id: str, conversation_id: UUID, is_typing: bool
    ) -> bool:
        """
        Set typing status for a user in a conversation.

        Args:
            user_id: User ID
            conversation_id: Conversation UUID
            is_typing: Whether user is typing

        Returns:
            True if status was updated, False otherwise
        """
        try:
            room_id = str(conversation_id)
            room = await self.room_manager.get_room('chat', 'conversation', room_id)

            if isinstance(room, ConversationRoom):
                if is_typing:
                    room.add_typer(user_id)
                else:
                    room.remove_typer(user_id)

                logger.debug(
                    f'Updated typing status for user {user_id} in conversation {conversation_id}: {is_typing}'
                )
                return True

            return False

        except Exception as e:
            logger.error(f'Error setting typing status: {e}')
            return False

    async def get_conversation_participants(self, conversation_id: UUID) -> Set[str]:
        """
        Get set of active participant user IDs in a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Set of user IDs currently connected to the conversation
        """
        try:
            room_id = str(conversation_id)
            room = await self.room_manager.get_room('chat', 'conversation', room_id)

            if room:
                return room.user_ids

            return set()

        except Exception as e:
            logger.error(f'Error getting conversation participants: {e}')
            return set()

    async def get_conversation_stats(self, conversation_id: UUID) -> Dict[str, Any]:
        """
        Get statistics and information about a conversation room.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Dictionary with conversation statistics
        """
        try:
            room_id = str(conversation_id)
            room = await self.room_manager.get_room('chat', 'conversation', room_id)

            if isinstance(room, ConversationRoom):
                return room.get_conversation_info()
            elif room:
                return room.get_room_info()
            else:
                return {
                    'conversation_id': str(conversation_id),
                    'exists': False,
                    'participant_count': 0,
                }

        except Exception as e:
            logger.error(f'Error getting conversation stats: {e}')
            return {'error': str(e)}

    @staticmethod
    async def cleanup_inactive_conversations() -> int:
        """
        Clean up conversations that have been inactive for too long.

        Returns:
            Number of conversations cleaned up
        """
        try:
            # This would require iterating through all conversation rooms
            # and checking their last activity time
            # Implementation would depend on the base RoomManager capabilities

            cleaned_count = 0

            # For now, we'll return 0 as this requires more complex room enumeration
            # In a full implementation, you'd iterate through rooms and check timestamps

            logger.debug(f'Cleaned up {cleaned_count} inactive conversations')
            return cleaned_count

        except Exception as e:
            logger.error(f'Error cleaning up inactive conversations: {e}')
            return 0

    @staticmethod
    async def validate_conversation_access(
        user: User, conversation_id: UUID, chat_service: ChatService
    ) -> bool:
        """
        Validate that a user has access to a conversation.

        Args:
            user: User to validate
            conversation_id: Conversation UUID
            chat_service: ChatService instance

        Returns:
            True if user has access, False otherwise
        """
        try:
            conversation = chat_service.get_conversation(
                conversation_id, UUID(str(user.id))
            )
            return conversation is not None

        except Exception as e:
            logger.warning(f'Conversation access validation failed: {e}')
            return False

    def get_chat_room_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all chat rooms."""
        base_stats = self.room_manager.get_room_stats()

        # Add chat-specific statistics
        chat_stats = base_stats.get('namespaces', {}).get('chat', {})
        conversation_stats = chat_stats.get('room_types', {}).get('conversation', {})

        return {
            'total_conversations': conversation_stats.get('room_count', 0),
            'total_chat_connections': conversation_stats.get('connection_count', 0),
            'base_room_stats': base_stats,
        }


# Utility functions for integration


def get_chat_room_manager() -> ChatRoomManager:
    """Get the global chat room manager instance."""

    # Create chat room manager if it doesn't exist
    if not hasattr(websocket_manager, '_chat_room_manager'):
        websocket_manager._chat_room_manager = ChatRoomManager(
            websocket_manager.room_manager
        )

    return websocket_manager._chat_room_manager


async def join_conversation_room(
    user_id: str, websocket, user: User, conversation_id: UUID, chat_service: ChatService
) -> bool:
    """
    Convenient function to join a conversation room.

    Args:
        user_id: User ID
        websocket: WebSocket connection
        user: User object
        conversation_id: Conversation UUID
        chat_service: ChatService instance

    Returns:
        True if successfully joined
    """
    chat_room_manager = get_chat_room_manager()
    return await chat_room_manager.join_conversation(
        user_id=user_id,
        websocket=websocket,
        user=user,
        conversation_id=conversation_id,
        chat_service=chat_service,
    )


async def broadcast_to_conversation_room(
    conversation_id: UUID, message: Dict[str, Any], exclude_user: Optional[str] = None
) -> int:
    """
    Convenient function to broadcast to a conversation room.

    Args:
        conversation_id: Conversation UUID
        message: Message to broadcast
        exclude_user: User to exclude from broadcast

    Returns:
        Number of successful broadcasts
    """
    chat_room_manager = get_chat_room_manager()
    return await chat_room_manager.broadcast_to_conversation(
        conversation_id=conversation_id, message=message, exclude_user=exclude_user
    )
