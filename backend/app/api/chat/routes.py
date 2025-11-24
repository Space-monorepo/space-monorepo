from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.chat.schema import (
    ConversationCreate,
    ConversationResponse,
    ConversationSearchParams,
    MessageAttachmentResponse,
    MessageCreate,
    MessageResponse,
    MessageSearchParams,
    MessageTypeEnum,
    UnreadCountResponse,
)
from app.api.chat.service import ChatService
from app.api.users.model import User
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse

router = APIRouter(prefix='/chat', tags=['chat'])


# Conversation endpoints
@router.post(
    '/conversations',
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ConversationResponse:
    """Create a new conversation between users"""
    with TransactionManager(session) as tm:
        return ChatService(tm).create_conversation(
            user_id=UUID(str(current_user.id)),
            participant_user_id=conversation_data.participant_user_id,
        )


@router.get('/conversations/{conversation_id}', response_model=ConversationResponse)
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ConversationResponse:
    """Get conversation details"""
    with TransactionManager(session) as tm:
        return ChatService(tm).get_conversation(
            conversation_id=conversation_id, user_id=UUID(str(current_user.id))
        )


@router.get('/conversations', response_model=PaginationResponse[ConversationResponse])
def list_user_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
) -> PaginationResponse[ConversationResponse]:
    """List user conversations with pagination and filters"""
    params = ConversationSearchParams(name=name, offset=offset, limit=limit)

    with TransactionManager(session) as tm:
        return ChatService(tm).list_user_conversations(
            user_id=UUID(str(current_user.id)), params=params
        )


# Message endpoints
@router.post(
    '/conversations/{conversation_id}/messages',
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> MessageResponse:
    """Send a text message in a conversation"""
    with TransactionManager(session) as tm:
        return ChatService(tm).send_message(
            conversation_id=conversation_id,
            sender_id=UUID(str(current_user.id)),
            content=message_data.content or '',
            reply_to_message_id=message_data.reply_to_message_id,
        )


@router.post(
    '/conversations/{conversation_id}/messages/attachment',
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message_with_attachment(  # noqa: PLR0913, PLR0917
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    file: UploadFile = File(...),
    message_type: MessageTypeEnum = Form(...),
    content: Optional[str] = Form(None),
    reply_to_message_id: Optional[UUID] = Form(None),
) -> MessageResponse:
    """Send a message with file attachment"""
    with TransactionManager(session) as tm:
        return ChatService(tm).send_message_with_attachment(
            conversation_id=conversation_id,
            sender_id=UUID(str(current_user.id)),
            file=file,
            message_type=message_type,
            content=content,
            reply_to_message_id=reply_to_message_id,
        )


@router.get(
    '/conversations/{conversation_id}/messages',
    response_model=PaginationResponse[MessageResponse],
)
def get_conversation_messages(  # noqa: PLR0913, PLR0917
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    before_message_id: Optional[UUID] = Query(None),
) -> PaginationResponse[MessageResponse]:
    """Get messages from a conversation with pagination"""
    params = MessageSearchParams(
        offset=offset, limit=limit, before_message_id=before_message_id
    )

    with TransactionManager(session) as tm:
        return ChatService(tm).get_conversation_messages(
            conversation_id=conversation_id,
            user_id=UUID(str(current_user.id)),
            params=params,
        )


@router.patch('/messages/{message_id}/read', status_code=status.HTTP_204_NO_CONTENT)
def mark_message_as_read(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """Mark a specific message as read"""
    with TransactionManager(session) as tm:
        ChatService(tm).mark_message_as_read(
            message_id=message_id, user_id=UUID(str(current_user.id))
        )


@router.patch(
    '/conversations/{conversation_id}/messages/read',
    status_code=status.HTTP_204_NO_CONTENT,
)
def mark_conversation_messages_as_read(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
    up_to_message_id: Optional[UUID] = Query(None),
) -> None:
    """Mark all messages in a conversation as read (up to a specific message if provided)"""
    with TransactionManager(session) as tm:
        ChatService(tm).mark_conversation_messages_as_read(
            conversation_id=conversation_id,
            user_id=UUID(str(current_user.id)),
            up_to_message_id=up_to_message_id,
        )


@router.get(
    '/conversations/{conversation_id}/unread-count', response_model=UnreadCountResponse
)
def get_conversation_unread_count(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> UnreadCountResponse:
    """Get unread message count for a specific conversation"""
    with TransactionManager(session) as tm:
        count = ChatService(tm).get_unread_count(
            conversation_id=conversation_id, user_id=UUID(str(current_user.id))
        )
        return UnreadCountResponse(unread_count=count)


@router.delete('/messages/{message_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """Delete a message (only by sender)"""
    with TransactionManager(session) as tm:
        ChatService(tm).delete_message(
            message_id=message_id, user_id=UUID(str(current_user.id))
        )


# Attachment endpoints
@router.get('/attachments/{attachment_id}', response_model=MessageAttachmentResponse)
def get_attachment(
    attachment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> MessageAttachmentResponse:
    """Get attachment details"""
    with TransactionManager(session) as tm:
        return ChatService(tm).get_attachment(
            attachment_id=attachment_id, user_id=UUID(str(current_user.id))
        )


@router.delete('/attachments/{attachment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """Delete an attachment (only by message sender)"""
    with TransactionManager(session) as tm:
        ChatService(tm).delete_attachment(
            attachment_id=attachment_id, user_id=UUID(str(current_user.id))
        )


# Health check endpoint
@router.get('/health', status_code=status.HTTP_200_OK)
def chat_health_check() -> dict:
    """Chat service health check"""
    return {'status': 'healthy', 'service': 'chat'}
