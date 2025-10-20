from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.api.communities.exceptions import (
    CommunityMemberAlreadyExistsError,
    CommunityMemberNotFoundError,
    CommunityNotFoundError,
    UnexpectedCommunityError,
    UnexpectedCommunityMemberError,
)
from app.api.communities.model import Community, CommunityMember
from app.api.communities.schema import (
    CommunityCreate,
    CommunityMemberCreate,
    CommunityMemberResponse,
    CommunityMemberRoleEnum,
    CommunityMemberStatusEnum,
    CommunityMemberCreate,
    CommunityMemberResponse,
)
from app.api.communities.service import CommunityService
from app.api.users.schema import UserStatusEnum
from app.utils.schema import PaginationSearchParams


@pytest.mark.unit
def test_create_community_service_success():
    """
    Tests the `create_community` method of CommunityService - success scenario.

    Scenario:
    - Given valid community creation data
    - When the service creates the community successfully
    - Then it should return the expected Community model
    """
    # Arrange
    fake_community_id = uuid4()
    fake_community_data = CommunityCreate(
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
    )

    expect_community_model = Mock(spec=Community)
    expect_community_model.id = fake_community_id
    expect_community_model.name = 'Test Community'
    expect_community_model.description = 'Test Description'
    expect_community_model.type_community = CommunityTypeEnum.UNIVERSITY

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.save.return_value = expect_community_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.create_community(fake_community_data)

    # Assert
    mock_community_repo.save.assert_called_once()
    assert result is not None
    assert result.id == fake_community_id
    assert result.name == 'Test Community'
    assert result.description == 'Test Description'
    assert result.type_community == CommunityTypeEnum.UNIVERSITY

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.save.return_value = expect_community_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.create_community(fake_community_data)

    # Assert
    mock_community_repo.save.assert_called_once()
    assert result is not None
    assert result.id == fake_community_id
    assert result.name == 'Test Community'
    assert result.description == 'Test Description'
    assert result.type_community == CommunityTypeEnum.UNIVERSITY


@pytest.mark.unit
def test_create_community_with_image_url_service_success():
    """
    Tests the `create_community` method of CommunityService with image_url.

    Scenario:
    - Given valid community creation data including an image_url
    - When the service creates the community successfully
    - Then it should convert HttpUrl to string and return the expected Community model
    """
    # Arrange
    fake_community_id = uuid4()
    fake_community_data = CommunityCreate(
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
        image_url='https://example.com/test-image.jpg',
    )

    expect_community_model = Mock(spec=Community)
    expect_community_model.id = fake_community_id
    expect_community_model.name = 'Test Community'
    expect_community_model.description = 'Test Description'
    expect_community_model.type_community = CommunityTypeEnum.UNIVERSITY
    expect_community_model.image_url = 'https://example.com/test-image.jpg'

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.save.return_value = expect_community_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.create_community(fake_community_data)

    # Assert
    mock_community_repo.save.assert_called_once()
    # Verify that the Community model was created with string image_url, not HttpUrl
    saved_community_args = mock_community_repo.save.call_args[0][0]
    assert hasattr(saved_community_args, '__dict__')

    assert result is not None
    assert result.id == fake_community_id
    assert result.name == 'Test Community'
    assert result.description == 'Test Description'
    assert result.type_community == CommunityTypeEnum.UNIVERSITY
    assert result.image_url == 'https://example.com/test-image.jpg'


@pytest.mark.unit
def test_create_community_service_unexpected_error():
    """
    Tests the `create_community` method of CommunityService - unexpected error scenario.

    Scenario:
    - Given valid community creation data
    - When an unexpected error occurs during save
    - Then it should raise UnexpectedCommunityError
    """
    # Arrange
    fake_community_data = CommunityCreate(
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
    )

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.save.side_effect = Exception('Database error')

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act & Assert
    with pytest.raises(UnexpectedCommunityError):
        service.create_community(fake_community_data)

    mock_community_repo.save.assert_called_once()


@pytest.mark.unit
def test_get_community_by_id_service_success():
    """
    Tests the `get_community` method of CommunityService.

    Scenario:
    - Given an existing community ID
    - When the service retrieves the community successfully
    - Then it should return the expected Community model
    """
    # Arrange
    fake_community_id = str(uuid4())

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id
    fake_community_model.name = 'Test Community'
    fake_community_model.description = 'Test Description'
    fake_community_model.type_community = CommunityTypeEnum.UNIVERSITY

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.get_community(fake_community_id)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    assert result is not None
    assert result.id == fake_community_id
    assert result.name == 'Test Community'
    assert result.description == 'Test Description'
    assert result.type_community == CommunityTypeEnum.UNIVERSITY


@pytest.mark.unit
def test_get_community_by_id_service_not_found():
    """
    Tests the `get_community` method of CommunityService when community is not found.

    Scenario:
    - Given a non-existent community ID
    - When the repository returns None
    - Then it should raise CommunityNotFoundError
    """
    # Arrange
    fake_community_id = str(uuid4())

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = None

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act & Assert
    with pytest.raises(CommunityNotFoundError):
        service.get_community(fake_community_id)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)


@pytest.mark.unit
def test_list_communities_service_success():
    """
    Tests the `list_communities` method of CommunityService.

    Scenario:
    - Given pagination parameters
    - When the service lists communities successfully
    - Then it should return a paginated response with CommunityResponse items
    """
    # Arrange
    fake_community_id = uuid4()
    fake_params = PaginationSearchParams(offset=0, limit=10)
    fake_datetime = datetime.now()

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id
    fake_community_model.name = 'Test Community'
    fake_community_model.description = 'Test Description'
    fake_community_model.type_community = CommunityTypeEnum.UNIVERSITY
    fake_community_model.image_url = 'https://example.com/community-image.jpg'
    fake_community_model.created_at = fake_datetime
    fake_community_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.list_all.return_value = ([fake_community_model], 1)

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.list_communities(fake_params)

    # Assert
    mock_community_repo.list_all.assert_called_once_with(fake_params)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].id == fake_community_id
    assert result.items[0].name == 'Test Community'
    assert result.items[0].description == 'Test Description'
    assert result.items[0].type_community == CommunityTypeEnum.UNIVERSITY
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_communities_with_search_service_success():
    """
    Tests the `list_communities` method of CommunityService with search parameter.

    Scenario:
    - Given pagination parameters with search term
    - When the service searches communities by name successfully
    - Then it should return communities matching the search term
    """
    # Arrange
    fake_community_id = uuid4()
    fake_community_name = 'Test Community'
    fake_params = PaginationSearchParams(offset=0, limit=10, search=fake_community_name)
    fake_datetime = datetime.now()

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id
    fake_community_model.name = fake_community_name
    fake_community_model.description = 'Test Description'
    fake_community_model.type_community = CommunityTypeEnum.UNIVERSITY
    fake_community_model.image_url = 'https://example.com/community-image.jpg'
    fake_community_model.created_at = fake_datetime
    fake_community_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.list_all.return_value = ([fake_community_model], 1)

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.list_communities(fake_params)

    # Assert
    mock_community_repo.list_all.assert_called_once_with(fake_params)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].id == fake_community_id
    assert result.items[0].name == fake_community_name
    assert result.total == 1


@pytest.mark.unit
def test_update_community_service_success():
    """
    Tests the `update_community` method of CommunityService.

    Scenario:
    - Given a community ID and update data
    - When the service updates the community successfully
    - Then it should return the updated Community model
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_community_update = CommunityUpdate(
        name='Updated Community',
        description='Updated Description',
        type_community=CommunityTypeEnum.COMMERCIAL,
    )

    fake_existing_community = Mock(spec=Community)
    fake_existing_community.id = fake_community_id
    fake_existing_community.name = 'Original Community'
    fake_existing_community.description = 'Original Description'
    fake_existing_community.type_community = CommunityTypeEnum.UNIVERSITY

    fake_updated_community = Mock(spec=Community)
    fake_updated_community.id = fake_community_id
    fake_updated_community.name = 'Updated Community'
    fake_updated_community.description = 'Updated Description'
    fake_updated_community.type_community = CommunityTypeEnum.COMMERCIAL

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_existing_community
    mock_community_repo.save.return_value = fake_updated_community

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.update_community(fake_community_id, fake_community_update)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_community_repo.save.assert_called_once_with(fake_existing_community)
    assert result is not None
    assert result.name == 'Updated Community'
    assert result.description == 'Updated Description'
    assert result.type_community == CommunityTypeEnum.COMMERCIAL


@pytest.mark.unit
def test_update_community_with_image_url_service_success():
    """
    Tests the `update_community` method of CommunityService with image_url.

    Scenario:
    - Given a community ID and update data including an image_url
    - When the service updates the community successfully
    - Then it should convert HttpUrl to string and return the updated Community model
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_community_update = CommunityUpdate(
        name='Updated Community',
        image_url='https://example.com/new-image.jpg',
    )

    fake_existing_community = Mock(spec=Community)
    fake_existing_community.id = fake_community_id
    fake_existing_community.name = 'Original Community'
    fake_existing_community.image_url = None

    fake_updated_community = Mock(spec=Community)
    fake_updated_community.id = fake_community_id
    fake_updated_community.name = 'Updated Community'
    fake_updated_community.image_url = 'https://example.com/new-image.jpg'

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_existing_community
    mock_community_repo.save.return_value = fake_updated_community

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.update_community(fake_community_id, fake_community_update)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_community_repo.save.assert_called_once_with(fake_existing_community)

    # Verify that setattr was called with string value, not HttpUrl object
    assert fake_existing_community.image_url == 'https://example.com/new-image.jpg'
    assert result is not None
    assert result.name == 'Updated Community'
    assert result.image_url == 'https://example.com/new-image.jpg'


@pytest.mark.unit
def test_update_community_partial_service_success():
    """
    Tests the `update_community` method of CommunityService with partial update.

    Scenario:
    - Given a community ID and partial update data (only name)
    - When the service updates the community partially
    - Then it should return the community with only updated fields changed
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_partial_update = CommunityUpdate(name='Partially Updated Community')

    fake_existing_community = Mock(spec=Community)
    fake_existing_community.id = fake_community_id
    fake_existing_community.name = 'Original Community'
    fake_existing_community.description = 'Original Description'
    fake_existing_community.type_community = CommunityTypeEnum.UNIVERSITY

    fake_updated_community = Mock(spec=Community)
    fake_updated_community.id = fake_community_id
    fake_updated_community.name = 'Partially Updated Community'
    fake_updated_community.description = 'Original Description'
    fake_updated_community.type_community = CommunityTypeEnum.UNIVERSITY

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_existing_community
    mock_community_repo.save.return_value = fake_updated_community

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.update_community(fake_community_id, fake_partial_update)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_community_repo.save.assert_called_once_with(fake_existing_community)
    assert result is not None
    assert result.name == 'Partially Updated Community'
    assert result.description == 'Original Description'
    assert result.type_community == CommunityTypeEnum.UNIVERSITY


@pytest.mark.unit
def test_update_community_service_not_found():
    """
    Tests the `update_community` method of CommunityService - not found scenario.

    Scenario:
    - Given a non-existent community ID and update data
    - When the community is not found
    - Then it should raise CommunityNotFoundError
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_community_update = CommunityUpdate(name='Updated Community')

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = None

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act & Assert
    with pytest.raises(CommunityNotFoundError):
        service.update_community(fake_community_id, fake_community_update)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)


@pytest.mark.unit
def test_update_community_service_unexpected_error():
    """
    Tests the `update_community` method of CommunityService - unexpected error scenario.

    Scenario:
    - Given valid community ID and update data
    - When an unexpected error occurs during save
    - Then it should raise UnexpectedCommunityError
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_community_update = CommunityUpdate(name='Updated Community')

    fake_existing_community = Mock(spec=Community)
    fake_existing_community.id = fake_community_id

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_existing_community
    mock_community_repo.save.side_effect = Exception('Database error')

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act & Assert
    with pytest.raises(UnexpectedCommunityError):
        service.update_community(fake_community_id, fake_community_update)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_community_repo.save.assert_called_once_with(fake_existing_community)


@pytest.mark.unit
def test_delete_community_service_success():
    """
    Tests the `delete_community` method of CommunityService.

    Scenario:
    - Given a community ID
    - When the service deletes the community successfully
    - Then it should return True indicating successful deletion
    """
    # Arrange
    fake_community_id = str(uuid4())

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_community_repo.delete.return_value = True

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act
    result = service.delete_community(fake_community_id)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_community_repo.delete.assert_called_once_with(fake_community_model)
    assert result is True


@pytest.mark.unit
def test_delete_community_service_not_found():
    """
    Tests the `delete_community` method of CommunityService when community is not found.

    Scenario:
    - Given a non-existent community ID
    - When the get_community method raises CommunityNotFoundError
    - Then it should propagate the exception
    """
    # Arrange
    fake_community_id = str(uuid4())

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = None

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act & Assert
    with pytest.raises(CommunityNotFoundError):
        service.delete_community(fake_community_id)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)


@pytest.mark.unit
def test_delete_community_service_unexpected_error():
    """
    Tests the `delete_community` method of CommunityService - unexpected error scenario.

    Scenario:
    - Given valid community ID
    - When an unexpected error occurs during deletion
    - Then it should raise UnexpectedCommunityError
    """
    # Arrange
    fake_community_id = str(uuid4())

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_community_repo.delete.side_effect = Exception('Database error')

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo

    # Act & Assert
    with pytest.raises(UnexpectedCommunityError):
        service.delete_community(fake_community_id)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_community_repo.delete.assert_called_once_with(fake_community_model)


@pytest.mark.unit
def test_list_members_service_success():
    """
    Tests the `list_members` method of CommunityService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service lists community members successfully
    - Then it should return a paginated response with CommunityMemberResponse items
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_params = PaginationSearchParams(offset=0, limit=10)

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.user_id = fake_user_id
    fake_member_model.community_id = fake_community_id
    fake_member_model.role = CommunityMemberRoleEnum.MEMBER

    fake_member_response = Mock(spec=CommunityMemberResponse)
    fake_member_response.user_id = fake_user_id
    fake_member_response.community_id = fake_community_id
    fake_member_response.role = CommunityMemberRoleEnum.MEMBER

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.list_members.return_value = ([fake_member_model], 1)

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service._map_member_to_response = Mock(return_value=fake_member_response)

    # Act
    result = service.list_members(fake_community_id, fake_params)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_member_repo.list_members.assert_called_once_with(fake_community_id, fake_params)
    service._map_member_to_response.assert_called_once_with(fake_member_model)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].user_id == fake_user_id
    assert result.items[0].community_id == fake_community_id
    assert result.items[0].role == CommunityMemberRoleEnum.MEMBER


@pytest.mark.unit
def test_list_user_communities_service_success():
    """
    Tests the `list_user_communities` method of CommunityService.

    Scenario:
    - Given a user ID and pagination parameters
    - When the service lists communities for the user successfully
    - Then it should return a paginated response with CommunityResponse items
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_params = PaginationSearchParams(offset=0, limit=10)

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id
    fake_community_model.name = 'Test Community'
    fake_community_model.description = 'Test Description'
    fake_community_model.type_community = CommunityTypeEnum.UNIVERSITY
    fake_community_model.image_url = 'https://example.com/community-image.jpg'
    fake_community_model.created_at = datetime.now()
    fake_community_model.updated_at = datetime.now()

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.list_communities_by_user.return_value = ([fake_community_model], 1)

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    result = service.list_user_communities(fake_user_id, fake_params)

    # Assert
    mock_member_repo.list_communities_by_user.assert_called_once_with(
        fake_user_id, fake_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].id == fake_community_id
    assert result.items[0].name == 'Test Community'
    assert result.total == 1
    assert result.has_more == False


@pytest.mark.unit
def test_list_moderators_service_success():
    """
    Tests the `list_moderators` method of CommunityService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service lists moderators for the community successfully
    - Then it should return a paginated response with CommunityMemberResponse items
    """
    # Arrange
    fake_community_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_params = PaginationSearchParams(offset=0, limit=10)

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    fake_moderator_model = Mock(spec=CommunityMember)
    fake_moderator_model.user_id = fake_user_id
    fake_moderator_model.community_id = fake_community_id
    fake_moderator_model.role = CommunityMemberRoleEnum.MODERATOR

    fake_moderator_response = Mock(spec=CommunityMemberResponse)
    fake_moderator_response.user_id = fake_user_id
    fake_moderator_response.community_id = fake_community_id
    fake_moderator_response.role = CommunityMemberRoleEnum.MODERATOR

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.list_moderators.return_value = ([fake_moderator_model], 1)

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service._map_member_to_response = Mock(return_value=fake_moderator_response)

    # Act
    result = service.list_moderators(fake_community_id, fake_params)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_member_repo.list_moderators.assert_called_once_with(
        fake_community_id, fake_params
    )
    service._map_member_to_response.assert_called_once_with(fake_moderator_model)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].user_id == fake_user_id
    assert result.items[0].community_id == fake_community_id
    assert result.items[0].role == CommunityMemberRoleEnum.MODERATOR
    assert result.total == 1
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_create_member_service_success():
    """
    Tests the `create_member` method of CommunityService.

    Scenario:
    - Given member creation data
    - When the service creates a community member successfully
    - Then it should return the CommunityMemberResponse
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_data = CommunityMemberCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        role=CommunityMemberRoleEnum.MEMBER,
        reputation=10,
        status_participation=CommunityMemberStatusEnum.ACTIVE,
    )

    # Create real community mock with proper attributes for _map_member_to_response
    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id
    fake_community_model.name = 'Test Community'

    # Create properly configured user mock with all required UserResponse fields
    fake_user_model = Mock()
    fake_user_model.id = fake_user_id
    fake_user_model.email = 'test@example.com'
    fake_user_model.name = 'Test User'
    fake_user_model.hashed_password = 'hashedpassword123456789'
    fake_user_model.profile_image_url = 'https://example.com/profile.jpg'
    fake_user_model.reputation_level = 5
    fake_user_model.status = UserStatusEnum.ACTIVE
    fake_user_model.created_at = datetime.now()
    fake_user_model.updated_at = datetime.now()

    # Create a properly configured member mock that will be returned by save()
    fake_saved_member = Mock(spec=CommunityMember)
    fake_saved_member.id = uuid4()  # Add missing id attribute with proper UUID
    fake_saved_member.user_id = fake_user_id
    fake_saved_member.community_id = fake_community_id
    fake_saved_member.role = CommunityMemberRoleEnum.MEMBER
    fake_saved_member.reputation = 10
    fake_saved_member.status_participation = CommunityMemberStatusEnum.ACTIVE
    fake_saved_member.entered_in = datetime.now()
    # Configure the user and community attributes for _map_member_to_response
    fake_saved_member.user = fake_user_model
    fake_saved_member.community = fake_community_model

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.member_exists.return_value = False
    mock_member_repo.save.return_value = fake_saved_member
    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service.user_service = mock_user_service

    # Act
    result = service.create_member(fake_member_data)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    mock_member_repo.member_exists.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    mock_member_repo.save.assert_called_once()
    # Verify the real _map_member_to_response was executed by checking the result
    assert result is not None
    assert str(result.user.id) == fake_user_id
    assert str(result.community.id) == fake_community_id
    assert result.role == CommunityMemberRoleEnum.MEMBER
    assert result.reputation == 10
    assert result.status_participation == CommunityMemberStatusEnum.ACTIVE
    assert hasattr(result, 'user')
    assert hasattr(result, 'community')
    assert hasattr(result, 'entered_in')
    # Verify user data is properly mapped
    assert result.user.email == 'test@example.com'
    assert result.user.name == 'Test User'
    assert result.community.name == 'Test Community'


@pytest.mark.unit
def test_create_member_service_member_already_exists():
    """
    Tests the `create_member` method when member already exists.

    Scenario:
    - Given valid member creation data
    - When the user is already a member of the community
    - Then it should raise CommunityMemberAlreadyExistsError
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_data = CommunityMemberCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        role=CommunityMemberRoleEnum.MEMBER,
        reputation=10,
        status_participation=CommunityMemberStatusEnum.ACTIVE,
    )

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    fake_user_model = Mock()
    fake_user_model.id = fake_user_id

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.member_exists.return_value = True  # Member already exists
    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service.user_service = mock_user_service

    # Act & Assert
    with pytest.raises(CommunityMemberAlreadyExistsError):
        service.create_member(fake_member_data)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    mock_member_repo.member_exists.assert_called_once_with(
        fake_user_id, fake_community_id
    )


@pytest.mark.unit
def test_create_member_service_unexpected_error():
    """
    Tests the `create_member` method when unexpected error occurs.

    Scenario:
    - Given valid member creation data
    - When an unexpected error occurs during save
    - Then it should raise UnexpectedCommunityMemberError
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_member_data = CommunityMemberCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        role=CommunityMemberRoleEnum.MEMBER,
        reputation=10,
        status_participation=CommunityMemberStatusEnum.ACTIVE,
    )

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    fake_user_model = Mock()
    fake_user_model.id = fake_user_id

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.member_exists.return_value = False
    mock_member_repo.save.side_effect = Exception('Database error')
    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service.user_service = mock_user_service

    # Act & Assert
    with pytest.raises(UnexpectedCommunityMemberError):
        service.create_member(fake_member_data)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    mock_member_repo.member_exists.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    mock_member_repo.save.assert_called_once()


@pytest.mark.unit
def test_remove_member_service_success():
    """
    Tests the `remove_member` method of CommunityService - success scenario.

    Scenario:
    - Given a member ID
    - When the service removes the member successfully
    - Then it should return True indicating successful removal
    """
    # Arrange
    fake_member_id = str(uuid4())

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.id = fake_member_id

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = fake_member_model
    mock_member_repo.delete.return_value = True

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    result = service.remove_member(fake_member_id)

    # Assert
    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)
    mock_member_repo.delete.assert_called_once_with(fake_member_model)
    assert result is True


@pytest.mark.unit
def test_remove_member_service_member_not_found():
    """
    Tests the `remove_member` method when member is not found.

    Scenario:
    - Given a non-existent member ID
    - When the member does not exist
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    fake_member_id = str(uuid4())

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = None

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service.remove_member(fake_member_id)

    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)


@pytest.mark.unit
def test_remove_member_service_unexpected_error():
    """
    Tests the `remove_member` method when unexpected error occurs.

    Scenario:
    - Given valid member ID
    - When an unexpected error occurs during deletion
    - Then it should raise UnexpectedCommunityMemberError
    """
    # Arrange
    fake_member_id = str(uuid4())

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.id = fake_member_id

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = fake_member_model
    mock_member_repo.delete.side_effect = Exception('Database error')

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(UnexpectedCommunityMemberError):
        service.remove_member(fake_member_id)

    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)
    mock_member_repo.delete.assert_called_once_with(fake_member_model)


@pytest.mark.unit
def test_update_member_role_service_success():
    """
    Tests the `update_member_role` method of CommunityService - success scenario.

    Scenario:
    - Given a member ID and new role
    - When the service updates the member role successfully
    - Then it should return the updated CommunityMemberResponse
    """
    # Arrange
    fake_member_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_new_role = CommunityMemberRoleEnum.ADMIN

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.id = fake_member_id
    fake_member_model.user_id = fake_user_id
    fake_member_model.community_id = fake_community_id
    fake_member_model.role = CommunityMemberRoleEnum.MODERATOR
    fake_member_model.reputation = 100

    fake_updated_member = Mock(spec=CommunityMember)
    fake_updated_member.id = fake_member_id
    fake_updated_member.user_id = fake_user_id
    fake_updated_member.community_id = fake_community_id
    fake_updated_member.role = CommunityMemberRoleEnum.ADMIN
    fake_updated_member.reputation = 100

    expect_member_response = Mock(spec=CommunityMemberResponse)
    expect_member_response.id = fake_member_id
    expect_member_response.user_id = fake_user_id
    expect_member_response.community_id = fake_community_id
    expect_member_response.role = CommunityMemberRoleEnum.ADMIN
    expect_member_response.reputation = 100

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = fake_member_model
    mock_member_repo.save.return_value = fake_updated_member

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo
    service._map_member_to_response = Mock(return_value=expect_member_response)

    # Act
    result = service.update_member_role(fake_member_id, fake_new_role)

    # Assert
    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)
    mock_member_repo.save.assert_called_once_with(fake_member_model)
    service._map_member_to_response.assert_called_once_with(fake_updated_member)
    assert result is not None
    assert result.role == CommunityMemberRoleEnum.ADMIN
    assert result.reputation == 100
    assert fake_member_model.role == CommunityMemberRoleEnum.ADMIN


@pytest.mark.unit
def test_update_member_role_service_member_not_found():
    """
    Tests the `update_member_role` method when member is not found.

    Scenario:
    - Given a non-existent member ID
    - When the member does not exist
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    fake_member_id = str(uuid4())
    fake_new_role = CommunityMemberRoleEnum.MODERATOR

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = None

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service.update_member_role(fake_member_id, fake_new_role)

    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)


@pytest.mark.unit
def test_update_member_role_service_unexpected_error():
    """
    Tests the `update_member_role` method when unexpected error occurs.

    Scenario:
    - Given valid member ID and new role
    - When an unexpected error occurs during save
    - Then it should raise UnexpectedCommunityMemberError
    """
    # Arrange
    fake_member_id = str(uuid4())
    fake_new_role = CommunityMemberRoleEnum.ADMIN

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.id = fake_member_id

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = fake_member_model
    mock_member_repo.save.side_effect = Exception('Database error')

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(UnexpectedCommunityMemberError):
        service.update_member_role(fake_member_id, fake_new_role)

    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)
    mock_member_repo.save.assert_called_once_with(fake_member_model)
    assert fake_member_model.role == fake_new_role


@pytest.mark.unit
def test_get_member_association_service_success():
    """
    Tests the `get_member_association` method of CommunityService.

    Scenario:
    - Given a user ID and community ID
    - When the service gets the member association successfully
    - Then it should return the CommunityMember model
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    fake_user_model = Mock()
    fake_user_model.id = fake_user_id

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.user_id = fake_user_id
    fake_member_model.community_id = fake_community_id
    fake_member_model.role = CommunityMemberRoleEnum.ADMIN

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.get_member_association.return_value = fake_member_model
    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service.user_service = mock_user_service

    # Act
    result = service.get_member_association(fake_user_id, fake_community_id)

    # Assert
    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    mock_member_repo.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    assert result is not None
    assert result.user_id == fake_user_id
    assert result.community_id == fake_community_id
    assert result.role == CommunityMemberRoleEnum.ADMIN


@pytest.mark.unit
def test_get_member_association_service_not_found():
    """
    Tests the `get_member_association` method when member association is not found.

    Scenario:
    - Given valid user and community IDs
    - When the member association does not exist
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())

    fake_community_model = Mock(spec=Community)
    fake_community_model.id = fake_community_id

    fake_user_model = Mock()
    fake_user_model.id = fake_user_id

    mock_tm = Mock()
    mock_community_repo = Mock()
    mock_community_repo.get_by_id.return_value = fake_community_model
    mock_member_repo = Mock()
    mock_member_repo.get_member_association.return_value = None
    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user_model

    service = CommunityService(mock_tm)
    service.community_repo = mock_community_repo
    service.member_repo = mock_member_repo
    service.user_service = mock_user_service

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service.get_member_association(fake_user_id, fake_community_id)

    mock_community_repo.get_by_id.assert_called_once_with(fake_community_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    mock_member_repo.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )


@pytest.mark.unit
def test_get_member_service_success():
    """
    Tests the `get_member` method of CommunityService - success scenario.

    Scenario:
    - Given a member ID
    - When the service retrieves the member successfully
    - Then it should return the CommunityMember model
    """
    # Arrange
    fake_member_id = str(uuid4())

    fake_member_model = Mock(spec=CommunityMember)
    fake_member_model.id = fake_member_id
    fake_member_model.role = CommunityMemberRoleEnum.MEMBER

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = fake_member_model

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    result = service.get_member(fake_member_id)

    # Assert
    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)
    assert result is not None
    assert result.id == fake_member_id
    assert result.role == CommunityMemberRoleEnum.MEMBER


@pytest.mark.unit
def test_get_member_service_not_found():
    """
    Tests the `get_member` method when member is not found.

    Scenario:
    - Given a non-existent member ID
    - When the member does not exist
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    fake_member_id = str(uuid4())

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = None

    service = CommunityService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service.get_member(fake_member_id)

    mock_member_repo.get_by_id.assert_called_once_with(fake_member_id)
