import pytest

from app.core.websocket.events import (
    ErrorEvent,
    EventResponse,
    JoinRoomEvent,
    PingEvent,
    WebSocketEvent,
)
from app.core.websocket.exceptions import EventValidationError


class TestWebSocketEvent:
    """Test WebSocket event schema validation."""

    @pytest.mark.unit
    def test_event_creation_websocket_success(self):
        """Test creating a basic WebSocket event."""
        event = WebSocketEvent(
            type="test_event",
            timestamp=1703001600.0,
            request_id="req_123"
        )

        assert event.type == "test_event"
        assert event.timestamp == 1703001600.0
        assert event.request_id == "req_123"

    @pytest.mark.unit
    def test_event_to_dict_websocket_success(self):
        """Test WebSocket event serialization."""
        event = WebSocketEvent(
            type="test_event",
            timestamp=1703001600.0,
            request_id="req_123"
        )

        result = event.to_dict()

        expected = {
            "type": "test_event",
            "timestamp": 1703001600.0,
            "request_id": "req_123"
        }
        assert result == expected

    @pytest.mark.unit
    def test_event_from_dict_websocket_success(self):
        """Test WebSocket event deserialization."""
        data = {
            "type": "test_event",
            "timestamp": 1703001600.0,
            "request_id": "req_123"
        }

        event = WebSocketEvent.from_dict(data)

        assert event.type == "test_event"
        assert event.timestamp == 1703001600.0
        assert event.request_id == "req_123"

    @pytest.mark.unit
    def test_event_from_dict_websocket_validation_error(self):
        """Test WebSocket event validation error."""
        data = {
            "timestamp": "invalid_timestamp",  # Should be float
            "request_id": "req_123"
            # Missing required 'type' field
        }

        with pytest.raises(EventValidationError, match="Invalid event data"):
            WebSocketEvent.from_dict(data)


class TestEventResponse:
    """Test event response schema validation."""

    @pytest.mark.unit
    def test_event_response_websocket_success(self):
        """Test successful event response creation."""
        response = EventResponse(
            success=True,
            request_id="req_123",
            data={"message": "Success"}
        )

        assert response.success is True
        assert response.request_id == "req_123"
        assert response.data == {"message": "Success"}
        assert response.error_code is None

    @pytest.mark.unit
    def test_event_response_websocket_error(self):
        """Test error event response creation."""
        response = EventResponse(
            success=False,
            request_id="req_123",
            error_code="VALIDATION_ERROR",
            message="Validation failed"
        )

        assert response.success is False
        assert response.request_id == "req_123"
        assert response.error_code == "VALIDATION_ERROR"
        assert response.message == "Validation failed"
        assert response.data is None


class TestPredefinedEvents:
    """Test predefined event schemas."""

    @pytest.mark.unit
    def test_ping_event_websocket_success(self):
        """Test ping event schema."""
        event = PingEvent(request_id="ping_123")

        assert event.type == "ping"
        assert event.request_id == "ping_123"

    @pytest.mark.unit
    def test_join_room_event_websocket_success(self):
        """Test join room event schema."""
        event = JoinRoomEvent(
            room_id="room_123",
            request_id="join_123"
        )

        assert event.type == "join_room"
        assert event.room_id == "room_123"
        assert event.request_id == "join_123"

    @pytest.mark.unit
    def test_error_event_websocket_success(self):
        """Test error event schema."""
        event = ErrorEvent(
            error_code="VALIDATION_ERROR",
            error_message="Invalid data",
            request_id="error_123"
        )

        assert event.type == "error"
        assert event.error_code == "VALIDATION_ERROR"
        assert event.error_message == "Invalid data"
        assert event.request_id == "error_123"
