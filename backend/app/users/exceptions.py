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


class UserNotAuthorizedError(Exception):
    """
    Exception raised when a user is not authorized to access a resource.
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

    @app.exception_handler(UserNotAuthorizedError)
    async def user_not_authorized_exception_handler(
        request: Request, exc: UserNotAuthorizedError
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                message=str(exc), error_type='user_not_authorized', details={}
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
