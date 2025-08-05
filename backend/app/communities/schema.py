import uuid

from datetime import datetime

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from app.users.schema import UserResponse


class CommunityRelated(BaseModel):
    id: uuid.UUID
    name: str = Field(
        ..., min_length=1, max_length=255, description='Name of the community'
    )


class CommunityTypeEnum(str, Enum):
    UNIVERSITY = 'university'
    NEIGHBORHOOD = 'neighborhood'
    COMPANY = 'company'
    GOVERNMENT = 'government'
    HEALTHCARE = 'healthcare'
    RELIGIOUS = 'religious'
    COMMERCIAL = 'commercial'
    CLUB = 'club'


class CommunityMemberStatusEnum(str, Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    BANNED = 'banned'


class CommunityMemberRoleEnum(str, Enum):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    MEMBER = 'member'


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description='The name of the community')
    description: str | None = Field(None, max_length=1000, description='The description of the community')
    type_community: CommunityTypeEnum = Field(..., description='The type of the community')


class CommunityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255, description='The name of the community')
    description: str | None = Field(None, max_length=1000, description='The description of the community')
    type_community: CommunityTypeEnum | None = Field(None, description='The type of the community')


class CommunityResponse(CommunityCreate):
    id: uuid.UUID = Field(..., description='The community ID')
    created_at: datetime = Field(..., description='The date and time the community was created')
    updated_at: datetime = Field(..., description='The date and time the community was last updated')

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'name': 'PUC Campinas',
                'description': 'A community for PUC Campinas',
                'type_community': 'university',
                'created_at': '2025-01-01T00:00:00Z',
                'updated_at': '2025-01-01T00:00:00Z'
            }
        }
    )


class CommunityMemberCreate(BaseModel):
    user_id: uuid.UUID = Field(..., description='The ID of the user')
    community_id: uuid.UUID = Field(..., description='The ID of the community')
    role: CommunityMemberRoleEnum = Field(default=CommunityMemberRoleEnum.MEMBER, description='The role of the member in the community')
    reputation: int = Field(default=0, description='The reputation of the member in the community')
    status_participation: CommunityMemberStatusEnum = Field(default=CommunityMemberStatusEnum.ACTIVE, description='The status of the member in the community')


class CommunityMemberUpdate(BaseModel):
    role: CommunityMemberRoleEnum | None = Field(None, description='The role of the member in the community')
    reputation: int | None = Field(None, description='The reputation of the member in the community')
    status_participation: CommunityMemberStatusEnum | None = Field(None, description='The status of the member in the community')


class CommunityMemberResponse(BaseModel):
    user_id: uuid.UUID
    community_id: uuid.UUID
    user: UserResponse
    community: CommunityRelated
    role: CommunityMemberRoleEnum
    status_participation: CommunityMemberStatusEnum
    reputation: int
    entered_in: datetime

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
                    'examples': [
                        {
                            'user_id': '123e4567-e89b-12d3-a456-426614174002',
                            'community_id': '123e4567-e89b-12d3-a456-426614174001',
                            'user': {
                                'id': '123e4567-e89b-12d3-a456-426614174002',
                                'email': 'member@example.com',
                                'name': 'Member Name',
                                'profile_image_url': 'https://example.com/image.jpg',
                                'reputation_level': 10,
                                'status': 'active',
                                'created_at': '2025-01-01T00:00:00Z',
                                'updated_at': '2025-01-01T00:00:00Z'
                            },
                            'community': {
                                'id': '123e4567-e89b-12d3-a456-426614174001',
                                'name': 'PUC Campinas'
                            },
                            'role': 'admin',
                            'status_participation': 'active',
                            'reputation': 100,
                            'entered_in': '2025-01-01T00:00:00Z'
                        }
                    ]
                }
    )
