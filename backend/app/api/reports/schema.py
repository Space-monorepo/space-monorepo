from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.api.communities.schema import CommunityMemberRoleEnum


class ReportTypeEnum(str, Enum):
    MEMBER_REPORT = 'member_report'
    POST_REPORT = 'post_report'
    COMMENT_REPORT = 'comment_report'


class VoteTypeEnum(str, Enum):
    SUSPEND = 'suspend'
    TOLERATE = 'tolerate'


class ReportReasonEnum(str, Enum):
    DISCRIMINATION = 'discrimination'
    HARASSMENT = 'harassment'
    HATE_SPEECH = 'hate_speech'
    INAPPROPRIATE_CONTENT = 'inappropriate_content'
    MISINFORMATION = 'misinformation'
    SENSITIVE_CONTENT = 'sensitive_content'
    SPAM = 'spam'
    THREAT = 'threat'
    OTHER = 'other'


class Author(BaseModel):
    id: str
    name: str = Field(..., min_length=1, max_length=255, description='Name of the user')
    profile_picture: str | None = None
    role: CommunityMemberRoleEnum = Field(
        ..., description='Role of the user in the community'
    )

    model_config = ConfigDict(from_attributes=True)


class ReportCreate(BaseModel):
    reporter_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the reporter'
    )
    type: ReportTypeEnum = Field(..., description='The type of the report')
    reason: ReportReasonEnum = Field(..., description='The reason of the report')
    description: str = Field(..., description='The description of the report')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'reporter_id': '123',
                    'community_id': '123',
                    'type': ReportTypeEnum.MEMBER_REPORT,
                    'reason': ReportReasonEnum.DISCRIMINATION,
                    'description': 'The description of the report',
                }
            ]
        },
    )


class ReportResponse(BaseModel):
    id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the report'
    )
    reporter: Author = Field(..., description='The reporter of the report')
    type: ReportTypeEnum = Field(..., description='The type of the report')
    reason: ReportReasonEnum = Field(..., description='The reason of the report')
    description: str = Field(..., description='The description of the report')
    created_at: datetime = Field(
        ..., description='The date and time the report was created'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123',
                    'reporter': {
                        'id': '123',
                        'name': 'John Doe',
                        'profile_picture': 'https://example.com/image.jpg',
                        'role': 'admin',
                    },
                    'type': ReportTypeEnum.MEMBER_REPORT,
                    'reason': ReportReasonEnum.DISCRIMINATION,
                    'description': 'The description of the report',
                    'created_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class ReportMemberCreate(BaseModel):
    report_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the reporter'
    )
    member_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the member'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report_id': '123',
                    'member_id': '456',
                    'community_id': '789',
                }
            ]
        },
    )


class ReportMemberResponse(BaseModel):
    report: ReportResponse = Field(..., description='The report of the member')
    member_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the member'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report': {
                        'id': '123',
                        'reporter': {
                            'id': '123',
                            'name': 'John Doe',
                            'profile_picture': 'https://example.com/image.jpg',
                            'role': 'admin',
                        },
                        'type': ReportTypeEnum.MEMBER_REPORT,
                        'reason': ReportReasonEnum.DISCRIMINATION,
                        'description': 'The description of the report',
                        'created_at': '2021-01-01T00:00:00Z',
                    },
                    'member_id': '456',
                    'community_id': '789',
                }
            ]
        },
    )


class MemberBriefReport(BaseModel):
    member: Author = Field(..., description='The member of the report')
    reason: ReportReasonEnum = Field(..., description='The reason of the report')
    reports_count: int = Field(..., description='The quantity of the reports')
    member_reputation: int = Field(..., description='The reputation of the member')
    member_reputation_level: str = Field(
        ..., description='The reputation level of the member'
    )
    member_popularity: float = Field(
        ..., ge=0.0, description='The popularity of the member'
    )
    member_entry_date: datetime = Field(
        ..., description='The date and time the member entered the community'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'member': {
                        'id': '123',
                        'name': 'John Doe',
                        'profile_picture': 'https://example.com/image.jpg',
                        'role': 'admin',
                    },
                    'reason': ReportReasonEnum.DISCRIMINATION,
                    'reports_count': 10,
                    'member_reputation': 100,
                    'member_reputation_level': 'helper',
                    'member_popularity': 0.5,
                    'member_entry_date': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class ReportPostCreate(BaseModel):
    report_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the reporter'
    )
    post_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the post'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report_id': '123',
                    'post_id': '456',
                    'community_id': '789',
                }
            ]
        },
    )


class ReportPostResponse(BaseModel):
    report: ReportResponse = Field(..., description='The report of the post')
    post_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the post'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report': {
                        'id': '123',
                        'reporter': {
                            'id': '123',
                            'name': 'John Doe',
                            'profile_picture': 'https://example.com/image.jpg',
                            'role': 'admin',
                        },
                        'type': ReportTypeEnum.POST_REPORT,
                        'reason': ReportReasonEnum.DISCRIMINATION,
                        'description': 'The description of the report',
                        'created_at': '2021-01-01T00:00:00Z',
                    },
                    'post_id': '456',
                    'community_id': '789',
                }
            ]
        },
    )


class PostBriefReport(BaseModel):
    post_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the post'
    )
    member: Author = Field(..., description='The member of the report')
    reason: ReportReasonEnum = Field(..., description='The reason of the report')
    title: str = Field(
        ..., min_length=1, max_length=255, description='The title of the post'
    )
    content: str = Field(
        ..., min_length=1, max_length=2000, description='The content of the post'
    )
    image_url: str | None = Field(None, description='The image URL of the post')
    report_count: int = Field(..., ge=0, description='The count of the reports')
    likes_count: int = Field(..., ge=0, description='The count of the likes')
    comments_count: int = Field(..., ge=0, description='The count of the comments')
    access_count: int = Field(..., ge=0, description='The count of the accesses')
    published_at: datetime = Field(
        ..., description='The date and time the post was published'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'post_id': '123',
                    'member': {
                        'id': '123',
                        'name': 'John Doe',
                        'profile_picture': 'https://example.com/image.jpg',
                        'role': 'admin',
                    },
                    'reason': ReportReasonEnum.DISCRIMINATION,
                    'title': 'Title of the post',
                    'content': 'Content of the post',
                    'image_url': 'https://example.com/image.jpg',
                    'report_count': 10,
                    'likes_count': 10,
                    'comments_count': 10,
                    'access_count': 10,
                    'published_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class ReportCommentCreate(BaseModel):
    report_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the reporter'
    )
    comment_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the comment'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report_id': '123',
                    'comment_id': '456',
                    'community_id': '789',
                }
            ]
        },
    )


class ReportCommentResponse(BaseModel):
    report: ReportResponse = Field(..., description='The report of the comment')
    comment_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the comment'
    )
    community_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the community'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report': {
                        'id': '123',
                        'reporter': {
                            'id': '123',
                            'name': 'John Doe',
                            'profile_picture': 'https://example.com/image.jpg',
                            'role': 'admin',
                        },
                        'type': ReportTypeEnum.COMMENT_REPORT,
                        'reason': ReportReasonEnum.DISCRIMINATION,
                        'description': 'The description of the report',
                        'created_at': '2021-01-01T00:00:00Z',
                    },
                    'comment_id': '456',
                    'community_id': '789',
                }
            ]
        },
    )


class CommentBriefReport(BaseModel):
    comment_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the comment'
    )
    member: Author = Field(..., description='The member of the report')
    reason: ReportReasonEnum = Field(..., description='The reasons of the report')
    content: str = Field(
        ..., min_length=1, max_length=2000, description='The content of the comment'
    )
    report_count: int = Field(..., ge=0, description='The count of the reports')
    likes_count: int = Field(..., ge=0, description='The count of the likes')
    # TODO: Add comments count after
    access_count: int = Field(..., ge=0, description='The count of the accesses')
    published_at: datetime = Field(
        ..., description='The date and time the comment was published'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'comment_id': '123',
                    'member': {
                        'id': '123',
                        'name': 'John Doe',
                        'profile_picture': 'https://example.com/image.jpg',
                        'role': 'admin',
                    },
                    'reason': ReportReasonEnum.DISCRIMINATION,
                    'content': 'Content of the comment',
                    'report_count': 10,
                    'likes_count': 10,
                    'access_count': 10,
                    'published_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class ModerationVotesCreate(BaseModel):
    report_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the report'
    )
    moderator_id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the moderator'
    )
    vote: VoteTypeEnum = Field(..., description='The vote of the moderation')

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'report_id': '123',
                    'moderator_id': '456',
                    'vote': 'suspend',
                }
            ]
        },
    )


class ModerationVotesResponse(ModerationVotesCreate):
    id: str = Field(
        ..., min_length=36, max_length=36, description='The ID of the moderation vote'
    )
    created_at: datetime = Field(
        ..., description='The date and time the moderation vote was created'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'id': '123',
                    'report_id': '123',
                    'moderator_id': '456',
                    'vote': 'suspend',
                    'created_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )
