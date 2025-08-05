import logging
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.api.communities.model import Community, CommunityMember
from app.api.communities.schema import CommunityMemberRoleEnum
from app.api.users.model import User
from app.core.repository import BaseRepository
from app.utils.schema import PaginationSearchParams


class CommunityRepository(BaseRepository[Community]):
    def __init__(self, session: Session):
        super().__init__(Community, session)
        self.session = session

    def list_all(self, params: PaginationSearchParams) -> tuple[List[Community], int]:
        query = self.session.query(Community)

        if params.name:
            query = query.filter(Community.name.ilike(f'%{params.name}%'))

        if params.status:
            query = query.filter(Community.type_community == params.status)

        total = query.count()
        communities = query.offset(params.offset).limit(params.limit).all()

        return communities, total


class CommunityMemberRepository(BaseRepository[CommunityMember]):
    def __init__(self, session: Session):
        super().__init__(CommunityMember, session)
        self.session = session
        self.logger = logging.getLogger(__name__)

    def get_member_association(
        self, user_id: UUID, community_id: UUID
    ) -> CommunityMember:
        member = (
            self.session.query(CommunityMember)
            .filter(
                CommunityMember.user_id == user_id,
                CommunityMember.community_id == community_id,
            )
            .first()
        )
        return member

    def member_exists(self, user_id: UUID, community_id: UUID) -> bool:
        """Check if a member association already exists"""
        return self.get_member_association(user_id, community_id) is not None

    def list_members(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[CommunityMember], int]:
        query = self.session.query(CommunityMember).filter(
            CommunityMember.community_id == community_id
        )

        if params.name:
            query = query.join(CommunityMember.user).filter(
                CommunityMember.user.name.ilike(f'%{params.name}%')
            )

        if params.status:
            query = query.filter(CommunityMember.status_participation == params.status)

        total = query.count()
        members = query.offset(params.offset).limit(params.limit).all()

        return members, total

    def list_communities_by_user(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[Community], int]:
        self.logger.debug(f'Searching for communities for user {user_id}')

        query = (
            self.session.query(Community)
            .join(CommunityMember, Community.id == CommunityMember.community_id)
            .filter(CommunityMember.user_id == user_id)
        )

        if params.name:
            query = query.filter(Community.name.ilike(f'%{params.name}%'))

        if params.status:
            query = query.filter(Community.type_community == params.status)

        query = query.order_by(Community.name)

        total = query.count()
        communities = query.offset(params.offset).limit(params.limit).all()

        return communities, total

    def list_moderators(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[CommunityMember], int]:
        query = self.session.query(CommunityMember).filter(
            CommunityMember.community_id == community_id,
            CommunityMember.role.in_([
                CommunityMemberRoleEnum.ADMIN.value,
                CommunityMemberRoleEnum.MODERATOR.value,
            ]),
        )

        if params.name:
            query = query.join(CommunityMember.user).filter(
                User.name.ilike(f'%{params.name}%')
            )

        total = query.count()
        moderators = query.offset(params.offset).limit(params.limit).all()

        return moderators, total
