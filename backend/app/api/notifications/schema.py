import uuid
from datetime import datetime

from pydantic import BaseModel

from app.api.notifications.model import NotificationTypeEnum


class NotificationBase(BaseModel):
    type: NotificationTypeEnum
    data: dict | None = None


class NotificationRead(NotificationBase):
    id: uuid.UUID
    read: bool
    created_at: datetime
    message: str = ''  # Adicionado valor padrão

    class Config:
        from_attributes = True  # Permite a validação a partir de objetos do SQLAlchemy


class NotificationMarkAllRead(BaseModel):
    message: str
