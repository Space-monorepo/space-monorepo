"""
Chat module for Space social network.

This module handles real-time messaging between connected users,
including text messages, file attachments, and conversation management.
"""

from .model import Conversation, Message, MessageAttachment
from .schema import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    MessageAttachmentResponse,
    MessageTypeEnum,
    ConversationParticipant,
    ConversationSearchParams,
    MessageSearchParams,
    WebSocketMessage,
    TypingEvent,
    MessageReadEvent,
    ChatErrorResponse,
)

__all__ = [
    # Models
    "Conversation",
    "Message",
    "MessageAttachment",
    # Schemas
    "ConversationCreate",
    "ConversationResponse",
    "ConversationListResponse",
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
    "MessageAttachmentResponse",
    "MessageTypeEnum",
    "ConversationParticipant",
    "ConversationSearchParams",
    "MessageSearchParams",
    "WebSocketMessage",
    "TypingEvent",
    "MessageReadEvent",
    "ChatErrorResponse",
]
