from uuid import UUID

from app.api.communities.schema import (
    CommunityMemberCreate,
    CommunityMemberResponse,
    CommunityMemberRoleEnum,
    CommunityResponse,
)
from app.api.communities.service import CommunityService
from app.api.post.exceptions import PostNotFoundError, UnexpectedPostError
from app.api.post.model import CampaignPost, PostFeedback
from app.api.post.schemas import (
    CampaignResponse,
    CampaignUpdate,
    PostFeedbackCreate,
    PostFeedbackResponse,
    PostTypeEnum,
)
from app.api.post.service import PostService
from app.api.reputation.service import ReputationService
from app.api.users.service import UserService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams


class AdministrationService:
    COMPLAINT_MEDIUM_THRESHOLD = 30
    COMPLAINT_HIGH_THRESHOLD = 50

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.post_repo = tm.get_post_repository()
        self.campaign_repo = tm.get_campaign_post_repository()
        self.campaign_participants_repo = tm.get_campaign_participants_repository()
        self.post_feedback_repo = tm.get_post_feedback_repository()
        self.post_service = PostService(tm)
        self.user_service = UserService(tm)
        self.community_service = CommunityService(tm)
        self.reputation_service = ReputationService(tm)

    def import_users_to_community(
        self, user_emails: list[str], community_id: str
    ) -> list[CommunityMemberResponse]:
        users = [self.user_service.get_by_email(email) for email in user_emails]
        members = []
        for user in users:
            community_member = CommunityMemberCreate(
                user_id=str(user.id), community_id=str(community_id)
            )
            member = self.community_service.create_member(community_member)
            members.append(self.community_service._map_member_to_response(member))
        return members

    def remove_member_from_community(self, member_id: str) -> bool:
        return self.community_service.remove_member(member_id)

    def update_member_role(
        self, member_id: UUID, new_role: CommunityMemberRoleEnum
    ) -> CommunityMemberResponse:
        return self.community_service.update_member_role(member_id, new_role)

    def list_all_members_from_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommunityMemberResponse]:
        self.community_service.get_community(community_id)
        members = self.community_service.list_members(community_id, params)
        return members

    def list_user_admin_communities(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommunityResponse]:
        user_communities = self.community_service.list_user_communities(user_id, params)
        communities_admin = []
        for community in user_communities.items:
            member_association = self.community_service.get_member_association(
                user_id, str(community.id)
            )
            if member_association.role == CommunityMemberRoleEnum.ADMIN:
                communities_admin.append(community)
        return PaginationResponse(
            items=communities_admin,
            total=len(communities_admin),
            has_more=len(communities_admin)
            > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def get_campaign(self, post_id: UUID) -> CampaignPost:
        campaign = self.campaign_repo.get_by_id(post_id)
        if not campaign:
            raise PostNotFoundError('Campaign not found')
        return campaign

    def update_campaign(
        self, post_id: UUID, campaign_update: CampaignUpdate
    ) -> CampaignResponse:
        try:
            campaign = self.get_campaign(post_id)
            old_status = campaign.status_campaign
            for key, value in campaign_update.model_dump(exclude_unset=True).items():
                setattr(campaign, key, value)
            campaign_saved = self.campaign_repo.save(campaign)

            post = self.post_service._get_post(post_id)
            member = self.community_service.get_member_association(
                post.user_id, post.community_id
            )
            self.reputation_service.reward_campaign_status_change_to_member(
                author_id=member.id,
                old_status=old_status,
                new_status=campaign_saved.status_campaign,
            )
            return CampaignResponse(
                post=self.post_service.get_post(post_id),
                target_participants=campaign_saved.target_participants,
                current_participants=campaign_saved.current_participants,
                status_campaign=campaign_saved.status_campaign,
            )
        except Exception as e:
            raise UnexpectedPostError('Unexpected error updating campaign') from e

    def list_all_campaigns_from_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CampaignResponse]:
        campaigns, total = self.campaign_repo.list_campaigns_by_community(
            community_id, params
        )
        campaigns_response = [
            CampaignResponse(
                post=self.post_service.get_post(campaign.post_id),
                target_participants=campaign.target_participants,
                current_participants=campaign.current_participants,
                status_campaign=campaign.status_campaign,
            )
            for campaign in campaigns
        ]
        return PaginationResponse(
            items=campaigns_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def create_post_feedback(self, post_feedback: PostFeedbackCreate) -> PostFeedback:
        try:
            post = self.post_service.get_post(post_feedback.post_id)
            if post.type_post not in {PostTypeEnum.CAMPAIGN, PostTypeEnum.COMPLAINT}:
                raise UnexpectedPostError('Post is not a campaign or complaint')
            self.community_service.get_member(post_feedback.member_id)
            feedback = PostFeedback(**post_feedback.model_dump())
            return self.post_feedback_repo.save(feedback)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating post feedback') from e

    def list_feedbacks_from_post(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PostFeedbackResponse]:
        feedbacks, total = self.post_feedback_repo.list_by_post(post_id, params)
        feedbacks_response = [
            PostFeedbackResponse.model_validate(feedback) for feedback in feedbacks
        ]
        return PaginationResponse(
            items=feedbacks_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )
