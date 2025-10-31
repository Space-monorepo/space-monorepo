from uuid import UUID

from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.api.reputation.schema import (
    POPULARITY_POINTS,
    REPUTATION_POINTS,
    PopularityActionEnum,
    ReputationActionEnum,
    ReputationLevelEnum,
)
from app.core.transaction import TransactionManager


class ReputationService:
    MIN_REPUTATION = 0

    LEVEL_THRESHOLDS = {
        ReputationLevelEnum.UNDER_OBSERVATION: 0,
        ReputationLevelEnum.HELPER: 3000,
        ReputationLevelEnum.CONTRIBUTOR: 6000,
        ReputationLevelEnum.LEADER: 8500,
    }

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.member_repo = tm.get_member_repository()

    def _calculate_level(self, reputation_points: int) -> str:
        if reputation_points >= self.LEVEL_THRESHOLDS[ReputationLevelEnum.LEADER]:
            return ReputationLevelEnum.LEADER.value
        elif reputation_points >= self.LEVEL_THRESHOLDS[ReputationLevelEnum.CONTRIBUTOR]:
            return ReputationLevelEnum.CONTRIBUTOR.value
        elif reputation_points >= self.LEVEL_THRESHOLDS[ReputationLevelEnum.HELPER]:
            return ReputationLevelEnum.HELPER.value
        else:
            return ReputationLevelEnum.UNDER_OBSERVATION.value

    def add_reputation_points(
        self, member_id: UUID, action: ReputationActionEnum
    ) -> None:
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise CommunityMemberNotFoundError(f'Member with ID {member_id} not found')

        points = REPUTATION_POINTS.get(action, 0)

        member.reputation += points
        member.reputation = max(self.MIN_REPUTATION, member.reputation)

        try:
            member.reputation_level = self._calculate_level(member.reputation)
            self.member_repo.save(member)
        except Exception as e:
            raise Exception(
                f'Error calculating reputation level for member {member_id}: {e}'
            ) from e

    def add_popularity_points(
        self, member_id: UUID, action: PopularityActionEnum
    ) -> None:
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise CommunityMemberNotFoundError(f'Member with ID {member_id} not found')

        points = POPULARITY_POINTS.get(action, 0)

        member.popularity += points
        member.popularity = max(self.MIN_REPUTATION, member.popularity)

        try:
            self.member_repo.save(member)
        except Exception as e:
            raise Exception(f'Error saving member {member_id}: {e}') from e
