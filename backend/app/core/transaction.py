import logging

from sqlalchemy.orm import Session

from app.communities.repository import CommunityMemberRepository, CommunityRepository
from app.comment.repository import CommentRepository, CommentLikesRepository
from app.post.repository import (
    CampaignParticipantsRepository,
    CampaignPostRepository,
    ComplaintPostRepository,
    PostFeedbackRepository,
    PostRepository,
    PollPostsRepository,
    PollOptionsRepository,
    PostLikesRepository
)
from app.rating.repository import RatingRepository
from app.users.repository import UserRepository
from app.badges.repository import BadgeRepository, MemberBadgeRepository

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
      