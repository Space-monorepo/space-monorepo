from fastapi import status


class WebSocketError(Exception):
    """
    Base exception for WebSocket-related errors.
    """

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        super().__init__(message)
        self.message = message
        self.code = code


class ConnectionError(WebSocketError):
    """
    Exception raised when there are problems with WebSocket connections.
    """

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        super().__init__(message, code)


class AuthenticationError(WebSocketError):
    """
    Exception raised when WebSocket authentication fails.
    """

    def __init__(self, message: str, code: int = status.WS_1008_POLICY_VIOLATION):
        super().__init__(message, code)


class EventHandlingError(WebSocketError):
    """
    Exception raised when there are problems processing WebSocket events.
    """

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        super().__init__(message, code)


class RoomError(WebSocketError):
    """
    Exception raised when there are problems with room operations.
    """

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        super().__init__(message, code)


class NamespaceError(WebSocketError):
    """
    Exception raised when there are problems with namespace operations.
    """

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        super().__init__(message, code)


class EventValidationError(WebSocketError):
    """
    Exception raised when event data validation fails.
    """

    def __init__(self, message: str, code: int = status.WS_1003_UNSUPPORTED_DATA):
        super().__init__(message, code)


class RateLimitError(WebSocketError):
    """
    Exception raised when rate limits are exceeded.
    """

    def __init__(self, message: str, code: int = status.WS_1008_POLICY_VIOLATION):
        super().__init__(message, code)


class BroadcastError(WebSocketError):
    """
    Exception raised when message broadcasting fails.
    """

    def __init__(self, message: str, code: int = status.WS_1011_INTERNAL_ERROR):
        super().__init__(message, code)
