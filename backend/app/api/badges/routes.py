from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.badges.exceptions import (
    BadgeAlreadyExistsError,
    BadgeNotFoundError,
    CannotDeleteSystemBadgeError,
    MemberAlreadyHasBadgeError,
    MemberBadgeNotFoundError,
    UnexpectedBadgeError,
)
from app.api.badges.schema import (
    BadgeCreate,
    BadgeResponse,
    BadgeUpdate,
    MemberBadgeCreate,
)
from app.api.badges.service import BadgeService
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/badges', tags=['badges'])
admin_router = APIRouter(prefix='/admin/badges', tags=['admin-badges'])


def _service(session: Session = Depends(get_db)) -> BadgeService:
    return BadgeService(TransactionManager(session))


def _raise_http_error(exc: Exception) -> None:
    error_map = {
        BadgeNotFoundError: status.HTTP_404_NOT_FOUND,
        BadgeAlreadyExistsError: status.HTTP_409_CONFLICT,
        CannotDeleteSystemBadgeError: status.HTTP_403_FORBIDDEN,
        MemberBadgeNotFoundError: status.HTTP_404_NOT_FOUND,
        MemberAlreadyHasBadgeError: status.HTTP_409_CONFLICT,
    }
    status_code = error_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    detail = (
        str(exc)
        if status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
        else 'An unexpected error occurred with badges.'
    )
    raise HTTPException(status_code=status_code, detail=detail)


# ---------------------- Rotas Públicas ----------------------


@router.get(
    '/{badge_id}',
    response_model=BadgeResponse,
    status_code=status.HTTP_200_OK,
)
def get_badge(badge_id: UUID, service: BadgeService = Depends(_service)):
    try:
        return service.get_badge(badge_id)
    except BadgeNotFoundError as e:
        _raise_http_error(e)


@router.get(
    '/',
    response_model=PaginationResponse[BadgeResponse],
    status_code=status.HTTP_200_OK,
)
def list_badges(
    community_id: UUID,
    params: PaginationSearchParams = Depends(),
    service: BadgeService = Depends(_service),
):
    return service.list_badges(community_id, params)


@router.get(
    '/member/{member_id}',
    response_model=List[BadgeResponse],
    status_code=status.HTTP_200_OK,
)
def list_badges_for_member(member_id: UUID, service: BadgeService = Depends(_service)):
    try:
        badges = service.list_badges_for_member(member_id)
        return [BadgeResponse.model_validate(badge) for badge in badges]
    except Exception as e:
        _raise_http_error(e)


# ---------------------- Rotas Admin ----------------------


@admin_router.post(
    '/', response_model=BadgeResponse, status_code=status.HTTP_201_CREATED
)
def create_badge(badge: BadgeCreate, service: BadgeService = Depends(_service)):
    try:
        return service.create_badge(badge)
    except (BadgeAlreadyExistsError, UnexpectedBadgeError) as e:
        _raise_http_error(e)


@admin_router.patch(
    '/{badge_id}',
    response_model=BadgeResponse,
    status_code=status.HTTP_200_OK,
)
def update_badge(
    badge_id: UUID,
    badge_update: BadgeUpdate,
    service: BadgeService = Depends(_service),
):
    try:
        return service.update_badge(badge_id, badge_update)
    except (
        BadgeNotFoundError,
        BadgeAlreadyExistsError,
        UnexpectedBadgeError,
    ) as e:
        _raise_http_error(e)


@admin_router.delete('/{badge_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_badge(badge_id: UUID, service: BadgeService = Depends(_service)):
    try:
        service.delete_badge(badge_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (
        BadgeNotFoundError,
        CannotDeleteSystemBadgeError,
        UnexpectedBadgeError,
    ) as e:
        _raise_http_error(e)


@admin_router.post('/assign', status_code=status.HTTP_201_CREATED)
def assign_badge(
    assignment: MemberBadgeCreate, service: BadgeService = Depends(_service)
):
    try:
        service.assign_badge_to_user(assignment)
        return Response(status_code=status.HTTP_201_CREATED)
    except (
        BadgeNotFoundError,
        MemberAlreadyHasBadgeError,
        UnexpectedBadgeError,
    ) as e:
        _raise_http_error(e)


@admin_router.delete(
    '/revoke/{member_id}/{badge_id}', status_code=status.HTTP_204_NO_CONTENT
)
def revoke_badge(
    member_id: UUID, badge_id: UUID, service: BadgeService = Depends(_service)
):
    try:
        service.revoke_badge_from_user(member_id, badge_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (MemberBadgeNotFoundError, UnexpectedBadgeError) as e:
        _raise_http_error(e)
