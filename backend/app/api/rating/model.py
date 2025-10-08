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
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.types import GUID


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    community_id = Column(GUID, ForeignKey('communities.id'), nullable=False, index=True)
    user_id = Column(GUID, ForeignKey('users.id'), nullable=False, index=True)
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
