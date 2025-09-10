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
from app.api.comment.exceptions import CommentSuspendedError, CommentNotFoundError, CommentLikesNotFoundError
from app.api.post.exceptions import PostNotFoundError
from app.api.users.model import User
from app.api.post.model import Post
from app.api.communities.model import CommunityMember
from app.api.communities.schema import CommunityMemberResponse, CommunityMemberRoleEnum
from app.utils.schema import PaginationSearchParams


@pytest.mark.unit
def test_create_comment_service_success():
    """
    Tests the `create_comment` method of CommentService.

    Scenario:
    - Given a valid comment creation request
    - When the service creates the comment and saves it to repository
    - Then it should return the created comment with mapped response
    """
    # Arrange
    fake_comment_id = uuid4()
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_content = "Test comment content"
    fake_status = CommentStatusEnum.ACTIVE
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment_create = CommentCreate(
        post_id=fake_post_id,
        user_id=fake_user_id,
        content=fake_content,
        parent_id=None,
        status=fake_status,
    )

    fake_created_comment = Mock(spec=Comment)
    fake_created_comment.id = fake_comment_id
    fake_created_comment.post_id = fake_post_id
    fake_created_comment.user_id = fake_user_id
    fake_created_comment.content = fake_content
    fake_created_comment.parent_id = None
    fake_created_comment.status = fake_status
    fake_created_comment.likes_count = 0
    fake_created_comment.report_count = 0
    fake_created_comment.created_at = datetime.now(timezone.utc)

    # Mock objects
    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.title = "Test Post"
    fake_post.community_id = fake_community_id
    fake_post.comments_count = 0
    fake_created_comment.post = fake_post

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = "Test User"
    fake_user.profile_image_url = "https://example.com/profile.jpg"
    fake_created_comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.save.return_value = fake_created_comment

    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_post

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    mock_community_service = Mock()

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.post_repo = mock_post_repo
    service.member_repo = mock_member_repo
    service.community_service = mock_community_service

    # Act
    result = service.create_comment(fake_comment_create)

    # Assert
    # The service calls get_by_id twice: once for validation, once to increment comments_count
    assert mock_post_repo.get_by_id.call_count == 2
    mock_post_repo.get_by_id.assert_called_with(fake_post_id)  # Check last call was correct
    mock_comment_repo.save.assert_called_once()
    mock_post_repo.save.assert_called_once_with(fake_post)
    mock_member_repo.get_member_role.assert_called_once_with(fake_user_id, fake_community_id)
    assert fake_post.comments_count == 1
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert result.id == fake_comment_id
    assert str(result.post.id) == fake_post_id
    assert str(result.user.id) == fake_user_id
    assert result.content == fake_content
    assert result.status == fake_status
    assert result.likes_count == 0
    assert result.report_count == 0
    assert result.parent_id is None
    assert result.user.member_role == fake_member_role


@pytest.mark.unit
def test_create_comment_reply_service_success():
    """
    Tests the `create_comment` method of CommentService for creating replies.

    Scenario:
    - Given a valid reply comment creation request with parent
    - When the service creates the reply comment
    - Then it should return the created reply linked to parent comment
    """
    # Arrange
    fake_comment_id = uuid4()
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_parent_id = str(uuid4())
    fake_content = "Test reply content"
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment_create = CommentCreate(
        post_id=fake_post_id,
        user_id=fake_user_id,
        content=fake_content,
        parent_id=fake_parent_id,
        status=CommentStatusEnum.ACTIVE,
    )

    fake_parent_comment = Mock(spec=Comment)
    fake_parent_comment.id = fake_parent_id
    fake_parent_comment.post_id = fake_post_id
    fake_parent_comment.parent_id = None

    fake_created_reply = Mock(spec=Comment)
    fake_created_reply.id = fake_comment_id
    fake_created_reply.post_id = fake_post_id
    fake_created_reply.user_id = fake_user_id
    fake_created_reply.content = fake_content
    fake_created_reply.parent_id = fake_parent_id
    fake_created_reply.status = CommentStatusEnum.ACTIVE
    fake_created_reply.likes_count = 0
    fake_created_reply.report_count = 0
    fake_created_reply.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos
    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.title = "Test Post"
    fake_post.community_id = fake_community_id
    fake_post.comments_count = 1
    fake_created_reply.post = fake_post

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = "Reply User"
    fake_user.profile_image_url = "https://example.com/profile.jpg"
    fake_created_reply.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_parent_comment
    mock_comment_repo.save.return_value = fake_created_reply

    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_post

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    mock_community_service = Mock()

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.post_repo = mock_post_repo
    service.member_repo = mock_member_repo
    service.community_service = mock_community_service

    # Act
    result = service.create_comment(fake_comment_create)

    # Assert
    # The service calls get_by_id twice: once for validation, once to increment comments_count
    assert mock_post_repo.get_by_id.call_count == 2
    mock_post_repo.get_by_id.assert_called_with(fake_post_id)  # Check last call was correct
    mock_comment_repo.get_by_id.assert_called_once_with(fake_parent_id)
    mock_comment_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert result.id == fake_comment_id
    assert str(result.parent_id) == fake_parent_id
    assert result.content == fake_content


@pytest.mark.unit
def test_get_comment_by_id_service_success():
    """
    Tests the `get_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID
    - When the service retrieves the comment from repository
    - Then it should return the expected comment response
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_content = "Test comment content"
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment = Mock(spec=Comment)
    fake_comment.id = fake_comment_id
    fake_comment.post_id = fake_post_id
    fake_comment.user_id = fake_user_id
    fake_comment.content = fake_content
    fake_comment.status = CommentStatusEnum.ACTIVE
    fake_comment.likes_count = 3
    fake_comment.report_count = 0
    fake_comment.parent_id = None
    fake_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos
    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.title = "Test Post"
    fake_post.community_id = fake_community_id
    fake_comment.post = fake_post

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = "Test User"
    fake_user.profile_image_url = "https://example.com/profile.jpg"
    fake_comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_comment

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.get_comment(fake_comment_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.content == fake_content
    assert str(result.user.id) == fake_user_id
    assert str(result.post.id) == fake_post_id
    assert result.status == CommentStatusEnum.ACTIVE
    assert result.likes_count == 3
    assert result.report_count == 0


@pytest.mark.unit
def test_list_comments_by_post_service_success():
    """
    Tests the `list_comments_by_post` method of CommentService.

    Scenario:
    - Given a valid post ID and pagination parameters
    - When the service lists comments by post from repository
    - Then it should return a paginated response with the expected comments
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_comment_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment = Mock(spec=Comment)
    fake_comment.id = fake_comment_id
    fake_comment.post_id = fake_post_id
    fake_comment.user_id = fake_user_id
    fake_comment.content = "Test comment content"
    fake_comment.status = CommentStatusEnum.ACTIVE
    fake_comment.likes_count = 5
    fake_comment.report_count = 1
    fake_comment.parent_id = None
    fake_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos
    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.title = "Test Post"
    fake_post.community_id = fake_community_id
    fake_comment.post = fake_post

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = "Comment User"
    fake_user.profile_image_url = "https://example.com/profile.jpg"
    fake_comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.list_comments_by_post.return_value = ([fake_comment], 1)

    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_post

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.post_repo = mock_post_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.list_comments_by_post(fake_post_id, fake_pagination_params, include_replies=False)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_comment_repo.list_comments_by_post.assert_called_once_with(fake_post_id, fake_pagination_params)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert str(result.items[0].post.id) == fake_post_id
    assert str(result.items[0].id) == fake_comment_id
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_comments_by_user_service_success():
    """
    Tests the `list_comments_by_user` method of CommentService.

    Scenario:
    - Given a valid user ID and pagination parameters
    - When the service lists comments by user from repository
    - Then it should return a paginated response with the expected comments
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_comment_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment = Mock(spec=Comment)
    fake_comment.id = fake_comment_id
    fake_comment.post_id = fake_post_id
    fake_comment.user_id = fake_user_id
    fake_comment.content = "User comment content"
    fake_comment.parent_id = None
    fake_comment.status = CommentStatusEnum.ACTIVE
    fake_comment.likes_count = 3
    fake_comment.report_count = 0
    fake_comment.parent_id = None
    fake_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos
    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.title = "User Post"
    fake_post.community_id = fake_community_id
    fake_comment.post = fake_post

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = "Test User"
    fake_user.profile_image_url = "https://example.com/profile.jpg"
    fake_comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.list_comments_by_user.return_value = ([fake_comment], 1)

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.list_comments_by_user(fake_user_id, fake_pagination_params)

    # Assert
    mock_comment_repo.list_comments_by_user.assert_called_once_with(fake_user_id, fake_pagination_params)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert str(result.items[0].user.id) == fake_user_id
    assert str(result.items[0].id) == fake_comment_id
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_replies_by_parent_service_success():
    """
    Tests the `list_replies_by_parent` method of CommentService.

    Scenario:
    - Given a valid parent comment ID and pagination parameters
    - When the service lists replies by parent from repository
    - Then it should return a paginated response with the expected replies
    """
    # Arrange
    fake_parent_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_reply_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_parent_comment = Mock(spec=Comment)
    fake_parent_comment.id = fake_parent_id
    fake_parent_comment.parent_id = None

    fake_reply = Mock(spec=Comment)
    fake_reply.id = fake_reply_id
    fake_reply.post_id = fake_post_id
    fake_reply.user_id = fake_user_id
    fake_reply.content = "Test reply content"
    fake_reply.parent_id = fake_parent_id
    fake_reply.status = CommentStatusEnum.ACTIVE
    fake_reply.likes_count = 1
    fake_reply.report_count = 0
    fake_reply.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos
    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.title = "Reply Post"
    fake_post.community_id = fake_community_id
    fake_reply.post = fake_post

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = "Reply User"
    fake_user.profile_image_url = "https://example.com/profile.jpg"
    fake_reply.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_parent_comment
    mock_comment_repo.list_replies_by_parent.return_value = ([fake_reply], 1)

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.list_replies_by_parent(fake_parent_id, fake_pagination_params)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_parent_id)
    mock_comment_repo.list_replies_by_parent.assert_called_once_with(fake_parent_id, fake_pagination_params)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert str(result.items[0].parent_id) == fake_parent_id
    assert str(result.items[0].id) == fake_reply_id
    assert result.total == 1


@pytest.mark.unit
def test_update_comment_content_service_success():
    """
    Tests the `update_comment` method of CommentService for content updates.

    Scenario:
    - Given a valid comment ID and update data
    - When the service updates the comment content and saves it to repository
    - Then it should return the updated comment response
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_original_content = "Original content"
    fake_updated_content = "Updated content"
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_comment_update = CommentUpdate(content=fake_updated_content)

    # Mock do comentário original
    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.user_id = fake_user_id
    fake_existing_comment.content = fake_original_content
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 2
    fake_existing_comment.report_count = 0
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    # Mock do comentário atualizado (retornado após save)
    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_comment_id
    fake_saved_comment.post_id = fake_post_id
    fake_saved_comment.user_id = fake_user_id
    fake_saved_comment.content = fake_updated_content  # Conteúdo atualizado
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 2
    fake_saved_comment.report_count = 0
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos para ambos os comentários
    for comment in [fake_existing_comment, fake_saved_comment]:
        fake_post = Mock(spec=Post)
        fake_post.id = fake_post_id
        fake_post.title = "Test Post"
        fake_post.community_id = fake_community_id
        comment.post = fake_post

        fake_user = Mock(spec=User)
        fake_user.id = fake_user_id
        fake_user.name = "Test User"
        fake_user.profile_image_url = "https://example.com/profile.jpg"
        comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    # Primeira chamada (_get_comment) retorna comentário original, segunda chamada retorna comentário atualizado
    mock_comment_repo.get_by_id.side_effect = [fake_existing_comment, fake_saved_comment]
    mock_comment_repo.save.return_value = fake_saved_comment

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.update_comment(fake_comment_id, fake_comment_update)

    # Assert
    assert mock_comment_repo.get_by_id.call_count == 2  # Chamado duas vezes
    mock_comment_repo.save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.content == fake_updated_content  # Conteúdo foi atualizado no objeto
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.content == fake_updated_content


@pytest.mark.unit
def test_update_comment_status_service_success():
    """
    Tests the `update_comment` method of CommentService for status updates.

    Scenario:
    - Given a valid comment ID and status update data
    - When the service updates the comment status and saves it to repository
    - Then it should return the updated comment with new status
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_role = CommunityMemberRoleEnum.MEMBER
    fake_comment_update = CommentUpdate(status=CommentStatusEnum.SUSPENDED)

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.user_id = fake_user_id
    fake_existing_comment.content = "Test content"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 1
    fake_existing_comment.report_count = 0
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_comment_id
    fake_saved_comment.post_id = fake_post_id
    fake_saved_comment.user_id = fake_user_id
    fake_saved_comment.content = "Test content"
    fake_saved_comment.status = CommentStatusEnum.SUSPENDED  # Status atualizado
    fake_saved_comment.likes_count = 1
    fake_saved_comment.report_count = 0
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos para ambos os comentários
    for comment in [fake_existing_comment, fake_saved_comment]:
        fake_post = Mock(spec=Post)
        fake_post.id = fake_post_id
        fake_post.title = "Test Post"
        fake_post.community_id = fake_community_id
        comment.post = fake_post

        fake_user = Mock(spec=User)
        fake_user.id = fake_user_id
        fake_user.name = "Test User"
        fake_user.profile_image_url = "https://example.com/profile.jpg"
        comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.side_effect = [fake_existing_comment, fake_saved_comment]
    mock_comment_repo.save.return_value = fake_saved_comment

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.update_comment(fake_comment_id, fake_comment_update)

    # Assert
    assert mock_comment_repo.get_by_id.call_count == 2
    mock_comment_repo.save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.status == CommentStatusEnum.SUSPENDED  # Status foi atualizado no objeto
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.status == CommentStatusEnum.SUSPENDED


@pytest.mark.unit
def test_delete_comment_service_success():
    """
    Tests the `delete_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID
    - When the service deletes the comment from repository
    - Then it should return True and decrement post comments count
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_post_id = str(uuid4())

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.content = "Comment to delete"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 5
    fake_existing_comment.report_count = 1
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.comments_count = 5  # Começando com 5 comentários

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_existing_comment
    mock_comment_repo.delete.return_value = True

    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_post

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.post_repo = mock_post_repo

    # Act
    result = service.delete_comment(fake_comment_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_comment_repo.delete.assert_called_once_with(fake_existing_comment)
    mock_post_repo.save.assert_called_once_with(fake_post)
    assert fake_post.comments_count == 4  # Verificar que foi decrementado
    assert result is True


@pytest.mark.unit
def test_like_comment_service_success():
    """
    Tests the `like_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID and member ID
    - When the service likes the comment and saves the like to repository
    - Then it should return the comment with incremented likes count
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_member_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.user_id = fake_user_id
    fake_existing_comment.content = "Comment to like"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 0
    fake_existing_comment.report_count = 0
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_comment_id
    fake_saved_comment.post_id = fake_post_id
    fake_saved_comment.user_id = fake_user_id
    fake_saved_comment.content = "Comment to like"
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 1  # Incrementado após like
    fake_saved_comment.report_count = 0
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos para ambos os comentários
    for comment in [fake_existing_comment, fake_saved_comment]:
        fake_post = Mock(spec=Post)
        fake_post.id = fake_post_id
        fake_post.title = "Test Post"
        fake_post.community_id = fake_community_id
        comment.post = fake_post

        fake_user = Mock(spec=User)
        fake_user.id = fake_user_id
        fake_user.name = "Test User"
        fake_user.profile_image_url = "https://example.com/profile.jpg"
        comment.user = fake_user

    fake_comment_like = Mock(spec=CommentLikes)
    fake_comment_like.comment_id = fake_comment_id
    fake_comment_like.member_id = fake_member_id

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_existing_comment
    mock_comment_repo.save.return_value = fake_saved_comment

    mock_comment_likes_repo = Mock()
    mock_comment_likes_repo.save.return_value = fake_comment_like

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.comment_likes_repo = mock_comment_likes_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.like_comment(fake_comment_id, fake_member_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_comment_likes_repo.save.assert_called_once()
    mock_comment_repo.save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.likes_count == 1  # Verificar que foi incrementado
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.likes_count == 1
    assert result.content == "Comment to like"


@pytest.mark.unit
def test_unlike_comment_service_success():
    """
    Tests the `unlike_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID and member ID with an existing like
    - When the service unlikes the comment and removes the like from repository
    - Then it should return the comment with decremented likes count
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_member_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.user_id = fake_user_id
    fake_existing_comment.content = "Comment to unlike"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 1  # Tem 1 like que será removido
    fake_existing_comment.report_count = 0
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_comment_id
    fake_saved_comment.post_id = fake_post_id
    fake_saved_comment.user_id = fake_user_id
    fake_saved_comment.content = "Comment to unlike"
    fake_saved_comment.status = CommentStatusEnum.ACTIVE
    fake_saved_comment.likes_count = 0  # Decrementado após unlike
    fake_saved_comment.report_count = 0
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos para ambos os comentários
    for comment in [fake_existing_comment, fake_saved_comment]:
        fake_post = Mock(spec=Post)
        fake_post.id = fake_post_id
        fake_post.title = "Test Post"
        fake_post.community_id = fake_community_id
        comment.post = fake_post

        fake_user = Mock(spec=User)
        fake_user.id = fake_user_id
        fake_user.name = "Test User"
        fake_user.profile_image_url = "https://example.com/profile.jpg"
        comment.user = fake_user

    fake_existing_like = Mock(spec=CommentLikes)
    fake_existing_like.comment_id = fake_comment_id
    fake_existing_like.member_id = fake_member_id

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_existing_comment
    mock_comment_repo.save.return_value = fake_saved_comment

    mock_comment_likes_repo = Mock()
    mock_comment_likes_repo.get_by_comment_and_member.return_value = fake_existing_like
    mock_comment_likes_repo.delete.return_value = True

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.comment_likes_repo = mock_comment_likes_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.unlike_comment(fake_comment_id, fake_member_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_comment_likes_repo.get_by_comment_and_member.assert_called_once_with(fake_comment_id, fake_member_id)
    mock_comment_likes_repo.delete.assert_called_once_with(fake_existing_like)
    mock_comment_repo.save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.likes_count == 0  # Verificar que foi decrementado
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.likes_count == 0
    assert result.content == "Comment to unlike"


@pytest.mark.unit
def test_list_likes_comment_service_success():
    """
    Tests the `list_likes_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID with existing likes
    - When the service lists members who liked the comment
    - Then it should return a list of community member responses
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_member_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.content = "Comment with likes"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 3
    fake_existing_comment.report_count = 0
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    # Mock do membro da comunidade que curtiu
    fake_community_member = Mock(spec=CommunityMember)
    fake_community_member.id = fake_member_id
    fake_community_member.user_id = fake_user_id
    fake_community_member.community_id = fake_community_id
    fake_community_member.role = CommunityMemberRoleEnum.MEMBER
    fake_community_member.status_participation = "active"

    # Mock da resposta do membro
    fake_member_response = Mock(spec=CommunityMemberResponse)
    fake_member_response.user_id = fake_user_id
    fake_member_response.community_id = fake_community_id
    fake_member_response.role = CommunityMemberRoleEnum.MEMBER

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_existing_comment

    mock_comment_likes_repo = Mock()
    mock_comment_likes_repo.list_by_comment.return_value = [fake_community_member]

    mock_community_service = Mock()
    mock_community_service._map_member_to_response.return_value = fake_member_response

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.comment_likes_repo = mock_comment_likes_repo
    service.community_service = mock_community_service

    # Act
    result = service.list_likes_comment(fake_comment_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_comment_likes_repo.list_by_comment.assert_called_once_with(fake_comment_id)
    mock_community_service._map_member_to_response.assert_called_once_with(fake_community_member)
    assert result is not None
    assert len(result) == 1
    assert result[0].user_id == fake_user_id
    assert result[0].community_id == fake_community_id
    assert result[0].role == CommunityMemberRoleEnum.MEMBER


@pytest.mark.unit
def test_report_comment_service_success():
    """
    Tests the `report_comment` method of CommentService.

    Scenario:
    - Given a valid comment ID below report threshold
    - When the service reports the comment
    - Then it should increment report count and maintain active status
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.user_id = fake_user_id
    fake_existing_comment.content = "Comment to report"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 2
    fake_existing_comment.report_count = 0  # Inicial
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_comment_id
    fake_saved_comment.post_id = fake_post_id
    fake_saved_comment.user_id = fake_user_id
    fake_saved_comment.content = "Comment to report"
    fake_saved_comment.status = CommentStatusEnum.ACTIVE  # Ainda ativo
    fake_saved_comment.likes_count = 2
    fake_saved_comment.report_count = 1  # Incrementado após report
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos para ambos os comentários
    for comment in [fake_existing_comment, fake_saved_comment]:
        fake_post = Mock(spec=Post)
        fake_post.id = fake_post_id
        fake_post.title = "Test Post"
        fake_post.community_id = fake_community_id
        comment.post = fake_post

        fake_user = Mock(spec=User)
        fake_user.id = fake_user_id
        fake_user.name = "Test User"
        fake_user.profile_image_url = "https://example.com/profile.jpg"
        comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_existing_comment
    mock_comment_repo.save.return_value = fake_saved_comment

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.report_comment(fake_comment_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_comment_repo.save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.report_count == 1  # Verificar que foi incrementado
    assert fake_existing_comment.status == CommentStatusEnum.ACTIVE  # Ainda ativo
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.report_count == 1
    assert result.status == CommentStatusEnum.ACTIVE


@pytest.mark.unit
def test_report_comment_threshold_service_success():
    """
    Tests the `report_comment` method of CommentService when reaching threshold.

    Scenario:
    - Given a comment at report threshold minus one
    - When the service reports the comment
    - Then it should change status to reported when threshold is reached
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_role = CommunityMemberRoleEnum.MEMBER

    # Set report count to threshold - 1 (threshold is 10 according to service)
    fake_existing_comment = Mock(spec=Comment)
    fake_existing_comment.id = fake_comment_id
    fake_existing_comment.post_id = fake_post_id
    fake_existing_comment.user_id = fake_user_id
    fake_existing_comment.content = "Comment at threshold"
    fake_existing_comment.status = CommentStatusEnum.ACTIVE
    fake_existing_comment.likes_count = 1
    fake_existing_comment.report_count = 9  # Um antes do threshold
    fake_existing_comment.parent_id = None
    fake_existing_comment.created_at = datetime.now(timezone.utc)

    fake_saved_comment = Mock(spec=Comment)
    fake_saved_comment.id = fake_comment_id
    fake_saved_comment.post_id = fake_post_id
    fake_saved_comment.user_id = fake_user_id
    fake_saved_comment.content = "Comment at threshold"
    fake_saved_comment.status = CommentStatusEnum.REPORTED  # Mudou para reported
    fake_saved_comment.likes_count = 1
    fake_saved_comment.report_count = 10  # Atingiu o threshold
    fake_saved_comment.parent_id = None
    fake_saved_comment.created_at = datetime.now(timezone.utc)

    # Mock relacionamentos para ambos os comentários
    for comment in [fake_existing_comment, fake_saved_comment]:
        fake_post = Mock(spec=Post)
        fake_post.id = fake_post_id
        fake_post.title = "Test Post"
        fake_post.community_id = fake_community_id
        comment.post = fake_post

        fake_user = Mock(spec=User)
        fake_user.id = fake_user_id
        fake_user.name = "Test User"
        fake_user.profile_image_url = "https://example.com/profile.jpg"
        comment.user = fake_user

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_existing_comment
    mock_comment_repo.save.return_value = fake_saved_comment

    mock_member_repo = Mock()
    mock_member_repo.get_member_role.return_value = fake_member_role

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.member_repo = mock_member_repo

    # Act
    result = service.report_comment(fake_comment_id)

    # Assert
    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_comment_repo.save.assert_called_once_with(fake_existing_comment)
    assert fake_existing_comment.report_count == 10  # Atingiu o threshold
    assert fake_existing_comment.status == CommentStatusEnum.REPORTED  # Status mudou
    assert result is not None
    assert isinstance(result, CommentResponse)
    assert str(result.id) == fake_comment_id
    assert result.report_count == 10
    assert result.status == CommentStatusEnum.REPORTED


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

@pytest.mark.unit
def test_create_comment_with_nonexistent_post_raises_error():
    """
    Tests that creating a comment with nonexistent post raises PostNotFoundError.

    Scenario:
    - Given a comment with non-existent post ID
    - When the service attempts to create the comment
    - Then it should raise PostNotFoundError
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())

    fake_comment_create = CommentCreate(
        post_id=fake_post_id,
        user_id=fake_user_id,
        content="Comment with nonexistent post",
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = None  # Post not found

    service = CommentService(mock_tm)
    service.post_repo = mock_post_repo

    # Act & Assert
    with pytest.raises(PostNotFoundError):
        service.create_comment(fake_comment_create)

    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)


@pytest.mark.unit
def test_create_comment_with_nonexistent_parent_raises_error():
    """
    Tests that creating a reply with nonexistent parent raises CommentNotFoundError.

    Scenario:
    - Given a comment with non-existent parent comment ID
    - When the service attempts to create the reply
    - Then it should raise CommentNotFoundError
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_parent_id = str(uuid4())

    fake_comment_create = CommentCreate(
        post_id=fake_post_id,
        user_id=fake_user_id,
        content="Reply with nonexistent parent",
        parent_id=fake_parent_id,
        status=CommentStatusEnum.ACTIVE,
    )

    fake_post = Mock(spec=Post)

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_post  # Post exists

    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = None  # Parent comment not found

    service = CommentService(mock_tm)
    service.post_repo = mock_post_repo
    service.comment_repo = mock_comment_repo

    # Act & Assert
    with pytest.raises(CommentNotFoundError):
        service.create_comment(fake_comment_create)

    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_comment_repo.get_by_id.assert_called_once_with(fake_parent_id)


@pytest.mark.unit
def test_get_nonexistent_comment_raises_error():
    """
    Tests that getting a nonexistent comment raises CommentNotFoundError.

    Scenario:
    - Given a non-existent comment ID
    - When the service attempts to get the comment
    - Then it should raise CommentNotFoundError
    """
    # Arrange
    fake_comment_id = str(uuid4())

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = None

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo

    # Act & Assert
    with pytest.raises(CommentNotFoundError):
        service.get_comment(fake_comment_id)

    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)


@pytest.mark.unit
def test_unlike_comment_without_like_raises_error():
    """
    Tests that unliking a comment without previous like raises CommentLikesNotFoundError.

    Scenario:
    - Given a comment that user has not liked
    - When the service attempts to unlike the comment
    - Then it should raise CommentLikesNotFoundError
    """
    # Arrange
    fake_comment_id = str(uuid4())
    fake_member_id = str(uuid4())

    fake_comment = Mock(spec=Comment)

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_comment  # Comment exists

    mock_comment_likes_repo = Mock()
    mock_comment_likes_repo.get_by_comment_and_member.return_value = None  # Like not found

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo
    service.comment_likes_repo = mock_comment_likes_repo

    # Act & Assert
    with pytest.raises(CommentLikesNotFoundError):
        service.unlike_comment(fake_comment_id, fake_member_id)

    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
    mock_comment_likes_repo.get_by_comment_and_member.assert_called_once_with(fake_comment_id, fake_member_id)


@pytest.mark.unit
def test_report_suspended_comment_raises_error():
    """
    Tests that reporting a suspended comment raises CommentSuspendedError.

    Scenario:
    - Given a comment with suspended status
    - When the service attempts to report the comment
    - Then it should raise CommentSuspendedError
    """
    # Arrange
    fake_comment_id = str(uuid4())

    fake_comment = Mock(spec=Comment)
    fake_comment.status = CommentStatusEnum.SUSPENDED

    mock_tm = Mock()
    mock_comment_repo = Mock()
    mock_comment_repo.get_by_id.return_value = fake_comment

    service = CommentService(mock_tm)
    service.comment_repo = mock_comment_repo

    # Act & Assert
    with pytest.raises(CommentSuspendedError):
        service.report_comment(fake_comment_id)

    mock_comment_repo.get_by_id.assert_called_once_with(fake_comment_id)
