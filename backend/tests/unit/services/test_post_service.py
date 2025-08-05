from app.api.post.model import Post, CampaignPost, ComplaintPost, PollPosts, PollOptions
from app.api.post.schemas import (
    PostCreate,
    PostTypeEnum,
    PostUpdate,
    CampaignStatusEnum,
    ComplaintStatusEnum,
    ComplaintLevelEnum,
    PollCreate,
)
from app.api.post.service import PostService
from app.utils.schema import PaginationSearchParams


def test_create_post_service(session_sql, transaction_manager, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        type_post=PostTypeEnum.CAMPAIGN,
        image_url=None,
    )

    post = PostService(transaction_manager).create_post(post)
    assert post.id is not None
    assert post.title == 'Title test'
    assert post.user.id == community_member_on_db.user_id
    assert post.community.id == community_member_on_db.community_id

    post_db = session_sql.query(Post).filter(Post.id == post.id).first()
    assert post_db is not None
    assert post_db.title == 'Title test'
    assert post_db.user_role_in_community == community_member_on_db.role


def test_get_post_by_id_service(transaction_manager, post_on_db):
    post = PostService(transaction_manager).get_post(post_on_db.id)
    assert post is not None
    assert post.id == post_on_db.id
    assert post.title == post_on_db.title
    assert post.user.role == post_on_db.user_role_in_community


def test_get_posts_by_user_service(transaction_manager, post_on_db, user_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    posts = PostService(transaction_manager).list_posts_by_user(user_on_db.id, params)
    assert posts is not None
    assert posts.items is not None
    assert len(posts.items) > 0
    assert posts.items[0].user.id == user_on_db.id


def test_get_posts_by_community_service(
    transaction_manager, post_on_db, community_on_db
):
    params = PaginationSearchParams(offset=0, limit=10)
    posts = PostService(transaction_manager).list_posts_by_community(
        community_on_db.id, params
    )
    assert posts is not None
    assert posts.items is not None
    assert len(posts.items) > 0
    assert posts.items[0].community.id == community_on_db.id


def test_get_user_feed_service(transaction_manager, posts_on_db, user_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    posts = PostService(transaction_manager).get_user_feed(user_on_db.id, params)
    assert posts is not None
    assert posts.items is not None
    assert len(posts.items) > 0
    assert posts.items[0].user.id == user_on_db.id
    assert posts.items[0].community.id == posts_on_db[0].community.id
    assert posts.items[0].type_post == PostTypeEnum.CAMPAIGN
    assert posts.items[1].type_post == PostTypeEnum.COMPLAINT
    assert posts.items[2].type_post == PostTypeEnum.ANNOUNCEMENT


def test_update_post_service(session_sql, transaction_manager, post_on_db):
    post_update = PostUpdate(content='Content updated')
    post = PostService(transaction_manager).update_post(post_on_db.id, post_update)
    assert post is not None
    assert post.content == 'Content updated'

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    assert post_db is not None
    assert post_db.content == 'Content updated'


def test_delete_post_service(session_sql, transaction_manager, post_on_db):
    result = PostService(transaction_manager).delete_post(post_on_db.id)
    assert result is True

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    assert post_db is None


def test_like_post_service(session_sql, transaction_manager, post_on_db, community_member_on_db):
    post = PostService(transaction_manager).like_post(post_on_db.id, community_member_on_db.user_id)
    assert post is not None
    assert post.likes_count == 1

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    assert post_db is not None
    assert post_db.likes_count == 1


def test_unlike_post_service(session_sql, transaction_manager, post_on_db, community_member_on_db):
    post = PostService(transaction_manager).like_post(post_on_db.id, community_member_on_db.user_id)
    assert post is not None
    assert post.likes_count == 1

    post = PostService(transaction_manager).unlike_post(post_on_db.id, community_member_on_db.user_id)
    assert post is not None
    assert post.likes_count == 0

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    assert post_db is not None
    assert post_db.likes_count == 0


def test_list_likes_post_service(session_sql, transaction_manager, post_on_db, community_member_on_db):
    post = PostService(transaction_manager).like_post(post_on_db.id, community_member_on_db.user_id)
    assert post is not None
    assert post.likes_count == 1

    members = PostService(transaction_manager).list_likes_post(post_on_db.id)
    assert members is not None
    assert len(members) == 1

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    assert post_db is not None
    assert post_db.likes_count == 1


def test_create_campaign_service(session_sql, transaction_manager, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        type_post=PostTypeEnum.CAMPAIGN,
        image_url=None,
    )
    post = PostService(transaction_manager).create_campaign(post)
    assert post is not None
    assert post.post.id is not None
    assert post.target_participants == 100
    assert post.current_participants == 0
    assert post.status_campaign == CampaignStatusEnum.PENDING
    
    campaign_db = session_sql.query(CampaignPost).filter(CampaignPost.post_id == post.post.id).first()
    assert campaign_db is not None
    assert campaign_db.target_participants == 100
    assert campaign_db.current_participants == 0
    assert campaign_db.status_campaign == CampaignStatusEnum.PENDING


def test_participate_campaign_service(session_sql, transaction_manager, campaign_post_on_db, user_on_db):
    campaign_participants = PostService(transaction_manager).participate_campaign(
        campaign_post_on_db.post_id, user_on_db.id
    )
    assert campaign_participants is not None
    assert campaign_participants.campaign_id == campaign_post_on_db.post_id
    assert campaign_participants.user_id == user_on_db.id
    
    campaign_db = session_sql.query(CampaignPost).filter(CampaignPost.post_id == campaign_post_on_db.post_id).first()
    assert campaign_db is not None
    assert campaign_db.current_participants == 1
    assert campaign_db.status_campaign == CampaignStatusEnum.PENDING


def test_list_user_campaigns_subscriptions_service(session_sql, transaction_manager, campaign_post_on_db, campaign_participants_on_db):
    campaigns = PostService(transaction_manager).list_user_campaigns_subscriptions(
        campaign_participants_on_db.user_id, PaginationSearchParams(offset=0, limit=10)
    )
    assert campaigns is not None
    assert campaigns.items is not None
    assert len(campaigns.items) == 1
    assert campaigns.items[0].post.id == campaign_post_on_db.post_id
    assert campaigns.items[0].target_participants == campaign_post_on_db.target_participants
    assert campaigns.items[0].current_participants == campaign_post_on_db.current_participants
    assert campaigns.items[0].status_campaign == campaign_post_on_db.status_campaign
    assert campaigns.total == 1
    assert campaigns.has_more == False


def test_create_complaint_service(session_sql, transaction_manager, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        type_post=PostTypeEnum.COMPLAINT,
        image_url=None,
    )
    post = PostService(transaction_manager).create_complaint(post)
    assert post is not None
    assert post.post.id is not None
    
    complaint_db = session_sql.query(ComplaintPost).filter(ComplaintPost.post_id == post.post.id).first()
    assert complaint_db is not None
    assert complaint_db.post_id == post.post.id
    assert complaint_db.status_complaint == ComplaintStatusEnum.PENDING
    assert complaint_db.level_complaint == ComplaintLevelEnum.LOW
    assert complaint_db.confirmations_count == 0


def test_create_poll_service(session_sql, transaction_manager, community_member_on_db):
    post = PostCreate(
        title='Title test',
        content='Content test',
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        type_post=PostTypeEnum.POLL,
        image_url=None,
    )
    poll = PollCreate(
        post=post,
        question='Question test',
        options=['Option 1', 'Option 2', 'Option 3'],
    )
    post = PostService(transaction_manager).create_poll(poll)
    assert post is not None
    assert post.post.id is not None

    poll_db = session_sql.query(PollPosts).filter(PollPosts.post_id == post.post.id).first()
    assert poll_db is not None
    assert poll_db.post_id == post.post.id
    assert poll_db.question == 'Question test'
    
    poll_options_db = session_sql.query(PollOptions).filter(PollOptions.post_id == post.post.id).all()
    assert poll_options_db is not None
    assert len(poll_options_db) == 3
    assert poll_options_db[0].answer == 'Option 1'
    assert poll_options_db[1].answer == 'Option 2'
    assert poll_options_db[2].answer == 'Option 3'


def test_get_poll_service(session_sql, transaction_manager, poll_post_on_db, poll_option_on_db):
    poll = PostService(transaction_manager).get_poll(poll_post_on_db.post_id)
    assert poll is not None
    assert poll.post_id == poll_post_on_db.post_id
    assert poll.question == poll_post_on_db.question
    assert poll.options == poll_option_on_db

    poll_db = session_sql.query(PollPosts).filter(PollPosts.post_id == poll_post_on_db.post_id).first()
    assert poll_db is not None
    assert poll_db.post_id == poll_post_on_db.post_id
    assert poll_db.question == poll_post_on_db.question
    assert poll_db.options == poll_option_on_db


def test_vote_poll_service(session_sql, transaction_manager, poll_post_on_db, poll_option_on_db):
    poll = PostService(transaction_manager).vote_poll(poll_option_on_db[0].id)
    assert poll is not None
    assert poll.post.id == poll_post_on_db.post_id
    assert poll.question == poll_post_on_db.question
    assert len(poll.options) == 3
    assert poll.options[0].answer == 'Test Option 0'
    assert poll.options[0].votes_count == 1
    assert poll.options[1].answer == 'Test Option 1'
    assert poll.options[1].votes_count == 0
    assert poll.options[2].answer == 'Test Option 2'
    assert poll.options[2].votes_count == 0

    poll_db = session_sql.query(PollOptions).filter(PollOptions.id == poll_option_on_db[0].id).first()
    assert poll_db is not None
    assert poll_db.votes_count == 1