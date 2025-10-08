import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime

from app.api.rating.model import Rating
from app.api.rating.schema import RatingCreate, RatingUpdate, RatingResponse
from app.api.rating.service import RatingService
from app.api.rating.exceptions import (
    RatingNotFoundError,
    RatingAlreadyExistsError,
    UnexpectedRatingError,
)
from app.api.communities.exceptions import (
    CommunityNotFoundError,
    CommunityMemberNotFoundError,
)
from app.api.communities.schema import CommunityResponse, CommunityMemberResponse
from app.utils.schema import PaginationSearchParams, PaginationResponse


@pytest.mark.unit
def test_create_rating_service_success():
    """
    Tests the `create_rating` method of RatingService - success scenario.

    Scenario:
    - Given valid rating creation data for a community member
    - When the service creates the rating successfully
    - Then it should return the expected RatingResponse
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_datetime = datetime.now()

    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=5,
        title='Excellent Community!',
        description='Great experience with this community',
    )

    mock_community = Mock(spec=CommunityResponse)
    mock_community.id = fake_community_id

    mock_member = Mock(spec=CommunityMemberResponse)
    mock_member.user_id = fake_user_id
    mock_member.community_id = fake_community_id

    expect_rating_model = Mock(spec=Rating)
    expect_rating_model.id = fake_rating_id
    expect_rating_model.user_id = fake_user_id
    expect_rating_model.community_id = fake_community_id
    expect_rating_model.rating = 5
    expect_rating_model.title = 'Excellent Community!'
    expect_rating_model.description = 'Great experience with this community'
    expect_rating_model.created_at = fake_datetime
    expect_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.save.return_value = expect_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(return_value=mock_community)
    service.community_service.get_member_association = Mock(return_value=mock_member)

    # Act
    result = service.create_rating(fake_rating_data)

    # Assert
    service.community_service.get_community.assert_called_once_with(fake_community_id)
    service.community_service.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    mock_rating_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, RatingResponse)


@pytest.mark.unit
def test_create_rating_service_without_description_success():
    """
    Tests the `create_rating` method of RatingService - success scenario without description.

    Scenario:
    - Given valid rating creation data without description
    - When the service creates the rating successfully
    - Then it should return the expected RatingResponse with null description
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_datetime = datetime.now()

    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=3,
        title='Average Community',
        description=None,
    )

    mock_community = Mock(spec=CommunityResponse)
    mock_member = Mock(spec=CommunityMemberResponse)

    expect_rating_model = Mock(spec=Rating)
    expect_rating_model.id = fake_rating_id
    expect_rating_model.user_id = fake_user_id
    expect_rating_model.community_id = fake_community_id
    expect_rating_model.rating = 3
    expect_rating_model.title = 'Average Community'
    expect_rating_model.description = None
    expect_rating_model.created_at = fake_datetime
    expect_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.save.return_value = expect_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(return_value=mock_community)
    service.community_service.get_member_association = Mock(return_value=mock_member)

    # Act
    result = service.create_rating(fake_rating_data)

    # Assert
    mock_rating_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, RatingResponse)


@pytest.mark.unit
def test_create_rating_service_minimum_rating_success():
    """
    Tests the `create_rating` method of RatingService - success scenario with minimum rating.

    Scenario:
    - Given valid rating creation data with minimum rating (1)
    - When the service creates the rating successfully
    - Then it should return the expected RatingResponse with rating 1
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_datetime = datetime.now()

    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=1,
        title='Poor Community',
        description='Not a good experience',
    )

    mock_community = Mock(spec=CommunityResponse)
    mock_member = Mock(spec=CommunityMemberResponse)

    expect_rating_model = Mock(spec=Rating)
    expect_rating_model.id = uuid4()
    expect_rating_model.user_id = fake_user_id
    expect_rating_model.community_id = fake_community_id
    expect_rating_model.rating = 1
    expect_rating_model.title = 'Poor Community'
    expect_rating_model.description = 'Not a good experience'
    expect_rating_model.created_at = fake_datetime
    expect_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.save.return_value = expect_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(return_value=mock_community)
    service.community_service.get_member_association = Mock(return_value=mock_member)

    # Act
    result = service.create_rating(fake_rating_data)

    # Assert
    mock_rating_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, RatingResponse)


@pytest.mark.unit
def test_create_rating_service_maximum_rating_success():
    """
    Tests the `create_rating` method of RatingService - success scenario with maximum rating.

    Scenario:
    - Given valid rating creation data with maximum rating (5)
    - When the service creates the rating successfully
    - Then it should return the expected RatingResponse with rating 5
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_datetime = datetime.now()

    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=5,
        title='Perfect Community',
        description='Excellent experience',
    )

    mock_community = Mock(spec=CommunityResponse)
    mock_member = Mock(spec=CommunityMemberResponse)

    expect_rating_model = Mock(spec=Rating)
    expect_rating_model.id = uuid4()
    expect_rating_model.user_id = fake_user_id
    expect_rating_model.community_id = fake_community_id
    expect_rating_model.rating = 5
    expect_rating_model.title = 'Perfect Community'
    expect_rating_model.description = 'Excellent experience'
    expect_rating_model.created_at = fake_datetime
    expect_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.save.return_value = expect_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(return_value=mock_community)
    service.community_service.get_member_association = Mock(return_value=mock_member)

    # Act
    result = service.create_rating(fake_rating_data)

    # Assert
    mock_rating_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, RatingResponse)


@pytest.mark.unit
@patch('app.api.rating.service.IntegrityError', Exception)
def test_create_rating_service_rating_already_exists():
    """
    Tests the `create_rating` method of RatingService when user has already rated the community.

    Scenario:
    - Given valid rating creation data for a user who has already rated the community
    - When an IntegrityError occurs during save
    - Then it should raise RatingAlreadyExistsError
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=4,
        title='Another Rating',
        description='This should fail',
    )

    mock_community = Mock(spec=CommunityResponse)
    mock_member = Mock(spec=CommunityMemberResponse)

    mock_tm = Mock()
    mock_rating_repo = Mock()

    # Import IntegrityError to simulate the actual exception
    from sqlalchemy.exc import IntegrityError

    mock_rating_repo.save.side_effect = IntegrityError('', '', '')

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(return_value=mock_community)
    service.community_service.get_member_association = Mock(return_value=mock_member)

    # Act & Assert
    with pytest.raises(
        RatingAlreadyExistsError, match='User has already rated this community'
    ):
        service.create_rating(fake_rating_data)

    service.community_service.get_community.assert_called_once_with(fake_community_id)
    service.community_service.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    mock_rating_repo.save.assert_called_once()


@pytest.mark.unit
def test_create_rating_service_community_not_found():
    """
    Tests the `create_rating` method of RatingService when community does not exist.

    Scenario:
    - Given rating creation data with non-existent community ID
    - When the community service raises CommunityNotFoundError
    - Then it should propagate the CommunityNotFoundError
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=5,
        title='Test Rating',
        description='This should fail',
    )

    mock_tm = Mock()
    mock_rating_repo = Mock()

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(
        side_effect=CommunityNotFoundError('Community not found')
    )

    # Act & Assert
    with pytest.raises(CommunityNotFoundError, match='Community not found'):
        service.create_rating(fake_rating_data)

    service.community_service.get_community.assert_called_once_with(fake_community_id)
    mock_rating_repo.save.assert_not_called()


@pytest.mark.unit
def test_create_rating_service_user_not_member():
    """
    Tests the `create_rating` method of RatingService when user is not a member of the community.

    Scenario:
    - Given rating creation data for a user who is not a member of the community
    - When the community service returns None for the member association
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    fake_user_id = uuid4()
    fake_community_id = uuid4()
    fake_rating_data = RatingCreate(
        user_id=fake_user_id,
        community_id=fake_community_id,
        rating=5,
        title='Test Rating',
        description='This should fail',
    )

    mock_community = Mock(spec=CommunityResponse)

    mock_tm = Mock()
    mock_rating_repo = Mock()

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo
    service.community_service.get_community = Mock(return_value=mock_community)
    service.community_service.get_member_association = Mock(return_value=None)

    # Act & Assert
    with pytest.raises(
        CommunityMemberNotFoundError, match='User is not a member of this community'
    ):
        service.create_rating(fake_rating_data)

    service.community_service.get_community.assert_called_once_with(fake_community_id)
    service.community_service.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    mock_rating_repo.save.assert_not_called()


@pytest.mark.unit
def test_get_rating_service_success():
    """
    Tests the `get_rating` method of RatingService - success scenario.

    Scenario:
    - Given a valid rating ID
    - When the service retrieves the rating successfully
    - Then it should return the expected RatingResponse
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_datetime = datetime.now()

    expect_rating_model = Mock(spec=Rating)
    expect_rating_model.id = fake_rating_id
    expect_rating_model.user_id = uuid4()
    expect_rating_model.community_id = uuid4()
    expect_rating_model.rating = 5
    expect_rating_model.title = 'Test Rating'
    expect_rating_model.description = 'Test Description'
    expect_rating_model.created_at = fake_datetime
    expect_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = expect_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.get_rating(fake_rating_id)

    # Assert
    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    assert result is not None
    assert isinstance(result, RatingResponse)


@pytest.mark.unit
def test_get_rating_service_not_found():
    """
    Tests the `get_rating` method of RatingService when rating is not found.

    Scenario:
    - Given a non-existent rating ID
    - When the repository returns None
    - Then it should raise RatingNotFoundError
    """
    # Arrange
    fake_rating_id = uuid4()

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = None

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act & Assert
    with pytest.raises(RatingNotFoundError, match='Rating not found'):
        service.get_rating(fake_rating_id)

    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)


@pytest.mark.unit
def test_list_ratings_by_community_service_success():
    """
    Tests the `list_ratings_by_community` method of RatingService - success scenario.

    Scenario:
    - Given valid pagination parameters and a community ID
    - When the service lists ratings successfully
    - Then it should return a paginated response with RatingResponse items
    """
    # Arrange
    fake_community_id = uuid4()
    fake_params = PaginationSearchParams(offset=0, limit=10)
    fake_datetime = datetime.now()

    fake_rating_model = Mock(spec=Rating)
    fake_rating_model.id = uuid4()
    fake_rating_model.user_id = uuid4()
    fake_rating_model.community_id = fake_community_id
    fake_rating_model.rating = 5
    fake_rating_model.title = 'Test Rating'
    fake_rating_model.description = 'Test Description'
    fake_rating_model.created_at = fake_datetime
    fake_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.list_ratings_by_community.return_value = ([fake_rating_model], 1)

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.list_ratings_by_community(fake_community_id, fake_params)

    # Assert
    mock_rating_repo.list_ratings_by_community.assert_called_once_with(
        fake_community_id, fake_params
    )
    assert result is not None
    assert isinstance(result, PaginationResponse)
    assert len(result.items) == 1
    assert result.total == 1
    assert result.has_more is False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_ratings_by_community_service_with_pagination_success():
    """
    Tests the `list_ratings_by_community` method of RatingService - success scenario with pagination.

    Scenario:
    - Given pagination parameters with limit 1
    - When the service lists ratings successfully
    - Then it should return a paginated response respecting the limit
    """
    # Arrange
    fake_community_id = uuid4()
    fake_params = PaginationSearchParams(offset=0, limit=1)
    fake_datetime = datetime.now()

    fake_rating_model = Mock(spec=Rating)
    fake_rating_model.id = uuid4()
    fake_rating_model.user_id = uuid4()
    fake_rating_model.community_id = fake_community_id
    fake_rating_model.rating = 5
    fake_rating_model.title = 'Test Rating'
    fake_rating_model.description = 'Test Description'
    fake_rating_model.created_at = fake_datetime
    fake_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.list_ratings_by_community.return_value = ([fake_rating_model], 1)

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.list_ratings_by_community(fake_community_id, fake_params)

    # Assert
    mock_rating_repo.list_ratings_by_community.assert_called_once_with(
        fake_community_id, fake_params
    )
    assert result is not None
    assert isinstance(result, PaginationResponse)
    assert len(result.items) == 1
    assert result.total == 1
    assert result.current_limit == 1


@pytest.mark.unit
def test_list_ratings_by_community_service_empty_success():
    """
    Tests the `list_ratings_by_community` method of RatingService - success scenario with no ratings.

    Scenario:
    - Given a community with no ratings
    - When the service lists ratings successfully
    - Then it should return an empty paginated response
    """
    # Arrange
    fake_community_id = uuid4()
    fake_params = PaginationSearchParams(offset=0, limit=10)

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.list_ratings_by_community.return_value = ([], 0)

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.list_ratings_by_community(fake_community_id, fake_params)

    # Assert
    mock_rating_repo.list_ratings_by_community.assert_called_once_with(
        fake_community_id, fake_params
    )
    assert result is not None
    assert isinstance(result, PaginationResponse)
    assert len(result.items) == 0
    assert result.total == 0
    assert result.has_more is False


@pytest.mark.unit
def test_update_rating_service_success():
    """
    Tests the `update_rating` method of RatingService - success scenario.

    Scenario:
    - Given a valid rating ID and update data
    - When the service updates the rating successfully
    - Then it should return the updated RatingResponse
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_datetime = datetime.now()
    fake_rating_update = RatingUpdate(
        rating=4, title='Updated Title', description='Updated description'
    )

    existing_rating_model = Mock(spec=Rating)
    existing_rating_model.id = fake_rating_id
    existing_rating_model.user_id = uuid4()
    existing_rating_model.community_id = uuid4()
    existing_rating_model.rating = 5
    existing_rating_model.title = 'Original Title'
    existing_rating_model.description = 'Original description'
    existing_rating_model.created_at = fake_datetime
    existing_rating_model.updated_at = fake_datetime

    updated_rating_model = Mock(spec=Rating)
    updated_rating_model.id = fake_rating_id
    updated_rating_model.user_id = existing_rating_model.user_id
    updated_rating_model.community_id = existing_rating_model.community_id
    updated_rating_model.rating = 4
    updated_rating_model.title = 'Updated Title'
    updated_rating_model.description = 'Updated description'
    updated_rating_model.created_at = fake_datetime
    updated_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = existing_rating_model
    mock_rating_repo.save.return_value = updated_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.update_rating(fake_rating_id, fake_rating_update)

    # Assert
    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    mock_rating_repo.save.assert_called_once_with(existing_rating_model)
    assert result is not None
    assert isinstance(result, RatingResponse)


@pytest.mark.unit
def test_update_rating_service_partial_success():
    """
    Tests the `update_rating` method of RatingService - success scenario with partial update.

    Scenario:
    - Given a valid rating ID and partial update data (only rating)
    - When the service updates the rating successfully
    - Then it should return the updated RatingResponse with only the rating changed
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_datetime = datetime.now()
    fake_rating_update = RatingUpdate(rating=2)

    existing_rating_model = Mock(spec=Rating)
    existing_rating_model.id = fake_rating_id
    existing_rating_model.user_id = uuid4()
    existing_rating_model.community_id = uuid4()
    existing_rating_model.rating = 5
    existing_rating_model.title = 'Original Title'
    existing_rating_model.description = 'Original description'
    existing_rating_model.created_at = fake_datetime
    existing_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = existing_rating_model
    mock_rating_repo.save.return_value = existing_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.update_rating(fake_rating_id, fake_rating_update)

    # Assert
    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    mock_rating_repo.save.assert_called_once_with(existing_rating_model)
    assert result is not None
    assert isinstance(result, RatingResponse)
    assert existing_rating_model.rating == 2  # Verify the rating was updated


@pytest.mark.unit
def test_update_rating_service_set_description_to_none_success():
    """
    Tests the `update_rating` method of RatingService - success scenario setting description to None.

    Scenario:
    - Given a valid rating ID and update data with description set to None
    - When the service updates the rating successfully
    - Then it should return the updated RatingResponse with description unchanged (None is not applied)
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_datetime = datetime.now()
    fake_rating_update = RatingUpdate(description=None)

    existing_rating_model = Mock(spec=Rating)
    existing_rating_model.id = fake_rating_id
    existing_rating_model.user_id = uuid4()
    existing_rating_model.community_id = uuid4()
    existing_rating_model.rating = 5
    existing_rating_model.title = 'Original Title'
    existing_rating_model.description = 'Original description'
    existing_rating_model.created_at = fake_datetime
    existing_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = existing_rating_model
    mock_rating_repo.save.return_value = existing_rating_model

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.update_rating(fake_rating_id, fake_rating_update)

    # Assert
    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    mock_rating_repo.save.assert_called_once_with(existing_rating_model)
    assert result is not None
    assert isinstance(result, RatingResponse)
    assert (
        existing_rating_model.description == 'Original description'
    )  # Verify the description was not updated when None


@pytest.mark.unit
def test_update_rating_service_not_found():
    """
    Tests the `update_rating` method of RatingService when rating is not found.

    Scenario:
    - Given a non-existent rating ID and update data
    - When the repository returns None for the rating
    - Then it should raise UnexpectedRatingError (as the service catches all exceptions)
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_rating_update = RatingUpdate(rating=3, title='Updated Title')

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = None

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act & Assert
    with pytest.raises(UnexpectedRatingError, match='Unexpected error updating rating'):
        service.update_rating(fake_rating_id, fake_rating_update)

    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)


@pytest.mark.unit
def test_update_rating_service_unexpected_error():
    """
    Tests the `update_rating` method of RatingService when an unexpected error occurs.

    Scenario:
    - Given a valid rating ID and update data
    - When an unexpected error occurs during update
    - Then it should raise UnexpectedRatingError
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_rating_update = RatingUpdate(rating=3, title='Updated Title')

    existing_rating_model = Mock(spec=Rating)

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = existing_rating_model
    mock_rating_repo.save.side_effect = Exception('Database error')

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act & Assert
    with pytest.raises(UnexpectedRatingError, match='Unexpected error updating rating'):
        service.update_rating(fake_rating_id, fake_rating_update)

    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    mock_rating_repo.save.assert_called_once()


@pytest.mark.unit
def test_delete_rating_service_success():
    """
    Tests the `delete_rating` method of RatingService - success scenario.

    Scenario:
    - Given a valid rating ID
    - When the service deletes the rating successfully
    - Then it should return True
    """
    # Arrange
    fake_rating_id = uuid4()
    fake_datetime = datetime.now()

    existing_rating_model = Mock(spec=Rating)
    existing_rating_model.id = fake_rating_id
    existing_rating_model.user_id = uuid4()
    existing_rating_model.community_id = uuid4()
    existing_rating_model.rating = 5
    existing_rating_model.title = 'Test Rating'
    existing_rating_model.description = 'Test Description'
    existing_rating_model.created_at = fake_datetime
    existing_rating_model.updated_at = fake_datetime

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = existing_rating_model
    mock_rating_repo.delete.return_value = True

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act
    result = service.delete_rating(fake_rating_id)

    # Assert
    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    mock_rating_repo.delete.assert_called_once_with(existing_rating_model)
    assert result is True


@pytest.mark.unit
def test_delete_rating_service_not_found():
    """
    Tests the `delete_rating` method of RatingService when rating is not found.

    Scenario:
    - Given a non-existent rating ID
    - When the repository returns None for the rating
    - Then it should raise UnexpectedRatingError (as the service catches all exceptions)
    """
    # Arrange
    fake_rating_id = uuid4()

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = None

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act & Assert
    with pytest.raises(UnexpectedRatingError, match='Unexpected error deleting rating'):
        service.delete_rating(fake_rating_id)

    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)


@pytest.mark.unit
def test_delete_rating_service_unexpected_error():
    """
    Tests the `delete_rating` method of RatingService when an unexpected error occurs.

    Scenario:
    - Given a valid rating ID
    - When an unexpected error occurs during deletion
    - Then it should raise UnexpectedRatingError
    """
    # Arrange
    fake_rating_id = uuid4()

    existing_rating_model = Mock(spec=Rating)

    mock_tm = Mock()
    mock_rating_repo = Mock()
    mock_rating_repo.get_by_id.return_value = existing_rating_model
    mock_rating_repo.delete.side_effect = Exception('Database error')

    service = RatingService(mock_tm)
    service.rating_repo = mock_rating_repo

    # Act & Assert
    with pytest.raises(UnexpectedRatingError, match='Unexpected error deleting rating'):
        service.delete_rating(fake_rating_id)

    mock_rating_repo.get_by_id.assert_called_once_with(fake_rating_id)
    mock_rating_repo.delete.assert_called_once()
