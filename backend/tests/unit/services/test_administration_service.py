import pytest
from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

from app.api.administration.schema import ImportMembers
from app.api.administration.service import AdministrationService
from app.api.communities.schema import (
    CommunityMemberCreate,
    CommunityMemberRoleEnum,
    CommunityMemberResponse,
)
from app.api.post.schemas import (
    CampaignUpdate,
    ComplaintLevelEnum,
    ComplaintUpdate,
    PostFeedbackCreate,
    PostTypeEnum,
)
from app.api.post.model import CampaignPost, PostFeedback
from app.api.post.schemas import PostResponse
from app.api.users.model import User
from app.utils.schema import PaginationSearchParams


@pytest.mark.unit
def test_import_users_to_community_service_success():
    """
    Tests the `import_users_to_community` method of AdministrationService.

    Scenario:
    - Given a list with one user email
    - When the service retrieves the user, creates a community member, and maps it to a response
    - Then it should return a list containing the expected CommunityMemberResponse
    """
    # Arrange
    fake_email = 'test@example.com'
    fake_community_id = str(uuid4())
    fake_user_id = str(uuid4())

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id

    expect_member_response = Mock(spec=CommunityMemberResponse)
    expect_member_response.user_id = fake_user_id
    expect_member_response.community_id = fake_community_id

    mock_tm = Mock()
    mock_user_service = Mock()
    mock_user_service.get_by_email.return_value = fake_user

    mock_community_service = Mock()
    mock_community_service.create_member.return_value = 'created_member'
    mock_community_service._map_member_to_response.return_value = expect_member_response

    service = AdministrationService(mock_tm)
    service.user_service = mock_user_service
    service.community_service = mock_community_service

    # Act
    result = service.import_users_to_community([fake_email], fake_community_id)

    # Assert
    mock_user_service.get_by_email.assert_called_once_with(fake_email)
    mock_community_service.create_member.assert_called_once_with(
        CommunityMemberCreate(
            user_id=fake_user_id,
            community_id=fake_community_id,
        )
    )
    mock_community_service._map_member_to_response.assert_called_once_with(
        'created_member'
    )
    assert result is not None
    assert len(result) == 1
    assert result[0].user_id == fake_user_id
    assert result[0].community_id == fake_community_id


@pytest.mark.unit
def test_list_all_members_from_community_service_success():
    """
    Tests the `list_all_members_from_community` method of AdministrationService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service gets the community and lists its members
    - Then it should return a paginated response with the expected members
    """
    # Arrange
    fake_community_id = uuid4()
    fake_user_id = uuid4()
    fake_member_id = uuid4()

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_member_response = Mock(spec=CommunityMemberResponse)
    fake_member_response.user_id = fake_user_id
    fake_member_response.community_id = fake_community_id
    fake_member_response.role = CommunityMemberRoleEnum.MEMBER
    fake_member_response.status_participation = 'active'

    fake_pagination_response = Mock()
    fake_pagination_response.items = [fake_member_response]
    fake_pagination_response.total = 1
    fake_pagination_response.has_more = False

    mock_tm = Mock()
    mock_community_service = Mock()
    mock_community_service.get_community.return_value = 'community'
    mock_community_service.list_members.return_value = fake_pagination_response

    service = AdministrationService(mock_tm)
    service.community_service = mock_community_service

    # Act
    result = service.list_all_members_from_community(
        fake_community_id, fake_pagination_params
    )

    # Assert
    mock_community_service.get_community.assert_called_once_with(fake_community_id)
    mock_community_service.list_members.assert_called_once_with(
        fake_community_id, fake_pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].user_id == fake_user_id
    assert result.items[0].community_id == fake_community_id
    assert result.items[0].role == CommunityMemberRoleEnum.MEMBER
    assert result.items[0].status_participation == 'active'
    assert result.total == 1
    assert result.has_more == False


@pytest.mark.unit
def test_list_user_admin_communities_service_success():
    """
    Tests the `list_user_admin_communities` method of AdministrationService.

    Scenario:
    - Given a user ID and pagination parameters
    - When the service lists user communities and filters for admin role
    - Then it should return a paginated response with only admin communities
    """
    # Arrange
    fake_user_id = str(uuid4())
    fake_community_id = str(uuid4())

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_community = Mock()
    fake_community.id = fake_community_id
    fake_community.name = 'Test Community'

    fake_member_association = Mock()
    fake_member_association.role = CommunityMemberRoleEnum.ADMIN

    fake_user_communities_response = Mock()
    fake_user_communities_response.items = [fake_community]

    mock_tm = Mock()
    mock_community_service = Mock()
    mock_community_service.list_user_communities.return_value = (
        fake_user_communities_response
    )
    mock_community_service.get_member_association.return_value = fake_member_association

    service = AdministrationService(mock_tm)
    service.community_service = mock_community_service

    # Act
    result = service.list_user_admin_communities(fake_user_id, fake_pagination_params)

    # Assert
    mock_community_service.list_user_communities.assert_called_once_with(
        fake_user_id, fake_pagination_params
    )
    mock_community_service.get_member_association.assert_called_once_with(
        fake_user_id, fake_community_id
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].id == fake_community_id
    assert result.items[0].name == 'Test Community'
    assert result.total == 1
    assert result.has_more == False


@pytest.mark.unit
def test_get_campaign_service_success():
    """
    Tests the `get_campaign` method of AdministrationService.

    Scenario:
    - Given a campaign post ID
    - When the service retrieves the campaign from repository
    - Then it should return the expected campaign
    """
    # Arrange
    fake_post_id = uuid4()

    fake_campaign = Mock()
    fake_campaign.post_id = fake_post_id
    fake_campaign.target_participants = 10
    fake_campaign.current_participants = 5
    fake_campaign.status_campaign = 'active'

    mock_tm = Mock()
    mock_campaign_repo = Mock()
    mock_campaign_repo.get_by_id.return_value = fake_campaign

    service = AdministrationService(mock_tm)
    service.campaign_repo = mock_campaign_repo

    # Act
    result = service.get_campaign(fake_post_id)

    # Assert
    mock_campaign_repo.get_by_id.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.post_id == fake_post_id
    assert result.target_participants == 10
    assert result.current_participants == 5
    assert result.status_campaign == 'active'


@pytest.mark.unit
def test_update_campaign_service_success():
    """
    Tests the `update_campaign` method of AdministrationService.

    Scenario:
    - Given a campaign post ID and update data
    - When the service updates the campaign and creates a response
    - Then it should return the expected campaign response
    """
    # Arrange
    fake_post_id = uuid4()
    fake_campaign_update = CampaignUpdate(target_participants=10)

    fake_campaign = Mock(spec=CampaignPost)
    fake_campaign.post_id = fake_post_id
    fake_campaign.target_participants = 5
    fake_campaign.current_participants = 3
    fake_campaign.status_campaign = 'pending'

    fake_saved_campaign = Mock()
    fake_saved_campaign.target_participants = 10
    fake_saved_campaign.current_participants = 3
    fake_saved_campaign.status_campaign = 'pending'

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id

    mock_tm = Mock()
    mock_campaign_repo = Mock()
    mock_campaign_repo.get_by_id.return_value = fake_campaign
    mock_campaign_repo.save.return_value = fake_saved_campaign

    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post

    service = AdministrationService(mock_tm)
    service.campaign_repo = mock_campaign_repo
    service.post_service = mock_post_service

    # Act
    result = service.update_campaign(fake_post_id, fake_campaign_update)

    # Assert
    mock_campaign_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_campaign_repo.save.assert_called_once_with(fake_campaign)
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.post.id == fake_post_id
    assert result.target_participants == 10
    assert result.current_participants == 3
    assert result.status_campaign == 'pending'


@pytest.mark.unit
def test_list_all_campaigns_from_community_service_success():
    """
    Tests the `list_all_campaigns_from_community` method of AdministrationService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service lists campaigns and creates responses
    - Then it should return a paginated response with campaign data
    """
    # Arrange
    fake_community_id = uuid4()
    fake_post_id = uuid4()

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_campaign = Mock(spec=CampaignPost)
    fake_campaign.post_id = fake_post_id
    fake_campaign.target_participants = 10
    fake_campaign.current_participants = 5
    fake_campaign.status_campaign = 'approved'

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id

    mock_tm = Mock()
    mock_campaign_repo = Mock()
    mock_campaign_repo.list_campaigns_by_community.return_value = ([fake_campaign], 1)

    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post

    service = AdministrationService(mock_tm)
    service.campaign_repo = mock_campaign_repo
    service.post_service = mock_post_service

    # Act
    result = service.list_all_campaigns_from_community(
        fake_community_id, fake_pagination_params
    )

    # Assert
    mock_campaign_repo.list_campaigns_by_community.assert_called_once_with(
        fake_community_id, fake_pagination_params
    )
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].post.id == fake_post_id
    assert result.items[0].target_participants == 10
    assert result.items[0].current_participants == 5
    assert result.items[0].status_campaign == 'approved'
    assert result.total == 1
    assert result.has_more == False


@pytest.mark.unit
def test_get_complaint_service_success():
    """
    Tests the `get_complaint` method of AdministrationService.

    Scenario:
    - Given a complaint post ID
    - When the service retrieves the complaint from repository
    - Then it should return the expected complaint
    """
    # Arrange
    fake_post_id = uuid4()

    fake_complaint = Mock()
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 5
    fake_complaint.status_complaint = 'pending'
    fake_complaint.level_complaint = ComplaintLevelEnum.LOW

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.get_by_id.return_value = fake_complaint

    service = AdministrationService(mock_tm)
    service.complaint_repo = mock_complaint_repo

    # Act
    result = service.get_complaint(fake_post_id)

    # Assert
    mock_complaint_repo.get_by_id.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.post_id == fake_post_id
    assert result.confirmations_count == 5
    assert result.status_complaint == 'pending'
    assert result.level_complaint == ComplaintLevelEnum.LOW


@pytest.mark.unit
def test_update_complaint_service_success():
    """
    Tests the `update_complaint` method of AdministrationService.

    Scenario:
    - Given a complaint post ID and update data
    - When the service updates the complaint and adjusts level based on confirmations
    - Then it should return the expected updated complaint
    """
    # Arrange
    fake_post_id = uuid4()
    fake_complaint_update = ComplaintUpdate(confirmations_count=1)

    fake_complaint = Mock()
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 0
    fake_complaint.status_complaint = 'pending'
    fake_complaint.level_complaint = ComplaintLevelEnum.LOW

    fake_saved_complaint = Mock()
    fake_saved_complaint.confirmations_count = 1
    fake_saved_complaint.status_complaint = 'pending'
    fake_saved_complaint.level_complaint = ComplaintLevelEnum.LOW

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.get_by_id.return_value = fake_complaint
    mock_complaint_repo.save.return_value = fake_saved_complaint

    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post

    service = AdministrationService(mock_tm)
    service.complaint_repo = mock_complaint_repo
    service.post_service = mock_post_service

    # Act
    result = service.update_complaint(fake_post_id, fake_complaint_update)

    # Assert
    mock_complaint_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_complaint_repo.save.assert_called_once_with(fake_complaint)
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.post.id == fake_post_id
    assert result.confirmations_count == 1
    assert result.status_complaint == 'pending'
    assert result.level_complaint == ComplaintLevelEnum.LOW


@pytest.mark.unit
def test_list_all_complaints_from_community_service_success():
    """
    Tests the `list_all_complaints_from_community` method of AdministrationService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service lists complaints and creates responses
    - Then it should return a paginated response with complaint data
    """
    # Arrange
    fake_community_id = uuid4()
    fake_post_id = uuid4()

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_complaint = Mock()
    fake_complaint.post_id = fake_post_id
    fake_complaint.confirmations_count = 5
    fake_complaint.status_complaint = 'pending'
    fake_complaint.level_complaint = ComplaintLevelEnum.LOW

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.list_complaints_by_community.return_value = ([fake_complaint], 1)

    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post

    service = AdministrationService(mock_tm)
    service.complaint_repo = mock_complaint_repo
    service.post_service = mock_post_service

    # Act
    result = service.list_all_complaints_from_community(
        fake_community_id, fake_pagination_params
    )

    # Assert
    mock_complaint_repo.list_complaints_by_community.assert_called_once_with(
        fake_community_id, fake_pagination_params
    )
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].post.id == fake_post_id
    assert result.items[0].confirmations_count == 5
    assert result.items[0].status_complaint == 'pending'
    assert result.items[0].level_complaint == ComplaintLevelEnum.LOW
    assert result.total == 1
    assert result.has_more == False


@pytest.mark.unit
def test_create_post_feedback_service_success():
    """
    Tests the `create_post_feedback` method of AdministrationService.

    Scenario:
    - Given a post feedback creation request
    - When the service creates the feedback
    - Then it should return the expected feedback
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_member_id = str(uuid4())

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id
    fake_post.type_post = PostTypeEnum.CAMPAIGN

    fake_post_feedback_create = PostFeedbackCreate(
        post_id=fake_post_id,
        member_id=fake_member_id,
        subject='Feedback',
        message='Example message',
    )

    fake_created_feedback = Mock()
    fake_created_feedback.post_id = fake_post_id
    fake_created_feedback.member_id = fake_member_id
    fake_created_feedback.subject = 'Feedback'
    fake_created_feedback.message = 'Example message'

    mock_tm = Mock()
    mock_post_feedback_repo = Mock()
    mock_post_feedback_repo.save.return_value = fake_created_feedback

    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post

    mock_community_service = Mock()
    mock_community_service.get_member.return_value = 'member'

    service = AdministrationService(mock_tm)
    service.post_feedback_repo = mock_post_feedback_repo
    service.post_service = mock_post_service
    service.community_service = mock_community_service

    # Act
    result = service.create_post_feedback(fake_post_feedback_create)

    # Assert
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    mock_community_service.get_member.assert_called_once_with(fake_member_id)
    mock_post_feedback_repo.save.assert_called_once()
    assert result is not None
    assert result.post_id == fake_post_id
    assert result.member_id == fake_member_id
    assert result.subject == 'Feedback'
    assert result.message == 'Example message'


@pytest.mark.unit
def test_list_all_post_feedbacks_service_success():
    """
    Tests the `list_feedbacks_from_post` method of AdministrationService.

    Scenario:
    - Given a post ID and pagination parameters
    - When the service lists feedbacks for the post
    - Then it should return a paginated response with feedback data
    """
    # Arrange
    fake_post_id = uuid4()
    fake_member_id = uuid4()

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_feedback = Mock(spec=PostFeedback)
    fake_feedback.id = uuid4()
    fake_feedback.post_id = fake_post_id
    fake_feedback.member_id = fake_member_id
    fake_feedback.subject = 'Feedback'
    fake_feedback.message = 'Example message'
    fake_feedback.created_at = datetime.now()

    mock_tm = Mock()
    mock_post_feedback_repo = Mock()
    mock_post_feedback_repo.list_by_post.return_value = ([fake_feedback], 1)

    service = AdministrationService(mock_tm)
    service.post_feedback_repo = mock_post_feedback_repo

    # Act
    result = service.list_feedbacks_from_post(fake_post_id, fake_pagination_params)

    # Assert
    mock_post_feedback_repo.list_by_post.assert_called_once_with(
        fake_post_id, fake_pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].post_id == fake_post_id
    assert result.items[0].member_id == fake_member_id
    assert result.items[0].subject == 'Feedback'
    assert result.items[0].message == 'Example message'
    assert result.total == 1
    assert result.has_more == False
