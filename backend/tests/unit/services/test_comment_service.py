import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timezone

from app.api.comment.model import Comment, CommentLikes
from app.api.comment.schema import (
    CommentCreate,
    CommentStatusEnum,
    CommentUpdate,
    CommentResponse,
)
from app.api.comment.service import CommentService
from app.api.comment.exceptions import (
    CommentSuspendedError,
    CommentNotFoundError,
    CommentLikesNotFoundError,
    UnexpectedCommentError,
)
from app.api.post.exceptions import PostNotFoundError
from app.api.users.model import User
from app.api.post.model import Post
from app.api.communities.model import CommunityMember
from app.api.communities.schema import CommunityMemberResponse, CommunityMemberRoleEnum
from app.utils.schema import PaginationSearchParams


# =============================================================================
# CONSTANTS
# =============================================================================

REPORT_THRESHOLD = 10
DEFAULT_LIKES_COUNT = 0
DEFAULT_REPORT_COUNT = 0
DEFAULT_COMMENTS_COUNT = 0
DEFAULT_PAGINATION_OFFSET = 0
DEFAULT_PAGINATION_LIMIT = 10


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def fake_ids():
    """Fixture que retorna IDs únicos para uso nos testes."""
    return {
        'comment_id': uuid4(),
        'post_id': str(uuid4()),
        'user_id': str(uuid4()),
        'community_id': str(uuid4()),
        'parent_id': str(uuid4()),
        'member_id': str(uuid4()),
        'reply_id': uuid4(),
    }


@pytest.fixture
def fake_comment_data():
    """Fixture com dados padrão para comentários."""
    return {
        'content': 'Test comment content',
        'status': CommentStatusEnum.ACTIVE,
        'likes_count': DEFAULT_LIKES_COUNT,
        'report_count': DEFAULT_REPORT_COUNT,
        'created_at': datetime.now(timezone.utc),
    }


@pytest.fixture
def fake_post(fake_ids):
    """Fixture que retorna um mock de Post."""
    post = Mock(spec=Post)
    post.id = fake_ids['post_id']
    post.title = 'Test Post'
    post.community_id = fake_ids['community_id']
    post.comments_count = DEFAULT_COMMENTS_COUNT
    return post


@pytest.fixture
def fake_user(fake_ids):
    """Fixture que retorna um mock de User."""
    user = Mock(spec=User)
    user.id = fake_ids['user_id']
    user.name = 'Test User'
    user.profile_image_url = 'https://example.com/profile.jpg'
    return user


@pytest.fixture
def fake_comment(fake_ids, fake_comment_data, fake_post, fake_user):
    """Fixture que retorna um mock de Comment com relacionamentos."""
    comment = Mock(spec=Comment)
    comment.id = fake_ids['comment_id']
    comment.post_id = fake_ids['post_id']
    comment.user_id = fake_ids['user_id']
    comment.content = fake_comment_data['content']
    comment.status = fake_comment_data['status']
    comment.likes_count = fake_comment_data['likes_count']
    comment.report_count = fake_comment_data['report_count']
    comment.parent_id = None
    comment.created_at = fake_comment_data['created_at']
    comment.post = fake_post
    comment.user = fake_user
    return comment


@pytest.fixture
def mock_repositories():
    """Fixture que retorna mocks dos repositórios."""
    return {
        'tm': Mock(),
        'comment_repo': Mock(),
        'post_repo': Mock(),
        'member_repo': Mock(),
        'comment_likes_repo': Mock(),
    }


@pytest.fixture
def mock_services():
    """Fixture que retorna mocks dos serviços."""
    return {
        'community_service': Mock(),
    }


@pytest.fixture
def comment_service(mock_repositories, mock_services):
    """Fixture que retorna uma instância configurada do CommentService."""
    service = CommentService(mock_repositories['tm'])
    service.comment_repo = mock_repositories['comment_repo']
    service.post_repo = mock_repositories['post_repo']
    service.member_repo = mock_repositories['member_repo']
    service.comment_likes_repo = mock_repositories['comment_likes_repo']
    service.community_service = mock_services['community_service']
    return service


@pytest.fixture
def pagination_params():
    """Fixture que retorna parâmetros de paginação padrão."""
    return PaginationSearchParams(
        offset=DEFAULT_PAGINATION_OFFSET, limit=DEFAULT_PAGINATION_LIMIT
    )


# =============================================================================
# SUCCESS TESTS
# =============================================================================


@pytest.mark.unit
def test_create_comment_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user, fake_comment
):
    """
    Tests the `create_comment` method of CommentService.

    Scenario:
    - Given a valid comment creation request
    - When the service creates the comment and saves it to repository
    - Then it should return the created comment with mapped response
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment_create = CommentCreate(
        post_id=fake_ids['post_id'],
        user_id=fake_ids['user_id'],
        content='Test comment content',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    mock_repositories['comment_repo'].save.return_value = fake_comment
    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.create_comment(fake_comment_create)

    # Assert
    assert mock_repositories['post_repo'].get_by_id.call_count == 2
    mock_repositories['comment_repo'].save.assert_called_once()
    mock_repositories['post_repo'].save.assert_called_once_with(fake_post)
    mock_repositories['member_repo'].get_member_role.assert_called_once_with(
        fake_ids['user_id'], fake_ids['community_id']
    )
    assert fake_post.comments_count == 1
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert str(result.post.id) == fake_ids['post_id']
    assert str(result.user.id) == fake_ids['user_id']
    assert result.content == 'Test comment content'
    assert result.status == CommentStatusEnum.ACTIVE
    assert result.likes_count == DEFAULT_LIKES_COUNT
    assert result.report_count == DEFAULT_REPORT_COUNT
    assert result.parent_id is None
    assert result.user.member_role == fake_member_role


@pytest.mark.unit
def test_create_comment_reply_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `create_comment` method of CommentService for creating replies.

    Scenario:
    - Given a valid reply comment creation request with parent
    - When the service creates the reply comment
    - Then it should return the created reply linked to parent comment
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment_create = CommentCreate(
        post_id=fake_ids['post_id'],
        user_id=fake_ids['user_id'],
        content='Test reply content',
        parent_id=fake_ids['parent_id'],
        status=CommentStatusEnum.ACTIVE,
    )

    fake_parent_comment = Mock(spec=Comment)
    fake_parent_comment.id = fake_ids['parent_id']
    fake_parent_comment.post_id = fake_ids['post_id']
    fake_parent_comment.parent_id = None

    fake_created_reply = Mock(spec=Comment)
    fake_created_reply.id = fake_ids['comment_id']
    fake_created_reply.post_id = fake_ids['post_id']
    fake_created_reply.user_id = fake_ids['user_id']
    fake_created_reply.content = 'Test reply content'
    fake_created_reply.parent_id = fake_ids['parent_id']
    fake_created_reply.status = CommentStatusEnum.ACTIVE
    fake_created_reply.likes_count = DEFAULT_LIKES_COUNT
    fake_created_reply.report_count = DEFAULT_REPORT_COUNT
    fake_created_reply.created_at = datetime.now(timezone.utc)
    fake_created_reply.post = fake_post
    fake_created_reply.user = fake_user

    mock_repositories['comment_repo'].get_by_id.return_value = fake_parent_comment
    mock_repositories['comment_repo'].save.return_value = fake_created_reply
    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.create_comment(fake_comment_create)

    # Assert
    assert mock_repositories['post_repo'].get_by_id.call_count == 2
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['parent_id']
    )
    mock_repositories['comment_repo'].save.assert_called_once()
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert str(result.parent_id) == fake_ids['parent_id']
    assert result.content == 'Test reply content'


@pytest.mark.unit
def test_get_comment_by_id_service_success(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests the `get_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID
    - When the service retrieves the comment from repository
    - Then it should return the expected comment response
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER
    fake_comment.likes_count = 3

    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.get_comment(fake_ids['comment_id'])

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.content == fake_comment.content
    assert str(result.user.id) == fake_ids['user_id']
    assert str(result.post.id) == fake_ids['post_id']
    assert result.status == CommentStatusEnum.ACTIVE
    assert result.likes_count == 3
    assert result.report_count == DEFAULT_REPORT_COUNT


@pytest.mark.unit
def test_list_comments_by_post_service_success(
    comment_service,
    mock_repositories,
    fake_ids,
    fake_post,
    fake_comment,
    pagination_params,
):
    """
    Tests the `list_comments_by_post` method of CommentService.

    Scenario:
    - Given a valid post ID and pagination parameters
    - When the service lists comments by post from repository
    - Then it should return a paginated response with the expected comments
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER
    fake_comment.likes_count = 5
    fake_comment.report_count = 1

    mock_repositories['comment_repo'].list_comments_by_post.return_value = (
        [fake_comment],
        1,
    )
    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.list_comments_by_post(
        fake_ids['post_id'], pagination_params, include_replies=False
    )

    # Assert
    mock_repositories['post_repo'].get_by_id.assert_called_once_with(fake_ids['post_id'])
    mock_repositories['comment_repo'].list_comments_by_post.assert_called_once_with(
        fake_ids['post_id'], pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert str(result.items[0].post.id) == fake_ids['post_id']
    assert str(result.items[0].id) == str(fake_ids['comment_id'])
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == DEFAULT_PAGINATION_OFFSET
    assert result.current_limit == DEFAULT_PAGINATION_LIMIT


@pytest.mark.unit
def test_list_comments_by_user_service_success(
    comment_service, mock_repositories, fake_ids, fake_comment, pagination_params
):
    """
    Tests the `list_comments_by_user` method of CommentService.

    Scenario:
    - Given a valid user ID and pagination parameters
    - When the service lists comments by user from repository
    - Then it should return a paginated response with the expected comments
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER
    fake_comment.content = 'User comment content'
    fake_comment.likes_count = 3

    mock_repositories['comment_repo'].list_comments_by_user.return_value = (
        [fake_comment],
        1,
    )
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.list_comments_by_user(
        fake_ids['user_id'], pagination_params
    )

    # Assert
    mock_repositories['comment_repo'].list_comments_by_user.assert_called_once_with(
        fake_ids['user_id'], pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert str(result.items[0].user.id) == fake_ids['user_id']
    assert str(result.items[0].id) == str(fake_ids['comment_id'])
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == DEFAULT_PAGINATION_OFFSET
    assert result.current_limit == DEFAULT_PAGINATION_LIMIT


@pytest.mark.unit
def test_list_replies_by_parent_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user, pagination_params
):
    """
    Tests the `list_replies_by_parent` method of CommentService.

    Scenario:
    - Given a valid parent comment ID and pagination parameters
    - When the service lists replies by parent from repository
    - Then it should return a paginated response with the expected replies
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_parent_comment = Mock(spec=Comment)
    fake_parent_comment.id = fake_ids['parent_id']
    fake_parent_comment.parent_id = None

    fake_reply = Mock(spec=Comment)
    fake_reply.id = fake_ids['reply_id']
    fake_reply.post_id = fake_ids['post_id']
    fake_reply.user_id = fake_ids['user_id']
    fake_reply.content = 'Test reply content'
    fake_reply.parent_id = fake_ids['parent_id']
    fake_reply.status = CommentStatusEnum.ACTIVE
    fake_reply.likes_count = 1
    fake_reply.report_count = DEFAULT_REPORT_COUNT
    fake_reply.created_at = datetime.now(timezone.utc)
    fake_reply.post = fake_post
    fake_reply.user = fake_user

    mock_repositories['comment_repo'].get_by_id.return_value = fake_parent_comment
    mock_repositories['comment_repo'].list_replies_by_parent.return_value = (
        [fake_reply],
        1,
    )
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.list_replies_by_parent(
        fake_ids['parent_id'], pagination_params
    )

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['parent_id']
    )
    mock_repositories['comment_repo'].list_replies_by_parent.assert_called_once_with(
        fake_ids['parent_id'], pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert str(result.items[0].parent_id) == fake_ids['parent_id']
    assert str(result.items[0].id) == str(fake_ids['reply_id'])
    assert result.total == 1


@pytest.mark.unit
def test_update_comment_content_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `update_comment` method of CommentService for content updates.

    Scenario:
    - Given a valid comment ID and update data
    - When the service updates the comment content and saves it to repository
    - Then it should return the updated comment response
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER
    fake_original_content = 'Original content'
    fake_updated_content = 'Updated content'

    fake_comment_update = CommentUpdate(content=fake_updated_content)

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = fake_original_content
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 2
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = fake_updated_content
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 2
    fake_saved_comment.report_count = DEFAULT_REPORT_COUNT
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    mock_repositories['comment_repo'].get_by_id.side_effect = [
        fake_existing_comment,
        fake_saved_comment,
    ]
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.update_comment(fake_ids['comment_id'], fake_comment_update)

    # Assert
    assert mock_repositories['comment_repo'].get_by_id.call_count == 2
    mock_repositories['comment_repo'].save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.content == fake_updated_content
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.content == fake_updated_content


@pytest.mark.unit
def test_update_comment_status_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `update_comment` method of CommentService for status updates.

    Scenario:
    - Given a valid comment ID and status update data
    - When the service updates the comment status and saves it to repository
    - Then it should return the updated comment with new status
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER
    fake_comment_update = CommentUpdate(status=CommentStatusEnum.SUSPENDED)

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = 'Test content'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 1
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = 'Test content'
    fake_saved_comment.status = CommentStatusEnum.SUSPENDED
    fake_saved_comment.likes_count = 1
    fake_saved_comment.report_count = DEFAULT_REPORT_COUNT
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    mock_repositories['comment_repo'].get_by_id.side_effect = [
        fake_existing_comment,
        fake_saved_comment,
    ]
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.update_comment(fake_ids['comment_id'], fake_comment_update)

    # Assert
    assert mock_repositories['comment_repo'].get_by_id.call_count == 2
    mock_repositories['comment_repo'].save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.status == CommentStatusEnum.SUSPENDED
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.status == CommentStatusEnum.SUSPENDED


@pytest.mark.unit
def test_delete_comment_service_success(comment_service, mock_repositories, fake_ids):
    """
    Tests the `delete_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID
    - When the service deletes the comment from repository
    - Then it should return True and decrement post comments count
    """
    # Arrange
    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.content = 'Comment to delete'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 5
    fake_existing_comment.report_count = 1
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_post = Mock(spec=Post)
    fake_post.id = fake_ids['post_id']
    fake_post.comments_count = 5

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].delete.return_value = True
    mock_repositories['post_repo'].get_by_id.return_value = fake_post

    # Act
    result = comment_service.delete_comment(fake_ids['comment_id'])

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories['post_repo'].get_by_id.assert_called_once_with(fake_ids['post_id'])
    mock_repositories['comment_repo'].delete.assert_called_once_with(
        fake_existing_comment
    )
    mock_repositories['post_repo'].save.assert_called_once_with(fake_post)
    assert fake_post.comments_count == 4
    assert result is True


@pytest.mark.unit
def test_like_comment_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `like_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID and member ID
    - When the service likes the comment and saves the like to repository
    - Then it should return the comment with incremented likes count
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = 'Comment to like'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = DEFAULT_LIKES_COUNT
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = 'Comment to like'
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 1
    fake_saved_comment.report_count = DEFAULT_REPORT_COUNT
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    fake_comment_like = Mock(spec=CommentLikes)
    fake_comment_like.comment_id = fake_ids['comment_id']
    fake_comment_like.member_id = fake_ids['member_id']

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories['comment_likes_repo'].save.return_value = fake_comment_like
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.like_comment(fake_ids['comment_id'], fake_ids['member_id'])

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories['comment_likes_repo'].save.assert_called_once()
    mock_repositories['comment_repo'].save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.likes_count == 1
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.likes_count == 1
    assert result.content == 'Comment to like'


@pytest.mark.unit
def test_unlike_comment_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `unlike_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID and member ID with an existing like
    - When the service unlikes the comment and removes the like from repository
    - Then it should return the comment with decremented likes count
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = 'Comment to unlike'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 1
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = 'Comment to unlike'
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = DEFAULT_LIKES_COUNT
    fake_saved_comment.report_count = DEFAULT_REPORT_COUNT
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    fake_existing_like = Mock(spec=CommentLikes)
    fake_existing_like.comment_id = fake_ids['comment_id']
    fake_existing_like.member_id = fake_ids['member_id']

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.return_value = fake_existing_like
    mock_repositories['comment_likes_repo'].delete.return_value = True
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.unlike_comment(
        fake_ids['comment_id'], fake_ids['member_id']
    )

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.assert_called_once_with(
        fake_ids['comment_id'], fake_ids['member_id']
    )
    mock_repositories['comment_likes_repo'].delete.assert_called_once_with(
        fake_existing_like
    )
    mock_repositories['comment_repo'].save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.likes_count == DEFAULT_LIKES_COUNT
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.likes_count == DEFAULT_LIKES_COUNT
    assert result.content == 'Comment to unlike'


@pytest.mark.unit
def test_list_likes_comment_service_success(
    comment_service, mock_repositories, mock_services, fake_ids
):
    """
    Tests the `list_likes_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID with existing likes
    - When the service lists members who liked the comment
    - Then it should return a list of community member responses
    """
    # Arrange
    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.content = 'Comment with likes'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 3
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_community_member = Mock(spec=CommunityMember)
    fake_community_member.id = fake_ids['member_id']
    fake_community_member.user_id = fake_ids['user_id']
    fake_community_member.community_id = fake_ids['community_id']
    fake_community_member.role = CommunityMemberRoleEnum.MEMBER
    fake_community_member.status_participation = 'active'

    fake_member_response = Mock(spec=CommunityMemberResponse)
    fake_member_response.user_id = fake_ids['user_id']
    fake_member_response.community_id = fake_ids['community_id']
    fake_member_response.role = CommunityMemberRoleEnum.MEMBER

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_likes_repo'].list_by_comment.return_value = [
        fake_community_member
    ]
    mock_services[
        'community_service'
    ]._map_member_to_response.return_value = fake_member_response

    # Act
    result = comment_service.list_likes_comment(fake_ids['comment_id'])

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories['comment_likes_repo'].list_by_comment.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_services['community_service']._map_member_to_response.assert_called_once_with(
        fake_community_member
    )
    assert result is not None
    assert len(result) == 1
    assert result[0].user_id == fake_ids['user_id']
    assert result[0].community_id == fake_ids['community_id']
    assert result[0].role == CommunityMemberRoleEnum.MEMBER


@pytest.mark.unit
def test_report_comment_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `report_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID below report threshold
    - When the service reports the comment
    - Then it should increment report count and maintain active status
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = 'Comment to report'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 2
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = 'Comment to report'
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 2
    fake_saved_comment.report_count = 1
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.report_comment(fake_ids['comment_id'])

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories['comment_repo'].save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.report_count == 1
    assert fake_existing_comment.status == CommentStatusEnum.ACTIVE
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.report_count == 1
    assert result.status == CommentStatusEnum.ACTIVE


@pytest.mark.unit
def test_report_comment_threshold_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `report_comment` method of CommentService when reaching threshold.

    Scenario:
    - Given a comment at report threshold minus one
    - When the service reports the comment
    - Then it should change status to reported when threshold is reached
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = 'Comment at threshold'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 1
    fake_existing_comment.report_count = REPORT_THRESHOLD - 1
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = 'Comment at threshold'
    fake_saved_comment.status = CommentStatusEnum.REPORTED
    fake_saved_comment.likes_count = 1
    fake_saved_comment.report_count = REPORT_THRESHOLD
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.report_comment(fake_ids['comment_id'])

    # Assert
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories['comment_repo'].save.assert_called_once()
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == str(fake_ids['comment_id'])
    assert result.status == CommentStatusEnum.REPORTED
    assert result.report_count == REPORT_THRESHOLD


@pytest.mark.unit
def test_list_comments_by_post_with_replies_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user, pagination_params
):
    """
    Tests the `list_comments_by_post` method of CommentService with replies included.

    Scenario:
    - Given a valid post ID with comments that have replies
    - When the service lists comments with include_replies=True
    - Then it should return comments with nested replies
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    # Mock main comment
    fake_main_comment = Mock(spec=Comment)
    fake_main_comment.id = fake_ids['comment_id']
    fake_main_comment.post_id = fake_ids['post_id']
    fake_main_comment.user_id = fake_ids['user_id']
    fake_main_comment.content = 'Main comment'
    fake_main_comment.status = CommentStatusEnum.ACTIVE
    fake_main_comment.likes_count = 2
    fake_main_comment.report_count = DEFAULT_REPORT_COUNT
    fake_main_comment.parent_id = None
    fake_main_comment.created_at = datetime.now(timezone.utc)
    fake_main_comment.post = fake_post
    fake_main_comment.user = fake_user

    # Mock reply comment
    fake_reply_comment = Mock(spec=Comment)
    fake_reply_comment.id = fake_ids['reply_id']
    fake_reply_comment.post_id = fake_ids['post_id']
    fake_reply_comment.user_id = fake_ids['user_id']
    fake_reply_comment.content = 'Reply comment'
    fake_reply_comment.status = CommentStatusEnum.ACTIVE
    fake_reply_comment.likes_count = 1
    fake_reply_comment.report_count = DEFAULT_REPORT_COUNT
    fake_reply_comment.parent_id = fake_ids['comment_id']
    fake_reply_comment.created_at = datetime.now(timezone.utc)
    fake_reply_comment.post = fake_post
    fake_reply_comment.user = fake_user

    # Setup pagination with status filter
    pagination_params.status = ['active']

    mock_repositories['comment_repo'].list_comments_by_post.return_value = (
        [fake_main_comment],
        1,
    )
    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Mock session query for replies - avoid recursion by returning empty on second call
    mock_session = Mock()
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    # First call returns the reply, second call (recursion) returns empty list
    mock_query.all.side_effect = [[fake_reply_comment], []]
    mock_session.query.return_value = mock_query
    mock_repositories['comment_repo'].session = mock_session

    # Act
    result = comment_service.list_comments_by_post(
        fake_ids['post_id'], pagination_params, include_replies=True
    )

    # Assert
    mock_repositories['post_repo'].get_by_id.assert_called_once_with(fake_ids['post_id'])
    mock_repositories['comment_repo'].list_comments_by_post.assert_called_once_with(
        fake_ids['post_id'], pagination_params
    )
    assert result is not None
    assert len(result.items) == 1
    assert str(result.items[0].id) == str(fake_ids['comment_id'])


@pytest.mark.unit
def test_list_comments_by_post_empty_result_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, pagination_params
):
    """
    Tests the `list_comments_by_post` method when no comments are found.

    Scenario:
    - Given a valid post ID with no comments
    - When the service lists comments with include_replies=True
    - Then it should return empty result
    """
    # Arrange
    mock_repositories['comment_repo'].list_comments_by_post.return_value = ([], 0)
    mock_repositories['post_repo'].get_by_id.return_value = fake_post

    # Act
    result = comment_service.list_comments_by_post(
        fake_ids['post_id'], pagination_params, include_replies=True
    )

    # Assert
    assert result.items == []
    assert result.total == 0
    assert result.has_more == False


@pytest.mark.unit
def test_get_like_service_success(comment_service, mock_repositories, fake_ids):
    """
    Tests the `get_like` method of CommentService.

    Scenario:
    - Given a valid comment ID and member ID with existing like
    - When the service gets the like
    - Then it should return the like object
    """
    # Arrange
    fake_like = Mock(spec=CommentLikes)
    fake_like.comment_id = fake_ids['comment_id']
    fake_like.member_id = fake_ids['member_id']

    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.return_value = fake_like

    # Act
    result = comment_service.get_like(fake_ids['comment_id'], fake_ids['member_id'])

    # Assert
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.assert_called_once_with(
        fake_ids['comment_id'], fake_ids['member_id']
    )
    assert result == fake_like


@pytest.mark.unit
def test_delete_comment_with_zero_comments_count_service_success(
    comment_service, mock_repositories, fake_ids
):
    """
    Tests the `delete_comment` method when post has zero comments count.

    Scenario:
    - Given a comment in a post with zero comments count
    - When the service deletes the comment
    - Then it should not decrement below zero
    """
    # Arrange
    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']

    fake_post = Mock(spec=Post)
    fake_post.id = fake_ids['post_id']
    fake_post.comments_count = 0

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].delete.return_value = True
    mock_repositories['post_repo'].get_by_id.return_value = fake_post

    # Act
    result = comment_service.delete_comment(fake_ids['comment_id'])

    # Assert
    assert fake_post.comments_count == 0
    assert result is True


@pytest.mark.unit
def test_unlike_comment_with_zero_likes_service_success(
    comment_service, mock_repositories, fake_ids, fake_post, fake_user
):
    """
    Tests the `unlike_comment` method when comment has zero likes.

    Scenario:
    - Given a comment with zero likes count
    - When the service unlikes the comment
    - Then it should not decrement below zero
    """
    # Arrange
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_ids['comment_id']
    fake_existing_comment.post_id = fake_ids['post_id']
    fake_existing_comment.user_id = fake_ids['user_id']
    fake_existing_comment.content = 'Comment to unlike'
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 0
    fake_existing_comment.report_count = DEFAULT_REPORT_COUNT
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)
    fake_existing_comment.post = fake_post
    fake_existing_comment.user = fake_user

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_ids['comment_id']
    fake_saved_comment.post_id = fake_ids['post_id']
    fake_saved_comment.user_id = fake_ids['user_id']
    fake_saved_comment.content = 'Comment to unlike'
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 0
    fake_saved_comment.report_count = DEFAULT_REPORT_COUNT
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)
    fake_saved_comment.post = fake_post
    fake_saved_comment.user = fake_user

    fake_existing_like = Mock(spec=CommentLikes)
    fake_existing_like.comment_id = fake_ids['comment_id']
    fake_existing_like.member_id = fake_ids['member_id']

    mock_repositories['comment_repo'].get_by_id.return_value = fake_existing_comment
    mock_repositories['comment_repo'].save.return_value = fake_saved_comment
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.return_value = fake_existing_like
    mock_repositories['comment_likes_repo'].delete.return_value = True
    mock_repositories['member_repo'].get_member_role.return_value = fake_member_role

    # Act
    result = comment_service.unlike_comment(
        fake_ids['comment_id'], fake_ids['member_id']
    )

    # Assert
    assert fake_existing_comment.likes_count == 0
    assert result is not None


# =============================================================================
# EXCEPTION HANDLER TESTS
# =============================================================================


@pytest.mark.unit
def test_create_comment_with_unexpected_error_raises_exception(
    comment_service, mock_repositories, fake_ids, fake_post
):
    """
    Tests that unexpected errors during comment creation raise UnexpectedCommentError.

    Scenario:
    - Given a valid comment creation request
    - When an unexpected error occurs during save
    - Then it should raise UnexpectedCommentError
    """
    # Arrange
    fake_comment_create = CommentCreate(
        post_id=fake_ids['post_id'],
        user_id=fake_ids['user_id'],
        content='Test comment',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['comment_repo'].save.side_effect = Exception('Database error')

    # Act & Assert
    with pytest.raises(UnexpectedCommentError):
        comment_service.create_comment(fake_comment_create)


@pytest.mark.unit
def test_update_comment_with_unexpected_error_raises_exception(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests that unexpected errors during comment update raise UnexpectedCommentError.

    Scenario:
    - Given a valid comment update request
    - When an unexpected error occurs during save
    - Then it should raise UnexpectedCommentError
    """
    # Arrange
    fake_comment_update = CommentUpdate(content='Updated content')

    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories['comment_repo'].save.side_effect = Exception('Database error')

    # Act & Assert
    with pytest.raises(UnexpectedCommentError):
        comment_service.update_comment(fake_ids['comment_id'], fake_comment_update)


@pytest.mark.unit
def test_delete_comment_with_unexpected_error_raises_exception(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests that unexpected errors during comment deletion raise UnexpectedCommentError.

    Scenario:
    - Given a valid comment deletion request
    - When an unexpected error occurs during deletion
    - Then it should raise UnexpectedCommentError
    """
    # Arrange
    fake_comment.post_id = fake_ids['post_id']

    fake_post = Mock(spec=Post)
    fake_post.comments_count = 1

    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['comment_repo'].delete.side_effect = Exception('Database error')

    # Act & Assert
    with pytest.raises(UnexpectedCommentError):
        comment_service.delete_comment(fake_ids['comment_id'])


@pytest.mark.unit
def test_like_comment_with_unexpected_error_raises_exception(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests that unexpected errors during comment like raise UnexpectedCommentError.

    Scenario:
    - Given a valid comment like request
    - When an unexpected error occurs during like save
    - Then it should raise UnexpectedCommentError
    """
    # Arrange
    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories['comment_likes_repo'].save.side_effect = Exception(
        'Database error'
    )

    # Act & Assert
    with pytest.raises(UnexpectedCommentError):
        comment_service.like_comment(fake_ids['comment_id'], fake_ids['member_id'])


@pytest.mark.unit
def test_unlike_comment_with_unexpected_error_raises_exception(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests that unexpected errors during comment unlike raise UnexpectedCommentError.

    Scenario:
    - Given a valid comment unlike request
    - When an unexpected error occurs during unlike
    - Then it should raise UnexpectedCommentError
    """
    # Arrange
    fake_like = Mock(spec=CommentLikes)

    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.return_value = fake_like
    mock_repositories['comment_likes_repo'].delete.side_effect = Exception(
        'Database error'
    )

    # Act & Assert
    with pytest.raises(UnexpectedCommentError):
        comment_service.unlike_comment(fake_ids['comment_id'], fake_ids['member_id'])


@pytest.mark.unit
def test_report_comment_with_unexpected_error_raises_exception(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests that unexpected errors during comment report raise UnexpectedCommentError.

    Scenario:
    - Given a valid comment report request
    - When an unexpected error occurs during report save
    - Then it should raise UnexpectedCommentError
    """
    # Arrange
    fake_comment.status = CommentStatusEnum.ACTIVE
    fake_comment.report_count = 1

    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories['comment_repo'].save.side_effect = Exception('Database error')

    # Act & Assert
    with pytest.raises(UnexpectedCommentError):
        comment_service.report_comment(fake_ids['comment_id'])


@pytest.mark.unit
def test_get_like_not_found_raises_exception(
    comment_service, mock_repositories, fake_ids
):
    """
    Tests that getting a non-existent like raises CommentLikesNotFoundError.

    Scenario:
    - Given comment and member IDs with no existing like
    - When the service attempts to get the like
    - Then it should raise CommentLikesNotFoundError
    """
    # Arrange
    mock_repositories['comment_likes_repo'].get_by_comment_and_member.return_value = None

    # Act & Assert
    with pytest.raises(CommentLikesNotFoundError):
        comment_service.get_like(fake_ids['comment_id'], fake_ids['member_id'])
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.assert_called_once_with(
        fake_ids['comment_id'], fake_ids['member_id']
    )


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


@pytest.mark.unit
def test_create_comment_with_nonexistent_post_raises_error(
    comment_service, mock_repositories, fake_ids
):
    """
    Tests that creating a comment with nonexistent post raises PostNotFoundError.

    Scenario:
    - Given a comment with non-existent post ID
    - When the service attempts to create the comment
    - Then it should raise PostNotFoundError
    """
    # Arrange
    fake_comment_create = CommentCreate(
        post_id=fake_ids['post_id'],
        user_id=fake_ids['user_id'],
        content='Comment with nonexistent post',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    mock_repositories['post_repo'].get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(PostNotFoundError):
        comment_service.create_comment(fake_comment_create)

    mock_repositories['post_repo'].get_by_id.assert_called_once_with(fake_ids['post_id'])


@pytest.mark.unit
def test_create_comment_with_nonexistent_parent_raises_error(
    comment_service, mock_repositories, fake_ids, fake_post
):
    """
    Tests that creating a reply with nonexistent parent raises CommentNotFoundError.

    Scenario:
    - Given a comment with non-existent parent comment ID
    - When the service attempts to create the reply
    - Then it should raise CommentNotFoundError
    """
    # Arrange
    fake_comment_create = CommentCreate(
        post_id=fake_ids['post_id'],
        user_id=fake_ids['user_id'],
        content='Reply with nonexistent parent',
        parent_id=fake_ids['parent_id'],
        status=CommentStatusEnum.ACTIVE,
    )

    mock_repositories['post_repo'].get_by_id.return_value = fake_post
    mock_repositories['comment_repo'].get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(CommentNotFoundError):
        comment_service.create_comment(fake_comment_create)

    mock_repositories['post_repo'].get_by_id.assert_called_once_with(fake_ids['post_id'])
    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['parent_id']
    )


@pytest.mark.unit
def test_get_nonexistent_comment_raises_error(
    comment_service, mock_repositories, fake_ids
):
    """
    Tests that getting a nonexistent comment raises CommentNotFoundError.

    Scenario:
    - Given a non-existent comment ID
    - When the service attempts to get the comment
    - Then it should raise CommentNotFoundError
    """
    # Arrange
    mock_repositories['comment_repo'].get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(CommentNotFoundError):
        comment_service.get_comment(fake_ids['comment_id'])

    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )


@pytest.mark.unit
def test_unlike_comment_without_like_raises_error(
    comment_service, mock_repositories, fake_ids, fake_comment
):
    """
    Tests that unliking a comment without previous like raises CommentLikesNotFoundError.

    Scenario:
    - Given a comment that user has not liked
    - When the service attempts to unlike the comment
    - Then it should raise CommentLikesNotFoundError
    """
    # Arrange
    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment
    mock_repositories['comment_likes_repo'].get_by_comment_and_member.return_value = None

    # Act & Assert
    with pytest.raises(CommentLikesNotFoundError):
        comment_service.unlike_comment(fake_ids['comment_id'], fake_ids['member_id'])

    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
    mock_repositories[
        'comment_likes_repo'
    ].get_by_comment_and_member.assert_called_once_with(
        fake_ids['comment_id'], fake_ids['member_id']
    )


@pytest.mark.unit
def test_report_suspended_comment_raises_error(
    comment_service, mock_repositories, fake_ids
):
    """
    Tests that reporting a suspended comment raises CommentSuspendedError.

    Scenario:
    - Given a comment with suspended status
    - When the service attempts to report the comment
    - Then it should raise CommentSuspendedError
    """
    # Arrange
    fake_comment = Mock(spec=Comment)
    fake_comment.status = CommentStatusEnum.SUSPENDED

    mock_repositories['comment_repo'].get_by_id.return_value = fake_comment

    # Act & Assert
    with pytest.raises(CommentSuspendedError):
        comment_service.report_comment(fake_ids['comment_id'])

    mock_repositories['comment_repo'].get_by_id.assert_called_once_with(
        fake_ids['comment_id']
    )
