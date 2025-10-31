from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.api.communities.schema import CommunityMemberRoleEnum
from app.api.post.exceptions import ComplaintNotFoundError, PostSuspendedError
from app.api.post.model import CampaignPost, ComplaintPost, PollOptions, PollPosts, Post
from app.api.post.schemas import (
    CampaignStatusEnum,
    CommunityRelated,
    ComplaintLevelEnum,
    ComplaintResponse,
    ComplaintStatusEnum,
    PollCreate,
    PostAuthor,
    PostCreate,
    PostResponse,
    PostStatusEnum,
    PostTypeEnum,
    PostUpdate,
)
from app.api.post.service import PostService
from app.utils.schema import PaginationSearchParams


@pytest.mark.unit
def test_create_post_service_success():
    """
    Tests the `create_post` method of PostService.

    Scenario:
    - Given a valid post creation request
    - When the service creates the post and saves it to repository
    - Then it should return the created post with mapped response
    """
    # Arrange
    fake_post_id = uuid4()
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_title = 'Test Post Title'
    fake_content = 'Test post content'
    fake_type_post = PostTypeEnum.ANNOUNCEMENT
    fake_image_url = 'https://example.com/image.jpg'
    fake_status = PostStatusEnum.ACTIVE
    fake_role = CommunityMemberRoleEnum.MEMBER

    fake_post_create = PostCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        title=fake_title,
        content=fake_content,
        type_post=fake_type_post,
        image_url=fake_image_url,
        status=fake_status,
    )

    fake_created_post = Mock(spec=Post)
    fake_created_post.id = fake_post_id
    fake_created_post.user_id = fake_user_id
    fake_created_post.community_id = fake_community_id
    fake_created_post.title = fake_title
    fake_created_post.content = fake_content
    fake_created_post.type_post = fake_type_post
    fake_created_post.image_url = fake_image_url
    fake_created_post.status = fake_status
    fake_created_post.user_role_in_community = fake_role
    fake_created_post.likes_count = 0
    fake_created_post.comments_count = 0
    fake_created_post.report_count = 0
    fake_created_post.created_at = '2024-01-01T00:00:00Z'
    fake_created_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock objects
    fake_community = Mock()
    fake_community.name = 'Test Community'
    fake_created_post.community = fake_community

    fake_user = Mock()
    fake_user.name = 'Test User'
    fake_user.profile_image_url = 'https://example.com/profile.jpg'
    fake_created_post.user = fake_user

    fake_member_association = Mock()
    fake_member_association.role = fake_role

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.save.return_value = fake_created_post

    mock_community_service = Mock()
    mock_community_service.get_member_association.return_value = fake_member_association

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo
    service.community_service = mock_community_service

    # Act
    result = service.create_post(fake_post_create)

    # Assert
    mock_community_service.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    mock_post_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, PostResponse)
    assert result.id == fake_post_id
    assert str(result.user.id) == fake_user_id
    assert str(result.community.id) == fake_community_id
    assert result.title == fake_title
    assert result.content == fake_content
    assert result.type_post == fake_type_post
    assert result.image_url == fake_image_url
    assert result.status == fake_status
    assert result.user.role == fake_role
    assert result.likes_count == 0
    assert result.comments_count == 0
    assert result.report_count == 0


@pytest.mark.unit
def test_get_post_by_id_service_success():
    """
    Tests the `get_post` method of PostService.

    Scenario:
    - Given a valid post ID
    - When the service retrieves the post from repository
    - Then it should return the expected post response
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_title = 'Test Post Title'
    fake_content = 'Test post content'
    fake_type_post = PostTypeEnum.ANNOUNCEMENT
    fake_role = CommunityMemberRoleEnum.MEMBER

    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.user_id = fake_user_id
    fake_post.community_id = fake_community_id
    fake_post.title = fake_title
    fake_post.content = fake_content
    fake_post.type_post = fake_type_post
    fake_post.image_url = 'https://example.com/image.jpg'
    fake_post.status = PostStatusEnum.ACTIVE
    fake_post.user_role_in_community = fake_role
    fake_post.likes_count = 5
    fake_post.comments_count = 3
    fake_post.report_count = 0
    fake_post.created_at = '2024-01-01T00:00:00Z'
    fake_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos
    fake_community = Mock()
    fake_community.name = 'Test Community'
    fake_post.community = fake_community

    fake_user = Mock()
    fake_user.name = 'Test User'
    fake_user.profile_image_url = 'https://example.com/profile.jpg'
    fake_post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_post

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.get_post(fake_post_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    assert result is not None
    assert isinstance(result, PostResponse)
    assert str(result.id) == fake_post_id
    assert result.title == fake_title
    assert result.content == fake_content
    assert str(result.user.id) == fake_user_id
    assert result.user.role == fake_role
    assert str(result.community.id) == fake_community_id
    assert result.likes_count == 5
    assert result.comments_count == 3
    assert result.report_count == 0


@pytest.mark.unit
def test_list_posts_by_user_service_success():
    """
    Tests the `list_posts_by_user` method of PostService.

    Scenario:
    - Given a valid user ID and pagination parameters
    - When the service lists posts by user from repository
    - Then it should return a paginated response with the expected posts
    """
    # Arrange
    fake_user_id = uuid4()
    fake_post_id = uuid4()
    fake_community_id = uuid4()
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.user_id = fake_user_id
    fake_post.community_id = fake_community_id
    fake_post.title = 'User Post Title'
    fake_post.content = 'User post content'
    fake_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_post.image_url = None
    fake_post.status = PostStatusEnum.ACTIVE
    fake_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_post.likes_count = 2
    fake_post.comments_count = 1
    fake_post.report_count = 0
    fake_post.created_at = '2024-01-01T00:00:00Z'
    fake_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos
    fake_community = Mock()
    fake_community.name = 'User Community'
    fake_post.community = fake_community

    fake_user = Mock()
    fake_user.name = 'Test User'
    fake_user.profile_image_url = 'https://example.com/profile.jpg'
    fake_post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.list_posts_by_user.return_value = ([fake_post], 1)

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.list_posts_by_user(fake_user_id, fake_pagination_params)

    # Assert
    mock_post_repo.list_posts_by_user.assert_called_once_with(
        fake_user_id, fake_pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].user.id == fake_user_id
    assert result.items[0].id == fake_post_id
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_posts_by_community_service_success():
    """
    Tests the `list_posts_by_community` method of PostService.

    Scenario:
    - Given a valid community ID and pagination parameters
    - When the service lists posts by community from repository
    - Then it should return a paginated response with the expected posts
    """
    # Arrange
    fake_community_id = uuid4()
    fake_user_id = uuid4()
    fake_post_id = uuid4()
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_post = Mock(spec=Post)
    fake_post.id = fake_post_id
    fake_post.user_id = fake_user_id
    fake_post.community_id = fake_community_id
    fake_post.title = 'Community Post Title'
    fake_post.content = 'Community post content'
    fake_post.type_post = PostTypeEnum.CAMPAIGN
    fake_post.image_url = 'https://example.com/campaign.jpg'
    fake_post.status = PostStatusEnum.ACTIVE
    fake_post.user_role_in_community = CommunityMemberRoleEnum.ADMIN
    fake_post.likes_count = 10
    fake_post.comments_count = 5
    fake_post.report_count = 1
    fake_post.created_at = '2024-01-01T00:00:00Z'
    fake_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos
    fake_community = Mock()
    fake_community.name = 'Test Community'
    fake_post.community = fake_community

    fake_user = Mock()
    fake_user.name = 'Community Admin'
    fake_user.profile_image_url = 'https://example.com/admin.jpg'
    fake_post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.list_posts_by_community.return_value = ([fake_post], 1)

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.list_posts_by_community(fake_community_id, fake_pagination_params)

    # Assert
    mock_post_repo.list_posts_by_community.assert_called_once_with(
        fake_community_id, fake_pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].community.id == fake_community_id
    assert result.items[0].id == fake_post_id
    assert result.items[0].type_post == PostTypeEnum.CAMPAIGN
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_get_user_feed_service_success():
    """
    Tests the `get_user_feed` method of PostService.

    Scenario:
    - Given a valid user ID and pagination parameters
    - When the service gets user feed from repository
    - Then it should return a paginated response with mixed post types
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Criar múltiplos posts com tipos diferentes
    fake_posts = []
    post_types = [
        PostTypeEnum.CAMPAIGN,
        PostTypeEnum.COMPLAINT,
        PostTypeEnum.ANNOUNCEMENT,
    ]

    for i, post_type in enumerate(post_types):
        fake_post = Mock(spec=Post)
        fake_post.id = uuid4()
        fake_post.user_id = fake_user_id
        fake_post.community_id = fake_community_id
        fake_post.title = f'Feed Post {i + 1}'
        fake_post.content = f'Feed content {i + 1}'
        fake_post.type_post = post_type
        fake_post.image_url = None
        fake_post.status = PostStatusEnum.ACTIVE
        fake_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
        fake_post.likes_count = i + 1
        fake_post.comments_count = i
        fake_post.report_count = 0
        fake_post.created_at = '2024-01-01T00:00:00Z'
        fake_post.updated_at = '2024-01-01T00:00:00Z'

        # Mock relacionamentos
        fake_community = Mock()
        fake_community.name = f'Feed Community {i + 1}'
        fake_post.community = fake_community

        fake_user = Mock()
        fake_user.name = f'Feed User {i + 1}'
        fake_user.profile_image_url = f'https://example.com/user{i + 1}.jpg'
        fake_post.user = fake_user

        fake_posts.append(fake_post)

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_user_feed.return_value = (fake_posts, 3)

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.get_user_feed(fake_user_id, fake_pagination_params)

    # Assert
    mock_post_repo.get_user_feed.assert_called_once_with(
        fake_user_id, fake_pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 3
    assert result.items[0].type_post == PostTypeEnum.CAMPAIGN
    assert result.items[1].type_post == PostTypeEnum.COMPLAINT
    assert result.items[2].type_post == PostTypeEnum.ANNOUNCEMENT
    assert result.total == 3
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_update_post_service_success():
    """
    Tests the `update_post` method of PostService.

    Scenario:
    - Given a valid post ID and update data
    - When the service updates the post and saves it to repository
    - Then it should return the updated post response
    """
    # Arrange
    fake_post_id = uuid4()
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_original_content = 'Original content'
    fake_updated_content = 'Content updated'

    fake_post_update = PostUpdate(content=fake_updated_content)

    # Mock do post original
    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Test Post Title'
    fake_existing_post.content = fake_original_content
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 3
    fake_existing_post.comments_count = 2
    fake_existing_post.report_count = 0
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock do post atualizado (retornado após save)
    fake_saved_post = Mock(spec=Post)
    fake_saved_post.id = fake_post_id
    fake_saved_post.user_id = fake_user_id
    fake_saved_post.community_id = fake_community_id
    fake_saved_post.title = 'Test Post Title'
    fake_saved_post.content = fake_updated_content  # Conteúdo atualizado
    fake_saved_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_saved_post.image_url = None
    fake_saved_post.status = PostStatusEnum.ACTIVE
    fake_saved_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_saved_post.likes_count = 3
    fake_saved_post.comments_count = 2
    fake_saved_post.report_count = 0
    fake_saved_post.created_at = '2024-01-01T00:00:00Z'
    fake_saved_post.updated_at = '2024-01-01T01:00:00Z'  # Updated timestamp

    # Mock relacionamentos para ambos os posts
    for post in [fake_existing_post, fake_saved_post]:
        fake_community = Mock()
        fake_community.name = 'Test Community'
        post.community = fake_community

        fake_user = Mock()
        fake_user.name = 'Test User'
        fake_user.profile_image_url = 'https://example.com/profile.jpg'
        post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    # Primeira chamada (_get_post) retorna post original, segunda chamada retorna post atualizado
    mock_post_repo.get_by_id.side_effect = [fake_existing_post, fake_saved_post]
    mock_post_repo.save.return_value = fake_saved_post

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.update_post(fake_post_id, fake_post_update)

    # Assert
    assert mock_post_repo.get_by_id.call_count == 2  # Chamado duas vezes
    mock_post_repo.save.assert_called_once_with(fake_existing_post)
    assert (
        fake_existing_post.content == fake_updated_content
    )  # Conteúdo foi atualizado no objeto
    assert result is not None
    assert isinstance(result, PostResponse)
    assert result.id == fake_post_id
    assert result.content == fake_updated_content
    assert result.title == 'Test Post Title'
    assert result.user.id == fake_user_id
    assert result.community.id == fake_community_id


@pytest.mark.unit
def test_delete_post_service_success():
    """
    Tests the `delete_post` method of PostService.

    Scenario:
    - Given a valid post ID
    - When the service deletes the post from repository
    - Then it should return True indicating successful deletion
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())

    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Post to Delete'
    fake_existing_post.content = 'Content to be deleted'
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 0
    fake_existing_post.comments_count = 0
    fake_existing_post.report_count = 0
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_existing_post
    mock_post_repo.delete.return_value = True

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.delete_post(fake_post_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_post_repo.delete.assert_called_once_with(fake_existing_post)
    assert result is True


@pytest.mark.unit
def test_like_post_service_success():
    """
    Tests the `like_post` method of PostService.

    Scenario:
    - Given a valid post ID and user ID
    - When the service likes the post and saves the like to repository
    - Then it should return the post with incremented likes count
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_id = str(uuid4())

    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Post to Like'
    fake_existing_post.content = 'Content to be liked'
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 0  # Começando com 0 likes
    fake_existing_post.comments_count = 2
    fake_existing_post.report_count = 0
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    fake_saved_post = Mock(spec=Post)
    fake_saved_post.id = fake_post_id
    fake_saved_post.user_id = fake_user_id
    fake_saved_post.community_id = fake_community_id
    fake_saved_post.title = 'Post to Like'
    fake_saved_post.content = 'Content to be liked'
    fake_saved_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_saved_post.image_url = None
    fake_saved_post.status = PostStatusEnum.ACTIVE
    fake_saved_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_saved_post.likes_count = 1  # Incrementado após like
    fake_saved_post.comments_count = 2
    fake_saved_post.report_count = 0
    fake_saved_post.created_at = '2024-01-01T00:00:00Z'
    fake_saved_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos para ambos os posts
    for post in [fake_existing_post, fake_saved_post]:
        fake_community = Mock()
        fake_community.name = 'Test Community'
        post.community = fake_community

        fake_user = Mock()
        fake_user.name = 'Test User'
        fake_user.profile_image_url = 'https://example.com/profile.jpg'
        post.user = fake_user

    fake_member_association = Mock()
    fake_member_association.id = fake_member_id

    fake_post_like = Mock()
    fake_post_like.post_id = fake_post_id
    fake_post_like.member_id = fake_member_id

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_existing_post
    mock_post_repo.save.return_value = fake_saved_post

    mock_post_likes_repo = Mock()
    mock_post_likes_repo.save.return_value = fake_post_like

    mock_community_service = Mock()
    mock_community_service.get_member_association.return_value = fake_member_association

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo
    service.post_likes_repo = mock_post_likes_repo
    service.community_service = mock_community_service

    # Act
    result = service.like_post(fake_post_id, fake_member_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_post_likes_repo.save.assert_called_once()
    mock_post_repo.save.assert_called_once_with(fake_existing_post)
    assert fake_existing_post.likes_count == 1  # Verificar que foi incrementado
    assert result is not None
    assert isinstance(result, PostResponse)
    assert str(result.id) == fake_post_id
    assert result.likes_count == 1
    assert result.title == 'Post to Like'


@pytest.mark.unit
def test_unlike_post_service_success():
    """
    Tests the `unlike_post` method of PostService.

    Scenario:
    - Given a valid post ID and user ID with an existing like
    - When the service unlikes the post and removes the like from repository
    - Then it should return the post with decremented likes count
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_id = str(uuid4())

    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Post to Unlike'
    fake_existing_post.content = 'Content to be unliked'
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 1  # Começando com 1 like
    fake_existing_post.comments_count = 2
    fake_existing_post.report_count = 0
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    fake_saved_post = Mock(spec=Post)
    fake_saved_post.id = fake_post_id
    fake_saved_post.user_id = fake_user_id
    fake_saved_post.community_id = fake_community_id
    fake_saved_post.title = 'Post to Unlike'
    fake_saved_post.content = 'Content to be unliked'
    fake_saved_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_saved_post.image_url = None
    fake_saved_post.status = PostStatusEnum.ACTIVE
    fake_saved_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_saved_post.likes_count = 0  # Decrementado após unlike
    fake_saved_post.comments_count = 2
    fake_saved_post.report_count = 0
    fake_saved_post.created_at = '2024-01-01T00:00:00Z'
    fake_saved_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos para ambos os posts
    for post in [fake_existing_post, fake_saved_post]:
        fake_community = Mock()
        fake_community.name = 'Test Community'
        post.community = fake_community

        fake_user = Mock()
        fake_user.name = 'Test User'
        fake_user.profile_image_url = 'https://example.com/profile.jpg'
        post.user = fake_user

    fake_member_association = Mock()
    fake_member_association.id = fake_member_id

    fake_existing_like = Mock()
    fake_existing_like.post_id = fake_post_id
    fake_existing_like.member_id = fake_member_id

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_existing_post
    mock_post_repo.save.return_value = fake_saved_post

    mock_post_likes_repo = Mock()
    mock_post_likes_repo.get_by_id.return_value = fake_existing_like
    mock_post_likes_repo.delete.return_value = True

    mock_community_service = Mock()

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo
    service.post_likes_repo = mock_post_likes_repo
    service.community_service = mock_community_service

    # Act
    result = service.unlike_post(fake_post_id, fake_member_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_post_likes_repo.get_by_id.assert_called_once_with(fake_post_id, fake_member_id)
    mock_post_likes_repo.delete.assert_called_once_with(fake_existing_like)
    mock_post_repo.save.assert_called_once_with(fake_existing_post)
    assert fake_existing_post.likes_count == 0  # Verificar que foi decrementado
    assert result is not None
    assert isinstance(result, PostResponse)
    assert str(result.id) == fake_post_id
    assert result.likes_count == 0
    assert result.title == 'Post to Unlike'


@pytest.mark.unit
def test_list_likes_post_service_success():
    """
    Tests the `list_likes_post` method of PostService.

    Scenario:
    - Given a valid post ID with existing likes
    - When the service lists members who liked the post
    - Then it should return a list of community member responses
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_id = str(uuid4())

    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Post with Likes'
    fake_existing_post.content = 'Content with likes'
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 1
    fake_existing_post.comments_count = 0
    fake_existing_post.report_count = 0
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock do membro da comunidade que curtiu
    fake_community_member = Mock()
    fake_community_member.id = fake_member_id
    fake_community_member.user_id = fake_user_id
    fake_community_member.community_id = fake_community_id
    fake_community_member.role = CommunityMemberRoleEnum.MEMBER
    fake_community_member.status_participation = 'active'

    # Mock da resposta do membro
    fake_member_response = Mock()
    fake_member_response.user_id = fake_user_id
    fake_member_response.community_id = fake_community_id
    fake_member_response.role = CommunityMemberRoleEnum.MEMBER
    fake_member_response.status_participation = 'active'

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_existing_post

    mock_post_likes_repo = Mock()
    mock_post_likes_repo.list_by_post.return_value = [fake_community_member]

    mock_community_service = Mock()
    mock_community_service._map_member_to_response.return_value = fake_member_response

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo
    service.post_likes_repo = mock_post_likes_repo
    service.community_service = mock_community_service

    # Act
    result = service.list_likes_post(fake_post_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_post_likes_repo.list_by_post.assert_called_once_with(fake_post_id)
    mock_community_service._map_member_to_response.assert_called_once_with(
        fake_community_member
    )
    assert result is not None
    assert len(result) == 1
    assert result[0].user_id == fake_user_id
    assert result[0].community_id == fake_community_id
    assert result[0].role == CommunityMemberRoleEnum.MEMBER


@pytest.mark.unit
def test_create_campaign_service_success():
    """
    Tests the `create_campaign` method of PostService.

    Scenario:
    - Given a valid campaign post creation request
    - When the service creates the post and associated campaign
    - Then it should return a campaign response with default values
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_title = 'Campaign Title'
    fake_content = 'Campaign content'

    fake_post_create = PostCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        title=fake_title,
        content=fake_content,
        type_post=PostTypeEnum.CAMPAIGN,
        image_url=None,
        status=PostStatusEnum.ACTIVE,
    )

    # Mock do post criado - usando mocks com spec
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Test User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_created_post_response = Mock(spec=PostResponse)
    fake_created_post_response.id = fake_post_id
    fake_created_post_response.community = fake_community
    fake_created_post_response.user = fake_user
    fake_created_post_response.type_post = PostTypeEnum.CAMPAIGN
    fake_created_post_response.title = fake_title
    fake_created_post_response.content = fake_content
    fake_created_post_response.image_url = None
    fake_created_post_response.status = PostStatusEnum.ACTIVE
    fake_created_post_response.likes_count = 0
    fake_created_post_response.comments_count = 0
    fake_created_post_response.report_count = 0
    fake_created_post_response.created_at = datetime.now(timezone.utc)
    fake_created_post_response.updated_at = datetime.now(timezone.utc)

    # Mock da campanha criada
    fake_campaign = Mock(spec=CampaignPost)
    fake_campaign.post_id = fake_post_id
    fake_campaign.target_participants = 100  # Valor padrão
    fake_campaign.current_participants = 0  # Valor padrão
    fake_campaign.status_campaign = CampaignStatusEnum.PENDING  # Valor padrão

    mock_tm = Mock()
    mock_campaign_repo = Mock()
    mock_campaign_repo.save.return_value = fake_campaign

    service = PostService(mock_tm)
    service.campaign_repo = mock_campaign_repo

    # Mock dos métodos que create_campaign chama
    service.create_post = Mock(return_value=fake_created_post_response)
    service.get_post = Mock(return_value=fake_created_post_response)

    # Act
    result = service.create_campaign(fake_post_create)

    # Assert
    service.create_post.assert_called_once_with(fake_post_create)
    service.get_post.assert_called_once_with(fake_post_id)
    mock_campaign_repo.save.assert_called_once()

    saved_campaign_call = mock_campaign_repo.save.call_args[0][0]
    assert saved_campaign_call.post_id == fake_post_id

    assert result is not None
    assert str(result.post.id) == fake_post_id
    assert result.target_participants == 100
    assert result.current_participants == 0
    assert result.status_campaign == CampaignStatusEnum.PENDING


@pytest.mark.unit
def test_participate_campaign_service_success():
    """
    Tests the `participate_campaign` method of PostService.

    Scenario:
    - Given a valid campaign post ID and member ID
    - When the service adds user to campaign participants
    - Then it should increment participants count and return participant record
    """
    # Arrange
    fake_post_id = uuid4()
    fake_member_id = uuid4()

    fake_campaign = Mock(spec=CampaignPost)
    fake_campaign.post_id = fake_post_id
    fake_campaign.target_participants = 100
    fake_campaign.current_participants = 0  # Antes da participação
    fake_campaign.status_campaign = CampaignStatusEnum.PENDING

    fake_updated_campaign = Mock(spec=CampaignPost)
    fake_updated_campaign.post_id = fake_post_id
    fake_updated_campaign.target_participants = 100
    fake_updated_campaign.current_participants = 1  # Após participação
    fake_updated_campaign.status_campaign = CampaignStatusEnum.PENDING

    fake_saved_participant = Mock()
    fake_saved_participant.campaign_id = fake_post_id
    fake_saved_participant.member_id = fake_member_id
    fake_saved_participant.joined_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_campaign_repo = Mock()
    mock_campaign_repo.get_by_id.return_value = fake_campaign
    mock_campaign_repo.save.return_value = fake_updated_campaign

    mock_campaign_participants_repo = Mock()
    mock_campaign_participants_repo.save.return_value = fake_saved_participant

    # Mock do member retornado pelo community_service.get_member
    fake_member = Mock()
    fake_member.id = fake_member_id
    fake_member.user_id = uuid4()  # Pode ser qualquer UUID para user_id

    mock_community_service = Mock()
    mock_community_service.get_member.return_value = fake_member

    service = PostService(mock_tm)
    service.campaign_repo = mock_campaign_repo
    service.campaign_participants_repo = mock_campaign_participants_repo
    service.community_service = mock_community_service

    # Act
    result = service.participate_campaign(fake_post_id, fake_member_id)

    # Assert
    mock_campaign_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_community_service.get_member.assert_called_once_with(fake_member_id)
    mock_campaign_repo.save.assert_called_once_with(fake_campaign)
    mock_campaign_participants_repo.save.assert_called_once()

    # Verificar que current_participants foi incrementado
    assert fake_campaign.current_participants == 1

    # Verificar o CampaignParticipants criado
    saved_participant_call = mock_campaign_participants_repo.save.call_args[0][0]
    assert saved_participant_call.campaign_id == fake_post_id
    assert saved_participant_call.member_id == fake_member_id
    assert saved_participant_call.user_id == fake_member.user_id

    # Verificar o resultado
    assert result is not None
    assert result.campaign_id == fake_post_id
    assert result.member_id == fake_member_id


@pytest.mark.unit
def test_list_user_campaigns_subscriptions_service_success():
    """
    Tests the `list_user_campaigns_subscriptions` method of PostService.

    Scenario:
    - Given a valid user ID and pagination parameters
    - When the service lists user's campaign subscriptions
    - Then it should return a paginated response with campaign data
    """
    # Arrange
    fake_user_id = uuid4()
    fake_post_id = uuid4()
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_campaign = Mock(spec=CampaignPost)
    fake_campaign.post_id = fake_post_id
    fake_campaign.target_participants = 100
    fake_campaign.current_participants = 15
    fake_campaign.status_campaign = CampaignStatusEnum.PENDING

    # Mock do PostResponse
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = uuid4()
    fake_community.name = 'Campaign Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Campaign User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.CAMPAIGN
    fake_post_response.title = 'Campaign Title'
    fake_post_response.content = 'Campaign content'
    fake_post_response.image_url = None
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 5
    fake_post_response.comments_count = 2
    fake_post_response.report_count = 0
    fake_post_response.created_at = datetime.now(timezone.utc)
    fake_post_response.updated_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_campaign_repo = Mock()
    mock_campaign_repo.list_user_campaigns_subscriptions.return_value = (
        [fake_campaign],
        1,
    )

    service = PostService(mock_tm)
    service.campaign_repo = mock_campaign_repo
    service.get_post = Mock(return_value=fake_post_response)

    # Act
    result = service.list_user_campaigns_subscriptions(
        fake_user_id, fake_pagination_params
    )

    # Assert
    mock_campaign_repo.list_user_campaigns_subscriptions.assert_called_once_with(
        fake_user_id, fake_pagination_params
    )
    service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].post.id == fake_post_id
    assert result.items[0].target_participants == 100
    assert result.items[0].current_participants == 15
    assert result.items[0].status_campaign == CampaignStatusEnum.PENDING
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_create_complaint_service_success():
    """
    Tests the `create_complaint` method of PostService.

    Scenario:
    - Given a valid complaint post creation request
    - When the service creates the post and associated complaint
    - Then it should return a complaint response with default values
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_title = 'Complaint Title'
    fake_content = 'Complaint content'

    fake_post_create = PostCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        title=fake_title,
        content=fake_content,
        type_post=PostTypeEnum.COMPLAINT,
        image_url=None,
        status=PostStatusEnum.ACTIVE,
    )

    # Mock do PostResponse criado
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Test User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_created_post_response = Mock(spec=PostResponse)
    fake_created_post_response.id = fake_post_id
    fake_created_post_response.community = fake_community
    fake_created_post_response.user = fake_user
    fake_created_post_response.type_post = PostTypeEnum.COMPLAINT
    fake_created_post_response.title = fake_title
    fake_created_post_response.content = fake_content
    fake_created_post_response.image_url = None
    fake_created_post_response.status = PostStatusEnum.ACTIVE
    fake_created_post_response.likes_count = 0
    fake_created_post_response.comments_count = 0
    fake_created_post_response.report_count = 0
    fake_created_post_response.created_at = datetime.now(timezone.utc)
    fake_created_post_response.updated_at = datetime.now(timezone.utc)

    # Mock da reclamação criada
    fake_complaint = Mock(spec=ComplaintPost)
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 0  # Valor padrão
    fake_complaint.status_complaint = ComplaintStatusEnum.PENDING  # Valor padrão
    fake_complaint.level_complaint = ComplaintLevelEnum.LOW  # Valor padrão

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.save.return_value = fake_complaint

    service = PostService(mock_tm)
    service.complaint_repo = mock_complaint_repo

    # Mock dos métodos que create_complaint chama
    service.create_post = Mock(return_value=fake_created_post_response)
    service.get_post = Mock(return_value=fake_created_post_response)

    # Act
    result = service.create_complaint(fake_post_create)

    # Assert
    service.create_post.assert_called_once_with(fake_post_create)
    service.get_post.assert_called_once_with(fake_post_id)
    mock_complaint_repo.save.assert_called_once()

    # Verificar o ComplaintPost criado
    saved_complaint_call = mock_complaint_repo.save.call_args[0][0]
    assert saved_complaint_call.post_id == fake_post_id

    # Verificar o resultado
    assert result is not None
    assert str(result.post.id) == fake_post_id
    assert result.confirmations_count == 0
    assert result.status_complaint == ComplaintStatusEnum.PENDING
    assert result.level_complaint == ComplaintLevelEnum.LOW


@pytest.mark.unit
def test_create_poll_service_success():
    """
    Tests the `create_poll` method of PostService.

    Scenario:
    - Given a valid poll creation request with question and options
    - When the service creates the post, poll, and options
    - Then it should return a poll response with all options
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_title = 'Poll Title'
    fake_content = 'Poll content'
    fake_question = 'Question test'
    fake_options = ['Option 1', 'Option 2', 'Option 3']

    fake_post_create = PostCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        title=fake_title,
        content=fake_content,
        type_post=PostTypeEnum.POLL,
        image_url=None,
        status=PostStatusEnum.ACTIVE,
    )

    fake_poll_create = PollCreate(
        post=fake_post_create,
        question=fake_question,
        options=fake_options,
    )

    # Mock do PostResponse criado
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Test User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_created_post_response = Mock(spec=PostResponse)
    fake_created_post_response.id = fake_post_id
    fake_created_post_response.community = fake_community
    fake_created_post_response.user = fake_user
    fake_created_post_response.type_post = PostTypeEnum.POLL
    fake_created_post_response.title = fake_title
    fake_created_post_response.content = fake_content
    fake_created_post_response.image_url = None
    fake_created_post_response.status = PostStatusEnum.ACTIVE
    fake_created_post_response.likes_count = 0
    fake_created_post_response.comments_count = 0
    fake_created_post_response.report_count = 0
    fake_created_post_response.created_at = datetime.now(timezone.utc)
    fake_created_post_response.updated_at = datetime.now(timezone.utc)

    # Mock da enquete criada
    fake_poll = Mock(spec=PollPosts)
    fake_poll.post_id = fake_post_id
    fake_poll.question = fake_question

    # Mock das opções criadas
    fake_poll_options = []
    for i, option_text in enumerate(fake_options):
        fake_option = Mock(spec=PollOptions)
        fake_option.id = uuid4()
        fake_option.post_id = fake_post_id
        fake_option.answer = option_text
        fake_option.votes_count = 0
        fake_poll_options.append(fake_option)

    mock_tm = Mock()
    mock_poll_posts_repo = Mock()
    mock_poll_posts_repo.save.return_value = fake_poll

    mock_poll_options_repo = Mock()
    mock_poll_options_repo.save.side_effect = fake_poll_options

    service = PostService(mock_tm)
    service.poll_posts_repo = mock_poll_posts_repo
    service.poll_options_repo = mock_poll_options_repo

    # Mock dos métodos que create_poll chama
    service.create_post = Mock(return_value=fake_created_post_response)
    service.get_post = Mock(return_value=fake_created_post_response)

    # Act
    result = service.create_poll(fake_poll_create)

    # Assert
    service.create_post.assert_called_once_with(fake_post_create)
    service.get_post.assert_called_once_with(fake_post_id)
    mock_poll_posts_repo.save.assert_called_once()
    assert mock_poll_options_repo.save.call_count == 3

    # Verificar o PollPosts criado
    saved_poll_call = mock_poll_posts_repo.save.call_args[0][0]
    assert saved_poll_call.post_id == fake_post_id
    assert saved_poll_call.question == fake_question

    # Verificar o resultado
    assert result is not None
    assert str(result.post.id) == fake_post_id
    assert result.question == fake_question
    assert len(result.options) == 3
    assert result.options[0].answer == 'Option 1'
    assert result.options[1].answer == 'Option 2'
    assert result.options[2].answer == 'Option 3'


@pytest.mark.unit
def test_get_poll_service_success():
    """
    Tests the `get_poll` method of PostService.

    Scenario:
    - Given a valid poll post ID
    - When the service retrieves the poll from repository
    - Then it should return the poll with its options
    """
    # Arrange
    fake_post_id = uuid4()
    fake_question = 'What is your favorite color?'

    # Mock das opções da enquete
    fake_poll_options = []
    option_texts = ['Red', 'Blue', 'Green']
    for i, option_text in enumerate(option_texts):
        fake_option = Mock(spec=PollOptions)
        fake_option.id = uuid4()
        fake_option.post_id = fake_post_id
        fake_option.answer = option_text
        fake_option.votes_count = i  # Votos diferentes para cada opção
        fake_poll_options.append(fake_option)

    fake_poll = Mock(spec=PollPosts)
    fake_poll.post_id = fake_post_id
    fake_poll.question = fake_question
    fake_poll.options = fake_poll_options

    mock_tm = Mock()
    mock_poll_posts_repo = Mock()
    mock_poll_posts_repo.get_by_id.return_value = fake_poll

    service = PostService(mock_tm)
    service.poll_posts_repo = mock_poll_posts_repo

    # Act
    result = service.get_poll(fake_post_id)

    # Assert
    mock_poll_posts_repo.get_by_id.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.post_id == fake_post_id
    assert result.question == fake_question
    assert result.options == fake_poll_options
    assert len(result.options) == 3
    assert result.options[0].answer == 'Red'
    assert result.options[0].votes_count == 0
    assert result.options[1].answer == 'Blue'
    assert result.options[1].votes_count == 1
    assert result.options[2].answer == 'Green'
    assert result.options[2].votes_count == 2


@pytest.mark.unit
def test_vote_poll_service_success():
    """
    Tests the `vote_poll` method of PostService.

    Scenario:
    - Given a valid poll option ID
    - When the service votes on the poll option
    - Then it should increment votes count and return updated poll response
    """
    # Arrange
    fake_post_id = uuid4()
    fake_poll_option_id = uuid4()
    fake_question = 'What is your favorite programming language?'

    # Mock da opção que será votada
    fake_voted_option = Mock(spec=PollOptions)
    fake_voted_option.id = fake_poll_option_id
    fake_voted_option.post_id = fake_post_id
    fake_voted_option.answer = 'Python'
    fake_voted_option.votes_count = 0  # Antes do voto

    # Mock das outras opções
    fake_other_options = []
    other_languages = ['JavaScript', 'Java']
    for i, lang in enumerate(other_languages):
        fake_option = Mock(spec=PollOptions)
        fake_option.id = uuid4()
        fake_option.post_id = fake_post_id
        fake_option.answer = lang
        fake_option.votes_count = 0
        fake_other_options.append(fake_option)

    # Todas as opções (incluindo a votada)
    all_options = [fake_voted_option] + fake_other_options

    # Mock da enquete
    fake_poll = Mock(spec=PollPosts)
    fake_poll.post_id = fake_post_id
    fake_poll.question = fake_question
    fake_poll.options = all_options

    # Mock do PostResponse
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = uuid4()
    fake_community.name = 'Tech Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = uuid4()
    fake_user.name = 'Poll Creator'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.ADMIN

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.POLL
    fake_post_response.title = 'Programming Languages Poll'
    fake_post_response.content = 'Vote for your favorite language'
    fake_post_response.image_url = None
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 5
    fake_post_response.comments_count = 3
    fake_post_response.report_count = 0
    fake_post_response.created_at = datetime.now(timezone.utc)
    fake_post_response.updated_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_poll_options_repo = Mock()
    mock_poll_options_repo.get_by_id.return_value = fake_voted_option
    mock_poll_options_repo.save.return_value = fake_voted_option

    service = PostService(mock_tm)
    service.poll_options_repo = mock_poll_options_repo
    service.get_poll = Mock(return_value=fake_poll)
    service.get_post = Mock(return_value=fake_post_response)

    # Act
    result = service.vote_poll(fake_poll_option_id)

    # Assert
    mock_poll_options_repo.get_by_id.assert_called_once_with(fake_poll_option_id)
    mock_poll_options_repo.save.assert_called_once_with(fake_voted_option)
    service.get_poll.assert_called_once_with(fake_post_id)
    service.get_post.assert_called_once_with(fake_post_id)

    # Verificar que o voto foi incrementado
    assert fake_voted_option.votes_count == 1

    # Verificar o resultado
    assert result is not None
    assert result.post.id == fake_post_id
    assert result.question == fake_question
    assert len(result.options) == 3

    # As opções devem estar ordenadas por answer (alfabética)
    assert result.options[0].answer == 'Java'  # Alfabeticamente primeiro
    assert result.options[0].votes_count == 0
    assert result.options[1].answer == 'JavaScript'
    assert result.options[1].votes_count == 0
    assert result.options[2].answer == 'Python'  # A que foi votada
    assert result.options[2].votes_count == 1


@pytest.mark.unit
def test_report_post_service_success():
    """
    Tests the `report_post` method of PostService.

    Scenario:
    - Given a valid post ID with active status
    - When the service reports the post
    - Then it should increment report_count and return updated post response
    """
    # Arrange
    fake_post_id = uuid4()
    fake_user_id = uuid4()
    fake_community_id = uuid4()

    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Post to Report'
    fake_existing_post.content = 'Content to be reported'
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 5
    fake_existing_post.comments_count = 2
    fake_existing_post.report_count = 0  # Começando com 0 reports
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    fake_saved_post = Mock(spec=Post)
    fake_saved_post.id = fake_post_id
    fake_saved_post.user_id = fake_user_id
    fake_saved_post.community_id = fake_community_id
    fake_saved_post.title = 'Post to Report'
    fake_saved_post.content = 'Content to be reported'
    fake_saved_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_saved_post.image_url = None
    fake_saved_post.status = PostStatusEnum.ACTIVE
    fake_saved_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_saved_post.likes_count = 5
    fake_saved_post.comments_count = 2
    fake_saved_post.report_count = 1  # Incrementado após report
    fake_saved_post.created_at = '2024-01-01T00:00:00Z'
    fake_saved_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos para ambos os posts
    for post in [fake_existing_post, fake_saved_post]:
        fake_community = Mock()
        fake_community.name = 'Test Community'
        post.community = fake_community

        fake_user = Mock()
        fake_user.name = 'Test User'
        fake_user.profile_image_url = 'https://example.com/profile.jpg'
        post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_existing_post
    mock_post_repo.save.return_value = fake_saved_post

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.report_post(fake_post_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(str(fake_post_id))
    mock_post_repo.save.assert_called_once_with(fake_existing_post)
    assert fake_existing_post.report_count == 1  # Verificar que foi incrementado
    assert result is not None
    assert isinstance(result, PostResponse)
    assert str(result.id) == str(fake_post_id)
    assert result.report_count == 1


@pytest.mark.unit
def test_report_post_service_suspended_error():
    """
    Tests the `report_post` method of PostService when post is already suspended.

    Scenario:
    - Given a post ID with suspended status
    - When the service tries to report the post
    - Then it should raise PostSuspendedError
    """
    # Arrange
    fake_post_id = uuid4()
    fake_user_id = uuid4()
    fake_community_id = uuid4()

    fake_suspended_post = Mock(spec=Post)
    fake_suspended_post.id = fake_post_id
    fake_suspended_post.user_id = fake_user_id
    fake_suspended_post.community_id = fake_community_id
    fake_suspended_post.title = 'Suspended Post'
    fake_suspended_post.content = 'Suspended content'
    fake_suspended_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_suspended_post.image_url = None
    fake_suspended_post.status = PostStatusEnum.SUSPENDED  # Post já suspenso
    fake_suspended_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_suspended_post.likes_count = 0
    fake_suspended_post.comments_count = 0
    fake_suspended_post.report_count = 0
    fake_suspended_post.created_at = '2024-01-01T00:00:00Z'
    fake_suspended_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos
    fake_community = Mock()
    fake_community.name = 'Test Community'
    fake_suspended_post.community = fake_community

    fake_user = Mock()
    fake_user.name = 'Test User'
    fake_user.profile_image_url = 'https://example.com/profile.jpg'
    fake_suspended_post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_suspended_post

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act & Assert
    with pytest.raises(PostSuspendedError) as exc_info:
        service.report_post(fake_post_id)
    assert 'Post is already suspended' in str(exc_info.value)


@pytest.mark.unit
def test_report_post_service_reports_threshold():
    """
    Tests the `report_post` method of PostService when reaching threshold.

    Scenario:
    - Given a post ID with report_count at threshold - 1
    - When the service reports the post
    - Then it should change status to REPORTED and increment report_count
    """
    # Arrange
    fake_post_id = uuid4()
    fake_user_id = uuid4()
    fake_community_id = uuid4()

    fake_existing_post = Mock(spec=Post)
    fake_existing_post.id = fake_post_id
    fake_existing_post.user_id = fake_user_id
    fake_existing_post.community_id = fake_community_id
    fake_existing_post.title = 'Post Near Threshold'
    fake_existing_post.content = 'Content near threshold'
    fake_existing_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_existing_post.image_url = None
    fake_existing_post.status = PostStatusEnum.ACTIVE
    fake_existing_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_existing_post.likes_count = 0
    fake_existing_post.comments_count = 0
    fake_existing_post.report_count = 29  # Um abaixo do threshold (30)
    fake_existing_post.created_at = '2024-01-01T00:00:00Z'
    fake_existing_post.updated_at = '2024-01-01T00:00:00Z'

    fake_saved_post = Mock(spec=Post)
    fake_saved_post.id = fake_post_id
    fake_saved_post.user_id = fake_user_id
    fake_saved_post.community_id = fake_community_id
    fake_saved_post.title = 'Post Near Threshold'
    fake_saved_post.content = 'Content near threshold'
    fake_saved_post.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_saved_post.image_url = None
    fake_saved_post.status = PostStatusEnum.REPORTED  # Status mudou para REPORTED
    fake_saved_post.user_role_in_community = CommunityMemberRoleEnum.MEMBER
    fake_saved_post.likes_count = 0
    fake_saved_post.comments_count = 0
    fake_saved_post.report_count = 30  # Agora no threshold
    fake_saved_post.created_at = '2024-01-01T00:00:00Z'
    fake_saved_post.updated_at = '2024-01-01T00:00:00Z'

    # Mock relacionamentos para ambos os posts
    for post in [fake_existing_post, fake_saved_post]:
        fake_community = Mock()
        fake_community.name = 'Test Community'
        post.community = fake_community

        fake_user = Mock()
        fake_user.name = 'Test User'
        fake_user.profile_image_url = 'https://example.com/profile.jpg'
        post.user = fake_user

    mock_tm = Mock()
    mock_post_repo = Mock()
    mock_post_repo.get_by_id.return_value = fake_existing_post
    mock_post_repo.save.return_value = fake_saved_post

    service = PostService(mock_tm)
    service.post_repo = mock_post_repo

    # Act
    result = service.report_post(fake_post_id)

    # Assert
    mock_post_repo.get_by_id.assert_called_once_with(str(fake_post_id))
    mock_post_repo.save.assert_called_once_with(fake_existing_post)
    assert fake_existing_post.report_count == 30  # Verificar que foi incrementado
    assert fake_existing_post.status == PostStatusEnum.REPORTED  # Status mudou
    assert result is not None
    assert isinstance(result, PostResponse)
    assert result.report_count == 30
    assert result.status == PostStatusEnum.REPORTED


@pytest.mark.unit
def test_confirm_complaint_service_success():
    """
    Tests the `confirm_complaint` method of PostService.

    Scenario:
    - Given a valid complaint post ID with low confirmations
    - When the service confirms the complaint
    - Then it should increment confirmations_count and maintain LOW level
    """
    # Arrange
    fake_post_id = uuid4()
    fake_community_id = uuid4()
    fake_user_id = uuid4()

    fake_complaint = Mock(spec=ComplaintPost)
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 5  # Baixo número de confirmações
    fake_complaint.status_complaint = ComplaintStatusEnum.PENDING
    fake_complaint.level_complaint = ComplaintLevelEnum.LOW

    fake_saved_complaint = Mock(spec=ComplaintPost)
    fake_saved_complaint.post_id = fake_post_id
    fake_saved_complaint.confirmations_count = 6  # Incrementado
    fake_saved_complaint.status_complaint = ComplaintStatusEnum.PENDING
    fake_saved_complaint.level_complaint = ComplaintLevelEnum.LOW  # Mantém LOW

    # Mock do PostResponse
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Test User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.COMPLAINT
    fake_post_response.title = 'Complaint Title'
    fake_post_response.content = 'Complaint content'
    fake_post_response.image_url = None
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 0
    fake_post_response.comments_count = 0
    fake_post_response.report_count = 0
    fake_post_response.created_at = datetime.now(timezone.utc)
    fake_post_response.updated_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.get_by_id.return_value = fake_complaint
    mock_complaint_repo.save.return_value = fake_saved_complaint

    service = PostService(mock_tm)
    service.complaint_repo = mock_complaint_repo
    service.get_post = Mock(return_value=fake_post_response)

    # Act
    result = service.confirm_complaint(fake_post_id)

    # Assert
    mock_complaint_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_complaint_repo.save.assert_called_once_with(fake_complaint)
    assert fake_complaint.confirmations_count == 6  # Verificar que foi incrementado
    assert fake_complaint.level_complaint == ComplaintLevelEnum.LOW  # Mantém LOW
    service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert isinstance(result, ComplaintResponse)
    assert result.confirmations_count == 6
    assert result.level_complaint == ComplaintLevelEnum.LOW
    assert result.status_complaint == ComplaintStatusEnum.PENDING


@pytest.mark.unit
def test_confirm_complaint_service_updates_level_low_to_medium():
    """
    Tests the `confirm_complaint` method when confirmations reach medium threshold.

    Scenario:
    - Given a complaint with 29 confirmations (below medium threshold)
    - When the service confirms the complaint
    - Then it should update level_complaint to MEDIUM
    """
    # Arrange
    fake_post_id = uuid4()
    fake_community_id = uuid4()
    fake_user_id = uuid4()

    fake_complaint = Mock(spec=ComplaintPost)
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 29  # Um abaixo do threshold de 30
    fake_complaint.status_complaint = ComplaintStatusEnum.PENDING
    fake_complaint.level_complaint = ComplaintLevelEnum.LOW

    fake_saved_complaint = Mock(spec=ComplaintPost)
    fake_saved_complaint.post_id = fake_post_id
    fake_saved_complaint.confirmations_count = 30  # Agora no threshold
    fake_saved_complaint.status_complaint = ComplaintStatusEnum.PENDING
    fake_saved_complaint.level_complaint = ComplaintLevelEnum.MEDIUM  # Mudou para MEDIUM

    # Mock do PostResponse
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Test User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.COMPLAINT
    fake_post_response.title = 'Complaint Title'
    fake_post_response.content = 'Complaint content'
    fake_post_response.image_url = None
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 0
    fake_post_response.comments_count = 0
    fake_post_response.report_count = 0
    fake_post_response.created_at = datetime.now(timezone.utc)
    fake_post_response.updated_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.get_by_id.return_value = fake_complaint
    mock_complaint_repo.save.return_value = fake_saved_complaint

    service = PostService(mock_tm)
    service.complaint_repo = mock_complaint_repo
    service.get_post = Mock(return_value=fake_post_response)

    # Act
    result = service.confirm_complaint(fake_post_id)

    # Assert
    mock_complaint_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_complaint_repo.save.assert_called_once_with(fake_complaint)
    assert fake_complaint.confirmations_count == 30
    assert fake_complaint.level_complaint == ComplaintLevelEnum.MEDIUM  # Mudou para MEDIUM
    service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert isinstance(result, ComplaintResponse)
    assert result.confirmations_count == 30
    assert result.level_complaint == ComplaintLevelEnum.MEDIUM
    assert result.status_complaint == ComplaintStatusEnum.PENDING


@pytest.mark.unit
def test_confirm_complaint_service_updates_level_to_high():
    """
    Tests the `confirm_complaint` method when confirmations reach high threshold.

    Scenario:
    - Given a complaint with 49 confirmations (below high threshold)
    - When the service confirms the complaint
    - Then it should update level_complaint to HIGH
    """
    # Arrange
    fake_post_id = uuid4()
    fake_community_id = uuid4()
    fake_user_id = uuid4()

    fake_complaint = Mock(spec=ComplaintPost)
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 49  # Um abaixo do threshold de 50
    fake_complaint.status_complaint = ComplaintStatusEnum.PENDING
    fake_complaint.level_complaint = ComplaintLevelEnum.MEDIUM

    fake_saved_complaint = Mock(spec=ComplaintPost)
    fake_saved_complaint.post_id = fake_post_id
    fake_saved_complaint.confirmations_count = 50  # Agora no threshold HIGH
    fake_saved_complaint.status_complaint = ComplaintStatusEnum.PENDING
    fake_saved_complaint.level_complaint = ComplaintLevelEnum.HIGH  # Mudou para HIGH

    # Mock do PostResponse
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = fake_user_id
    fake_user.name = 'Test User'
    fake_user.profile_picture = 'https://example.com/profile.jpg'
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.COMPLAINT
    fake_post_response.title = 'Complaint Title'
    fake_post_response.content = 'Complaint content'
    fake_post_response.image_url = None
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 0
    fake_post_response.comments_count = 0
    fake_post_response.report_count = 0
    fake_post_response.created_at = datetime.now(timezone.utc)
    fake_post_response.updated_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.get_by_id.return_value = fake_complaint
    mock_complaint_repo.save.return_value = fake_saved_complaint

    service = PostService(mock_tm)
    service.complaint_repo = mock_complaint_repo
    service.get_post = Mock(return_value=fake_post_response)

    # Act
    result = service.confirm_complaint(fake_post_id)

    # Assert
    mock_complaint_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_complaint_repo.save.assert_called_once_with(fake_complaint)
    assert fake_complaint.confirmations_count == 50
    assert fake_complaint.level_complaint == ComplaintLevelEnum.HIGH  # Mudou para HIGH
    service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert isinstance(result, ComplaintResponse)
    assert result.confirmations_count == 50
    assert result.level_complaint == ComplaintLevelEnum.HIGH
    assert result.status_complaint == ComplaintStatusEnum.PENDING
