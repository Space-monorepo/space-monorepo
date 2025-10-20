from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class ConversationNotFoundError(Exception):
    """
    Exception raised when a conversation is not found.
    """

    pass


class ConversationAlreadyExistsError(Exception):
    """
    Exception raised when a conversation already exists between users.
    """

    pass


class UnauthorizedConversationAccessError(Exception):
    """
    Exception raised when user tries to access conversation they don't participate in.
    """

    pass


class MessageNotFoundError(Exception):
    """
    Exception raised when a message is not found.
    """

    pass


class UnauthorizedMessageAccessError(Exception):
    """
    Exception raised when user tries to access message they don't have permission for.
    """

    pass


class InvalidMessageTypeError(Exception):
    """
    Exception raised when message type is invalid for the operation.
    """

    pass


class MessageTooLongError(Exception):
    """
    Exception raised when message content exceeds maximum length.
    """

    pass


class RateLimitExceededError(Exception):
    """
    Exception raised when user exceeds message rate limit.
    """

    pass


class FileNotFoundError(Exception):
    """
    Exception raised when a file attachment is not found.
    """

    pass


class FileUploadError(Exception):
    """
    Exception raised when file upload fails.
    """

    pass


class InvalidFileTypeError(Exception):
    """
    Exception raised when uploaded file type is not allowed.
    """

    pass


class FileSizeExceededError(Exception):
    """
    Exception raised when uploaded file exceeds size limit.
    """

    pass


class VirusScanFailedError(Exception):
    """
    Exception raised when uploaded file fails virus scan.
    """

    pass


class UsersNotConnectedError(Exception):
    """
    Exception raised when users are not connected and try to chat.
    """

    pass


class UnexpectedChatError(Exception):
    """
    Exception raised when an unexpected chat error occurs.
    """

    pass


def _create_error_response(
    status_code: int, message: str, error_type: str
) -> JSONResponse:
    """Helper function to create standardized error responses"""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            message=message, error_type=error_type, details={}
        ).model_dump(mode='json'),
    )


def _register_chat_error_handlers(app: FastAPI):
    """Register chat-specific error handlers with reduced complexity"""

    # 404 handlers
    @app.exception_handler(ConversationNotFoundError)
    async def conversation_not_found_handler(
        request: Request, exc: ConversationNotFoundError
    ):
        return _create_error_response(
            status.HTTP_404_NOT_FOUND, str(exc), 'conversation_not_found'
        )

    @app.exception_handler(MessageNotFoundError)
    async def message_not_found_handler(request: Request, exc: MessageNotFoundError):
        return _create_error_response(
            status.HTTP_404_NOT_FOUND, str(exc), 'message_not_found'
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        return _create_error_response(
            status.HTTP_404_NOT_FOUND, str(exc), 'file_not_found'
        )


def _register_chat_auth_handlers(app: FastAPI):
    """Register chat authorization error handlers"""

    @app.exception_handler(UnauthorizedConversationAccessError)
    async def unauthorized_conversation_handler(
        request: Request, exc: UnauthorizedConversationAccessError
    ):
        return _create_error_response(
            status.HTTP_403_FORBIDDEN, str(exc), 'unauthorized_conversation_access'
        )

    @app.exception_handler(UnauthorizedMessageAccessError)
    async def unauthorized_message_handler(
        request: Request, exc: UnauthorizedMessageAccessError
    ):
        return _create_error_response(
            status.HTTP_403_FORBIDDEN, str(exc), 'unauthorized_message_access'
        )

    @app.exception_handler(UsersNotConnectedError)
    async def users_not_connected_handler(request: Request, exc: UsersNotConnectedError):
        return _create_error_response(
            status.HTTP_403_FORBIDDEN, str(exc), 'users_not_connected'
        )


def _register_chat_validation_handlers(app: FastAPI):
    """Register chat validation error handlers"""

    @app.exception_handler(InvalidMessageTypeError)
    async def invalid_message_type_handler(
        request: Request, exc: InvalidMessageTypeError
    ):
        return _create_error_response(
            status.HTTP_400_BAD_REQUEST, str(exc), 'invalid_message_type'
        )

    @app.exception_handler(MessageTooLongError)
    async def message_too_long_handler(request: Request, exc: MessageTooLongError):
        return _create_error_response(
            status.HTTP_400_BAD_REQUEST, str(exc), 'message_too_long'
        )

    @app.exception_handler(FileUploadError)
    async def file_upload_handler(request: Request, exc: FileUploadError):
        return _create_error_response(
            status.HTTP_400_BAD_REQUEST, str(exc), 'file_upload_error'
        )

    @app.exception_handler(InvalidFileTypeError)
    async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeError):
        return _create_error_response(
            status.HTTP_400_BAD_REQUEST, str(exc), 'invalid_file_type'
        )

    @app.exception_handler(VirusScanFailedError)
    async def virus_scan_failed_handler(request: Request, exc: VirusScanFailedError):
        return _create_error_response(
            status.HTTP_400_BAD_REQUEST, str(exc), 'virus_scan_failed'
        )


def _register_chat_conflict_handlers(app: FastAPI):
    """Register chat conflict and rate limit handlers"""

    @app.exception_handler(ConversationAlreadyExistsError)
    async def conversation_exists_handler(
        request: Request, exc: ConversationAlreadyExistsError
    ):
        return _create_error_response(
            status.HTTP_409_CONFLICT, str(exc), 'conversation_already_exists'
        )

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(request: Request, exc: RateLimitExceededError):
        return _create_error_response(
            status.HTTP_429_TOO_MANY_REQUESTS, str(exc), 'rate_limit_exceeded'
        )

    @app.exception_handler(FileSizeExceededError)
    async def file_size_handler(request: Request, exc: FileSizeExceededError):
        return _create_error_response(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc), 'file_size_exceeded'
        )

    @app.exception_handler(UnexpectedChatError)
    async def unexpected_error_handler(request: Request, exc: UnexpectedChatError):
        return _create_error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc), 'unexpected_chat_error'
        )


def add_chat_exception_handler(app: FastAPI):
    """Register all chat exception handlers"""
    _register_chat_error_handlers(app)
    _register_chat_auth_handlers(app)
    _register_chat_validation_handlers(app)
    _register_chat_conflict_handlers(app)
