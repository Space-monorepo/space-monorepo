import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.users.schema import (
    ConnectionStatusEnum,
    LoginSchema,
    UserConnectionCreate,
    UserConnectionResponse,
    UserConnectionUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)


@pytest.mark.unit
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


@pytest.mark.unit
def test_user_update_schema():
    user_updated = UserUpdate(email='new_johndoe@example.com')

    assert user_updated.model_dump(exclude_unset=True) == {
        'email': 'new_johndoe@example.com',
    }


@pytest.mark.unit
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


@pytest.mark.unit
def test_connection_status_enum():
    """Test ConnectionStatusEnum values"""
    assert ConnectionStatusEnum.pending.value == 'pending'
    assert ConnectionStatusEnum.accepted.value == 'accepted'
    assert ConnectionStatusEnum.rejected.value == 'rejected'
    assert ConnectionStatusEnum.blocked.value == 'blocked'


@pytest.mark.unit
def test_user_connection_create_schema():
    """Test UserConnectionCreate schema validation"""
    addressee_id = uuid.uuid4()

    connection_create = UserConnectionCreate(addressee_id=addressee_id)

    assert connection_create.model_dump() == {
        'addressee_id': addressee_id,
    }


@pytest.mark.unit
def test_user_connection_create_invalid_schema():
    """Test UserConnectionCreate schema with invalid data"""
    # Test invalid UUID format
    with pytest.raises(ValidationError):
        UserConnectionCreate(addressee_id='invalid-uuid')

    # Test missing required field
    with pytest.raises(ValidationError):
        UserConnectionCreate()


@pytest.mark.unit
def test_user_connection_update_schema():
    """Test UserConnectionUpdate schema validation"""
    connection_update = UserConnectionUpdate(status=ConnectionStatusEnum.accepted)

    assert connection_update.model_dump() == {
        'status': 'accepted',
    }

    # Test with different statuses
    update_rejected = UserConnectionUpdate(status=ConnectionStatusEnum.rejected)
    assert update_rejected.model_dump() == {
        'status': 'rejected',
    }

    update_blocked = UserConnectionUpdate(status=ConnectionStatusEnum.blocked)
    assert update_blocked.model_dump() == {
        'status': 'blocked',
    }


@pytest.mark.unit
def test_user_connection_update_invalid_schema():
    """Test UserConnectionUpdate schema with invalid data"""
    # Test invalid status
    with pytest.raises(ValidationError):
        UserConnectionUpdate(status='invalid_status')

    # Test missing required field
    with pytest.raises(ValidationError):
        UserConnectionUpdate()


@pytest.mark.unit
def test_user_connection_response_schema():
    """Test UserConnectionResponse schema validation"""
    connection_id = uuid.uuid4()
    requester_id = uuid.uuid4()
    addressee_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    connection_response = UserConnectionResponse(
        id=connection_id,
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=ConnectionStatusEnum.pending,
        created_at=created_at,
        updated_at=updated_at,
        rejected_at=None,
    )

    assert connection_response.model_dump() == {
        'id': connection_id,
        'requester_id': requester_id,
        'addressee_id': addressee_id,
        'status': 'pending',
        'created_at': created_at,
        'updated_at': updated_at,
        'rejected_at': None,
    }


@pytest.mark.unit
def test_user_connection_response_with_rejected_at():
    """Test UserConnectionResponse schema with rejected_at field"""
    connection_id = uuid.uuid4()
    requester_id = uuid.uuid4()
    addressee_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()
    rejected_at = datetime.now()

    connection_response = UserConnectionResponse(
        id=connection_id,
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=ConnectionStatusEnum.rejected,
        created_at=created_at,
        updated_at=updated_at,
        rejected_at=rejected_at,
    )

    assert connection_response.model_dump() == {
        'id': connection_id,
        'requester_id': requester_id,
        'addressee_id': addressee_id,
        'status': 'rejected',
        'created_at': created_at,
        'updated_at': updated_at,
        'rejected_at': rejected_at,
    }


@pytest.mark.unit
def test_user_connection_response_all_statuses():
    """Test UserConnectionResponse schema with all possible statuses"""
    connection_id = uuid.uuid4()
    requester_id = uuid.uuid4()
    addressee_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    # Test accepted status
    accepted_response = UserConnectionResponse(
        id=connection_id,
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=ConnectionStatusEnum.accepted,
        created_at=created_at,
        updated_at=updated_at,
        rejected_at=None,
    )
    assert accepted_response.status == ConnectionStatusEnum.accepted

    # Test blocked status
    blocked_response = UserConnectionResponse(
        id=connection_id,
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=ConnectionStatusEnum.blocked,
        created_at=created_at,
        updated_at=updated_at,
        rejected_at=None,
    )
    assert blocked_response.status == ConnectionStatusEnum.blocked


@pytest.mark.unit
def test_user_connection_response_invalid_schema():
    """Test UserConnectionResponse schema with invalid data"""
    connection_id = uuid.uuid4()
    requester_id = uuid.uuid4()
    addressee_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    # Test invalid status
    with pytest.raises(ValidationError):
        UserConnectionResponse(
            id=connection_id,
            requester_id=requester_id,
            addressee_id=addressee_id,
            status='invalid_status',
            created_at=created_at,
            updated_at=updated_at,
            rejected_at=None,
        )

    # Test invalid UUID formats
    with pytest.raises(ValidationError):
        UserConnectionResponse(
            id='invalid-uuid',
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=ConnectionStatusEnum.pending,
            created_at=created_at,
            updated_at=updated_at,
            rejected_at=None,
        )

    # Test missing required fields
    with pytest.raises(ValidationError):
        UserConnectionResponse(
            id=connection_id,
            requester_id=requester_id,
            addressee_id=addressee_id,
            # missing status
            created_at=created_at,
            updated_at=updated_at,
            rejected_at=None,
        )


@pytest.mark.unit
def test_user_connection_model_config():
    """Test UserConnectionResponse model configuration"""
    connection_id = uuid.uuid4()
    requester_id = uuid.uuid4()
    addressee_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    connection_response = UserConnectionResponse(
        id=connection_id,
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=ConnectionStatusEnum.pending,
        created_at=created_at,
        updated_at=updated_at,
        rejected_at=None,
    )

    # Test that enum values are used (not enum objects)
    model_dict = connection_response.model_dump()
    assert isinstance(model_dict['status'], str)
    assert model_dict['status'] == 'pending'

    # Test model_config keys exist
    assert 'from_attributes' in connection_response.model_config
    assert 'use_enum_values' in connection_response.model_config
    assert 'json_schema_extra' in connection_response.model_config

    # Test from_attributes is True for ORM compatibility
    assert connection_response.model_config['from_attributes'] is True

    # Test use_enum_values is True for proper enum serialization
    assert connection_response.model_config['use_enum_values'] is True
