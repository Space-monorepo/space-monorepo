from typing import List
from uuid import UUID

from sqlalchemy import String, case, desc, select
from sqlalchemy.orm import Session

from app.api.communities.model import CommunityMember
from app.api.post.model import (
    CampaignParticipants,
    CampaignPost,
    ComplaintPost,
    PollOptions,
    PollPosts,
    Post,
    PostFeedback,
    PostLikes,
)
from app.api.post.schemas import ComplaintLevelEnum, ComplaintStatusEnum, PostStatusEnum
from app.core.repository import BaseRepository
from app.utils.schema import PaginationSearchParams


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: Session):
        super().__init__(Post, session)
        self.session = session

    def list_posts_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Post], int]:
        query = self.session.query(Post).filter(Post.community_id == community_id)

        if params.type_post:
            query = query.filter(Post.type_post == params.type_post)

        if params.status_campaign:
            query = query.filter(Post.status_campaign.in_(params.status_campaign))

        if params.name:
            query = query.filter(Post.title.ilike(f'%{params.name}%'))

        if params.status:
            query = query.filter(Post.status == params.status)

        total = query.count()
        posts = query.offset(params.offset).limit(params.limit).all()

        return posts, total

    def list_posts_by_user(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Post], int]:
        query = self.session.query(Post).filter(Post.user_id == user_id)

        if params.status:
            query = query.filter(Post.status == params.status)

        total = query.count()
        posts = query.offset(params.offset).limit(params.limit).all()

        return posts, total

    def list_reported_posts(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Post], int]:
        query = self.session.query(Post).filter(Post.community_id == community_id)
        query = query.filter(Post.status == PostStatusEnum.REPORTED)

        total = query.count()
        posts = query.offset(params.offset).limit(params.limit).all()
        return posts, total

    def list_suspended_posts(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Post], int]:
        query = self.session.query(Post).filter(Post.community_id == community_id)
        query = query.filter(Post.status == PostStatusEnum.SUSPENDED)

        total = query.count()
        posts = query.offset(params.offset).limit(params.limit).all()

        return posts, total

    def get_user_feed(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Post], int]:
        subscribed_community_ids = (
            self.session.query(CommunityMember.community_id)
            .filter(CommunityMember.user_id == user_id)
            .subquery()
        )

        query = self.session.query(Post).filter(
            Post.community_id.in_(select(subscribed_community_ids))
        )

        if params.name:
            query = query.filter(Post.title.ilike(f'%{params.name}%'))

        if params.status:
            query = query.filter(Post.status == params.status)

        total = query.count()
        query = query.order_by(desc(Post.created_at))
        posts = query.offset(params.offset).limit(params.limit).all()
        return posts, total


class ComplaintPostRepository(BaseRepository[ComplaintPost]):
    def __init__(self, session: Session):
        super().__init__(ComplaintPost, session)
        self.session = session

    def get_by_id(self, post_id: UUID) -> ComplaintPost:
        complaint = (
            self.session.query(ComplaintPost)
            .filter(ComplaintPost.post_id == post_id)
            .first()
        )
        if complaint:
            self.logger.debug(
                f'Model {ComplaintPost.__qualname__} with id {post_id} retrieved successfully'
            )
            return complaint
        else:
            self.logger.warning(
                f'Model {ComplaintPost.__qualname__} with id {post_id} not found'
            )

    def save(self, model: ComplaintPost) -> ComplaintPost:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {ComplaintPost.__qualname__} with id {model.post_id} saved successfully'
        )
        return model

    def list_complaints_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[ComplaintPost], int]:
        query = (
            self.session.query(ComplaintPost)
            .filter(ComplaintPost.status_complaint == ComplaintStatusEnum.PENDING)
            .join(Post, Post.id == ComplaintPost.post_id)
            .filter(Post.community_id == community_id)
        )

        if params.status:
            query = query.filter(Post.status.in_(params.status))

        if params.name:
            query = query.filter(Post.title.ilike(f'%{params.name}%'))

        priority_order = case(
            (ComplaintPost.level_complaint == ComplaintLevelEnum.HIGH.value, 3),
            (ComplaintPost.level_complaint == ComplaintLevelEnum.MEDIUM.value, 2),
            (ComplaintPost.level_complaint == ComplaintLevelEnum.LOW.value, 1),
            else_=0,
        )
        query = query.order_by(desc(priority_order))

        total = query.count()
        complaints = query.offset(params.offset).limit(params.limit).all()
        return complaints, total


class CampaignPostRepository(BaseRepository[CampaignPost]):
    def __init__(self, session: Session):
        super().__init__(CampaignPost, session)
        self.session = session

    def get_by_id(self, post_id: UUID) -> CampaignPost:
        campaign = (
            self.session.query(CampaignPost)
            .filter(CampaignPost.post_id == post_id)
            .first()
        )
        if campaign:
            self.logger.debug(
                f'Model {CampaignPost.__qualname__} with id {post_id} retrieved successfully'
            )
            return campaign
        else:
            self.logger.warning(
                f'Model {CampaignPost.__qualname__} with id {post_id} not found'
            )

    def save(self, model: CampaignPost) -> CampaignPost:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {CampaignPost.__qualname__} with id {model.post_id} saved successfully'
        )
        return model

    def list_campaigns_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[CampaignPost], int]:
        query = self.session.query(CampaignPost)
        query = query.join(Post, Post.id == CampaignPost.post_id)
        query = query.filter(Post.community_id == community_id)

        if params.status_campaign:
            query = query.filter(
                CampaignPost.status_campaign.in_(params.status_campaign)
            )

        if params.name:
            query = query.filter(Post.title.ilike(f'%{params.name}%'))

        if params.status:
            query = query.filter(Post.status.in_(params.status))

        total = query.count()
        campaign_posts = query.offset(params.offset).limit(params.limit).all()

        return campaign_posts, total

    def list_user_campaigns_subscriptions(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[CampaignPost], int]:
        query = (
            self.session.query(CampaignPost)
            .join(
                CampaignParticipants,
                CampaignParticipants.campaign_id == CampaignPost.post_id,
            )
            .filter(CampaignParticipants.user_id == user_id)
        )

        total = query.count()
        campaigns = query.offset(params.offset).limit(params.limit).all()
        return campaigns, total


class PollPostsRepository(BaseRepository[PollPosts]):
    def __init__(self, session: Session):
        super().__init__(PollPosts, session)
        self.session = session

    def get_by_id(self, post_id: UUID) -> PollPosts | None:
        post_id_column = PollPosts.post_id
        is_string_column = isinstance(post_id_column.type, String)
        post_id_value = str(post_id) if is_string_column else post_id

        poll = (
            self.session.query(PollPosts)
            .filter(PollPosts.post_id == post_id_value)
            .first()
        )
        if poll:
            self.logger.debug(
                f'Model {PollPosts.__qualname__} with id {post_id} retrieved successfully'
            )
            return poll
        else:
            self.logger.warning(
                f'Model {PollPosts.__qualname__} with id {post_id} not found'
            )
            return None

    def list_polls_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[PollPosts], int]:
        query = (
            self.session.query(PollPosts)
            .join(Post, Post.id == PollPosts.post_id)
            .filter(Post.community_id == community_id)
        )
        total = query.count()
        polls = query.offset(params.offset).limit(params.limit).all()
        return polls, total

    def save(self, model: PollPosts) -> PollPosts:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {PollPosts.__qualname__} with id {model.post_id} saved successfully'
        )
        return model


class PollOptionsRepository(BaseRepository[PollOptions]):
    def __init__(self, session: Session):
        super().__init__(PollOptions, session)
        self.session = session

    def list_by_post(self, post_id: UUID) -> list[PollOptions] | None:
        post_id_column = PollOptions.post_id
        is_string_column = isinstance(post_id_column.type, String)
        post_id_value = str(post_id) if is_string_column else post_id

        poll = (
            self.session.query(PollOptions)
            .filter(PollOptions.post_id == post_id_value)
            .all()
        )
        if poll:
            self.logger.debug(
                f'Model {PollOptions.__qualname__} with id {post_id} retrieved successfully'
            )
            return poll
        else:
            self.logger.warning(
                f'Model {PollOptions.__qualname__} with id {post_id} not found'
            )
            return None


class PostFeedbackRepository(BaseRepository[PostFeedback]):
    def __init__(self, session: Session):
        super().__init__(PostFeedback, session)
        self.session = session

    def get_by_id(self, post_id: UUID) -> PostFeedback:
        feedback = (
            self.session.query(PostFeedback)
            .filter(PostFeedback.post_id == post_id)
            .first()
        )
        if feedback:
            self.logger.debug(
                f'Model {PostFeedback.__qualname__} with id {post_id} retrieved successfully'
            )
            return feedback
        else:
            self.logger.warning(
                f'Model {PostFeedback.__qualname__} with id {post_id} not found'
            )

    def list_by_post(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[PostFeedback], int]:
        feedbacks = self.session.query(PostFeedback).filter(
            PostFeedback.post_id == post_id
        )
        total = feedbacks.count()
        feedbacks = feedbacks.offset(params.offset).limit(params.limit).all()
        self.logger.debug(
            f'Model {PostFeedback.__qualname__} with id {post_id} retrieved successfully'
        )
        return feedbacks, total


class CampaignParticipantsRepository(BaseRepository[CampaignParticipants]):
    def __init__(self, session: Session):
        super().__init__(CampaignParticipants, session)
        self.session = session

    def get_by_id(self, post_id: UUID, user_id: UUID) -> CampaignParticipants:
        participant = (
            self.session.query(CampaignParticipants)
            .filter(
                CampaignParticipants.campaign_id == post_id,
                CampaignParticipants.user_id == user_id,
            )
            .first()
        )
        if participant:
            self.logger.debug(
                f'Model {CampaignParticipants.__qualname__} with id {post_id} retrieved successfully'
            )
            return participant
        else:
            self.logger.warning(
                f'Model {CampaignParticipants.__qualname__} with id {post_id} not found'
            )

    def save(self, model: CampaignParticipants) -> CampaignParticipants:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {CampaignParticipants.__qualname__} with id {model.campaign_id} saved successfully'
        )
        return model

    def delete(self, model: CampaignParticipants) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {CampaignParticipants.__qualname__} with id {model.campaign_id} deleted successfully'
        )
        return True

    def list_by_post(self, post_id: UUID) -> list[CommunityMember]:
        community_members = (
            self.session.query(CommunityMember)
            .join(
                CampaignParticipants,
                CommunityMember.id == CampaignParticipants.member_id,
            )
            .filter(CampaignParticipants.campaign_id == post_id)
            .all()
        )
        return community_members


class PostLikesRepository(BaseRepository[PostLikes]):
    def __init__(self, session: Session):
        super().__init__(PostLikes, session)
        self.session = session

    def get_by_id(self, post_id: UUID, member_id: UUID) -> PostLikes:
        like = (
            self.session.query(PostLikes)
            .filter(PostLikes.post_id == post_id, PostLikes.member_id == member_id)
            .first()
        )
        if like:
            self.logger.debug(
                f'Model {PostLikes.__qualname__} with id {post_id} retrieved successfully'
            )
            return like
        else:
            self.logger.warning(
                f'Model {PostLikes.__qualname__} with id {post_id} not found'
            )

    def save(self, model: PostLikes) -> PostLikes:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {PostLikes.__qualname__} with id {model.post_id} saved successfully'
        )
        return model

    def delete(self, model: PostLikes) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {PostLikes.__qualname__} with id {model.post_id} deleted successfully'
        )
        return True

    def list_by_post(self, post_id: UUID) -> list[CommunityMember]:
        community_members = (
            self.session.query(CommunityMember)
            .join(PostLikes, CommunityMember.id == PostLikes.member_id)
            .filter(PostLikes.post_id == post_id)
            .all()
        )

        self.logger.debug(f'Retrieved {len(community_members)} likes for post {post_id}')
        return community_members
