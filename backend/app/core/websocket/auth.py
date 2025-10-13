import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from uuid import UUID

import jwt
from fastapi import WebSocket, WebSocketException, status
from sqlalchemy.orm import Session

from app.api.users.model import User
from app.api.users.service import UserService
from app.core.config import settings
from app.core.transaction import TransactionManager

from .exceptions import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


class WebSocketAuth:
    """WebSocket authentication manager."""

    def __init__(self):
        self._connection_limits: Dict[str, Tuple[int, datetime]] = {}
        self._active_sessions: Dict[str, Tuple[str, datetime]] = {}

        if settings.ENVIRONMENT == 'test':
            self.max_connections_per_ip = 1000
            self.rate_limit_window = 300
            self.session_timeout = 3600
        else:
            self.max_connections_per_ip = 10
            self.rate_limit_window = 300
            self.session_timeout = 3600

    @staticmethod
    def _get_client_ip(websocket: WebSocket) -> str:
        forwarded_for = websocket.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = websocket.headers.get('x-real-ip')
        if real_ip:
            return real_ip.strip()

        if hasattr(websocket, 'client') and websocket.client:
            return websocket.client.host

        return 'unknown'

    def _check_rate_limit(self, client_ip: str) -> bool:
        now = datetime.now(timezone.utc)

        if client_ip not in self._connection_limits:
            self._connection_limits[client_ip] = (1, now)
            return True

        count, last_reset = self._connection_limits[client_ip]

        if (now - last_reset).total_seconds() > self.rate_limit_window:
            self._connection_limits[client_ip] = (1, now)
            return True

        if count >= self.max_connections_per_ip:
            return False

        self._connection_limits[client_ip] = (count + 1, last_reset)
        return True

    @staticmethod
    def _extract_token(websocket: WebSocket) -> Optional[str]:
        token = websocket.query_params.get('token')
        if token:
            return token

        auth_header = websocket.headers.get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]

        cookies = websocket.headers.get('cookie', '')
        for cookie in cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                if name == 'access_token':
                    return value

        return None

    @staticmethod
    def _validate_jwt_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError('Token expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f'Invalid token: {str(e)}')

    @staticmethod
    async def _get_user_from_payload(payload: dict, session: Session) -> User:
        email = payload.get('sub')
        if not email:
            raise AuthenticationError('Token missing user identifier')

        user_id = payload.get('user_id')
        if user_id:
            try:
                UUID(user_id)
            except ValueError:
                raise AuthenticationError('Invalid user ID format in token')

        with TransactionManager(session) as tm:
            user_service = UserService(tm)
            user = user_service.get_by_email(email, flag=None)

            if not user:
                raise AuthenticationError(f'User not found: {email}')

            if hasattr(user, 'status') and user.status == 'inactive':
                raise AuthenticationError('User account is inactive')

            return user

    def _update_session(self, token: str, user_id: str):
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        self._active_sessions[token_hash] = (user_id, datetime.now(timezone.utc))

    async def authenticate_websocket(
        self, websocket: WebSocket, session: Session
    ) -> User:
        try:
            client_ip = self._get_client_ip(websocket)

            if not self._check_rate_limit(client_ip):
                logger.warning(f'Rate limit exceeded for IP: {client_ip}')
                raise RateLimitError('Rate limit exceeded')

            token = self._extract_token(websocket)
            if not token:
                raise AuthenticationError('Authentication token required')

            payload = self._validate_jwt_token(token)
            user = await self._get_user_from_payload(payload, session)
            self._update_session(token, str(user.id))

            logger.info(f'WebSocket authenticated: user_id={user.id}, ip={client_ip}')
            return user

        except (AuthenticationError, RateLimitError) as e:
            logger.warning(f'WebSocket authentication failed: {e}')
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
        except Exception as e:
            logger.error(f'WebSocket authentication error: {e}', exc_info=True)
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason=f'Authentication service error: {str(e)}',
            )

    def get_connection_stats(self) -> dict:
        now = datetime.now(timezone.utc)

        active_limits = sum(
            1
            for count, last_reset in self._connection_limits.values()
            if (now - last_reset).total_seconds() <= self.rate_limit_window
        )

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
        }

    async def cleanup_expired_data(self):
        now = datetime.now(timezone.utc)

        expired_ips = [
            ip
            for ip, (count, last_reset) in self._connection_limits.items()
            if (now - last_reset).total_seconds() > self.rate_limit_window
        ]

        for ip in expired_ips:
            del self._connection_limits[ip]

        expired_sessions = [
            token_hash
            for token_hash, (user_id, last_activity) in self._active_sessions.items()
            if (now - last_activity).total_seconds() > self.session_timeout
        ]

        for token_hash in expired_sessions:
            del self._active_sessions[token_hash]

        if expired_ips or expired_sessions:
            logger.debug(
                f'Cleaned up {len(expired_ips)} IP limits and {len(expired_sessions)} sessions'
            )


websocket_auth = WebSocketAuth()
