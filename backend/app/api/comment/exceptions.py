from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class CommentNotFoundError(Exception):
    """
    Exception raised when a comment is not found.
    """

    pass


class CommentLikesNotFoundError(Exception):
    """
    Exception raised when a comment likes is not found.
    """

    pass


class CommentSuspendedError(Exception):
    """
    Exception raised when a comment is already suspended.
    """

    pass


class UnexpectedCommentError(Exception):
    """
    Exception raised when an unexpected error occurs.
    """

    pass


class CommentPermissionError(Exception):
    """
    Exception raised when user doesn't have permission to perform action.
    """

    pass


def add_comment_exception_handler(app: FastAPI):
    @app.exception_handler(CommentNotFoundError)
    async def comment_not_found_exception_handler(
        request: Request, exc: CommentNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='comment_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CommentLikesNotFoundError)
    async def comment_likes_not_found_exception_handler(
        request: Request, exc: CommentLikesNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='comment_likes_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CommentSuspendedError)
    async def comment_suspended_exception_handler(
        request: Request, exc: CommentSuspendedError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='comment_suspended', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedCommentError)
    async def unexpected_comment_error_exception_handler(
        request: Request, exc: UnexpectedCommentError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_comment_error', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CommentPermissionError)
    async def comment_permission_exception_handler(
        request: Request, exc: CommentPermissionError
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                message=str(exc), error_type='comment_permission_error', details={}
            ).model_dump(mode='json'),
        )
