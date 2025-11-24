from typing import List, Literal
from uuid import UUID

from cloudinary import uploader as cloudinary_uploader
from fastapi import UploadFile

from app.api.chat.exceptions import (
    CannotCreateSelfConversationError,
    ConversationAlreadyExistsError,
    ConversationNotFoundError,
    FileNotFoundError,
    FileSizeExceededError,
    FileUploadError,
    InvalidFileTypeError,
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
from app.core.config import configure_cloudinary
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse


class ChatService:
    MAX_MESSAGE_LENGTH = 2000
    RATE_LIMIT_MESSAGES_PER_MINUTE = 60

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.conversation_repo = tm.get_conversation_repository()
        self.message_repo = tm.get_message_repository()
        self.attachment_repo = tm.get_message_attachment_repository()
        self.user_service = UserService(tm)
        self.upload_service = CloudinaryUploadService()

    def create_conversation(
        self, user_id: UUID, participant_user_id: UUID
    ) -> ConversationResponse:
        """Create a new conversation between two users"""
        if user_id == participant_user_id:
            raise CannotCreateSelfConversationError(
                'Cannot create a conversation with yourself'
            )
        self.user_service.get_user(user_id)
        self.user_service.get_user(participant_user_id)
        connection = self.user_service.get_connection_status(
            user_id, participant_user_id
        )
        if not connection or str(connection.status) != 'accepted':
            raise UsersNotConnectedError(
                'Users must be connected to start a conversation'
            )
        existing_conversation = self.conversation_repo.find_conversation_between_users(
            user_id, participant_user_id
        )
        if existing_conversation:
            raise ConversationAlreadyExistsError(
                'Conversation already exists between these users'
            )
        try:
            conversation = self.conversation_repo.create_conversation(
                user_id, participant_user_id
            )
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

    def send_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str,
        reply_to_message_id: UUID | None = None,
    ) -> MessageResponse:
        """Send a text message"""
        self._get_conversation_with_validation(conversation_id, sender_id)
        if not content or not content.strip():
            raise InvalidMessageTypeError('Text messages must have content')

        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise MessageTooLongError(
                f'Message content cannot exceed {self.MAX_MESSAGE_LENGTH} characters'
            )

        if reply_to_message_id:
            reply_message = self.message_repo.get_by_id(reply_to_message_id)
            if not reply_message or str(reply_message.conversation_id) != str(
                conversation_id
            ):
                raise MessageNotFoundError(
                    'Reply message not found in this conversation'
                )
        try:
            message = self.message_repo.create_message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content.strip(),
                message_type=MessageTypeEnum.text.value,
                reply_to_message_id=reply_to_message_id,
            )
            self.conversation_repo.update_last_message(
                conversation_id, UUID(str(message.id))
            )
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
        file: UploadFile,
        message_type: MessageTypeEnum,
        content: str | None = None,
        reply_to_message_id: UUID | None = None,
    ) -> MessageResponse:
        """Send a message with file attachment"""
        self._get_conversation_with_validation(conversation_id, sender_id)
        if message_type == MessageTypeEnum.text:
            raise InvalidMessageTypeError('Use send_message for text messages')
        if reply_to_message_id:
            reply_message = self.message_repo.get_by_id(reply_to_message_id)
            if not reply_message or str(reply_message.conversation_id) != str(
                conversation_id
            ):
                raise MessageNotFoundError(
                    'Reply message not found in this conversation'
                )
        try:
            upload_result = self.upload_service.upload_file(file, message_type)
            message = self.message_repo.create_message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content.strip() if content else None,
                message_type=message_type.value,
                reply_to_message_id=reply_to_message_id,
            )
            self.attachment_repo.create_attachment(
                message_id=UUID(str(message.id)),
                file_name=file.filename or 'attachment',
                file_size=int(upload_result['size']),
                file_type=file.content_type or 'application/octet-stream',
                file_url=str(upload_result['url']),
                public_id=str(upload_result['public_id']),
                thumbnail_url=str(upload_result['thumbnail_url'])
                if upload_result.get('thumbnail_url')
                else None,
            )
            self.conversation_repo.update_last_message(
                conversation_id, UUID(str(message.id))
            )
            message_with_details = self.message_repo.get_message_with_details(
                UUID(str(message.id))
            )
            return ChatService._map_message_to_response(message_with_details)
        except (InvalidFileTypeError, FileUploadError):
            raise
        except Exception as e:
            raise UnexpectedChatError(
                'Unexpected error sending message with attachment'
            ) from e

    def get_conversation_messages(
        self, conversation_id: UUID, user_id: UUID, params: MessageSearchParams
    ) -> PaginationResponse[MessageResponse]:
        """Get messages in a conversation with pagination"""
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
        message = self.message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundError('Message not found')
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
        self._get_conversation_with_validation(conversation_id, user_id)
        try:
            return self.message_repo.count_unread_messages(conversation_id, user_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error getting unread count') from e

    def mark_conversation_messages_as_read(
        self, conversation_id: UUID, user_id: UUID, up_to_message_id: UUID | None = None
    ) -> int:
        """Mark all unread messages in a conversation as read (up to a specific message if provided)"""
        self._get_conversation_with_validation(conversation_id, user_id)
        try:
            message_ids = self.message_repo.get_unread_message_ids(
                conversation_id, user_id, up_to_message_id
            )
            if not message_ids:
                return 0
            return self.message_repo.bulk_mark_as_read(message_ids, user_id)
        except Exception as e:
            raise UnexpectedChatError(
                'Unexpected error marking conversation messages as read'
            ) from e

    def delete_message(self, message_id: UUID, user_id: UUID) -> bool:
        """Delete a message (only by sender)"""
        message = self.message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundError('Message not found')
        if str(message.sender_id) != str(user_id):
            raise UnauthorizedMessageAccessError('You can only delete your own messages')
        try:
            return self.message_repo.delete_message(message_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error deleting message') from e

    def get_attachment(
        self, attachment_id: UUID, user_id: UUID
    ) -> MessageAttachmentResponse:
        """Get attachment details with access validation"""
        attachment = self.attachment_repo.get_attachment_with_message(attachment_id)
        if not attachment:
            raise FileNotFoundError('Attachment not found')
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
        if str(attachment.message.sender_id) != str(user_id):
            raise UnauthorizedMessageAccessError(
                'You can only delete attachments from your own messages'
            )
        try:
            if attachment.public_id:
                resource_type = self.upload_service.get_resource_type_from_public_id(
                    attachment.public_id
                )
                self.upload_service.delete_file(attachment.public_id, resource_type)
            return self.attachment_repo.delete_attachment(attachment_id)
        except Exception as e:
            raise UnexpectedChatError('Unexpected error deleting attachment') from e

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
        user1 = ConversationParticipant.model_validate(conversation.user1)
        user2 = ConversationParticipant.model_validate(conversation.user2)
        if str(current_user_id) == str(conversation.user1_id):
            other_participant = user2
        else:
            other_participant = user1
        last_message = None
        if conversation.last_message:
            last_message = ChatService._map_message_to_response(
                conversation.last_message
            )
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
        sender = ConversationParticipant.model_validate(message.sender)
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
        attachments = [
            MessageAttachmentResponse.model_validate(attachment)
            for attachment in message.attachments
        ]
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

    def validate_users_can_chat(self, user1_id: UUID, user2_id: UUID) -> bool:
        """Validate that two users can chat (are connected)"""
        connection = self.user_service.get_connection_status(user1_id, user2_id)
        return connection is not None and str(connection.status) == 'accepted'


class CloudinaryUploadService:
    """Service for handling file uploads to Cloudinary"""

    # File size limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Allowed MIME types by category
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp',
    }

    ALLOWED_VIDEO_TYPES = {
        'video/mp4',
        'video/quicktime',
        'video/x-msvideo',  # AVI
        'video/webm',
    }

    ALLOWED_DOCUMENT_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    # Cloudinary folders
    CHAT_IMAGES_FOLDER = 'chat/images'
    CHAT_VIDEOS_FOLDER = 'chat/videos'
    CHAT_DOCUMENTS_FOLDER = 'chat/documents'

    def __init__(self):
        """Initialize the upload service and ensure Cloudinary is configured"""
        configure_cloudinary()

    @staticmethod
    def _get_file_size(file: UploadFile) -> int:
        """Get the size of an uploaded file"""
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        return size

    def _validate_file_size(self, file: UploadFile) -> None:
        """Validate that file size is within limits"""
        file_size = CloudinaryUploadService._get_file_size(file)
        if file_size > self.MAX_FILE_SIZE:
            raise FileSizeExceededError(
                f'File size ({file_size} bytes) exceeds maximum allowed size ({self.MAX_FILE_SIZE} bytes)'
            )

    def _validate_file_type(
        self, file: UploadFile, message_type: MessageTypeEnum
    ) -> None:
        """Validate that file type matches the message type"""
        content_type = file.content_type or ''

        if message_type == MessageTypeEnum.image:
            if content_type not in self.ALLOWED_IMAGE_TYPES:
                raise InvalidFileTypeError(
                    f'Invalid image type: {content_type}. Allowed types: {", ".join(self.ALLOWED_IMAGE_TYPES)}'
                )
        elif message_type == MessageTypeEnum.video:
            if content_type not in self.ALLOWED_VIDEO_TYPES:
                raise InvalidFileTypeError(
                    f'Invalid video type: {content_type}. Allowed types: {", ".join(self.ALLOWED_VIDEO_TYPES)}'
                )
        elif message_type == MessageTypeEnum.document:
            if content_type not in self.ALLOWED_DOCUMENT_TYPES:
                raise InvalidFileTypeError(
                    f'Invalid document type: {content_type}. Allowed types: {", ".join(self.ALLOWED_DOCUMENT_TYPES)}'
                )
        else:
            raise InvalidFileTypeError(f'Unsupported message type: {message_type}')

    def _get_folder_by_type(self, message_type: MessageTypeEnum) -> str:
        """Get the appropriate Cloudinary folder based on message type"""
        folder_map = {
            MessageTypeEnum.image: self.CHAT_IMAGES_FOLDER,
            MessageTypeEnum.video: self.CHAT_VIDEOS_FOLDER,
            MessageTypeEnum.document: self.CHAT_DOCUMENTS_FOLDER,
        }
        return folder_map.get(message_type, self.CHAT_IMAGES_FOLDER)

    @staticmethod
    def _get_resource_type(
        message_type: MessageTypeEnum,
    ) -> Literal['image', 'video', 'raw', 'auto']:
        """Get the appropriate Cloudinary resource type"""
        if message_type == MessageTypeEnum.image:
            return 'image'
        elif message_type == MessageTypeEnum.video:
            return 'video'
        elif message_type == MessageTypeEnum.document:
            return 'raw'
        return 'auto'

    def upload_file(
        self, file: UploadFile, message_type: MessageTypeEnum
    ) -> dict[str, str | int]:
        """
        Upload a file to Cloudinary

        Args:
            file: The file to upload
            message_type: Type of message (image, video, document)

        Returns:
            dict with keys: url, public_id, format, size, thumbnail_url (for images)

        Raises:
            FileSizeExceededError: If file is too large
            InvalidFileTypeError: If file type is not allowed
            FileUploadError: If upload fails
        """
        # Validate file
        self._validate_file_size(file)
        self._validate_file_type(file, message_type)

        try:
            # Get upload parameters
            folder = self._get_folder_by_type(message_type)
            resource_type = CloudinaryUploadService._get_resource_type(message_type)

            # Read file content
            file.file.seek(0)
            file_content = file.file.read()

            # Upload to Cloudinary
            upload_params = {
                'folder': folder,
                'resource_type': resource_type,
                'use_filename': True,
                'unique_filename': True,
            }

            # For images, generate a thumbnail
            if message_type == MessageTypeEnum.image:
                upload_params['eager'] = [
                    {'width': 300, 'height': 300, 'crop': 'fill', 'quality': 'auto'}
                ]
                upload_params['eager_async'] = False

            result = cloudinary_uploader.upload(file_content, **upload_params)

            # Prepare response data
            response_data = {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result.get('format', ''),
                'size': result.get('bytes', 0),
            }

            # Add thumbnail URL for images
            if message_type == MessageTypeEnum.image and 'eager' in result:
                if result['eager']:
                    response_data['thumbnail_url'] = result['eager'][0]['secure_url']

            return response_data

        except (FileSizeExceededError, InvalidFileTypeError):
            raise
        except Exception as e:
            raise FileUploadError(f'Failed to upload file: {str(e)}') from e

    @staticmethod
    def delete_file(public_id: str, resource_type: str = 'auto') -> bool:
        """
        Delete a file from Cloudinary

        Args:
            public_id: The Cloudinary public ID of the file
            resource_type: Type of resource (image, video, raw, auto)

        Returns:
            True if deletion was successful

        Raises:
            FileUploadError: If deletion fails
        """
        try:
            result = cloudinary_uploader.destroy(
                public_id, resource_type=resource_type, invalidate=True
            )
            return result.get('result') == 'ok'
        except Exception as e:
            raise FileUploadError(f'Failed to delete file: {str(e)}') from e

    def get_resource_type_from_public_id(self, public_id: str) -> str:
        """
        Determine resource type from public_id folder structure

        Args:
            public_id: The Cloudinary public ID

        Returns:
            Resource type (image, video, raw)
        """
        if public_id.startswith(self.CHAT_IMAGES_FOLDER):
            return 'image'
        elif public_id.startswith(self.CHAT_VIDEOS_FOLDER):
            return 'video'
        elif public_id.startswith(self.CHAT_DOCUMENTS_FOLDER):
            return 'raw'
        return 'auto'
