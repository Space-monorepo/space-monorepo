from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class CommunityNotFoundError(Exception):
    pass


class CommunityMemberNotFoundError(Exception):
    pass


class CommunityAlreadyExistsError(Exception):
    pass


class CommunityMemberAlreadyExistsError(Exception):
    pass


class UnexpectedCommunityError(Exception):
    pass


class UnexpectedCommunityMemberError(Exception):
    pass


def add_community_exception_handler(app: FastAPI):
    @app.exception_handler(CommunityNotFoundError)
    async def community_not_found_handler(request: Request, exc: CommunityNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='community_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CommunityMemberNotFoundError)
    async def community_member_not_found_handler(
        request: Request, exc: CommunityMemberNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='community_member_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CommunityAlreadyExistsError)
    async def community_already_exists_handler(
        request: Request, exc: CommunityAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='community_already_exists', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(CommunityMemberAlreadyExistsError)
    async def community_member_already_exists_handler(
        request: Request, exc: CommunityMemberAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc),
                error_type='community_member_already_exists',
                details={},
            ).model_dump(mode='json'),
        )

    @app.exception_handler(UnexpectedCommunityError)
    async def unexpected_community_error_handler(
        request: Request, exc: UnexpectedCommunityError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_community_error', details={}
            ).model_dump(mode='json'),
        )
