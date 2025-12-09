from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class PopularityUpdateError(Exception):
    """
    Exception raised when an error occurs updating popularity points.
    """

    pass


class ReputationUpdateError(Exception):
    """
    Exception raised when an error occurs updating reputation points.
    """

    pass


def add_reputation_exception_handler(app: FastAPI):
    @app.exception_handler(PopularityUpdateError)
    async def popularity_update_error_exception_handler(
        request: Request, exc: PopularityUpdateError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='popularity_update_error', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ReputationUpdateError)
    async def reputation_update_error_exception_handler(
        request: Request, exc: ReputationUpdateError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='reputation_update_error', details={}
            ).model_dump(mode='json'),
        )
