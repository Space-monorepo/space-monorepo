from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class BadgeNotFoundError(Exception):
    """Exception raised when a badge is not found."""

    pass


class MemberBadgeNotFoundError(Exception):
    """Exception raised when a member's badge assignment is not found."""

    pass


class BadgeAlreadyExistsError(Exception):
    """Exception raised when a badge with the same name already exists."""

    pass


class MemberAlreadyHasBadgeError(Exception):
    """Exception raised when a member already has a specific badge."""

    pass


class CannotDeleteSystemBadgeError(Exception):
    """Exception raised when attempting to delete a system-defined badge."""

    pass


class UnexpectedBadgeError(Exception):
    """Exception raised for unexpected errors during badge operations."""

    pass


def add_badge_exception_handler(app: FastAPI):
    @app.exception_handler(BadgeNotFoundError)
    async def badge_not_found_exception_handler(
        request: Request, exc: BadgeNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc) or 'Badge not found.', error_type='badge_not_found'
            ).model_dump(mode='json'),
        )

    @app.exception_handler(MemberBadgeNotFoundError)
    async def user_badge_not_found_exception_handler(
        request: Request, exc: MemberBadgeNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc) or 'User badge assignment not found.',
                error_type='user_badge_not_found',
            ).model_dump(mode='json'),
        )

    @app.exception_handler(BadgeAlreadyExistsError)
    async def badge_already_exists_exception_handler(
        request: Request, exc: BadgeAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc) or f"Badge with name '{exc.name}' already exists.",
                error_type='badge_already_exists',
                details={'name': exc.name},
            ).model_dump(mode='json'),
        )

    @app.exception_handler(MemberAlreadyHasBadgeError)
    async def member_already_has_badge_exception_handler(
        request: Request, exc: MemberAlreadyHasBadgeError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc)
                or (f"Member '{exc.member_id}' already has badge '{exc.badge_id}'."),
                error_type='member_already_has_badge',
                details={
                    'member_id': str(exc.member_id),
                    'badge_id': str(exc.badge_id),
                },
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CannotDeleteSystemBadgeError)
    async def cannot_delete_system_badge_exception_handler(
        request: Request, exc: CannotDeleteSystemBadgeError
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                message=str(exc) or 'System-defined badges cannot be deleted.',
                error_type='cannot_delete_system_badge',
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedBadgeError)
    async def unexpected_badge_error_exception_handler(
        request: Request, exc: UnexpectedBadgeError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc)
                or 'An unexpected error occurred with a badge operation.',
                error_type='unexpected_badge_error',
            ).model_dump(mode='json'),
        )
