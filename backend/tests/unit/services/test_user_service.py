from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.api.users.exceptions import (
    ConnectionAlreadyExistsError,
    ConnectionCooldownError,
    ConnectionNotFoundError,
    SelfConnectionError,
)
from app.api.users.model import User, UserConnection
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
    fake_email = 'johndoe@example.com'
    fake_name = 'John Doe'
    fake_hashed_password = 'hashed_password'
    fake_profile_image_url = None
    fake_reputation_level = 1
    fake_status = 'pending'
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
    service.get_by_email = Mock(
        return_value=None
    )  # Mock para simular que usuário não existe

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
    fake_user_id = str(uuid4())
    fake_email = 'johndoe@example.com'
    fake_name = 'John Doe'

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
    assert str(result.id) == fake_user_id
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
    fake_email = 'johndoe@example.com'
    fake_user_id = uuid4()
    fake_name = 'John Doe'

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
    fake_user_id = str(uuid4())
    fake_old_email = 'johndoe@example.com'
    fake_new_email = 'new_johndoe@example.com'
    fake_name = 'John Doe'

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
    assert str(result.id) == fake_user_id
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


@pytest.mark.unit
def test_request_connection_service_success():
    """
    Tests the `request_connection` method of UserService - success scenario.

    Scenario:
    - Given valid requester and addressee IDs
    - When the service creates a connection request successfully
    - Then it should return the created UserConnection
    """
    # Arrange
    fake_requester_id = uuid4()
    fake_addressee_id = uuid4()
    fake_connection_id = uuid4()

    fake_requester = Mock(spec=User)
    fake_requester.id = fake_requester_id

    fake_addressee = Mock(spec=User)
    fake_addressee.id = fake_addressee_id

    fake_connection = Mock(spec=UserConnection)
    fake_connection.id = fake_connection_id
    fake_connection.requester_id = fake_requester_id
    fake_connection.addressee_id = fake_addressee_id
    fake_connection.status = 'pending'

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.check_existing_connection.return_value = None
    mock_connection_repo.check_rejection_cooldown.return_value = False
    mock_connection_repo.create_connection_request.return_value = fake_connection

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo
    service.get_user = Mock(side_effect=[fake_requester, fake_addressee])

    # Act
    result = service.request_connection(fake_requester_id, fake_addressee_id)

    # Assert
    service.get_user.assert_any_call(fake_requester_id)
    service.get_user.assert_any_call(fake_addressee_id)
    mock_connection_repo.check_existing_connection.assert_called_once_with(
        fake_requester_id, fake_addressee_id
    )
    mock_connection_repo.check_rejection_cooldown.assert_called_once_with(
        fake_requester_id, fake_addressee_id
    )
    mock_connection_repo.create_connection_request.assert_called_once_with(
        fake_requester_id, fake_addressee_id
    )
    assert result == fake_connection
    assert result.status == 'pending'


@pytest.mark.unit
def test_request_connection_service_self_connection_error():
    """
    Tests the `request_connection` method of UserService - self connection error.

    Scenario:
    - Given same requester and addressee IDs
    - When the service attempts to create a self-connection
    - Then it should raise SelfConnectionError
    """
    # Arrange
    fake_user_id = uuid4()

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id

    mock_tm = Mock()
    service = UserService(mock_tm)
    service.get_user = Mock(return_value=fake_user)

    # Act & Assert
    with pytest.raises(SelfConnectionError) as exc_info:
        service.request_connection(fake_user_id, fake_user_id)

    assert str(exc_info.value) == 'Cannot send connection request to yourself'
    service.get_user.assert_any_call(fake_user_id)


@pytest.mark.unit
def test_request_connection_service_already_exists_error():
    """
    Tests the `request_connection` method of UserService - connection already exists.

    Scenario:
    - Given valid requester and addressee IDs with existing connection
    - When the service attempts to create a duplicate connection
    - Then it should raise ConnectionAlreadyExistsError
    """
    # Arrange
    fake_requester_id = uuid4()
    fake_addressee_id = uuid4()

    fake_requester = Mock(spec=User)
    fake_addressee = Mock(spec=User)

    fake_existing_connection = Mock(spec=UserConnection)

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.check_existing_connection.return_value = (
        fake_existing_connection
    )

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo
    service.get_user = Mock(side_effect=[fake_requester, fake_addressee])

    # Act & Assert
    with pytest.raises(ConnectionAlreadyExistsError) as exc_info:
        service.request_connection(fake_requester_id, fake_addressee_id)

    assert str(exc_info.value) == 'Connection already exists between these users'
    mock_connection_repo.check_existing_connection.assert_called_once()


@pytest.mark.unit
def test_request_connection_service_cooldown_error():
    """
    Tests the `request_connection` method of UserService - rejection cooldown active.

    Scenario:
    - Given valid requester and addressee IDs with active rejection cooldown
    - When the service attempts to create a connection during cooldown
    - Then it should raise ConnectionCooldownError
    """
    # Arrange
    fake_requester_id = uuid4()
    fake_addressee_id = uuid4()

    fake_requester = Mock(spec=User)
    fake_addressee = Mock(spec=User)

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.check_existing_connection.return_value = None
    mock_connection_repo.check_rejection_cooldown.return_value = True

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo
    service.get_user = Mock(side_effect=[fake_requester, fake_addressee])

    # Act & Assert
    with pytest.raises(ConnectionCooldownError) as exc_info:
        service.request_connection(fake_requester_id, fake_addressee_id)

    assert (
        str(exc_info.value)
        == 'Cannot send connection request. Please wait 1 hour after rejection'
    )
    mock_connection_repo.check_rejection_cooldown.assert_called_once()


@pytest.mark.unit
def test_accept_connection_service_success():
    """
    Tests the `accept_connection` method of UserService - success scenario.

    Scenario:
    - Given valid connection ID and user ID
    - When the service accepts the connection successfully
    - Then it should return the accepted UserConnection
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    fake_connection = Mock(spec=UserConnection)
    fake_connection.id = fake_connection_id
    fake_connection.status = 'accepted'

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.accept_connection.return_value = fake_connection

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.accept_connection(fake_connection_id, fake_user_id)

    # Assert
    mock_connection_repo.accept_connection.assert_called_once_with(
        fake_connection_id, fake_user_id
    )
    assert result == fake_connection
    assert result.status == 'accepted'


@pytest.mark.unit
def test_accept_connection_service_not_found_error():
    """
    Tests the `accept_connection` method of UserService - connection not found.

    Scenario:
    - Given invalid connection ID or unauthorized user
    - When the service attempts to accept non-existent connection
    - Then it should raise ConnectionNotFoundError
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.accept_connection.return_value = None

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act & Assert
    with pytest.raises(ConnectionNotFoundError) as exc_info:
        service.accept_connection(fake_connection_id, fake_user_id)

    assert (
        str(exc_info.value)
        == 'Connection not found or you are not authorized to accept this request'
    )
    mock_connection_repo.accept_connection.assert_called_once()


@pytest.mark.unit
def test_reject_connection_service_success():
    """
    Tests the `reject_connection` method of UserService - success scenario.

    Scenario:
    - Given valid connection ID and user ID
    - When the service rejects the connection successfully
    - Then it should return the rejected UserConnection
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    fake_connection = Mock(spec=UserConnection)
    fake_connection.id = fake_connection_id
    fake_connection.status = 'rejected'

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.reject_connection.return_value = fake_connection

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.reject_connection(fake_connection_id, fake_user_id)

    # Assert
    mock_connection_repo.reject_connection.assert_called_once_with(
        fake_connection_id, fake_user_id
    )
    assert result == fake_connection
    assert result.status == 'rejected'


@pytest.mark.unit
def test_reject_connection_service_not_found_error():
    """
    Tests the `reject_connection` method of UserService - connection not found.

    Scenario:
    - Given invalid connection ID or unauthorized user
    - When the service attempts to reject non-existent connection
    - Then it should raise ConnectionNotFoundError
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.reject_connection.return_value = None

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act & Assert
    with pytest.raises(ConnectionNotFoundError) as exc_info:
        service.reject_connection(fake_connection_id, fake_user_id)

    assert (
        str(exc_info.value)
        == 'Connection not found or you are not authorized to reject this request'
    )
    mock_connection_repo.reject_connection.assert_called_once()


@pytest.mark.unit
def test_delete_connection_service_success():
    """
    Tests the `delete_connection` method of UserService - success scenario.

    Scenario:
    - Given valid connection ID and user ID
    - When the service deletes the connection successfully
    - Then it should return True
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.delete_connection.return_value = True

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.delete_connection(fake_connection_id, fake_user_id)

    # Assert
    mock_connection_repo.delete_connection.assert_called_once_with(
        fake_connection_id, fake_user_id
    )
    assert result is True


@pytest.mark.unit
def test_delete_connection_service_not_found_error():
    """
    Tests the `delete_connection` method of UserService - connection not found.

    Scenario:
    - Given invalid connection ID or unauthorized user
    - When the service attempts to delete non-existent connection
    - Then it should raise ConnectionNotFoundError
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.delete_connection.return_value = False

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act & Assert
    with pytest.raises(ConnectionNotFoundError) as exc_info:
        service.delete_connection(fake_connection_id, fake_user_id)

    assert (
        str(exc_info.value)
        == 'Connection not found or you are not authorized to delete this connection'
    )
    mock_connection_repo.delete_connection.assert_called_once()


@pytest.mark.unit
def test_get_connection_service_success():
    """
    Tests the `get_connection` method of UserService - success scenario.

    Scenario:
    - Given valid connection ID
    - When the service retrieves the connection successfully
    - Then it should return the UserConnection
    """
    # Arrange
    fake_connection_id = uuid4()

    fake_connection = Mock(spec=UserConnection)
    fake_connection.id = fake_connection_id

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.get_connection_by_id.return_value = fake_connection

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.get_connection(fake_connection_id)

    # Assert
    mock_connection_repo.get_connection_by_id.assert_called_once_with(fake_connection_id)
    assert result == fake_connection


@pytest.mark.unit
def test_get_connection_service_not_found_error():
    """
    Tests the `get_connection` method of UserService - connection not found.

    Scenario:
    - Given invalid connection ID
    - When the service attempts to retrieve non-existent connection
    - Then it should raise ConnectionNotFoundError
    """
    # Arrange
    fake_connection_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.get_connection_by_id.return_value = None

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act & Assert
    with pytest.raises(ConnectionNotFoundError) as exc_info:
        service.get_connection(fake_connection_id)

    assert str(exc_info.value) == 'Connection not found'
    mock_connection_repo.get_connection_by_id.assert_called_once()


@pytest.mark.unit
def test_get_connection_status_service_success():
    """
    Tests the `get_connection_status` method of UserService - success scenario.

    Scenario:
    - Given valid user IDs with existing connection
    - When the service checks connection status
    - Then it should return the UserConnection
    """
    # Arrange
    fake_user1_id = uuid4()
    fake_user2_id = uuid4()

    fake_connection = Mock(spec=UserConnection)
    fake_connection.requester_id = fake_user1_id
    fake_connection.addressee_id = fake_user2_id
    fake_connection.status = 'accepted'

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.check_existing_connection.return_value = fake_connection

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.get_connection_status(fake_user1_id, fake_user2_id)

    # Assert
    mock_connection_repo.check_existing_connection.assert_called_once_with(
        fake_user1_id, fake_user2_id
    )
    assert result == fake_connection


@pytest.mark.unit
def test_get_connection_status_service_no_connection():
    """
    Tests the `get_connection_status` method of UserService - no connection exists.

    Scenario:
    - Given valid user IDs with no existing connection
    - When the service checks connection status
    - Then it should return None
    """
    # Arrange
    fake_user1_id = uuid4()
    fake_user2_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.check_existing_connection.return_value = None

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.get_connection_status(fake_user1_id, fake_user2_id)

    # Assert
    mock_connection_repo.check_existing_connection.assert_called_once_with(
        fake_user1_id, fake_user2_id
    )
    assert result is None


@pytest.mark.unit
def test_validate_connection_participation_service_success():
    """
    Tests the `validate_connection_participation` method of UserService - success scenario.

    Scenario:
    - Given valid connection ID and user ID
    - When the service validates user participation
    - Then it should return True
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.validate_user_participation.return_value = True

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.validate_connection_participation(fake_connection_id, fake_user_id)

    # Assert
    mock_connection_repo.validate_user_participation.assert_called_once_with(
        fake_connection_id, fake_user_id
    )
    assert result is True


@pytest.mark.unit
def test_validate_connection_participation_service_false():
    """
    Tests the `validate_connection_participation` method of UserService - user not participant.

    Scenario:
    - Given connection ID and non-participant user ID
    - When the service validates user participation
    - Then it should return False
    """
    # Arrange
    fake_connection_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_connection_repo = Mock()
    mock_connection_repo.validate_user_participation.return_value = False

    service = UserService(mock_tm)
    service.connection_repo = mock_connection_repo

    # Act
    result = service.validate_connection_participation(fake_connection_id, fake_user_id)

    # Assert
    mock_connection_repo.validate_user_participation.assert_called_once_with(
        fake_connection_id, fake_user_id
    )
    assert result is False
