import logging
import uuid
from typing import Any, Dict, List, Optional

from app.api.notifications import schema
from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.notifications.repository import NotificationRepository
from app.api.users.model import User
from app.core.transaction import TransactionManager

NOTIFICATION_CONTENT_TRUNCATE_LENGTH = 30


class NotificationService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.notification_repo: NotificationRepository = tm.get_notification_repository()

    @staticmethod
    def _get_truncated_content(content: str, length: int) -> str:
        """Trunca o conteúdo do comentário se for muito longo."""
        if len(content) > length:
            return content[:length] + '...'
        return content

    @staticmethod
    # ruff: noqa: PLR0911
    def _format_notification_message(notification: Notification) -> str:
        data = notification.data or {}
        notif_type = notification.type

        try:
            actor_name = data.get('actor_name', 'Alguém')
            post_title = data.get('post_title', 'sua publicação')
            comment_content = data.get('comment_content', 'um comentário')
            community_name = data.get('community_name', 'uma comunidade')
            truncated_comment = NotificationService._get_truncated_content(
                comment_content, NOTIFICATION_CONTENT_TRUNCATE_LENGTH
            )

            MESSAGE_TEMPLATES = {
                NotificationTypeEnum.INTERACTION: {
                    'like': f'{actor_name} curtiu {post_title}.',
                    'comment': f'{actor_name} comentou em {post_title}: "{truncated_comment}"',
                    'comment_like': f'{actor_name} curtiu seu comentário: "{truncated_comment}"',
                },
                NotificationTypeEnum.CONNECTION: {
                    'new_member': f'{actor_name} entrou na comunidade {community_name}.',
                    'badge': f'Você recebeu um novo emblema: {data.get("badge_name", "Novo Emblema")}',
                    'follow_request': f'{actor_name} quer te seguir.',
                    'follow_accepted': f'{actor_name} aceitou sua solicitação de conexão.',
                    'request_received': f'{actor_name} quer se conectar com você.',
                },
                NotificationTypeEnum.CAMPAIGN: {
                    'default': f'Nova campanha em {community_name}: {data.get("campaign_title", "Participe!")}'
                },
                NotificationTypeEnum.OFFICIAL_NOTICE: {
                    'default': f'Aviso do Space: {data.get("notice_title", "Temos novidades")}'
                },
            }

            type_map = MESSAGE_TEMPLATES.get(notif_type)
            if not type_map:
                return 'Você tem uma nova notificação.'

            subtype_key = 'default'
            if notif_type == NotificationTypeEnum.INTERACTION:
                subtype_key = data.get('interaction_type')
            elif notif_type == NotificationTypeEnum.CONNECTION:
                subtype_key = data.get('connection_type')

            return type_map.get(subtype_key, 'Você tem uma nova notificação.')

        except Exception as e:
            logging.error(
                f'Erro ao formatar mensagem da notificação {notification.id}: {e}'
            )
            return 'Você tem uma nova notificação.'

    def create_notification(
        self,
        *,
        user_id: uuid.UUID | str,
        type: NotificationTypeEnum,
        data: Dict[str, Any],
    ) -> Notification:
        logging.warning(
            f'!!!!!!!!! TENTANDO CRIAR NOTIFICACAO DO TIPO: {type} PARA O USUARIO: {user_id} !!!!!!!!!'
        )

        # CORREÇÃO: O model agora espera um str (as_uuid=False)
        notification_data = {'user_id': str(user_id), 'type': type, 'data': data}

        db_notification = self.notification_repo.create(obj_in=notification_data)

        return db_notification

    def create_interaction_notification(
        self,
        *,
        recipient: User,
        actor: User,
        interaction_type: str,
        post_title: str,
        comment_content: Optional[str] = None,
    ):
        data = {
            'interaction_type': interaction_type,
            'actor_id': str(actor.id),
            'actor_name': actor.name,
            'post_title': post_title,
        }
        if comment_content:
            data['comment_content'] = comment_content

        return self.create_notification(
            user_id=recipient.id, type=NotificationTypeEnum.INTERACTION, data=data
        )

    def create_connection_notification(
        self,
        *,
        recipient: User,
        actor: User,
        connection_type: str,
    ):
        data = {
            'connection_type': connection_type,
            'actor_id': str(actor.id),
            'actor_name': actor.name,
        }

        return self.create_notification(
            user_id=recipient.id, type=NotificationTypeEnum.CONNECTION, data=data
        )

    def get_user_notifications(
        self, *, user: User, notification_type: Optional[NotificationTypeEnum] = None
    ) -> List[schema.NotificationRead]:
        logging.warning(
            f'!!!!!!!!! TENTANDO LER NOTIFICACOES PARA O USUARIO: {user.id} !!!!!!!!!'
        )

        db_notifications = self.notification_repo.get_by_user_id(
            user_id=user.id, notification_type=notification_type
        )

        response_notifications = []
        for notif in db_notifications:
            message = self._format_notification_message(notif)
            # CORREÇÃO: Usar model_validate (ou from_orm) para converter o modelo
            response = schema.NotificationRead.model_validate(notif)
            response.message = message
            response_notifications.append(response)

        return response_notifications

    def mark_as_read(
        self, *, notification_id: uuid.UUID, user: User
    ) -> Optional[schema.NotificationRead]:
        db_notification = self.notification_repo.mark_as_read(
            notification_id=notification_id, user_id=user.id
        )

        if db_notification:
            message = self._format_notification_message(db_notification)
            # CORREÇÃO: Usar model_validate (ou from_orm) para converter o modelo
            response = schema.NotificationRead.model_validate(db_notification)
            response.message = message
            return response
        return None

    def mark_all_as_read(self, *, user: User) -> dict:
        count = self.notification_repo.mark_all_as_read(user_id=user.id)
        return {'message': f'{count} notificações marcadas como lidas.'}
