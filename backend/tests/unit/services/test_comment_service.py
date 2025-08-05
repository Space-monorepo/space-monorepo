import uuid

from app.comment.model import Comment, CommentLikes
from app.comment.schema import (
    CommentCreate,
    CommentStatusEnum,
    CommentUpdate,
)
from app.comment.service import CommentService
from app.utils.schema import PaginationSearchParams
from app.comment.exceptions import CommentSuspendedError, CommentNotFoundError, CommentLikesNotFoundError
from app.post.exceptions import PostNotFoundError


def test_create_comment_service(session_sql, transaction_manager, post_on_db, user_on_db):
    comment = CommentCreate(
        post_id=post_on_db.id,
        user_id=user_on_db.id,
        content='Este é um comentário de teste',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    comment_response = CommentService(transaction_manager).create_comment(comment)
    assert comment_response.id is not None
    assert comment_response.content == 'Este é um comentário de teste'
    assert comment_response.user.id == user_on_db.id
    assert comment_response.post.id == post_on_db.id
    assert comment_response.status == CommentStatusEnum.ACTIVE
    assert comment_response.likes_count == 0
    assert comment_response.report_count == 0
    assert comment_response.parent_id is None

    comment_db = session_sql.query(Comment).filter(Comment.id == comment_response.id).first()
    assert comment_db is not None
    assert comment_db.content == 'Este é um comentário de teste'
    assert comment_db.user_id == user_on_db.id
    assert comment_db.post_id == post_on_db.id
    assert comment_db.status == CommentStatusEnum.ACTIVE


def test_create_comment_reply_service(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    reply = CommentCreate(
        post_id=comment_on_db.post_id,
        user_id=secondary_user_on_db.id,
        content='Esta é uma resposta ao comentário',
        parent_id=comment_on_db.id,
        status=CommentStatusEnum.ACTIVE,
    )

    reply_response = CommentService(transaction_manager).create_comment(reply)
    assert reply_response.id is not None
    assert reply_response.content == 'Esta é uma resposta ao comentário'
    assert reply_response.user.id == secondary_user_on_db.id
    assert reply_response.post.id == comment_on_db.post_id
    assert reply_response.parent_id == comment_on_db.id

    reply_db = session_sql.query(Comment).filter(Comment.id == reply_response.id).first()
    assert reply_db is not None
    assert reply_db.parent_id == comment_on_db.id


def test_get_comment_by_id_service(transaction_manager, comment_on_db):
    comment = CommentService(transaction_manager).get_comment(comment_on_db.id)
    assert comment is not None
    assert comment.id == comment_on_db.id
    assert comment.content == comment_on_db.content
    assert comment.user.id == comment_on_db.user_id
    assert comment.post.id == comment_on_db.post_id


def test_list_comments_by_post_service(transaction_manager, comment_on_db, post_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    comments = CommentService(transaction_manager).list_comments_by_post(post_on_db.id, params)
    assert comments is not None
    assert comments.items is not None
    assert len(comments.items) > 0
    assert comments.items[0].post.id == post_on_db.id
    assert comments.total > 0
    assert comments.current_offset == 0
    assert comments.current_limit == 10


def test_list_comments_by_user_service(transaction_manager, comment_on_db, user_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    comments = CommentService(transaction_manager).list_comments_by_user(user_on_db.id, params)
    assert comments is not None
    assert comments.items is not None
    assert len(comments.items) > 0
    assert comments.items[0].user.id == user_on_db.id
    assert comments.total > 0
    assert comments.current_offset == 0
    assert comments.current_limit == 10


def test_list_replies_by_parent_service(transaction_manager, comment_reply_on_db, comment_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    replies = CommentService(transaction_manager).list_replies_by_parent(comment_on_db.id, params)
    assert replies is not None
    assert replies.items is not None
    assert len(replies.items) > 0
    assert replies.items[0].parent_id == comment_on_db.id
    assert replies.total > 0
    assert replies.current_offset == 0
    assert replies.current_limit == 10


def test_update_comment_service(session_sql, transaction_manager, comment_on_db):
    comment_update = CommentUpdate(content='Conteúdo atualizado')
    comment = CommentService(transaction_manager).update_comment(comment_on_db.id, comment_update)
    assert comment is not None
    assert comment.content == 'Conteúdo atualizado'
    assert comment.id == comment_on_db.id

    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db is not None
    assert comment_db.content == 'Conteúdo atualizado'


def test_update_comment_status_service(session_sql, transaction_manager, comment_on_db):
    comment_update = CommentUpdate(status=CommentStatusEnum.SUSPENDED)
    comment = CommentService(transaction_manager).update_comment(comment_on_db.id, comment_update)
    assert comment is not None
    assert comment.status == CommentStatusEnum.SUSPENDED
    assert comment.id == comment_on_db.id

    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db is not None
    assert comment_db.status == CommentStatusEnum.SUSPENDED


def test_delete_comment_service(session_sql, transaction_manager, comment_on_db):
    result = CommentService(transaction_manager).delete_comment(comment_on_db.id)
    assert result is True

    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db is None


def test_like_comment_service(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    original_likes_count = comment_on_db.likes_count
    
    comment = CommentService(transaction_manager).like_comment(comment_on_db.id, secondary_user_on_db.id)
    assert comment is not None
    assert comment.likes_count == original_likes_count + 1
    assert comment.id == comment_on_db.id

    session_sql.refresh(comment_on_db)
    assert comment_on_db.likes_count == original_likes_count + 1

    like_db = session_sql.query(CommentLikes).filter(
        CommentLikes.comment_id == comment_on_db.id,
        CommentLikes.user_id == secondary_user_on_db.id
    ).first()
    assert like_db is not None
    assert like_db.comment_id == comment_on_db.id
    assert like_db.user_id == secondary_user_on_db.id


def test_unlike_comment_service(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    original_likes_count = comment_on_db.likes_count
    
    comment = CommentService(transaction_manager).like_comment(comment_on_db.id, secondary_user_on_db.id)
    assert comment is not None
    assert comment.likes_count == original_likes_count + 1

    comment = CommentService(transaction_manager).unlike_comment(comment_on_db.id, secondary_user_on_db.id)
    assert comment is not None
    assert comment.likes_count == original_likes_count
    assert comment.id == comment_on_db.id

    session_sql.refresh(comment_on_db)
    assert comment_on_db.likes_count == original_likes_count
    
    like_db = session_sql.query(CommentLikes).filter(
            CommentLikes.comment_id == comment_on_db.id,
            CommentLikes.user_id == secondary_user_on_db.id
        ).first()
    assert like_db is None


def test_list_likes_comment_service(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    initial_likes_count = comment_on_db.likes_count
    
    comment = CommentService(transaction_manager).like_comment(comment_on_db.id, secondary_user_on_db.id)
    assert comment is not None
    assert comment.likes_count == initial_likes_count + 1

    likes = CommentService(transaction_manager).list_likes_comment(comment_on_db.id)
    assert likes is not None
    assert len(likes) == 1
    assert likes[0].comment_id == comment_on_db.id
    assert likes[0].user_id == secondary_user_on_db.id
    assert likes[0].created_at is not None



def test_report_comment_service(session_sql, transaction_manager, comment_on_db):
    original_report_count = comment_on_db.report_count
    
    comment = CommentService(transaction_manager).report_comment(comment_on_db.id)
    assert comment is not None
    assert comment.report_count == original_report_count + 1
    assert comment.id == comment_on_db.id
    
    if original_report_count + 1 < CommentService.REPORT_THRESHOLD:
        assert comment.status == CommentStatusEnum.ACTIVE
    else:
        assert comment.status == CommentStatusEnum.REPORTED

    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db is not None
    assert comment_db.report_count == original_report_count + 1


def test_report_comment_threshold_service(session_sql, transaction_manager, comment_on_db):
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    comment_db.report_count = CommentService.REPORT_THRESHOLD - 1
    session_sql.commit()

    comment = CommentService(transaction_manager).report_comment(comment_on_db.id)
    assert comment is not None
    assert comment.report_count == CommentService.REPORT_THRESHOLD
    assert comment.status == CommentStatusEnum.REPORTED
    assert comment.id == comment_on_db.id

    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db is not None
    assert comment_db.report_count == CommentService.REPORT_THRESHOLD
    assert comment_db.status == CommentStatusEnum.REPORTED


def test_list_user_liked_comments_service(transaction_manager, comment_on_db, secondary_user_on_db):
    initial_likes_count = comment_on_db.likes_count
    
    comment = CommentService(transaction_manager).like_comment(comment_on_db.id, secondary_user_on_db.id)
    assert comment is not None
    assert comment.likes_count == initial_likes_count + 1

    params = PaginationSearchParams(offset=0, limit=10)
    liked_comments = CommentService(transaction_manager).list_user_liked_comments(secondary_user_on_db.id, params)
    assert liked_comments is not None
    assert liked_comments.items is not None
    assert len(liked_comments.items) > 0
    assert liked_comments.items[0].id == comment_on_db.id
    assert liked_comments.total > 0
    assert liked_comments.current_offset == 0
    assert liked_comments.current_limit == 10



def test_create_comment_increments_post_comments_count(session_sql, transaction_manager, post_on_db, secondary_user_on_db):
    original_comments_count = post_on_db.comments_count
    
    comment = CommentCreate(
        post_id=post_on_db.id,
        user_id=secondary_user_on_db.id,
        content='Comentário que deve incrementar contador',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    comment_response = CommentService(transaction_manager).create_comment(comment)
    assert comment_response.id is not None

    session_sql.refresh(post_on_db)
    assert post_on_db.comments_count == original_comments_count + 1


def test_delete_comment_decrements_post_comments_count(session_sql, transaction_manager, comment_on_db, post_on_db):
    original_comments_count = post_on_db.comments_count
    
    result = CommentService(transaction_manager).delete_comment(comment_on_db.id)
    assert result is True

    session_sql.refresh(post_on_db)
    if original_comments_count > 0:
        assert post_on_db.comments_count == original_comments_count - 1
    else:
        assert post_on_db.comments_count == 0


def test_create_comment_with_nonexistent_post_raises_error(transaction_manager, user_on_db):    
    comment = CommentCreate(
        post_id=uuid.uuid4(),
        user_id=user_on_db.id,
        content='Comentário em post inexistente',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    try:
        CommentService(transaction_manager).create_comment(comment)
        assert False, "Deveria ter levantado PostNotFoundError"
    except PostNotFoundError:
        assert True


def test_create_comment_with_nonexistent_parent_raises_error(transaction_manager, post_on_db, user_on_db):    
    comment = CommentCreate(
        post_id=post_on_db.id,
        user_id=user_on_db.id,
        content='Resposta a comentário inexistente',
        parent_id=uuid.uuid4(),
        status=CommentStatusEnum.ACTIVE,
    )

    try:
        CommentService(transaction_manager).create_comment(comment)
        assert False, "Deveria ter levantado CommentNotFoundError"
    except CommentNotFoundError:
        assert True


def test_get_nonexistent_comment_raises_error(transaction_manager):
    try:
        CommentService(transaction_manager).get_comment(uuid.uuid4())
        assert False, "Deveria ter levantado CommentNotFoundError"
    except CommentNotFoundError:
        assert True


def test_unlike_comment_without_like_raises_error(transaction_manager, comment_on_db, secondary_user_on_db):
    try:
        CommentService(transaction_manager).unlike_comment(comment_on_db.id, secondary_user_on_db.id)
        assert False, "Deveria ter levantado CommentLikesNotFoundError"
    except CommentLikesNotFoundError:
        assert True


def test_report_suspended_comment_raises_error(session_sql, transaction_manager, comment_on_db):
    
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    comment_db.status = CommentStatusEnum.SUSPENDED
    session_sql.commit()

    try:
        CommentService(transaction_manager).report_comment(comment_on_db.id)
        assert False, "Deveria ter levantado CommentSuspendedError"
    except CommentSuspendedError:
        assert True