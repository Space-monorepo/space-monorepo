from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.communities.model import CommunityMember
from app.api.reputation.schema import (
    PopularityScoreResponse,
    ReputationLevelResponse,
    ReputationScoreResponse,
)
from app.api.reputation.service import ReputationService
from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager

router = APIRouter(prefix='/reputation', tags=['Reputation'])


@router.get(
    '/{community_id}/score',
    response_model=ReputationScoreResponse,
    status_code=status.HTTP_200_OK,
)
def get_reputation_score(
    session: Session = Depends(get_db),
    member: CommunityMember = Depends(require_roles(['member'])),
) -> ReputationScoreResponse:
    with TransactionManager(session) as tm:
        stats = ReputationService(tm).get_member_stats(member.id)
        return ReputationScoreResponse(reputation=stats['reputation'])


@router.get(
    '/{community_id}/level',
    response_model=ReputationLevelResponse,
    status_code=status.HTTP_200_OK,
)
def get_reputation_level(
    session: Session = Depends(get_db),
    member: CommunityMember = Depends(require_roles(['member'])),
) -> ReputationLevelResponse:
    with TransactionManager(session) as tm:
        stats = ReputationService(tm).get_member_stats(member.id)
        return ReputationLevelResponse(reputation_level=stats['reputation_level'])


@router.get(
    '/{community_id}/popularity',
    response_model=PopularityScoreResponse,
    status_code=status.HTTP_200_OK,
)
def get_popularity_score(
    session: Session = Depends(get_db),
    member: CommunityMember = Depends(require_roles(['member'])),
) -> PopularityScoreResponse:
    with TransactionManager(session) as tm:
        stats = ReputationService(tm).get_member_stats(member.id)
        return PopularityScoreResponse(popularity=stats['popularity'])
