import pytest
from fastapi import status

from app.core.websocket.exceptions import (
    AuthenticationError,
    EventHandlingError,
    EventValidationError,
    WebSocketError,
)


class TestWebSocketError:
    """Test the base WebSocketError exception schema."""

    @pytest.mark.unit
    def test_websocket_error_creation(self):
        """Test WebSocketError creation with message and code."""
        error = WebSocketError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.code == status.WS_1011_INTERNAL_ERROR

    @pytest.mark.unit
    def test_websocket_error_custom_code(self):
        """Test WebSocketError with custom status code."""
        custom_code = status.WS_1008_POLICY_VIOLATION
        error = WebSocketError("Test error", custom_code)
        assert error.code == custom_code
        assert error.message == "Test error"


class TestAuthenticationError:
    """Test AuthenticationError exception schema."""

    @pytest.mark.unit
    def test_authentication_error_creation(self):
        """Test AuthenticationError creation and properties."""
        error = AuthenticationError("Invalid token")
        assert error.message == "Invalid token"
        assert error.code == status.WS_1008_POLICY_VIOLATION
        assert isinstance(error, WebSocketError)


class TestEventValidationError:
    """Test EventValidationError exception schema."""

    @pytest.mark.unit
    def test_event_validation_error_creation(self):
        """Test EventValidationError creation and properties."""
        error = EventValidationError("Invalid event data")
        assert error.message == "Invalid event data"
        assert error.code == status.WS_1003_UNSUPPORTED_DATA
        assert isinstance(error, WebSocketError)


class TestEventHandlingError:
    """Test EventHandlingError exception schema."""

    @pytest.mark.unit
    def test_event_handling_error_creation(self):
        """Test EventHandlingError creation and properties."""
        error = EventHandlingError("Handler failed")
        assert error.message == "Handler failed"
        assert error.code == status.WS_1011_INTERNAL_ERROR
        assert isinstance(error, WebSocketError)


class TestExceptionCodes:
    """Test WebSocket exception status codes."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "exception_class,expected_code",
        [
            (AuthenticationError, status.WS_1008_POLICY_VIOLATION),
            (EventHandlingError, status.WS_1011_INTERNAL_ERROR),
            (EventValidationError, status.WS_1003_UNSUPPORTED_DATA),
        ],
    )
    def test_exception_codes_parametrized(self, exception_class, expected_code):
        """Test that exceptions use correct WebSocket status codes."""
        exception = exception_class("Test message")
        assert exception.code == expected_code
        assert isinstance(exception, WebSocketError)
