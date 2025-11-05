from uuid import UUID

from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.api.post.schemas import ComplaintLevelEnum
from app.api.reports.model import ReportComment, ReportMember, ReportPost
from app.api.reports.schema import VoteTypeEnum
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

    def award_campaign_creation(self, author_id: UUID) -> None:
        self.add_reputation_points(author_id, ReputationActionEnum.CREATE_CAMPAIGN)

    def award_campaign_status_change(
        self, author_id: UUID, old_status: str, new_status: str
    ) -> None:
        if old_status != 'approved' and new_status == 'approved':
            self.add_reputation_points(author_id, ReputationActionEnum.CAMPAIGN_ACCEPTED)
        elif old_status != 'rejected' and new_status == 'rejected':
            self.add_reputation_points(author_id, ReputationActionEnum.CAMPAIGN_REJECTED)

    def award_campaign_support(self, supporter_id: UUID) -> None:
        self.add_reputation_points(supporter_id, ReputationActionEnum.CAMPAIGN_SUPPORT)

    def award_post_creation(self, author_id: UUID) -> None:
        self.add_popularity_points(author_id, PopularityActionEnum.CREATE_POST)

    def award_post_like(self, liker_id: UUID, post_author_id: UUID) -> None:
        self.add_popularity_points(liker_id, PopularityActionEnum.LIKE)
        self.add_popularity_points(post_author_id, PopularityActionEnum.RECEIVE_LIKE)

    def award_comment_creation(self, commenter_id: UUID, post_author_id: UUID) -> None:
        self.add_popularity_points(commenter_id, PopularityActionEnum.COMMENT_POST)
        self.add_popularity_points(post_author_id, PopularityActionEnum.RECEIVE_COMMENT)

    def award_comment_like(self, liker_id: UUID, comment_author_id: UUID) -> None:
        self.add_popularity_points(liker_id, PopularityActionEnum.LIKE)
        self.add_popularity_points(comment_author_id, PopularityActionEnum.RECEIVE_LIKE)

    def __apply_points_to_all_reporters(
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
                self.add_reputation_points(reporter_id, reputation_action)
                self.add_popularity_points(reporter_id, popularity_action)

    def handle_post_report_suspended(self, post_id: UUID, author_post_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_posts, _ = self.report_post_repo.list_reports_by_post(
            post_id, all_params
        )
        self.__apply_points_to_all_reporters(all_report_posts, VoteTypeEnum.SUSPEND)
        self.add_reputation_points(
            author_post_id, ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )
        self.add_popularity_points(
            author_post_id, PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )

    def handle_post_report_tolerated(self, post_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_posts, _ = self.report_post_repo.list_reports_by_post(
            post_id, all_params
        )
        self.__apply_points_to_all_reporters(all_report_posts, VoteTypeEnum.TOLERATE)

    def handle_member_report_suspended(self, member_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_members, _ = self.report_member_repo.list_reports_by_member(
            member_id, all_params
        )
        self.__apply_points_to_all_reporters(all_report_members, VoteTypeEnum.SUSPEND)
        self.add_reputation_points(
            member_id, ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )
        self.add_popularity_points(
            member_id, PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )

    def handle_member_report_tolerated(self, member_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_members, _ = self.report_member_repo.list_reports_by_member(
            member_id, all_params
        )
        self.__apply_points_to_all_reporters(all_report_members, VoteTypeEnum.TOLERATE)

    def handle_comment_report_suspended(
        self, comment_id: UUID, author_comment_id: UUID
    ) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_comments, _ = self.report_comment_repo.list_reports_by_comment(
            comment_id, all_params
        )
        self.__apply_points_to_all_reporters(all_report_comments, VoteTypeEnum.SUSPEND)
        self.add_reputation_points(
            author_comment_id, ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )
        self.add_popularity_points(
            author_comment_id, PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER
        )

    def handle_comment_report_tolerated(self, comment_id: UUID) -> None:
        all_params = PaginationSearchParams(limit=9999, offset=0)
        all_report_comments, _ = self.report_comment_repo.list_reports_by_comment(
            comment_id, all_params
        )
        self.__apply_points_to_all_reporters(all_report_comments, VoteTypeEnum.TOLERATE)

    def award_complaint_creation(self, author_id: UUID) -> None:
        self.add_reputation_points(author_id, ReputationActionEnum.CREATE_COMPLAINT)
        self.add_popularity_points(author_id, PopularityActionEnum.CREATE_COMPLAINT)

    def award_complaint_confirmation(
        self, confirmer_id: UUID, complaint_level: str
    ) -> None:
        if complaint_level == ComplaintLevelEnum.LOW.value:
            self.add_reputation_points(
                confirmer_id, ReputationActionEnum.CONFIRM_COMPLAINT_LOW
            )
        elif complaint_level == ComplaintLevelEnum.MEDIUM.value:
            self.add_reputation_points(
                confirmer_id, ReputationActionEnum.CONFIRM_COMPLAINT_MEDIUM
            )
        elif complaint_level == ComplaintLevelEnum.HIGH.value:
            self.add_reputation_points(
                confirmer_id, ReputationActionEnum.CONFIRM_COMPLAINT_HIGH
            )

    def award_complaint_resolution(self, author_id: UUID, complaint_level: str) -> None:
        if complaint_level == ComplaintLevelEnum.LOW.value:
            self.add_reputation_points(
                author_id, ReputationActionEnum.COMPLAINT_RESOLVED_LOW
            )
            self.add_popularity_points(
                author_id, PopularityActionEnum.COMPLAINT_RESOLVED_LOW
            )
        elif complaint_level == ComplaintLevelEnum.MEDIUM.value:
            self.add_reputation_points(
                author_id, ReputationActionEnum.COMPLAINT_RESOLVED_MEDIUM
            )
            self.add_popularity_points(
                author_id, PopularityActionEnum.COMPLAINT_RESOLVED_MEDIUM
            )
        elif complaint_level == ComplaintLevelEnum.HIGH.value:
            self.add_reputation_points(
                author_id, ReputationActionEnum.COMPLAINT_RESOLVED_HIGH
            )
            self.add_popularity_points(
                author_id, PopularityActionEnum.COMPLAINT_RESOLVED_HIGH
            )

    def award_complaint_resolution_by_moderator(self, moderator_id: UUID) -> None:
        self.add_reputation_points(
            moderator_id, ReputationActionEnum.RESOLVE_COMPLAINT_MODERATOR
        )
