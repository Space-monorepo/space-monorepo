import uuid
from typing import List, Optional

from sqlalchemy import String, cast, desc
from sqlalchemy.orm import Session

from app.api.notifications.model import Notification, NotificationTypeEnum
from app.core.repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def create(self, *, obj_in) -> Notification:
        obj_data = {}
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump()
        elif isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            raise TypeError(f'obj_in invalido: {type(obj_in)}')

        db_obj = self.model(**obj_data)
        return self.save(db_obj)

    def get_by_user_id(
        self,
        user_id: uuid.UUID | str,
        *,
        skip: int = 0,
        limit: int = 20,
        notification_type: Optional[NotificationTypeEnum] = None,
    ) -> List[Notification]:
        # CORREÇÃO DEFINITIVA: Cast para String
        # Isso converte a coluna user_id (seja UUID ou VARCHAR) para texto e compara com a string do ID.
        query = self.session.query(self.model).filter(
            cast(self.model.user_id, String) == str(user_id)
        )

        if notification_type:
            query = query.filter(self.model.type == notification_type)

        return (
            query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        )

    def count_unread(self, *, user_id: uuid.UUID | str) -> int:
        """Conta o número de notificações não lidas para um usuário."""
        count = (
            self.session.query(self.model)
            .filter(
                cast(self.model.user_id, String) == str(user_id),
                self.model.read == False,  # noqa: E712
            )
            .count()
        )
        return count

    def mark_as_read(
        self, *, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Notification]:
        notification = self.get_by_id(id=notification_id)

        # Comparação segura convertendo ambos para string
        if notification and str(notification.user_id) == str(user_id):
            notification.read = True
            return self.save(notification)

        return None

    def mark_all_as_read(self, *, user_id: uuid.UUID) -> int:
        # Filtro com Cast para garantir compatibilidade
        num_updated = (
            self.session.query(self.model)
            .filter(
                cast(self.model.user_id, String) == str(user_id),
                self.model.read == False,  # noqa: E712
            )
            .update({'read': True}, synchronize_session=False)
        )
        return num_updated
