import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.post.schemas import (
    CampaignParticipantsResponse,
    CampaignResponse,
    CampaignStatusEnum,
    CampaignUpdate,
    CommunityMemberRoleEnum,
    CommunityRelated,
    ComplaintLevelEnum,
    ComplaintResponse,
    ComplaintStatusEnum,
    ComplaintUpdate,
    PollCreate,
    PollOptionResponse,
    PollResponse,
    PollVoteResponse,
    PostAuthor,
    PostCreate,
    PostFeedbackCreate,
    PostFeedbackResponse,
    PostFeedResponse,
    PostResponse,
    PostStatusEnum,
    PostTypeEnum,
    PostUpdate,
)


@pytest.mark.unit
def test_post_create_schema():
    user_id = str(uuid.uuid4())
    community_id = str(uuid.uuid4())

    post = PostCreate(
        community_id=community_id,
        user_id=user_id,
        type_post=PostTypeEnum.CAMPAIGN,
        title='Test Post',
        content='Test Content',
        image_url='https://example.com/image.jpg',
        status=PostStatusEnum.ACTIVE,
    )

    assert post.model_dump() == {
        'title': 'Test Post',
        'content': 'Test Content',
        'user_id': user_id,
        'community_id': community_id,
        'type_post': 'campaign',
        'image_url': 'https://example.com/image.jpg',
        'status': 'active',
    }


@pytest.mark.unit
def test_post_update_schema():
    post = PostUpdate(
        content='Updated Content',
        status=PostStatusEnum.SUSPENDED,
    )

    assert post.model_dump() == {
        'content': 'Updated Content',
        'status': 'suspended',
    }


@pytest.mark.unit
def test_post_response_schema():
    post_id = uuid.uuid4()
    community_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    post = PostResponse(
        id=post_id,
        community=CommunityRelated(
            id=community_id,
            name='Test Community',
        ),
        user=PostAuthor(
            id=user_id,
            name='Test User',
            role='member',
            profile_picture='https://example.com/profile.jpg',
        ),
        type_post=PostTypeEnum.CAMPAIGN,
        title='Test Post',
        content='Test Content',
        image_url='https://example.com/image.jpg',
        status=PostStatusEnum.ACTIVE,
        likes_count=0,
        comments_count=0,
        report_count=0,
        created_at=created_at,
        updated_at=updated_at,
    )

    assert post.model_dump() == {
        'id': post_id,
        'community': {
            'id': community_id,
            'name': 'Test Community',
        },
        'user': {
            'id': user_id,
            'name': 'Test User',
            'role': 'member',
            'profile_picture': 'https://example.com/profile.jpg',
        },
        'type_post': 'campaign',
        'title': 'Test Post',
        'content': 'Test Content',
        'image_url': 'https://example.com/image.jpg',
        'status': 'active',
        'likes_count': 0,
        'comments_count': 0,
        'report_count': 0,
        'created_at': created_at,
        'updated_at': updated_at,
        'poll_question': None,
        'poll_options': None,
    }


@pytest.mark.unit
def test_post_response_with_poll_schema():
    """
    Tests PostResponse schema with poll fields populated.
    
    Scenario:
    - Given a poll post with question and options
    - When creating a PostResponse instance
    - Then it should include poll_question and poll_options
    """
    post_id = uuid.uuid4()
    community_id = uuid.uuid4()
    user_id = uuid.uuid4()
    option_id_1 = uuid.uuid4()
    option_id_2 = uuid.uuid4()
    option_id_3 = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    poll_options = [
        PollOptionResponse(
            id=option_id_1,
            answer='Red',
            votes_count=5,
        ),
        PollOptionResponse(
            id=option_id_2,
            answer='Blue',
            votes_count=3,
        ),
        PollOptionResponse(
            id=option_id_3,
            answer='Green',
            votes_count=2,
        ),
    ]

    post = PostResponse(
        id=post_id,
        community=CommunityRelated(
            id=community_id,
            name='Test Community',
        ),
        user=PostAuthor(
            id=user_id,
            name='Test User',
            role='member',
            profile_picture='https://example.com/profile.jpg',
        ),
        type_post=PostTypeEnum.POLL,
        title='Test Poll',
        content='Test Poll Content',
        image_url=None,
        status=PostStatusEnum.ACTIVE,
        likes_count=10,
        comments_count=5,
        report_count=0,
        created_at=created_at,
        updated_at=updated_at,
        poll_question='What is your favorite color?',
        poll_options=poll_options,
    )

    post_dict = post.model_dump()
    
    assert post_dict['id'] == post_id
    assert post_dict['type_post'] == 'poll'
    assert post_dict['poll_question'] == 'What is your favorite color?'
    assert post_dict['poll_options'] is not None
    assert len(post_dict['poll_options']) == 3
    assert post_dict['poll_options'][0]['answer'] == 'Red'
    assert post_dict['poll_options'][0]['votes_count'] == 5
    assert post_dict['poll_options'][1]['answer'] == 'Blue'
    assert post_dict['poll_options'][1]['votes_count'] == 3
    assert post_dict['poll_options'][2]['answer'] == 'Green'
    assert post_dict['poll_options'][2]['votes_count'] == 2


@pytest.mark.unit
def test_post_create_invalid_schema():
    with pytest.raises(ValidationError):
        PostCreate(
            community_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            type_post=PostTypeEnum.CAMPAIGN,
            title='',
            content='',
            image_url='',
            status=PostStatusEnum.ACTIVE,
        )


@pytest.mark.unit
def test_post_update_invalid_schema():
    with pytest.raises(ValidationError):
        PostUpdate(
            content='',
            status=PostStatusEnum.ACTIVE,
        )


@pytest.mark.unit
def test_post_author_invalid_schema():
    with pytest.raises(ValidationError):
        PostAuthor(id=uuid.uuid4(), name='', role='admin', profile_picture=None)

    with pytest.raises(ValidationError):
        PostAuthor(id=uuid.uuid4(), name='John Doe', role='', profile_picture=None)


@pytest.mark.unit
def test_post_community_related_invalid_schema():
    with pytest.raises(ValidationError):
        CommunityRelated(id=uuid.uuid4(), name='')


@pytest.mark.unit
def test_post_response_invalid_schema():
    with pytest.raises(ValidationError):
        PostResponse(
            id=uuid.uuid4(),
            community=CommunityRelated(id=uuid.uuid4(), name=''),
            user=PostAuthor(id=uuid.uuid4(), name='', role='', profile_picture=''),
            type_post=PostTypeEnum.CAMPAIGN,
            title='Example title',
            content='Example content',
            image_url=None,
            status=PostStatusEnum.ACTIVE,
            likes_count=0,
            comments_count=0,
            report_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )


@pytest.mark.unit
def test_campaign_update_schema():
    campaign_update = CampaignUpdate(
        target_participants=200,
        status_campaign='approved',
    )

    assert campaign_update.model_dump() == {
        'target_participants': 200,
        'status_campaign': 'approved',
    }


@pytest.mark.unit
def test_campaign_response_schema():
    post_id = uuid.uuid4()
    community_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    community = CommunityRelated(id=community_id, name='Test Community')

    user = PostAuthor(
        id=user_id,
        name='Test User',
        role='member',
        profile_picture='https://example.com/profile.jpg',
    )

    post = PostResponse(
        id=post_id,
        community=community,
        user=user,
        type_post=PostTypeEnum.CAMPAIGN,
        title='Example title',
        content='Example content',
        image_url=None,
        status=PostStatusEnum.ACTIVE,
        likes_count=0,
        comments_count=0,
        report_count=0,
        created_at=created_at,
        updated_at=updated_at,
    )

    campaign_response = CampaignResponse(
        post=post,
        target_participants=200,
        current_participants=150,
        status_campaign=CampaignStatusEnum.APPROVED,
    )
    assert campaign_response.model_dump() == {
        'post': {
            'id': post_id,
            'community': {
                'id': community_id,
                'name': 'Test Community',
            },
            'user': {
                'id': user_id,
                'name': 'Test User',
                'role': CommunityMemberRoleEnum.MEMBER,
                'profile_picture': 'https://example.com/profile.jpg',
            },
            'type_post': PostTypeEnum.CAMPAIGN,
            'title': 'Example title',
            'content': 'Example content',
            'image_url': None,
            'status': PostStatusEnum.ACTIVE,
            'likes_count': 0,
            'comments_count': 0,
            'report_count': 0,
            'created_at': created_at,
            'updated_at': updated_at,
            'poll_question': None,
            'poll_options': None,
        },
        'target_participants': 200,
        'current_participants': 150,
        'status_campaign': CampaignStatusEnum.APPROVED,
    }


@pytest.mark.unit
def test_campaign_participants_response_schema():
    campaign_id = uuid.uuid4()
    user_id = uuid.uuid4()
    member_id = uuid.uuid4()
    created_at = datetime.now()

    campaign_participants_response = CampaignParticipantsResponse(
        campaign_id=campaign_id,
        user_id=user_id,
        member_id=member_id,
        joined_at=created_at,
    )
    assert campaign_participants_response.model_dump() == {
        'campaign_id': campaign_id,
        'user_id': user_id,
        'member_id': member_id,
        'joined_at': created_at,
    }


@pytest.mark.unit
def test_post_feedback_create_schema():
    post_id = str(uuid.uuid4())
    member_id = str(uuid.uuid4())
    post_feedback_create = PostFeedbackCreate(
        post_id=post_id,
        member_id=member_id,
        subject='Example subject',
        message='Example message',
    )
    assert post_feedback_create.model_dump() == {
        'post_id': post_id,
        'member_id': member_id,
        'subject': 'Example subject',
        'message': 'Example message',
    }


@pytest.mark.unit
def test_post_feedback_response_schema():
    id = uuid.uuid4()
    post_id = uuid.uuid4()
    member_id = uuid.uuid4()
    created_at = datetime.now()

    post_feedback_response = PostFeedbackResponse(
        id=id,
        post_id=post_id,
        member_id=member_id,
        subject='Example subject',
        message='Example message',
        created_at=created_at,
    )

    assert post_feedback_response.model_dump() == {
        'id': id,
        'post_id': post_id,
        'member_id': member_id,
        'subject': 'Example subject',
        'message': 'Example message',
        'created_at': created_at,
    }


@pytest.mark.unit
def test_complaint_update_schema():
    complaint_update = ComplaintUpdate(
        confirmations_count=1,
        status_complaint=ComplaintStatusEnum.PENDING,
    )
    assert complaint_update.model_dump() == {
        'confirmations_count': 1,
        'status_complaint': ComplaintStatusEnum.PENDING,
    }


@pytest.mark.unit
def test_complaint_response_schema():
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_at = datetime.now()

    community = CommunityRelated(
        id=uuid.uuid4(),
        name='Test Community',
    )

    user = PostAuthor(
        id=user_id,
        name='Test User',
        role='member',
        profile_picture='https://example.com/profile.jpg',
    )

    post = PostResponse(
        id=post_id,
        community=community,
        user=user,
        type_post=PostTypeEnum.CAMPAIGN,
        title='Example title',
        content='Example content',
        image_url=None,
        status=PostStatusEnum.ACTIVE,
        likes_count=0,
        comments_count=0,
        report_count=0,
        created_at=created_at,
        updated_at=created_at,
    )

    complaint_response = ComplaintResponse(
        post=post,
        confirmations_count=1,
        status_complaint=ComplaintStatusEnum.PENDING,
        level_complaint=ComplaintLevelEnum.LOW,
    )
    assert complaint_response.model_dump() == {
        'post': {
            'id': post_id,
            'community': {
                'id': community.id,
                'name': 'Test Community',
            },
            'user': {
                'id': user_id,
                'name': 'Test User',
                'role': 'member',
                'profile_picture': 'https://example.com/profile.jpg',
            },
            'type_post': PostTypeEnum.CAMPAIGN,
            'title': 'Example title',
            'content': 'Example content',
            'image_url': None,
            'status': PostStatusEnum.ACTIVE,
            'likes_count': 0,
            'comments_count': 0,
            'report_count': 0,
            'created_at': created_at,
            'updated_at': created_at,
            'poll_question': None,
            'poll_options': None,
        },
        'confirmations_count': 1,
        'status_complaint': ComplaintStatusEnum.PENDING,
        'level_complaint': ComplaintLevelEnum.LOW,
    }


@pytest.mark.unit
def test_poll_create_schema():
    community_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    poll_create = PollCreate(
        post=PostCreate(
            community_id=community_id,
            user_id=user_id,
            type_post=PostTypeEnum.POLL,
            title='Example title',
            content='Example content',
            image_url=None,
            status=PostStatusEnum.ACTIVE,
        ),
        question='Example question',
        options=['Option 1', 'Option 2', 'Option 3'],
    )
    assert poll_create.model_dump() == {
        'post': {
            'community_id': community_id,
            'user_id': user_id,
            'type_post': PostTypeEnum.POLL,
            'title': 'Example title',
            'content': 'Example content',
            'image_url': None,
            'status': PostStatusEnum.ACTIVE,
        },
        'question': 'Example question',
        'options': ['Option 1', 'Option 2', 'Option 3'],
    }


@pytest.mark.unit
def test_poll_response_schema():
    post_id = uuid.uuid4()
    option_id_1 = uuid.uuid4()
    option_id_2 = uuid.uuid4()
    option_id_3 = uuid.uuid4()
    community_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_at = datetime.now()

    community = CommunityRelated(
        id=community_id,
        name='Test Community',
    )

    user = PostAuthor(
        id=user_id,
        name='Test User',
        role='member',
        profile_picture='https://example.com/profile.jpg',
    )

    poll_response = PollResponse(
        post=PostResponse(
            id=post_id,
            community=community,
            user=user,
            type_post=PostTypeEnum.POLL,
            title='Example title',
            content='Example content',
            image_url=None,
            status=PostStatusEnum.ACTIVE,
            likes_count=0,
            comments_count=0,
            report_count=0,
            created_at=created_at,
            updated_at=created_at,
        ),
        question='Example question',
        options=[
            PollOptionResponse(
                id=option_id_1,
                answer='Option 1',
                votes_count=0,
            ),
            PollOptionResponse(
                id=option_id_2,
                answer='Option 2',
                votes_count=0,
            ),
            PollOptionResponse(
                id=option_id_3,
                answer='Option 3',
                votes_count=0,
            ),
        ],
    )
    assert poll_response.model_dump() == {
        'post': {
            'id': post_id,
            'community': {
                'id': community_id,
                'name': 'Test Community',
            },
            'user': {
                'id': user_id,
                'name': 'Test User',
                'role': 'member',
                'profile_picture': 'https://example.com/profile.jpg',
            },
            'type_post': PostTypeEnum.POLL,
            'title': 'Example title',
            'content': 'Example content',
            'image_url': None,
            'status': PostStatusEnum.ACTIVE,
            'likes_count': 0,
            'comments_count': 0,
            'report_count': 0,
            'created_at': created_at,
            'updated_at': created_at,
            'poll_question': None,
            'poll_options': None,
        },
        'question': 'Example question',
        'options': [
            {
                'id': option_id_1,
                'answer': 'Option 1',
                'votes_count': 0,
            },
            {
                'id': option_id_2,
                'answer': 'Option 2',
                'votes_count': 0,
            },
            {
                'id': option_id_3,
                'answer': 'Option 3',
                'votes_count': 0,
            },
        ],
    }


@pytest.mark.unit
def test_poll_vote_response_schema():
    id = uuid.uuid4()
    poll_option_id = uuid.uuid4()
    member_id = uuid.uuid4()
    created_at = datetime.now()

    poll_vote_response = PollVoteResponse(
        id=id,
        poll_option_id=poll_option_id,
        member_id=member_id,
        created_at=created_at,
    )
    assert poll_vote_response.model_dump() == {
        'id': id,
        'poll_option_id': poll_option_id,
        'member_id': member_id,
        'created_at': created_at,
    }
