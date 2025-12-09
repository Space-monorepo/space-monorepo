import uuid
from datetime import datetime

import pytest

from app.api.moderation.schema import ModerationActionResponse, PollBriefResponse
from app.api.post.schemas import (
    CommunityMemberRoleEnum,
    CommunityRelated,
    PollOptionResponse,
    PostAuthor,
    PostResponse,
)
from app.api.reports.schema import ReportTypeEnum, VoteTypeEnum


@pytest.mark.unit
def test_moderation_action_response_schema():
    action = VoteTypeEnum.SUSPEND
    report_type = ReportTypeEnum.POST_REPORT
    message = 'Post suspenso com sucesso'
    executed_at = datetime.now()

    response = ModerationActionResponse(
        action=action,
        report_type=report_type,
        message=message,
        executed_at=executed_at,
    )
    assert response.model_dump() == {
        'action': action,
        'report_type': report_type,
        'message': message,
        'executed_at': executed_at,
    }


@pytest.mark.unit
def test_poll_brief_response_schema():

    post_id = uuid.uuid4()
    community_id = uuid.uuid4()
    user_id = uuid.uuid4()
    poll_option_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    poll_brief_response = PollBriefResponse(
        post=PostResponse(
            id=post_id,
            community=CommunityRelated(
                id=community_id,
                name='Community 1',
            ),
            user=PostAuthor(
                id=user_id,
                name='User 1',
                profile_picture='https://example.com/image.jpg',
                role=CommunityMemberRoleEnum.ADMIN,
            ),
            type_post='poll',
            title='Title of the poll',
            content='Content of the poll',
            image_url='https://example.com/image.jpg',
            status='active',
            likes_count=10,
            comments_count=5,
            report_count=0,
            created_at=created_at,
            updated_at=updated_at,
            poll_question='What is your favorite color?',
            poll_options=[
                PollOptionResponse(
                    id=poll_option_id,
                    answer='Red',
                    votes_count=10,
                )
            ],
        ),
        question='What is your favorite color?',
        options=[
            PollOptionResponse(
                id=poll_option_id,
                answer='Red',
                votes_count=10,
            ),
        ],
        total_votes=18,
    )
    assert poll_brief_response.model_dump() == {
        'post': {
            'id': post_id,
            'community': {
                'id': community_id,
                'name': 'Community 1',
            },
            'user': {
                'id': user_id,
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
            'created_at': created_at,
            'updated_at': updated_at,
        },
        'question': 'What is your favorite color?',
        'options': [
            {
                'id': poll_option_id,
                'answer': 'Red',
                'votes_count': 10,
            }
        ],
        'total_votes': 18,
    }
