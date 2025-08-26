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


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default, index=True)
    community_id = Column(
        UUIDColumn, ForeignKey('communities.id'), nullable=False, index=True
    )
    user_id = Column(UUIDColumn, ForeignKey('users.id'), nullable=False, index=True)
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
