import enum
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.config import settings
from app.core.database import Base

# Configuração adaptativa idêntica ao modelo User para corrigir erro em testes
if settings.ENVIRONMENT == 'test':
    # No ambiente de teste (SQLite), usamos String para evitar problemas de tipo
    UUIDColumn = String(36)
    UserFKType = String(36)

    def uuid_default():
        return str(uuid.uuid4())

else:
    # Em produção (Postgres), usamos UUID nativo
    UUIDColumn = UUID(as_uuid=True)
    UserFKType = UUID(as_uuid=True)

    def uuid_default():
        return uuid.uuid4()


class NotificationTypeEnum(str, enum.Enum):
    CAMPAIGN = 'CAMPAIGN'
    OFFICIAL_NOTICE = 'OFFICIAL_NOTICE'
    CONNECTION = 'CONNECTION'
    INTERACTION = 'INTERACTION'


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(UUIDColumn, primary_key=True, default=uuid_default)

    # Tipo dinâmico para alinhar com User.id em qualquer ambiente
    user_id = Column(UserFKType, ForeignKey('users.id'), nullable=False, index=True)

    type = Column(SQLAlchemyEnum(NotificationTypeEnum), nullable=False, index=True)
    read = Column(Boolean, default=False, nullable=False, index=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship('User')
