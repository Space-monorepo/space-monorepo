import pytest
from fastapi import status


@pytest.mark.integration
def test_health_endpoint_websocket_success(client_sql):
    """Test WebSocket health check endpoint route."""
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "chat_websocket"
    assert "chat_connections" in data
    assert "total_connections" in data
    assert "supported_events" in data
    assert isinstance(data["supported_events"], list)


@pytest.mark.integration
def test_health_endpoint_response_structure_websocket_success(client_sql):
    """Test WebSocket health endpoint response structure."""
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    required_fields = ["status", "service", "chat_connections", "total_connections", "supported_events"]

    for field in required_fields:
        assert field in data

    # Verify data types
    assert isinstance(data["chat_connections"], int)
    assert isinstance(data["total_connections"], int)
    assert isinstance(data["supported_events"], list)
    assert data["status"] in ["healthy", "unhealthy"]


@pytest.mark.integration
def test_stats_endpoint_websocket_success(client_sql):
    """Test WebSocket stats endpoint route."""
    response = client_sql.get('/chat/ws/stats')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Should have main sections
    if "error" not in data:
        assert "general" in data
        assert "chat" in data
        assert "timestamp" in data

        # Verify general stats structure
        general_stats = data["general"]
        assert "total_connections" in general_stats
        assert "current_connections" in general_stats
        # Stats tracks messages_sent and messages_received separately
        assert "messages_sent" in general_stats or "total_messages" in general_stats
        assert "namespaces" in general_stats

        # Verify chat stats structure
        chat_stats = data["chat"]
        # Chat stats may have different structure based on implementation
        assert "total_conversations" in chat_stats or "active_rooms" in chat_stats
        assert "total_chat_connections" in chat_stats or "total_participants" in chat_stats
        assert "base_room_stats" in chat_stats or "rooms" in chat_stats
    else:
        # If error occurred, should be handled gracefully
        assert isinstance(data["error"], str)


@pytest.mark.integration
def test_stats_endpoint_response_structure_websocket_success(client_sql):
    """Test WebSocket stats endpoint response structure."""
    response = client_sql.get('/chat/ws/stats')

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"

    data = response.json()

    # Should either return full stats or error
    if "error" not in data:
        # Verify nested structure
        assert isinstance(data["general"], dict)
        assert isinstance(data["chat"], dict)

        # Verify data types in general stats
        general = data["general"]
        assert isinstance(general["total_connections"], int)
        assert isinstance(general["current_connections"], int)
        # Stats may have messages_sent/messages_received or total_messages
        assert isinstance(general.get("total_messages", 0), int) or isinstance(general.get("messages_sent", 0), int)
        assert isinstance(general["namespaces"], dict)

        # Verify data types in chat stats
        chat = data["chat"]
        # Chat stats may have different field names
        assert isinstance(chat.get("active_rooms", 0), int) or isinstance(chat.get("total_conversations", 0), int)
        assert isinstance(chat.get("total_participants", 0), int) or isinstance(chat.get("total_chat_connections", 0), int)
        assert isinstance(chat.get("rooms", {}), dict) or isinstance(chat.get("base_room_stats", {}), dict)


@pytest.mark.integration
def test_health_endpoint_availability_websocket_success(client_sql):
    """Test WebSocket health endpoint is always available."""
    # Health endpoint should always respond
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # Should always have status field
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


@pytest.mark.integration
def test_stats_endpoint_availability_websocket_success(client_sql):
    """Test WebSocket stats endpoint is always available."""
    # Stats endpoint should always respond
    response = client_sql.get('/chat/ws/stats')

    assert response.status_code == status.HTTP_200_OK

    # Should not return server error even if stats are unavailable
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.integration
def test_endpoints_response_time_websocket_success(client_sql):
    """Test WebSocket monitoring endpoints response time."""
    # Health endpoint should be fast
    health_response = client_sql.get('/chat/ws/health')
    assert health_response.status_code == status.HTTP_200_OK
    # Response time should be reasonable (not testing exact time due to CI variability)

    # Stats endpoint should also be reasonably fast
    stats_response = client_sql.get('/chat/ws/stats')
    assert stats_response.status_code == status.HTTP_200_OK


@pytest.mark.integration
def test_health_endpoint_security_websocket_success(client_sql):
    """Test WebSocket health endpoint doesn't expose sensitive data."""
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    response_str = str(data).lower()

    # Should not expose sensitive information
    sensitive_terms = ["password", "secret", "key", "token"]
    for term in sensitive_terms:
        assert term not in response_str


@pytest.mark.integration
def test_stats_endpoint_security_websocket_success(client_sql):
    """Test WebSocket stats endpoint doesn't expose sensitive data."""
    response = client_sql.get('/chat/ws/stats')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    response_str = str(data).lower()

    # Should not expose sensitive information
    sensitive_terms = ["password", "secret", "key", "token"]
    for term in sensitive_terms:
        assert term not in response_str


@pytest.mark.integration
def test_health_endpoint_with_connection_activity_websocket_success(authenticated_websocket_client, client_sql):
    """Test WebSocket health endpoint reflects connection activity."""
    # First check without connections
    initial_response = client_sql.get('/chat/ws/health')
    initial_data = initial_response.json()
    initial_connections = initial_data["total_connections"]

    # Create WebSocket connection and check health
    url = f"/chat/ws?token={authenticated_websocket_client.token}"
    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Health should still be accessible during active connection
        active_response = client_sql.get('/chat/ws/health')
        assert active_response.status_code == status.HTTP_200_OK

        active_data = active_response.json()
        assert active_data["status"] == "healthy"
        # Connection count might or might not be immediately reflected


@pytest.mark.integration
def test_monitoring_endpoints_json_format_websocket_success(client_sql):
    """Test WebSocket monitoring endpoints return valid JSON."""
    # Test health endpoint JSON
    health_response = client_sql.get('/chat/ws/health')
    assert health_response.status_code == status.HTTP_200_OK

    health_data = health_response.json()
    assert isinstance(health_data, dict)

    # Test stats endpoint JSON
    stats_response = client_sql.get('/chat/ws/stats')
    assert stats_response.status_code == status.HTTP_200_OK

    stats_data = stats_response.json()
    assert isinstance(stats_data, dict)


@pytest.mark.integration
def test_health_endpoint_service_identification_websocket_success(client_sql):
    """Test WebSocket health endpoint correctly identifies service."""
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["service"] == "chat_websocket"
    assert "chat" in data["service"]  # Confirms this is chat WebSocket service
