from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.rating.schema import (
    RatingCreate,
    RatingResponse,
    RatingUpdate,
)
from app.rating.service import RatingService
from app.users.model import User
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/ratings', tags=['ratings'])


@router.post(
    '/{community_id}/create-rating',
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rating(
    rating: RatingCreate,
    session: Session = Depends(get_db),
    _: User = Depends(require_roles(['member'])),
) -> RatingResponse:
    with TransactionManager(session) as tm:
        return RatingService(tm).create_rating(rating)


@router.get(
    '/{community_id}/rating/{rating_id}',
    response_model=RatingResponse,
    status_code=status.HTTP_200_OK,
)
def get_rating(
    rating_id: str,
    session: Session = Depends(get_db),
    _: User = Depends(require_roles(['member'])),
) -> RatingResponse:
    with TransactionManager(session) as tm:
        return RatingService(tm).get_rating(rating_id)


@router.get(
    '/{community_id}/list-ratings',
    response_model=PaginationResponse[RatingResponse],
    status_code=status.HTTP_200_OK,
)
def list_ratings_by_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: User = Depends(require_roles(['member'])),
) -> PaginationResponse[RatingResponse]:
    with TransactionManager(session) as tm:
        return RatingService(tm).list_ratings_by_community(community_id, params)


@router.patch(
    '/{community_id}/rating/{rating_id}',
    response_model=RatingResponse,
    status_code=status.HTTP_200_OK,
)
def update_rating(
    rating_id: str,
    rating_update: RatingUpdate,
    session: Session = Depends(get_db),
    _: User = Depends(require_roles(['member'])),
) -> RatingResponse:
    with TransactionManager(session) as tm:
        return RatingService(tm).update_rating(rating_id, rating_update)


@router.delete(
    '/{community_id}/rating/{rating_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rating(
    rating_id: str,
    session: Session = Depends(get_db),
    _: User = Depends(require_roles(['member'])),
):
    with TransactionManager(session) as tm:
        RatingService(tm).delete_rating(rating_id)