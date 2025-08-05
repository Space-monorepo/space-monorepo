from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.rating.model import Rating
from app.core.repository import BaseRepository
from app.utils.schema import PaginationSearchParams


class RatingRepository(BaseRepository[Rating]):
    def __init__(self, session: Session):
        super().__init__(Rating, session)
        self.session = session

    def list_ratings_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[Rating], int]:
        query = self.session.query(self.model).filter(
            self.model.community_id == community_id
        )

        if params.name:
            query = query.filter(
                self.model.title.ilike(f'%{params.name}%')
                | self.model.description.ilike(f'%{params.name}%')
            )

        query = query.order_by(desc(self.model.created_at))

        ratings = query.offset(params.offset).limit(params.limit).all()
        total = query.count()

        self.logger.debug(f'Listing ratings for community {community_id}')
        return ratings, total
