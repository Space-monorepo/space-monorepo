from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.reports.model import (
    ModerationVotes,
    Report,
    ReportComment,
    ReportMember,
    ReportPost,
)
from app.api.reports.schema import ReportReasonEnum, VoteTypeEnum
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

    def get_by_id(self, id: UUID) -> ReportMember:
        report_member = (
            self.session.query(ReportMember).filter(ReportMember.report_id == id).first()
        )
        if report_member:
            self.logger.debug(
                f'Model {ReportMember.__qualname__} with id {id} retrieved successfully'
            )
            return report_member
        else:
            self.logger.warning(
                f'Model {ReportMember.__qualname__} with id {id} not found'
            )
            return None

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
        # Subquery que conta reportes por member_id e reason
        subq = (
            select(
                ReportMember.member_id,
                Report.reason,
                func.count(ReportMember.report_id).label('count'),
            )
            .join(Report, ReportMember.report_id == Report.id)
            .where(ReportMember.community_id == community_id)
            .group_by(ReportMember.member_id, Report.reason)
            .subquery()
        )

        # Query principal que ordena pelo máximo de reportes por razão
        member_ids = (
            select(subq.c.member_id)
            .group_by(subq.c.member_id)
            .order_by(func.max(subq.c.count).desc())
        )
        return list(self.session.scalars(member_ids).all())

    def list_members_by_reason_and_count(
        self, community_id: UUID
    ) -> list[tuple[UUID, ReportReasonEnum, int]]:
        """
        Retorna lista de tuplas (member_id, reason, count) ordenadas pela contagem
        de reportes de forma decrescente.
        """
        query = (
            select(
                ReportMember.member_id,
                Report.reason,
                func.count(ReportMember.report_id).label('count'),
            )
            .join(Report, ReportMember.report_id == Report.id)
            .where(ReportMember.community_id == community_id)
            .group_by(ReportMember.member_id, Report.reason)
            .order_by(func.count(ReportMember.report_id).desc())
        )
        results = self.session.execute(query).all()
        return [(row[0], ReportReasonEnum(row[1]), row[2]) for row in results]


class ReportPostRepository(BaseRepository[ReportPost]):
    def __init__(self, session: Session):
        super().__init__(ReportPost, session)
        self.session = session

    def get_by_id(self, id: UUID) -> ReportPost:
        report_post = (
            self.session.query(ReportPost).filter(ReportPost.report_id == id).first()
        )
        if report_post:
            self.logger.debug(
                f'Model {ReportPost.__qualname__} with id {id} retrieved successfully'
            )
            return report_post
        else:
            self.logger.warning(
                f'Model {ReportPost.__qualname__} with id {id} not found'
            )
            return None

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

    def list_posts_by_reason_and_count(
        self, community_id: UUID
    ) -> list[tuple[UUID, ReportReasonEnum, int]]:
        """
        Retorna lista de tuplas (post_id, reason, count) ordenadas pela contagem
        de reportes de forma decrescente.
        """
        query = (
            select(
                ReportPost.post_id,
                Report.reason,
                func.count(ReportPost.report_id).label('count'),
            )
            .join(Report, ReportPost.report_id == Report.id)
            .where(ReportPost.community_id == community_id)
            .group_by(ReportPost.post_id, Report.reason)
            .order_by(func.count(ReportPost.report_id).desc())
        )
        results = self.session.execute(query).all()
        return [(row[0], ReportReasonEnum(row[1]), row[2]) for row in results]


class ReportCommentRepository(BaseRepository[ReportComment]):
    def __init__(self, session: Session):
        super().__init__(ReportComment, session)
        self.session = session

    def get_by_id(self, id: UUID) -> ReportComment:
        report_comment = (
            self.session.query(ReportComment)
            .filter(ReportComment.report_id == id)
            .first()
        )
        if report_comment:
            self.logger.debug(
                f'Model {ReportComment.__qualname__} with id {id} retrieved successfully'
            )
            return report_comment
        else:
            self.logger.warning(
                f'Model {ReportComment.__qualname__} with id {id} not found'
            )
            return None

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

    def list_comments_by_reason_and_count(
        self, community_id: UUID
    ) -> list[tuple[UUID, ReportReasonEnum, int]]:
        """
        Retorna lista de tuplas (comment_id, reason, count) ordenadas pela contagem
        de reportes de forma decrescente.
        """
        query = (
            select(
                ReportComment.comment_id,
                Report.reason,
                func.count(ReportComment.report_id).label('count'),
            )
            .join(Report, ReportComment.report_id == Report.id)
            .where(ReportComment.community_id == community_id)
            .group_by(ReportComment.comment_id, Report.reason)
            .order_by(func.count(ReportComment.report_id).desc())
        )
        results = self.session.execute(query).all()
        return [(row[0], ReportReasonEnum(row[1]), row[2]) for row in results]


class ModerationVotesRepository(BaseRepository[ModerationVotes]):
    def __init__(self, session: Session):
        super().__init__(ModerationVotes, session)
        self.session = session

    def report_has_suspension_vote(self, report_id: UUID) -> bool:
        query = self.session.query(ModerationVotes).filter(
            ModerationVotes.report_id == report_id,
            ModerationVotes.vote == VoteTypeEnum.SUSPEND,
        )
        return query.count() > 0

    def report_has_tolerance_vote(self, report_id: UUID) -> bool:
        query = self.session.query(ModerationVotes).filter(
            ModerationVotes.report_id == report_id,
            ModerationVotes.vote == VoteTypeEnum.TOLERATE,
        )
        return query.count() > 0

    def count_votes_by_type(self, report_id: UUID, vote_type: VoteTypeEnum) -> int:
        """Conta quantos votos de um tipo específico existem para um report."""
        count = (
            self.session.query(ModerationVotes)
            .filter(
                ModerationVotes.report_id == report_id, ModerationVotes.vote == vote_type
            )
            .count()
        )
        self.logger.debug(
            f'Count {count} votes of type {vote_type} for report {report_id}'
        )
        return count

    def moderator_has_voted(self, report_id: UUID, moderator_id: UUID) -> bool:
        """Verifica se um moderador já votou em um report específico."""
        vote = (
            self.session.query(ModerationVotes)
            .filter(
                ModerationVotes.report_id == report_id,
                ModerationVotes.moderator_id == moderator_id,
            )
            .first()
        )
        has_voted = vote is not None
        self.logger.debug(
            f'Moderator {moderator_id} has{"" if has_voted else " not"} voted on report {report_id}'
        )
        return has_voted

    def delete_votes_by_report(self, report_id: UUID) -> bool:
        """Deleta todos os votos associados a um report."""
        votes = (
            self.session.query(ModerationVotes)
            .filter(ModerationVotes.report_id == report_id)
            .all()
        )
        for vote in votes:
            self.session.delete(vote)
        self.session.flush()
        self.logger.debug(f'Deleted {len(votes)} votes for report {report_id}')
        return True

    def get_vote_counts(self, report_id: UUID) -> tuple[int, int]:
        """Retorna a contagem de votos (suspend_count, tolerate_count)."""
        suspend_count = self.count_votes_by_type(report_id, VoteTypeEnum.SUSPEND)
        tolerate_count = self.count_votes_by_type(report_id, VoteTypeEnum.TOLERATE)
        self.logger.debug(
            f'Vote counts for report {report_id}: {suspend_count} suspend, {tolerate_count} tolerate'
        )
        return suspend_count, tolerate_count
