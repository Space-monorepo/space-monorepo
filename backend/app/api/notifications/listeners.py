import datetime
import logging
import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, event, insert, select
from sqlalchemy.orm.attributes import get_history

# Importamos CommunityMember para buscar os destinatários dos avisos
from app.api.communities.model import Community, CommunityMember
from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.post.model import CampaignParticipants, CampaignPost, Post, PostFeedback

logger = logging.getLogger(__name__)


def _create_notifications_batch(
    connection, participant_ids, data, notification_type=NotificationTypeEnum.CAMPAIGN
):
    """
    Cria notificações em lote.
    Aceita um tipo opcional (padrão CAMPAIGN, mas pode ser OFFICIAL_NOTICE).
    """
    if not participant_ids:
        print(
            f'!!! LISTENERS: Lista de destinatários vazia para {notification_type.value}.'
        )
        return

    notif_values = []
    now = datetime.datetime.now()

    # set() evita duplicatas caso o ID venha repetido
    # Remove IDs nulos ou vazios
    valid_ids = {str(pid) for pid in participant_ids if pid}

    for pid in valid_ids:
        notif_values.append({
            'id': uuid.uuid4(),
            'user_id': str(pid),
            'type': notification_type.value,  # Usa o valor do Enum passado (ex: 'OFFICIAL_NOTICE')
            'read': False,
            'data': data,
            'created_at': now,
        })

    try:
        connection.execute(insert(Notification), notif_values)
        print(
            f'!!! LISTENERS: {len(notif_values)} notificações do tipo {notification_type.value} criadas com SUCESSO.'
        )
    except Exception as e:
        logger.error(f'Erro ao inserir notificações: {e}')
        print(f'!!! LISTENERS: Erro crítico no insert: {e}')


def _determine_event_type(target: CampaignPost) -> Optional[str]:
    status_history = get_history(target, 'status_campaign')
    participants_history = get_history(target, 'current_participants')

    if status_history.has_changes():
        raw_status = str(target.status_campaign).lower()

        # Garante que pegamos apenas o valor final se vier com prefixo de enum
        if '.' in raw_status:
            new_status = raw_status.split('.')[-1]
        else:
            new_status = raw_status

        status_map = {
            'approved': 'approved',
            'rejected': 'rejected',
            'in_progress': 'in_progress',
            'finished': 'finished',
            'canceled': 'canceled',
        }
        return status_map.get(new_status)

    if participants_history.has_changes():
        if target.current_participants >= target.target_participants:
            old_value = (
                participants_history.deleted[0] if participants_history.deleted else 0
            )
            if old_value < target.target_participants:
                return 'target_reached'

    return None


def _get_feedback_content(connection, post_id: UUID) -> Optional[str]:
    feedback_stmt = (
        select(PostFeedback.message)
        .where(PostFeedback.post_id == post_id)
        .order_by(desc(PostFeedback.created_at))
        .limit(1)
    )
    result = connection.execute(feedback_stmt).first()
    return result[0] if result else None


def campaign_post_after_update(mapper, connection, target: CampaignPost):
    """Listener para atualizações de Campanhas (Aprovação, Finalização, Cancelamento, etc)"""
    event_type = _determine_event_type(target)

    if not event_type:
        return

    info_stmt = (
        select(Post.title, Community.name, Post.user_id)
        .join(Community, Post.community_id == Community.id)
        .where(Post.id == target.post_id)
    )
    result = connection.execute(info_stmt).first()

    if not result:
        return

    campaign_title, community_name, author_id = result

    feedback_content = None
    if event_type in {'approved', 'rejected'}:
        feedback_content = _get_feedback_content(connection, target.post_id)

    parts_stmt = select(CampaignParticipants.user_id).where(
        CampaignParticipants.campaign_id == target.post_id
    )
    participant_ids = [row[0] for row in connection.execute(parts_stmt).fetchall()]

    # Inclui o autor na notificação para status importantes (incluindo canceled)
    if author_id and event_type in {'approved', 'rejected', 'finished', 'canceled'}:
        participant_ids.append(author_id)

    data = {
        'campaign_title': campaign_title,
        'community_name': community_name,
        'campaign_status_type': event_type,
    }

    if feedback_content:
        data['feedback_content'] = feedback_content

    _create_notifications_batch(
        connection,
        participant_ids,
        data,
        notification_type=NotificationTypeEnum.CAMPAIGN,
    )


def post_after_insert(mapper, connection, target: Post):
    """
    Listener para novos Posts.
    Verifica se é um ANÚNCIO (OFFICIAL_NOTICE) e notifica a comunidade.
    """
    # 1. Limpeza robusta do tipo do post
    raw_type = str(target.type_post).lower()
    if '.' in raw_type:
        clean_type = raw_type.split('.')[-1]
    else:
        clean_type = raw_type

    print(
        f"!!! LISTENERS: Novo Post inserido. Tipo detectado: '{clean_type}' (Original: '{raw_type}')"
    )

    # Verifica se é anúncio
    if clean_type != 'announcement':
        return

    print(f'!!! LISTENERS: Processando Anúncio: {target.title}')

    # Busca nome da comunidade
    community_name_stmt = select(Community.name).where(
        Community.id == target.community_id
    )
    community_name_result = connection.execute(community_name_stmt).first()
    community_name = community_name_result[0] if community_name_result else 'Comunidade'

    # Busca TODOS os membros da comunidade
    members_stmt = select(CommunityMember.user_id).where(
        CommunityMember.community_id == target.community_id,
        # CommunityMember.user_id != target.user_id  <-- COMENTADO PARA VOCÊ PODER TESTAR (RECEBER O PRÓPRIO AVISO)
    )
    member_ids = [row[0] for row in connection.execute(members_stmt).fetchall()]

    if not member_ids:
        print('!!! LISTENERS: Nenhum membro encontrado para notificar.')
        return

    data = {
        'notice_title': target.title,
        'community_name': community_name,
        'post_id': str(target.id),
    }

    _create_notifications_batch(
        connection,
        member_ids,
        data,
        notification_type=NotificationTypeEnum.OFFICIAL_NOTICE,
    )


def register_listeners():
    # Registra listener de atualização de campanha
    event.listen(CampaignPost, 'after_update', campaign_post_after_update)

    # Registra listener de criação de post (para anúncios)
    event.listen(Post, 'after_insert', post_after_insert)
