import logging

from sqlalchemy.orm import Session

from app.api.badges.repository import BadgeRepository, MemberBadgeRepository
from app.api.chat.repository import (
    ConversationRepository,
    MessageAttachmentRepository,
    MessageRepository,
)
from app.api.comment.repository import CommentLikesRepository, CommentRepository
from app.api.communities.repository import CommunityMemberRepository, CommunityRepository
from app.api.post.repository import (
    CampaignParticipantsRepository,
    CampaignPostRepository,
    ComplaintPostRepository,
    PollOptionsRepository,
    PollPostsRepository,
    PostFeedbackRepository,
    PostLikesRepository,
    PostRepository,
)
from app.api.rating.repository import RatingRepository
from app.api.reports.repository import (
    ModerationVotesRepository,
    ReportCommentRepository,
    ReportMemberRepository,
    ReportPostRepository,
    ReportRepository,
)
from app.api.users.repository import UserConnectionRepository, UserRepository

logger = logging.getLogger(__name__)


class TransactionManager:
    def __init__(self, session: Session):
        self._session = session

    def __enter__(self):
        logger.debug('Initiating transactional block')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.warning(
                f'Error on block transactional: {exc_val}. Performing rollback.',
                exc_info=True,
            )
            self._session.rollback()
        else:
            try:
                logger.debug(
                    'Transactional block completed with success. Performing success.'
                )
                self._session.commit()
            except Exception as e:
                logger.error(
                    f'Error during committing: {e}. Performing rollback.', exc_info=True
                )
                self._session.rollback()
                raise
            finally:
                logger.debug('Closing TransactionManager session')

    def get_user_repository(self):
        return UserRepository(self._session)

    def get_post_repository(self):
        return PostRepository(self._session)

    def get_complaint_post_repository(self):
        return ComplaintPostRepository(self._session)

    def get_campaign_post_repository(self):
        return CampaignPostRepository(self._session)

    def get_campaign_participants_repository(self):
        return CampaignParticipantsRepository(self._session)

    def get_post_feedback_repository(self):
        return PostFeedbackRepository(self._session)

    def get_poll_posts_repository(self):
        return PollPostsRepository(self._session)

    def get_poll_options_repository(self):
        return PollOptionsRepository(self._session)

    def get_post_likes_repository(self):
        return PostLikesRepository(self._session)

    def get_community_repository(self):
        return CommunityRepository(self._session)

    def get_member_repository(self):
        return CommunityMemberRepository(self._session)

    def get_badge_repository(self):
        return BadgeRepository(self._session)

    def get_member_badge_repository(self):
        return MemberBadgeRepository(self._session)

    def get_rating_repository(self):
        return RatingRepository(self._session)

    def get_comment_repository(self):
        return CommentRepository(self._session)

    def get_comment_likes_repository(self):
        return CommentLikesRepository(self._session)

    def get_user_connection_repository(self):
        return UserConnectionRepository(self._session)

    def get_report_repository(self):
        return ReportRepository(self._session)

    def get_report_member_repository(self):
        return ReportMemberRepository(self._session)

    def get_report_post_repository(self):
        return ReportPostRepository(self._session)

    def get_report_comment_repository(self):
        return ReportCommentRepository(self._session)

    def get_moderation_votes_repository(self):
        return ModerationVotesRepository(self._session)

    def get_conversation_repository(self):
        return ConversationRepository(self._session)

    def get_message_repository(self):
        return MessageRepository(self._session)

    def get_message_attachment_repository(self):
        return MessageAttachmentRepository(self._session)
