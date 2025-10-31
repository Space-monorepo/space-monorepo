from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.post.schemas import PollResponse
from app.api.reports.schema import ReportTypeEnum, VoteTypeEnum


class ModerationActionResponse(BaseModel):
    action: VoteTypeEnum = Field(
        ..., description='The action taken (suspend or tolerate)'
    )
    report_type: ReportTypeEnum = Field(..., description='The type of content moderated')
    message: str = Field(..., description='Human-readable message describing the action')
    executed_at: datetime = Field(
        ..., description='The date and time the action was executed'
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'examples': [
                {
                    'action': 'suspend',
                    'report_type': 'post_report',
                    'message': 'Post suspenso com sucesso',
                    'executed_at': '2021-01-01T00:00:00Z',
                }
            ]
        },
    )


class PollBriefResponse(PollResponse):
    total_votes: int = Field(..., description='The total votes for the poll')

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
                        'title': 'Title of the poll',
                        'content': 'Content of the poll',
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
                    'total_votes': 18,
                }
            ]
        },
    )
