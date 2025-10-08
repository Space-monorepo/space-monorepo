import pytest
from fastapi import status
from fastapi.websockets import WebSocketDisconnect


@pytest.mark.integration
def test_websocket_chat_route_connection(authenticated_websocket_client):
    """Test WebSocket chat route connection establishment."""
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        assert websocket is not None


@pytest.mark.integration
def test_websocket_chat_route_ping_pong(authenticated_websocket_client):
    """Test WebSocket chat route ping/pong functionality."""
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        ping_event = {
            'type': 'ping',
            'request_id': 'test_ping_123',
            'timestamp': 1703001600.0,
        }

        websocket.send_json(ping_event)
        response = websocket.receive_json()

        assert response['type'] == 'pong'
        assert response['request_id'] == 'test_ping_123'


@pytest.mark.integration
def test_websocket_chat_route_send_message(
    authenticated_websocket_client, sample_conversation_id
):
    """Test WebSocket chat route send message functionality."""
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        message_event = {
            'type': 'send_message',
            'conversation_id': str(sample_conversation_id),
            'content': 'Test message content',
            'request_id': 'test_msg_123',
            'timestamp': 1703001600.0,
        }

        websocket.send_json(message_event)
        response = websocket.receive_json()

        assert response['request_id'] == 'test_msg_123'
        assert response.get('success') is True or response.get('type') == 'message_sent'


@pytest.mark.integration
def test_websocket_chat_route_join_conversation(
    authenticated_websocket_client, sample_conversation_id
):
    """Test WebSocket chat route join conversation functionality."""
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        join_event = {
            'type': 'join_conversation',
            'conversation_id': str(sample_conversation_id),
            'request_id': 'test_join_123',
            'timestamp': 1703001600.0,
        }

        websocket.send_json(join_event)
        response = websocket.receive_json()

        assert response['request_id'] == 'test_join_123'
        assert (
            response.get('success') is True
            or response.get('type') == 'conversation_joined'
        )


@pytest.mark.integration
def test_websocket_chat_route_invalid_event(authenticated_websocket_client):
    """Test WebSocket chat route handles invalid events."""
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        invalid_event = {'type': 'invalid_event_type', 'request_id': 'test_invalid_123'}

        websocket.send_json(invalid_event)
        response = websocket.receive_json()

        assert response['request_id'] == 'test_invalid_123'
        assert response.get('type') == 'error'
        # Error response may have success=False or just type=error
        assert response.get('success') is False or response.get('type') == 'error'


@pytest.mark.integration
def test_websocket_chat_route_unauthenticated(websocket_client):
    """Test WebSocket chat route rejects unauthenticated connections."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect('/chat/ws'):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_websocket_chat_route_invalid_token(websocket_client):
    """Test WebSocket chat route rejects invalid tokens."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect('/chat/ws?token=invalid_token'):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_websocket_health_route(client_sql):
    """Test WebSocket health route."""
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'chat_websocket'
    assert 'chat_connections' in data
    assert 'total_connections' in data
    assert 'supported_events' in data


@pytest.mark.integration
def test_websocket_stats_route(client_sql):
    """Test WebSocket stats route."""
    response = client_sql.get('/chat/ws/stats')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Should either return stats or error, but not crash
    if 'error' not in data:
        assert 'general' in data
        assert 'chat' in data
        assert 'timestamp' in data
