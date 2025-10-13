import asyncio
import base64
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import WebSocket

from app.api.chat.service import ChatService
from app.api.users.model import User
from app.core.database import SessionLocal
from app.core.transaction import TransactionManager
from app.core.websocket.events import EventHandler, EventResponse
from app.core.websocket.manager import websocket_manager
from app.core.websocket.rooms import RoomManager

from .events import (
    BulkMarkReadEvent,
    ChatMessageEvent,
    ConversationJoinedEvent,
    ConversationLeftEvent,
    JoinConversationEvent,
    LeaveConversationEvent,
    MarkMessageReadEvent,
    MessageReadEvent,
    MessageReceivedEvent,
    MessageWithAttachmentEvent,
    StopTypingEvent,
    TypingEvent,
    UserJoinedConversationEvent,
    UserLeftConversationEvent,
    UserStoppedTypingEvent,
    UserTypingEvent,
)

logger = logging.getLogger(__name__)


class ChatEventHandler(EventHandler):
    """Handler for chat WebSocket events."""

    session_factory = SessionLocal

    def __init__(self, namespace: str = 'chat'):
        super().__init__(namespace)
        self._typing_users: Dict[str, Dict[str, datetime]] = {}
        self._typing_cleanup_task = None
        self._started = False
        self.typing_timeout = 10
        self.max_file_size = 52428800
        self.cleanup_interval = 5

    def _ensure_started(self):
        if not self._started:
            self._started = True
            try:
                loop = asyncio.get_running_loop()
                if self._typing_cleanup_task is None:
                    self._typing_cleanup_task = loop.create_task(
                        self._cleanup_typing_indicators()
                    )
            except RuntimeError:
                pass

    def register_events(self) -> None:
        self.register_event_type(
            'send_message', ChatMessageEvent, self._handle_send_message
        )
        self.register_event_type(
            'send_message_with_attachment',
            MessageWithAttachmentEvent,
            self._handle_send_message_with_attachment,
        )
        self.register_event_type(
            'join_conversation', JoinConversationEvent, self._handle_join_conversation
        )
        self.register_event_type(
            'leave_conversation', LeaveConversationEvent, self._handle_leave_conversation
        )
        self.register_event_type('typing', TypingEvent, self._handle_typing)
        self.register_event_type(
            'stop_typing', StopTypingEvent, self._handle_stop_typing
        )
        self.register_event_type(
            'mark_message_read', MarkMessageReadEvent, self._handle_mark_message_read
        )
        self.register_event_type(
            'bulk_mark_read', BulkMarkReadEvent, self._handle_bulk_mark_read
        )

    @classmethod
    async def _get_chat_service(cls) -> ChatService:
        session = cls.session_factory()
        try:
            return ChatService(TransactionManager(session))
        finally:
            pass

    @staticmethod
    async def _get_room_manager() -> RoomManager:
        return websocket_manager.room_manager

    async def _handle_send_message(
        self, websocket: WebSocket, user: User, event: ChatMessageEvent
    ) -> EventResponse:
        self._ensure_started()

        try:
            session = self.session_factory()
            with TransactionManager(session) as tm:
                chat_service = ChatService(tm)
                message_response = chat_service.send_message(
                    conversation_id=event.conversation_id,
                    sender_id=UUID(str(user.id)),
                    content=event.content,
                    reply_to_message_id=event.reply_to_message_id,
                )

            await self._broadcast_message_to_conversation(
                str(event.conversation_id),
                MessageReceivedEvent(
                    type='message_received',
                    conversation_id=event.conversation_id,
                    message=message_response.model_dump(mode='json'),
                    timestamp=datetime.now(timezone.utc).timestamp(),
                    request_id=event.request_id,
                ).to_dict(),
                exclude_user=str(user.id),
            )

            await self._clear_typing_indicator(str(event.conversation_id), str(user.id))

            return EventResponse(
                success=True,
                message='Message sent successfully',
                data=message_response.model_dump(mode='json'),
                request_id=event.request_id,
                error_code=None,
            )

        except Exception as e:
            logger.error(f'Error sending message: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=str(e),
                request_id=event.request_id,
                error_code='MESSAGE_SEND_ERROR',
                data={},
            )

    async def _handle_send_message_with_attachment(
        self, websocket: WebSocket, user: User, event: MessageWithAttachmentEvent
    ) -> EventResponse:
        try:
            if event.file_size > self.max_file_size:
                return EventResponse(
                    success=False,
                    message='File size exceeds maximum allowed size',
                    error_code='FILE_TOO_LARGE',
                    request_id=event.request_id,
                    data={},
                )

            try:
                file_data = base64.b64decode(event.file_data)
                if len(file_data) != event.file_size:
                    raise ValueError('File size mismatch')
            except Exception:
                return EventResponse(
                    success=False,
                    message='Invalid file data format',
                    error_code='INVALID_FILE_DATA',
                    request_id=event.request_id,
                    data={},
                )

            chat_service = await self._get_chat_service()
            file_url = f'/chat/files/{event.conversation_id}/{event.file_name}'

            message_response = chat_service.send_message_with_attachment(
                conversation_id=event.conversation_id,
                sender_id=UUID(str(user.id)),
                message_type=event.message_type,
                file_name=event.file_name,
                file_size=event.file_size,
                file_type=event.content_type,
                file_url=file_url,
                content=event.content,
                reply_to_message_id=event.reply_to_message_id,
            )

            await self._broadcast_message_to_conversation(
                str(event.conversation_id),
                MessageReceivedEvent(
                    type='message_received',
                    conversation_id=event.conversation_id,
                    message=message_response.model_dump(mode='json'),
                    timestamp=datetime.now(timezone.utc).timestamp(),
                    request_id=event.request_id,
                ).to_dict(),
                exclude_user=str(user.id),
            )

            return EventResponse(
                success=True,
                message='Message with attachment sent successfully',
                request_id=event.request_id,
                data={},
                error_code=None,
            )

        except Exception as e:
            logger.error(f'Error sending message with attachment: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=str(e),
                request_id=event.request_id,
                error_code='ATTACHMENT_ERROR',
                data={},
            )

    async def _handle_join_conversation(
        self, websocket: WebSocket, user: User, event: JoinConversationEvent
    ) -> EventResponse:
        try:
            chat_service = await self._get_chat_service()
            room_manager = await self._get_room_manager()

            chat_service.get_conversation(event.conversation_id, UUID(str(user.id)))

            room_id = str(event.conversation_id)
            success = await room_manager.join_room(
                user_id=str(user.id),
                websocket=websocket,
                user=user,
                namespace=self.namespace,
                room_type='conversation',
                room_id=room_id,
            )

            if not success:
                return EventResponse(
                    success=False,
                    message='Failed to join conversation room',
                    error_code='ROOM_JOIN_ERROR',
                    request_id=event.request_id,
                    data={},
                )

            await self._broadcast_message_to_conversation(
                room_id,
                UserJoinedConversationEvent(
                    type='user_joined_conversation',
                    conversation_id=event.conversation_id,
                    user_id=UUID(str(user.id)),
                    user_name=str(user.name),
                    joined_at=datetime.now(timezone.utc).isoformat(),
                    timestamp=datetime.now(timezone.utc).timestamp(),
                    request_id=event.request_id,
                ).to_dict(),
                exclude_user=str(user.id),
            )

            confirmation = ConversationJoinedEvent(
                type='conversation_joined',
                conversation_id=event.conversation_id,
                participant_count=2,
                unread_count=0,
                timestamp=datetime.now(timezone.utc).timestamp(),
                request_id=event.request_id,
            )

            return EventResponse(
                success=True,
                message='Successfully joined conversation',
                request_id=event.request_id,
                data=confirmation.model_dump(mode='json'),
                error_code=None,
            )

        except Exception as e:
            logger.error(f'Error joining conversation: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=str(e),
                request_id=event.request_id,
                error_code='CONVERSATION_JOIN_ERROR',
                data={},
            )

    async def _handle_leave_conversation(
        self, websocket: WebSocket, user: User, event: LeaveConversationEvent
    ) -> EventResponse:
        try:
            room_manager = await self._get_room_manager()
            room_id = str(event.conversation_id)

            success = await room_manager.leave_room(
                str(user.id), self.namespace, 'conversation', room_id
            )

            if success:
                await self._clear_typing_indicator(room_id, str(user.id))

                await self._broadcast_message_to_conversation(
                    room_id,
                    UserLeftConversationEvent(
                        type='user_left_conversation',
                        conversation_id=event.conversation_id,
                        user_id=UUID(str(user.id)),
                        user_name=str(user.name),
                        left_at=datetime.now(timezone.utc).isoformat(),
                        timestamp=datetime.now(timezone.utc).timestamp(),
                        request_id=event.request_id,
                    ).to_dict(),
                    exclude_user=str(user.id),
                )

                confirmation = ConversationLeftEvent(
                    type='conversation_left',
                    conversation_id=event.conversation_id,
                    timestamp=datetime.now(timezone.utc).timestamp(),
                    request_id=event.request_id,
                )

                return EventResponse(
                    success=True,
                    message='Successfully left conversation',
                    data=confirmation.model_dump(mode='json'),
                    request_id=event.request_id,
                    error_code=None,
                )
            else:
                return EventResponse(
                    success=False,
                    message='Failed to leave conversation room',
                    error_code='ROOM_LEAVE_ERROR',
                    request_id=event.request_id,
                    data={},
                )

        except Exception as e:
            logger.error(f'Error leaving conversation: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=str(e),
                request_id=event.request_id,
                error_code='CONVERSATION_LEAVE_ERROR',
                data=None,
            )

    async def _handle_typing(
        self, websocket: WebSocket, user: User, event: TypingEvent
    ) -> EventResponse:
        try:
            conversation_id = str(event.conversation_id)
            user_id = str(user.id)

            if conversation_id not in self._typing_users:
                self._typing_users[conversation_id] = {}

            self._typing_users[conversation_id][user_id] = datetime.now(timezone.utc)

            await self._broadcast_message_to_conversation(
                conversation_id,
                UserTypingEvent(
                    type='user_typing',
                    conversation_id=event.conversation_id,
                    user_id=UUID(str(user.id)),
                    user_name=str(user.name),
                    timestamp=datetime.now(timezone.utc).timestamp(),
                    request_id=None,
                ).to_dict(),
                exclude_user=user_id,
            )

            return EventResponse(
                success=True,
                message='Typing indicator sent',
                data=None,
                error_code=None,
                request_id=event.request_id,
            )

        except Exception as e:
            logger.error(f'Error handling typing: {e}', exc_info=True)
            return EventResponse(
                success=True,
                message='Typing indicator processed',
                data=None,
                error_code=None,
                request_id=event.request_id,
            )

    async def _handle_stop_typing(
        self, websocket: WebSocket, user: User, event: StopTypingEvent
    ) -> EventResponse:
        try:
            conversation_id = str(event.conversation_id)
            user_id = str(user.id)

            await self._clear_typing_indicator(conversation_id, user_id, str(user.name))

            return EventResponse(
                success=True,
                message='Stopped typing indicator',
                data=None,
                error_code=None,
                request_id=event.request_id,
            )

        except Exception as e:
            logger.error(f'Error handling stop typing: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message='Failed to stop typing indicator',
                error_code='HANDLER_ERROR',
                data=None,
                request_id=event.request_id,
            )

    async def _handle_mark_message_read(
        self, websocket: WebSocket, user: User, event: MarkMessageReadEvent
    ) -> EventResponse:
        try:
            chat_service = await self._get_chat_service()

            chat_service.mark_message_as_read(event.message_id, UUID(str(user.id)))

            await self._broadcast_message_to_conversation(
                str(event.conversation_id),
                MessageReadEvent(
                    type='message_read',
                    conversation_id=event.conversation_id,
                    message_id=event.message_id,
                    read_by_user_id=UUID(str(user.id)),
                    read_by_user_name=str(user.name),
                    read_at=datetime.now(timezone.utc).isoformat(),
                    timestamp=datetime.now(timezone.utc).timestamp(),
                    request_id=event.request_id,
                ).to_dict(),
                exclude_user=str(user.id),
            )

            return EventResponse(
                success=True,
                message='Message marked as read',
                data={'message_id': str(event.message_id)},
                request_id=event.request_id,
                error_code=None,
            )

        except Exception as e:
            logger.error(f'Error marking message as read: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=str(e),
                request_id=event.request_id,
                error_code='MARK_READ_ERROR',
                data=None,
            )

    async def _handle_bulk_mark_read(
        self, websocket: WebSocket, user: User, event: BulkMarkReadEvent
    ) -> EventResponse:
        try:
            chat_service = await self._get_chat_service()

            chat_service.bulk_mark_messages_as_read(
                event.message_ids, UUID(str(user.id))
            )

            return EventResponse(
                success=True,
                message='Messages marked as read',
                data={
                    'marked_count': len(event.message_ids)
                    if hasattr(event, 'message_ids')
                    else 1
                },
                request_id=event.request_id,
                error_code=None,
            )

        except Exception as e:
            logger.error(f'Error bulk marking messages as read: {e}', exc_info=True)
            return EventResponse(
                success=False,
                message=str(e),
                request_id=event.request_id,
                error_code='BULK_MARK_READ_ERROR',
                data={},
            )

    async def _broadcast_message_to_conversation(
        self,
        conversation_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None,
    ):
        try:
            room_manager = await self._get_room_manager()
            exclude_users = {exclude_user} if exclude_user else None

            await room_manager.broadcast_to_room(
                namespace=self.namespace,
                room_type='conversation',
                room_id=conversation_id,
                message=message,
                exclude_users=exclude_users,
            )

        except Exception as e:
            logger.error(f'Error broadcasting to conversation {conversation_id}: {e}')

    async def _clear_typing_indicator(
        self, conversation_id: str, user_id: str, user_name: str = 'Unknown'
    ):
        try:
            if (
                conversation_id in self._typing_users
                and user_id in self._typing_users[conversation_id]
            ):
                del self._typing_users[conversation_id][user_id]

                if not self._typing_users[conversation_id]:
                    del self._typing_users[conversation_id]

                await self._broadcast_message_to_conversation(
                    conversation_id,
                    UserStoppedTypingEvent(
                        type='user_stopped_typing',
                        conversation_id=UUID(conversation_id),
                        user_id=UUID(user_id),
                        user_name=user_name,
                        timestamp=datetime.now(timezone.utc).timestamp(),
                        request_id=None,
                    ).to_dict(),
                    exclude_user=user_id,
                )

        except Exception as e:
            logger.error(f'Error clearing typing indicator: {e}')

    async def _cleanup_typing_indicators(self):
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)

                now = datetime.now(timezone.utc)
                expired_indicators = []

                for conversation_id, users in self._typing_users.items():
                    for user_id, last_typing in users.items():
                        if (now - last_typing).total_seconds() > self.typing_timeout:
                            expired_indicators.append((conversation_id, user_id))

                for conversation_id, user_id in expired_indicators:
                    await self._clear_typing_indicator(conversation_id, user_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error in typing cleanup: {e}')

    def __del__(self):
        if (
            hasattr(self, '_typing_cleanup_task')
            and self._typing_cleanup_task
            and not self._typing_cleanup_task.done()
        ):
            self._typing_cleanup_task.cancel()
