from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BadgeCreate(BaseModel):
    community_id: UUID = Field(
        ..., description='ID of the community this badge belongs to.'
    )
    name: str = Field(
        ..., min_length=1, max_length=100, description='Name of the badge.'
    )
    description: str | None = Field(
        None, max_length=500, description='Description of the badge.'
    )
    image_url: str | None = Field(
        None, max_length=255, description='URL for the badge image.'
    )

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'community_id': '123e4567-e89b-12d3-a456-426614174000',
                    'name': 'Badge 1',
                    'description': 'Description of badge 1',
                    'image_url': 'https://example.com/badge1.png',
                }
            ]
        }
    )


class BadgeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    image_url: str | None = Field(None, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'name': 'Badge 1',
                    'description': 'Description of badge 1',
                    'image_url': 'https://example.com/badge1.png',
                }
            ]
        }
    )


class BadgeResponse(BadgeCreate):
    id: UUID = Field(..., description='Unique ID of the badge.')
    created_at: datetime = Field(..., description='Timestamp of badge creation.')
    updated_at: datetime = Field(..., description='Timestamp of last badge update.')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123e4567-e89b-12d3-a456-426614174000',
                    'community_id': '123e4567-e89b-12d3-a456-426614174000',
                    'name': 'Badge 1',
                    'description': 'Description of badge 1',
                    'image_url': 'https://example.com/badge1.png',
                    'created_at': '2021-01-01T00:00:00Z',
                    'updated_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class MemberBadgeCreate(BaseModel):
    member_id: UUID = Field(..., description='ID of the member receiving the badge.')
    badge_id: UUID = Field(..., description='ID of the badge being assigned.')


class MemberBadgeResponse(MemberBadgeCreate):
    achieved_at: datetime = Field(
        ..., description='Timestamp when the member achieved the badge.'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'member_id': '123e4567-e89b-12d3-a456-426614174000',
                    'badge_id': '123e4567-e89b-12d3-a456-426614174000',
                    'achieved_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )
