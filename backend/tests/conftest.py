import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.api.badges.model import Badge as BadgeModel
from app.api.badges.model import MemberBadge as MemberBadgeModel
from app.api.comment.model import Comment, CommentLikes
from app.api.comment.schema import CommentStatusEnum
from app.api.communities.model import Community, CommunityMember
from app.api.communities.schema import CommunityMemberRoleEnum, CommunityTypeEnum
from app.api.post.model import (
    CampaignParticipants,
    CampaignPost,
    ComplaintPost,
    PollOptions,
    PollPosts,
    Post,
    PostFeedback,
)
from app.api.post.repository import PostRepository
from app.api.post.schemas import (
    CampaignStatusEnum,
    PostTypeEnum,
)
from app.api.rating.model import Rating
from app.api.users.schema import UserCreate
from app.api.users.service import UserService
from app.core.config import settings
from app.core.database import Base, get_db, get_mongo_db
from app.core.transaction import TransactionManager
from app.main import app


@pytest.fixture(scope='session')
def setup_sql_db():
    if settings.ENVIRONMENT == 'test':
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={'check_same_thread': False, 'timeout': 20},
            poolclass=StaticPool,
            echo=False,
        )
    else:
        engine = create_engine(settings.DATABASE_URL)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session_sql(setup_sql_db):
    session: Session = setup_sql_db
    session.rollback()
    session.connection()
    if settings.ENVIRONMENT == 'test':
        for table in Base.metadata.sorted_tables:
            session.execute(text(f'DELETE FROM {table.name}'))
    else:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(
                text(f'TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE')
            )

    session.commit()
    try:
        yield session
    finally:
        session.rollback()
        session.expunge_all()


@pytest.fixture
def mongo_db():
    mongo_uri = settings.MONGO_URI
    test_db_name = settings.MONGO_INITDB_DATABASE + '_test'
    client = MongoClient(mongo_uri)
    db = client[test_db_name]
    yield db

    for collection in db.list_collection_names():
        db[collection].drop()


@pytest.fixture
def client_sql(session_sql):
    def get_db_override():
        return session_sql

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_db_override
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def client_mongo(mongo_db):
    def get_mongo_db_override():
        return mongo_db

    with TestClient(app) as client:
        app.dependency_overrides[get_mongo_db] = get_mongo_db_override
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def authenticate_client(session_sql, user_on_db):
    def get_db_override():
        return session_sql

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_db_override
        response = client.post(
            '/users/login',
            data={'username': user_on_db.email, 'password': 'hashed_password'},
        )
        token = response.json().get('access_token')
        client.headers.update({'Authorization': f'Bearer {token}'})
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def authenticate_member_client(session_sql, secondary_user_on_db):
    def get_db_override():
        return session_sql

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_db_override
        response = client.post(
            '/users/login',
            data={'username': secondary_user_on_db.email, 'password': 'hashed_password'},
        )
        token = response.json().get('access_token')
        client.headers.update({'Authorization': f'Bearer {token}'})
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def transaction_manager(session_sql):
    return TransactionManager(session_sql)


@pytest.fixture
def user_on_db(transaction_manager):
    user = UserCreate(
        email='johndoe@example.com',
        name='John Doe',
        hashed_password='hashed_password',
        profile_image_url=None,
        reputation_level=1,
        status='active',
    )

    user = UserService(transaction_manager).create_user(user)
    return user


@pytest.fixture
def secondary_user_on_db(transaction_manager):
    user = UserCreate(
        email='ana@example.com',
        name='Ana Doe',
        hashed_password='hashed_password',
        profile_image_url=None,
        reputation_level=1,
        status='active',
    )

    user = UserService(transaction_manager).create_user(user)
    return user


@pytest.fixture
def community_on_db(session_sql):
    community = Community(
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
    )

    session_sql.add(community)
    session_sql.flush()
    session_sql.refresh(community)
    return community


@pytest.fixture
def community_member_on_db(session_sql, community_on_db, user_on_db):
    community_member = CommunityMember(
        community_id=community_on_db.id,
        user_id=user_on_db.id,
        role=CommunityMemberRoleEnum.ADMIN,
    )

    session_sql.add(community_member)
    session_sql.flush()
    session_sql.refresh(community_member)
    return community_member


@pytest.fixture
def moderator_member_on_db(session_sql, community_on_db, user_on_db):
    moderator_member = CommunityMember(
        community_id=community_on_db.id,
        user_id=user_on_db.id,
        role=CommunityMemberRoleEnum.MODERATOR,
    )

    session_sql.add(moderator_member)
    session_sql.flush()
    session_sql.refresh(moderator_member)
    return moderator_member


@pytest.fixture
def commun_member_on_db(session_sql, community_on_db, secondary_user_on_db):
    community_member = CommunityMember(
        community_id=community_on_db.id,
        user_id=secondary_user_on_db.id,
        role=CommunityMemberRoleEnum.MEMBER,
    )

    session_sql.add(community_member)
    session_sql.flush()
    session_sql.refresh(community_member)
    return community_member


@pytest.fixture
def post_on_db(session_sql, community_on_db, user_on_db, community_member_on_db):
    post = Post(
        community_id=community_on_db.id,
        user_id=user_on_db.id,
        user_role_in_community=community_member_on_db.role,
        type_post=PostTypeEnum.CAMPAIGN,
        title='Test Post',
        content='Test Content',
        image_url=None,
    )

    session_sql.add(post)
    session_sql.flush()
    session_sql.refresh(post)
    return post


@pytest.fixture
def posts_on_db(session_sql, community_on_db, user_on_db, community_member_on_db):
    posts = [
        Post(
            community_id=community_on_db.id,
            user_id=user_on_db.id,
            user_role_in_community=community_member_on_db.role,
            type_post=PostTypeEnum.CAMPAIGN,
            title='Test Post Campaign',
            content='Test Content Campaign',
            image_url=None,
        ),
        Post(
            community_id=community_on_db.id,
            user_id=user_on_db.id,
            user_role_in_community=community_member_on_db.role,
            type_post=PostTypeEnum.COMPLAINT,
            title='Test Post Complaint',
            content='Test Content Complaint',
            image_url=None,
        ),
        Post(
            community_id=community_on_db.id,
            user_id=user_on_db.id,
            user_role_in_community=community_member_on_db.role,
            type_post=PostTypeEnum.ANNOUNCEMENT,
            title='Test Post Announcement',
            content='Test Content Announcement',
            image_url=None,
        ),
    ]

    session_sql.add_all(posts)
    session_sql.flush()
    for post in posts:
        session_sql.refresh(post)
    return posts


@pytest.fixture
def campaign_post_on_db(session_sql, post_on_db):
    campaign_post = CampaignPost(
        post_id=post_on_db.id,
        target_participants=100,
        current_participants=0,
        status_campaign=CampaignStatusEnum.PENDING,
    )

    session_sql.add(campaign_post)
    session_sql.flush()
    session_sql.refresh(campaign_post)
    return campaign_post


@pytest.fixture
def campaign_participants_on_db(
    session_sql, campaign_post_on_db, community_member_on_db
):
    campaign_participants = CampaignParticipants(
        campaign_id=campaign_post_on_db.post_id,
        user_id=community_member_on_db.user_id,
        member_id=community_member_on_db.id,
    )

    session_sql.add(campaign_participants)
    session_sql.flush()
    session_sql.refresh(campaign_participants)
    return campaign_participants


@pytest.fixture
def complaint_post_on_db(session_sql, post_on_db):
    complaint_post = ComplaintPost(
        post_id=post_on_db.id,
    )

    session_sql.add(complaint_post)
    session_sql.flush()
    session_sql.refresh(complaint_post)
    return complaint_post


@pytest.fixture
def poll_post_on_db(session_sql, post_on_db):
    poll_post = PollPosts(
        post_id=post_on_db.id,
        question='Test Poll',
    )

    session_sql.add(poll_post)
    session_sql.flush()
    session_sql.refresh(poll_post)
    return poll_post


@pytest.fixture
def poll_option_on_db(session_sql, poll_post_on_db):
    poll_options = [
        PollOptions(
            post_id=poll_post_on_db.post_id,
            answer=f'Test Option {i}',
        )
        for i in range(3)
    ]

    session_sql.add_all(poll_options)
    session_sql.flush()
    for poll_option in poll_options:
        session_sql.refresh(poll_option)
    return poll_options


@pytest.fixture
def post_feedback_on_db(session_sql, post_on_db, community_member_on_db):
    post_feedback = PostFeedback(
        post_id=post_on_db.id,
        member_id=community_member_on_db.id,
        subject='Feedback',
        message='Example message',
    )

    session_sql.add(post_feedback)
    session_sql.flush()
    session_sql.refresh(post_feedback)
    return post_feedback


@pytest.fixture
def mock_db_session():
    """Fixture para mockar a sessão do banco de dados (se necessário isoladamente)."""
    return MagicMock()


@pytest.fixture
def mock_post_repository(mock_db_session):
    """Fixture para mockar o PostRepository."""
    # Mockamos o repositório diretamente, não precisamos instanciar com mock_db_session
    #  aqui
    # a menos que a inicialização do repositório tenha lógica complexa com a sessão.
    # Geralmente, mockamos os métodos que serão chamados pelo serviço.
    mock_repo = MagicMock(spec=PostRepository)
    return mock_repo


@pytest.fixture
def badge_on_db(session_sql, community_on_db):
    badge = BadgeModel(
        id=str(uuid.uuid4()),
        name='Test Badge',
        description='Test Description',
        community_id=str(community_on_db.id),
        image_url='http://example.com/fixture_badge.png',
    )
    session_sql.add(badge)
    session_sql.flush()  # Mudança de flush para commit pode ser necessária se a sessão não persistir
    session_sql.commit()  # Adicionado para garantir que o dado persista para o cliente de teste
    return badge


@pytest.fixture
def secondary_badge_on_db(session_sql, community_on_db):
    badge = BadgeModel(
        id=uuid.uuid4(),
        name='Secondary Badge',
        description='Secondary Description',
        community_id=community_on_db.id,
    )
    session_sql.add(badge)
    session_sql.flush()
    session_sql.refresh(badge)
    return badge


@pytest.fixture
def member_badge_assignment_on_db(
    session_sql,
    community_member_on_db,
    badge_on_db,
):
    assignment = MemberBadgeModel(
        member_id=community_member_on_db.id,
        badge_id=badge_on_db.id,
    )
    session_sql.add(assignment)
    session_sql.flush()
    session_sql.refresh(assignment)
    return assignment


@pytest.fixture
def rating_on_db(session_sql, community_member_on_db):
    rating = Rating(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=5,
        title='Test Rating',
        description='Test rating description',
    )

    session_sql.add(rating)
    session_sql.flush()
    session_sql.refresh(rating)
    return rating


@pytest.fixture
def multiple_ratings_on_db(
    session_sql, community_on_db, user_on_db, secondary_user_on_db
):
    # Create additional community member for secondary user
    secondary_member = CommunityMember(
        community_id=community_on_db.id,
        user_id=secondary_user_on_db.id,
        role=CommunityMemberRoleEnum.MEMBER,
    )
    session_sql.add(secondary_member)
    session_sql.flush()

    ratings = [
        Rating(
            user_id=user_on_db.id,
            community_id=community_on_db.id,
            rating=5,
            title='Excellent Community!',
            description='Great experience',
        ),
        Rating(
            user_id=secondary_user_on_db.id,
            community_id=community_on_db.id,
            rating=4,
            title='Good Community',
            description='Nice place',
        ),
    ]

    session_sql.add_all(ratings)
    session_sql.flush()
    for rating in ratings:
        session_sql.refresh(rating)
    return ratings


@pytest.fixture
def comment_on_db(session_sql, post_on_db, user_on_db):
    comment = Comment(
        post_id=post_on_db.id,
        user_id=user_on_db.id,
        content='Este é um comentário de teste',
        status=CommentStatusEnum.ACTIVE,
        likes_count=0,
        report_count=0,
        parent_id=None,
    )

    session_sql.add(comment)
    session_sql.flush()
    session_sql.refresh(comment)
    return comment


@pytest.fixture
def comment_reply_on_db(session_sql, comment_on_db, secondary_user_on_db):
    reply = Comment(
        post_id=comment_on_db.post_id,
        user_id=secondary_user_on_db.id,
        content='Esta é uma resposta ao comentário',
        status=CommentStatusEnum.ACTIVE,
        likes_count=0,
        report_count=0,
        parent_id=comment_on_db.id,
    )

    session_sql.add(reply)
    session_sql.flush()
    session_sql.refresh(reply)
    return reply


@pytest.fixture
def comment_like_on_db(session_sql, comment_on_db, user_on_db):
    comment_like = CommentLikes(
        comment_id=comment_on_db.id,
        user_id=user_on_db.id,
    )

    session_sql.add(comment_like)
    session_sql.flush()
    session_sql.refresh(comment_like)
    return comment_like
