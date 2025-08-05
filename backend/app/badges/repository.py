from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.badges.model import Badge, MemberBadge
from app.core.repository import BaseRepository
from app.utils.schema import PaginationSearchParams


class BadgeRepository(BaseRepository[Badge]):
    def __init__(self, session: Session):
        super().__init__(Badge, session)

    def get_by_name_and_community(self, name: str, community_id: UUID) -> Badge | None:
        return (
            self.session.query(Badge)
            .filter(Badge.name == name, Badge.community_id == community_id)
            .first()
        )

    def list_all(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> Tuple[List[Badge], int]:
        query = self.session.query(Badge).filter(Badge.community_id == community_id)

        if params.name:
            query = query.filter(Badge.name.ilike(f'%{params.name}%'))

        total = query.count()
        items = query.order_by(Badge.created_at.desc())

        if params.offset is not None:
            items = items.offset(params.offset)
        if params.limit is not None:
            items = items.limit(params.limit)

        return items.all(), total


class MemberBadgeRepository(BaseRepository[MemberBadge]):
    def __init__(self, session: Session):
        super().__init__(MemberBadge, session)

    def save(self, model: MemberBadge) -> MemberBadge:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {self.model.__qualname__} with id {model.member_id} and {model.badge_id} saved successfully'
        )
        return model
    
    def delete(self, model: MemberBadge) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {self.model.__qualname__} with id {model.member_id} and {model.badge_id} deleted successfully'
        )
        return True

    def get_by_member_badge(self, member_id: UUID, badge_id: UUID) -> MemberBadge | None:
        return (
            self.session.query(MemberBadge)
            .filter(
                MemberBadge.member_id == member_id,
                MemberBadge.badge_id == badge_id,
            )
            .first()
        )

    def list_by_member_id(
        self, member_id: UUID, params: PaginationSearchParams
    ) -> Tuple[List[MemberBadge], int]:
        query = self.session.query(MemberBadge).filter(
            MemberBadge.member_id == member_id
        )

        total = query.count()
        items = query.order_by(MemberBadge.achieved_at.desc())

        if params.offset is not None:
            items = items.offset(params.offset)
        if params.limit is not None:
            items = items.limit(params.limit)

        return items.all(), total

    def list_by_badge_id(
        self, badge_id: UUID, params: PaginationSearchParams
    ) -> Tuple[List[MemberBadge], int]:
        query = self.session.query(MemberBadge).filter(MemberBadge.badge_id == badge_id)

        total = query.count()
        items = query.order_by(MemberBadge.achieved_at.desc())

        if params.offset is not None:
            items = items.offset(params.offset)
        if params.limit is not None:
            items = items.limit(params.limit)

        return items.all(), total
