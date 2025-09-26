import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
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
        order_by='Message.created_at',
    )

    # Relationship to the last message
    last_message = relationship(
        'Message', foreign_keys=[last_message_id], post_update=True, uselist=False
    )

    # Constraints
    __table_args__ = (
        # Prevent self-conversations
        CheckConstraint('user1_id != user2_id', name='no_self_conversation'),
        # Ensure user1_id < user2_id for consistent ordering
        CheckConstraint('user1_id < user2_id', name='ordered_participants'),
        # Unique conversation per pair
        UniqueConstraint('user1_id', 'user2_id', name='unique_conversation_pair'),
    )


class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    conversation_id = Column(
        UUIDColumn, ForeignKey('conversations.id'), nullable=False, index=True
    )
    sender_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, nullable=False, default='text')
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    is_read = Column(Boolean, nullable=False, default=False)
    reply_to_message_id = Column(UUIDColumn, ForeignKey('messages.id'), nullable=True)

    # Relationships
    conversation = relationship('Conversation', back_populates='messages')
    sender = relationship('User', foreign_keys=[sender_id])

    # Self-referential relationship for replies
    reply_to_message = relationship(
        'Message', remote_side=[id], foreign_keys=[reply_to_message_id], uselist=False
    )

    # Attachments
    attachments = relationship(
        'MessageAttachment', back_populates='message', cascade='all, delete-orphan'
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'image', 'file', 'voice')",
            name='valid_message_type',
        ),
        # Index for efficient message retrieval
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
        # Index for unread messages
        Index(
            'idx_message_conversation_unread', 'conversation_id', 'is_read', 'created_at'
        ),
    )


class MessageAttachment(Base):
    __tablename__ = 'message_attachments'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    message_id = Column(
        UUIDColumn, ForeignKey('messages.id'), nullable=False, index=True
    )
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    message = relationship('Message', back_populates='attachments')

    # Constraints
    __table_args__ = (
        CheckConstraint('file_size > 0', name='positive_file_size'),
        CheckConstraint('file_size <= 52428800', name='max_file_size_50mb'),  # 50MB
    )
