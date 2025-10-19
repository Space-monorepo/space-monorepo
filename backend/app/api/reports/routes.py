from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.communities.model import CommunityMember
from app.api.reports.schema import (
    ReportCreate,
    ReportCommentCreate,
    ReportMemberCreate,
    ReportPostCreate,
    ReportMemberResponse,
    ReportPostResponse,
    ReportCommentResponse,
)
from app.api.reports.service import ReportService
from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager

router = APIRouter(prefix='/reports/{community_id}', tags=['reports'])


@router.post(
    '/create-report-member/{member_id}',
    response_model=ReportMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report_member(
    community_id: str,
    member_id: str,
    report: ReportCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> ReportMemberResponse:
    with TransactionManager(session) as tm:
        report_created = ReportService(tm).create_report(report)
        report_member = ReportMemberCreate(
            report_id=report_created.id,
            member_id=member_id,
            community_id=community_id,
        )
        ReportService(tm).create_report_member(report_member)
        return ReportMemberResponse(
            report=report_created,
            member_id=member_id,
            community_id=community_id,
        )


@router.post(
    '/create-report-post/{post_id}',
    response_model=ReportPostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report_post(
    community_id: str,
    post_id: str,
    report: ReportCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> ReportPostResponse:
    with TransactionManager(session) as tm:
        report_created = ReportService(tm).create_report(report)
        report_post = ReportPostCreate(
            report_id=report_created.id,
            post_id=post_id,
            community_id=community_id,
        )
        ReportService(tm).create_report_post(report_post)
        return ReportPostResponse(
            report=report_created,
            post_id=post_id,
            community_id=community_id,
        )


@router.post(
    '/create-report-comment/{comment_id}',
    response_model=ReportCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report_comment(
    community_id: str,
    comment_id: str,
    report: ReportCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> ReportCommentResponse:
    with TransactionManager(session) as tm:
        report_created = ReportService(tm).create_report(report)
        report_comment = ReportCommentCreate(
            report_id=report_created.id,
            comment_id=comment_id,
            community_id=community_id,
        )
        ReportService(tm).create_report_comment(report_comment)
        return ReportCommentResponse(
            report=report_created,
            comment_id=comment_id,
            community_id=community_id,
        )
