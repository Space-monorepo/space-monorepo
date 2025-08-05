import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserStatusEnum(str, Enum):
    pending = 'pending'
    active = 'active'
    suspended = 'suspended'
    banned = 'banned'
    inactive = 'inactive'


class UserCreate(BaseModel):
    email: EmailStr = Field(
        ..., min_length=1, max_length=255, description='The email address of the user'
    )
    name: str = Field(
        ..., min_length=1, max_length=255, description='The name of the user'
    )
    hashed_password: str = Field(
        ..., min_length=15, max_length=255, description='The hashed password of the user'
    )
    profile_image_url: str | None = Field(
        None, max_length=255, description='The profile image URL'
    )
    reputation_level: int = Field(0, description='The reputation level of user.')
    status: UserStatusEnum = Field(
        UserStatusEnum.pending, description='Whether the user is active or not.'
    )


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(
        None, min_length=1, max_length=255, description='The email address of the user'
    )
    name: str | None = Field(
        None, min_length=1, max_length=255, description='The name of the user'
    )
    hashed_password: str | None = Field(
        None,
        min_length=15,
        max_length=255,
        description='The hashed password of the user',
    )
    profile_image_url: str | None = Field(
        None, max_length=255, description='The profile image URL'
    )
    reputation_level: int | None = Field(
        None, description='The reputation level of user.'
    )
    status: UserStatusEnum | None = Field(
        None, description='Whether the user is active or not.'
    )


class UserResponse(UserCreate):
    id: uuid.UUID = Field(..., description='The user ID')
    email: EmailStr = Field(
        ..., min_length=1, max_length=255, description='The email address of the user'
    )
    name: str = Field(
        ..., min_length=1, max_length=255, description='The name of the user'
    )
    profile_image_url: str | None = Field(
        None, max_length=255, description='The profile image URL'
    )
    reputation_level: int = Field(0, description='The reputation level of user.')
    status: UserStatusEnum = Field(
        UserStatusEnum.pending, description='Whether the user is active or not.'
    )
    created_at: datetime = Field(
        ..., description='The date and time the user was created.'
    )
    updated_at: datetime = Field(
        ..., description='The date and time the user was last updated.'
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'email': 'johndoe@example.com',
                'name': 'John Doe',
                'profile_image_url': 'https://example.com/profile.jpg',
                'reputation_level': 10,
                'status': 'active',
                'created_at': '2021-01-01T00:00:00Z',
                'updated_at': '2021-01-01T00:00:00Z',
            }
        },
    )


class LoginSchema(BaseModel):
    email: EmailStr = Field(
        ..., min_length=1, max_length=255, description='The email address of the user'
    )
    password: str = Field(
        ..., min_length=15, max_length=255, description='The hashed password of the user'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'email': 'johndoe@example.com',
                'hashed_password': 'hashed_password',
            }
        },
    )
