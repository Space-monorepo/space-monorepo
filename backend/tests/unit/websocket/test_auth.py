from unittest.mock import patch

import pytest
from fastapi import WebSocketException, status

from app.core.websocket.exceptions import AuthenticationError


class TestWebSocketAuthentication:
    """Test essential WebSocket authentication service functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.core.websocket.auth.WebSocketAuth._validate_jwt_token')
    @patch('app.core.websocket.auth.WebSocketAuth._get_user_from_payload')
    async def test_authenticate_websocket_success(
        self, mock_get_user, mock_validate_token, websocket_auth,
        mock_authenticated_websocket, mock_session, mock_user
    ):
        """Test successful WebSocket authentication."""
        mock_validate_token.return_value = {"sub": "test@example.com", "user_id": str(mock_user.id)}
        mock_get_user.return_value = mock_user

        user = await websocket_auth.authenticate_websocket(
            mock_authenticated_websocket, mock_session
        )

        assert user == mock_user
        assert mock_validate_token.called
        assert mock_get_user.called

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_websocket_no_token_error(
        self, websocket_auth, mock_websocket, mock_session
    ):
        """Test WebSocket authentication without token."""
        mock_websocket.query_params = {}
        mock_websocket.headers = {}

        with pytest.raises(WebSocketException) as exc_info:
            await websocket_auth.authenticate_websocket(mock_websocket, mock_session)

        assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
        assert "Authentication token required" in exc_info.value.reason

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.core.websocket.auth.WebSocketAuth._check_rate_limit')
    async def test_authenticate_websocket_rate_limit_error(
        self, mock_rate_limit, websocket_auth, mock_authenticated_websocket, mock_session
    ):
        """Test WebSocket authentication with rate limit exceeded."""
        mock_rate_limit.return_value = False

        with pytest.raises(WebSocketException) as exc_info:
            await websocket_auth.authenticate_websocket(
                mock_authenticated_websocket, mock_session
            )

        assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
        assert "Rate limit exceeded" in exc_info.value.reason

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('app.core.websocket.auth.WebSocketAuth._validate_jwt_token')
    async def test_authenticate_websocket_invalid_token_error(
        self, mock_validate_token, websocket_auth, mock_authenticated_websocket, mock_session
    ):
        """Test WebSocket authentication with invalid token."""
        mock_validate_token.side_effect = AuthenticationError("Invalid token")

        with pytest.raises(WebSocketException) as exc_info:
            await websocket_auth.authenticate_websocket(mock_authenticated_websocket, mock_session)

        assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
        assert "Invalid token" in exc_info.value.reason
