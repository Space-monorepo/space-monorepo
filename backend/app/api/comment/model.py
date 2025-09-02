import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
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


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    post_id = Column(UUIDColumn, ForeignKey('posts.id'), nullable=False)
    user_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='active')
    likes_count = Column(Integer, nullable=False, default=0)
    report_count = Column(Integer, nullable=False, default=0)
    parent_id = Column(UUIDColumn, ForeignKey('comments.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    post = relationship('Post', back_populates='comments')
    user = relationship('User', back_populates='comments')
    parent = relationship('Comment', remote_side=[id], back_populates='replies')
    replies = relationship(
        'Comment', back_populates='parent', cascade='all, delete-orphan'
    )
    liked_by = relationship(
        'CommunityMember',
        secondary='comment_likes',
        back_populates='liked_comments',
        viewonly=True,  # Torna este relacionamento somente leitura
    )
    likes = relationship(
        'CommentLikes', back_populates='comment', cascade='all, delete-orphan'
    )


class CommentLikes(Base):
    __tablename__ = 'comment_likes'

    comment_id = Column(
        UUIDColumn, ForeignKey('comments.id'), nullable=False, primary_key=True
    )
    member_id = Column(
        UUIDColumn, ForeignKey('community_members.id'), nullable=False, primary_key=True
    )
    created_at = Column(DateTime, nullable=False, default=func.now())

    comment = relationship('Comment', back_populates='likes')
    member = relationship('CommunityMember')
