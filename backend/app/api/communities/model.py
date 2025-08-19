import uuid

from sqlalchemy import (
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


class Community(Base):
    __tablename__ = 'communities'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type_community = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    posts = relationship('Post', back_populates='community')

    members = relationship(
        'CommunityMember', back_populates='community', cascade='all, delete-orphan'
    )

    users = relationship('User', secondary='community_members', viewonly=True)

    badges = relationship(
        'Badge', back_populates='community', cascade='all, delete-orphan'
    )

    ratings = relationship(
        'Rating', back_populates='community', cascade='all, delete-orphan'
    )


class CommunityMember(Base):
    __tablename__ = 'community_members'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    user_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False)
    community_id = Column(
        UUIDColumn, ForeignKey('communities.id'), nullable=False, index=True
    )
    role = Column(String, nullable=False)
    reputation = Column(Integer, nullable=False, default=0)
    status_participation = Column(String, nullable=False, default='active')
    entered_in = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'community_id', name='uq_user_community'),
    )

    user = relationship('User', back_populates='community_memberships')

    community = relationship('Community', back_populates='members')

    liked_posts = relationship('Post', secondary='post_likes', back_populates='likes')

    badges = relationship('Badge', secondary='member_badges', back_populates='members')
