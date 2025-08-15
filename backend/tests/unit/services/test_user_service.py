import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.api.users.model import User
from app.api.users.schema import UserCreate, UserUpdate
from app.api.users.service import UserService


@pytest.mark.unit
def test_create_user_service_success():
    """
    Tests the `create_user` method of UserService.

    Scenario:
    - Given a valid user creation request
    - When the service creates the user and saves it to repository
    - Then it should return the created user with generated ID
    """
    # Arrange
    fake_email = "johndoe@example.com"
    fake_name = "John Doe"
    fake_hashed_password = "hashed_password"
    fake_profile_image_url = None
    fake_reputation_level = 1
    fake_status = "pending"
    fake_user_id = uuid4()

    fake_user_create = UserCreate(
        email=fake_email,
        name=fake_name,
        hashed_password=fake_hashed_password,
        profile_image_url=fake_profile_image_url,
        reputation_level=fake_reputation_level,
        status=fake_status,
    )

    fake_created_user = Mock(spec=User)
    fake_created_user.id = fake_user_id
    fake_created_user.email = fake_email
    fake_created_user.name = fake_name
    fake_created_user.hashed_password = fake_hashed_password
    fake_created_user.profile_image_url = fake_profile_image_url
    fake_created_user.reputation_level = fake_reputation_level
    fake_created_user.status = fake_status

    mock_tm = Mock()
    mock_user_repo = Mock()
    mock_user_repo.save.return_value = fake_created_user

    service = UserService(mock_tm)
    service.user_repo = mock_user_repo
    service.get_by_email = Mock(return_value=None)  # Mock para simular que usuário não existe

    # Act
    result = service.create_user(fake_user_create)

    # Assert
    mock_user_repo.save.assert_called_once()
    assert result is not None
    assert result.id == fake_user_id
    assert result.email == fake_email
    assert result.name == fake_name
    assert result.hashed_password == fake_hashed_password
    assert result.profile_image_url == fake_profile_image_url
    assert result.reputation_level == fake_reputation_level
    assert result.status == fake_status


@pytest.mark.unit
def test_get_user_service_success():
    """
    Tests the `get_user` method of UserService.

    Scenario:
    - Given a valid user ID
    - When the service retrieves the user from repository
    - Then it should return the expected user
    """
    # Arrange
    fake_user_id = uuid4()
    fake_email = "johndoe@example.com"
    fake_name = "John Doe"

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.email = fake_email
    fake_user.name = fake_name

    mock_tm = Mock()
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = fake_user

    service = UserService(mock_tm)
    service.user_repo = mock_user_repo

    # Act
    result = service.get_user(fake_user_id)

    # Assert
    mock_user_repo.get_by_id.assert_called_once_with(fake_user_id)
    assert result is not None
    assert result.id == fake_user_id
    assert result.email == fake_email
    assert result.name == fake_name


@pytest.mark.unit
def test_get_by_email_service_success():
    """
    Tests the `get_by_email` method of UserService.

    Scenario:
    - Given a valid user email
    - When the service retrieves the user from repository by email
    - Then it should return the expected user
    """
    # Arrange
    fake_email = "johndoe@example.com"
    fake_user_id = uuid4()
    fake_name = "John Doe"

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.email = fake_email
    fake_user.name = fake_name

    mock_tm = Mock()
    mock_user_repo = Mock()
    mock_user_repo.get_by_email.return_value = fake_user

    service = UserService(mock_tm)
    service.user_repo = mock_user_repo

    # Act
    result = service.get_by_email(fake_email)

    # Assert
    mock_user_repo.get_by_email.assert_called_once_with(fake_email)
    assert result is not None
    assert result.id == fake_user_id
    assert result.email == fake_email
    assert result.name == fake_name


@pytest.mark.unit
def test_update_user_service_success():
    """
    Tests the `update_user` method of UserService.

    Scenario:
    - Given a valid user ID and update data
    - When the service updates the user and saves it to repository
    - Then it should return the updated user
    """
    # Arrange
    fake_user_id = uuid4()
    fake_old_email = "johndoe@example.com"
    fake_new_email = "new_johndoe@example.com"
    fake_name = "John Doe"

    fake_user_update = UserUpdate(email=fake_new_email)

    fake_existing_user = Mock(spec=User)
    fake_existing_user.id = fake_user_id
    fake_existing_user.email = fake_old_email
    fake_existing_user.name = fake_name

    fake_updated_user = Mock(spec=User)
    fake_updated_user.id = fake_user_id
    fake_updated_user.email = fake_new_email
    fake_updated_user.name = fake_name

    mock_tm = Mock()
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = fake_existing_user
    mock_user_repo.save.return_value = fake_updated_user

    service = UserService(mock_tm)
    service.user_repo = mock_user_repo

    # Act
    result = service.update_user(fake_user_id, fake_user_update)

    # Assert
    mock_user_repo.get_by_id.assert_called_once_with(fake_user_id)
    mock_user_repo.save.assert_called_once_with(fake_existing_user)
    assert result is not None
    assert result.id == fake_user_id
    assert result.email == fake_new_email
    assert result.name == fake_name


@pytest.mark.unit
def test_delete_user_service_success():
    """
    Tests the `delete_user` method of UserService.

    Scenario:
    - Given a valid user ID
    - When the service deletes the user from repository
    - Then it should return True indicating successful deletion
    """
    # Arrange
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_user_repo = Mock()
    mock_user_repo.delete.return_value = True

    service = UserService(mock_tm)
    service.user_repo = mock_user_repo

    # Act
    result = service.delete_user(fake_user_id)

    # Assert
    mock_user_repo.delete.assert_called_once()
    assert result is True
