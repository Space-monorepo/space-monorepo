import pytest
import uuid

from app.api.comment.model import Comment, CommentLikes
from app.api.comment.schema import (
    CommentCreate,
    CommentStatusEnum,
    CommentUpdate,
)
from app.api.comment.service import CommentService
from app.utils.schema import PaginationSearchParams
from app.api.comment.exceptions import CommentSuspendedError, CommentNotFoundError, CommentLikesNotFoundError
from app.api.post.exceptions import PostNotFoundError


# =============================================================================
# CREATE COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_create_comment_service_success(session_sql, transaction_manager, post_on_db, user_on_db):
    """
    Tests the `create_comment` method of CommentService.

    Scenario:
    - Given a valid comment data with post and user
    - When the service creates the comment
    - Then it should return the created comment response and persist in database
    """
    # Arrange
    comment = CommentCreate(
        post_id=post_on_db.id,
        user_id=user_on_db.id,
        content='Este é um comentário de teste',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    # Act
    comment_response = CommentService(transaction_manager).create_comment(comment)

    # Assert
    assert comment_response.id is not None
    assert comment_response.content == 'Este é um comentário de teste'
    assert comment_response.user.id == uuid.UUID(user_on_db.id)
    assert comment_response.post.id == uuid.UUID(post_on_db.id)
    assert comment_response.status == CommentStatusEnum.ACTIVE
    assert comment_response.likes_count == 0
    assert comment_response.report_count == 0
    assert comment_response.parent_id is None

    # Verify database persistence
    comment_db = session_sql.query(Comment).filter(Comment.id == str(comment_response.id)).first()
    assert comment_db is not None
    assert comment_db.content == 'Este é um comentário de teste'
    assert comment_db.user_id == user_on_db.id
    assert comment_db.post_id == post_on_db.id
    assert comment_db.status == CommentStatusEnum.ACTIVE


@pytest.mark.unit
def test_create_comment_reply_service_success(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    """
    Tests the `create_comment` method of CommentService for creating replies.

    Scenario:
    - Given a valid reply data with parent comment
    - When the service creates the reply comment
    - Then it should return the created reply and link to parent comment
    """
    # Arrange
    reply = CommentCreate(
        post_id=comment_on_db.post_id,
        user_id=secondary_user_on_db.id,
        content='Esta é uma resposta ao comentário',
        parent_id=comment_on_db.id,
        status=CommentStatusEnum.ACTIVE,
    )

    # Act
    reply_response = CommentService(transaction_manager).create_comment(reply)

    # Assert
    assert reply_response.id is not None
    assert reply_response.content == 'Esta é uma resposta ao comentário'
    assert reply_response.user.id == uuid.UUID(secondary_user_on_db.id)
    assert reply_response.post.id == uuid.UUID(comment_on_db.post_id)
    assert reply_response.parent_id == uuid.UUID(comment_on_db.id)

    # Verify database persistence
    reply_db = session_sql.query(Comment).filter(Comment.id == str(reply_response.id)).first()
    assert reply_db is not None
    assert reply_db.parent_id == comment_on_db.id


@pytest.mark.unit
def test_create_comment_increments_post_comments_count_success(session_sql, transaction_manager, post_on_db, secondary_user_on_db):
    """
    Tests that creating a comment increments the post's comments count.

    Scenario:
    - Given a post with current comments count
    - When a new comment is created for that post
    - Then the post's comments count should be incremented by 1
    """
    # Arrange
    original_comments_count = post_on_db.comments_count

    comment = CommentCreate(
        post_id=post_on_db.id,
        user_id=secondary_user_on_db.id,
        content='Este comentário deve incrementar o contador',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    # Act
    CommentService(transaction_manager).create_comment(comment)

    # Refresh the post to get updated data
    session_sql.refresh(post_on_db)

    # Assert
    assert post_on_db.comments_count == original_comments_count + 1


# =============================================================================
# READ COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_get_comment_by_id_service_success(transaction_manager, comment_on_db):
    """
    Tests the `get_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID
    - When the service retrieves the comment
    - Then it should return the expected comment with all related data
    """
    # Act
    comment = CommentService(transaction_manager).get_comment(comment_on_db.id)

    # Assert
    assert comment is not None
    assert comment.id == uuid.UUID(comment_on_db.id)
    assert comment.content == comment_on_db.content
    assert comment.status == comment_on_db.status
    assert comment.user.id == uuid.UUID(comment_on_db.user_id)
    assert comment.post.id == uuid.UUID(comment_on_db.post_id)


# =============================================================================
# LIST COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_list_comments_by_post_service_success(transaction_manager, comment_on_db, post_on_db):
    """
    Tests the `list_comments_by_post` method of CommentService.

    Scenario:
    - Given a post with comments and pagination parameters
    - When the service lists comments by post
    - Then it should return a paginated list of comments for that post
    """
    # Arrange
    params = PaginationSearchParams(offset=0, limit=10)

    # Act
    comments = CommentService(transaction_manager).list_comments_by_post(post_on_db.id, params)

    # Assert
    assert comments is not None
    assert comments.items is not None
    assert len(comments.items) > 0
    assert comments.items[0].post.id == uuid.UUID(post_on_db.id)
    assert comments.total > 0
    assert comments.current_offset == 0
    assert comments.current_limit == 10


@pytest.mark.unit
def test_list_comments_by_user_service_success(transaction_manager, comment_on_db, user_on_db):
    """
    Tests the `list_comments_by_user` method of CommentService.

    Scenario:
    - Given a user with comments and pagination parameters
    - When the service lists comments by user
    - Then it should return a paginated list of comments from that user
    """
    # Arrange
    params = PaginationSearchParams(offset=0, limit=10)

    # Act
    comments = CommentService(transaction_manager).list_comments_by_user(user_on_db.id, params)

    # Assert
    assert comments is not None
    assert comments.items is not None
    assert len(comments.items) > 0
    assert comments.items[0].user.id == uuid.UUID(user_on_db.id)
    assert comments.total > 0
    assert comments.current_offset == 0
    assert comments.current_limit == 10


@pytest.mark.unit
def test_list_replies_by_parent_service_success(transaction_manager, comment_reply_on_db, comment_on_db):
    """
    Tests the `list_replies_by_parent` method of CommentService.

    Scenario:
    - Given a parent comment with replies and pagination parameters
    - When the service lists replies by parent comment
    - Then it should return a paginated list of replies to that comment
    """
    # Arrange
    params = PaginationSearchParams(offset=0, limit=10)

    # Act
    replies = CommentService(transaction_manager).list_replies_by_parent(comment_on_db.id, params)

    # Assert
    assert replies is not None
    assert replies.items is not None
    assert len(replies.items) > 0
    assert replies.items[0].parent_id == uuid.UUID(comment_on_db.id)
    assert replies.total > 0
    assert replies.current_offset == 0
    assert replies.current_limit == 10


# =============================================================================
# UPDATE COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_update_comment_content_service_success(session_sql, transaction_manager, comment_on_db):
    """
    Tests the `update_comment` method of CommentService for content updates.

    Scenario:
    - Given a valid comment and updated content
    - When the service updates the comment content
    - Then it should return updated comment and persist changes in database
    """
    # Arrange
    comment_update = CommentUpdate(content='Conteúdo atualizado')

    # Act
    updated_comment = CommentService(transaction_manager).update_comment(comment_on_db.id, comment_update)

    # Assert
    assert updated_comment is not None
    assert updated_comment.content == 'Conteúdo atualizado'
    assert updated_comment.id == uuid.UUID(comment_on_db.id)

    # Verify database persistence
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db.content == 'Conteúdo atualizado'


@pytest.mark.unit
def test_update_comment_status_service_success(session_sql, transaction_manager, comment_on_db):
    """
    Tests the `update_comment` method of CommentService for status updates.

    Scenario:
    - Given a valid comment and new status
    - When the service updates the comment status
    - Then it should return updated comment with new status and persist in database
    """
    # Arrange
    comment_update = CommentUpdate(status=CommentStatusEnum.SUSPENDED)

    # Act
    updated_comment = CommentService(transaction_manager).update_comment(comment_on_db.id, comment_update)

    # Assert
    assert updated_comment is not None
    assert updated_comment.status == CommentStatusEnum.SUSPENDED
    assert updated_comment.id == uuid.UUID(comment_on_db.id)

    # Verify database persistence
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db.status == CommentStatusEnum.SUSPENDED


# =============================================================================
# DELETE COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_delete_comment_service_success(session_sql, transaction_manager, comment_on_db):
    """
    Tests the `delete_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID
    - When the service deletes the comment
    - Then it should return True and remove comment from database
    """
    # Act
    result = CommentService(transaction_manager).delete_comment(comment_on_db.id)

    # Assert
    assert result is True

    # Verify database deletion
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    assert comment_db is None


@pytest.mark.unit
def test_delete_comment_decrements_post_comments_count_success(session_sql, transaction_manager, post_on_db, user_on_db):
    """
    Tests that deleting a comment decrements the post's comments count.

    Scenario:
    - Given a post with current comments count > 0
    - When a comment is deleted from that post
    - Then the post's comments count should be decremented by 1
    """
    # Arrange - First create a comment to ensure the post has comments_count > 0
    comment_create = CommentCreate(
        post_id=post_on_db.id,
        user_id=user_on_db.id,
        content='Este comentário será deletado',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    # Create comment to increment the counter
    comment_response = CommentService(transaction_manager).create_comment(comment_create)
    session_sql.refresh(post_on_db)
    comments_count_after_create = post_on_db.comments_count

    # Act - Delete the comment
    CommentService(transaction_manager).delete_comment(str(comment_response.id))

    # Refresh the post to get updated data
    session_sql.refresh(post_on_db)

    # Assert
    assert post_on_db.comments_count == comments_count_after_create - 1


# =============================================================================
# LIKE COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_like_comment_service_success(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    """
    Tests the `like_comment` method of CommentService.

    Scenario:
    - Given a valid comment and user
    - When the service likes the comment
    - Then it should increment likes count and create like record in database
    """
    # Arrange
    original_likes_count = comment_on_db.likes_count
    user_id = secondary_user_on_db.id
    comment_id = comment_on_db.id

    # Act
    like_response = CommentService(transaction_manager).like_comment(comment_id, user_id)

    # Assert
    assert like_response is not None
    assert like_response.likes_count == original_likes_count + 1
    assert like_response.id == uuid.UUID(comment_id)

    # Verify database changes
    session_sql.refresh(comment_on_db)
    assert comment_on_db.likes_count == original_likes_count + 1

    # Verify like record creation
    like_record = session_sql.query(CommentLikes).filter(
        CommentLikes.comment_id == comment_id,
        CommentLikes.user_id == user_id
    ).first()
    assert like_record is not None


@pytest.mark.unit
def test_unlike_comment_service_success(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    """
    Tests the `unlike_comment` method of CommentService.

    Scenario:
    - Given a previously liked comment
    - When the service unlikes the comment
    - Then it should decrement likes count and remove like record from database
    """
    # Arrange
    original_likes_count = comment_on_db.likes_count
    user_id = secondary_user_on_db.id
    comment_id = comment_on_db.id

    # First like the comment to set up test state
    CommentService(transaction_manager).like_comment(comment_id, user_id)
    session_sql.refresh(comment_on_db)
    liked_count = comment_on_db.likes_count

    # Act
    unlike_response = CommentService(transaction_manager).unlike_comment(comment_id, user_id)

    # Assert
    assert unlike_response is not None
    assert unlike_response.likes_count == liked_count - 1
    assert unlike_response.id == uuid.UUID(comment_id)

    # Verify database changes
    session_sql.refresh(comment_on_db)
    assert comment_on_db.likes_count == liked_count - 1

    # Verify like record deletion
    like_record = session_sql.query(CommentLikes).filter(
        CommentLikes.comment_id == comment_id,
        CommentLikes.user_id == user_id
    ).first()
    assert like_record is None


@pytest.mark.unit
def test_list_likes_comment_service_success(session_sql, transaction_manager, comment_on_db, secondary_user_on_db):
    """
    Tests the `list_likes_comment` method of CommentService.

    Scenario:
    - Given a comment with likes
    - When the service lists comment likes
    - Then it should return list of all likes for that comment
    """
    # Arrange
    initial_likes_count = comment_on_db.likes_count
    comment_id = comment_on_db.id
    user_id = secondary_user_on_db.id

    # Add a like to ensure we have data
    CommentService(transaction_manager).like_comment(comment_id, user_id)

    # Act
    likes = CommentService(transaction_manager).list_likes_comment(comment_id)

    # Assert
    assert likes is not None
    assert len(likes) > 0
    assert likes[0].comment_id == uuid.UUID(comment_id)
    assert likes[0].user_id == uuid.UUID(user_id)


@pytest.mark.unit
def test_list_user_liked_comments_service_success(transaction_manager, comment_on_db, secondary_user_on_db):
    """
    Tests the `list_user_liked_comments` method of CommentService.

    Scenario:
    - Given a user who has liked comments and pagination parameters
    - When the service lists user's liked comments
    - Then it should return a paginated list of comments liked by that user
    """
    # Arrange
    comment_id = comment_on_db.id
    user_id = secondary_user_on_db.id

    # Like the comment first to ensure we have data
    CommentService(transaction_manager).like_comment(comment_id, user_id)
    params = PaginationSearchParams(offset=0, limit=10)

    # Act
    liked_comments = CommentService(transaction_manager).list_user_liked_comments(user_id, params)

    # Assert
    assert liked_comments is not None
    assert liked_comments.items is not None
    assert len(liked_comments.items) > 0
    assert liked_comments.total > 0
    assert liked_comments.current_offset == 0
    assert liked_comments.current_limit == 10

    # Verify that the returned comments contain the liked comment
    found_comment = False
    for comment in liked_comments.items:
        if comment.id == uuid.UUID(comment_id):
            found_comment = True
            break
    assert found_comment


# =============================================================================
# REPORT COMMENT TESTS
# =============================================================================

@pytest.mark.unit
def test_report_comment_service_success(session_sql, transaction_manager, comment_on_db):
    """
    Tests the `report_comment` method of CommentService.

    Scenario:
    - Given a valid comment below report threshold
    - When the service reports the comment
    - Then it should increment report count and maintain active status
    """
    # Arrange
    original_report_count = comment_on_db.report_count
    comment_id = comment_on_db.id

    # Act
    reported_comment = CommentService(transaction_manager).report_comment(comment_id)

    # Assert
    assert reported_comment is not None
    assert reported_comment.report_count == original_report_count + 1
    assert reported_comment.status == CommentStatusEnum.ACTIVE  # Should remain active if below threshold
    assert reported_comment.id == uuid.UUID(comment_id)

    # Verify database persistence
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_id).first()
    assert comment_db.report_count == original_report_count + 1


@pytest.mark.unit
def test_report_comment_threshold_service_success(session_sql, transaction_manager, comment_on_db):
    """
    Tests the `report_comment` method of CommentService when reaching threshold.

    Scenario:
    - Given a comment at report threshold minus one
    - When the service reports the comment
    - Then it should change status to reported when threshold is reached
    """
    # Arrange
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    # Set report count to threshold - 1 (threshold is 10 according to service)
    comment_db.report_count = 9
    session_sql.commit()

    # Act
    reported_comment = CommentService(transaction_manager).report_comment(comment_on_db.id)

    # Assert
    assert reported_comment is not None
    assert reported_comment.report_count == 10
    assert reported_comment.status == CommentStatusEnum.REPORTED  # Should change to reported at threshold


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

@pytest.mark.unit
def test_create_comment_with_nonexistent_post_raises_error(transaction_manager, user_on_db):
    """
    Tests that creating a comment with nonexistent post raises PostNotFoundError.

    Scenario:
    - Given a comment with non-existent post ID
    - When the service attempts to create the comment
    - Then it should raise PostNotFoundError
    """
    # Arrange
    comment = CommentCreate(
        post_id='00000000-0000-0000-0000-000000000000',  # Non-existent post ID
        user_id=user_on_db.id,
        content='Este comentário tem um post inexistente',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    # Act & Assert
    with pytest.raises(PostNotFoundError):
        CommentService(transaction_manager).create_comment(comment)


@pytest.mark.unit
def test_create_comment_with_nonexistent_parent_raises_error(transaction_manager, post_on_db, user_on_db):
    """
    Tests that creating a reply with nonexistent parent raises CommentNotFoundError.

    Scenario:
    - Given a comment with non-existent parent comment ID
    - When the service attempts to create the reply
    - Then it should raise CommentNotFoundError
    """
    # Arrange
    comment = CommentCreate(
        post_id=post_on_db.id,
        user_id=user_on_db.id,
        content='Esta é uma resposta a um comentário inexistente',
        parent_id='00000000-0000-0000-0000-000000000000',  # Non-existent parent ID
        status=CommentStatusEnum.ACTIVE,
    )

    # Act & Assert
    with pytest.raises(CommentNotFoundError):
        CommentService(transaction_manager).create_comment(comment)


@pytest.mark.unit
def test_get_nonexistent_comment_raises_error(transaction_manager):
    """
    Tests that getting a nonexistent comment raises CommentNotFoundError.

    Scenario:
    - Given a non-existent comment ID
    - When the service attempts to get the comment
    - Then it should raise CommentNotFoundError
    """
    # Act & Assert
    with pytest.raises(CommentNotFoundError):
        CommentService(transaction_manager).get_comment('00000000-0000-0000-0000-000000000000')


@pytest.mark.unit
def test_unlike_comment_without_like_raises_error(transaction_manager, comment_on_db, secondary_user_on_db):
    """
    Tests that unliking a comment without previous like raises CommentLikesNotFoundError.

    Scenario:
    - Given a comment that user has not liked
    - When the service attempts to unlike the comment
    - Then it should raise CommentLikesNotFoundError
    """
    # Act & Assert
    with pytest.raises(CommentLikesNotFoundError):
        CommentService(transaction_manager).unlike_comment(comment_on_db.id, secondary_user_on_db.id)


@pytest.mark.unit
def test_report_suspended_comment_raises_error(session_sql, transaction_manager, comment_on_db):
    """
    Tests that reporting a suspended comment raises CommentSuspendedError.

    Scenario:
    - Given a comment with suspended status
    - When the service attempts to report the comment
    - Then it should raise CommentSuspendedError
    """
    # Arrange
    comment_db = session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    comment_db.status = CommentStatusEnum.SUSPENDED
    session_sql.commit()

    # Act & Assert
    with pytest.raises(CommentSuspendedError):
        CommentService(transaction_manager).report_comment(comment_on_db.id)
