import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
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


class Post(Base):
    __tablename__ = 'posts'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    community_id = Column(UUIDColumn, ForeignKey('communities.id'), nullable=False)
    user_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False)
    user_role_in_community = Column(String, nullable=False)
    type_post = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default='active')
    likes_count = Column(Integer, nullable=False, default=0)
    comments_count = Column(Integer, nullable=False, default=0)
    report_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    community = relationship('Community', back_populates='posts')
    user = relationship('User', back_populates='posts')
    likes = relationship(
        'CommunityMember',
        secondary='post_likes',
        back_populates='liked_posts',
    )
    comments = relationship('Comment', back_populates='post')


class CampaignPost(Base):
    __tablename__ = 'campaign_posts'

    post_id = Column(UUIDColumn, ForeignKey('posts.id'), primary_key=True)
    target_participants = Column(Integer, nullable=False, default=100)
    current_participants = Column(Integer, nullable=False, default=0)
    status_campaign = Column(String, nullable=False, default='pending')


class CampaignParticipants(Base):
    __tablename__ = 'campaign_participants'
    __table_args__ = (PrimaryKeyConstraint('campaign_id', 'user_id'),)

    campaign_id = Column(
        UUIDColumn, ForeignKey('campaign_posts.post_id'), nullable=False
    )
    user_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False)
    joined_at = Column(DateTime, nullable=False, default=func.now())


class ComplaintPost(Base):
    __tablename__ = 'complaint_posts'

    post_id = Column(UUIDColumn, ForeignKey('posts.id'), primary_key=True)
    confirmations_count = Column(Integer, nullable=False, default=0)
    status_complaint = Column(String, nullable=False, default='pending')
    level_complaint = Column(String, nullable=False, default='low')


class PollPosts(Base):
    __tablename__ = 'poll_posts'

    post_id = Column(UUIDColumn, ForeignKey('posts.id'), primary_key=True)
    question = Column(String, nullable=False)

    options = relationship(
        'PollOptions',
        back_populates='poll',
        foreign_keys='PollOptions.post_id',
        cascade='all, delete-orphan',
    )


class PollOptions(Base):
    __tablename__ = 'poll_options'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    post_id = Column(UUIDColumn, ForeignKey('poll_posts.post_id'), nullable=False)
    answer = Column(String, nullable=False)
    votes_count = Column(Integer, nullable=False, default=0)

    poll = relationship('PollPosts', back_populates='options')


class PostFeedback(Base):
    __tablename__ = 'post_feedbacks'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    post_id = Column(UUIDColumn, ForeignKey('posts.id'), nullable=False)
    member_id = Column(UUIDColumn, ForeignKey('community_members.id'), nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())


class PostLikes(Base):
    __tablename__ = 'post_likes'

    post_id = Column(
        UUIDColumn, ForeignKey('posts.id'), nullable=False, primary_key=True
    )
    member_id = Column(
        UUIDColumn,
        ForeignKey('community_members.id'),
        nullable=False,
        primary_key=True,
    )
    created_at = Column(DateTime, nullable=False, default=func.now())
