from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.reports.model import (
    ModerationVotes,
    Report,
    ReportComment,
    ReportMember,
    ReportPost,
)
from app.core.repository import BaseRepository
from app.utils.schema import PaginationSearchParams


class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: Session):
        super().__init__(Report, session)
        self.session = session

    def list_reports_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[Report], int]:
        query = self.session.query(Report)
        query = query.filter(Report.community_id == community_id)
        if params.type_report:
            query = query.filter(Report.type == params.type_report)

        total = query.count()
        reports = query.offset(params.offset).limit(params.limit).all()
        return reports, total


class ReportMemberRepository(BaseRepository[ReportMember]):
    def __init__(self, session: Session):
        super().__init__(ReportMember, session)
        self.session = session

    def save(self, model: ReportMember) -> ReportMember:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {ReportMember.__qualname__} with id {model.report_id} saved successfully'
        )
        return model

    def delete(self, model: ReportMember) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {ReportMember.__qualname__} with id {model.report_id} deleted successfully'
        )
        return True

    def get_by_reporter_member_reason(
        self, reporter_id: UUID, member_id: UUID, reason: str
    ) -> ReportMember | None:
        report_base = (
            self.session.query(Report)
            .filter(
                Report.reporter_id == reporter_id,
                Report.reason == reason,
                Report.type == 'member_report',
            )
            .first()
        )
        if not report_base:
            return None
        report_member = (
            self.session.query(ReportMember)
            .filter(
                ReportMember.report_id == report_base.id,
                ReportMember.member_id == member_id,
            )
            .first()
        )
        if report_member:
            return report_member
        return None

    def list_reports_by_member(
        self, member_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[ReportMember], int]:
        query = self.session.query(ReportMember).filter(
            ReportMember.member_id == member_id
        )
        total = query.count()
        reports = query.offset(params.offset).limit(params.limit).all()
        return reports, total

    def list_member_ids_by_community(self, community_id: UUID) -> list[UUID]:
        member_ids = (
            select(ReportMember.member_id)
            .where(ReportMember.community_id == community_id)
            .distinct()
        )
        return list(self.session.scalars(member_ids).all())

    def count_reports_by_member(self, member_id: UUID) -> int:
        return (
            self.session.query(ReportMember)
            .filter(ReportMember.member_id == member_id)
            .count()
        )

    def list_reasons_by_member(self, member_id: UUID) -> list[str]:
        reasons = (
            select(Report.reason)
            .join(ReportMember, Report.id == ReportMember.report_id)
            .where(ReportMember.member_id == member_id)
            .distinct()
            .order_by(Report.reason.asc())
        )
        return list(self.session.scalars(reasons).all())


class ReportPostRepository(BaseRepository[ReportPost]):
    def __init__(self, session: Session):
        super().__init__(ReportPost, session)
        self.session = session

    def save(self, model: ReportPost) -> ReportPost:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {ReportPost.__qualname__} with id {model.report_id} saved successfully'
        )
        return model

    def delete(self, model: ReportPost) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {ReportPost.__qualname__} with id {model.report_id} deleted successfully'
        )
        return True

    def get_by_reporter_post_reason(
        self, reporter_id: UUID, post_id: UUID, reason: str
    ) -> ReportPost | None:
        report_base = (
            self.session.query(Report)
            .filter(
                Report.reporter_id == reporter_id,
                Report.reason == reason,
                Report.type == 'post_report',
            )
            .first()
        )
        if not report_base:
            return None
        report_post = (
            self.session.query(ReportPost)
            .filter(
                ReportPost.report_id == report_base.id, ReportPost.post_id == post_id
            )
            .first()
        )
        if report_post:
            return report_post
        return None

    def list_reports_by_post(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[ReportPost], int]:
        query = self.session.query(ReportPost).filter(ReportPost.post_id == post_id)
        total = query.count()
        reports = query.offset(params.offset).limit(params.limit).all()
        return reports, total

    def list_post_ids_by_community(self, community_id: UUID) -> list[UUID]:
        post_ids = (
            select(ReportPost.post_id)
            .where(ReportPost.community_id == community_id)
            .distinct()
        )
        return list(self.session.scalars(post_ids).all())

    def list_reasons_by_post(self, post_id: UUID) -> list[str]:
        reasons = (
            select(Report.reason)
            .join(ReportPost, Report.id == ReportPost.report_id)
            .where(ReportPost.post_id == post_id)
            .distinct()
            .order_by(Report.reason.asc())
        )
        return list(self.session.scalars(reasons).all())


class ReportCommentRepository(BaseRepository[ReportComment]):
    def __init__(self, session: Session):
        super().__init__(ReportComment, session)
        self.session = session

    def save(self, model: ReportComment) -> ReportComment:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {ReportComment.__qualname__} with id {model.report_id} saved successfully'
        )
        return model

    def delete(self, model: ReportComment) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {ReportComment.__qualname__} with id {model.report_id} deleted successfully'
        )
        return True

    def get_by_reporter_comment_reason(
        self, reporter_id: UUID, comment_id: UUID, reason: str
    ) -> ReportComment | None:
        report_base = (
            self.session.query(Report)
            .filter(
                Report.reporter_id == reporter_id,
                Report.reason == reason,
                Report.type == 'comment_report',
            )
            .first()
        )
        if not report_base:
            return None
        report_comment = (
            self.session.query(ReportComment)
            .filter(
                ReportComment.report_id == report_base.id,
                ReportComment.comment_id == comment_id,
            )
            .first()
        )
        if report_comment:
            return report_comment
        return None

    def list_reports_by_comment(
        self, comment_id: UUID, params: PaginationSearchParams
    ) -> tuple[list[ReportComment], int]:
        query = self.session.query(ReportComment).filter(
            ReportComment.comment_id == comment_id
        )
        total = query.count()
        reports = query.offset(params.offset).limit(params.limit).all()
        return reports, total

    def list_comment_ids_by_community(self, community_id: UUID) -> list[UUID]:
        comment_ids = (
            select(ReportComment.comment_id)
            .where(ReportComment.community_id == community_id)
            .distinct()
        )
        return list(self.session.scalars(comment_ids).all())

    def list_reasons_by_comment(self, comment_id: UUID) -> list[str]:
        reasons = (
            select(Report.reason)
            .join(ReportComment, Report.id == ReportComment.report_id)
            .where(ReportComment.comment_id == comment_id)
            .distinct()
            .order_by(Report.reason.asc())
        )
        return list(self.session.scalars(reasons).all())


class ModerationVotesRepository(BaseRepository[ModerationVotes]):
    def __init__(self, session: Session):
        super().__init__(ModerationVotes, session)
        self.session = session
