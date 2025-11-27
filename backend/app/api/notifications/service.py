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
            campaign_title = data.get('campaign_title', 'Campanha')
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
                    'default': f'Nova campanha em {community_name}: {campaign_title}',
                    'approved': f'Sua campanha "{campaign_title}" foi aprovada!',
                    'rejected': f'Sua campanha "{campaign_title}" não foi aprovada.',
                    'finished': f'A campanha "{campaign_title}" foi finalizada.',
                    'canceled': f'A campanha "{campaign_title}" foi cancelada.',
                    'target_reached': f'A campanha "{campaign_title}" atingiu a meta!',
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
                subtype_key = data.get('interaction_type', 'like')
            elif notif_type == NotificationTypeEnum.CONNECTION:
                subtype_key = data.get('connection_type', 'default')
            elif notif_type == NotificationTypeEnum.CAMPAIGN:
                subtype_key = data.get('campaign_status_type', 'default')

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
        notification_data = {'user_id': str(user_id), 'type': type, 'data': data}
        return self.notification_repo.create(obj_in=notification_data)

    def create_interaction_notification(  # noqa: PLR0913
        self,
        *,
        recipient: User,
        actor: User,
        interaction_type: str,
        post_title: str,
        community_id: Optional[uuid.UUID | str] = None,
        community_name: Optional[str] = None,
        post_id: Optional[uuid.UUID | str] = None,
        comment_id: Optional[uuid.UUID | str] = None,
        comment_content: Optional[str] = None,
    ):
        # SEGURANÇA: Se vier sem post_id, ignora para deixar o Listener criar a certa.
        # Correção PLR6201: Usando set {} em vez de list []
        if interaction_type in {'like', 'comment'} and not post_id:
            return None

        actor_username = getattr(actor, 'username', 'user')
        actor_picture = getattr(actor, 'profile_image_url', None)

        data = {
            'interaction_type': interaction_type,
            'actor_id': str(actor.id),
            'actor_name': actor.name,
            'actor_username': actor_username,
            'actor_picture': actor_picture,
            'post_title': post_title,
        }

        if community_id:
            data['community_id'] = str(community_id)
        if community_name:
            data['community_name'] = community_name
        if post_id:
            data['post_id'] = str(post_id)
        if comment_content:
            data['comment_content'] = comment_content
        if comment_id:
            data['comment_id'] = str(comment_id)

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
            'actor_username': getattr(actor, 'username', ''),
            'actor_picture': getattr(actor, 'profile_image_url', None),
        }

        return self.create_notification(
            user_id=recipient.id, type=NotificationTypeEnum.CONNECTION, data=data
        )

    def get_user_notifications(
        self, *, user: User, notification_type: Optional[NotificationTypeEnum] = None
    ) -> List[schema.NotificationRead]:
        db_notifications = self.notification_repo.get_by_user_id(
            user_id=user.id, notification_type=notification_type
        )

        response_notifications = []
        for notif in db_notifications:
            message = self._format_notification_message(notif)
            response = schema.NotificationRead.model_validate(notif)
            response.message = message
            response_notifications.append(response)

        return response_notifications

    def get_unread_count(self, *, user: User) -> dict:
        count = self.notification_repo.count_unread(user_id=user.id)
        return {'count': count}

    def mark_as_read(
        self, *, notification_id: uuid.UUID, user: User
    ) -> Optional[schema.NotificationRead]:
        db_notification = self.notification_repo.mark_as_read(
            notification_id=notification_id, user_id=user.id
        )

        if db_notification:
            message = self._format_notification_message(db_notification)
            response = schema.NotificationRead.model_validate(db_notification)
            response.message = message
            return response
        return None

    def mark_all_as_read(self, *, user: User) -> dict:
        count = self.notification_repo.mark_all_as_read(user_id=user.id)
        return {'message': f'{count} notificações marcadas como lidas.'}
