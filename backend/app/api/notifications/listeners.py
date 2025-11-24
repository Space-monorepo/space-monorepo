import logging
import uuid
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, event, insert, select
from sqlalchemy.orm.attributes import get_history

from app.api.communities.model import Community
from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.post.model import CampaignParticipants, CampaignPost, Post, PostFeedback

logger = logging.getLogger(__name__)


def _create_notifications_batch(connection, participant_ids, data):
    if not participant_ids:
        return

    notif_values = []
    for pid in participant_ids:
        notif_values.append({
            'id': str(uuid.uuid4()),
            'user_id': str(pid),
            'type': NotificationTypeEnum.CAMPAIGN,
            'read': False,
            'data': data,
        })

    try:
        connection.execute(insert(Notification), notif_values)
    except Exception as e:
        logger.error(f'Erro ao inserir notificações automáticas de campanha: {e}')


def _determine_event_type(target: CampaignPost) -> Optional[str]:
    status_history = get_history(target, 'status_campaign')
    participants_history = get_history(target, 'current_participants')

    if status_history.has_changes():
        new_status = target.status_campaign
        status_map = {
            'APPROVED': 'approved',
            'REJECTED': 'rejected',
            'IN_PROGRESS': 'in_progress',
            'FINISHED': 'finished',
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
    event_type = _determine_event_type(target)

    if not event_type:
        return

    info_stmt = (
        select(Post.title, Community.name)
        .join(Community, Post.community_id == Community.id)
        .where(Post.id == target.post_id)
    )
    result = connection.execute(info_stmt).first()

    if not result:
        return

    campaign_title, community_name = result

    feedback_content = None
    if event_type in {'approved', 'rejected'}:
        feedback_content = _get_feedback_content(connection, target.post_id)

    parts_stmt = select(CampaignParticipants.user_id).where(
        CampaignParticipants.campaign_id == target.post_id
    )
    participant_ids = [row[0] for row in connection.execute(parts_stmt).fetchall()]

    if not participant_ids:
        return

    data = {
        'campaign_title': campaign_title,
        'community_name': community_name,
        'campaign_status_type': event_type,
    }

    if feedback_content:
        data['feedback_content'] = feedback_content

    _create_notifications_batch(connection, participant_ids, data)


def register_listeners():
    event.listen(CampaignPost, 'after_update', campaign_post_after_update)
