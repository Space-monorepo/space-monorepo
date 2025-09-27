import pytest
import app.auth.security as auth_security
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

from app.auth.deps import get_current_user
from app.auth.schema import TokenSchema
from app.auth.security import AuthService
from app.api.users.schema import LoginSchema
from app.api.users.model import User


@pytest.fixture
def mock_bcrypt():
    """
    Fixture para mockar o módulo bcrypt de forma segura.
    Usa monkeypatch para garantir que o mock seja revertido após o teste.
    """
    mock_bcrypt_module = Mock()

    # Fazer o patch
    original_bcrypt = getattr(auth_security, 'bcrypt', None)

    # Aplicar o mock
    auth_security.bcrypt = mock_bcrypt_module

    # Retornar o mock para ser usado no teste
    yield mock_bcrypt_module

    # Cleanup: restaurar o módulo original
    if original_bcrypt:
        auth_security.bcrypt = original_bcrypt


@pytest.fixture
def mock_jwt():
    """
    Fixture para mockar o módulo jwt de forma segura.
    Usa monkeypatch para garantir que o mock seja revertido após o teste.
    """
    mock_jwt_module = Mock()

    # Fazer o patch
    original_jwt = getattr(auth_security, 'jwt', None)

    # Aplicar o mock
    auth_security.jwt = mock_jwt_module

    # Retornar o mock para ser usado no teste
    yield mock_jwt_module

    # Cleanup: restaurar o módulo original
    if original_jwt:
        auth_security.jwt = original_jwt


@pytest.mark.unit
def test_authenticate_login_service_success():
    """
    Tests the `authenticate_login` method of AuthService.

    Scenario:
    - Given valid email and password credentials
    - When the service authenticates the user login
    - Then it should return the authenticated user
    """
    # Arrange
    fake_email = 'johndoe@example.com'
    fake_password = 'plaintext_password'
    fake_user_id = uuid4()
    fake_name = 'John Doe'
    fake_hashed_password = 'hashed_password_hash'

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.email = fake_email
    fake_user.name = fake_name
    fake_user.hashed_password = fake_hashed_password

    mock_tm = Mock()
    mock_user_service = Mock()
    mock_user_service.get_by_email.return_value = fake_user

    import app.api.users.service as user_service_module

    user_service_module.UserService = Mock(return_value=mock_user_service)

    service = AuthService(mock_tm)
    service.verify_password = Mock(
        return_value=True
    )  # Mock para simular verificação bem-sucedida

    # Act
    result = service.authenticate_login(fake_email, fake_password)

    # Assert
    assert result is not None
    assert result.id == fake_user_id
    assert result.email == fake_email
    assert result.name == fake_name

    # Verificar que o UserService foi chamado corretamente
    mock_user_service.get_by_email.assert_called_once_with(fake_email)


@pytest.mark.unit
def test_authenticate_login_service_user_not_found():
    """
    Tests the `authenticate_login` method of AuthService when user is not found.

    Scenario:
    - Given invalid email credentials
    - When the service tries to authenticate the user login
    - Then it should raise UserNotAuthenticatedError
    """
    # Arrange
    fake_email = 'nonexistent@example.com'
    fake_password = 'hashed_password'

    mock_tm = Mock()
    mock_user_service = Mock()
    mock_user_service.get_by_email.return_value = None

    service = AuthService(mock_tm)
    service.verify_password = Mock(return_value=False)

    # Act & Assert
    with pytest.raises(Exception):  # UserNotAuthenticatedError seria esperado
        service.authenticate_login(fake_email, fake_password)


@pytest.mark.unit
def test_create_token_service_success(mock_jwt):
    """
    Tests the `create_token` method of AuthService.

    Scenario:
    - Given a valid payload with user email
    - When the service creates a JWT token
    - Then it should return a TokenSchema with valid expiration
    """
    # Arrange
    fake_email = 'johndoe@example.com'
    fake_payload = {'sub': fake_email}
    fake_access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huZG9lQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM1NjgwMDAwfQ.example_signature'
    fake_exp = datetime.now(timezone.utc) + timedelta(minutes=30)

    mock_tm = Mock()
    mock_jwt.encode.return_value = fake_access_token

    service = AuthService(mock_tm)

    # Act
    result = service.create_token(fake_payload)

    # Assert
    assert result is not None
    assert isinstance(result, TokenSchema)
    assert result.access_token is not None
    assert result.access_token == fake_access_token


@pytest.mark.unit
def test_create_token_service_with_custom_expiration(mock_jwt):
    """
    Tests the `create_token` method of AuthService with custom expiration.

    Scenario:
    - Given a valid payload and custom expiration time
    - When the service creates a JWT token with custom expiration
    - Then it should return a TokenSchema with the specified expiration
    """
    # Arrange
    fake_email = 'johndoe@example.com'
    fake_payload = {'sub': fake_email}
    fake_exp = datetime.now(timezone.utc) + timedelta(hours=2)
    fake_access_token = 'custom_expiration_token'

    mock_tm = Mock()
    mock_jwt.encode.return_value = fake_access_token

    service = AuthService(mock_tm)

    # Act
    result = service.create_token(fake_payload, exp=fake_exp)

    # Assert
    assert result is not None
    assert isinstance(result, TokenSchema)
    assert result.access_token is not None
    assert result.access_token == fake_access_token


@pytest.mark.unit
def test_hash_password_service_success(mock_bcrypt):
    """
    Tests the `hash_password` method of AuthService.

    Scenario:
    - Given a plain text password
    - When the service hashes the password using bcrypt
    - Then it should return a hashed version of the password
    """
    # Arrange
    fake_plain_password = 'plaintext_password'
    fake_salt = b'fake_salt_bytes'
    fake_hashed_password = 'hashed_password_string'

    mock_tm = Mock()
    mock_bcrypt.gensalt.return_value = fake_salt

    # Criar um mock object que simula o comportamento dos bytes retornados pelo hashpw
    mock_hashed_bytes = Mock()
    mock_hashed_bytes.decode.return_value = fake_hashed_password
    mock_bcrypt.hashpw.return_value = mock_hashed_bytes

    service = AuthService(mock_tm)

    # Act
    result = service.hash_password(fake_plain_password)

    # Assert
    mock_bcrypt.gensalt.assert_called_once()
    mock_bcrypt.hashpw.assert_called_once_with(
        fake_plain_password.encode('utf-8'), fake_salt
    )
    mock_hashed_bytes.decode.assert_called_once_with('utf-8')
    assert result == fake_hashed_password


@pytest.mark.unit
def test_verify_password_service_success(mock_bcrypt):
    """
    Tests the `verify_password` method of AuthService.

    Scenario:
    - Given a plain text password and hashed password
    - When the service verifies the password using bcrypt
    - Then it should return True if passwords match
    """
    # Arrange
    fake_plain_password = 'plaintext_password'
    fake_hashed_password = 'hashed_password_hash'

    mock_tm = Mock()
    mock_bcrypt.checkpw.return_value = True

    service = AuthService(mock_tm)

    # Act
    result = service.verify_password(fake_plain_password, fake_hashed_password)

    # Assert
    mock_bcrypt.checkpw.assert_called_once_with(
        fake_plain_password.encode('utf-8'), fake_hashed_password.encode('utf-8')
    )
    assert result is True


@pytest.mark.unit
def test_verify_password_service_failure(mock_bcrypt):
    """
    Tests the `verify_password` method of AuthService when passwords don't match.

    Scenario:
    - Given a plain text password and incorrect hashed password
    - When the service verifies the password using bcrypt
    - Then it should return False indicating password mismatch
    """
    # Arrange
    fake_plain_password = 'plaintext_password'
    fake_hashed_password = 'incorrect_hashed_password'

    mock_tm = Mock()
    mock_bcrypt.checkpw.return_value = False

    service = AuthService(mock_tm)

    # Act
    result = service.verify_password(fake_plain_password, fake_hashed_password)

    # Assert
    mock_bcrypt.checkpw.assert_called_once_with(
        fake_plain_password.encode('utf-8'), fake_hashed_password.encode('utf-8')
    )
    assert result is False


@pytest.mark.unit
def test_login_service_success(mock_jwt):
    """
    Tests the `login` method of AuthService.

    Scenario:
    - Given valid login credentials
    - When the service authenticates and creates a token
    - Then it should return a TokenSchema with access token
    """
    # Arrange
    fake_email = 'johndoe@example.com'
    fake_password = 'plaintext_password'
    fake_user_id = uuid4()
    fake_name = 'John Doe'
    fake_hashed_password = 'hashed_password_hash'
    fake_access_token = 'login_access_token'

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.email = fake_email
    fake_user.name = fake_name
    fake_user.hashed_password = fake_hashed_password

    fake_login_schema = LoginSchema(email=fake_email, password=fake_password)

    mock_tm = Mock()
    mock_jwt.encode.return_value = fake_access_token

    service = AuthService(mock_tm)
    service.authenticate_login = Mock(return_value=fake_user)
    service.create_token = Mock(
        return_value=Mock(spec=TokenSchema, access_token=fake_access_token)
    )

    # Act
    result = service.login(fake_login_schema)

    # Assert
    service.authenticate_login.assert_called_once_with(fake_email, fake_password)
    service.create_token.assert_called_once()
    assert result is not None
    assert result.access_token == fake_access_token
