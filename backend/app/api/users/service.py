from uuid import UUID

from app.api.communities.schema import CommunityResponse
from app.api.users.exceptions import (
    UnexpectedUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.api.users.model import User
from app.api.users.schema import UserCreate, UserUpdate
from app.auth.security import AuthService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams


class UserService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.auth_service = AuthService(tm)
        self.member_repo = tm.get_member_repository()
        self.user_repo = tm.get_user_repository()

    def create_user(self, user: UserCreate) -> User:
        user_already_exists = self.get_by_email(user.email, 'signup')
        if user_already_exists:
            raise UserAlreadyExistsError('User already exists.')

        # TODO: Adicionar a verificacao de email

        user.hashed_password = self.auth_service.hash_password(user.hashed_password)
        new_user = User(**user.model_dump())
        try:
            return self.user_repo.save(new_user)
        except Exception as e:
            raise UnexpectedUserError('Unexpected error creating user') from e

    def get_user(self, id: UUID) -> User:
        user = self.user_repo.get_by_id(id)
        if not user:
            raise UserNotFoundError('User not found')
        return user

    def get_by_email(self, email: str, flag: str | None = None) -> User:
        user = self.user_repo.get_by_email(email)
        if flag == 'signup':
            return user
        else:
            if not user:
                raise UserNotFoundError(f'User with email {email} not found.')
            return user

    def update_user(self, id: UUID, user_updated: UserUpdate) -> User:
        user = self.get_user(id)
        for key, value in user_updated.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        try:
            return self.user_repo.save(user)
        except Exception as e:
            raise UnexpectedUserError('Unexpected error updating user') from e

    def delete_user(self, id: UUID) -> bool:
        user = self.get_user(id)
        try:
            self.user_repo.delete(user)
            return True
        except Exception as e:
            raise UnexpectedUserError('Unexpected error deleting user') from e

    def list_communities(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommunityResponse]:
        memberships, total = self.member_repo.list_communities_by_user(user_id, params)
        communities = [
            CommunityResponse.model_validate(community) for community in memberships
        ]
        return PaginationResponse(
            items=communities,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )
