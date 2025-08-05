import datetime

import bcrypt
import jwt

from app.auth.schema import TokenSchema
from app.core.config import settings
from app.core.transaction import TransactionManager
from app.users.exceptions import UserNotAuthenticatedError
from app.users.model import User
from app.users.schema import LoginSchema


class AuthService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


    def verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


    def authenticate_login(
            self,
            email: str, 
            password: str, 
    ) -> User:
        from app.users.service import UserService
        user_service = UserService(self.tm)
        user: User = user_service.get_by_email(email)
        password_verified = self.verify_password(password, user.hashed_password)
        if not password_verified:
            raise UserNotAuthenticatedError('User not authenticated.')
        return user


    def login(self, user: LoginSchema) -> TokenSchema:
        authenticated_user = self.authenticate_login(user.email, user.password)
        payload = {'sub': authenticated_user.email}
        return self.create_token(payload)


    def create_token(self, payload: dict, exp: datetime.datetime | None = None) -> TokenSchema:
        expires_at = exp or datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload.update({'exp': expires_at})
        if exp:
            payload.update({'exp': exp})
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return TokenSchema(access_token=access_token, exp=payload.get('exp'))

