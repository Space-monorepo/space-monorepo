import pytest
from fastapi import status

from app.api.post.model import CampaignPost
from app.api.post.schemas import (
    CampaignStatusEnum,
    ComplaintLevelEnum,
    ComplaintStatusEnum,
    PollCreate,
    PostCreate,
    PostStatusEnum,
    PostTypeEnum,
    PostUpdate,
)

# TODO: Fazer o teste de reportar o post
# TODO: Fazer o teste para verificar se quando atualiza o status do post
# o usuario é moderador ou admin e quando o conteúdo é o dono do post


@pytest.mark.integration
def test_create_announcement_route(authenticate_client, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=str(community_member_on_db.user_id),
        community_id=str(community_member_on_db.community_id),
        type_post=PostTypeEnum.ANNOUNCEMENT,
        image_url=None,
    )

    response = authenticate_client.post(
        f'/posts/{community_member_on_db.community_id}/create-announcement',
        json=post.model_dump(mode='json'),
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert response_data['title'] == post.title
    assert response_data['content'] == post.content
    assert response_data['user']['id'] == str(post.user_id)
    assert response_data['user']['role'] == community_member_on_db.role
    assert response_data['community']['id'] == str(post.community_id)
    assert response_data['type_post'] == post.type_post
    assert response_data['image_url'] == post.image_url


@pytest.mark.integration
def test_get_post_route(authenticate_client, post_on_db):
    response = authenticate_client.get(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['id'] == str(post_on_db.id)
    assert response_data['title'] == post_on_db.title
    assert response_data['content'] == post_on_db.content
    assert response_data['user']['id'] == str(post_on_db.user_id)
    assert response_data['user']['role'] == post_on_db.user_role_in_community
    assert response_data['community']['id'] == str(post_on_db.community_id)
    assert response_data['type_post'] == post_on_db.type_post
    assert response_data['image_url'] == post_on_db.image_url


@pytest.mark.integration
def test_list_posts_by_user_route(authenticate_client, posts_on_db):
    response = authenticate_client.get(
        f'/posts/{posts_on_db[0].community_id}/user/{posts_on_db[0].user_id}/list-posts'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['items'][0]['id'] == str(posts_on_db[0].id)
    assert response_data['items'][1]['id'] == str(posts_on_db[1].id)
    assert response_data['items'][2]['id'] == str(posts_on_db[2].id)
    assert response_data['total'] == len(posts_on_db)


@pytest.mark.integration
def test_list_posts_by_community_route(authenticate_client, posts_on_db):
    response = authenticate_client.get(
        f'/posts/{posts_on_db[0].community_id}/community/list-posts'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['items'][0]['id'] == str(posts_on_db[0].id)
    assert response_data['items'][1]['id'] == str(posts_on_db[1].id)
    assert response_data['items'][2]['id'] == str(posts_on_db[2].id)
    assert response_data['total'] == len(posts_on_db)


@pytest.mark.integration
def test_update_post_route(authenticate_client, post_on_db, community_member_on_db):
    post_update = PostUpdate(
        content='Updated content',
    )

    response = authenticate_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}',
        json=post_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['content'] == post_update.content


@pytest.mark.integration
def test_update_post_status_route(
    authenticate_client, post_on_db, community_member_on_db
):
    post_update = PostUpdate(
        status=PostStatusEnum.SUSPENDED,
    )

    response = authenticate_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}',
        json=post_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == post_update.status


@pytest.mark.integration
def test_update_post_status_from_not_admin_route(
    authenticate_member_client, post_on_db, commun_member_on_db
):
    post_update = PostUpdate(
        status=PostStatusEnum.SUSPENDED,
    )

    response = authenticate_member_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}',
        json=post_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
def test_update_post_from_not_owner_route(
    authenticate_member_client, post_on_db, commun_member_on_db
):
    post_update = PostUpdate(
        content='Updated content',
    )

    response = authenticate_member_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}',
        json=post_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
def test_delete_post_route(authenticate_client, post_on_db):
    response = authenticate_client.delete(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authenticate_client.get(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_like_post_route(authenticate_client, post_on_db):
    response = authenticate_client.post(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}/like'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['likes_count'] == 1


@pytest.mark.integration
def test_unlike_post_route(authenticate_client, post_on_db):
    response = authenticate_client.post(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}/like'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['likes_count'] == 1

    response = authenticate_client.post(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}/unlike'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['likes_count'] == 0


@pytest.mark.integration
def test_create_campaign_route(authenticate_client, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=str(community_member_on_db.user_id),
        community_id=str(community_member_on_db.community_id),
        type_post=PostTypeEnum.CAMPAIGN,
        image_url=None,
    )
    response = authenticate_client.post(
        f'/posts/{community_member_on_db.community_id}/post/campaign',
        json=post.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['post']['title'] == post.title
    assert response.json()['post']['content'] == post.content
    assert response.json()['post']['user']['id'] == str(post.user_id)
    assert response.json()['post']['user']['role'] == community_member_on_db.role
    assert response.json()['post']['community']['id'] == str(post.community_id)
    assert response.json()['post']['type_post'] == post.type_post
    assert response.json()['post']['image_url'] == post.image_url
    assert response.json()['post']['status'] == PostStatusEnum.ACTIVE
    assert response.json()['target_participants'] == 100
    assert response.json()['current_participants'] == 0
    assert response.json()['status_campaign'] == CampaignStatusEnum.PENDING


@pytest.mark.integration
def test_participate_campaign_route(
    session_sql, authenticate_client, community_member_on_db, campaign_post_on_db
):
    response = authenticate_client.post(
        f'/posts/{community_member_on_db.community_id}/post/{campaign_post_on_db.post_id}/campaign/participate'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['campaign_id'] == str(campaign_post_on_db.post_id)
    assert response.json()['user_id'] == str(community_member_on_db.user_id)

    post = (
        session_sql.query(CampaignPost)
        .filter(CampaignPost.post_id == campaign_post_on_db.post_id)
        .first()
    )
    assert post.current_participants == 1


@pytest.mark.integration
def test_create_complaint_route(authenticate_client, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=str(community_member_on_db.user_id),
        community_id=str(community_member_on_db.community_id),
        type_post=PostTypeEnum.COMPLAINT,
        image_url=None,
    )
    response = authenticate_client.post(
        f'/posts/{community_member_on_db.community_id}/post/complaint',
        json=post.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['post']['title'] == post.title
    assert response.json()['post']['content'] == post.content
    assert response.json()['post']['user']['id'] == str(post.user_id)
    assert response.json()['post']['user']['role'] == community_member_on_db.role
    assert response.json()['post']['community']['id'] == str(post.community_id)
    assert response.json()['post']['type_post'] == post.type_post
    assert response.json()['post']['image_url'] == post.image_url
    assert response.json()['post']['status'] == PostStatusEnum.ACTIVE
    assert response.json()['level_complaint'] == ComplaintLevelEnum.LOW
    assert response.json()['status_complaint'] == ComplaintStatusEnum.PENDING


@pytest.mark.integration
def test_create_poll_route(authenticate_client, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=str(community_member_on_db.user_id),
        community_id=str(community_member_on_db.community_id),
        type_post=PostTypeEnum.POLL,
        image_url=None,
    )

    poll = PollCreate(
        post=post,
        question='Question test',
        options=['Option 1', 'Option 2', 'Option 3'],
    )
    response = authenticate_client.post(
        f'/posts/{community_member_on_db.community_id}/post/poll',
        json=poll.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['post']['title'] == post.title
    assert response.json()['question'] == poll.question
    assert response.json()['options'][0]['answer'] == poll.options[0]
    assert response.json()['options'][1]['answer'] == poll.options[1]
    assert response.json()['options'][2]['answer'] == poll.options[2]


@pytest.mark.integration
def test_vote_poll_route(authenticate_client, community_member_on_db, poll_option_on_db):
    poll_option = poll_option_on_db[0]
    response = authenticate_client.patch(
        f'/posts/{community_member_on_db.community_id}/post/poll-options/{poll_option.id}/vote',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['options'][0]['votes_count'] == 1


@pytest.mark.integration
def test_get_user_feed_route(authenticate_client, community_member_on_db, post_on_db):
    response = authenticate_client.get('/posts/feed')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['items'][0]['id'] == str(post_on_db.id)


@pytest.mark.integration
def test_list_user_campaigns_route(
    authenticate_client,
    community_member_on_db,
    campaign_post_on_db,
    campaign_participants_on_db,
):
    response = authenticate_client.get('/posts/post/list-user-campaigns')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['items'][0]['post']['id'] == str(campaign_post_on_db.post_id)
    assert (
        response.json()['items'][0]['target_participants']
        == campaign_post_on_db.target_participants
    )
    assert (
        response.json()['items'][0]['current_participants']
        == campaign_post_on_db.current_participants
    )
    assert (
        response.json()['items'][0]['status_campaign']
        == campaign_post_on_db.status_campaign
    )


@pytest.mark.integration
def test_report_post_route(authenticate_client, post_on_db):
    """
    Tests the report_post route.

    Scenario:
    - Given a valid post ID
    - When the route reports the post
    - Then it should increment report_count and return updated post
    """
    initial_report_count = post_on_db.report_count or 0
    
    response = authenticate_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}/report'
    )
    
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['id'] == str(post_on_db.id)
    assert response_data['report_count'] == initial_report_count + 1
    assert response_data['status'] == post_on_db.status or PostStatusEnum.ACTIVE


@pytest.mark.integration
def test_report_post_suspended_route(session_sql, authenticate_client, post_on_db):
    """
    Tests the report_post route when post is already suspended.

    Scenario:
    - Given a post with suspended status
    - When the route tries to report the post
    - Then it should return 409 Conflict
    """
    # Atualizar post para status SUSPENDED
    from app.api.post.model import Post
    post = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    post.status = PostStatusEnum.SUSPENDED
    session_sql.commit()
    
    response = authenticate_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}/report'
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.integration
def test_report_post_threshold_route(session_sql, authenticate_client, post_on_db):
    """
    Tests the report_post route when reaching report threshold.

    Scenario:
    - Given a post with report_count at threshold - 1
    - When the route reports the post
    - Then it should change status to REPORTED
    """
    # Atualizar post para ter report_count próximo ao threshold
    from app.api.post.model import Post
    post = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    post.report_count = 29  # Um abaixo do threshold de 30
    post.status = PostStatusEnum.ACTIVE
    session_sql.commit()
    
    response = authenticate_client.patch(
        f'/posts/{post_on_db.community_id}/post/{post_on_db.id}/report'
    )
    
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['report_count'] == 30
    assert response_data['status'] == PostStatusEnum.REPORTED


@pytest.mark.integration
def test_confirm_complaint_route(authenticate_client, complaint_post_on_db, post_on_db):
    """
    Tests the confirm_complaint route.

    Scenario:
    - Given a valid complaint post ID
    - When the route confirms the complaint
    - Then it should increment confirmations_count and return updated complaint
    """
    initial_confirmations = complaint_post_on_db.confirmations_count or 0
    initial_level = complaint_post_on_db.level_complaint or ComplaintLevelEnum.LOW
    
    response = authenticate_client.post(
        f'/posts/{post_on_db.community_id}/complaint/{complaint_post_on_db.post_id}/confirm'
    )
    
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['post']['id'] == str(complaint_post_on_db.post_id)
    assert response_data['confirmations_count'] == initial_confirmations + 1
    assert response_data['status_complaint'] == complaint_post_on_db.status_complaint
    
    # Verificar se o level foi atualizado corretamente
    new_confirmations = initial_confirmations + 1
    if new_confirmations >= 50:
        assert response_data['level_complaint'] == ComplaintLevelEnum.HIGH
    elif new_confirmations >= 30:
        assert response_data['level_complaint'] == ComplaintLevelEnum.MEDIUM
    else:
        assert response_data['level_complaint'] == ComplaintLevelEnum.LOW
