from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.comment.schema import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.api.comment.service import CommentService
from app.api.communities.model import CommunityMember
from app.api.communities.schema import CommunityMemberResponse
from app.auth.deps import require_comment_owner, require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/comments', tags=['comments'])


@router.get(
    '/{community_id}/post/{post_id}/comment/{comment_id}',
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def get_comment(
    comment_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> CommentResponse:
    with TransactionManager(session) as tm:
        return CommentService(tm).get_comment(comment_id)


@router.get(
    '/{community_id}/post/{post_id}/list-comments',
    response_model=PaginationResponse[CommentResponse],
    status_code=status.HTTP_200_OK,
)
def list_comments_by_post(
    post_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> PaginationResponse[CommentResponse]:
    with TransactionManager(session) as tm:
        return CommentService(tm).list_comments_by_post(post_id, params)


@router.get(
    '/{community_id}/user/{user_id}/list-comments',
    response_model=PaginationResponse[CommentResponse],
    status_code=status.HTTP_200_OK,
)
def list_comments_by_user(
    user_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> PaginationResponse[CommentResponse]:
    with TransactionManager(session) as tm:
        return CommentService(tm).list_comments_by_user(user_id, params)


@router.get(
    '/{community_id}/comment/{parent_id}/list-replies',
    response_model=PaginationResponse[CommentResponse],
    status_code=status.HTTP_200_OK,
)
def list_replies_by_parent(
    parent_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> PaginationResponse[CommentResponse]:
    with TransactionManager(session) as tm:
        return CommentService(tm).list_replies_by_parent(parent_id, params)


@router.post(
    '/{community_id}/post/{post_id}/create-comment',
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    comment: CommentCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> CommentResponse:
    with TransactionManager(session) as tm:
        return CommentService(tm).create_comment(comment)


@router.patch(
    '/{community_id}/comment/{comment_id}',
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def update_comment(
    community_id: str,
    comment_id: str,
    comment: CommentUpdate,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> CommentResponse:
    if comment.content and not require_comment_owner(
        comment_id, session, current_member
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    if comment.status and current_member.role not in {'admin', 'moderator'}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    with TransactionManager(session) as tm:
        return CommentService(tm).update_comment(comment_id, comment)


@router.delete(
    '/{community_id}/comment/{comment_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
):
    with TransactionManager(session) as tm:
        CommentService(tm).delete_comment(comment_id)


@router.post(
    '/{community_id}/comment/{comment_id}/like',
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def like_comment(
    comment_id: str,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> CommentResponse:
    with TransactionManager(session) as tm:
        return CommentService(tm).like_comment(comment_id, current_member.id)


@router.post(
    '/{community_id}/comment/{comment_id}/unlike',
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def unlike_comment(
    comment_id: str,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> CommentResponse:
    with TransactionManager(session) as tm:
        return CommentService(tm).unlike_comment(comment_id, current_member.id)


@router.get(
    '/{community_id}/comment/{comment_id}/list-likes',
    response_model=list[CommunityMemberResponse],
    status_code=status.HTTP_200_OK,
)
def list_likes_comment(
    comment_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> list[CommunityMemberResponse]:
    with TransactionManager(session) as tm:
        return CommentService(tm).list_likes_comment(comment_id)


@router.patch(
    '/{community_id}/comment/{comment_id}/report',
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def report_comment(
    comment_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> CommentResponse:
    with TransactionManager(session) as tm:
        return CommentService(tm).report_comment(comment_id)
