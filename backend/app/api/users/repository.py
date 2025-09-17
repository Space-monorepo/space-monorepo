from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.api.users.model import User, UserConnection
from app.core.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
        self.db = db

    def get_by_email(self, email: str) -> User | bool:
        return self.db.query(User).filter(User.email == email).first()


class UserConnectionRepository(BaseRepository[UserConnection]):
    def __init__(self, db: Session):
        super().__init__(UserConnection, db)
        self.db = db

    # Connection methods
    def get_connection_by_id(self, connection_id: UUID) -> UserConnection | None:
        """Get connection by ID"""
        return (
            self.db.query(UserConnection)
            .filter(UserConnection.id == connection_id)
            .first()
        )

    def check_existing_connection(
        self, requester_id: UUID, addressee_id: UUID
    ) -> UserConnection | None:
        """Check if connection exists between two users (bidirectional)"""
        return (
            self.db.query(UserConnection)
            .filter(
                or_(
                    and_(
                        UserConnection.requester_id == requester_id,
                        UserConnection.addressee_id == addressee_id,
                    ),
                    and_(
                        UserConnection.requester_id == addressee_id,
                        UserConnection.addressee_id == requester_id,
                    ),
                )
            )
            .first()
        )

    def check_rejection_cooldown(self, requester_id: UUID, addressee_id: UUID) -> bool:
        """Check if there's an active rejection cooldown (1 hour)"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        rejected_connection = (
            self.db.query(UserConnection)
            .filter(
                and_(
                    UserConnection.requester_id == requester_id,
                    UserConnection.addressee_id == addressee_id,
                    UserConnection.status == 'rejected',
                    UserConnection.rejected_at > one_hour_ago,
                )
            )
            .first()
        )

        return rejected_connection is not None

    def create_connection_request(
        self, requester_id: UUID, addressee_id: UUID
    ) -> UserConnection:
        """Create a new connection request"""
        connection = UserConnection(
            requester_id=requester_id, addressee_id=addressee_id, status='pending'
        )

        self.db.add(connection)
        self.db.flush()
        self.db.refresh(connection)
        return connection

    def accept_connection(
        self, connection_id: UUID, user_id: UUID
    ) -> UserConnection | None:
        """Accept a connection request - only addressee can accept"""
        connection = (
            self.db.query(UserConnection)
            .filter(
                and_(
                    UserConnection.id == connection_id,
                    UserConnection.addressee_id == user_id,
                    UserConnection.status == 'pending',
                )
            )
            .first()
        )

        if not connection:
            return None

        connection.status = 'accepted'
        self.db.flush()
        self.db.refresh(connection)
        return connection

    def reject_connection(
        self, connection_id: UUID, user_id: UUID
    ) -> UserConnection | None:
        """Reject a connection request - only addressee can reject"""
        connection = (
            self.db.query(UserConnection)
            .filter(
                and_(
                    UserConnection.id == connection_id,
                    UserConnection.addressee_id == user_id,
                    UserConnection.status == 'pending',
                )
            )
            .first()
        )

        if not connection:
            return None

        connection.status = 'rejected'
        connection.rejected_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(connection)
        return connection

    def delete_connection(self, connection_id: UUID, user_id: UUID) -> bool:
        """Delete an existing connection - either participant can delete"""
        connection = (
            self.db.query(UserConnection)
            .filter(
                and_(
                    UserConnection.id == connection_id,
                    or_(
                        UserConnection.requester_id == user_id,
                        UserConnection.addressee_id == user_id,
                    ),
                )
            )
            .first()
        )

        if not connection:
            return False

        self.db.delete(connection)
        self.db.flush()
        return True

    def get_user_connections(
        self, user_id: UUID, status: str = None
    ) -> list[UserConnection]:
        """Get all connections for a user, optionally filtered by status"""
        query = self.db.query(UserConnection).filter(
            or_(
                UserConnection.requester_id == user_id,
                UserConnection.addressee_id == user_id,
            )
        )

        if status:
            query = query.filter(UserConnection.status == status)

        return query.all()

    def validate_user_participation(self, connection_id: UUID, user_id: UUID) -> bool:
        """Validate if user participates in the connection"""
        connection = (
            self.db.query(UserConnection)
            .filter(
                and_(
                    UserConnection.id == connection_id,
                    or_(
                        UserConnection.requester_id == user_id,
                        UserConnection.addressee_id == user_id,
                    ),
                )
            )
            .first()
        )

        return connection is not None
