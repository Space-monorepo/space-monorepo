from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.api.chat.schema import MessageTypeEnum
from app.core.websocket.events import WebSocketEvent

MAX_ATTACHMENT_FILE_SIZE_BYTES = 52_428_800
MAX_BULK_MARK_READ = 100


class ChatEventType(str, Enum):
    SEND_MESSAGE = 'send_message'
    MESSAGE_SENT = 'message_sent'
    MESSAGE_RECEIVED = 'message_received'
    MESSAGE_WITH_ATTACHMENT = 'send_message_with_attachment'
    JOIN_CONVERSATION = 'join_conversation'
    LEAVE_CONVERSATION = 'leave_conversation'
    CONVERSATION_JOINED = 'conversation_joined'
    CONVERSATION_LEFT = 'conversation_left'
    TYPING = 'typing'
    STOP_TYPING = 'stop_typing'
    USER_TYPING = 'user_typing'
    USER_STOPPED_TYPING = 'user_stopped_typing'
    MARK_MESSAGE_READ = 'mark_message_read'
    MESSAGE_READ = 'message_read'
    BULK_MARK_READ = 'bulk_mark_read'
    USER_JOINED_CONVERSATION = 'user_joined_conversation'
    USER_LEFT_CONVERSATION = 'user_left_conversation'
    USER_ONLINE = 'user_online'
    USER_OFFLINE = 'user_offline'
    CHAT_ERROR = 'chat_error'
    PERMISSION_ERROR = 'permission_error'


class ChatMessageEvent(WebSocketEvent):
    """Event for sending a text message."""

    type: Literal['send_message'] = Field(default=ChatEventType.SEND_MESSAGE)
    conversation_id: UUID
    content: str = Field(..., min_length=1, max_length=2000)
    reply_to_message_id: Optional[UUID] = None

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class MessageWithAttachmentEvent(WebSocketEvent):
    """Event for sending a message with attachment."""

    type: Literal['send_message_with_attachment'] = Field(
        default=ChatEventType.MESSAGE_WITH_ATTACHMENT
    )
    conversation_id: UUID
    content: Optional[str] = Field(None, max_length=2000)
    message_type: MessageTypeEnum
    file_name: str
    file_data: str
    file_size: int
    content_type: str
    reply_to_message_id: Optional[UUID] = None

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        if v > MAX_ATTACHMENT_FILE_SIZE_BYTES:
            raise ValueError('File size cannot exceed 50MB')
        return v


class JoinConversationEvent(WebSocketEvent):
    """Event for joining a conversation."""

    type: Literal['join_conversation'] = Field(default=ChatEventType.JOIN_CONVERSATION)
    conversation_id: UUID


class LeaveConversationEvent(WebSocketEvent):
    """Event for leaving a conversation."""

    type: Literal['leave_conversation'] = Field(default=ChatEventType.LEAVE_CONVERSATION)
    conversation_id: UUID


class TypingEvent(WebSocketEvent):
    """Event indicating user started typing."""

    type: Literal['typing'] = Field(default=ChatEventType.TYPING)
    conversation_id: UUID


class StopTypingEvent(WebSocketEvent):
    """Event indicating user stopped typing."""

    type: Literal['stop_typing'] = Field(default=ChatEventType.STOP_TYPING)
    conversation_id: UUID


class MarkMessageReadEvent(WebSocketEvent):
    """Event for marking a message as read."""

    type: Literal['mark_message_read'] = Field(default=ChatEventType.MARK_MESSAGE_READ)
    message_id: UUID
    conversation_id: UUID


class BulkMarkReadEvent(WebSocketEvent):
    """Event for marking multiple messages as read."""

    type: Literal['bulk_mark_read'] = Field(default=ChatEventType.BULK_MARK_READ)
    conversation_id: UUID
    message_ids: List[UUID]
    up_to_message_id: Optional[UUID] = None

    @field_validator('message_ids')
    @classmethod
    def validate_message_ids(cls, v):
        if len(v) > MAX_BULK_MARK_READ:
            raise ValueError('Cannot mark more than 100 messages at once')
        return v


class MessageReceivedEvent(WebSocketEvent):
    """Event broadcast when new message is received."""

    type: Literal['message_received'] = Field(default=ChatEventType.MESSAGE_RECEIVED)
    conversation_id: UUID
    message: Dict[str, Any]


class UserTypingEvent(WebSocketEvent):
    """Event broadcast when user starts typing."""

    type: Literal['user_typing'] = Field(default=ChatEventType.USER_TYPING)
    conversation_id: UUID
    user_id: UUID
    user_name: str


class UserStoppedTypingEvent(WebSocketEvent):
    """Event broadcast when user stops typing."""

    type: Literal['user_stopped_typing'] = Field(
        default=ChatEventType.USER_STOPPED_TYPING
    )
    conversation_id: UUID
    user_id: UUID
    user_name: str


class MessageReadEvent(WebSocketEvent):
    """Event broadcast when message is marked as read."""

    type: Literal['message_read'] = Field(default=ChatEventType.MESSAGE_READ)
    conversation_id: UUID
    message_id: UUID
    read_by_user_id: UUID
    read_by_user_name: str
    read_at: str


class UserJoinedConversationEvent(WebSocketEvent):
    """Event broadcast when user joins conversation."""

    type: Literal['user_joined_conversation'] = Field(
        default=ChatEventType.USER_JOINED_CONVERSATION
    )
    conversation_id: UUID
    user_id: UUID
    user_name: str
    joined_at: str


class UserLeftConversationEvent(WebSocketEvent):
    """Event broadcast when user leaves conversation."""

    type: Literal['user_left_conversation'] = Field(
        default=ChatEventType.USER_LEFT_CONVERSATION
    )
    conversation_id: UUID
    user_id: UUID
    user_name: str
    left_at: str


class ConversationJoinedEvent(WebSocketEvent):
    """Confirmation event for joining conversation."""

    type: Literal['conversation_joined'] = Field(
        default=ChatEventType.CONVERSATION_JOINED
    )
    conversation_id: UUID
    participant_count: int
    unread_count: int


class ConversationLeftEvent(WebSocketEvent):
    """Confirmation event for leaving conversation."""

    type: Literal['conversation_left'] = Field(default=ChatEventType.CONVERSATION_LEFT)
    conversation_id: UUID


class ChatErrorEvent(WebSocketEvent):
    """Event for chat-specific errors."""

    type: Literal['chat_error'] = Field(default=ChatEventType.CHAT_ERROR)
    error_code: str
    error_message: str
    conversation_id: Optional[UUID] = None
    message_id: Optional[UUID] = None


class PermissionErrorEvent(WebSocketEvent):
    """Event for permission errors."""

    type: Literal['permission_error'] = Field(default=ChatEventType.PERMISSION_ERROR)
    error_message: str
    required_permission: str
    resource_id: Optional[str] = None
