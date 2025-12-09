from uuid import UUID

from app.api.badges.exceptions import (
    BadgeAlreadyExistsError,
    BadgeNotFoundError,
    CannotDeleteSystemBadgeError,
    MemberAlreadyHasBadgeError,
    MemberBadgeNotFoundError,
    UnexpectedBadgeError,
)
from app.api.badges.model import Badge, MemberBadge
from app.api.badges.schema import (
    BadgeCreate,
    BadgeResponse,
    BadgeUpdate,
    MemberBadgeCreate,
)
from app.api.communities.service import CommunityService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

SYSTEM_BADGE_NAMES = ['Líder', 'Ativo', 'Amigável', 'Efetivo']


class BadgeService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.badge_repo = tm.get_badge_repository()
        self.member_badge_repo = tm.get_member_badge_repository()
        self.community_service = CommunityService(tm)

    def create_badge(self, badge_data: BadgeCreate) -> Badge:
        self.community_service.get_community(badge_data.community_id)
        badge_already_exists = self.badge_repo.get_by_name_and_community(
            badge_data.name, badge_data.community_id
        )
        if badge_already_exists:
            raise BadgeAlreadyExistsError(
                f"Badge '{badge_data.name}' already exists in community '{badge_data.community_id}'."
            )
        try:
            badge = Badge(**badge_data.model_dump())
            saved_badge = self.badge_repo.save(badge)
            return saved_badge
        except Exception as e:
            raise UnexpectedBadgeError(
                f'Unexpected error creating badge: {str(e)}'
            ) from e

    def get_badge(self, badge_id: UUID) -> Badge:
        badge = self.badge_repo.get_by_id(badge_id)
        if not badge:
            raise BadgeNotFoundError(f"Badge with id '{badge_id}' not found.")
        return badge

    def update_badge(self, badge_id: UUID, badge_update: BadgeUpdate) -> Badge:
        badge = self.get_badge(badge_id)

        if badge_update.name and badge_update.name != badge.name:
            badge_already_exists = self.badge_repo.get_by_name_and_community(
                badge_update.name, badge.community_id
            )
            if badge_already_exists:
                raise BadgeAlreadyExistsError(
                    f"Badge '{badge_update.name}' already exists in community '{badge.community_id}'."
                )

        for key, value in badge_update.model_dump(exclude_unset=True).items():
            setattr(badge, key, value)

        try:
            updated_badge = self.badge_repo.save(badge)
            return updated_badge
        except Exception as e:
            raise UnexpectedBadgeError(
                f"Unexpected error updating badge '{badge_id}': {str(e)}"
            ) from e

    def delete_badge(self, badge_id: UUID) -> bool:
        badge = self.get_badge(badge_id)
        if badge.name in SYSTEM_BADGE_NAMES:
            raise CannotDeleteSystemBadgeError(
                f"System badge '{badge.name}' (from community {badge.community_id}) cannot be deleted."
            )
        try:
            return self.badge_repo.delete(badge)
        except Exception as e:
            raise UnexpectedBadgeError(
                f"Unexpected error deleting badge '{badge_id}': {str(e)}"
            ) from e

    def list_badges(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[BadgeResponse]:
        badges, total = self.badge_repo.list_all(community_id, params)
        items = [BadgeResponse.model_validate(badge) for badge in badges]
        return PaginationResponse(
            items=items,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def assign_badge_to_user(self, assignment_data: MemberBadgeCreate) -> MemberBadge:
        self.community_service.get_member(assignment_data.member_id)
        self.get_badge(assignment_data.badge_id)

        existing_assignment = self.member_badge_repo.get_by_member_badge(
            member_id=assignment_data.member_id,
            badge_id=assignment_data.badge_id,
        )
        if existing_assignment:
            raise MemberAlreadyHasBadgeError(
                f"Member '{assignment_data.member_id}' already has badge '{assignment_data.badge_id}'."
            )

        try:
            user_badge = MemberBadge(**assignment_data.model_dump())
            saved_assignment = self.member_badge_repo.save(user_badge)
            return saved_assignment
        except Exception as e:
            raise UnexpectedBadgeError(
                f'Unexpected error assigning badge: {str(e)}'
            ) from e

    def revoke_badge_from_user(self, member_id: UUID, badge_id: UUID) -> bool:
        assignment = self.member_badge_repo.get_by_member_badge(
            member_id=member_id, badge_id=badge_id
        )
        if not assignment:
            raise MemberBadgeNotFoundError(
                f"Member '{member_id}' does not have badge '{badge_id}' to revoke."
            )
        try:
            return self.member_badge_repo.delete(assignment)
        except Exception as e:
            raise UnexpectedBadgeError(
                f'Unexpected error revoking badge: {str(e)}'
            ) from e

    def list_badges_for_member(self, member_id: UUID) -> list[Badge]:
        self.community_service.get_member(member_id)

        session = self.badge_repo.session

        badges = (
            session.query(Badge)
            .join(MemberBadge, Badge.id == MemberBadge.badge_id)
            .filter(MemberBadge.member_id == member_id)
            .all()
        )
        return badges
