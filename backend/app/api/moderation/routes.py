from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.communities.model import CommunityMember
from app.api.moderation.schema import ModerationActionResponse, PollBriefResponse
from app.api.moderation.service import ModerationService
from app.api.post.schemas import ComplaintResponse, ComplaintStatusEnum, PostResponse
from app.api.reports.schema import (
    CommentBriefReport,
    MemberBriefReport,
    ModerationVotesCreate,
    ModerationVotesResponse,
    PostBriefReport,
    ReportResponse,
)
from app.api.reports.service import ReportService
from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/moderation/{community_id}', tags=['moderation'])


@router.get(
    '/list-all-member-brief-reports',
    response_model=PaginationResponse[MemberBriefReport],
    status_code=status.HTTP_200_OK,
)
def list_all_member_brief_reports(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[MemberBriefReport]:
    with TransactionManager(session) as tm:
        return ReportService(tm).list_member_brief_reports(community_id, params)


@router.get(
    '/list-all-member-reports/{member_id}',
    response_model=PaginationResponse[ReportResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_member_reports(
    community_id: str,
    member_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[ReportResponse]:
    with TransactionManager(session) as tm:
        return ReportService(tm).list_member_reports(member_id, params)


@router.delete(
    '/report-member/{report_member_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_report_member(
    community_id: str,
    report_member_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> None:
    with TransactionManager(session) as tm:
        ReportService(tm).delete_report_member(report_member_id)


@router.get(
    '/list-all-post-brief-reports',
    response_model=PaginationResponse[PostBriefReport],
    status_code=status.HTTP_200_OK,
)
def list_all_post_brief_reports(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[PostBriefReport]:
    with TransactionManager(session) as tm:
        return ReportService(tm).list_post_brief_reports(community_id, params)


@router.get(
    '/list-all-post-reports/{post_id}',
    response_model=PaginationResponse[ReportResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_post_reports(
    community_id: str,
    post_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[ReportResponse]:
    with TransactionManager(session) as tm:
        return ReportService(tm).list_post_reports(post_id, params)


@router.delete(
    '/report-post/{report_post_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_report_post(
    community_id: str,
    report_post_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> None:
    with TransactionManager(session) as tm:
        ReportService(tm).delete_report_post(report_post_id)


@router.get(
    '/list-all-comment-brief-reports',
    response_model=PaginationResponse[CommentBriefReport],
    status_code=status.HTTP_200_OK,
)
def list_all_comment_brief_reports(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[CommentBriefReport]:
    with TransactionManager(session) as tm:
        return ReportService(tm).list_comment_brief_reports(community_id, params)


@router.get(
    '/list-all-comment-reports/{comment_id}',
    response_model=PaginationResponse[ReportResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_comment_reports(
    community_id: str,
    comment_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[ReportResponse]:
    with TransactionManager(session) as tm:
        return ReportService(tm).list_comment_reports(comment_id, params)


@router.get(
    '/list-all-complaints',
    response_model=PaginationResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_complaints_from_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[ComplaintResponse]:
    with TransactionManager(session) as tm:
        return ModerationService(tm).list_all_complaints_from_community(
            community_id, params
        )


@router.get(
    '/list-all-polls',
    response_model=PaginationResponse[PollBriefResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_polls_from_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[PollBriefResponse]:
    with TransactionManager(session) as tm:
        return ModerationService(tm).list_all_polls_from_community(community_id, params)


@router.get(
    '/list-all-announcements',
    response_model=PaginationResponse[PostResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_announcements_from_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[PostResponse]:
    with TransactionManager(session) as tm:
        return ModerationService(tm).list_all_announcements_from_community(
            community_id, params
        )


@router.patch(
    '/complaint/{post_id}/status/{complaint_status}',
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
)
def update_status_complaint(
    post_id: str,
    complaint_status: ComplaintStatusEnum,
    session: Session = Depends(get_db),
    moderator: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> ComplaintResponse:
    with TransactionManager(session) as tm:
        return ModerationService(tm).udpate_status_complaint(
            post_id, complaint_status, moderator.id
        )


@router.delete(
    '/report-comment/{report_comment_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_report_comment(
    community_id: str,
    report_comment_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> None:
    with TransactionManager(session) as tm:
        ReportService(tm).delete_report_comment(report_comment_id)


@router.post(
    '/moderate-report/{report_id}',
    response_model=ModerationActionResponse | ModerationVotesResponse,
    status_code=status.HTTP_200_OK,
)
def moderate_report(
    community_id: str,
    report_id: str,
    vote: ModerationVotesCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> ModerationActionResponse | ModerationVotesResponse:
    with TransactionManager(session) as tm:
        return ModerationService(tm).moderate_report(report_id, vote)
