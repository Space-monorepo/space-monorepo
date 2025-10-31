from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.api.communities.schema import (
    CommunityMemberResponse,
    CommunityMemberRoleEnum,
    CommunityMemberStatusEnum,
)
from app.api.moderation.schema import ModerationActionResponse
from app.api.moderation.service import ModerationService
from app.api.post.schemas import (
    CommunityRelated,
    ComplaintLevelEnum,
    ComplaintStatusEnum,
    PollOptionResponse,
    PostAuthor,
    PostResponse,
    PostStatusEnum,
    PostTypeEnum,
)
from app.api.reports.exceptions import ModeratorAlreadyVotedError
from app.api.reports.model import (
    ModerationVotes,
    ReportComment,
    ReportMember,
    ReportPost,
)
from app.api.reports.schema import (
    Author,
    ModerationVotesCreate,
    ReportReasonEnum,
    ReportResponse,
    ReportTypeEnum,
    VoteTypeEnum,
)
from app.utils.schema import PaginationSearchParams


@pytest.mark.unit
def test_moderate_post_with_rejection_success():
    """
    Tests the `moderate_post` method of ModerationService when status is rejected.

    Scenario:
    - Given a valid post ID and new_status as 'rejected'
    - When the service moderates the post
    - Then it should delete the post and return True
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_new_status = PostStatusEnum.REJECTED

    # Mock do PostResponse
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = uuid4()
    fake_community.name = "Test Community"

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = uuid4()
    fake_user.name = "Test User"
    fake_user.profile_picture = "https://example.com/profile.jpg"
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_post_response.title = "Test Post"
    fake_post_response.content = "Test content"
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 5
    fake_post_response.comments_count = 2
    fake_post_response.report_count = 0

    mock_tm = Mock()
    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post_response
    mock_post_service.delete_post.return_value = True

    service = ModerationService(mock_tm)
    service.post_service = mock_post_service

    # Act
    result = service.moderate_post(fake_post_id, fake_new_status)

    # Assert
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    mock_post_service.delete_post.assert_called_once_with(fake_post_id)
    assert result is True


@pytest.mark.unit
def test_moderate_post_with_status_update_success():
    """
    Tests the `moderate_post` method of ModerationService when updating status.

    Scenario:
    - Given a valid post ID and new_status as 'suspended'
    - When the service moderates the post
    - Then it should update the post status and return updated PostResponse
    """
    # Arrange
    fake_post_id = str(uuid4())
    fake_new_status = PostStatusEnum.SUSPENDED

    # Mock do PostResponse original
    fake_community = Mock(spec=CommunityRelated)
    fake_community.id = uuid4()
    fake_community.name = "Test Community"

    fake_user = Mock(spec=PostAuthor)
    fake_user.id = uuid4()
    fake_user.name = "Test User"
    fake_user.profile_picture = "https://example.com/profile.jpg"
    fake_user.role = CommunityMemberRoleEnum.MEMBER

    fake_post_response = Mock(spec=PostResponse)
    fake_post_response.id = fake_post_id
    fake_post_response.community = fake_community
    fake_post_response.user = fake_user
    fake_post_response.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_post_response.title = "Test Post"
    fake_post_response.content = "Test content"
    fake_post_response.status = PostStatusEnum.ACTIVE
    fake_post_response.likes_count = 5
    fake_post_response.comments_count = 2
    fake_post_response.report_count = 0

    # Mock do PostResponse atualizado
    fake_updated_post_response = Mock(spec=PostResponse)
    fake_updated_post_response.id = fake_post_id
    fake_updated_post_response.community = fake_community
    fake_updated_post_response.user = fake_user
    fake_updated_post_response.type_post = PostTypeEnum.ANNOUNCEMENT
    fake_updated_post_response.title = "Test Post"
    fake_updated_post_response.content = "Test content"
    fake_updated_post_response.status = PostStatusEnum.SUSPENDED
    fake_updated_post_response.likes_count = 5
    fake_updated_post_response.comments_count = 2
    fake_updated_post_response.report_count = 0

    mock_tm = Mock()
    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post_response
    mock_post_service.update_post.return_value = fake_updated_post_response

    service = ModerationService(mock_tm)
    service.post_service = mock_post_service

    # Act
    result = service.moderate_post(fake_post_id, fake_new_status)

    # Assert
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    mock_post_service.update_post.assert_called_once_with(fake_post_id, fake_post_response)
    assert result is not None
    assert isinstance(result, Mock)
    assert result.status == PostStatusEnum.SUSPENDED


@pytest.mark.unit
def test_delete_comment_service_success():
    """
    Tests the `delete_comment` method of ModerationService.

    Scenario:
    - Given a valid comment ID
    - When the service deletes the comment
    - Then it should return True indicating successful deletion
    """
    # Arrange
    fake_comment_id = str(uuid4())

    mock_tm = Mock()
    mock_comment_service = Mock()
    mock_comment_service.delete_comment.return_value = True

    service = ModerationService(mock_tm)
    service.comment_service = mock_comment_service

    # Act
    result = service.delete_comment(fake_comment_id)

    # Assert
    mock_comment_service.delete_comment.assert_called_once_with(fake_comment_id)
    assert result is True


@pytest.mark.unit
def test_moderate_report_moderator_already_voted_raises_error():
    """
    Tests the `moderate_report` method when moderator tries to vote twice.

    Scenario:
    - Given a moderator who has already voted on a report
    - When the moderator tries to vote again
    - Then it should raise ModeratorAlreadyVotedError
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.SUSPEND,
    )

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = True

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo

    # Act & Assert
    with pytest.raises(ModeratorAlreadyVotedError) as exc_info:
        service.moderate_report(fake_report_id, fake_vote)

    assert f'Moderator {fake_moderator_id} has already voted' in str(exc_info.value)
    mock_moderation_votes_repo.moderator_has_voted.assert_called_once_with(
        fake_report_id, fake_moderator_id
    )


@pytest.mark.unit
def test_moderate_report_first_vote_waits_for_more_votes():
    """
    Tests the `moderate_report` method when it's the first vote.

    Scenario:
    - Given a report with no votes
    - When a moderator casts the first vote
    - Then it should save the vote and return response without taking action
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())
    fake_vote_id = str(uuid4())
    fake_created_at = datetime.now(timezone.utc)

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.SUSPEND,
    )

    fake_saved_vote = Mock(spec=ModerationVotes)
    fake_saved_vote.id = fake_vote_id
    fake_saved_vote.report_id = fake_report_id
    fake_saved_vote.moderator_id = fake_moderator_id
    fake_saved_vote.vote = VoteTypeEnum.SUSPEND
    fake_saved_vote.created_at = fake_created_at

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = False
    mock_moderation_votes_repo.save.return_value = fake_saved_vote
    mock_moderation_votes_repo.get_vote_counts.return_value = (1, 0)  # 1 suspend, 0 tolerate

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo

    # Act
    result = service.moderate_report(fake_report_id, fake_vote)

    # Assert
    assert result.id == fake_vote_id
    assert result.report_id == fake_report_id
    assert result.moderator_id == fake_moderator_id
    assert result.vote == VoteTypeEnum.SUSPEND
    mock_moderation_votes_repo.save.assert_called_once()
    mock_moderation_votes_repo.get_vote_counts.assert_called_once_with(fake_report_id)


@pytest.mark.unit
def test_moderate_report_suspend_post_with_majority_votes():
    """
    Tests the `moderate_report` method suspends post when 2 suspend votes.

    Scenario:
    - Given a post report with 1 suspend vote already
    - When a second moderator votes suspend
    - Then it should suspend the post, delete votes and report
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_vote_id = str(uuid4())
    fake_created_at = datetime.now(timezone.utc)

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.SUSPEND,
    )

    fake_saved_vote = Mock(spec=ModerationVotes)
    fake_saved_vote.id = fake_vote_id
    fake_saved_vote.report_id = fake_report_id
    fake_saved_vote.moderator_id = fake_moderator_id
    fake_saved_vote.vote = VoteTypeEnum.SUSPEND
    fake_saved_vote.created_at = fake_created_at

    fake_reporter = Author(
        id=str(uuid4()),
        name="Reporter User",
        profile_picture=None,
        role=CommunityMemberRoleEnum.MEMBER,
    )

    fake_report = ReportResponse(
        id=fake_report_id,
        reporter=fake_reporter,
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.SPAM,
        description="Spam post",
        created_at=fake_created_at,
    )

    fake_report_post = Mock(spec=ReportPost)
    fake_report_post.report_id = fake_report_id
    fake_report_post.post_id = fake_post_id

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = False
    mock_moderation_votes_repo.save.return_value = fake_saved_vote
    mock_moderation_votes_repo.get_vote_counts.return_value = (2, 0)  # 2 suspend, 0 tolerate
    mock_moderation_votes_repo.delete_votes_by_report.return_value = True

    mock_report_service = Mock()
    mock_report_service.get_report.return_value = fake_report
    mock_report_service.report_post_repo.get_by_id.return_value = fake_report_post
    mock_report_service.delete_report.return_value = True

    mock_post_service = Mock()
    mock_post_service.update_post.return_value = Mock()

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo
    service.report_service = mock_report_service
    service.post_service = mock_post_service

    # Act
    result = service.moderate_report(fake_report_id, fake_vote)

    # Assert
    assert isinstance(result, ModerationActionResponse)
    assert result.action == VoteTypeEnum.SUSPEND
    assert result.report_type == ReportTypeEnum.POST_REPORT
    assert "Post suspenso com sucesso" in result.message
    mock_post_service.update_post.assert_called_once()
    mock_moderation_votes_repo.delete_votes_by_report.assert_called_once_with(fake_report_id)
    mock_report_service.delete_report.assert_called_once_with(fake_report_id)


@pytest.mark.unit
def test_moderate_report_tolerate_post_with_majority_votes():
    """
    Tests the `moderate_report` method tolerates post when 2 tolerate votes.

    Scenario:
    - Given a post report with 1 tolerate vote already
    - When a second moderator votes tolerate
    - Then it should mark post as active, delete votes and report
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_vote_id = str(uuid4())
    fake_created_at = datetime.now(timezone.utc)

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.TOLERATE,
    )

    fake_saved_vote = Mock(spec=ModerationVotes)
    fake_saved_vote.id = fake_vote_id
    fake_saved_vote.report_id = fake_report_id
    fake_saved_vote.moderator_id = fake_moderator_id
    fake_saved_vote.vote = VoteTypeEnum.TOLERATE
    fake_saved_vote.created_at = fake_created_at

    fake_reporter = Author(
        id=str(uuid4()),
        name="Reporter User",
        profile_picture=None,
        role=CommunityMemberRoleEnum.MEMBER,
    )

    fake_report = ReportResponse(
        id=fake_report_id,
        reporter=fake_reporter,
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.SPAM,
        description="Spam post",
        created_at=fake_created_at,
    )

    fake_report_post = Mock(spec=ReportPost)
    fake_report_post.report_id = fake_report_id
    fake_report_post.post_id = fake_post_id

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = False
    mock_moderation_votes_repo.save.return_value = fake_saved_vote
    mock_moderation_votes_repo.get_vote_counts.return_value = (0, 2)  # 0 suspend, 2 tolerate
    mock_moderation_votes_repo.delete_votes_by_report.return_value = True

    mock_report_service = Mock()
    mock_report_service.get_report.return_value = fake_report
    mock_report_service.report_post_repo.get_by_id.return_value = fake_report_post
    mock_report_service.delete_report.return_value = True

    mock_post_service = Mock()
    mock_post_service.update_post.return_value = Mock()

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo
    service.report_service = mock_report_service
    service.post_service = mock_post_service

    # Act
    result = service.moderate_report(fake_report_id, fake_vote)

    # Assert
    assert isinstance(result, ModerationActionResponse)
    assert result.action == VoteTypeEnum.TOLERATE
    assert result.report_type == ReportTypeEnum.POST_REPORT
    assert "Post tolerado e mantido ativo" in result.message
    mock_post_service.update_post.assert_called_once()
    mock_moderation_votes_repo.delete_votes_by_report.assert_called_once_with(fake_report_id)
    mock_report_service.delete_report.assert_called_once_with(fake_report_id)


@pytest.mark.unit
def test_moderate_report_suspend_member_with_majority_votes():
    """
    Tests the `moderate_report` method suspends member when 2 suspend votes.

    Scenario:
    - Given a member report with 1 suspend vote already
    - When a second moderator votes suspend
    - Then it should suspend the member, delete votes and report
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())
    fake_member_id = str(uuid4())
    fake_vote_id = str(uuid4())
    fake_created_at = datetime.now(timezone.utc)

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.SUSPEND,
    )

    fake_saved_vote = Mock(spec=ModerationVotes)
    fake_saved_vote.id = fake_vote_id
    fake_saved_vote.report_id = fake_report_id
    fake_saved_vote.moderator_id = fake_moderator_id
    fake_saved_vote.vote = VoteTypeEnum.SUSPEND
    fake_saved_vote.created_at = fake_created_at

    fake_reporter = Author(
        id=str(uuid4()),
        name="Reporter User",
        profile_picture=None,
        role=CommunityMemberRoleEnum.MEMBER,
    )

    fake_report = ReportResponse(
        id=fake_report_id,
        reporter=fake_reporter,
        type=ReportTypeEnum.MEMBER_REPORT,
        reason=ReportReasonEnum.HARASSMENT,
        description="Harassment behavior",
        created_at=fake_created_at,
    )

    fake_report_member = Mock(spec=ReportMember)
    fake_report_member.report_id = fake_report_id
    fake_report_member.member_id = fake_member_id

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = False
    mock_moderation_votes_repo.save.return_value = fake_saved_vote
    mock_moderation_votes_repo.get_vote_counts.return_value = (2, 0)  # 2 suspend, 0 tolerate
    mock_moderation_votes_repo.delete_votes_by_report.return_value = True

    mock_report_service = Mock()
    mock_report_service.get_report.return_value = fake_report
    mock_report_service.report_member_repo.get_by_id.return_value = fake_report_member
    mock_report_service.delete_report.return_value = True

    mock_community_service = Mock()
    mock_community_service.update_member_status.return_value = Mock()

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo
    service.report_service = mock_report_service
    service.community_service = mock_community_service

    # Act
    result = service.moderate_report(fake_report_id, fake_vote)

    # Assert
    assert isinstance(result, ModerationActionResponse)
    assert result.action == VoteTypeEnum.SUSPEND
    assert result.report_type == ReportTypeEnum.MEMBER_REPORT
    assert "Membro suspenso com sucesso" in result.message
    mock_community_service.update_member_status.assert_called_once_with(
        fake_member_id, CommunityMemberStatusEnum.SUSPENDED
    )
    mock_moderation_votes_repo.delete_votes_by_report.assert_called_once_with(fake_report_id)
    mock_report_service.delete_report.assert_called_once_with(fake_report_id)


@pytest.mark.unit
def test_moderate_report_delete_comment_with_majority_votes():
    """
    Tests the `moderate_report` method deletes comment when 2 suspend votes.

    Scenario:
    - Given a comment report with 1 suspend vote already
    - When a second moderator votes suspend
    - Then it should delete the comment, delete votes and report
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())
    fake_comment_id = str(uuid4())
    fake_vote_id = str(uuid4())
    fake_created_at = datetime.now(timezone.utc)

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.SUSPEND,
    )

    fake_saved_vote = Mock(spec=ModerationVotes)
    fake_saved_vote.id = fake_vote_id
    fake_saved_vote.report_id = fake_report_id
    fake_saved_vote.moderator_id = fake_moderator_id
    fake_saved_vote.vote = VoteTypeEnum.SUSPEND
    fake_saved_vote.created_at = fake_created_at

    fake_reporter = Author(
        id=str(uuid4()),
        name="Reporter User",
        profile_picture=None,
        role=CommunityMemberRoleEnum.MEMBER,
    )

    fake_report = ReportResponse(
        id=fake_report_id,
        reporter=fake_reporter,
        type=ReportTypeEnum.COMMENT_REPORT,
        reason=ReportReasonEnum.HATE_SPEECH,
        description="Hate speech comment",
        created_at=fake_created_at,
    )

    fake_report_comment = Mock(spec=ReportComment)
    fake_report_comment.report_id = fake_report_id
    fake_report_comment.comment_id = fake_comment_id

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = False
    mock_moderation_votes_repo.save.return_value = fake_saved_vote
    mock_moderation_votes_repo.get_vote_counts.return_value = (2, 0)  # 2 suspend, 0 tolerate
    mock_moderation_votes_repo.delete_votes_by_report.return_value = True

    mock_report_service = Mock()
    mock_report_service.get_report.return_value = fake_report
    mock_report_service.report_comment_repo.get_by_id.return_value = fake_report_comment
    mock_report_service.delete_report.return_value = True

    mock_comment_service = Mock()
    mock_comment_service.delete_comment.return_value = True

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo
    service.report_service = mock_report_service
    service.comment_service = mock_comment_service

    # Act
    result = service.moderate_report(fake_report_id, fake_vote)

    # Assert
    assert isinstance(result, ModerationActionResponse)
    assert result.action == VoteTypeEnum.SUSPEND
    assert result.report_type == ReportTypeEnum.COMMENT_REPORT
    assert "Comentário deletado com sucesso" in result.message
    mock_comment_service.delete_comment.assert_called_once_with(fake_comment_id)
    mock_moderation_votes_repo.delete_votes_by_report.assert_called_once_with(fake_report_id)
    mock_report_service.delete_report.assert_called_once_with(fake_report_id)


@pytest.mark.unit
def test_moderate_report_majority_wins_suspend_over_tolerate():
    """
    Tests the `moderate_report` method where suspend wins with 2 votes vs 1 tolerate.

    Scenario:
    - Given a post report with 2 suspend votes and 1 tolerate vote
    - When calculating the action
    - Then it should suspend the post (majority wins)
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_moderator_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_vote_id = str(uuid4())
    fake_created_at = datetime.now(timezone.utc)

    fake_vote = ModerationVotesCreate(
        report_id=fake_report_id,
        moderator_id=fake_moderator_id,
        vote=VoteTypeEnum.SUSPEND,
    )

    fake_saved_vote = Mock(spec=ModerationVotes)
    fake_saved_vote.id = fake_vote_id
    fake_saved_vote.report_id = fake_report_id
    fake_saved_vote.moderator_id = fake_moderator_id
    fake_saved_vote.vote = VoteTypeEnum.SUSPEND
    fake_saved_vote.created_at = fake_created_at

    fake_reporter = Author(
        id=str(uuid4()),
        name="Reporter User",
        profile_picture=None,
        role=CommunityMemberRoleEnum.MEMBER,
    )

    fake_report = ReportResponse(
        id=fake_report_id,
        reporter=fake_reporter,
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.MISINFORMATION,
        description="Misinformation post",
        created_at=fake_created_at,
    )

    fake_report_post = Mock(spec=ReportPost)
    fake_report_post.report_id = fake_report_id
    fake_report_post.post_id = fake_post_id

    mock_tm = Mock()
    mock_moderation_votes_repo = Mock()
    mock_moderation_votes_repo.moderator_has_voted.return_value = False
    mock_moderation_votes_repo.save.return_value = fake_saved_vote
    mock_moderation_votes_repo.get_vote_counts.return_value = (2, 1)  # 2 suspend, 1 tolerate
    mock_moderation_votes_repo.delete_votes_by_report.return_value = True

    mock_report_service = Mock()
    mock_report_service.get_report.return_value = fake_report
    mock_report_service.report_post_repo.get_by_id.return_value = fake_report_post
    mock_report_service.delete_report.return_value = True

    mock_post_service = Mock()
    mock_post_service.update_post.return_value = Mock()

    service = ModerationService(mock_tm)
    service.moderation_votes_repo = mock_moderation_votes_repo
    service.report_service = mock_report_service
    service.post_service = mock_post_service

    # Act
    result = service.moderate_report(fake_report_id, fake_vote)

    # Assert
    assert isinstance(result, ModerationActionResponse)
    assert result.action == VoteTypeEnum.SUSPEND
    assert result.report_type == ReportTypeEnum.POST_REPORT
    assert "Post suspenso com sucesso" in result.message
    # Verify that suspend action was taken (post was suspended, not tolerated)
    calls = mock_post_service.update_post.call_args_list
    assert len(calls) == 1
    # The update should be for suspending the post
    mock_moderation_votes_repo.delete_votes_by_report.assert_called_once_with(fake_report_id)
    mock_report_service.delete_report.assert_called_once_with(fake_report_id)


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

    service = ModerationService(mock_tm)
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
def test_update_complaint_status_service_success():

    """
    Tests the `udpate_status_complaint` method of ModerationService.

    Scenario:
    - Given a valid post ID and new complaint status
    - When the service updates the complaint status
    - Then it should update and return the complaint with new status
    """
    # Arrange
    fake_post_id = uuid4()
    fake_old_status = ComplaintStatusEnum.PENDING
    fake_new_status = ComplaintStatusEnum.RESOLVED

    # Mock do ComplaintPost original
    fake_complaint_post = Mock()
    fake_complaint_post.post_id = fake_post_id
    fake_complaint_post.status_complaint = fake_old_status
    fake_complaint_post.confirmations_count = 5
    fake_complaint_post.level_complaint = ComplaintLevelEnum.LOW

    # Mock do ComplaintPost atualizado
    fake_saved_complaint_post = Mock()
    fake_saved_complaint_post.confirmations_count = 5
    fake_saved_complaint_post.status_complaint = fake_new_status
    fake_saved_complaint_post.level_complaint = ComplaintLevelEnum.LOW

    # Mock do PostResponse
    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id

    mock_tm = Mock()
    mock_complaint_repo = Mock()
    mock_complaint_repo.get_by_id.return_value = fake_complaint_post
    mock_complaint_repo.save.return_value = fake_saved_complaint_post

    mock_post_service = Mock()
    mock_post_service.get_post.return_value = fake_post

    service = ModerationService(mock_tm)
    service.complaint_repo = mock_complaint_repo
    service.post_service = mock_post_service

    # Act
    result = service.udpate_status_complaint(fake_post_id, fake_new_status)

    # Assert
    mock_complaint_repo.get_by_id.assert_called_once_with(fake_post_id)
    mock_complaint_repo.save.assert_called_once_with(fake_complaint_post)
    mock_post_service.get_post.assert_called_once_with(fake_post_id)
    assert result is not None
    assert result.post.id == fake_post_id
    assert result.status_complaint == fake_new_status
    assert result.confirmations_count == 5
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

    service = ModerationService(mock_tm)
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
def test_update_member_status_service_success():
    """
    Tests the `update_member_status` method of ModerationService.

    Scenario:
    - Given a valid member ID and new status
    - When the service updates the member status
    - Then it should return the updated CommunityMemberResponse
    """
    # Arrange
    fake_member_id = str(uuid4())
    fake_new_status = CommunityMemberStatusEnum.SUSPENDED

    fake_member_response = Mock(spec=CommunityMemberResponse)
    fake_member_response.id = fake_member_id
    fake_member_response.status = fake_new_status

    mock_tm = Mock()
    mock_community_service = Mock()
    mock_community_service.update_member_status.return_value = fake_member_response

    service = ModerationService(mock_tm)
    service.community_service = mock_community_service

    # Act
    result = service.update_member_status(fake_member_id, fake_new_status)

    # Assert
    mock_community_service.update_member_status.assert_called_once_with(
        fake_member_id, fake_new_status
    )
    assert result is not None
    assert result.id == fake_member_id
    assert result.status == fake_new_status


@pytest.mark.unit
def test_list_all_announcements_from_community_service_success():
    """
    Tests the `list_all_announcements_from_community` method of ModerationService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service lists announcements from the community
    - Then it should set type_post to ANNOUNCEMENT and return paginated posts
    """
    # Arrange
    fake_community_id = uuid4()
    fake_post_id = uuid4()

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_post_id
    fake_post.type_post = PostTypeEnum.ANNOUNCEMENT

    fake_pagination_response = Mock()
    fake_pagination_response.items = [fake_post]
    fake_pagination_response.total = 1
    fake_pagination_response.has_more = False

    mock_tm = Mock()
    mock_post_service = Mock()
    mock_post_service.list_posts_by_community.return_value = fake_pagination_response

    service = ModerationService(mock_tm)
    service.post_service = mock_post_service

    # Act
    result = service.list_all_announcements_from_community(
        fake_community_id, fake_pagination_params
    )

    # Assert
    assert fake_pagination_params.type_post == PostTypeEnum.ANNOUNCEMENT
    mock_post_service.list_posts_by_community.assert_called_once_with(
        fake_community_id, fake_pagination_params
    )
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].id == fake_post_id
    assert result.items[0].type_post == PostTypeEnum.ANNOUNCEMENT
    assert result.total == 1
    assert result.has_more == False


@pytest.mark.unit
def test_list_all_polls_from_community_service_success():
    """
    Tests the `list_all_polls_from_community` method of ModerationService.

    Scenario:
    - Given a community ID and pagination parameters
    - When the service lists polls from the community
    - Then it should return a paginated response with poll data including options and votes
    """
    # Arrange
    fake_community_id = uuid4()
    fake_poll_id = uuid4()

    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    fake_poll = Mock()
    fake_poll.id = fake_poll_id
    fake_poll.post_id = fake_poll_id
    fake_poll.question = "What is your favorite color?"

    fake_option1 = PollOptionResponse(
        id=uuid4(),
        answer="Blue",
        votes_count=5
    )

    fake_option2 = PollOptionResponse(
        id=uuid4(),
        answer="Red",
        votes_count=3
    )

    fake_post = Mock(spec=PostResponse)
    fake_post.id = fake_poll_id
    fake_post.type_post = PostTypeEnum.POLL

    mock_tm = Mock()
    mock_poll_repo = Mock()
    mock_poll_repo.list_polls_by_community.return_value = ([fake_poll], 1)

    mock_post_service = Mock()
    mock_post_service.list_poll_options.return_value = [fake_option1, fake_option2]
    mock_post_service.get_post.return_value = fake_post

    service = ModerationService(mock_tm)
    service.poll_repo = mock_poll_repo
    service.post_service = mock_post_service

    # Act
    result = service.list_all_polls_from_community(
        fake_community_id, fake_pagination_params
    )

    # Assert
    mock_poll_repo.list_polls_by_community.assert_called_once_with(
        fake_community_id, fake_pagination_params
    )
    mock_post_service.list_poll_options.assert_called_once_with(fake_poll_id)
    mock_post_service.get_post.assert_called_once_with(fake_poll_id)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 1
    assert result.items[0].post.id == fake_poll_id
    assert result.items[0].question == "What is your favorite color?"
    assert result.items[0].total_votes == 8
    assert result.total == 1
    assert result.has_more == False
