import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.core.database import Base

if settings.ENVIRONMENT == 'test':
    UUIDColumn = String(36)

    def uuid_default():
        return str(uuid.uuid4())

else:
    UUIDColumn = UUID(as_uuid=True)

    def uuid_default():
        return uuid.uuid4()


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    user1_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
    user2_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    last_message_id = Column(UUIDColumn, nullable=True)

    # Relationships
    user1 = relationship('User', foreign_keys=[user1_id])
    user2 = relationship('User', foreign_keys=[user2_id])

    messages = relationship(
        'Message',
        back_populates='conversation',
        cascade='all, delete-orphan',
        order_by='Message.created_at.desc()'
    )

    last_message = relationship(
        'Message',
        foreign_keys=[last_message_id],
        post_update=True
    )

    __table_args__ = (
        CheckConstraint('user1_id != user2_id', name='no_self_conversation'),
        UniqueConstraint('user1_id', 'user2_id', name='unique_conversation'),
    )


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    conversation_id = Column(
        UUIDColumn, ForeignKey('conversations.id'), nullable=False, index=True
    )
    sender_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
    content = Column(Text, nullable=True)  # Opcional para anexos
    message_type = Column(
        String(20),
        nullable=False,
        default='text'
    )  # 'text', 'image', 'document', 'audio', 'video', 'system'
    created_at = Column(DateTime, nullable=False, default=func.now())
    is_read = Column(Boolean, nullable=False, default=False)
    reply_to_message_id = Column(UUIDColumn, ForeignKey('messages.id'), nullable=True)

    # Relationships
    conversation = relationship('Conversation', back_populates='messages')
    sender = relationship('User', foreign_keys=[sender_id])

    reply_to_message = relationship(
        'Message',
        remote_side=[id],
        foreign_keys=[reply_to_message_id]
    )

    replies = relationship(
        'Message',
        remote_side=[reply_to_message_id],
        foreign_keys=[reply_to_message_id]
    )

    attachments = relationship(
        'MessageAttachment',
        back_populates='message',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'image', 'document', 'audio', 'video', 'system')",
            name='valid_message_type'
        ),
        CheckConstraint(
            "(message_type = 'text' AND content IS NOT NULL) OR (message_type != 'text')",
            name='text_messages_require_content'
        ),
    )


class MessageAttachment(Base):
    __tablename__ = 'message_attachments'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    message_id = Column(
        UUIDColumn, ForeignKey('messages.id'), nullable=False, index=True
    )
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    file_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    message = relationship('Message', back_populates='attachments')

    __table_args__ = (
        CheckConstraint('file_size > 0', name='positive_file_size'),
    )
