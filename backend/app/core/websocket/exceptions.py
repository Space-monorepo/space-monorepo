"""
WebSocket-specific exceptions for the centralized WebSocket system.

These exceptions provide specific error handling for WebSocket operations
and maintain consistency with the FastAPI error handling patterns.
"""

from fastapi import status


class WebSocketError(Exception):
    """Base exception for all WebSocket-related errors."""

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        self.message = message
        self.code = code
        super().__init__(message)


class ConnectionError(WebSocketError):
    """Raised when there are issues with WebSocket connections."""

    def __init__(self, message: str = 'WebSocket connection error'):
        super().__init__(message, status.WS_1002_PROTOCOL_ERROR)


class AuthenticationError(WebSocketError):
    """Raised when WebSocket authentication fails."""

    def __init__(self, message: str = 'WebSocket authentication failed'):
        super().__init__(message, status.WS_1008_POLICY_VIOLATION)


class EventHandlingError(WebSocketError):
    """Raised when there are issues processing WebSocket events."""

    def __init__(self, message: str = 'Event handling error'):
        super().__init__(message, status.WS_1011_INTERNAL_ERROR)


class RoomError(WebSocketError):
    """Raised when there are issues with room operations."""

    def __init__(self, message: str = 'Room operation error'):
        super().__init__(message, status.WS_1011_INTERNAL_ERROR)


class NamespaceError(WebSocketError):
    """Raised when there are issues with namespace operations."""

    def __init__(self, message: str = 'Namespace error'):
        super().__init__(message, status.WS_1008_POLICY_VIOLATION)


class EventValidationError(WebSocketError):
    """Raised when event data validation fails."""

    def __init__(self, message: str = 'Event validation failed'):
        super().__init__(message, status.WS_1003_UNSUPPORTED_DATA)


class RateLimitError(WebSocketError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str = 'Rate limit exceeded'):
        super().__init__(message, status.WS_1008_POLICY_VIOLATION)


class BroadcastError(WebSocketError):
    """Raised when message broadcasting fails."""

    def __init__(self, message: str = 'Broadcast error'):
        super().__init__(message, status.WS_1011_INTERNAL_ERROR)
