import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
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


class User(Base):
    __tablename__ = 'users'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    reputation_level = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    posts = relationship('Post', back_populates='user', foreign_keys='Post.user_id')

    communities = relationship('Community', secondary='community_members', viewonly=True)

    community_memberships = relationship(
        'CommunityMember', back_populates='user', cascade='all, delete-orphan'
    )

    ratings = relationship('Rating', back_populates='user', cascade='all, delete-orphan')

    comments = relationship(
        'Comment', back_populates='user', cascade='all, delete-orphan'
    )

    sent_connections = relationship(
        'UserConnection',
        foreign_keys='UserConnection.requester_id',
        back_populates='requester',
        cascade='all, delete-orphan',
    )

    received_connections = relationship(
        'UserConnection',
        foreign_keys='UserConnection.addressee_id',
        back_populates='addressee',
        cascade='all, delete-orphan',
    )


class UserConnection(Base):
    __tablename__ = 'user_connections'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    requester_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
    addressee_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    rejected_at = Column(DateTime, nullable=True)

    requester = relationship(
        'User', foreign_keys=[requester_id], back_populates='sent_connections'
    )

    addressee = relationship(
        'User', foreign_keys=[addressee_id], back_populates='received_connections'
    )

    __table_args__ = (
        CheckConstraint('requester_id != addressee_id', name='no_self_connection'),
        UniqueConstraint(
            'requester_id', 'addressee_id', name='unique_connection_request'
        ),
    )
