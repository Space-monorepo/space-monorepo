import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.api.communities.schema import CommunityMemberRoleEnum


class CommentStatusEnum(str, Enum):
    ACTIVE = 'active'
    REPORTED = 'reported'
    SUSPENDED = 'suspended'


class CommentAuthor(BaseModel):
    id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255, description='Name of the user')
    profile_image_url: str | None = None
    member_role: CommunityMemberRoleEnum | None = Field(
        None,
        description='The role of the user in the community where the comment was made',
    )
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PostRelated(BaseModel):
    id: uuid.UUID
    title: str = Field(
        ..., min_length=1, max_length=255, description='Title of the post'
    )

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    post_id: uuid.UUID = Field(..., description='Post id of the comment')
    user_id: uuid.UUID = Field(..., description='User id of the comment')
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description='Content of the comment',
    )
    parent_id: uuid.UUID | None = Field(
        None, description='Parent comment id for replies'
    )
    status: CommentStatusEnum = Field(
        CommentStatusEnum.ACTIVE, description='Status of the comment'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post_id': '123e4567-e89b-12d3-a456-426614174000',
                    'user_id': '456e7890-e89b-12d3-a456-426614174000',
                    'content': 'Este é um comentário muito interessante!',
                    'parent_id': None,
                    'status': 'active',
                }
            ]
        },
    )


class CommentUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=1000)
    status: CommentStatusEnum | None = Field(None, description='Status of the comment')


class CommentResponse(BaseModel):
    id: uuid.UUID
    post: PostRelated
    user: CommentAuthor
    content: str
    status: CommentStatusEnum
    likes_count: int
    report_count: int
    parent_id: uuid.UUID | None
    created_at: datetime
    replies: list['CommentResponse'] = []

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123e4567-e89b-12d3-a456-426614174000',
                    'post': {
                        'id': '789e0123-e89b-12d3-a456-426614174000',
                        'title': 'Título do Post',
                    },
                    'user': {
                        'id': '456e7890-e89b-12d3-a456-426614174000',
                        'name': 'João Silva',
                        'profile_image_url': 'https://example.com/profile.jpg',
                        'member_role': 'member',
                    },
                    'content': 'Este é um comentário muito interessante!',
                    'status': 'active',
                    'likes_count': 5,
                    'report_count': 0,
                    'parent_id': None,
                    'created_at': '2021-01-01T00:00:00Z',
                    'replies': [],
                }
            ]
        },
    )


class CommentLikeResponse(BaseModel):
    comment_id: uuid.UUID = Field(..., description='Comment id that was liked')
    user_id: uuid.UUID = Field(..., description='User id who liked')
    created_at: datetime = Field(..., description='When the like was created')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'comment_id': '123e4567-e89b-12d3-a456-426614174000',
                    'user_id': '456e7890-e89b-12d3-a456-426614174000',
                    'created_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


# Para auto-referência das replies
CommentResponse.model_rebuild()
