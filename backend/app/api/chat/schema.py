import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

from app.utils.schema import PaginationResponse


class MessageTypeEnum(str, Enum):
    text = 'text'
    image = 'image'
    document = 'document'
    audio = 'audio'
    video = 'video'
    system = 'system'


# User related schemas for responses
class ConversationParticipant(BaseModel):
    id: uuid.UUID = Field(..., description='The user ID')
    name: str = Field(..., description='The user name')
    profile_image_url: str | None = Field(None, description='The user profile image URL')

    model_config = ConfigDict(from_attributes=True)


# Message Attachment schemas
class MessageAttachmentCreate(BaseModel):
    file_name: str = Field(
        ..., min_length=1, max_length=255, description='The file name'
    )
    file_size: int = Field(..., gt=0, description='The file size in bytes')
    file_type: str = Field(
        ..., min_length=1, max_length=100, description='The MIME type'
    )
    file_url: str = Field(..., min_length=1, max_length=500, description='The file URL')
    thumbnail_url: str | None = Field(
        None, max_length=500, description='The thumbnail URL'
    )


class MessageAttachmentResponse(MessageAttachmentCreate):
    id: uuid.UUID = Field(..., description='The attachment ID')
    message_id: uuid.UUID = Field(..., description='The message ID')
    created_at: datetime = Field(..., description='The attachment creation timestamp')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'message_id': '123e4567-e89b-12d3-a456-426614174001',
                'file_name': 'document.pdf',
                'file_size': 1024000,
                'file_type': 'application/pdf',
                'file_url': 'https://storage.example.com/files/document.pdf',
                'thumbnail_url': 'https://storage.example.com/thumbnails/document.jpg',
                'created_at': '2021-01-01T00:00:00Z',
            }
        },
    )


# Message schemas
class MessageCreate(BaseModel):
    content: str | None = Field(
        None, max_length=2000, description='The message content (max 2000 chars)'
    )
    message_type: MessageTypeEnum = Field(
        MessageTypeEnum.text, description='The type of message'
    )
    reply_to_message_id: uuid.UUID | None = Field(
        None, description='The ID of the message being replied to'
    )

    @validator('content')
    def validate_content_for_text_messages(cls, v, values):
        message_type = values.get('message_type', MessageTypeEnum.text)
        if message_type == MessageTypeEnum.text and (not v or not v.strip()):
            raise ValueError('Text messages must have content')
        return v


class MessageWithAttachmentCreate(BaseModel):
    message_type: MessageTypeEnum = Field(..., description='The type of message')
    reply_to_message_id: uuid.UUID | None = Field(
        None, description='The ID of the message being replied to'
    )
    content: str | None = Field(
        None, max_length=2000, description='Optional message content for attachments'
    )

    @validator('message_type')
    def validate_attachment_message_type(cls, v):
        if v == MessageTypeEnum.text:
            raise ValueError('Use MessageCreate for text messages')
        return v


class MessageUpdate(BaseModel):
    is_read: bool = Field(..., description='Mark message as read/unread')


class MessageResponse(BaseModel):
    id: uuid.UUID = Field(..., description='The message ID')
    conversation_id: uuid.UUID = Field(..., description='The conversation ID')
    sender_id: uuid.UUID = Field(..., description='The sender user ID')
    content: str | None = Field(None, description='The message content')
    message_type: MessageTypeEnum = Field(..., description='The type of message')
    created_at: datetime = Field(..., description='The message creation timestamp')
    is_read: bool = Field(..., description='Whether the message has been read')
    reply_to_message_id: uuid.UUID | None = Field(
        None, description='The ID of the message being replied to'
    )

    # Relationships
    sender: ConversationParticipant = Field(..., description='The message sender')
    reply_to_message: Optional['MessageResponse'] = Field(
        None, description='The message being replied to'
    )
    attachments: List[MessageAttachmentResponse] = Field(
        default_factory=list, description='Message attachments'
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174001',
                'sender_id': '123e4567-e89b-12d3-a456-426614174002',
                'content': 'Hello, how are you?',
                'message_type': 'text',
                'created_at': '2021-01-01T00:00:00Z',
                'is_read': False,
                'reply_to_message_id': None,
                'sender': {
                    'id': '123e4567-e89b-12d3-a456-426614174002',
                    'name': 'John Doe',
                    'profile_image_url': 'https://example.com/profile.jpg',
                },
                'reply_to_message': None,
                'attachments': [],
            }
        },
    )


# Conversation schemas
class ConversationCreate(BaseModel):
    participant_user_id: uuid.UUID = Field(
        ..., description='The ID of the user to start a conversation with'
    )


class ConversationResponse(BaseModel):
    id: uuid.UUID = Field(..., description='The conversation ID')
    user1_id: uuid.UUID = Field(..., description='The first user ID')
    user2_id: uuid.UUID = Field(..., description='The second user ID')
    created_at: datetime = Field(..., description='The conversation creation timestamp')
    updated_at: datetime = Field(
        ..., description='The conversation last update timestamp'
    )
    last_message_id: uuid.UUID | None = Field(
        None, description='The ID of the last message'
    )

    # Relationships
    user1: ConversationParticipant = Field(..., description='The first participant')
    user2: ConversationParticipant = Field(..., description='The second participant')
    last_message: MessageResponse | None = Field(
        None, description='The last message in the conversation'
    )

    # Computed fields
    unread_count: int = Field(
        0, description='Number of unread messages for the current user'
    )
    other_participant: ConversationParticipant = Field(
        ..., description='The other participant (not the current user)'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'user1_id': '123e4567-e89b-12d3-a456-426614174001',
                'user2_id': '123e4567-e89b-12d3-a456-426614174002',
                'created_at': '2021-01-01T00:00:00Z',
                'updated_at': '2021-01-01T00:00:00Z',
                'last_message_id': '123e4567-e89b-12d3-a456-426614174003',
                'user1': {
                    'id': '123e4567-e89b-12d3-a456-426614174001',
                    'name': 'John Doe',
                    'profile_image_url': 'https://example.com/john.jpg',
                },
                'user2': {
                    'id': '123e4567-e89b-12d3-a456-426614174002',
                    'name': 'Jane Smith',
                    'profile_image_url': 'https://example.com/jane.jpg',
                },
                'last_message': {
                    'id': '123e4567-e89b-12d3-a456-426614174003',
                    'content': 'See you tomorrow!',
                    'message_type': 'text',
                    'created_at': '2021-01-01T12:00:00Z',
                },
                'unread_count': 2,
                'other_participant': {
                    'id': '123e4567-e89b-12d3-a456-426614174002',
                    'name': 'Jane Smith',
                    'profile_image_url': 'https://example.com/jane.jpg',
                },
            }
        },
    )


# Using the existing PaginationResponse for consistency
ConversationListResponse = PaginationResponse[ConversationResponse]


# Using the existing PaginationResponse for consistency
MessageListResponse = PaginationResponse[MessageResponse]


# WebSocket event schemas
class WebSocketMessage(BaseModel):
    event: str = Field(..., description='The event type')
    data: dict = Field(..., description='The event data')


class TypingEvent(BaseModel):
    conversation_id: uuid.UUID = Field(..., description='The conversation ID')
    user_id: uuid.UUID = Field(..., description='The user ID who is typing')
    is_typing: bool = Field(..., description='Whether the user is typing')


class MessageReadEvent(BaseModel):
    message_id: uuid.UUID = Field(..., description='The message ID that was read')
    read_by_user_id: uuid.UUID = Field(
        ..., description='The user ID who read the message'
    )


class JoinConversationEvent(BaseModel):
    conversation_id: uuid.UUID = Field(..., description='The conversation ID to join')


class SendMessageEvent(BaseModel):
    conversation_id: uuid.UUID = Field(..., description='The conversation ID')
    content: str = Field(..., max_length=2000, description='The message content')
    reply_to_message_id: uuid.UUID | None = Field(
        None, description='The ID of the message being replied to'
    )


# File upload validation schemas
class FileUploadLimits(BaseModel):
    max_size_mb: int
    allowed_extensions: List[str]
    allowed_mime_types: List[str]


class ImageFileValidation(BaseModel):
    max_size_mb: int = Field(10, description='Maximum size in MB for images')
    allowed_extensions: List[str] = Field(
        default=['jpg', 'jpeg', 'png', 'gif', 'webp'],
        description='Allowed image extensions',
    )
    allowed_mime_types: List[str] = Field(
        default=['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        description='Allowed MIME types for images',
    )


class DocumentFileValidation(BaseModel):
    max_size_mb: int = Field(25, description='Maximum size in MB for documents')
    allowed_extensions: List[str] = Field(
        default=['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'],
        description='Allowed document extensions',
    )
    allowed_mime_types: List[str] = Field(
        default=[
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        ],
        description='Allowed MIME types for documents',
    )


class VideoFileValidation(BaseModel):
    max_size_mb: int = Field(50, description='Maximum size in MB for videos')
    max_duration_minutes: int = Field(2, description='Maximum duration in minutes')
    allowed_extensions: List[str] = Field(
        default=['mp4', 'webm', 'mov'], description='Allowed video extensions'
    )
    allowed_mime_types: List[str] = Field(
        default=['video/mp4', 'video/webm', 'video/quicktime'],
        description='Allowed MIME types for videos',
    )


class AudioFileValidation(BaseModel):
    max_size_mb: int = Field(10, description='Maximum size in MB for audio')
    max_duration_minutes: int = Field(5, description='Maximum duration in minutes')
    allowed_extensions: List[str] = Field(
        default=['mp3', 'wav', 'ogg', 'm4a'], description='Allowed audio extensions'
    )
    allowed_mime_types: List[str] = Field(
        default=['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'],
        description='Allowed MIME types for audio',
    )


class FileValidationResult(BaseModel):
    is_valid: bool = Field(..., description='Whether the file is valid')
    error_message: str | None = Field(
        None, description='Error message if validation failed'
    )
    file_info: dict | None = Field(None, description='File information if valid')
    virus_scan_passed: bool = Field(True, description='Whether virus scan passed')


# Search and filter schemas - custom implementation for chat-specific needs
class ConversationSearchParams(BaseModel):
    """
    Search params for conversations with chat-specific functionality.
    """

    name: str | None = Field(
        None, max_length=100, description='Search term for participant names'
    )
    offset: int | None = Field(0, description='The offset to apply to the search')
    limit: int | None = Field(
        20, ge=1, le=100, description='The limit to apply to the search'
    )

    model_config = ConfigDict(
        json_schema_extra={'example': {'name': 'john', 'offset': 0, 'limit': 20}}
    )


class MessageSearchParams(BaseModel):
    """
    Message search params with reverse pagination support.
    Uses offset/limit but also supports before_message_id for chat-specific needs.
    """

    offset: int | None = Field(0, description='The offset to apply to the search')
    limit: int | None = Field(
        50, ge=1, le=100, description='The limit to apply to the search'
    )
    before_message_id: uuid.UUID | None = Field(
        None, description='Get messages before this message ID (for reverse pagination)'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {'offset': 0, 'limit': 50, 'before_message_id': None}
        }
    )


# Connection status validation schema (for integration with users domain)
class ConnectionStatusCheck(BaseModel):
    user1_id: uuid.UUID = Field(..., description='First user ID')
    user2_id: uuid.UUID = Field(..., description='Second user ID')
    is_connected: bool = Field(..., description='Whether users are connected')

    model_config = ConfigDict(from_attributes=True)


# Rate limiting schemas
class RateLimitInfo(BaseModel):
    messages_sent: int = Field(
        ..., description='Number of messages sent in current window'
    )
    limit: int = Field(..., description='Maximum messages allowed per window')
    window_minutes: int = Field(..., description='Time window in minutes')
    reset_at: datetime = Field(..., description='When the limit resets')

    model_config = ConfigDict(from_attributes=True)


# Error response schemas
class ChatErrorResponse(BaseModel):
    error_code: str = Field(..., description='Error code')
    message: str = Field(..., description='Error message')
    details: dict | None = Field(None, description='Additional error details')

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'error_code': 'CONVERSATION_NOT_FOUND',
                'message': 'Conversation not found or you do not have access to it',
                'details': None,
            }
        }
    )


# Bulk operations schemas
class BulkMarkAsReadRequest(BaseModel):
    message_ids: List[uuid.UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description='List of message IDs to mark as read',
    )


class BulkMarkAsReadResponse(BaseModel):
    marked_count: int = Field(..., description='Number of messages marked as read')
    failed_ids: List[uuid.UUID] = Field(
        default_factory=list, description='IDs that failed to be marked'
    )

    model_config = ConfigDict(from_attributes=True)


# Chat configuration and constants schemas
class ChatValidationConstants(BaseModel):
    max_message_length: int = Field(2000, description='Maximum message content length')
    rate_limit_messages_per_minute: int = Field(
        60, description='Rate limit for messages per minute'
    )
    max_file_size_mb: dict = Field(
        default={'image': 10, 'document': 25, 'video': 50, 'audio': 10},
        description='Maximum file sizes by type in MB',
    )
    max_media_duration_minutes: dict = Field(
        default={'video': 2, 'audio': 5},
        description='Maximum media duration by type in minutes',
    )

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'max_message_length': 2000,
                'rate_limit_messages_per_minute': 60,
                'max_file_size_mb': {
                    'image': 10,
                    'document': 25,
                    'video': 50,
                    'audio': 10,
                },
                'max_media_duration_minutes': {'video': 2, 'audio': 5},
            }
        }
    )


class ConversationParticipantInfo(BaseModel):
    """Extended participant info for conversation details"""

    id: uuid.UUID = Field(..., description='The user ID')
    name: str = Field(..., description='The user name')
    profile_image_url: str | None = Field(None, description='The user profile image URL')
    last_seen: datetime | None = Field(None, description='Last time user was online')
    is_online: bool = Field(False, description='Whether user is currently online')

    model_config = ConfigDict(from_attributes=True)


# Count response schemas
class UnreadCountResponse(BaseModel):
    """Response for unread message count"""

    unread_count: int = Field(..., ge=0, description='Number of unread messages')

    model_config = ConfigDict(json_schema_extra={'example': {'unread_count': 5}})


# Update MessageResponse to resolve forward reference
MessageResponse.model_rebuild()
