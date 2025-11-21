from uuid import UUID

from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.api.communities.service import CommunityService
from app.api.post.model import Post
from app.api.reports.model import ReportComment, ReportMember, ReportPost
from app.api.reports.schema import VoteTypeEnum
from app.api.reputation.exceptions import (
    PopularityUpdateError,
    ReputationUpdateError,
)
from app.api.reputation.schema import (
    POPULARITY_POINTS,
    REPUTATION_POINTS,
    PopularityActionEnum,
    ReputationActionEnum,
    ReputationLevelEnum,
)
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationSearchParams


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
        self.report_post_repo = tm.get_report_post_repository()
        self.report_member_repo = tm.get_report_member_repository()
        self.report_comment_repo = tm.get_report_comment_repository()
        self.report_repo = tm.get_report_repository()
        self.community_service = CommunityService(tm)

    def _calculate_level(self, reputation_points: int) -> str:
        if reputation_points >= self.LEVEL_THRESHOLDS[ReputationLevelEnum.LEADER]:
            return ReputationLevelEnum.LEADER.value
        elif reputation_points >= self.LEVEL_THRESHOLDS[ReputationLevelEnum.CONTRIBUTOR]:
            return ReputationLevelEnum.CONTRIBUTOR.value
        elif reputation_points >= self.LEVEL_THRESHOLDS[ReputationLevelEnum.HELPER]:
            return ReputationLevelEnum.HELPER.value
        else:
            return ReputationLevelEnum.UNDER_OBSERVATION.value

    def _add_reputation_points(
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
            raise ReputationUpdateError(
                f'Error updating reputation for member {member_id}: {e}'
            ) from e

    def _add_popularity_points(
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
            raise PopularityUpdateError(
                f'Error updating popularity for member {member_id}: {e}'
            ) from e

    def get_member_stats(self, member_id: UUID) -> dict:
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise CommunityMemberNotFoundError(f'Member with ID {member_id} not found')
        return {
            'reputation': member.reputation,
            'reputation_level': member.reputation_level,
            'popularity': member.popularity,
        }

    def reward_campaign_creation_to_member(self, author_id: UUID) -> None:
        self._add_reputation_points(author_id, ReputationActionEnum.CREATE_CAMPAIGN)

    def reward_campaign_status_change_to_member(
        self, author_id: UUID, old_status: str, new_status: str
    ) -> None:
        if old_status != 'approved' and new_status == 'approved':
            self._add_reputation_points(
                author_id, ReputationActionEnum.CAMPAIGN_ACCEPTED
            )
        elif old_status != 'rejected' and new_status == 'rejected':
            self._add_reputation_points(
                author_id, ReputationActionEnum.CAMPAIGN_REJECTED
            )

    def reward_campaign_support_to_member(self, supporter_id: UUID) -> None:
        self._add_reputation_points(supporter_id, ReputationActionEnum.CAMPAIGN_SUPPORT)

    def reward_post_creation_to_member(self, author_id: UUID) -> None:
        self._add_popularity_points(author_id, PopularityActionEnum.CREATE_POST)

    def reward_post_like_to_member(self, liker_id: UUID, post_author_id: UUID) -> None:
        self._add_popularity_points(liker_id, PopularityActionEnum.LIKE)
        self._add_popularity_points(post_author_id, PopularityActionEnum.RECEIVE_LIKE)

    def reward_comment_creation_to_member(
        self, commenter_id: UUID, post_author_id: UUID
    ) -> None:
        self._add_popularity_points(commenter_id, PopularityActionEnum.COMMENT_POST)
        self._add_popularity_points(post_author_id, PopularityActionEnum.RECEIVE_COMMENT)

    def reward_comment_like_to_member(
        self, liker_id: UUID, comment_author_id: UUID
    ) -> None:
        self._add_popularity_points(liker_id, PopularityActionEnum.LIKE)
        self._add_popularity_points(comment_author_id, PopularityActionEnum.RECEIVE_LIKE)

    def _apply_points_to_all_reporters(
        self,
        report_list: list[ReportPost | ReportMember | ReportComment],
        action: VoteTypeEnum,
    ) -> None:
        reputation_action = (
            ReputationActionEnum.REPORT_SUSPENDED
            if action == VoteTypeEnum.SUSPEND
            else ReputationActionEnum.REPORT_TOLERATED
        )
        popularity_action = (
            PopularityActionEnum.REPORT_SUSPENDED
            if action == VoteTypeEnum.SUSPEND
            else PopularityActionEnum.REPORT_TOLERATED
        )
        for report_item in report_list:
            report = self.report_repo.get_by_id(report_item.report_id)
            if report:
                reporter_id = report.reporter_id
                self._add_reputation_points(reporter_id, reputation_action)
                self._add_popularity_points(reporter_id, popularity_action)

    def handle_post_report_suspended(self, post_id: UUID, author_post_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_posts, _ = self.report_post_repo.list_reports_by_post(
            post_id, all_params
        )
        self._apply_points_to_all_reporters(all_report_posts, VoteTypeEnum.SUSPEND)
        self._add_reputation_points(
            author_post_id, ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )
        self._add_popularity_points(
            author_post_id, PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )

    def handle_post_report_tolerated(self, post_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_posts, _ = self.report_post_repo.list_reports_by_post(
            post_id, all_params
        )
        self._apply_points_to_all_reporters(all_report_posts, VoteTypeEnum.TOLERATE)

    def handle_member_report_suspended(self, member_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_members, _ = self.report_member_repo.list_reports_by_member(
            member_id, all_params
        )
        self._apply_points_to_all_reporters(all_report_members, VoteTypeEnum.SUSPEND)
        self._add_reputation_points(
            member_id, ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )
        self._add_popularity_points(
            member_id, PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )

    def handle_member_report_tolerated(self, member_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_members, _ = self.report_member_repo.list_reports_by_member(
            member_id, all_params
        )
        self._apply_points_to_all_reporters(all_report_members, VoteTypeEnum.TOLERATE)

    def handle_comment_report_suspended(
        self, comment_id: UUID, author_comment_id: UUID
    ) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_comments, _ = self.report_comment_repo.list_reports_by_comment(
            comment_id, all_params
        )
        self._apply_points_to_all_reporters(all_report_comments, VoteTypeEnum.SUSPEND)
        self._add_reputation_points(
            author_comment_id, ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )
        self._add_popularity_points(
            author_comment_id, PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )

    def handle_comment_report_tolerated(self, comment_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_comments, _ = self.report_comment_repo.list_reports_by_comment(
            comment_id, all_params
        )
        self._apply_points_to_all_reporters(all_report_comments, VoteTypeEnum.TOLERATE)

    def reward_complaint_creation_to_member(self, author_id: UUID) -> None:
        self._add_reputation_points(author_id, ReputationActionEnum.CREATE_COMPLAINT)
        self._add_popularity_points(author_id, PopularityActionEnum.CREATE_COMPLAINT)

    def reward_complaint_confirmation_to_member(self, member_id: UUID) -> None:
        self._add_reputation_points(member_id, ReputationActionEnum.CONFIRM_COMPLAINT)

    def reward_complaint_resolution_to_member(self, post: Post) -> None:
        try:
            author_member = self.community_service.get_member_association(
                post.user.id, post.community.id
            )
        except Exception as e:
            raise CommunityMemberNotFoundError(
                'Unexpected error updating reputation'
            ) from e
        try:
            self._add_reputation_points(
                author_member.id, ReputationActionEnum.COMPLAINT_RESOLVED
            )
        except Exception as e:
            raise ReputationUpdateError('Unexpected error updating reputation') from e
        try:
            self._add_popularity_points(
                author_member.id, PopularityActionEnum.COMPLAINT_RESOLVED
            )
        except Exception as e:
            raise PopularityUpdateError('Unexpected error updating popularity') from e

    def reward_complaint_resolution_to_moderator(self, moderator_id: UUID) -> None:
        try:
            self._add_reputation_points(
                moderator_id, ReputationActionEnum.RESOLVE_COMPLAINT_MODERATOR
            )
        except Exception as e:
            raise ReputationUpdateError('Unexpected error updating reputation') from e
