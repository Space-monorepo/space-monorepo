from datetime import datetime
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.api.chat.model import Conversation, Message, MessageAttachment
from app.api.chat.schema import ConversationSearchParams, MessageSearchParams
from app.api.users.model import User
from app.core.repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: Session):
        super().__init__(Conversation, session)  # type: ignore
        self.session = session

    def get_conversation_with_participants(
        self, conversation_id: UUID
    ) -> Conversation | None:
        """Get conversation with user details loaded - uses custom query for eager loading"""
        return (
            self.session.query(Conversation)
            .options(
                joinedload(Conversation.user1),
                joinedload(Conversation.user2),
                joinedload(Conversation.last_message).joinedload(Message.sender),
            )
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def find_conversation_between_users(
        self, user1_id: UUID, user2_id: UUID
    ) -> Conversation | None:
        """Find existing conversation between two users (bidirectional) - custom query for complex filter"""
        user1_str = str(user1_id)
        user2_str = str(user2_id)

        return (
            self.session.query(Conversation)
            .filter(
                or_(
                    and_(
                        Conversation.user1_id == user1_str,
                        Conversation.user2_id == user2_str,
                    ),
                    and_(
                        Conversation.user1_id == user2_str,
                        Conversation.user2_id == user1_str,
                    ),
                )
            )
            .first()
        )

    def create_conversation(self, user1_id: UUID, user2_id: UUID) -> Conversation:
        """Create a new conversation between two users - uses BaseRepository.save()"""
        # Ensure consistent ordering (smaller ID first)
        if str(user1_id) < str(user2_id):
            conversation = Conversation(user1_id=str(user1_id), user2_id=str(user2_id))
        else:
            conversation = Conversation(user1_id=str(user2_id), user2_id=str(user1_id))

        return self.save(conversation)

    def list_user_conversations(
        self, user_id: UUID, params: ConversationSearchParams
    ) -> Tuple[List[Conversation], int]:
        """List conversations for a user with search and pagination - custom query for complex joins"""
        user_id_str = str(user_id)

        # Base query for conversations where user participates
        query = (
            self.session.query(Conversation)
            .options(
                joinedload(Conversation.user1),
                joinedload(Conversation.user2),
                joinedload(Conversation.last_message).joinedload(Message.sender),
            )
            .filter(
                or_(
                    Conversation.user1_id == user_id_str,
                    Conversation.user2_id == user_id_str,
                )
            )
        )

        # Search by participant name
        if params.name:
            other_user_alias = self.session.query(User).subquery()
            query = query.join(
                other_user_alias,
                or_(
                    and_(
                        Conversation.user1_id != user_id_str,
                        Conversation.user1_id == other_user_alias.c.id,
                    ),
                    and_(
                        Conversation.user2_id != user_id_str,
                        Conversation.user2_id == other_user_alias.c.id,
                    ),
                ),
            ).filter(other_user_alias.c.name.ilike(f'%{params.name}%'))

        total = query.count()

        # Order by last activity (updated_at) descending
        conversations = (
            query.order_by(desc(Conversation.updated_at))
            .offset(params.offset or 0)
            .limit(params.limit or 20)
            .all()
        )

        return conversations, total

    def validate_user_participation(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Check if user participates in the conversation - uses BaseRepository.get_by_id()"""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return False

        user_id_str = str(user_id)
        return (
            str(conversation.user1_id) == user_id_str
            or str(conversation.user2_id) == user_id_str
        )

    def update_last_message(self, conversation_id: UUID, message_id: UUID) -> None:
        """Update the last message of a conversation"""
        conversation = self.get_by_id(conversation_id)
        if conversation:
            self.session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).update({
                'last_message_id': str(message_id),
                'updated_at': datetime.utcnow(),
            })
            self.session.flush()

    def get_other_participant_id(
        self, conversation_id: UUID, user_id: UUID
    ) -> UUID | None:
        """Get the other participant's ID in a conversation"""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return None

        user_id_str = str(user_id)
        if str(conversation.user1_id) == user_id_str:
            return UUID(str(conversation.user2_id))
        elif str(conversation.user2_id) == user_id_str:
            return UUID(str(conversation.user1_id))
        return None

    def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation - uses BaseRepository.get_by_id() and BaseRepository.delete()"""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            return False
        return self.delete(conversation)


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: Session):
        super().__init__(Message, session)  # type: ignore
        self.session = session

    def create_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str | None = None,
        message_type: str = 'text',
        reply_to_message_id: UUID | None = None,
    ) -> Message:
        """Create a new message - uses BaseRepository.save()"""
        message = Message(
            conversation_id=str(conversation_id),
            sender_id=str(sender_id),
            content=content,
            message_type=message_type,
            reply_to_message_id=str(reply_to_message_id)
            if reply_to_message_id
            else None,
        )

        return self.save(message)

    def list_conversation_messages(
        self, conversation_id: UUID, params: MessageSearchParams
    ) -> Tuple[List[Message], int]:
        """List messages in a conversation with pagination - custom query for eager loading and reverse pagination"""
        query = (
            self.session.query(Message)
            .options(
                joinedload(Message.sender),
                joinedload(Message.reply_to_message).joinedload(Message.sender),
                joinedload(Message.attachments),
            )
            .filter(Message.conversation_id == conversation_id)
        )

        # Support for reverse pagination (before_message_id)
        if params.before_message_id:
            before_message = self.get_by_id(params.before_message_id)
            if before_message:
                query = query.filter(Message.created_at < before_message.created_at)

        total = query.count()

        # Order by created_at descending (newest first)
        messages = (
            query.order_by(desc(Message.created_at))
            .offset(params.offset or 0)
            .limit(params.limit or 50)
            .all()
        )

        return messages, total

    def get_message_with_details(self, message_id: UUID) -> Message | None:
        """Get message with all related data loaded - custom query for eager loading (can't use base get_by_id)"""
        return (
            self.session.query(Message)
            .options(
                joinedload(Message.sender),
                joinedload(Message.conversation),
                joinedload(Message.reply_to_message).joinedload(Message.sender),
                joinedload(Message.attachments),
            )
            .filter(Message.id == message_id)
            .first()
        )

    def mark_message_as_read(self, message_id: UUID, user_id: UUID) -> bool:
        """Mark a message as read by a specific user - uses BaseRepository.get_by_id() for validation"""
        message = self.get_by_id(message_id)
        if not message:
            return False

        # Only allow marking as read if user is not the sender
        if str(message.sender_id) == str(user_id):
            return False

        self.session.query(Message).filter(Message.id == message_id).update({
            'is_read': True
        })
        self.session.flush()
        return True

    def bulk_mark_as_read(self, message_ids: List[UUID], user_id: UUID) -> int:
        """Mark multiple messages as read, returns count of successfully marked messages"""
        user_id_str = str(user_id)

        # Update messages where user is not the sender
        updated_count = (
            self.session.query(Message)
            .filter(
                and_(
                    Message.id.in_([str(mid) for mid in message_ids]),
                    Message.sender_id != user_id_str,
                    Message.is_read.is_(False),
                )
            )
            .update({Message.is_read: True}, synchronize_session=False)
        )

        self.session.flush()
        return updated_count

    def count_unread_messages(self, conversation_id: UUID, user_id: UUID) -> int:
        """Count unread messages in a conversation for a specific user"""
        user_id_str = str(user_id)

        return (
            self.session.query(Message)
            .filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user_id_str,
                    Message.is_read.is_(False),
                )
            )
            .count()
        )

    def get_latest_messages_in_conversations(
        self, conversation_ids: List[UUID]
    ) -> List[Message]:
        """Get the latest message for each conversation"""
        if not conversation_ids:
            return []

        # Subquery to get the latest message ID for each conversation
        latest_message_subquery = (
            self.session.query(
                Message.conversation_id,
                func.max(Message.created_at).label('latest_created_at'),
            )
            .filter(Message.conversation_id.in_([str(cid) for cid in conversation_ids]))
            .group_by(Message.conversation_id)
            .subquery()
        )

        # Get the actual messages
        return (
            self.session.query(Message)
            .options(joinedload(Message.sender))
            .join(
                latest_message_subquery,
                and_(
                    Message.conversation_id == latest_message_subquery.c.conversation_id,
                    Message.created_at == latest_message_subquery.c.latest_created_at,
                ),
            )
            .all()
        )

    def validate_message_ownership(self, message_id: UUID, user_id: UUID) -> bool:
        """Check if user owns the message - uses BaseRepository.get_by_id()"""
        message = self.get_by_id(message_id)
        if not message:
            return False
        return str(message.sender_id) == str(user_id)

    def delete_message(self, message_id: UUID) -> bool:
        """Delete a message - uses BaseRepository.get_by_id() and BaseRepository.delete()"""
        message = self.get_by_id(message_id)
        if not message:
            return False
        return self.delete(message)


class MessageAttachmentRepository(BaseRepository[MessageAttachment]):
    def __init__(self, session: Session):
        super().__init__(MessageAttachment, session)  # type: ignore
        self.session = session

    def create_attachment(  # noqa: PLR0913, PLR0917
        self,
        message_id: UUID,
        file_name: str,
        file_size: int,
        file_type: str,
        file_url: str,
        thumbnail_url: str | None = None,
    ) -> MessageAttachment:
        """Create a new message attachment - uses BaseRepository.save()"""
        attachment = MessageAttachment(
            message_id=str(message_id),
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            file_url=file_url,
            thumbnail_url=thumbnail_url,
        )

        return self.save(attachment)

    def list_message_attachments(self, message_id: UUID) -> List[MessageAttachment]:
        """Get all attachments for a message"""
        return (
            self.session.query(MessageAttachment)
            .filter(MessageAttachment.message_id == message_id)
            .order_by(MessageAttachment.created_at)
            .all()
        )

    def get_attachment_with_message(
        self, attachment_id: UUID
    ) -> MessageAttachment | None:
        """Get attachment with message details loaded - custom query for eager loading (can't use base get_by_id)"""
        return (
            self.session.query(MessageAttachment)
            .options(joinedload(MessageAttachment.message))
            .filter(MessageAttachment.id == attachment_id)
            .first()
        )

    def delete_message_attachments(self, message_id: UUID) -> int:
        """Delete all attachments for a message, returns count of deleted attachments"""
        deleted_count = (
            self.session.query(MessageAttachment)
            .filter(MessageAttachment.message_id == message_id)
            .delete(synchronize_session=False)
        )

        self.session.flush()
        return deleted_count

    def delete_attachment(self, attachment_id: UUID) -> bool:
        """Delete a single attachment - uses BaseRepository.get_by_id() and BaseRepository.delete()"""
        attachment = self.get_by_id(attachment_id)
        if not attachment:
            return False
        return self.delete(attachment)

    def get_attachments_by_type(
        self, conversation_id: UUID, file_type: str
    ) -> List[MessageAttachment]:
        """Get all attachments of a specific type in a conversation"""
        return (
            self.session.query(MessageAttachment)
            .join(Message, MessageAttachment.message_id == Message.id)
            .filter(
                and_(
                    Message.conversation_id == conversation_id,
                    MessageAttachment.file_type.startswith(file_type),
                )
            )
            .order_by(desc(MessageAttachment.created_at))
            .all()
        )
