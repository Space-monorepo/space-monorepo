from typing import List
from uuid import UUID

from app.api.chat.exceptions import (
    ConversationAlreadyExistsError,
    ConversationNotFoundError,
    FileNotFoundError,
    InvalidMessageTypeError,
    MessageNotFoundError,
    MessageTooLongError,
    UnauthorizedConversationAccessError,
    UnauthorizedMessageAccessError,
    UnexpectedChatError,
    UsersNotConnectedError,
)
from app.api.chat.model import Conversation, Message
from app.api.chat.schema import (
    ConversationParticipant,
    ConversationResponse,
    ConversationSearchParams,
    MessageAttachmentResponse,
    MessageResponse,
    MessageSearchParams,
    MessageTypeEnum,
)
from app.api.users.service import UserService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse


class ChatService:
    # Chat configuration constants
    MAX_MESSAGE_LENGTH = 2000
    RATE_LIMIT_MESSAGES_PER_MINUTE = 60

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.conversation_repo = tm.get_conversation_repository()
        self.message_repo = tm.get_message_repository()
        self.attachment_repo = tm.get_message_attachment_repository()
        self.user_service = UserService(tm)

    # Conversation methods

    def create_conversation(
        self, user_id: UUID, participant_user_id: UUID
    ) -> ConversationResponse:
        """Create a new conversation between two users"""
        # Validate users exist
        self.user_service.get_user(user_id)
        self.user_service.get_user(participant_user_id)

        # Check if users are connected
        connection = self.user_service.get_connection_status(
            user_id, participant_user_id
        )
        if not connection or str(connection.status) != 'accepted':
            raise UsersNotConnectedError(
                'Users must be connected to start a conversation'
            )

        # Check if conversation already exists
        existing_conversation = self.conversation_repo.find_conversation_between_users(
            user_id, participant_user_id
        )
        if existing_conversation:
            raise ConversationAlreadyExistsError(
                'Conversation already exists between these users'
            )

        try:
            # Create conversation
            conversation = self.conversation_repo.create_conversation(
                user_id, participant_user_id
            )

            # Return response with participants
            unread_count = self.message_repo.count_unread_messages(
                UUID(str(conversation.id)), user_id
            )
            return ChatService._map_conversation_to_response(
                conversation, user_id, unread_count
            )
        except Exception as e:
            raise UnexpectedChatError('Unexpected error creating conversation') from e

    def get_conversation(
        self, conversation_id: UUID, user_id: UUID
    ) -> ConversationResponse:
        """Get conversation details"""
        # Validate conversation exists and user participates
        conversation = self._get_conversation_with_validation(conversation_id, user_id)

        unread_count = self.message_repo.count_unread_messages(
            UUID(str(conversation.id)), user_id
        )
        return ChatService._map_conversation_to_response(
            conversation, user_id, unread_count
        )

    def list_user_conversations(
        self, user_id: UUID, params: ConversationSearchParams
    ) -> PaginationResponse[ConversationResponse]:
        """List conversations for a user with search and pagination"""
        try:
            conversations, total = self.conversation_repo.list_user_conversations(
                user_id, params
            )

            conversation_responses = []
            for conv in conversations:
                unread_count = self.message_repo.count_unread_messages(
                    UUID(str(conv.id)), user_id
                )
                conversation_responses.append(
                    ChatService._map_conversation_to_response(
                        conv, user_id, unread_count
                    )
                )

            return PaginationResponse(
                items=conversation_responses,
                total=total,
                has_more=total > (params.offset or 0) + (params.limit or 20),
                current_offset=params.offset or 0,
                current_limit=params.limit or 20,
            )
        except Exception as e:
            raise UnexpectedChatError('Unexpected error listing conversations') from e

    # Message methods

    def send_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str,
        reply_to_message_id: UUID | None = None,
    ) -> MessageResponse:
        """Send a text message"""
        # Validate conversation and user participation
        self._get_conversation_with_validation(conversation_id, sender_id)

        # Validate message content
        if not content or not content.strip():
            raise InvalidMessageTypeError('Text messages must have content')

        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise MessageTooLongError(
                f'Message content cannot exceed {self.MAX_MESSAGE_LENGTH} characters'
            )

        # Check rate limit
        self._check_rate_limit(sender_id)

        # Validate reply message if provided
        if reply_to_message_id:
            reply_message = self.message_repo.get_by_id(reply_to_message_id)
            if not reply_message or str(reply_message.conversation_id) != str(
                conversation_id
            ):
                raise MessageNotFoundError(
                    'Reply message not found in this conversation'
                )

        try:
            # Create message
            message = self.message_repo.create_message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content.strip(),
                message_type=MessageTypeEnum.text.value,
                reply_to_message_id=reply_to_message_id,
            )

            # Update conversation's last message
            self.conversation_repo.update_last_message(
                conversation_id, UUID(str(message.id))
            )

            # Get message with details for response
            message_with_details = self.message_repo.get_message_with_details(
                UUID(str(message.id))
            )

            return ChatService._map_message_to_response(message_with_details)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error sending message') from e

    def send_message_with_attachment(  # noqa: PLR0913, PLR0917
        self,
        conversation_id: UUID,
        sender_id: UUID,
        message_type: MessageTypeEnum,
        file_name: str,
        file_size: int,
        file_type: str,
        file_url: str,
        thumbnail_url: str | None = None,
        content: str | None = None,
        reply_to_message_id: UUID | None = None,
    ) -> MessageResponse:
        """Send a message with file attachment"""
        # Validate conversation and user participation
        self._get_conversation_with_validation(conversation_id, sender_id)

        # Validate message type
        if message_type == MessageTypeEnum.text:
            raise InvalidMessageTypeError('Use send_message for text messages')

        # Check rate limit
        self._check_rate_limit(sender_id)

        # Validate reply message if provided
        if reply_to_message_id:
            reply_message = self.message_repo.get_by_id(reply_to_message_id)
            if not reply_message or str(reply_message.conversation_id) != str(
                conversation_id
            ):
                raise MessageNotFoundError(
                    'Reply message not found in this conversation'
                )

        try:
            # Create message
            message = self.message_repo.create_message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content.strip() if content else None,
                message_type=message_type.value,
                reply_to_message_id=reply_to_message_id,
            )

            # Create attachment
            self.attachment_repo.create_attachment(
                message_id=UUID(str(message.id)),
                file_name=file_name,
                file_size=file_size,
                file_type=file_type,
                file_url=file_url,
                thumbnail_url=thumbnail_url,
            )

            # Update conversation's last message
            self.conversation_repo.update_last_message(
                conversation_id, UUID(str(message.id))
            )

            # Get message with details for response
            message_with_details = self.message_repo.get_message_with_details(
                UUID(str(message.id))
            )

            return ChatService._map_message_to_response(message_with_details)
        except Exception as e:
            raise UnexpectedChatError(
                'Unexpected error sending message with attachment'
            ) from e

    def get_conversation_messages(
        self, conversation_id: UUID, user_id: UUID, params: MessageSearchParams
    ) -> PaginationResponse[MessageResponse]:
        """Get messages in a conversation with pagination"""
        # Validate conversation and user participation
        self._get_conversation_with_validation(conversation_id, user_id)

        try:
            messages, total = self.message_repo.list_conversation_messages(
                conversation_id, params
            )

            message_responses = [
                ChatService._map_message_to_response(msg) for msg in messages
            ]

            return PaginationResponse(
                items=message_responses,
                total=total,
                has_more=total > (params.offset or 0) + (params.limit or 50),
                current_offset=params.offset or 0,
                current_limit=params.limit or 50,
            )
        except Exception as e:
            raise UnexpectedChatError(
                'Unexpected error getting conversation messages'
            ) from e

    def mark_message_as_read(self, message_id: UUID, user_id: UUID) -> bool:
        """Mark a message as read by the current user"""
        # Get message and validate access
        message = self.message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundError('Message not found')

        # Validate user participates in conversation
        if not self.conversation_repo.validate_user_participation(
            UUID(str(message.conversation_id)), user_id
        ):
            raise UnauthorizedMessageAccessError(
                'You do not have access to this message'
            )

        try:
            return self.message_repo.mark_message_as_read(message_id, user_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error marking message as read') from e

    def bulk_mark_messages_as_read(self, message_ids: List[UUID], user_id: UUID) -> int:
        """Mark multiple messages as read"""
        if not message_ids:
            return 0

        # Validate all messages exist and user has access
        for message_id in message_ids:
            message = self.message_repo.get_by_id(message_id)
            if not message:
                raise MessageNotFoundError(f'Message {message_id} not found')

            if not self.conversation_repo.validate_user_participation(
                UUID(str(message.conversation_id)), user_id
            ):
                raise UnauthorizedMessageAccessError(
                    f'You do not have access to message {message_id}'
                )

        try:
            return self.message_repo.bulk_mark_as_read(message_ids, user_id)
        except Exception as e:
            raise UnexpectedChatError(
                'Unexpected error bulk marking messages as read'
            ) from e

    def get_unread_count(self, conversation_id: UUID, user_id: UUID) -> int:
        """Get count of unread messages in a conversation for the user"""
        # Validate conversation and user participation
        self._get_conversation_with_validation(conversation_id, user_id)

        try:
            return self.message_repo.count_unread_messages(conversation_id, user_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error getting unread count') from e

    def delete_message(self, message_id: UUID, user_id: UUID) -> bool:
        """Delete a message (only by sender)"""
        # Validate message ownership
        if not self.message_repo.validate_message_ownership(message_id, user_id):
            raise UnauthorizedMessageAccessError('You can only delete your own messages')

        try:
            return self.message_repo.delete_message(message_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error deleting message') from e

    # Attachment methods

    def get_attachment(
        self, attachment_id: UUID, user_id: UUID
    ) -> MessageAttachmentResponse:
        """Get attachment details with access validation"""
        attachment = self.attachment_repo.get_attachment_with_message(attachment_id)
        if not attachment:
            raise FileNotFoundError('Attachment not found')

        # Validate user has access to the conversation
        conversation_id = UUID(str(attachment.message.conversation_id))
        if not self.conversation_repo.validate_user_participation(
            conversation_id, user_id
        ):
            raise UnauthorizedMessageAccessError(
                'You do not have access to this attachment'
            )

        return MessageAttachmentResponse.model_validate(attachment)

    def delete_attachment(self, attachment_id: UUID, user_id: UUID) -> bool:
        """Delete an attachment (only by message sender)"""
        attachment = self.attachment_repo.get_attachment_with_message(attachment_id)
        if not attachment:
            raise FileNotFoundError('Attachment not found')

        # Validate user owns the message
        if str(attachment.message.sender_id) != str(user_id):
            raise UnauthorizedMessageAccessError(
                'You can only delete attachments from your own messages'
            )

        try:
            return self.attachment_repo.delete_attachment(attachment_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error deleting attachment') from e

    # Private helper methods

    def _get_conversation_with_validation(
        self, conversation_id: UUID, user_id: UUID
    ) -> Conversation:
        """Get conversation and validate user participation"""
        conversation = self.conversation_repo.get_conversation_with_participants(
            conversation_id
        )
        if not conversation:
            raise ConversationNotFoundError('Conversation not found')

        if not self.conversation_repo.validate_user_participation(
            conversation_id, user_id
        ):
            raise UnauthorizedConversationAccessError(
                'You do not participate in this conversation'
            )

        return conversation

    @staticmethod
    def _map_conversation_to_response(
        conversation: Conversation, current_user_id: UUID, unread_count: int
    ) -> ConversationResponse:
        """Map conversation model to response schema"""
        # Get participants
        user1 = ConversationParticipant.model_validate(conversation.user1)
        user2 = ConversationParticipant.model_validate(conversation.user2)

        # Determine other participant
        if str(current_user_id) == str(conversation.user1_id):
            other_participant = user2
        else:
            other_participant = user1

        # Map last message if exists
        last_message = None
        if conversation.last_message:
            last_message = ChatService._map_message_to_response(
                conversation.last_message
            )

        # Create response using model_validate to handle SQLAlchemy columns
        conversation_dict = {
            'id': UUID(str(conversation.id)),
            'user1_id': UUID(str(conversation.user1_id)),
            'user2_id': UUID(str(conversation.user2_id)),
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'last_message_id': UUID(str(conversation.last_message_id))
            if str(conversation.last_message_id or '')
            else None,
            'user1': user1,
            'user2': user2,
            'last_message': last_message,
            'unread_count': unread_count,
            'other_participant': other_participant,
        }

        return ConversationResponse.model_validate(conversation_dict)

    @staticmethod
    def _map_message_to_response(message: Message) -> MessageResponse:
        """Map message model to response schema"""
        # Map sender
        sender = ConversationParticipant.model_validate(message.sender)

        # Map reply message if exists
        reply_to_message = None
        if message.reply_to_message:
            reply_sender = ConversationParticipant.model_validate(
                message.reply_to_message.sender
            )

            reply_dict = {
                'id': UUID(str(message.reply_to_message.id)),
                'conversation_id': UUID(str(message.reply_to_message.conversation_id)),
                'sender_id': UUID(str(message.reply_to_message.sender_id)),
                'content': message.reply_to_message.content,
                'message_type': MessageTypeEnum(
                    str(message.reply_to_message.message_type)
                ),
                'created_at': message.reply_to_message.created_at,
                'is_read': message.reply_to_message.is_read,
                'reply_to_message_id': UUID(
                    str(message.reply_to_message.reply_to_message_id)
                )
                if message.reply_to_message.reply_to_message_id
                else None,
                'sender': reply_sender,
                'reply_to_message': None,  # Avoid deep nesting
                'attachments': [],
            }

            reply_to_message = MessageResponse.model_validate(reply_dict)

        # Map attachments
        attachments = [
            MessageAttachmentResponse.model_validate(attachment)
            for attachment in message.attachments
        ]

        # Create response using model_validate to handle SQLAlchemy columns
        message_dict = {
            'id': UUID(str(message.id)),
            'conversation_id': UUID(str(message.conversation_id)),
            'sender_id': UUID(str(message.sender_id)),
            'content': message.content,
            'message_type': MessageTypeEnum(str(message.message_type)),
            'created_at': message.created_at,
            'is_read': message.is_read,
            'reply_to_message_id': UUID(str(message.reply_to_message_id))
            if str(message.reply_to_message_id or '')
            else None,
            'sender': sender,
            'reply_to_message': reply_to_message,
            'attachments': attachments,
        }

        return MessageResponse.model_validate(message_dict)

    def _check_rate_limit(self, user_id: UUID) -> None:
        """Check if user has exceeded rate limit for sending messages"""
        # For now, implement a simple time-based check
        # In production, this would use Redis or similar cache

        # This is a simplified implementation
        # In a real system, you'd track message counts per user per minute
        # For the scope of this implementation, we'll skip the actual rate limiting
        # but keep the method for future implementation
        pass

    # Connection validation integration

    def validate_users_can_chat(self, user1_id: UUID, user2_id: UUID) -> bool:
        """Validate that two users can chat (are connected)"""
        connection = self.user_service.get_connection_status(user1_id, user2_id)
        return connection is not None and str(connection.status) == 'accepted'
