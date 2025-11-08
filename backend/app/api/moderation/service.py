from datetime import datetime, timezone
from uuid import UUID

from app.api.comment.service import CommentService
from app.api.communities.schema import CommunityMemberResponse, CommunityMemberStatusEnum
from app.api.communities.service import CommunityService
from app.api.moderation.schema import ModerationActionResponse, PollBriefResponse
from app.api.post.exceptions import ComplaintNotFoundError, UnexpectedPostError
from app.api.post.model import ComplaintPost
from app.api.post.schemas import (
    ComplaintResponse,
    ComplaintStatusEnum,
    PostResponse,
    PostStatusEnum,
    PostTypeEnum,
    PostUpdate,
)
from app.api.post.service import PostService
from app.api.reports.exceptions import ModeratorAlreadyVotedError
from app.api.reports.model import ModerationVotes
from app.api.reports.schema import (
    ModerationVotesCreate,
    ModerationVotesResponse,
    ReportResponse,
    ReportTypeEnum,
    VoteTypeEnum,
)
from app.api.reports.service import ReportService
from app.api.reputation.service import ReputationService
from app.api.users.service import UserService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams


class ModerationService:
    REPORT_VOTES_THRESHOLD = 2

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.moderation_votes_repo = tm.get_moderation_votes_repository()
        self.post_repo = tm.get_post_repository()
        self.complaint_repo = tm.get_complaint_post_repository()
        self.poll_repo = tm.get_poll_posts_repository()
        self.report_service = ReportService(tm)
        self.post_service = PostService(tm)
        self.user_service = UserService(tm)
        self.comment_service = CommentService(tm)
        self.community_service = CommunityService(tm)
        self.reputation_service = ReputationService(tm)

    def moderate_post(
        self, post_id: str, new_status: PostStatusEnum
    ) -> PostResponse | bool:
        post = self.post_service.get_post(post_id)
        if new_status == PostStatusEnum.REJECTED:
            return self.post_service.delete_post(post_id)
        post.status = new_status
        return self.post_service.update_post(post_id, post)

    def moderate_report(
        self, report_id: str, vote: ModerationVotesCreate
    ) -> ModerationVotesResponse | ModerationActionResponse:
        if self.moderation_votes_repo.moderator_has_voted(report_id, vote.moderator_id):
            raise ModeratorAlreadyVotedError(
                f'Moderator {vote.moderator_id} has already voted on report {report_id}'
            )

        moderation_vote = ModerationVotes(**vote.model_dump())
        saved_vote = self.moderation_votes_repo.save(moderation_vote)

        suspend_count, tolerate_count = self.moderation_votes_repo.get_vote_counts(
            report_id
        )
        total_votes = suspend_count + tolerate_count

        if total_votes < self.REPORT_VOTES_THRESHOLD:
            return ModerationVotesResponse(
                id=str(saved_vote.id),
                report_id=str(saved_vote.report_id),
                moderator_id=str(saved_vote.moderator_id),
                vote=saved_vote.vote,
                created_at=saved_vote.created_at,
            )

        action = (
            VoteTypeEnum.SUSPEND
            if suspend_count >= tolerate_count
            else VoteTypeEnum.TOLERATE
        )

        report = self.report_service.get_report(report_id)

        message = self.__take_action(report, action)

        self.moderation_votes_repo.delete_votes_by_report(report_id)
        self.report_service.delete_report(report_id)

        return ModerationActionResponse(
            action=action,
            report_type=report.type,
            message=message,
            executed_at=datetime.now(timezone.utc),
        )

    def __take_action(self, report: ReportResponse, action: VoteTypeEnum) -> str:
        if report.type == ReportTypeEnum.POST_REPORT:
            report_post = self.report_service.report_post_repo.get_by_id(report.id)
            post = self.post_service.get_post(str(report_post.post_id))
            author_post_id = post.user.id
            if action == VoteTypeEnum.SUSPEND:
                self.reputation_service.handle_post_report_suspended(
                    report_post.post_id,
                    author_post_id,
                )
                self.__suspend_post(report_post.post_id)
                message = 'Post suspenso com sucesso'
            else:
                self.reputation_service.handle_post_report_tolerated(report_post.post_id)
                self.__tolerate_post(report_post.post_id)
                message = 'Post tolerado e mantido ativo'

        elif report.type == ReportTypeEnum.MEMBER_REPORT:
            report_member = self.report_service.report_member_repo.get_by_id(report.id)
            reported_member_id = report_member.member_id
            if action == VoteTypeEnum.SUSPEND:
                self.reputation_service.handle_member_report_suspended(
                    reported_member_id
                )
                self.__suspend_member(report_member.member_id)
                message = 'Membro suspenso com sucesso'
            else:
                self.reputation_service.handle_member_report_tolerated(
                    reported_member_id
                )
                message = 'Membro tolerado e mantido ativo'

        elif report.type == ReportTypeEnum.COMMENT_REPORT:
            report_comment = self.report_service.report_comment_repo.get_by_id(report.id)
            comment = self.comment_service.get_comment(str(report_comment.comment_id))
            author_comment_id = comment.user.id
            if action == VoteTypeEnum.SUSPEND:
                self.reputation_service.handle_comment_report_suspended(
                    report_comment.comment_id, author_comment_id
                )
                self.__delete_comment(report_comment.comment_id)
                message = 'Comentário deletado com sucesso'
            else:
                self.reputation_service.handle_comment_report_tolerated(
                    report_comment.comment_id
                )
                message = 'Comentário tolerado e mantido ativo'
        return message

    def __suspend_post(self, post_id: str) -> None:
        post_update = PostUpdate(status=PostStatusEnum.SUSPENDED)
        self.post_service.update_post(post_id, post_update)

    def __tolerate_post(self, post_id: str) -> None:
        post_update = PostUpdate(status=PostStatusEnum.ACTIVE)
        self.post_service.update_post(post_id, post_update)

    def __suspend_member(self, member_id: str) -> None:
        self.community_service.update_member_status(
            member_id, CommunityMemberStatusEnum.SUSPENDED
        )

    def __delete_comment(self, comment_id: str) -> None:
        self.comment_service.delete_comment(comment_id)

    def update_member_status(
        self, member_id: str, new_status: CommunityMemberStatusEnum
    ) -> CommunityMemberResponse:
        return self.community_service.update_member_status(member_id, new_status)

    def get_complaint(self, post_id: UUID) -> ComplaintPost:
        complaint = self.complaint_repo.get_by_id(post_id)
        if not complaint:
            raise ComplaintNotFoundError('Complaint not found')
        return complaint

    def udpate_status_complaint(
        self, post_id: UUID, status: ComplaintStatusEnum, moderator_id: UUID
    ) -> ComplaintResponse:
        try:
            complaint_post = self.get_complaint(post_id)
            complaint_post.status_complaint = status
            complaint_post_saved = self.complaint_repo.save(complaint_post)
            post = self.post_service.get_post(post_id)
            if status == ComplaintStatusEnum.RESOLVED:
                self.reputation_service.award_complaint_resolution(post.user.id)
                self.reputation_service.award_complaint_resolution_by_moderator(
                    moderator_id
                )
            return ComplaintResponse(
                post=post,
                confirmations_count=complaint_post_saved.confirmations_count,
                status_complaint=complaint_post_saved.status_complaint,
                level_complaint=complaint_post_saved.level_complaint,
            )
        except Exception as e:
            raise UnexpectedPostError('Unexpected error updating complaint') from e

    def list_all_complaints_from_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[ComplaintResponse]:
        complaints, total = self.complaint_repo.list_complaints_by_community(
            community_id, params
        )
        complaints_response = [
            ComplaintResponse(
                post=self.post_service.get_post(complaint.post_id),
                confirmations_count=complaint.confirmations_count,
                status_complaint=complaint.status_complaint,
                level_complaint=complaint.level_complaint,
            )
            for complaint in complaints
        ]
        return PaginationResponse(
            items=complaints_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_all_announcements_from_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PostResponse]:
        params.type_post = PostTypeEnum.ANNOUNCEMENT
        return self.post_service.list_posts_by_community(community_id, params)

    def list_all_polls_from_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PollBriefResponse]:
        polls, total = self.poll_repo.list_polls_by_community(community_id, params)
        polls_response = []
        for poll in polls:
            options = self.post_service.list_poll_options(poll.post_id)
            post = self.post_service.get_post(poll.post_id)
            polls_response.append(
                PollBriefResponse(
                    post=post,
                    question=poll.question,
                    options=options,
                    total_votes=sum(option.votes_count for option in options),
                )
            )
        return PaginationResponse(
            items=polls_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def delete_comment(self, comment_id: str) -> bool:
        return self.comment_service.delete_comment(comment_id)
