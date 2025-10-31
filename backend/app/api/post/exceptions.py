from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class PostNotFoundError(Exception):
    """
    Exception raised when a post is not found.
    """

    pass


class PostSuspendedError(Exception):
    """
    Exception raised when a post is already suspended.
    """

    pass


class UnexpectedPostError(Exception):
    """
    Exception raised when an unexpected error occurs.
    """

    pass


class PostLikesNotFoundError(Exception):
    """
    Exception raised when a post likes is not found.
    """

    pass


class PollOptionNotFoundError(Exception):
    """
    Exception raised when a poll option is not found.
    """

    pass


class ComplaintNotFoundError(Exception):
    """
    Exception raised when a complaint is not found.
    """

    pass


def add_post_exception_handler(app: FastAPI):
    @app.exception_handler(ComplaintNotFoundError)
    async def complaint_not_found_exception_handler(
        request: Request, exc: ComplaintNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='complaint_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(PostNotFoundError)
    async def post_not_found_exception_handler(request: Request, exc: PostNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='post_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(PostSuspendedError)
    async def post_suspended_exception_handler(
        request: Request, exc: PostSuspendedError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='post_suspended', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedPostError)
    async def unexpected_post_error_exception_handler(
        request: Request, exc: UnexpectedPostError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_post_error', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(PostLikesNotFoundError)
    async def post_likes_not_found_exception_handler(
        request: Request, exc: PostLikesNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='post_likes_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(PollOptionNotFoundError)
    async def poll_option_not_found_exception_handler(
        request: Request, exc: PollOptionNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='poll_option_not_found', details={}
            ).model_dump(mode='json'),
        )
