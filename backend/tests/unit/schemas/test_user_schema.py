from datetime import datetime
import uuid

from app.users.schema import LoginSchema, UserCreate, UserResponse, UserUpdate


def test_user_input_schema():
    user = UserCreate(
        email='johndoe@example.com',
        name='John Doe',
        hashed_password='hashed_password',
        profile_image_url=None,
        reputation_level=1,
        status='pending',
    )

    assert user.model_dump() == {
        'email': 'johndoe@example.com',
        'name': 'John Doe',
        'hashed_password': 'hashed_password',
        'profile_image_url': None,
        'reputation_level': 1,
        'status': 'pending',
    }

    user = LoginSchema(email='johndoe@example.com', password='hashed_password')

    assert user.model_dump() == {
        'email': 'johndoe@example.com',
        'password': 'hashed_password',
    }


def test_user_update_schema():
    user_updated = UserUpdate(email='new_johndoe@example.com')

    assert user_updated.model_dump(exclude_unset=True) == {
        'email': 'new_johndoe@example.com',
    }


def test_user_response_schema():
    user_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    user_response = UserResponse(
        id=user_id,
        email='johndoe@example.com',
        name='John Doe',
        hashed_password='hashed_password',
        profile_image_url=None,
        reputation_level=1,
        status='pending',
        created_at=created_at,
        updated_at=updated_at,
    )

    assert user_response.model_dump() == {
        'id': user_id,
        'email': 'johndoe@example.com',
        'name': 'John Doe',
        'hashed_password': 'hashed_password',
        'profile_image_url': None,
        'reputation_level': 1,
        'status': 'pending',
        'created_at': created_at,
        'updated_at': updated_at,
    }
