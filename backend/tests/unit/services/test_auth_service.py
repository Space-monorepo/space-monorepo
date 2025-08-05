import datetime

from app.auth.deps import get_current_user
from app.auth.schema import TokenSchema
from app.auth.security import AuthService
from app.api.users.schema import LoginSchema


def test_authenticate_login(transaction_manager, user_on_db):
    user = LoginSchema(email='johndoe@example.com', password='hashed_password')
    authenticated_user = AuthService(transaction_manager).authenticate_login(
        user.email, user.password
    )
    assert authenticated_user.email == user_on_db.email


def test_create_token(transaction_manager):
    payload = {'sub': 'johndoe@example.com'}
    token = AuthService(transaction_manager).create_token(payload)
    assert isinstance(token, TokenSchema)
    assert token.access_token is not None
    assert token.exp < datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
        minutes=31
    )


def test_get_current_user(session_sql, transaction_manager, user_on_db):
    payload = {'sub': user_on_db.email}
    token = AuthService(transaction_manager).create_token(payload)
    current_user = get_current_user(session_sql, token.access_token)
    assert current_user.email == user_on_db.email
