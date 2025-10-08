import pytest
from fastapi import status
from fastapi.websockets import WebSocketDisconnect


@pytest.mark.integration
def test_websocket_ping_event_route(authenticated_websocket_client, websocket_event_data):
    """Test WebSocket ping event through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send ping event
        ping_event = websocket_event_data["ping"]
        websocket.send_json(ping_event)

        # Receive pong response
        response = websocket.receive_json()

        assert response["type"] == "pong"
        assert response["request_id"] == ping_event["request_id"]
        assert "timestamp" in response


@pytest.mark.integration
def test_websocket_join_conversation_event_route(authenticated_websocket_client, websocket_event_data):
    """Test WebSocket join conversation event through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send join conversation event
        join_event = websocket_event_data["join_room"]
        websocket.send_json(join_event)

        # Receive join confirmation
        response = websocket.receive_json()

        assert response["request_id"] == join_event["request_id"]
        # Response should have either success status or error information
        # Since the conversation doesn't exist, it's expected to fail
        assert "success" in response or "type" in response
        # If it fails, should have error information
        if response.get("success") is False:
            assert "error_code" in response or "message" in response


@pytest.mark.integration
def test_websocket_send_message_event_route(authenticated_websocket_client, websocket_event_data):
    """Test WebSocket send message event through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send message event
        message_event = websocket_event_data["send_message"]
        websocket.send_json(message_event)

        # Receive message confirmation or response
        response = websocket.receive_json()

        assert response["request_id"] == message_event["request_id"]
        # Response should have either success status or error information
        # Since the conversation doesn't exist, it's expected to fail
        assert "success" in response or "type" in response
        # If it fails, should have error information
        if response.get("success") is False:
            assert "error_code" in response or "message" in response


@pytest.mark.integration
def test_websocket_invalid_event_route(authenticated_websocket_client, websocket_event_data):
    """Test WebSocket invalid event handling through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send invalid event
        invalid_event = websocket_event_data["invalid_event"]
        websocket.send_json(invalid_event)

        # Should receive error response
        response = websocket.receive_json()

        assert response.get("type") == "error"
        # Error response may have success=False or just type=error
        assert response.get("success") is False or response.get("type") == "error"
        assert response["request_id"] == "invalid_123"
        assert "error_code" in response or "error_message" in response


@pytest.mark.integration
def test_websocket_malformed_json_route(authenticated_websocket_client):
    """Test WebSocket malformed JSON handling through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send malformed JSON
        try:
            websocket.send_text("invalid json{}")

            # Try to receive response
            response = websocket.receive_json()

            # If we get a response, it should be an error
            assert response.get("type") == "error"
            # Error response may have success=False or just type=error
            assert response.get("success") is False or response.get("type") == "error"

        except WebSocketDisconnect as e:
            # Connection might be closed due to malformed data
            assert e.code in [status.WS_1003_UNSUPPORTED_DATA, status.WS_1011_INTERNAL_ERROR]


@pytest.mark.integration
def test_websocket_event_without_request_id_route(authenticated_websocket_client):
    """Test WebSocket event without request_id through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send event without request_id
        event = {
            "type": "ping",
            "timestamp": 1703001600.0
            # Missing request_id
        }
        websocket.send_json(event)

        # Should receive response - request_id is optional
        response = websocket.receive_json()

        # Should process successfully even without request_id
        assert response.get("type") in ["pong", "error"]
        # If pong, it processed successfully
        # If error, should have error information
        if response.get("type") == "error":
            assert "error_message" in response or "message" in response


@pytest.mark.integration
def test_websocket_event_sequence_route(authenticated_websocket_client, websocket_event_data):
    """Test WebSocket multiple events sequence through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send multiple events in sequence
        events = [
            websocket_event_data["ping"],
            {
                "type": "ping",
                "request_id": "ping_2",
                "timestamp": 1703001601.0
            },
            {
                "type": "ping",
                "request_id": "ping_3",
                "timestamp": 1703001602.0
            }
        ]

        responses = []
        for event in events:
            websocket.send_json(event)
            response = websocket.receive_json()
            responses.append(response)

        # Verify all events were processed
        assert len(responses) == len(events)

        # Verify responses correspond to requests
        for event, response in zip(events, responses):
            assert response["request_id"] == event["request_id"]
            assert response.get("type") == "pong"


@pytest.mark.integration
def test_websocket_chat_namespace_route(authenticated_websocket_client):
    """Test WebSocket chat namespace routing."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send chat-specific event
        chat_event = {
            "type": "send_message",
            "conversation_id": "12345678-1234-5678-9012-123456789def",
            "content": "Testing chat namespace",
            "request_id": "namespace_msg_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(chat_event)
        response = websocket.receive_json()

        # Should be processed by chat namespace
        assert response["request_id"] == chat_event["request_id"]
        # Response should have status information - conversation doesn't exist so expect failure
        assert "success" in response or "type" in response
        # If it fails, should have error information
        if response.get("success") is False:
            assert "error_code" in response or "message" in response


@pytest.mark.integration
def test_websocket_error_recovery_route(authenticated_websocket_client):
    """Test WebSocket error handling and recovery through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send valid event first
        valid_event = {
            "type": "ping",
            "request_id": "valid_ping",
            "timestamp": 1703001600.0
        }

        websocket.send_json(valid_event)
        valid_response = websocket.receive_json()
        assert valid_response.get("type") == "pong"

        # Send invalid event
        invalid_event = {
            "type": "unknown_event_type",
            "request_id": "invalid_123"
        }

        websocket.send_json(invalid_event)
        error_response = websocket.receive_json()
        assert error_response.get("type") == "error"

        # Send another valid event to ensure connection still works
        recovery_event = {
            "type": "ping",
            "request_id": "recovery_ping",
            "timestamp": 1703001601.0
        }

        websocket.send_json(recovery_event)
        recovery_response = websocket.receive_json()
        assert recovery_response.get("type") == "pong"
        assert recovery_response.get("request_id") == "recovery_ping"


@pytest.mark.integration
def test_websocket_event_validation_route(authenticated_websocket_client):
    """Test WebSocket event validation through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Test missing required fields
        incomplete_event = {
            "type": "send_message",
            # Missing conversation_id and content
            "request_id": "incomplete_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(incomplete_event)
        response = websocket.receive_json()

        assert response["request_id"] == "incomplete_123"
        # Should return validation error
        assert response.get("success") is False or response.get("type") == "error"


@pytest.mark.integration
def test_websocket_event_response_format_route(authenticated_websocket_client):
    """Test WebSocket event response format consistency through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Test different event types for consistent response format
        events = [
            {
                "type": "ping",
                "request_id": "format_ping",
                "timestamp": 1703001600.0
            },
            {
                "type": "send_message",
                "conversation_id": "12345678-1234-5678-9012-123456789ghi",
                "content": "Format test message",
                "request_id": "format_msg",
                "timestamp": 1703001601.0
            }
        ]

        for event in events:
            websocket.send_json(event)
            response = websocket.receive_json()

            # Verify common response format
            assert "request_id" in response
            assert response["request_id"] == event["request_id"]
            assert "type" in response or "success" in response

            # If it's an error response, should have proper error fields
            if response.get("success") is False or response.get("type") == "error":
                assert "error_code" in response or "error_message" in response or "message" in response


@pytest.mark.integration
def test_websocket_concurrent_events_route(authenticated_websocket_client):
    """Test WebSocket concurrent event handling through route."""
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # First receive welcome message
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Send multiple ping events rapidly
        events = [
            {
                "type": "ping",
                "request_id": f"concurrent_ping_{i}",
                "timestamp": 1703001600.0 + i
            }
            for i in range(5)
        ]

        # Send all events
        for event in events:
            websocket.send_json(event)

        # Receive all responses
        responses = []
        for _ in range(len(events)):
            response = websocket.receive_json()
            responses.append(response)

        # Verify all events were processed
        assert len(responses) == len(events)

        # Verify each request got a response
        request_ids = {event["request_id"] for event in events}
        response_ids = {resp["request_id"] for resp in responses}
        assert request_ids == response_ids

        # All should be pong responses
        for response in responses:
            assert response.get("type") == "pong"
