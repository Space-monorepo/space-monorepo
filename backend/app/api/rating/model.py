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

from app.core.database import Base


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    community_id = Column(
        UUID(as_uuid=True), ForeignKey('communities.id'), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True
    )
    rating = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    community = relationship('Community', back_populates='ratings')
    user = relationship('User', back_populates='ratings')

    __table_args__ = (
        UniqueConstraint('user_id', 'community_id', name='uq_user_community_rating'),
    )
