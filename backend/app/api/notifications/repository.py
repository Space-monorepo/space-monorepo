import uuid
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.notifications.model import Notification, NotificationTypeEnum
from app.core.repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def create(self, *, obj_in) -> Notification:
        """
        Cria uma nova notificação.
        """
        obj_data = {}
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump()
        elif isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            raise TypeError(
                f'obj_in deve ser um schema Pydantic ou um dict, mas foi {type(obj_in)}'
            )

        db_obj = self.model(**obj_data)
        return self.save(db_obj)

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 20,
        notification_type: Optional[NotificationTypeEnum] = None,
    ) -> List[Notification]:
        """Busca notificações para um usuário, com filtros."""
        query = self.session.query(self.model).filter(self.model.user_id == user_id)
        if notification_type:
            query = query.filter(self.model.type == notification_type)
        return (
            query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        )

    def mark_as_read(
        self, *, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Notification]:
        """Marca uma notificação como lida."""

        notification = self.get_by_id(id=notification_id)

        # CORREÇÃO: Converter ambos para string garante que a comparação
        # funcione tanto em testes (SQLite/String) quanto em produção (Postgres/UUID)
        if notification and str(notification.user_id) == str(user_id):
            notification.read = True
            return self.save(notification)

        return None

    def mark_all_as_read(self, *, user_id: uuid.UUID) -> int:
        """Marca todas as notificações de um usuário como lidas."""
        num_updated = (
            self.session.query(self.model)
            .filter(self.model.user_id == user_id, self.model.read == False)  # noqa: E712
            .update({'read': True}, synchronize_session=False)
        )
        return num_updated
