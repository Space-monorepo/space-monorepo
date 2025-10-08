"""
Custom SQLAlchemy types for cross-database compatibility.
"""

from uuid import UUID

from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's native UUID type when available,
    otherwise uses String(36) for databases like SQLite.

    This ensures UUIDs work seamlessly across different database backends
    without requiring manual type checking or conversion in repositories.

    Usage:
        from app.core.types import GUID

        class User(Base):
            id = Column(GUID, primary_key=True, default=uuid.uuid4)
    """

    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):  # noqa: PLR6301
        """
        Select the appropriate type based on the database dialect.

        PostgreSQL: Use native UUID type
        Others (SQLite, etc): Use String(36)
        """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):  # noqa: PLR6301
        """
        Process the value before sending to the database.

        Converts UUID objects to strings for non-PostgreSQL databases.
        """
        if value is None:
            return value

        if dialect.name == 'postgresql':
            # PostgreSQL handles UUID natively
            return value
        else:
            # Convert to string for SQLite and others
            return str(value) if isinstance(value, UUID) else value

    def process_result_value(self, value, dialect):  # noqa: PLR6301
        """
        Process the value when retrieving from the database.

        Converts strings back to UUID objects for consistency.
        """
        if value is None:
            return value

        # Ensure we always return a UUID object
        if isinstance(value, UUID):
            return value
        else:
            return UUID(value)
