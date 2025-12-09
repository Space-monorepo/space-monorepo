from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class UserAlreadyExistsError(Exception):
    """
    Exception raised when a user already exists.
    """

    pass


class UserNotAuthenticatedError(Exception):
    """
    Exception raised when a user is not authenticated.
    """

    pass


class UserNotFoundError(Exception):
    """
    Exception raised when a user is not found.
    """

    pass


class UnexpectedUserError(Exception):
    """
    Exception raised when an unexpected database error occurs.
    """

    pass


class ConnectionNotFoundError(Exception):
    """
    Exception raised when a connection is not found.
    """

    pass


class ConnectionAlreadyExistsError(Exception):
    """
    Exception raised when a connection already exists between users.
    """

    pass


class ConnectionCooldownError(Exception):
    """
    Exception raised when trying to request connection during cooldown period.
    """

    pass


class SelfConnectionError(Exception):
    """
    Exception raised when trying to connect to oneself.
    """

    pass


class UnexpectedConnectionError(Exception):
    """
    Exception raised when an unexpected connection error occurs.
    """

    pass


def add_user_exception_handler(app: FastAPI):
    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc),
                error_type='user_already_exists',
                details={'email': exc.email},
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UserNotAuthenticatedError)
    async def user_not_authenticated_exception_handler(
        request: Request, exc: UserNotAuthenticatedError
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(
                message=str(exc), error_type='user_not_authenticated', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='user_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedUserError)
    async def unexpected_user_error_exception_handler(
        request: Request, exc: UnexpectedUserError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_user_error', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ConnectionNotFoundError)
    async def connection_not_found_exception_handler(
        request: Request, exc: ConnectionNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='connection_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ConnectionAlreadyExistsError)
    async def connection_already_exists_exception_handler(
        request: Request, exc: ConnectionAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='connection_already_exists', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ConnectionCooldownError)
    async def connection_cooldown_exception_handler(
        request: Request, exc: ConnectionCooldownError
    ):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=ErrorResponse(
                message=str(exc), error_type='connection_cooldown', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(SelfConnectionError)
    async def self_connection_exception_handler(
        request: Request, exc: SelfConnectionError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                message=str(exc), error_type='self_connection', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedConnectionError)
    async def unexpected_connection_error_exception_handler(
        request: Request, exc: UnexpectedConnectionError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_connection_error', details={}
            ).model_dump(mode='json'),
        )
