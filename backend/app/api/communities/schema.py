import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.api.reputation.schema import ReputationLevelEnum
from app.api.users.schema import UserResponse


class CommunityRelated(BaseModel):
    id: uuid.UUID
    name: str = Field(
        ..., min_length=1, max_length=255, description='Name of the community'
    )
    image_url: HttpUrl | None = Field(None, description='The image URL of the community')


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
    name: str = Field(
        ..., min_length=1, max_length=255, description='The name of the community'
    )
    description: str | None = Field(
        None, max_length=1000, description='The description of the community'
    )
    type_community: CommunityTypeEnum = Field(
        ..., description='The type of the community'
    )
    image_url: HttpUrl | None = Field(None, description='The image URL of the community')


class CommunityUpdate(BaseModel):
    name: str | None = Field(
        None, min_length=1, max_length=255, description='The name of the community'
    )
    description: str | None = Field(
        None, max_length=1000, description='The description of the community'
    )
    type_community: CommunityTypeEnum | None = Field(
        None, description='The type of the community'
    )
    image_url: HttpUrl | None = Field(None, description='The image URL of the community')


class CommunityResponse(CommunityCreate):
    id: uuid.UUID = Field(..., description='The community ID')
    created_at: datetime = Field(
        ..., description='The date and time the community was created'
    )
    updated_at: datetime = Field(
        ..., description='The date and time the community was last updated'
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'name': 'PUC Campinas',
                'description': 'A community for PUC Campinas',
                'type_community': 'university',
                'image_url': 'https://example.com/images/puc-campinas.jpg',
                'created_at': '2025-01-01T00:00:00Z',
                'updated_at': '2025-01-01T00:00:00Z',
            }
        },
    )


class CommunityMemberCreate(BaseModel):
    user_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the user'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )
    role: CommunityMemberRoleEnum = Field(
        default=CommunityMemberRoleEnum.MEMBER,
        description='The role of the member in the community',
    )
    status_participation: CommunityMemberStatusEnum = Field(
        default=CommunityMemberStatusEnum.ACTIVE,
        description='The status of the member in the community',
    )


class CommunityMemberUpdate(BaseModel):
    role: CommunityMemberRoleEnum | None = Field(
        None, description='The role of the member in the community'
    )
    status_participation: CommunityMemberStatusEnum | None = Field(
        None, description='The status of the member in the community'
    )


class CommunityMemberResponse(BaseModel):
    id: uuid.UUID
    user: UserResponse
    community: CommunityRelated
    role: CommunityMemberRoleEnum
    status_participation: CommunityMemberStatusEnum
    reputation: int
    reputation_level: ReputationLevelEnum
    popularity: int
    entered_in: datetime

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123e4567-e89b-12d3-a456-426614174002',
                    'user': {
                        'id': '123e4567-e89b-12d3-a456-426614174002',
                        'username': 'johndoe',
                        'email': 'member@example.com',
                        'name': 'Member Name',
                        'profile_image_url': 'https://example.com/image.jpg',
                        'bio': 'I am a software engineer',
                        'status': 'active',
                        'created_at': '2025-01-01T00:00:00Z',
                        'updated_at': '2025-01-01T00:00:00Z',
                    },
                    'community': {
                        'id': '123e4567-e89b-12d3-a456-426614174001',
                        'name': 'PUC Campinas',
                    },
                    'role': 'admin',
                    'status_participation': 'active',
                    'reputation': 5000,
                    'reputation_level': 'helper',
                    'popularity': 0,
                    'entered_in': '2025-01-01T00:00:00Z',
                }
            ]
        },
    )
