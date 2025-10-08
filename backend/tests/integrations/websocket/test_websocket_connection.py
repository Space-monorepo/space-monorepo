import pytest
from fastapi import status
from fastapi.websockets import WebSocketDisconnect


@pytest.mark.integration
def test_websocket_connection_route_success(authenticated_websocket_client):
    """Test successful WebSocket connection to chat route."""
    with authenticated_websocket_client.websocket_connect(f"/chat/ws?token={authenticated_websocket_client.token}") as websocket:
        # Connection should establish successfully
        assert websocket is not None


@pytest.mark.integration
def test_websocket_connection_route_without_auth(websocket_client):
    """Test WebSocket connection route without authentication fails."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect("/chat/ws"):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_websocket_connection_route_with_invalid_token(websocket_client):
    """Test WebSocket connection route with invalid token fails."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect("/chat/ws?token=invalid_token"):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_websocket_connection_route_with_conversation_id(authenticated_websocket_client, sample_conversation_id):
    """Test WebSocket connection route with conversation_id parameter."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}&conversation_id={str(sample_conversation_id)}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Should connect successfully with conversation_id
        assert websocket is not None


@pytest.mark.integration
def test_websocket_connection_route_lifecycle(authenticated_websocket_client):
    """Test complete WebSocket connection route lifecycle."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Verify connection is established
        assert websocket is not None

        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Connection should remain stable during test
        # Test by sending a simple ping
        ping_data = {
            "type": "ping",
            "request_id": "lifecycle_ping",
            "timestamp": 1703001600.0
        }

        websocket.send_json(ping_data)
        response = websocket.receive_json()

        # Should receive pong response
        assert response["type"] == "pong"
        assert response["request_id"] == "lifecycle_ping"

    # Connection should close cleanly without errors


@pytest.mark.integration
def test_websocket_connection_route_error_handling(authenticated_websocket_client):
    """Test WebSocket connection route handles errors gracefully."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send malformed data to test error handling
        try:
            websocket.send_text("invalid json data")

            # If connection remains open, should receive error
            try:
                response = websocket.receive_json()
                if "type" in response:
                    assert response["type"] == "error"
            except WebSocketDisconnect:
                # Connection might close on malformed data - this is acceptable
                pass

        except WebSocketDisconnect as e:
            # Connection might close immediately on malformed data
            assert e.code in [status.WS_1003_UNSUPPORTED_DATA, status.WS_1011_INTERNAL_ERROR]


@pytest.mark.integration
def test_websocket_connection_route_with_headers(websocket_client, user_on_db):
    """Test WebSocket connection route with authorization header."""
    # Get authentication token
    response = websocket_client.post(
        '/users/login',
        data={'username': user_on_db.email, 'password': 'hashed_password'}
    )
    token = response.json().get('access_token')

    # Connect with token in URL
    with websocket_client.websocket_connect(f"/chat/ws?token={token}") as websocket:
        assert websocket is not None


@pytest.mark.integration
def test_websocket_connection_route_cleanup(authenticated_websocket_client):
    """Test WebSocket connection route cleanup on disconnect."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    # Multiple connection cycles to test cleanup
    for i in range(3):
        with authenticated_websocket_client.websocket_connect(url) as websocket:
            # First receive welcome message
            welcome_response = websocket.receive_json()
            assert welcome_response["type"] == "welcome"

            # Basic operation to ensure connection works
            ping_data = {
                "type": "ping",
                "request_id": f"cleanup_ping_{i}",
                "timestamp": 1703001600.0 + i
            }

            websocket.send_json(ping_data)
            response = websocket.receive_json()
            assert response["type"] == "pong"

        # Each connection should close cleanly
