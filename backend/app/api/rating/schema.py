import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description='Rating score from 1 to 5')
    title: str = Field(
        ..., min_length=1, max_length=255, description='Title of the rating'
    )
    description: str | None = Field(
        None, max_length=1000, description='Detailed description of the rating'
    )


class RatingCreate(RatingBase):
    user_id: str = Field(
        ..., min_length=36, max_length=36, description='ID of the user giving the rating'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='ID of the community being rated'
    )


class RatingUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5, description='Rating score from 1 to 5')
    title: str | None = Field(
        None, min_length=1, max_length=255, description='Title of the rating'
    )
    description: str | None = Field(
        None, max_length=1000, description='Detailed description of the rating'
    )


class RatingResponse(RatingBase):
    id: uuid.UUID
    user_id: uuid.UUID
    community_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'user_id': 'a1b2c3d4-e5f6-7890-1234-567890abcdef',
                'community_id': 'b1c2d3e4-f5g6-7890-1234-567890ghijkl',
                'rating': 5,
                'title': 'Excellent Community!',
                'description': 'Loved the experience and the members.',
                'created_at': '2024-01-01T10:00:00Z',
                'updated_at': '2024-01-01T11:00:00Z',
            }
        },
    )
