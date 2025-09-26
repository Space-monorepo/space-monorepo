"""
Chat-specific WebSocket events for real-time messaging.

This module defines all the WebSocket events that are specific to the chat domain,
extending the base event system with chat functionality like sending messages,
typing indicators, conversation management, and message status updates.

All events inherit from the base WebSocketEvent class to ensure consistency
and type safety across the application.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import Field, validator

from app.api.chat.schema import MessageTypeEnum
from app.core.websocket.events import WebSocketEvent

MAX_ATTACHMENT_FILE_SIZE_BYTES = 52_428_800
MAX_BULK_MARK_READ = 100


class ChatEventType(str, Enum):
    """Chat-specific event types."""

    # Message events
    SEND_MESSAGE = 'send_message'
    MESSAGE_SENT = 'message_sent'
    MESSAGE_RECEIVED = 'message_received'
    MESSAGE_WITH_ATTACHMENT = 'send_message_with_attachment'

    # Conversation events
    JOIN_CONVERSATION = 'join_conversation'
    LEAVE_CONVERSATION = 'leave_conversation'
    CONVERSATION_JOINED = 'conversation_joined'
    CONVERSATION_LEFT = 'conversation_left'

    # Typing events
    TYPING = 'typing'
    STOP_TYPING = 'stop_typing'
    USER_TYPING = 'user_typing'
    USER_STOPPED_TYPING = 'user_stopped_typing'

    # Message status events
    MARK_MESSAGE_READ = 'mark_message_read'
    MESSAGE_READ = 'message_read'
    BULK_MARK_READ = 'bulk_mark_read'

    # Presence events
    USER_JOINED_CONVERSATION = 'user_joined_conversation'
    USER_LEFT_CONVERSATION = 'user_left_conversation'
    USER_ONLINE = 'user_online'
    USER_OFFLINE = 'user_offline'

    # Error events
    CHAT_ERROR = 'chat_error'
    PERMISSION_ERROR = 'permission_error'


class ChatMessageEvent(WebSocketEvent):
    """Event for sending a text message in a conversation."""

    type: Literal['send_message'] = Field(default=ChatEventType.SEND_MESSAGE)
    conversation_id: UUID = Field(..., description='ID of the conversation')
    content: str = Field(
        ..., min_length=1, max_length=2000, description='Message content'
    )
    reply_to_message_id: Optional[UUID] = Field(
        None, description='ID of message being replied to'
    )

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty or whitespace only')
        return v.strip()

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'send_message',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'content': 'Hello, how are you?',
                'reply_to_message_id': None,
                'request_id': 'req_123',
            }
        }


class MessageWithAttachmentEvent(WebSocketEvent):
    """Event for sending a message with file attachment."""

    type: Literal['send_message_with_attachment'] = Field(
        default=ChatEventType.MESSAGE_WITH_ATTACHMENT
    )
    conversation_id: UUID = Field(..., description='ID of the conversation')
    content: Optional[str] = Field(
        None, max_length=2000, description='Optional message content'
    )
    message_type: MessageTypeEnum = Field(..., description='Type of message/attachment')
    file_name: str = Field(..., description='Name of the file')
    file_data: str = Field(..., description='Base64 encoded file data')
    file_size: int = Field(
        ...,
        gt=0,
        le=MAX_ATTACHMENT_FILE_SIZE_BYTES,
        description='File size in bytes (max 50MB)',
    )
    content_type: str = Field(..., description='MIME type of the file')
    reply_to_message_id: Optional[UUID] = Field(
        None, description='ID of message being replied to'
    )

    @validator('file_size')
    def validate_file_size(cls, v):
        if v > MAX_ATTACHMENT_FILE_SIZE_BYTES:  # 50MB
            raise ValueError('File size cannot exceed 50MB')
        return v

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'send_message_with_attachment',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'content': 'Check out this image!',
                'message_type': 'image',
                'file_name': 'photo.jpg',
                'file_data': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA...',
                'file_size': 1024000,
                'content_type': 'image/jpeg',
            }
        }


class JoinConversationEvent(WebSocketEvent):
    """Event for joining a conversation to receive real-time updates."""

    type: Literal['join_conversation'] = Field(default=ChatEventType.JOIN_CONVERSATION)
    conversation_id: UUID = Field(..., description='ID of the conversation to join')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'join_conversation',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'request_id': 'req_456',
            }
        }


class LeaveConversationEvent(WebSocketEvent):
    """Event for leaving a conversation to stop receiving updates."""

    type: Literal['leave_conversation'] = Field(default=ChatEventType.LEAVE_CONVERSATION)
    conversation_id: UUID = Field(..., description='ID of the conversation to leave')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'leave_conversation',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
            }
        }


class TypingEvent(WebSocketEvent):
    """Event indicating user started typing in a conversation."""

    type: Literal['typing'] = Field(default=ChatEventType.TYPING)
    conversation_id: UUID = Field(..., description='ID of the conversation')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'typing',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
            }
        }


class StopTypingEvent(WebSocketEvent):
    """Event indicating user stopped typing in a conversation."""

    type: Literal['stop_typing'] = Field(default=ChatEventType.STOP_TYPING)
    conversation_id: UUID = Field(..., description='ID of the conversation')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'stop_typing',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
            }
        }


class MarkMessageReadEvent(WebSocketEvent):
    """Event for marking a message as read."""

    type: Literal['mark_message_read'] = Field(default=ChatEventType.MARK_MESSAGE_READ)
    message_id: UUID = Field(..., description='ID of the message to mark as read')
    conversation_id: UUID = Field(..., description='ID of the conversation')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'mark_message_read',
                'message_id': '123e4567-e89b-12d3-a456-426614174001',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
            }
        }


class BulkMarkReadEvent(WebSocketEvent):
    """Event for marking multiple messages as read."""

    type: Literal['bulk_mark_read'] = Field(default=ChatEventType.BULK_MARK_READ)
    conversation_id: UUID = Field(..., description='ID of the conversation')
    message_ids: List[UUID] = Field(
        ..., description='List of message IDs to mark as read'
    )
    up_to_message_id: Optional[UUID] = Field(
        None, description='Mark all messages up to this one'
    )

    @validator('message_ids')
    def validate_message_ids(cls, v):
        if len(v) > MAX_BULK_MARK_READ:
            raise ValueError('Cannot mark more than 100 messages at once')
        return v

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'bulk_mark_read',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'message_ids': [
                    '123e4567-e89b-12d3-a456-426614174001',
                    '123e4567-e89b-12d3-a456-426614174002',
                ],
            }
        }


# Outgoing events (sent from server to client)


class MessageReceivedEvent(WebSocketEvent):
    """Event broadcast when a new message is received in a conversation."""

    type: Literal['message_received'] = Field(default=ChatEventType.MESSAGE_RECEIVED)
    conversation_id: UUID = Field(..., description='ID of the conversation')
    message: Dict[str, Any] = Field(..., description='Complete message object')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'message_received',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'message': {
                    'id': '123e4567-e89b-12d3-a456-426614174001',
                    'content': 'Hello!',
                    'sender': {'id': 'user123', 'name': 'John Doe'},
                    'created_at': '2024-01-01T12:00:00Z',
                },
            }
        }


class UserTypingEvent(WebSocketEvent):
    """Event broadcast when a user starts typing."""

    type: Literal['user_typing'] = Field(default=ChatEventType.USER_TYPING)
    conversation_id: UUID = Field(..., description='ID of the conversation')
    user_id: UUID = Field(..., description='ID of the typing user')
    user_name: str = Field(..., description='Name of the typing user')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'user_typing',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'user_id': '123e4567-e89b-12d3-a456-426614174002',
                'user_name': 'John Doe',
            }
        }


class UserStoppedTypingEvent(WebSocketEvent):
    """Event broadcast when a user stops typing."""

    type: Literal['user_stopped_typing'] = Field(
        default=ChatEventType.USER_STOPPED_TYPING
    )
    conversation_id: UUID = Field(..., description='ID of the conversation')
    user_id: UUID = Field(..., description='ID of the user')
    user_name: str = Field(..., description='Name of the user')


class MessageReadEvent(WebSocketEvent):
    """Event broadcast when a message is marked as read."""

    type: Literal['message_read'] = Field(default=ChatEventType.MESSAGE_READ)
    conversation_id: UUID = Field(..., description='ID of the conversation')
    message_id: UUID = Field(..., description='ID of the message that was read')
    read_by_user_id: UUID = Field(..., description='ID of the user who read the message')
    read_by_user_name: str = Field(
        ..., description='Name of the user who read the message'
    )
    read_at: str = Field(..., description='ISO timestamp when message was read')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'message_read',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'message_id': '123e4567-e89b-12d3-a456-426614174001',
                'read_by_user_id': '123e4567-e89b-12d3-a456-426614174002',
                'read_by_user_name': 'Jane Smith',
                'read_at': '2024-01-01T12:05:00Z',
            }
        }


class UserJoinedConversationEvent(WebSocketEvent):
    """Event broadcast when a user joins a conversation."""

    type: Literal['user_joined_conversation'] = Field(
        default=ChatEventType.USER_JOINED_CONVERSATION
    )
    conversation_id: UUID = Field(..., description='ID of the conversation')
    user_id: UUID = Field(..., description='ID of the user who joined')
    user_name: str = Field(..., description='Name of the user who joined')
    joined_at: str = Field(..., description='ISO timestamp when user joined')


class UserLeftConversationEvent(WebSocketEvent):
    """Event broadcast when a user leaves a conversation."""

    type: Literal['user_left_conversation'] = Field(
        default=ChatEventType.USER_LEFT_CONVERSATION
    )
    conversation_id: UUID = Field(..., description='ID of the conversation')
    user_id: UUID = Field(..., description='ID of the user who left')
    user_name: str = Field(..., description='Name of the user who left')
    left_at: str = Field(..., description='ISO timestamp when user left')


class ConversationJoinedEvent(WebSocketEvent):
    """Confirmation event sent when user successfully joins a conversation."""

    type: Literal['conversation_joined'] = Field(
        default=ChatEventType.CONVERSATION_JOINED
    )
    conversation_id: UUID = Field(..., description='ID of the conversation')
    participant_count: int = Field(..., description='Number of active participants')
    unread_count: int = Field(..., description='Number of unread messages')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'conversation_joined',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
                'participant_count': 2,
                'unread_count': 3,
            }
        }


class ConversationLeftEvent(WebSocketEvent):
    """Confirmation event sent when user successfully leaves a conversation."""

    type: Literal['conversation_left'] = Field(default=ChatEventType.CONVERSATION_LEFT)
    conversation_id: UUID = Field(..., description='ID of the conversation')


class ChatErrorEvent(WebSocketEvent):
    """Event for chat-specific errors."""

    type: Literal['chat_error'] = Field(default=ChatEventType.CHAT_ERROR)
    error_code: str = Field(..., description='Chat error code')
    error_message: str = Field(..., description='Human-readable error message')
    conversation_id: Optional[UUID] = Field(None, description='Related conversation ID')
    message_id: Optional[UUID] = Field(None, description='Related message ID')

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'chat_error',
                'error_code': 'MESSAGE_TOO_LONG',
                'error_message': 'Message exceeds maximum length of 2000 characters',
                'conversation_id': '123e4567-e89b-12d3-a456-426614174000',
            }
        }


class PermissionErrorEvent(WebSocketEvent):
    """Event for permission-related errors."""

    type: Literal['permission_error'] = Field(default=ChatEventType.PERMISSION_ERROR)
    error_message: str = Field(..., description='Permission error message')
    required_permission: str = Field(..., description='Required permission')
    resource_id: Optional[str] = Field(
        None, description='ID of the resource being accessed'
    )

    class Config:
        json_schema_extra = {
            'example': {
                'type': 'permission_error',
                'error_message': 'You do not have permission to access this conversation',
                'required_permission': 'conversation_access',
                'resource_id': '123e4567-e89b-12d3-a456-426614174000',
            }
        }
