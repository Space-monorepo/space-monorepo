from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class RatingNotFoundError(Exception):
    """Exception raised when a rating is not found."""

    pass


class RatingAlreadyExistsError(Exception):
    """Exception raised when a user tries to rate a community more than once."""

    pass


class UnexpectedRatingError(Exception):
    """Exception raised for unexpected errors during rating operations."""

    pass


def add_rating_exception_handler(app: FastAPI):
    @app.exception_handler(RatingNotFoundError)
    async def rating_not_found_handler(request: Request, exc: RatingNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='rating_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(RatingAlreadyExistsError)
    async def rating_already_exists_handler(
        request: Request, exc: RatingAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='rating_already_exists', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedRatingError)
    async def unexpected_rating_error_handler(
        request: Request, exc: UnexpectedRatingError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_rating_error', details={}
            ).model_dump(mode='json'),
        )
