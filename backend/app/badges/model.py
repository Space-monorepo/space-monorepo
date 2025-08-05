import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Badge(Base):
    __tablename__ = 'badges'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    community_id = Column(UUID(as_uuid=True), ForeignKey('communities.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    members = relationship(
        'CommunityMember', secondary='member_badges', back_populates='badges'
    )

    community = relationship('Community', back_populates='badges')

    __table_args__ = (
        UniqueConstraint('name', 'community_id', name='uq_badge_name_community'),
    )


class MemberBadge(Base):
    __tablename__ = 'member_badges'

    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey('community_members.id', ondelete='CASCADE'),
        primary_key=True,
    )
    badge_id = Column(
        UUID(as_uuid=True), ForeignKey('badges.id', ondelete='CASCADE'), primary_key=True
    )
    achieved_at = Column(DateTime(timezone=True), default=func.now())
