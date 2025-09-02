from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.administration.schema import ImportMembers, MemberRoleUpdate
from app.api.administration.service import AdministrationService
from app.api.communities.model import CommunityMember
from app.api.communities.schema import (
    CommunityMemberResponse,
    CommunityResponse,
)
from app.api.post.schemas import (
    CampaignResponse,
    CampaignUpdate,
    ComplaintResponse,
    ComplaintUpdate,
    PostFeedbackCreate,
    PostFeedbackResponse,
)
from app.auth.deps import get_db, require_roles
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/admin/{community_id}', tags=['administration'])


@router.post(
    '/users/add-users',
    response_model=list[CommunityMemberResponse],
    status_code=status.HTTP_201_CREATED,
)
def import_users_to_community(
    members: ImportMembers,
    community_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> list[CommunityMemberResponse]:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).import_users_to_community(
            members.emails, community_id
        )


@router.get(
    '/users/list-all',
    response_model=PaginationResponse[CommunityMemberResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_members_from_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> PaginationResponse[CommunityMemberResponse]:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).list_all_members_from_community(
            community_id, params
        )


@router.patch(
    '/users/{member_id}/update-role',
    response_model=CommunityMemberResponse,
    status_code=status.HTTP_200_OK,
)
def update_member_role(
    member_id: UUID,
    role_update: MemberRoleUpdate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> CommunityMemberResponse:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).update_member_role(
            member_id, role_update.new_role
        )


@router.delete(
    '/users/{member_id}/remove',
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member_from_community(
    member_id: UUID,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> None:
    with TransactionManager(session) as tm:
        AdministrationService(tm).remove_member_from_community(member_id)


@router.get(
    '/users/list-admin-communities',
    response_model=PaginationResponse[CommunityResponse],
    status_code=status.HTTP_200_OK,
)
def list_user_admin_communities(
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['admin'])),
) -> PaginationResponse[CommunityResponse]:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).list_user_admin_communities(
            current_member.user_id, params
        )


@router.patch(
    '/post/{post_id}/campaign',
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
)
def update_campaign(
    post_id: str,
    campaign_update: CampaignUpdate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> CampaignResponse:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).update_campaign(post_id, campaign_update)


@router.get(
    '/post/list-all-campaigns',
    response_model=PaginationResponse[CampaignResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_campaigns_from_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> PaginationResponse[CampaignResponse]:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).list_all_campaigns_from_community(
            community_id, params
        )


@router.patch(
    '/post/{post_id}/complaint',
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
)
def update_complaint(
    post_id: str,
    complaint_update: ComplaintUpdate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> ComplaintResponse:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).update_complaint(post_id, complaint_update)


@router.get(
    '/post/list-all-complaints',
    response_model=PaginationResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_complaints_from_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> PaginationResponse[ComplaintResponse]:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).list_all_complaints_from_community(
            community_id, params
        )


@router.post(
    '/post/create-feedback',
    response_model=PostFeedbackResponse,
    status_code=status.HTTP_200_OK,
)
def create_post_feedback(
    post: PostFeedbackCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> PostFeedbackResponse:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).create_post_feedback(post)


@router.get(
    '/post/{post_id}/list-feedbacks',
    response_model=PaginationResponse[PostFeedbackResponse],
    status_code=status.HTTP_200_OK,
)
def list_feedbacks_from_post(
    post_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin'])),
) -> PaginationResponse[PostFeedbackResponse]:
    with TransactionManager(session) as tm:
        return AdministrationService(tm).list_feedbacks_from_post(post_id, params)
