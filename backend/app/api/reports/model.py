import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
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


class Report(Base):
    __tablename__ = 'reports'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    reporter_id = Column(UUIDColumn, ForeignKey('community_members.id'), nullable=False)
    type = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # reporter = relationship('CommunityMember', back_populates='reports')
    moderation_votes = relationship('ModerationVotes', back_populates='report')


class ReportMember(Base):
    __tablename__ = 'report_members'

    report_id = Column(UUIDColumn, ForeignKey('reports.id'), primary_key=True)
    member_id = Column(UUIDColumn, ForeignKey('community_members.id'), nullable=False)
    community_id = Column(UUIDColumn, ForeignKey('communities.id'), nullable=False)

    # member = relationship('CommunityMember', back_populates='reports')
    # community = relationship('Community', back_populates='report_members')


class ReportPost(Base):
    __tablename__ = 'report_posts'

    report_id = Column(UUIDColumn, ForeignKey('reports.id'), primary_key=True)
    post_id = Column(UUIDColumn, ForeignKey('posts.id'), nullable=False)
    community_id = Column(UUIDColumn, ForeignKey('communities.id'), nullable=False)

    post = relationship('Post', back_populates='reports')
    # community = relationship('Community', back_populates='report_posts')


class ReportComment(Base):
    __tablename__ = 'report_comments'

    report_id = Column(UUIDColumn, ForeignKey('reports.id'), primary_key=True)
    comment_id = Column(UUIDColumn, ForeignKey('comments.id'), nullable=False)
    community_id = Column(UUIDColumn, ForeignKey('communities.id'), nullable=False)

    # comment = relationship('Comment', back_populates='reports')
    # community = relationship('Community', back_populates='report_comments')


class ModerationVotes(Base):
    __tablename__ = 'moderation_votes'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    report_id = Column(UUIDColumn, ForeignKey('reports.id'), nullable=False)
    moderator_id = Column(UUIDColumn, ForeignKey('community_members.id'), nullable=False)
    vote = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    report = relationship('Report', back_populates='moderation_votes')
