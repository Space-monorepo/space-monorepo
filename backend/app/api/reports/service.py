from uuid import UUID

from app.api.comment.service import CommentService
from app.api.communities.service import CommunityService
from app.api.post.service import PostService
from app.api.reports.exceptions import (
    ReportCommentAlreadyExistsError,
    ReportMemberAlreadyExistsError,
    ReportNotFoundError,
    ReportPostAlreadyExistsError,
    UnexpectedReportError,
)
from app.api.reports.model import (
    Report,
    ReportComment,
    ReportMember,
    ReportPost,
)
from app.api.reports.schema import (
    Author,
    CommentBriefReport,
    MemberBriefReport,
    PostBriefReport,
    ReportCommentCreate,
    ReportCreate,
    ReportMemberCreate,
    ReportPostCreate,
    ReportResponse,
)
from app.api.users.service import UserService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams


class ReportService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.report_repo = tm.get_report_repository()
        self.report_member_repo = tm.get_report_member_repository()
        self.report_post_repo = tm.get_report_post_repository()
        self.report_comment_repo = tm.get_report_comment_repository()
        self.moderation_votes_repo = tm.get_moderation_votes_repository()
        self.community_service = CommunityService(tm)
        self.user_service = UserService(tm)
        self.post_service = PostService(tm)
        self.comment_service = CommentService(tm)

    def _get_report(self, report_id: UUID) -> Report:
        report = self.report_repo.get_by_id(str(report_id))
        if not report:
            raise ReportNotFoundError('Report not found')
        return report

    def get_report(self, report_id: UUID) -> ReportResponse:
        report = self._get_report(report_id)
        member = self.community_service.get_member(report.reporter_id)
        user = self.user_service.get_user(member.user_id)
        return ReportResponse(
            id=str(report.id),
            reporter=Author(
                id=str(member.id),
                name=user.name,
                profile_picture=user.profile_image_url,
                role=member.role,
            ),
            type=report.type,
            reason=report.reason,
            description=report.description,
            created_at=report.created_at,
        )

    def create_report(self, report: ReportCreate) -> ReportResponse:
        try:
            report = Report(**report.model_dump())
            report = self.report_repo.save(report)
            member = self.community_service.get_member(report.reporter_id)
            user = self.user_service.get_user(member.user_id)
            return ReportResponse(
                id=str(report.id),
                reporter=Author(
                    id=str(member.id),
                    name=user.name,
                    profile_picture=user.profile_image_url,
                    role=member.role,
                ),
                type=report.type,
                reason=report.reason,
                description=report.description,
                created_at=report.created_at,
            )
        except Exception as e:
            raise UnexpectedReportError('Unexpected error creating report') from e

    def delete_report(self, report_id: UUID) -> bool:
        try:
            report = self._get_report(report_id)
            return self.report_repo.delete(report)
        except Exception as e:
            raise UnexpectedReportError('Unexpected error deleting report') from e

    def list_member_reports(
        self, member_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[ReportResponse]:
        reports_members, total = self.report_member_repo.list_reports_by_member(
            member_id, params
        )
        reports = [
            self.get_report(report_member.report_id) for report_member in reports_members
        ]

        return PaginationResponse(
            items=reports,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_member_brief_reports(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[MemberBriefReport]:
        report_members = self.report_member_repo.list_members_by_reason_and_count(
            community_id
        )
        total = len(report_members)

        offset = params.offset or 0
        limit = params.limit or 10
        paginated_report_members = report_members[offset : offset + limit]

        brief_reports = []
        for member_id, reason, reports_count in paginated_report_members:
            member = self.community_service.get_member(member_id)
            user = self.user_service.get_user(member.user_id)
            brief_reports.append(
                MemberBriefReport(
                    member=Author(
                        id=str(member.id),
                        name=user.name,
                        profile_picture=user.profile_image_url,
                        role=member.role,
                    ),
                    reason=reason,
                    reports_count=reports_count,
                    member_reputation=member.reputation,
                    member_popularity=0.0,  # TODO: Add popularity after
                    member_entry_date=member.entered_in,
                )
            )
        return PaginationResponse(
            items=brief_reports,
            total=total,
            has_more=total > offset + limit,
            current_offset=offset,
            current_limit=limit,
        )

    def _get_report_member(self, report_member_id: UUID) -> ReportMember:
        report_member = self.report_member_repo.get_by_id(report_member_id)
        if not report_member:
            raise ReportNotFoundError('Report member not found')
        return report_member

    def create_report_member(self, report_member: ReportMemberCreate) -> ReportMember:
        try:
            report_base = self._get_report(report_member.report_id)
            report = self.report_member_repo.get_by_reporter_member_reason(
                report_base.reporter_id, report_member.member_id, report_base.reason
            )
            if report:
                raise ReportMemberAlreadyExistsError(
                    'Report already exists for the member with the same reason'
                )

            new_report_member = ReportMember(**report_member.model_dump())
            return self.report_member_repo.save(new_report_member)
        except ReportMemberAlreadyExistsError as e:
            raise e from e
        except Exception as e:
            raise UnexpectedReportError('Unexpected error creating report member') from e

    def delete_report_member(self, report_member_id: UUID) -> bool:
        try:
            self._get_report(report_member_id)
            report = self._get_report_member(report_member_id)
            self.report_member_repo.delete(report)
            self.delete_report(report_member_id)
            return True
        except ReportNotFoundError as e:
            raise e from e
        except Exception as e:
            raise UnexpectedReportError('Unexpected error deleting report member') from e

    def list_post_reports(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[ReportResponse]:
        reports_posts, total = self.report_post_repo.list_reports_by_post(
            post_id, params
        )
        reports = [
            self.get_report(report_post.report_id) for report_post in reports_posts
        ]
        return PaginationResponse(
            items=reports,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_post_brief_reports(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PostBriefReport]:
        report_posts = self.report_post_repo.list_posts_by_reason_and_count(community_id)
        total = len(report_posts)

        offset = params.offset or 0
        limit = params.limit or 10
        paginated_report_posts = report_posts[offset : offset + limit]

        brief_reports = []
        for post_id, reason, reports_count in paginated_report_posts:
            post = self.post_service.get_post(post_id)
            member = self.community_service.get_member_association(
                post.user.id, community_id
            )
            user = self.user_service.get_user(member.user_id)
            brief_reports.append(
                PostBriefReport(
                    post_id=str(post_id),
                    member=Author(
                        id=str(member.id),
                        name=user.name,
                        profile_picture=user.profile_image_url,
                        role=member.role,
                    ),
                    reason=reason,
                    title=post.title,
                    content=post.content,
                    image_url=post.image_url,
                    report_count=reports_count,
                    likes_count=post.likes_count,
                    comments_count=post.comments_count,
                    access_count=1000,  # TODO: Add access count after
                    published_at=post.created_at,
                )
            )
        return PaginationResponse(
            items=brief_reports,
            total=total,
            has_more=total > offset + limit,
            current_offset=offset,
            current_limit=limit,
        )

    def _get_report_post(self, report_post_id: UUID) -> ReportPost:
        report_post = self.report_post_repo.get_by_id(report_post_id)
        if not report_post:
            raise ReportNotFoundError('Report post not found')
        return report_post

    def create_report_post(self, report_post: ReportPostCreate) -> ReportPost:
        try:
            report_base = self._get_report(report_post.report_id)
            report = self.report_post_repo.get_by_reporter_post_reason(
                report_base.reporter_id, report_post.post_id, report_base.reason
            )
            if report:
                raise ReportPostAlreadyExistsError(
                    'Report already exists for the post with the same reason'
                )

            new_report_post = ReportPost(**report_post.model_dump())
            return self.report_post_repo.save(new_report_post)
        except ReportPostAlreadyExistsError as e:
            raise e from e
        except Exception as e:
            raise UnexpectedReportError('Unexpected error creating report post') from e

    def delete_report_post(self, report_post_id: UUID) -> bool:
        try:
            self._get_report(report_post_id)
            report = self._get_report_post(report_post_id)
            self.report_post_repo.delete(report)
            self.delete_report(report_post_id)
            return True
        except ReportNotFoundError as e:
            raise e from e
        except Exception as e:
            raise UnexpectedReportError('Unexpected error deleting report post') from e

    def list_comment_reports(
        self, comment_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[ReportResponse]:
        reports_comments, total = self.report_comment_repo.list_reports_by_comment(
            comment_id, params
        )
        reports = [
            self.get_report(report_comment.report_id)
            for report_comment in reports_comments
        ]
        return PaginationResponse(
            items=reports,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_comment_brief_reports(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommentBriefReport]:
        report_comments = self.report_comment_repo.list_comments_by_reason_and_count(
            community_id
        )
        total = len(report_comments)

        offset = params.offset or 0
        limit = params.limit or 10
        paginated_report_comments = report_comments[offset : offset + limit]

        brief_reports = []
        for comment_id, reason, reports_count in paginated_report_comments:
            comment = self.comment_service.get_comment(comment_id)
            member = self.community_service.get_member_association(
                comment.user.id, community_id
            )
            user = self.user_service.get_user(member.user_id)
            brief_reports.append(
                CommentBriefReport(
                    comment_id=str(comment_id),
                    member=Author(
                        id=str(member.id),
                        name=user.name,
                        profile_picture=user.profile_image_url,
                        role=member.role,
                    ),
                    reason=reason,
                    content=comment.content,
                    report_count=reports_count,
                    likes_count=comment.likes_count,
                    # TODO: Add comments count after
                    access_count=1000,  # TODO: Add access count after
                    published_at=comment.created_at,
                )
            )
        return PaginationResponse(
            items=brief_reports,
            total=total,
            has_more=total > offset + limit,
            current_offset=offset,
            current_limit=limit,
        )

    def _get_report_comment(self, report_comment_id: UUID) -> ReportComment:
        report_comment = self.report_comment_repo.get_by_id(report_comment_id)
        if not report_comment:
            raise ReportNotFoundError('Report comment not found')
        return report_comment

    def create_report_comment(
        self, report_comment: ReportCommentCreate
    ) -> ReportComment:
        try:
            report_base = self._get_report(report_comment.report_id)
            report = self.report_comment_repo.get_by_reporter_comment_reason(
                report_base.reporter_id, report_comment.comment_id, report_base.reason
            )
            if report:
                raise ReportCommentAlreadyExistsError(
                    'Report already exists for the comment with the same reason'
                )

            new_report_comment = ReportComment(**report_comment.model_dump())
            return self.report_comment_repo.save(new_report_comment)
        except ReportCommentAlreadyExistsError as e:
            raise e from e
        except Exception as e:
            raise UnexpectedReportError(
                'Unexpected error creating report comment'
            ) from e

    def delete_report_comment(self, report_comment_id: UUID) -> bool:
        try:
            self._get_report(report_comment_id)
            report = self._get_report_comment(report_comment_id)
            self.report_comment_repo.delete(report)
            self.delete_report(report_comment_id)
            return True
        except ReportNotFoundError as e:
            raise e from e
        except Exception as e:
            raise UnexpectedReportError(
                'Unexpected error deleting report comment'
            ) from e
