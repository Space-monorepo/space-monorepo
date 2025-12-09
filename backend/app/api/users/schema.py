import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserStatusEnum(str, Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    BANNED = 'banned'
    INACTIVE = 'inactive'


class ConnectionStatusEnum(str, Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    BLOCKED = 'blocked'


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=1, max_length=50, description='The username of the user'
    )
    email: EmailStr = Field(
        ..., min_length=1, max_length=255, description='The email address of the user'
    )
    name: str = Field(
        ..., min_length=1, max_length=255, description='The name of the user'
    )
    hashed_password: str = Field(
        ..., min_length=15, max_length=255, description='The hashed password of the user'
    )
    bio: str | None = Field(
        None, min_length=0, max_length=255, description='The bio of the user'
    )
    profile_image_url: str | None = Field(
        None, max_length=255, description='The profile image URL'
    )
    status: UserStatusEnum = Field(
        UserStatusEnum.PENDING, description='Whether the user is active or not.'
    )


class UserUpdate(BaseModel):
    username: str | None = Field(
        None, min_length=1, max_length=50, description='The username of the user'
    )
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
    bio: str | None = Field(
        None, min_length=0, max_length=255, description='The bio of the user'
    )
    status: UserStatusEnum | None = Field(
        None, description='Whether the user is active or not.'
    )


class UserResponse(UserCreate):
    id: uuid.UUID = Field(..., description='The user ID')
    username: str = Field(
        ..., min_length=1, max_length=50, description='The username of the user'
    )
    email: EmailStr = Field(
        ..., min_length=1, max_length=255, description='The email address of the user'
    )
    name: str = Field(
        ..., min_length=1, max_length=255, description='The name of the user'
    )
    bio: str | None = Field(
        None, min_length=0, max_length=255, description='The bio of the user'
    )
    profile_image_url: str | None = Field(
        None, max_length=255, description='The profile image URL'
    )
    status: UserStatusEnum = Field(
        UserStatusEnum.PENDING, description='Whether the user is active or not.'
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
                'username': 'johndoe',
                'email': 'johndoe@example.com',
                'name': 'John Doe',
                'bio': 'I am a software engineer',
                'profile_image_url': 'https://example.com/profile.jpg',
                'status': 'active',
                'created_at': '2021-01-01T00:00:00Z',
                'updated_at': '2021-01-01T00:00:00Z',
            }
        },
    )


class UserConnectionCreate(BaseModel):
    addressee_id: uuid.UUID = Field(
        ..., description='The ID of the user who will receive the connection request'
    )


class UserConnectionUpdate(BaseModel):
    status: ConnectionStatusEnum = Field(
        ..., description='The new status of the connection'
    )


class UserConnectionResponse(BaseModel):
    id: uuid.UUID = Field(..., description='The connection ID')
    requester_id: uuid.UUID = Field(
        ..., description='The ID of the user who sent the connection request'
    )
    addressee_id: uuid.UUID = Field(
        ..., description='The ID of the user who received the connection request'
    )
    status: ConnectionStatusEnum = Field(
        ..., description='The current status of the connection'
    )
    created_at: datetime = Field(
        ..., description='The date and time the connection request was created'
    )
    updated_at: datetime = Field(
        ..., description='The date and time the connection was last updated'
    )
    rejected_at: datetime | None = Field(
        None,
        description='The date and time the connection was rejected (for cooldown control)',
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'requester_id': '123e4567-e89b-12d3-a456-426614174001',
                'addressee_id': '123e4567-e89b-12d3-a456-426614174002',
                'status': 'pending',
                'created_at': '2021-01-01T00:00:00Z',
                'updated_at': '2021-01-01T00:00:00Z',
                'rejected_at': None,
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
