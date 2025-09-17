from uuid import UUID

from app.api.communities.schema import CommunityResponse
from app.api.users.exceptions import (
    ConnectionAlreadyExistsError,
    ConnectionCooldownError,
    ConnectionNotFoundError,
    SelfConnectionError,
    UnexpectedConnectionError,
    UnexpectedUserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.api.users.model import User, UserConnection
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
        self.connection_repo = tm.get_user_connection_repository()

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
        user = self.user_repo.get_by_id(str(id))
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

    def request_connection(
        self, requester_id: UUID, addressee_id: UUID
    ) -> UserConnection:
        """Send a connection request to another user"""
        _ = self.get_user(requester_id)  # Validate user exists
        _ = self.get_user(addressee_id)  # Validate user exists

        if requester_id == addressee_id:
            raise SelfConnectionError('Cannot send connection request to yourself')

        existing_connection = self.connection_repo.check_existing_connection(
            requester_id, addressee_id
        )
        if existing_connection:
            raise ConnectionAlreadyExistsError(
                'Connection already exists between these users'
            )

        if self.connection_repo.check_rejection_cooldown(requester_id, addressee_id):
            raise ConnectionCooldownError(
                'Cannot send connection request. Please wait 1 hour after rejection'
            )

        try:
            return self.connection_repo.create_connection_request(
                requester_id, addressee_id
            )
        except Exception as e:
            raise UnexpectedConnectionError(
                'Unexpected error creating connection request'
            ) from e

    def accept_connection(self, connection_id: UUID, user_id: UUID) -> UserConnection:
        """Accept a connection request"""
        try:
            connection = self.connection_repo.accept_connection(connection_id, user_id)
            if not connection:
                raise ConnectionNotFoundError(
                    'Connection not found or you are not authorized to accept this request'
                )
            return connection
        except ConnectionNotFoundError:
            raise
        except Exception as e:
            raise UnexpectedConnectionError(
                'Unexpected error accepting connection'
            ) from e

    def reject_connection(self, connection_id: UUID, user_id: UUID) -> UserConnection:
        """Reject a connection request"""
        try:
            connection = self.connection_repo.reject_connection(connection_id, user_id)
            if not connection:
                raise ConnectionNotFoundError(
                    'Connection not found or you are not authorized to reject this request'
                )
            return connection
        except ConnectionNotFoundError:
            raise
        except Exception as e:
            raise UnexpectedConnectionError(
                'Unexpected error rejecting connection'
            ) from e

    def delete_connection(self, connection_id: UUID, user_id: UUID) -> bool:
        """Delete an existing connection"""
        try:
            success = self.connection_repo.delete_connection(connection_id, user_id)
            if not success:
                raise ConnectionNotFoundError(
                    'Connection not found or you are not authorized to delete this connection'
                )
            return success
        except ConnectionNotFoundError:
            raise
        except Exception as e:
            raise UnexpectedConnectionError(
                'Unexpected error deleting connection'
            ) from e

    def get_connection(self, connection_id: UUID) -> UserConnection:
        """Get connection by ID"""
        connection = self.connection_repo.get_connection_by_id(connection_id)
        if not connection:
            raise ConnectionNotFoundError('Connection not found')
        return connection

    def get_connection_status(
        self, user1_id: UUID, user2_id: UUID
    ) -> UserConnection | None:
        """Get connection status between two users"""
        return self.connection_repo.check_existing_connection(user1_id, user2_id)

    def validate_connection_participation(
        self, connection_id: UUID, user_id: UUID
    ) -> bool:
        """Validate if user participates in the connection"""
        return self.connection_repo.validate_user_participation(connection_id, user_id)
