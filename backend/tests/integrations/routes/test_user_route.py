
import pytest
from fastapi import status

from app.api.users.exceptions import UserNotFoundError
from app.api.users.schema import UserCreate, UserResponse, UserStatusEnum, UserUpdate
from app.api.users.service import UserService


def test_create_user_route(transaction_manager, client_sql):
    user = UserCreate(
        email='johndoe@example.com',
        name='John Doe',
        hashed_password='hashed_password',
        profile_image_url=None,
        reputation_level=1,
        status=UserStatusEnum.pending,
    )

    response = client_sql.post('/users/signup', json=user.model_dump(mode='json'))

    user_on_db = UserService(transaction_manager).get_by_email(user.email)
    user_response = UserResponse.model_validate(user_on_db)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


def test_get_user_by_id_route(authenticate_client, user_on_db):
    response = authenticate_client.get('/users/me')
    assert response.status_code == status.HTTP_200_OK
    user_response = UserResponse.model_validate(user_on_db)
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


def test_get_user_by_email_route(client_sql, user_on_db):
    response = client_sql.get(f'/users/{user_on_db.email}')
    assert response.status_code == status.HTTP_200_OK
    user_response = UserResponse.model_validate(user_on_db)
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


def test_update_user_route(transaction_manager, authenticate_client, user_on_db):
    user = UserUpdate(email='new_johndoe@example.com')

    response = authenticate_client.patch(
        '/users/me', json=user.model_dump(mode='json', exclude_unset=True)
    )

    user_on_db = UserService(transaction_manager).get_user(user_on_db.id)
    assert response.status_code == status.HTTP_200_OK
    assert user_on_db.email == 'new_johndoe@example.com'


def test_delete_user_route(transaction_manager, authenticate_client, user_on_db):
    response = authenticate_client.delete('/users/me')
    assert response.status_code == status.HTTP_200_OK

    with pytest.raises(UserNotFoundError):
        user_on_db = UserService(transaction_manager).get_user(user_on_db.id)


def test_login_user_route(client_sql, user_on_db):
    response = client_sql.post(
        '/users/login',
        data={'username': user_on_db.email, 'password': 'hashed_password'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in response.json()
