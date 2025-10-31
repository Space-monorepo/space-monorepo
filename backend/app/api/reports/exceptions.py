from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.schema import ErrorResponse


class UnexpectedReportError(Exception):
    """
    Exception raised when an unexpected error occurs.
    """

    pass


class ReportNotFoundError(Exception):
    """
    Exception raised when a report is not found.
    """

    pass


class ReportMemberAlreadyExistsError(Exception):
    """
    Exception raised when a report member already exists.
    """

    pass


class ReportPostAlreadyExistsError(Exception):
    """
    Exception raised when a report post already exists.
    """

    pass


class ReportCommentAlreadyExistsError(Exception):
    """
    Exception raised when a report comment already exists.
    """

    pass


class ModeratorAlreadyVotedError(Exception):
    """
    Exception raised when a moderator tries to vote twice on the same report.
    """

    pass


def add_report_exception_handler(app: FastAPI):
    @app.exception_handler(UnexpectedReportError)
    async def unexpected_report_error_exception_handler(
        request: Request, exc: UnexpectedReportError
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message=str(exc), error_type='unexpected_report_error', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ReportNotFoundError)
    async def report_not_found_exception_handler(
        request: Request, exc: ReportNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                message=str(exc), error_type='report_not_found', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ReportMemberAlreadyExistsError)
    async def report_member_already_exists_exception_handler(
        request: Request, exc: ReportMemberAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='report_member_already_exists', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ReportPostAlreadyExistsError)
    async def report_post_already_exists_exception_handler(
        request: Request, exc: ReportPostAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='report_post_already_exists', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ReportCommentAlreadyExistsError)
    async def report_comment_already_exists_exception_handler(
        request: Request, exc: ReportCommentAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='report_comment_already_exists', details={}
            ).model_dump(mode='json'),
        )

    @app.exception_handler(ModeratorAlreadyVotedError)
    async def moderator_already_voted_exception_handler(
        request: Request, exc: ModeratorAlreadyVotedError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                message=str(exc), error_type='moderator_already_voted', details={}
            ).model_dump(mode='json'),
        )
