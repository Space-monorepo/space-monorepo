from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MessageStatusEnum(str, Enum):
    sent = 'sent'
    delivered = 'delivered'
    read = 'read'


class MessageBase(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=1000, description='Conteúdo da mensagem'
    )
    receiver_id: str = Field(..., description='ID do destinatário')


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str = Field(..., alias='_id')
    sender_id: str
    status: MessageStatusEnum = Field(default=MessageStatusEnum.sent)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True,
    )


class MessageUpdate(BaseModel):
    content: str | None = None
    status: MessageStatusEnum | None = None
