import pytest
from unittest.mock import Mock
from uuid import uuid4

from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.api.users.model import User


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection for testing."""
    websocket = Mock(spec=WebSocket)
    websocket.client = Mock()
    websocket.client.host = "127.0.0.1"
    websocket.headers = {}
    websocket.query_params = {}
    return websocket


@pytest.fixture
def mock_authenticated_websocket(mock_websocket):
    """Create a mock authenticated WebSocket with token."""
    mock_websocket.query_params = {"token": "valid_jwt_token"}
    mock_websocket.headers = {
        "authorization": "Bearer valid_jwt_token",
        "x-forwarded-for": "192.168.1.1",
    }
    return mock_websocket


@pytest.fixture
def mock_user():
    """Create a mock User object for testing."""
    user = Mock(spec=User)
    user.id = uuid4()
    user.email = "test@example.com"
    user.name = "Test User"
    user.status = "active"
    return user


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = Mock(spec=Session)
    return session


@pytest.fixture
def websocket_auth():
    """Create a WebSocketAuth instance for testing."""
    from app.core.websocket.auth import WebSocketAuth
    auth = WebSocketAuth()
    # Clear any existing state
    auth._connection_limits.clear()
    auth._active_sessions.clear()
    auth._started = False
    return auth
