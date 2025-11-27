import datetime
import logging
import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, event, insert, select
from sqlalchemy.orm.attributes import get_history

# IMPORTANTE: Importando os models corretos de Comentário
from app.api.comment.model import Comment, CommentLikes

# Models necessários
from app.api.communities.model import Community, CommunityMember
from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.post.model import (
    CampaignParticipants,
    CampaignPost,
    Post,
    PostFeedback,
    PostLikes,
)
from app.api.users.model import User

logger = logging.getLogger(__name__)


# --- FUNÇÕES AUXILIARES ---


def _create_single_notification(connection, user_id, data, notification_type):
    """
    Cria uma única notificação diretamente no banco.
    """
    if not user_id:
        return

    try:
        stmt = insert(Notification).values(
            id=uuid.uuid4(),
            user_id=str(user_id),
            type=notification_type.value,
            read=False,
            data=data,
            created_at=datetime.datetime.now(),
        )
        connection.execute(stmt)
    except Exception as e:
        logger.error(f'Erro ao criar notificação via listener: {e}')


def _create_notifications_batch(
    connection, participant_ids, data, notification_type=NotificationTypeEnum.CAMPAIGN
):
    """
    Cria notificações em lote (Campanhas/Avisos).
    """
    if not participant_ids:
        return

    notif_values = []
    now = datetime.datetime.now()
    valid_ids = {str(pid) for pid in participant_ids if pid}

    for pid in valid_ids:
        notif_values.append({
            'id': uuid.uuid4(),
            'user_id': str(pid),
            'type': notification_type.value,
            'read': False,
            'data': data,
            'created_at': now,
        })

    try:
        connection.execute(insert(Notification), notif_values)
    except Exception as e:
        logger.error(f'Erro ao inserir notificações em lote: {e}')


def _determine_event_type(target: CampaignPost) -> Optional[str]:
    status_history = get_history(target, 'status_campaign')
    participants_history = get_history(target, 'current_participants')

    if status_history.has_changes():
        raw_status = str(target.status_campaign).lower()
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


# --- LISTENERS DE CAMPANHA E AVISOS ---


def campaign_post_after_update(mapper, connection, target: CampaignPost):
    """Listener para atualizações de Campanhas"""
    try:
        event_type = _determine_event_type(target)
        if not event_type:
            return

        info_stmt = (
            select(Post.title, Community.name, Post.user_id, Post.community_id)
            .join(Community, Post.community_id == Community.id)
            .where(Post.id == target.post_id)
        )
        result = connection.execute(info_stmt).first()

        if not result:
            return

        campaign_title, community_name, author_id, community_id = result

        feedback_content = None
        if event_type in {'approved', 'rejected'}:
            feedback_content = _get_feedback_content(connection, target.post_id)

        parts_stmt = select(CampaignParticipants.user_id).where(
            CampaignParticipants.campaign_id == target.post_id
        )
        participant_ids = [row[0] for row in connection.execute(parts_stmt).fetchall()]

        if author_id and event_type in {'approved', 'rejected', 'finished', 'canceled'}:
            participant_ids.append(author_id)

        data = {
            'campaign_title': campaign_title,
            'community_name': community_name,
            'campaign_status_type': event_type,
            'post_id': str(target.post_id),
            'community_id': str(community_id),
            'current_participants': target.current_participants,
            'target_participants': target.target_participants,
        }

        if feedback_content:
            data['feedback_content'] = feedback_content

        _create_notifications_batch(
            connection,
            participant_ids,
            data,
            notification_type=NotificationTypeEnum.CAMPAIGN,
        )
    except Exception as e:
        logger.error(f'Erro no listener de campanha: {e}')


def post_after_insert(mapper, connection, target: Post):
    """Listener para novos Anúncios (Official Notice)"""
    try:
        raw_type = str(target.type_post).lower()
        if '.' in raw_type:
            clean_type = raw_type.split('.')[-1]
        else:
            clean_type = raw_type

        if clean_type != 'announcement':
            return

        community_name_stmt = select(Community.name).where(
            Community.id == target.community_id
        )
        community_name_result = connection.execute(community_name_stmt).first()
        community_name = (
            community_name_result[0] if community_name_result else 'Comunidade'
        )

        members_stmt = select(CommunityMember.user_id).where(
            CommunityMember.community_id == target.community_id,
        )
        member_ids = [row[0] for row in connection.execute(members_stmt).fetchall()]

        data = {
            'notice_title': target.title,
            'community_name': community_name,
            'post_id': str(target.id),
            'community_id': str(target.community_id),
        }

        _create_notifications_batch(
            connection,
            member_ids,
            data,
            notification_type=NotificationTypeEnum.OFFICIAL_NOTICE,
        )
    except Exception as e:
        logger.error(f'Erro no listener de anúncio: {e}')


# --- NOVOS LISTENERS PARA INTERAÇÕES (CORRIGIDOS) ---


def post_like_after_insert(mapper, connection, target: PostLikes):
    """Disparado quando ocorre um LIKE em POST."""
    try:
        post_q = (
            select(Post.title, Post.user_id, Post.community_id, Community.name)
            .join(Community, Post.community_id == Community.id)
            .where(Post.id == target.post_id)
        )
        post_res = connection.execute(post_q).first()

        if not post_res:
            return
        post_title, post_author_id, community_id, community_name = post_res

        actor_q = (
            select(User.name, User.id, User.username, User.profile_image_url)
            .join(CommunityMember, CommunityMember.user_id == User.id)
            .where(CommunityMember.id == target.member_id)
        )
        actor_res = connection.execute(actor_q).first()

        if not actor_res:
            return
        actor_name, actor_user_id, actor_username, actor_picture = actor_res

        if str(post_author_id) == str(actor_user_id):
            return

        data = {
            'interaction_type': 'like',
            'actor_name': actor_name,
            'actor_username': actor_username,
            'actor_picture': actor_picture,
            'post_title': post_title,
            'actor_id': str(actor_user_id),
            'post_id': str(target.post_id),
            'community_id': str(community_id),
            'community_name': community_name,
        }

        _create_single_notification(
            connection, post_author_id, data, NotificationTypeEnum.INTERACTION
        )

    except Exception as e:
        logger.error(f'Erro no listener de Like: {e}')


def comment_after_insert(mapper, connection, target: Comment):
    """Disparado quando ocorre um COMENTÁRIO REAL."""
    try:
        # 1. Buscar Post e Comunidade
        post_q = (
            select(Post.title, Post.user_id, Post.community_id, Community.name)
            .join(Community, Post.community_id == Community.id)
            .where(Post.id == target.post_id)
        )
        post_res = connection.execute(post_q).first()

        if not post_res:
            return
        post_title, post_author_id, community_id, community_name = post_res

        # 2. Buscar quem comentou (via CommunityMember)
        actor_q = (
            select(User.name, User.id, User.username, User.profile_image_url)
            .join(CommunityMember, CommunityMember.user_id == User.id)
            .where(CommunityMember.id == target.member_id)
        )
        actor_res = connection.execute(actor_q).first()

        if not actor_res:
            return
        actor_name, actor_user_id, actor_username, actor_picture = actor_res

        # 3. Não notificar se for o próprio dono do post
        if str(post_author_id) == str(actor_user_id):
            return

        data = {
            'interaction_type': 'comment',
            'actor_name': actor_name,
            'actor_username': actor_username,
            'actor_picture': actor_picture,
            'post_title': post_title,
            'comment_content': target.content,  # Comment usa 'content', não 'message'
            'actor_id': str(actor_user_id),
            'post_id': str(target.post_id),
            'comment_id': str(target.id),
            'community_id': str(community_id),
            'community_name': community_name,
        }

        _create_single_notification(
            connection, post_author_id, data, NotificationTypeEnum.INTERACTION
        )

    except Exception as e:
        logger.error(f'Erro no listener de Comentário: {e}')


def comment_like_after_insert(mapper, connection, target: CommentLikes):  # noqa: PLR0914
    """Disparado quando ocorre um LIKE em COMENTÁRIO."""
    try:
        # 1. Buscar Comentário, Post e Comunidade
        # Precisamos fazer join: CommentLikes -> Comment -> Post -> Community

        # Primeiro pegamos o comentário para saber o dono dele (quem recebe a notificação)
        comment_q = select(Comment.member_id, Comment.post_id, Comment.content).where(
            Comment.id == target.comment_id
        )
        comment_res = connection.execute(comment_q).first()
        if not comment_res:
            return
        comment_owner_member_id, post_id, comment_content = comment_res

        # Buscar ID do usuário dono do comentário
        owner_q = (
            select(User.id)
            .join(CommunityMember, CommunityMember.user_id == User.id)
            .where(CommunityMember.id == comment_owner_member_id)
        )
        owner_res = connection.execute(owner_q).first()
        if not owner_res:
            return
        recipient_user_id = owner_res[0]

        # Buscar dados do Post e Comunidade
        post_q = (
            select(Post.title, Post.community_id, Community.name)
            .join(Community, Post.community_id == Community.id)
            .where(Post.id == post_id)
        )
        post_res = connection.execute(post_q).first()
        if not post_res:
            return
        post_title, community_id, community_name = post_res

        # Buscar quem curtiu (Actor)
        actor_q = (
            select(User.name, User.id, User.username, User.profile_image_url)
            .join(CommunityMember, CommunityMember.user_id == User.id)
            .where(CommunityMember.id == target.member_id)
        )
        actor_res = connection.execute(actor_q).first()
        if not actor_res:
            return
        actor_name, actor_user_id, actor_username, actor_picture = actor_res

        # Não notificar se curtiu o próprio comentário
        if str(recipient_user_id) == str(actor_user_id):
            return

        data = {
            'interaction_type': 'comment_like',
            'actor_name': actor_name,
            'actor_username': actor_username,
            'actor_picture': actor_picture,
            'post_title': post_title,
            'comment_content': comment_content,
            'actor_id': str(actor_user_id),
            'post_id': str(post_id),
            'comment_id': str(target.comment_id),
            'community_id': str(community_id),
            'community_name': community_name,
        }

        _create_single_notification(
            connection, recipient_user_id, data, NotificationTypeEnum.INTERACTION
        )

    except Exception as e:
        logger.error(f'Erro no listener de Like em Comentário: {e}')


def register_listeners():
    event.listen(CampaignPost, 'after_update', campaign_post_after_update)
    event.listen(Post, 'after_insert', post_after_insert)
    event.listen(PostLikes, 'after_insert', post_like_after_insert)

    # NOVOS REGISTROS PARA COMENTÁRIOS REAIS
    event.listen(Comment, 'after_insert', comment_after_insert)
    event.listen(CommentLikes, 'after_insert', comment_like_after_insert)
