import pytest
from fastapi import status

from app.api.users.exceptions import (
    UserNotFoundError,
)
from app.api.users.schema import (
    UserConnectionCreate,
    UserCreate,
    UserResponse,
    UserStatusEnum,
    UserUpdate,
)
from app.api.users.service import UserService


@pytest.mark.integration
def test_create_user_route(transaction_manager, client_sql):
    user = UserCreate(
        email='johndoe@example.com',
        name='John Doe',
        username='johndoe',
        hashed_password='hashed_password',
        bio='I am a software engineer',
        profile_image_url=None,
        status=UserStatusEnum.PENDING,
    )

    response = client_sql.post('/users/signup', json=user.model_dump(mode='json'))

    user_on_db = UserService(transaction_manager).get_by_email(user.email)
    user_response = UserResponse.model_validate(user_on_db)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


@pytest.mark.integration
def test_get_user_by_id_route(authenticate_client, user_on_db):
    response = authenticate_client.get('/users/me')
    assert response.status_code == status.HTTP_200_OK
    user_response = UserResponse.model_validate(user_on_db)
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


@pytest.mark.integration
def test_get_user_by_user_id_route(client_sql, user_on_db):
    response = client_sql.get(f'/users/user/{user_on_db.id}')
    assert response.status_code == status.HTTP_200_OK
    user_response = UserResponse.model_validate(user_on_db)
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


@pytest.mark.integration
def test_get_user_by_email_route(client_sql, user_on_db):
    response = client_sql.get(f'/users/{user_on_db.email}')
    assert response.status_code == status.HTTP_200_OK
    user_response = UserResponse.model_validate(user_on_db)
    assert response.json() == user_response.model_dump(mode='json', by_alias=True)


@pytest.mark.integration
def test_update_user_route(transaction_manager, authenticate_client, user_on_db):
    user = UserUpdate(email='new_johndoe@example.com')

    response = authenticate_client.patch(
        '/users/me', json=user.model_dump(mode='json', exclude_unset=True)
    )

    user_on_db = UserService(transaction_manager).get_user(user_on_db.id)
    assert response.status_code == status.HTTP_200_OK
    assert user_on_db.email == 'new_johndoe@example.com'


@pytest.mark.integration
def test_delete_user_route(transaction_manager, authenticate_client, user_on_db):
    response = authenticate_client.delete('/users/me')
    assert response.status_code == status.HTTP_200_OK

    with pytest.raises(UserNotFoundError):
        user_on_db = UserService(transaction_manager).get_user(user_on_db.id)


@pytest.mark.integration
def test_login_user_route(client_sql, user_on_db):
    response = client_sql.post(
        '/users/login',
        data={'username': user_on_db.email, 'password': 'hashed_password'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in response.json()


# Connection tests
@pytest.mark.integration
def test_request_connection_route(authenticate_client, secondary_user_on_db):
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)

    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['addressee_id'] == str(secondary_user_on_db.id)
    assert response_data['status'] == 'pending'


@pytest.mark.integration
def test_request_connection_self_connection_error(authenticate_client, user_on_db):
    connection_data = UserConnectionCreate(addressee_id=user_on_db.id)

    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['error_type'] == 'self_connection'


@pytest.mark.integration
def test_request_connection_already_exists_error(
    authenticate_client, secondary_user_on_db
):
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)

    # First request
    authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )

    # Second request should fail
    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()['error_type'] == 'connection_already_exists'


@pytest.mark.integration
def test_accept_connection_route(
    authenticate_client, authenticate_member_client, user_on_db, secondary_user_on_db
):
    # User sends connection request
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)
    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )
    connection_id = response.json()['id']

    # Secondary user accepts connection
    response = authenticate_member_client.put(
        f'/users/connections/{connection_id}/accept'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'accepted'


@pytest.mark.integration
def test_accept_connection_not_found_error(authenticate_client):
    fake_connection_id = '123e4567-e89b-12d3-a456-426614174000'

    response = authenticate_client.put(f'/users/connections/{fake_connection_id}/accept')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['error_type'] == 'connection_not_found'


@pytest.mark.integration
def test_reject_connection_route(
    authenticate_client, authenticate_member_client, user_on_db, secondary_user_on_db
):
    # User sends connection request
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)
    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )
    connection_id = response.json()['id']

    # Secondary user rejects connection
    response = authenticate_member_client.put(
        f'/users/connections/{connection_id}/reject'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'rejected'
    assert response.json()['rejected_at'] is not None


@pytest.mark.integration
def test_reject_connection_not_found_error(authenticate_client):
    fake_connection_id = '123e4567-e89b-12d3-a456-426614174000'

    response = authenticate_client.put(f'/users/connections/{fake_connection_id}/reject')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['error_type'] == 'connection_not_found'


@pytest.mark.integration
def test_delete_connection_route(
    authenticate_client, authenticate_member_client, user_on_db, secondary_user_on_db
):
    # User sends connection request
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)
    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )
    connection_id = response.json()['id']

    # Secondary user accepts connection
    authenticate_member_client.put(f'/users/connections/{connection_id}/accept')

    # User deletes connection
    response = authenticate_client.delete(f'/users/connections/{connection_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is True


@pytest.mark.integration
def test_delete_connection_not_found_error(authenticate_client):
    fake_connection_id = '123e4567-e89b-12d3-a456-426614174000'

    response = authenticate_client.delete(f'/users/connections/{fake_connection_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['error_type'] == 'connection_not_found'


@pytest.mark.integration
def test_get_connection_status_no_connection(authenticate_client, secondary_user_on_db):
    response = authenticate_client.get(
        f'/users/connections/status/{secondary_user_on_db.id}'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None


@pytest.mark.integration
def test_get_connection_status_pending(authenticate_client, secondary_user_on_db):
    # Send connection request
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)
    authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )

    # Check status
    response = authenticate_client.get(
        f'/users/connections/status/{secondary_user_on_db.id}'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'pending'


@pytest.mark.integration
def test_get_connection_status_accepted(
    authenticate_client, authenticate_member_client, user_on_db, secondary_user_on_db
):
    # Send connection request
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)
    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )
    connection_id = response.json()['id']

    # Accept connection
    authenticate_member_client.put(f'/users/connections/{connection_id}/accept')

    # Check status
    response = authenticate_client.get(
        f'/users/connections/status/{secondary_user_on_db.id}'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'accepted'


@pytest.mark.integration
def test_connection_workflow_complete(
    authenticate_client, authenticate_member_client, user_on_db, secondary_user_on_db
):
    """Test complete connection workflow: request -> accept -> can chat"""
    # 1. Send connection request
    connection_data = UserConnectionCreate(addressee_id=secondary_user_on_db.id)
    response = authenticate_client.post(
        '/users/connections/request', json=connection_data.model_dump(mode='json')
    )

    assert response.status_code == status.HTTP_201_CREATED
    connection_id = response.json()['id']

    # 2. Check status is pending
    response = authenticate_client.get(
        f'/users/connections/status/{secondary_user_on_db.id}'
    )
    assert response.json()['status'] == 'pending'

    # 3. Accept connection
    response = authenticate_member_client.put(
        f'/users/connections/{connection_id}/accept'
    )
    assert response.status_code == status.HTTP_200_OK

    # 4. Check final status is accepted
    response = authenticate_client.get(
        f'/users/connections/status/{secondary_user_on_db.id}'
    )
    assert response.json()['status'] == 'accepted'
