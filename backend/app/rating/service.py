from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.communities.exceptions import CommunityNotFoundError, CommunityMemberNotFoundError
from app.communities.service import CommunityService
from app.core.transaction import TransactionManager
from app.rating.exceptions import (
    RatingNotFoundError,
    RatingAlreadyExistsError,
    UnexpectedRatingError,
)
from app.rating.model import Rating
from app.rating.schema import (
    RatingCreate,
    RatingResponse,
    RatingUpdate,
)
from app.utils.schema import PaginationResponse, PaginationSearchParams


class RatingService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.rating_repo = tm.get_rating_repository()
        self.community_service = CommunityService(tm)

    def _get_rating(self, rating_id: UUID) -> Rating:
        rating = self.rating_repo.get_by_id(rating_id)
        if not rating:
            raise RatingNotFoundError('Rating not found')
        return rating

    def create_rating(self, rating: RatingCreate) -> RatingResponse:
        try:
            community = self.community_service.get_community(rating.community_id)
            if not community:
                raise CommunityNotFoundError('Community not found')
                
            member = self.community_service.get_member_association(
                rating.user_id, rating.community_id
            )
            if not member:
                raise CommunityMemberNotFoundError('User is not a member of this community')
            
            rating_model = Rating(**rating.model_dump())
            rating_saved = self.rating_repo.save(rating_model)
            return RatingResponse.model_validate(rating_saved)
        except IntegrityError:
            raise RatingAlreadyExistsError('User has already rated this community')
        except (CommunityNotFoundError, CommunityMemberNotFoundError):
            raise
        except Exception as e:
            raise UnexpectedRatingError('Unexpected error creating rating') from e


    def get_rating(self, rating_id: UUID) -> RatingResponse:
        rating = self._get_rating(rating_id)
        return RatingResponse.model_validate(rating)

    def list_ratings_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[RatingResponse]:
        try:
            ratings, total = self.rating_repo.list_ratings_by_community(community_id, params)
            return PaginationResponse(
                items=[RatingResponse.model_validate(rating) for rating in ratings],
                total=total,
                has_more=total > (params.offset or 0) + (params.limit or 10),
                current_offset=params.offset or 0,
                current_limit=params.limit or 10,
            )
        except Exception as e:
            raise UnexpectedRatingError('Unexpected error listing ratings by community') from e

    def update_rating(self, rating_id: UUID, rating_update: RatingUpdate) -> RatingResponse:
        try:
            rating = self._get_rating(rating_id)
            
            if rating_update.rating is not None:
                rating.rating = rating_update.rating
            if rating_update.title is not None:
                rating.title = rating_update.title
            if rating_update.description is not None:
                rating.description = rating_update.description
            
            rating_saved = self.rating_repo.save(rating)
            return RatingResponse.model_validate(rating_saved)
        except Exception as e:
            raise UnexpectedRatingError('Unexpected error updating rating') from e

    def delete_rating(self, rating_id: UUID) -> bool:
        try:
            rating = self._get_rating(rating_id)
            return self.rating_repo.delete(rating)
        except Exception as e:
            raise UnexpectedRatingError('Unexpected error deleting rating') from e