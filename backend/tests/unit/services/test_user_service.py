from app.api.users.model import User
from app.api.users.schema import UserCreate, UserUpdate
from app.api.users.service import UserService


def test_create_user_service(session_sql, transaction_manager):
    user = UserCreate(
        email='johndoe@example.com',
        name='John Doe',
        hashed_password='hashed_password',
        profile_image_url=None,
        reputation_level=1,
        status='pending',
    )

    user = UserService(transaction_manager).create_user(user)
    assert user.id is not None
    assert user.email == 'johndoe@example.com'

    user = session_sql.query(User).filter(User.email == 'johndoe@example.com').first()
    assert user is not None
    assert user.email == 'johndoe@example.com'


def test_get_user_by_id_service(transaction_manager, user_on_db):
    user = UserService(transaction_manager).get_user(user_on_db.id)
    assert user is not None
    assert user.email == 'johndoe@example.com'


def test_get_user_by_email_service(transaction_manager, user_on_db):
    user = UserService(transaction_manager).get_by_email(user_on_db.email)
    assert user is not None
    assert user.email == 'johndoe@example.com'


def test_update_user_service(transaction_manager, user_on_db):
    user = UserUpdate(email='new_johndoe@example.com')
    user = UserService(transaction_manager).update_user(user_on_db.id, user)
    assert user is not None
    assert user.email == 'new_johndoe@example.com'


def test_delete_user_service(session_sql, transaction_manager, user_on_db):
    result = UserService(transaction_manager).delete_user(user_on_db.id)
    assert result is True
    user = session_sql.query(User).filter(User.id == user_on_db.id).first()
    assert user is None
