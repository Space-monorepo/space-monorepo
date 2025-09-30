"""
Centralized WebSocket authentication system.

This module provides secure, standardized authentication for WebSocket connections
across all domains. It supports JWT token validation, user retrieval, and
connection-level security measures.

Key features:
- JWT token validation for WebSocket connections
- Multiple authentication methods (query params, headers, cookies)
- Rate limiting and connection throttling
- User session management
- Security logging and monitoring
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import UUID

import jwt
from fastapi import WebSocket, WebSocketException, status
from sqlalchemy.orm import Session

from app.api.users.model import User
from app.api.users.service import UserService
from app.core.config import settings
from app.core.transaction import TransactionManager

from .exceptions import (
    AuthenticationError,
    BroadcastError,
    EventHandlingError,
    EventValidationError,
    NamespaceError,
    RateLimitError,
    RoomError,
)

logger = logging.getLogger(__name__)


class WebSocketAuth:
    """
    Centralized WebSocket authentication manager.

    Handles authentication, rate limiting, and security for WebSocket connections
    across all domains in the application.
    """

    def __init__(self):
        # Rate limiting: IP -> (connection_count, last_reset)
        self._connection_limits: Dict[str, Tuple[int, datetime]] = {}

        # Active sessions: token_hash -> (user_id, last_activity)
        self._active_sessions: Dict[str, Tuple[str, datetime]] = {}

        # Configuration
        self.max_connections_per_ip = 10
        self.rate_limit_window = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour

        # Cleanup task
        self._cleanup_task = None
        self._started = False

    def _ensure_started(self):
        """Ensure background tasks are started (lazy initialization)."""
        if not self._started:
            self._started = True
            try:
                loop = asyncio.get_running_loop()
                if self._cleanup_task is None:
                    self._cleanup_task = loop.create_task(self._cleanup_loop())
            except RuntimeError:
                # No running event loop, tasks will be started when needed
                pass

    def _start_cleanup_task(self):
        """Start background task for cleaning up expired sessions and limits."""
        self._ensure_started()

    async def _cleanup_loop(self):
        """Background cleanup of expired data."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                await self._cleanup_expired_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Error in WebSocket auth cleanup: {e}')

    async def _cleanup_expired_data(self):
        """Clean up expired sessions and rate limit data."""
        now = datetime.now(timezone.utc)

        # Clean up rate limits
        expired_ips = []
        for ip, (count, last_reset) in self._connection_limits.items():
            if (now - last_reset).total_seconds() > self.rate_limit_window:
                expired_ips.append(ip)

        for ip in expired_ips:
            del self._connection_limits[ip]

        # Clean up expired sessions
        expired_sessions = []
        for token_hash, (user_id, last_activity) in self._active_sessions.items():
            if (now - last_activity).total_seconds() > self.session_timeout:
                expired_sessions.append(token_hash)

        for token_hash in expired_sessions:
            del self._active_sessions[token_hash]

        if expired_ips or expired_sessions:
            logger.debug(
                f'Cleaned up {len(expired_ips)} IP limits and {len(expired_sessions)} expired sessions'
            )

    @staticmethod
    def _get_client_ip(websocket: WebSocket) -> str:
        """Extract client IP from WebSocket connection."""
        # Try to get real IP from headers (for proxy setups)
        forwarded_for = websocket.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in case of multiple proxies
            return forwarded_for.split(',')[0].strip()

        real_ip = websocket.headers.get('x-real-ip')
        if real_ip:
            return real_ip.strip()

        # Fallback to direct connection IP
        if hasattr(websocket, 'client') and websocket.client:
            return websocket.client.host

        return 'unknown'

    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client IP is within rate limits."""
        now = datetime.now(timezone.utc)

        if client_ip not in self._connection_limits:
            self._connection_limits[client_ip] = (1, now)
            return True

        count, last_reset = self._connection_limits[client_ip]

        # Reset counter if window has expired
        if (now - last_reset).total_seconds() > self.rate_limit_window:
            self._connection_limits[client_ip] = (1, now)
            return True

        # Check if within limits
        if count >= self.max_connections_per_ip:
            return False

        # Increment counter
        self._connection_limits[client_ip] = (count + 1, last_reset)
        return True

    @staticmethod
    def _extract_token(websocket: WebSocket) -> Optional[str]:
        """
        Extract JWT token from WebSocket connection.

        Tries multiple methods in order:
        1. Query parameter 'token'
        2. Authorization header (Bearer format)
        3. Cookie 'access_token'

        Args:
            websocket: WebSocket connection

        Returns:
            JWT token string or None if not found
        """
        # Method 1: Query parameter
        token = websocket.query_params.get('token')
        if token:
            return token

        # Method 2: Authorization header
        auth_header = websocket.headers.get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix

        # Method 3: Cookie
        cookies = websocket.headers.get('cookie', '')
        for cookie in cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                if name == 'access_token':
                    return value

        return None

    @staticmethod
    def _validate_jwt_token(token: str) -> Dict[str, Any]:
        """
        Validate JWT token and extract payload.

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f'Invalid token: {str(e)}')
        except Exception as e:
            raise AuthenticationError(f'Token validation error: {str(e)}')

    @staticmethod
    async def _get_user_from_payload(payload: Dict[str, Any], session: Session) -> User:
        """
        Retrieve user from token payload.

        Args:
            payload: JWT token payload
            session: Database session

        Returns:
            User object

        Raises:
            AuthenticationError: If user not found or inactive
        """
        email = payload.get('sub')
        if not email:
            raise AuthenticationError('Token payload missing user identifier')

        # Additional payload validation
        user_id = payload.get('user_id')
        if user_id:
            try:
                UUID(user_id)  # Validate UUID format
            except ValueError:
                raise AuthenticationError('Invalid user ID format in token')

        # Get user from database
        try:
            with TransactionManager(session) as tm:
                user_service = UserService(tm)
                user = user_service.get_by_email(email, flag=None)

                if not user:
                    raise AuthenticationError(f'User not found: {email}')

                # Additional user validation
                if hasattr(user, 'status') and user.status == 'inactive':
                    raise AuthenticationError('User account is inactive')

                return user

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            logger.error(f'Database error during user retrieval: {e}')
            raise AuthenticationError('User retrieval failed')

    def _update_session(self, token: str, user_id: str):
        """Update session tracking for the token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        self._active_sessions[token_hash] = (user_id, datetime.now(timezone.utc))

    async def authenticate_websocket(
        self, websocket: WebSocket, session: Session
    ) -> User:
        """
        Authenticate WebSocket connection and return user.

        This is the main authentication method that should be used by
        all WebSocket endpoints across the application.

        Args:
            websocket: WebSocket connection
            session: Database session

        Returns:
            Authenticated User object

        Raises:
            WebSocketException: If authentication fails
        """
        # Ensure background tasks are started
        self._ensure_started()

        try:
            # Get client IP for rate limiting
            client_ip = self._get_client_ip(websocket)

            # Check rate limits
            if not self._check_rate_limit(client_ip):
                logger.warning(f'Rate limit exceeded for IP: {client_ip}')
                raise RateLimitError('Rate limit exceeded')

            # Extract token
            token = self._extract_token(websocket)
            if not token:
                raise AuthenticationError('Authentication token required')

            # Validate token
            payload = self._validate_jwt_token(token)

            # Get user
            user = await self._get_user_from_payload(payload, session)

            # Update session tracking
            self._update_session(token, str(user.id))

            # Log successful authentication
            logger.info(f'WebSocket authenticated: user_id={user.id}, ip={client_ip}')

            return user

        except (AuthenticationError, RateLimitError) as e:
            logger.warning(f'WebSocket authentication failed: {e}')
            raise self._convert_to_websocket_exception(e)
        except Exception as e:
            logger.error(f'WebSocket authentication error: {e}', exc_info=True)
            raise self._convert_to_websocket_exception(e)

    @staticmethod
    def _convert_to_websocket_exception(error: Exception) -> WebSocketException:
        """
        Convert custom WebSocket exceptions to FastAPI WebSocketException.

        Args:
            error: The exception to convert

        Returns:
            WebSocketException with appropriate code and reason
        """
        if isinstance(error, (AuthenticationError, RateLimitError, EventValidationError,
                            EventHandlingError, RoomError, NamespaceError, BroadcastError)):
            return WebSocketException(code=error.code, reason=str(error))
        else:
            return WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f'Authentication service error: {str(error)}'
            )

    @staticmethod
    async def validate_user_permission(
        user: User,
        namespace: str,
        action: str,
        resource_id: Optional[str] = None,
        **context,
    ) -> bool:
        """
        Validate user permissions for WebSocket actions.

        This method can be extended by domains to implement specific
        permission checks based on their business logic.

        Args:
            user: Authenticated user
            namespace: WebSocket namespace (e.g., 'chat', 'notifications')
            action: Action being performed (e.g., 'join_room', 'send_message')
            resource_id: Optional resource identifier
            **context: Additional context for permission checking

        Returns:
            True if user has permission, False otherwise
        """
        # Base permission checks
        if not user:
            return False

        # Check if user is active
        if hasattr(user, 'status') and user.status != 'active':
            return False

        # Domain-specific permission logic should be implemented
        # by individual services using this method as a template

        # For now, allow all authenticated users
        # Individual domains should override this with their logic
        return True

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get authentication and connection statistics."""
        now = datetime.now(timezone.utc)

        # Count active rate limits
        active_limits = sum(
            1
            for count, last_reset in self._connection_limits.values()
            if (now - last_reset).total_seconds() <= self.rate_limit_window
        )

        # Count active sessions
        active_sessions = sum(
            1
            for user_id, last_activity in self._active_sessions.values()
            if (now - last_activity).total_seconds() <= self.session_timeout
        )

        return {
            'active_rate_limits': active_limits,
            'active_sessions': active_sessions,
            'total_tracked_ips': len(self._connection_limits),
            'total_tracked_sessions': len(self._active_sessions),
            'rate_limit_window': self.rate_limit_window,
            'session_timeout': self.session_timeout,
            'max_connections_per_ip': self.max_connections_per_ip,
        }

    async def revoke_user_sessions(self, user_id: str) -> int:
        """
        Revoke all active sessions for a user.

        Useful for security purposes (password change, account compromise, etc.)

        Args:
            user_id: User ID to revoke sessions for

        Returns:
            Number of sessions revoked
        """
        revoked_count = 0
        sessions_to_remove = []

        for token_hash, (
            session_user_id,
            last_activity,
        ) in self._active_sessions.items():
            if session_user_id == user_id:
                sessions_to_remove.append(token_hash)
                revoked_count += 1

        for token_hash in sessions_to_remove:
            del self._active_sessions[token_hash]

        if revoked_count > 0:
            logger.info(f'Revoked {revoked_count} WebSocket sessions for user {user_id}')

        return revoked_count

    async def cleanup_ip_limits(self, ip_address: str) -> bool:
        """
        Clear rate limits for a specific IP address.

        Useful for administrative purposes or after resolving false positives.

        Args:
            ip_address: IP address to clear limits for

        Returns:
            True if limits were cleared, False if IP not found
        """
        if ip_address in self._connection_limits:
            del self._connection_limits[ip_address]
            logger.info(f'Cleared rate limits for IP: {ip_address}')
            return True
        return False

    def __del__(self):
        """Cleanup when auth manager is destroyed."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# Global WebSocket authentication instance
websocket_auth = WebSocketAuth()
