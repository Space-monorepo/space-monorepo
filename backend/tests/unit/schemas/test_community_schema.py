import uuid
import pytest

from datetime import datetime
from pydantic import ValidationError

from app.api.communities.schema import (
    CommunityRelated,
    CommunityCreate,
    CommunityResponse,
    CommunityUpdate,
    CommunityTypeEnum,
    CommunityMemberRoleEnum,
    CommunityMemberStatusEnum,
    CommunityMemberCreate,
    CommunityMemberUpdate,
    CommunityMemberResponse,
)
from app.api.users.schema import UserResponse, UserStatusEnum


@pytest.mark.unit
def test_community_related_schema():
    community_id = uuid.uuid4()
    community = CommunityRelated(id=community_id, name='Test Community')

    assert community.model_dump() == {'id': community_id, 'name': 'Test Community'}


@pytest.mark.unit
def test_community_type_enum():
    assert CommunityTypeEnum.UNIVERSITY.value == 'university'
    assert CommunityTypeEnum.NEIGHBORHOOD.value == 'neighborhood'
    assert CommunityTypeEnum.COMPANY.value == 'company'
    assert CommunityTypeEnum.GOVERNMENT.value == 'government'
    assert CommunityTypeEnum.HEALTHCARE.value == 'healthcare'
    assert CommunityTypeEnum.RELIGIOUS.value == 'religious'
    assert CommunityTypeEnum.COMMERCIAL.value == 'commercial'
    assert CommunityTypeEnum.CLUB.value == 'club'


@pytest.mark.unit
def test_community_member_status_enum():
    assert CommunityMemberStatusEnum.ACTIVE.value == 'active'
    assert CommunityMemberStatusEnum.SUSPENDED.value == 'suspended'
    assert CommunityMemberStatusEnum.BANNED.value == 'banned'


@pytest.mark.unit
def test_community_member_role_enum():
    assert CommunityMemberRoleEnum.ADMIN.value == 'admin'
    assert CommunityMemberRoleEnum.MODERATOR.value == 'moderator'
    assert CommunityMemberRoleEnum.MEMBER.value == 'member'


@pytest.mark.unit
def test_community_create_schema():
    community = CommunityCreate(
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
    )

    assert community.model_dump() == {
        'name': 'Test Community',
        'description': 'Test Description',
        'type_community': 'university',
    }


@pytest.mark.unit
def test_community_update_schema():
    community_update = CommunityUpdate(
        name='Updated Community',
        description='Updated Description',
        type_community=CommunityTypeEnum.COMMERCIAL,
    )

    assert community_update.model_dump() == {
        'name': 'Updated Community',
        'description': 'Updated Description',
        'type_community': 'commercial',
    }

    # Test with partial updates
    partial_update = CommunityUpdate(
        name='Updated Community',
    )
    assert partial_update.model_dump() == {
        'name': 'Updated Community',
        'description': None,
        'type_community': None,
    }


@pytest.mark.unit
def test_community_response_schema():
    community_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    community = CommunityResponse(
        id=community_id,
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
        created_at=created_at,
        updated_at=updated_at,
    )

    assert community.model_dump() == {
        'id': community_id,
        'name': 'Test Community',
        'description': 'Test Description',
        'type_community': 'university',
        'created_at': created_at,
        'updated_at': updated_at,
    }


@pytest.mark.unit
def test_community_member_create_schema():
    user_id = str(uuid.uuid4())
    community_id = str(uuid.uuid4())

    member = CommunityMemberCreate(
        user_id=user_id,
        community_id=community_id,
        role=CommunityMemberRoleEnum.ADMIN,
        reputation=10,
        status_participation=CommunityMemberStatusEnum.ACTIVE,
    )

    assert member.model_dump() == {
        'user_id': user_id,
        'community_id': community_id,
        'role': CommunityMemberRoleEnum.ADMIN,
        'reputation': 10,
        'status_participation': CommunityMemberStatusEnum.ACTIVE,
    }

    member_with_defaults = CommunityMemberCreate(
        user_id=user_id,
        community_id=community_id,
    )

    assert member_with_defaults.model_dump() == {
        'user_id': user_id,
        'community_id': community_id,
        'role': 'member',
        'reputation': 0,
        'status_participation': 'active',
    }


@pytest.mark.unit
def test_community_member_update_schema():
    # Test with all fields
    member_update = CommunityMemberUpdate(
        role=CommunityMemberRoleEnum.MODERATOR,
        reputation=20,
        status_participation=CommunityMemberStatusEnum.SUSPENDED,
    )

    assert member_update.model_dump() == {
        'role': 'moderator',
        'reputation': 20,
        'status_participation': 'suspended',
    }

    # Test with partial updates
    partial_update = CommunityMemberUpdate(
        role=CommunityMemberRoleEnum.MODERATOR,
    )
    assert partial_update.model_dump() == {
        'role': 'moderator',
        'reputation': None,
        'status_participation': None,
    }


@pytest.mark.unit
def test_community_member_response_schema():
    id = uuid.uuid4()
    user_id = uuid.uuid4()
    community_id = uuid.uuid4()
    entered_in = datetime.now()
    created_at = datetime.now()
    updated_at = datetime.now()

    # Create user with all required fields including hashed_password
    user = UserResponse(
        id=user_id,
        email='test@example.com',
        name='Test User',
        hashed_password='securehashedpassword123456',  # This is the missing field
        profile_image_url='https://example.com/image.jpg',
        reputation_level=5,
        status=UserStatusEnum.ACTIVE,
        created_at=created_at,
        updated_at=updated_at,
    )

    community = CommunityRelated(id=community_id, name='Test Community')

    member_response = CommunityMemberResponse(
        id=id,
        user=user,
        community=community,
        role=CommunityMemberRoleEnum.ADMIN,
        status_participation=CommunityMemberStatusEnum.ACTIVE,
        reputation=10,
        entered_in=entered_in,
    )

    assert member_response.model_dump() == {
        'id': id,
        'user': user.model_dump(),
        'community': community.model_dump(),
        'role': 'admin',
        'status_participation': 'active',
        'reputation': 10,
        'entered_in': entered_in,
    }


@pytest.mark.unit
def test_community_create_invalid_schema():
    # Test invalid name (empty string)
    with pytest.raises(ValidationError):
        CommunityCreate(
            name='',
            description='Test Description',
            type_community=CommunityTypeEnum.UNIVERSITY,
        )

    # Test invalid name (too long)
    with pytest.raises(ValidationError):
        CommunityCreate(
            name='a' * 256,
            description='Test Description',
            type_community=CommunityTypeEnum.UNIVERSITY,
        )

    # Test invalid description (too long)
    with pytest.raises(ValidationError):
        CommunityCreate(
            name='Test Community',
            description='a' * 1001,
            type_community=CommunityTypeEnum.UNIVERSITY,
        )

    # Test invalid community type
    with pytest.raises(ValidationError):
        CommunityCreate(
            name='Test Community',
            description='Test Description',
            type_community='invalid_type',
        )


@pytest.mark.unit
def test_community_update_invalid_schema():
    # Test invalid name (empty string)
    with pytest.raises(ValidationError):
        CommunityUpdate(
            name='',
            description='Updated Description',
        )

    # Test invalid name (too long)
    with pytest.raises(ValidationError):
        CommunityUpdate(
            name='a' * 256,
            description='Updated Description',
        )

    # Test invalid description (too long)
    with pytest.raises(ValidationError):
        CommunityUpdate(
            name='Updated Community',
            description='a' * 1001,
        )

    # Test invalid community type
    with pytest.raises(ValidationError):
        CommunityUpdate(
            name='Updated Community',
            type_community='invalid_type',
        )


@pytest.mark.unit
def test_community_member_create_invalid_schema():
    # Test invalid role
    with pytest.raises(ValidationError):
        CommunityMemberCreate(
            user_id=uuid.uuid4(),
            community_id=uuid.uuid4(),
            role='invalid_role',
        )

    # Test invalid status
    with pytest.raises(ValidationError):
        CommunityMemberCreate(
            user_id=uuid.uuid4(),
            community_id=uuid.uuid4(),
            status_participation='invalid_status',
        )

    # Test missing required field
    with pytest.raises(ValidationError):
        CommunityMemberCreate(
            user_id=uuid.uuid4(),
            community_id='',
        )


@pytest.mark.unit
def test_community_member_update_invalid_schema():
    # Test invalid role
    with pytest.raises(ValidationError):
        CommunityMemberUpdate(
            role='invalid_role',
        )

    # Test invalid status
    with pytest.raises(ValidationError):
        CommunityMemberUpdate(
            status_participation='invalid_status',
        )
