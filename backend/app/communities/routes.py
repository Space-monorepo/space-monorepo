from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.users.schema import UserResponse
from app.communities.schema import (
    CommunityUpdate,
    CommunityResponse,
    CommunityMemberResponse,
)
from app.communities.service import CommunityService
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/communities', tags=['communities'])

@router.get(
    '/{community_id}',
    response_model=CommunityResponse,
    status_code=status.HTTP_200_OK
)
def get_community(
    community_id: UUID,
    session: Session = Depends(get_db),
    _: UserResponse = Depends(get_current_user),
) -> CommunityResponse:
    with TransactionManager(session) as tm:
        return CommunityService(tm).get_community(community_id)


@router.get(
    '/',
    response_model=PaginationResponse[CommunityResponse],
    status_code=status.HTTP_200_OK
)
def list_communities(
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: UserResponse = Depends(get_current_user),
) -> PaginationResponse[CommunityResponse]:
    with TransactionManager(session) as tm:
        return CommunityService(tm).list_communities(params)


@router.patch(
    '/{community_id}',
    response_model=CommunityResponse,
    status_code=status.HTTP_200_OK
)
def update_community(
    community_id: UUID,
    community: CommunityUpdate,
    session: Session = Depends(get_db),
    _: UserResponse = Depends(require_roles(['admin'])),
) -> CommunityResponse:
    with TransactionManager(session) as tm:
        return CommunityService(tm).update_community(community_id, community)


@router.delete(
    '/{community_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_community(
    community_id: UUID,
    session: Session = Depends(get_db),
    _: UserResponse = Depends(require_roles(['admin'])),
):
    with TransactionManager(session) as tm:
        CommunityService(tm).delete_community(community_id)


@router.get(
    '/{community_id}/members',
    response_model=PaginationResponse[CommunityMemberResponse],
    status_code=status.HTTP_200_OK
)
def list_community_members(
    community_id: UUID,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: UserResponse = Depends(get_current_user),
) -> PaginationResponse[CommunityMemberResponse]:
    with TransactionManager(session) as tm:
        return CommunityService(tm).list_members(community_id, params)


@router.get(
    '/user/{user_id}/communities',
    response_model=PaginationResponse[CommunityResponse],
    status_code=status.HTTP_200_OK
)
def list_user_communities(
    user_id: UUID,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: UserResponse = Depends(get_current_user),
) -> PaginationResponse[CommunityResponse]:
    with TransactionManager(session) as tm:
        return CommunityService(tm).list_user_communities(user_id, params)


@router.get(
    '/{community_id}/moderators',
    response_model=PaginationResponse[CommunityMemberResponse],
    status_code=status.HTTP_200_OK
)
def list_community_moderators(
    community_id: UUID,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: UserResponse = Depends(get_current_user),
) -> PaginationResponse[CommunityMemberResponse]:
    with TransactionManager(session) as tm:
        return CommunityService(tm).list_moderators(community_id, params)
