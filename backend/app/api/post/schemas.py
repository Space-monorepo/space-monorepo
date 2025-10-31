import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.api.communities.schema import CommunityMemberRoleEnum


class CommunityRelated(BaseModel):
    id: uuid.UUID
    name: str = Field(
        ..., min_length=1, max_length=255, description='Name of the community'
    )
    image_url: HttpUrl | None = Field(None, description='The image URL of the community')


class PostAuthor(BaseModel):
    id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255, description='Name of the user')
    profile_picture: str | None = None
    role: CommunityMemberRoleEnum = Field(
        ..., description='Role of the user in the community'
    )

    model_config = ConfigDict(from_attributes=True)


class CampaignStatusEnum(str, Enum):
    PENDING = 'pending'
    UNDER_ANALYSIS = 'under_analysis'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    IN_PROGRESS = 'in_progress'
    CANCELED = 'canceled'
    FINISHED = 'finished'


class PostStatusEnum(str, Enum):
    ACTIVE = 'active'
    REPORTED = 'reported'  # TODO: Verificar se o REPORTED realmente é necessário
    SUSPENDED = 'suspended'
    REJECTED = 'rejected'


class PostTypeEnum(str, Enum):
    CAMPAIGN = 'campaign'
    COMPLAINT = 'complaint'
    POLL = 'poll'
    ANNOUNCEMENT = 'announcement'
    # Ideas: event, news, job, share, other


class ComplaintStatusEnum(str, Enum):
    PENDING = 'pending'
    UNDER_INVESTIGATION = 'under_investigation'
    RESOLVED = 'resolved'


class ComplaintLevelEnum(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class PostCreate(BaseModel):
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='Community id of the post'
    )
    user_id: str = Field(
        ..., min_length=36, max_length=36, description='User id of the post'
    )
    type_post: PostTypeEnum = Field(
        ..., description='Type of post, required for certain types.'
    )
    title: str = Field(
        ..., min_length=1, max_length=255, description='Title of the post'
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description='Content of the post, required for certain types.',
    )
    image_url: str | None = Field(
        None,
        max_length=255,
        description='URL of the post image, required for campaigns.',
    )
    status: PostStatusEnum = Field(
        PostStatusEnum.ACTIVE, description='Status of the post'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'community_id': '123',
                    'user_id': '456',
                    'type_post': 'campaign',
                    'title': 'Title of the post',
                    'content': 'Content of the post',
                    'image_url': 'https://example.com/image.jpg',
                    'status': 'active',
                }
            ]
        },
    )


class PostUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=255)
    status: PostStatusEnum | None = Field(None, description='Status of the post')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [{'content': 'Conteúdo do post', 'status': 'active'}]
        },
    )


class PostResponse(BaseModel):
    id: uuid.UUID
    community: CommunityRelated
    user: PostAuthor
    type_post: PostTypeEnum
    title: str
    content: str
    image_url: str | None
    status: PostStatusEnum
    likes_count: int
    comments_count: int
    report_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123',
                    'community_id': {
                        'id': '123',
                        'name': 'Community 1',
                    },
                    'user': {
                        'id': '456',
                        'name': 'User 1',
                        'profile_picture': 'https://example.com/image.jpg',
                        'role': 'admin',
                    },
                    'type_post': 'campaign',
                    'title': 'Title of the post',
                    'content': 'Content of the post',
                    'image_url': 'https://example.com/image.jpg',
                    'likes_count': 10,
                    'comments_count': 5,
                    'report_count': 0,
                    'created_at': '2021-01-01T00:00:00Z',
                    'updated_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class CampaignUpdate(BaseModel):
    target_participants: int | None = Field(
        None, description='Target participants for the campaign'
    )
    status_campaign: CampaignStatusEnum | None = Field(
        None, description='Status of the campaign'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'target_participants': 200,
                    'status_campaign': 'approved',
                }
            ]
        },
    )


class CampaignResponse(BaseModel):
    post: PostResponse = Field(..., description='Post of the campaign')
    target_participants: int = Field(
        None, description='Target participants for the campaign'
    )
    current_participants: int = Field(
        ..., description='Current participants for the campaign'
    )
    status_campaign: CampaignStatusEnum = Field(
        ..., description='Status of the campaign'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post': {
                        'id': '123',
                        'community_id': {
                            'id': '123',
                            'name': 'Community 1',
                        },
                        'user': {
                            'id': '456',
                            'name': 'User 1',
                            'profile_picture': 'https://example.com/image.jpg',
                            'role': 'admin',
                        },
                        'type_post': 'campaign',
                        'title': 'Title of the post',
                        'content': 'Content of the post',
                        'image_url': 'https://example.com/image.jpg',
                        'status': 'active',
                        'likes_count': 10,
                        'comments_count': 5,
                        'report_count': 0,
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z',
                    },
                    'target_participants': 100,
                    'current_participants': 5,
                    'status_campaign': 'pending',
                }
            ]
        },
    )


class CampaignParticipantsResponse(BaseModel):
    campaign_id: uuid.UUID = Field(..., description='Campaign id of the participant')
    user_id: uuid.UUID = Field(..., description='User id of the participant')
    member_id: uuid.UUID = Field(..., description='Member id of the participant')
    joined_at: datetime = Field(..., description='Joined at of the participant')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'campaign_id': '123',
                    'user_id': '456',
                    'member_id': '789',
                    'joined_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class PostFeedbackCreate(BaseModel):
    post_id: str = Field(
        ..., min_length=36, max_length=36, description='Post id of the feedback'
    )
    member_id: str = Field(
        ...,
        min_length=36,
        max_length=36,
        description='Community member id of the feedback',
    )
    subject: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=255)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post_id': '123',
                    'member_id': '456',
                    'subject': 'Subject of the feedback',
                    'message': 'Message of the feedback',
                }
            ]
        },
    )


class PostFeedbackResponse(PostFeedbackCreate):
    id: uuid.UUID = Field(..., description='Id of the feedback')
    post_id: uuid.UUID = Field(..., description='Id of the post')
    member_id: uuid.UUID = Field(..., description='Id of the member')
    created_at: datetime = Field(..., description='Created at of the feedback')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123',
                    'post_id': '123',
                    'member_id': '456',
                    'subject': 'Subject of the feedback',
                    'message': 'Message of the feedback',
                    'created_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class ComplaintUpdate(BaseModel):
    confirmations_count: int | None = Field(
        None, description='Confirmations count of the complaint'
    )
    status_complaint: ComplaintStatusEnum | None = Field(
        None, description='Status of the complaint'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'confirmations_count': 1,
                    'status_complaint': 'pending',
                }
            ]
        },
    )


class ComplaintResponse(BaseModel):
    post: PostResponse = Field(..., description='Post of the complaint')
    confirmations_count: int = Field(
        ..., description='Confirmations count of the complaint'
    )
    status_complaint: ComplaintStatusEnum = Field(
        ..., description='Status of the complaint'
    )
    level_complaint: ComplaintLevelEnum = Field(
        ..., description='Level of the complaint'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post': {
                        'id': '123',
                        'community_id': {
                            'id': '123',
                            'name': 'Community 1',
                        },
                        'user': {
                            'id': '456',
                            'name': 'User 1',
                            'profile_picture': 'https://example.com/image.jpg',
                            'role': 'admin',
                        },
                        'type_post': 'campaign',
                        'title': 'Title of the post',
                        'content': 'Content of the post',
                        'image_url': 'https://example.com/image.jpg',
                        'status': 'active',
                        'likes_count': 10,
                        'comments_count': 5,
                        'report_count': 0,
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z',
                    },
                    'confirmations_count': 1,
                    'status_complaint': 'pending',
                    'level_complaint': 'low',
                }
            ]
        },
    )


class PollCreate(BaseModel):
    post: PostCreate = Field(...)
    question: str = Field(
        ..., min_length=1, max_length=255, description='Question of the poll'
    )
    options: list[str] = Field(
        ..., min_length=1, max_length=255, description='options of the poll'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post': {
                        'community_id': '123',
                        'user_id': '456',
                        'type_post': 'poll',
                        'title': 'Title of the poll',
                        'content': 'Content of the poll',
                        'image_url': 'https://example.com/image.jpg',
                    },
                    'question': 'What is your favorite color?',
                    'options': ['Red', 'Green', 'Blue'],
                }
            ]
        },
    )


class PollOptionResponse(BaseModel):
    id: uuid.UUID = Field(..., description='Id of the poll answer')
    answer: str = Field(
        ..., min_length=1, max_length=255, description='Answer of the poll'
    )
    votes_count: int = Field(..., description='Votes count of the poll answer')


class PollResponse(BaseModel):
    post: PostResponse = Field(..., description='Post of the poll')
    question: str = Field(
        ..., min_length=1, max_length=255, description='Question of the poll'
    )
    options: list[PollOptionResponse] = Field(..., description='options of the poll')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post': {
                        'id': '123',
                        'community_id': {
                            'id': '123',
                            'name': 'Community 1',
                        },
                        'user': {
                            'id': '456',
                            'name': 'User 1',
                            'profile_picture': 'https://example.com/image.jpg',
                            'role': 'admin',
                        },
                        'type_post': 'poll',
                        'title': 'Title of the post',
                        'content': 'Content of the post',
                        'image_url': 'https://example.com/image.jpg',
                        'status': 'active',
                        'likes_count': 10,
                        'comments_count': 5,
                        'report_count': 0,
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z',
                    },
                    'question': 'What is your favorite color?',
                    'options': [
                        {
                            'id': '1',
                            'answer': 'Red',
                            'votes_count': 10,
                        },
                        {
                            'id': '2',
                            'answer': 'Green',
                            'votes_count': 5,
                        },
                        {
                            'id': '3',
                            'answer': 'Blue',
                            'votes_count': 3,
                        },
                    ],
                }
            ]
        },
    )
