from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.badges.schema import BadgeResponse, MemberBadgeResponse
from app.api.badges.service import BadgeService
from app.api.users.schema import UserResponse
from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/badges/{community_id}', tags=['Badges'])


@router.get(
    '/badge/{badge_id}',
    response_model=BadgeResponse,
    status_code=status.HTTP_200_OK,
)
def get_badge(
    badge_id: UUID,
    session: Session = Depends(get_db),
    _: UserResponse = Depends(require_roles(['member'])),
) -> BadgeResponse:
    with TransactionManager(session) as tm:
        service = BadgeService(tm)
        badge = service.get_badge(badge_id)
        return BadgeResponse.model_validate(badge)


@router.get(
    '/list-badges',
    response_model=PaginationResponse[BadgeResponse],
    status_code=status.HTTP_200_OK,
)
def list_badges(
    community_id: UUID,
    params: PaginationSearchParams = Depends(),
    session: Session = Depends(get_db),
    _: UserResponse = Depends(require_roles(['member'])),
) -> PaginationResponse[BadgeResponse]:
    with TransactionManager(session) as tm:
        service = BadgeService(tm)
        return service.list_badges(community_id, params)


@router.get(
    '/member/{member_id}/list-badges',
    response_model=list[BadgeResponse],
    status_code=status.HTTP_200_OK,
)
def list_badges_for_member(
    member_id: UUID,
    session: Session = Depends(get_db),
    _: UserResponse = Depends(require_roles(['member'])),
) -> list[MemberBadgeResponse]:
    with TransactionManager(session) as tm:
        service = BadgeService(tm)
        badges = service.list_badges_for_member(member_id)
        return [BadgeResponse.model_validate(badge) for badge in badges]
