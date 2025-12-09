from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.api.communities.model import CommunityMember
from app.api.communities.schema import CommunityMemberRoleEnum
from app.api.reports.model import Report, ReportComment, ReportMember, ReportPost
from app.api.reports.schema import (
    CommentBriefReport,
    MemberBriefReport,
    PostBriefReport,
    ReportCommentCreate,
    ReportCreate,
    ReportMemberCreate,
    ReportPostCreate,
    ReportReasonEnum,
    ReportTypeEnum,
)
from app.api.reports.service import ReportService
from app.api.users.model import User
from app.utils.schema import PaginationSearchParams


@pytest.mark.unit
def test_get_report_service_success():
    """
    Tests the `get_report` method of ReportService.

    Scenario:
    - Given a valid report ID
    - When the service gets the report
    - Then it should return the report
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_type = ReportTypeEnum.MEMBER_REPORT
    fake_reason = ReportReasonEnum.DISCRIMINATION
    fake_description = 'User is being disrespectful'

    fake_report = Report(
        id=fake_report_id,
        reporter_id=fake_reporter_id,
        type=fake_type,
        reason=fake_reason,
        description=fake_description,
        created_at=datetime.now(timezone.utc),
    )

    fake_member = Mock(spec=CommunityMember)
    fake_member.id = fake_reporter_id
    fake_member.user_id = fake_user_id
    fake_member.role = CommunityMemberRoleEnum.MEMBER

    fake_user = Mock(spec=User)
    fake_user.name = 'John Doe'
    fake_user.profile_image_url = 'https://example.com/image.jpg'

    mock_tm = Mock()
    mock_community_service = Mock()
    mock_community_service.get_member.return_value = fake_member

    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user
    mock_tm.get_community_service.return_value = mock_community_service
    mock_tm.get_user_service.return_value = mock_user_service

    service = ReportService(mock_tm)
    service.community_service = mock_community_service
    service.user_service = mock_user_service
    service._get_report = Mock(return_value=fake_report)

    # Act
    result = service.get_report(fake_report_id)

    # Assert
    mock_community_service.get_member.assert_called_once_with(fake_reporter_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    assert result is not None
    assert result.id == fake_report_id
    assert result.type == fake_type
    assert result.reason == fake_reason
    assert result.description == fake_description
    assert result.reporter.id == fake_reporter_id
    assert result.reporter.name == fake_user.name
    assert result.reporter.profile_picture == fake_user.profile_image_url
    assert result.reporter.role == fake_member.role


@pytest.mark.unit
def test_create_report_service_success():
    """
    Tests the `create_report` method of ReportService.

    Scenario:
    - Given a valid report creation request
    - When the service creates the report and saves it to repository
    - Then it should return the created report
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_type = ReportTypeEnum.MEMBER_REPORT
    fake_reason = ReportReasonEnum.DISCRIMINATION
    fake_description = 'User is being disrespectful'

    fake_report_create = ReportCreate(
        reporter_id=fake_reporter_id,
        type=fake_type,
        reason=fake_reason,
        description=fake_description,
    )

    fake_created_report = Mock(spec=Report)
    fake_created_report.id = fake_report_id
    fake_created_report.reporter_id = fake_reporter_id
    fake_created_report.type = fake_type
    fake_created_report.reason = fake_reason
    fake_created_report.description = fake_description
    fake_created_report.created_at = datetime.now(timezone.utc)

    fake_member = Mock(spec=CommunityMember)
    fake_member.id = fake_reporter_id
    fake_member.user_id = fake_user_id
    fake_member.role = CommunityMemberRoleEnum.MEMBER

    fake_user = Mock(spec=User)
    fake_user.id = fake_user_id
    fake_user.name = 'John Doe'
    fake_user.profile_image_url = 'https://example.com/image.jpg'

    mock_tm = Mock()
    mock_report_repo = Mock()
    mock_report_repo.save.return_value = fake_created_report

    mock_community_service = Mock()
    mock_community_service.get_member.return_value = fake_member

    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user
    mock_tm.get_community_service.return_value = mock_community_service
    mock_tm.get_user_service.return_value = mock_user_service

    service = ReportService(mock_tm)
    service.report_repo = mock_report_repo
    service.community_service = mock_community_service
    service.user_service = mock_user_service

    # Act
    result = service.create_report(fake_report_create)

    # Assert
    mock_community_service.get_member.assert_called_once_with(fake_reporter_id)
    mock_user_service.get_user.assert_called_once_with(fake_user_id)
    mock_report_repo.save.assert_called_once()
    assert result is not None
    assert result.id == fake_report_id
    assert result.reporter.id == fake_reporter_id
    assert result.reporter.name == fake_user.name
    assert result.reporter.profile_picture == fake_user.profile_image_url
    assert result.reporter.role == fake_member.role
    assert result.type == fake_type
    assert result.reason == fake_reason
    assert result.description == fake_description
    assert result.created_at == fake_created_report.created_at


@pytest.mark.unit
def test_delete_report_service_success():
    """
    Tests the `delete_report` method of ReportService.

    Scenario:
    - Given a valid report ID
    - When the service deletes the report from repository
    - Then it should return True indicating successful deletion
    """
    # Arrange
    fake_report_id = uuid4()
    fake_reporter_id = str(uuid4())

    fake_existing_report = Mock(spec=Report)
    fake_existing_report.id = str(fake_report_id)
    fake_existing_report.reporter_id = fake_reporter_id
    fake_existing_report.type = ReportTypeEnum.POST_REPORT
    fake_existing_report.reason = ReportReasonEnum.SPAM
    fake_existing_report.description = 'This is spam content'
    fake_existing_report.created_at = datetime.now(timezone.utc)

    mock_tm = Mock()
    mock_report_repo = Mock()
    mock_report_repo.get_by_id.return_value = fake_existing_report
    mock_report_repo.delete.return_value = True

    service = ReportService(mock_tm)
    service.report_repo = mock_report_repo

    # Act
    result = service.delete_report(fake_report_id)

    # Assert
    mock_report_repo.get_by_id.assert_called_once_with(str(fake_report_id))
    mock_report_repo.delete.assert_called_once_with(fake_existing_report)
    assert result is True


@pytest.mark.unit
def test_create_report_member_service_success():
    """
    Tests the `create_report_member` method of ReportService.

    Scenario:
    - Given a valid report member creation request
    - When the service creates the report member and saves it to repository
    - Then it should return a ReportMemberResponse with mapped data
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_member_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_reason = ReportReasonEnum.HARASSMENT
    fake_description = 'Member is harassing others'

    fake_report_member_create = ReportMemberCreate(
        report_id=fake_report_id,
        member_id=fake_member_id,
        community_id=fake_community_id,
    )

    # Mock do report base
    fake_report_base = Mock(spec=Report)
    fake_report_base.id = fake_report_id
    fake_report_base.reporter_id = fake_reporter_id
    fake_report_base.type = ReportTypeEnum.MEMBER_REPORT
    fake_report_base.reason = fake_reason
    fake_report_base.description = fake_description
    fake_report_base.created_at = datetime.now(timezone.utc)

    # Mock do report member criado
    fake_created_report_member = Mock(spec=ReportMember)
    fake_created_report_member.report_id = fake_report_id
    fake_created_report_member.member_id = fake_member_id
    fake_created_report_member.community_id = fake_community_id

    mock_tm = Mock()
    mock_report_member_repo = Mock()
    mock_report_member_repo.get_by_reporter_member_reason.return_value = None
    mock_report_member_repo.save.return_value = fake_created_report_member

    service = ReportService(mock_tm)
    service._get_report = Mock(return_value=fake_report_base)
    service.report_member_repo = mock_report_member_repo

    # Act
    result = service.create_report_member(fake_report_member_create)

    # Assert
    service._get_report.assert_called_once_with(fake_report_id)
    mock_report_member_repo.get_by_reporter_member_reason.assert_called_once_with(
        fake_reporter_id, fake_member_id, fake_reason
    )
    mock_report_member_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, ReportMember)
    assert result.member_id == fake_member_id
    assert result.community_id == fake_community_id


@pytest.mark.unit
def test_create_report_post_service_success():
    """
    Tests the `create_report_post` method of ReportService.

    Scenario:
    - Given a valid report post creation request
    - When the service creates the report post and saves it to repository
    - Then it should return a ReportPostResponse with mapped data
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_post_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_reason = ReportReasonEnum.INAPPROPRIATE_CONTENT
    fake_description = 'Post contains false information'

    fake_report_post_create = ReportPostCreate(
        report_id=fake_report_id,
        post_id=fake_post_id,
        community_id=fake_community_id,
    )

    # Mock do report base
    fake_report_base = Mock(spec=Report)
    fake_report_base.id = fake_report_id
    fake_report_base.reporter_id = fake_reporter_id
    fake_report_base.type = ReportTypeEnum.POST_REPORT
    fake_report_base.reason = fake_reason
    fake_report_base.description = fake_description
    fake_report_base.created_at = datetime.now(timezone.utc)

    # Mock do report post criado
    fake_created_report_post = Mock(spec=ReportPost)
    fake_created_report_post.report_id = fake_report_id
    fake_created_report_post.post_id = fake_post_id
    fake_created_report_post.community_id = fake_community_id

    mock_tm = Mock()
    mock_report_post_repo = Mock()
    mock_report_post_repo.get_by_reporter_post_reason.return_value = None
    mock_report_post_repo.save.return_value = fake_created_report_post

    service = ReportService(mock_tm)
    service._get_report = Mock(return_value=fake_report_base)
    service.report_post_repo = mock_report_post_repo

    # Act
    result = service.create_report_post(fake_report_post_create)

    # Assert
    service._get_report.assert_called_once_with(fake_report_id)
    mock_report_post_repo.get_by_reporter_post_reason.assert_called_once_with(
        fake_reporter_id, fake_post_id, fake_reason
    )
    mock_report_post_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, ReportPost)
    assert result.post_id == fake_post_id
    assert result.community_id == fake_community_id


@pytest.mark.unit
def test_create_report_comment_service_success():
    """
    Tests the `create_report_comment` method of ReportService.

    Scenario:
    - Given a valid report comment creation request
    - When the service creates the report comment and saves it to repository
    - Then it should return a ReportCommentResponse with mapped data
    """
    # Arrange
    fake_report_id = str(uuid4())
    fake_comment_id = str(uuid4())
    fake_community_id = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_reason = ReportReasonEnum.HATE_SPEECH
    fake_description = 'Comment contains hate speech'

    fake_report_comment_create = ReportCommentCreate(
        report_id=fake_report_id,
        comment_id=fake_comment_id,
        community_id=fake_community_id,
    )

    # Mock do report base
    fake_report_base = Mock(spec=Report)
    fake_report_base.id = fake_report_id
    fake_report_base.reporter_id = fake_reporter_id
    fake_report_base.type = ReportTypeEnum.COMMENT_REPORT
    fake_report_base.reason = fake_reason
    fake_report_base.description = fake_description
    fake_report_base.created_at = datetime.now(timezone.utc)

    # Mock do report comment criado
    fake_created_report_comment = Mock(spec=ReportComment)
    fake_created_report_comment.report_id = fake_report_id
    fake_created_report_comment.comment_id = fake_comment_id
    fake_created_report_comment.community_id = fake_community_id

    mock_tm = Mock()
    mock_report_comment_repo = Mock()
    mock_report_comment_repo.get_by_reporter_comment_reason.return_value = None
    mock_report_comment_repo.save.return_value = fake_created_report_comment

    service = ReportService(mock_tm)
    service._get_report = Mock(return_value=fake_report_base)
    service.report_comment_repo = mock_report_comment_repo

    # Act
    result = service.create_report_comment(fake_report_comment_create)

    # Assert
    service._get_report.assert_called_once_with(fake_report_id)
    mock_report_comment_repo.get_by_reporter_comment_reason.assert_called_once_with(
        fake_reporter_id, fake_comment_id, fake_reason
    )
    mock_report_comment_repo.save.assert_called_once()
    assert result is not None
    assert isinstance(result, ReportComment)
    assert result.comment_id == fake_comment_id
    assert result.community_id == fake_community_id


@pytest.mark.unit
def test_delete_report_member_service_success():
    """
    Tests the `delete_report_member` method of ReportService.

    Scenario:
    - Given a valid report member ID
    - When the service deletes the report member
    - Then it should delete both the report and report member and return True
    """
    # Arrange
    fake_report_member_id = uuid4()
    fake_reporter_id = str(uuid4())

    fake_existing_report = Mock(spec=Report)
    fake_existing_report.id = str(fake_report_member_id)
    fake_existing_report.reporter_id = fake_reporter_id
    fake_existing_report.type = ReportTypeEnum.MEMBER_REPORT
    fake_existing_report.reason = ReportReasonEnum.HARASSMENT
    fake_existing_report.description = 'Member is harassing others'
    fake_existing_report.created_at = datetime.now(timezone.utc)

    fake_report_member = Mock(spec=ReportMember)
    fake_report_member.report_id = str(fake_report_member_id)

    mock_tm = Mock()
    mock_report_member_repo = Mock()
    mock_report_member_repo.get_by_id.return_value = fake_report_member
    mock_report_member_repo.delete.return_value = True

    service = ReportService(mock_tm)
    service._get_report = Mock(return_value=fake_existing_report)
    service.delete_report = Mock(return_value=True)
    service.report_member_repo = mock_report_member_repo

    # Act
    result = service.delete_report_member(fake_report_member_id)

    # Assert
    service._get_report.assert_called_once_with(fake_report_member_id)
    service.delete_report.assert_called_once_with(fake_report_member_id)
    mock_report_member_repo.get_by_id.assert_called_once_with(fake_report_member_id)
    mock_report_member_repo.delete.assert_called_once_with(fake_report_member)
    assert result is True


@pytest.mark.unit
def test_delete_report_post_service_success():
    """
    Tests the `delete_report_post` method of ReportService.

    Scenario:
    - Given a valid report post ID
    - When the service deletes the report post
    - Then it should delete both the report and report post and return True
    """
    # Arrange
    fake_report_post_id = uuid4()
    fake_reporter_id = str(uuid4())

    fake_existing_report = Mock(spec=Report)
    fake_existing_report.id = str(fake_report_post_id)
    fake_existing_report.reporter_id = fake_reporter_id
    fake_existing_report.type = ReportTypeEnum.POST_REPORT
    fake_existing_report.reason = ReportReasonEnum.SPAM
    fake_existing_report.description = 'Post contains spam'
    fake_existing_report.created_at = datetime.now(timezone.utc)

    fake_report_post = Mock(spec=ReportPost)
    fake_report_post.report_id = str(fake_report_post_id)

    mock_tm = Mock()
    mock_report_post_repo = Mock()
    mock_report_post_repo.get_by_id.return_value = fake_report_post
    mock_report_post_repo.delete.return_value = True

    service = ReportService(mock_tm)
    service._get_report = Mock(return_value=fake_existing_report)
    service.delete_report = Mock(return_value=True)
    service.report_post_repo = mock_report_post_repo

    # Act
    result = service.delete_report_post(fake_report_post_id)

    # Assert
    service._get_report.assert_called_once_with(fake_report_post_id)
    service.delete_report.assert_called_once_with(fake_report_post_id)
    mock_report_post_repo.get_by_id.assert_called_once_with(fake_report_post_id)
    mock_report_post_repo.delete.assert_called_once_with(fake_report_post)
    assert result is True


@pytest.mark.unit
def test_delete_report_comment_service_success():
    """
    Tests the `delete_report_comment` method of ReportService.

    Scenario:
    - Given a valid report comment ID
    - When the service deletes the report comment
    - Then it should delete both the report and report comment and return True
    """
    # Arrange
    fake_report_comment_id = uuid4()
    fake_reporter_id = str(uuid4())

    fake_existing_report = Mock(spec=Report)
    fake_existing_report.id = str(fake_report_comment_id)
    fake_existing_report.reporter_id = fake_reporter_id
    fake_existing_report.type = ReportTypeEnum.COMMENT_REPORT
    fake_existing_report.reason = ReportReasonEnum.HATE_SPEECH
    fake_existing_report.description = 'Comment contains hate speech'
    fake_existing_report.created_at = datetime.now(timezone.utc)

    fake_report_comment = Mock(spec=ReportComment)
    fake_report_comment.report_id = str(fake_report_comment_id)

    mock_tm = Mock()
    mock_report_comment_repo = Mock()
    mock_report_comment_repo.get_by_id.return_value = fake_report_comment
    mock_report_comment_repo.delete.return_value = True

    service = ReportService(mock_tm)
    service._get_report = Mock(return_value=fake_existing_report)
    service.delete_report = Mock(return_value=True)
    service.report_comment_repo = mock_report_comment_repo

    # Act
    result = service.delete_report_comment(fake_report_comment_id)

    # Assert
    service._get_report.assert_called_once_with(fake_report_comment_id)
    service.delete_report.assert_called_once_with(fake_report_comment_id)
    mock_report_comment_repo.get_by_id.assert_called_once_with(fake_report_comment_id)
    mock_report_comment_repo.delete.assert_called_once_with(fake_report_comment)
    assert result is True


@pytest.mark.unit
def test_list_member_reports_service_success():
    """
    Tests the `list_member_reports` method of ReportService.

    Scenario:
    - Given a valid member ID and pagination parameters
    - When the service lists reports for a member
    - Then it should return a paginated response with report data
    """
    # Arrange
    fake_member_id = uuid4()
    fake_report_id_1 = str(uuid4())
    fake_report_id_2 = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Mock dos report members
    fake_report_member_1 = Mock(spec=ReportMember)
    fake_report_member_1.report_id = fake_report_id_1
    fake_report_member_1.member_id = str(fake_member_id)

    fake_report_member_2 = Mock(spec=ReportMember)
    fake_report_member_2.report_id = fake_report_id_2
    fake_report_member_2.member_id = str(fake_member_id)

    # Mock do report response
    fake_report_response_1 = Mock()
    fake_report_response_1.id = fake_report_id_1
    fake_report_response_1.type = ReportTypeEnum.MEMBER_REPORT
    fake_report_response_1.reason = ReportReasonEnum.HARASSMENT
    fake_report_response_1.description = 'Member harassment report'

    fake_report_response_2 = Mock()
    fake_report_response_2.id = fake_report_id_2
    fake_report_response_2.type = ReportTypeEnum.MEMBER_REPORT
    fake_report_response_2.reason = ReportReasonEnum.DISCRIMINATION
    fake_report_response_2.description = 'Member discrimination report'

    mock_tm = Mock()
    mock_report_member_repo = Mock()
    mock_report_member_repo.list_reports_by_member.return_value = (
        [fake_report_member_1, fake_report_member_2],
        2,
    )

    service = ReportService(mock_tm)
    service.report_member_repo = mock_report_member_repo
    service.get_report = Mock(
        side_effect=[fake_report_response_1, fake_report_response_2]
    )

    # Act
    result = service.list_member_reports(fake_member_id, fake_pagination_params)

    # Assert
    mock_report_member_repo.list_reports_by_member.assert_called_once_with(
        fake_member_id, fake_pagination_params
    )
    assert service.get_report.call_count == 2
    service.get_report.assert_any_call(fake_report_id_1)
    service.get_report.assert_any_call(fake_report_id_2)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 2
    assert result.items[0].id == fake_report_id_1
    assert result.items[1].id == fake_report_id_2
    assert result.total == 2
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_post_reports_service_success():
    """
    Tests the `list_post_reports` method of ReportService.

    Scenario:
    - Given a valid post ID and pagination parameters
    - When the service lists reports for a post
    - Then it should return a paginated response with report data
    """
    # Arrange
    fake_post_id = uuid4()
    fake_report_id_1 = str(uuid4())
    fake_report_id_2 = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Mock dos report posts
    fake_report_post_1 = Mock(spec=ReportPost)
    fake_report_post_1.report_id = fake_report_id_1
    fake_report_post_1.post_id = str(fake_post_id)

    fake_report_post_2 = Mock(spec=ReportPost)
    fake_report_post_2.report_id = fake_report_id_2
    fake_report_post_2.post_id = str(fake_post_id)

    # Mock do report response
    fake_report_response_1 = Mock()
    fake_report_response_1.id = fake_report_id_1
    fake_report_response_1.type = ReportTypeEnum.POST_REPORT
    fake_report_response_1.reason = ReportReasonEnum.SPAM
    fake_report_response_1.description = 'Post spam report'

    fake_report_response_2 = Mock()
    fake_report_response_2.id = fake_report_id_2
    fake_report_response_2.type = ReportTypeEnum.POST_REPORT
    fake_report_response_2.reason = ReportReasonEnum.INAPPROPRIATE_CONTENT
    fake_report_response_2.description = 'Post inappropriate content report'

    mock_tm = Mock()
    mock_report_post_repo = Mock()
    mock_report_post_repo.list_reports_by_post.return_value = (
        [fake_report_post_1, fake_report_post_2],
        2,
    )

    service = ReportService(mock_tm)
    service.report_post_repo = mock_report_post_repo
    service.get_report = Mock(
        side_effect=[fake_report_response_1, fake_report_response_2]
    )

    # Act
    result = service.list_post_reports(fake_post_id, fake_pagination_params)

    # Assert
    mock_report_post_repo.list_reports_by_post.assert_called_once_with(
        fake_post_id, fake_pagination_params
    )
    assert service.get_report.call_count == 2
    service.get_report.assert_any_call(fake_report_id_1)
    service.get_report.assert_any_call(fake_report_id_2)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 2
    assert result.items[0].id == fake_report_id_1
    assert result.items[1].id == fake_report_id_2
    assert result.total == 2
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_comment_reports_service_success():
    """
    Tests the `list_comment_reports` method of ReportService.

    Scenario:
    - Given a valid comment ID and pagination parameters
    - When the service lists reports for a comment
    - Then it should return a paginated response with report data
    """
    # Arrange
    fake_comment_id = uuid4()
    fake_report_id_1 = str(uuid4())
    fake_report_id_2 = str(uuid4())
    fake_reporter_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Mock dos report comments
    fake_report_comment_1 = Mock(spec=ReportComment)
    fake_report_comment_1.report_id = fake_report_id_1
    fake_report_comment_1.comment_id = str(fake_comment_id)

    fake_report_comment_2 = Mock(spec=ReportComment)
    fake_report_comment_2.report_id = fake_report_id_2
    fake_report_comment_2.comment_id = str(fake_comment_id)

    # Mock do report response
    fake_report_response_1 = Mock()
    fake_report_response_1.id = fake_report_id_1
    fake_report_response_1.type = ReportTypeEnum.COMMENT_REPORT
    fake_report_response_1.reason = ReportReasonEnum.HATE_SPEECH
    fake_report_response_1.description = 'Comment hate speech report'

    fake_report_response_2 = Mock()
    fake_report_response_2.id = fake_report_id_2
    fake_report_response_2.type = ReportTypeEnum.COMMENT_REPORT
    fake_report_response_2.reason = ReportReasonEnum.HARASSMENT
    fake_report_response_2.description = 'Comment harassment report'

    mock_tm = Mock()
    mock_report_comment_repo = Mock()
    mock_report_comment_repo.list_reports_by_comment.return_value = (
        [fake_report_comment_1, fake_report_comment_2],
        2,
    )

    service = ReportService(mock_tm)
    service.report_comment_repo = mock_report_comment_repo
    service.get_report = Mock(
        side_effect=[fake_report_response_1, fake_report_response_2]
    )

    # Act
    result = service.list_comment_reports(fake_comment_id, fake_pagination_params)

    # Assert
    mock_report_comment_repo.list_reports_by_comment.assert_called_once_with(
        fake_comment_id, fake_pagination_params
    )
    assert service.get_report.call_count == 2
    service.get_report.assert_any_call(fake_report_id_1)
    service.get_report.assert_any_call(fake_report_id_2)
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 2
    assert result.items[0].id == fake_report_id_1
    assert result.items[1].id == fake_report_id_2
    assert result.total == 2
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_member_brief_reports_service_success():
    """
    Tests the `list_member_brief_reports` method of ReportService.

    Scenario:
    - Given a valid community ID and pagination parameters
    - When the service lists brief reports for members in a community
    - Then it should return a paginated response with member brief report data
    """
    # Arrange
    fake_community_id = uuid4()
    fake_member_id_1 = str(uuid4())
    fake_member_id_2 = str(uuid4())
    fake_user_id_1 = str(uuid4())
    fake_user_id_2 = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Mock dos members
    fake_member_1 = Mock(spec=CommunityMember)
    fake_member_1.id = fake_member_id_1
    fake_member_1.user_id = fake_user_id_1
    fake_member_1.name = 'Member 1'
    fake_member_1.role = CommunityMemberRoleEnum.MEMBER
    fake_member_1.reputation = 50
    fake_member_1.reputation_level = 'helper'
    fake_member_1.entered_in = datetime.now(timezone.utc)
    fake_member_1.popularity = 100.0

    fake_member_2 = Mock(spec=CommunityMember)
    fake_member_2.id = fake_member_id_2
    fake_member_2.user_id = fake_user_id_2
    fake_member_2.name = 'Member 2'
    fake_member_2.role = CommunityMemberRoleEnum.MEMBER
    fake_member_2.reputation = 30
    fake_member_2.reputation_level = 'under_observation'
    fake_member_2.entered_in = datetime.now(timezone.utc)
    fake_member_2.popularity = 50.0

    # Mock dos users
    fake_user_1 = Mock(spec=User)
    fake_user_1.name = 'User 1'
    fake_user_1.profile_image_url = 'https://example.com/user1.jpg'

    fake_user_2 = Mock(spec=User)
    fake_user_2.name = 'User 2'
    fake_user_2.profile_image_url = 'https://example.com/user2.jpg'

    # Mock dos dados do repositório - retorna tuplas (member_id, reason, reports_count)
    # Cada tupla representa uma combinação única de (member_id, reason)
    fake_report_members = [
        (fake_member_id_1, ReportReasonEnum.HARASSMENT, 2),
        (fake_member_id_1, ReportReasonEnum.DISCRIMINATION, 1),
        (fake_member_id_2, ReportReasonEnum.SPAM, 1),
    ]

    mock_tm = Mock()
    mock_report_member_repo = Mock()
    mock_report_member_repo.list_members_by_reason_and_count.return_value = (
        fake_report_members
    )

    mock_community_service = Mock()
    mock_community_service.get_member.side_effect = [
        fake_member_1,
        fake_member_1,
        fake_member_2,
    ]

    mock_user_service = Mock()
    mock_user_service.get_user.side_effect = [fake_user_1, fake_user_1, fake_user_2]

    service = ReportService(mock_tm)
    service.report_member_repo = mock_report_member_repo
    service.community_service = mock_community_service
    service.user_service = mock_user_service

    # Act
    result = service.list_member_brief_reports(fake_community_id, fake_pagination_params)

    # Assert
    mock_report_member_repo.list_members_by_reason_and_count.assert_called_once_with(
        fake_community_id
    )
    assert mock_community_service.get_member.call_count == 3
    assert mock_user_service.get_user.call_count == 3
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 3
    assert isinstance(result.items[0], MemberBriefReport)
    assert result.items[0].member.id == fake_member_id_1
    assert result.items[0].reports_count == 2
    assert result.items[0].reason == ReportReasonEnum.HARASSMENT
    assert result.items[0].member_reputation == 50
    assert result.items[1].member.id == fake_member_id_1
    assert result.items[1].reports_count == 1
    assert result.items[1].reason == ReportReasonEnum.DISCRIMINATION
    assert result.items[2].member.id == fake_member_id_2
    assert result.items[2].reports_count == 1
    assert result.items[2].reason == ReportReasonEnum.SPAM
    assert result.total == 3
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_post_brief_reports_service_success():
    """
    Tests the `list_post_brief_reports` method of ReportService.

    Scenario:
    - Given a valid community ID and pagination parameters
    - When the service lists brief reports for posts in a community
    - Then it should return a paginated response with post brief report data
    """
    # Arrange
    fake_community_id = uuid4()
    fake_post_id_1 = str(uuid4())
    fake_post_id_2 = str(uuid4())
    fake_member_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Mock do member e user
    fake_member = Mock(spec=CommunityMember)
    fake_member.id = fake_member_id
    fake_member.user_id = fake_user_id
    fake_member.role = CommunityMemberRoleEnum.MODERATOR

    fake_user = Mock(spec=User)
    fake_user.name = 'Post Author'
    fake_user.profile_image_url = 'https://example.com/author.jpg'

    # Mock dos posts
    fake_post_1 = Mock()
    fake_post_1.user = Mock()
    fake_post_1.user.id = fake_member_id
    fake_post_1.title = 'Post Title 1'
    fake_post_1.content = 'Post content 1'
    fake_post_1.image_url = 'https://example.com/post1.jpg'
    fake_post_1.report_count = 5
    fake_post_1.likes_count = 10
    fake_post_1.comments_count = 3
    fake_post_1.created_at = datetime.now(timezone.utc)

    fake_post_2 = Mock()
    fake_post_2.user = Mock()
    fake_post_2.user.id = fake_member_id
    fake_post_2.title = 'Post Title 2'
    fake_post_2.content = 'Post content 2'
    fake_post_2.image_url = None
    fake_post_2.report_count = 2
    fake_post_2.likes_count = 5
    fake_post_2.comments_count = 1
    fake_post_2.created_at = datetime.now(timezone.utc)

    # Mock dos dados do repositório - retorna tuplas (post_id, reason, reports_count)
    # Cada tupla representa uma combinação única de (post_id, reason)
    fake_report_posts = [
        (fake_post_id_1, ReportReasonEnum.SPAM, 3),
        (fake_post_id_1, ReportReasonEnum.INAPPROPRIATE_CONTENT, 2),
        (fake_post_id_2, ReportReasonEnum.HATE_SPEECH, 2),
    ]

    mock_tm = Mock()
    mock_report_post_repo = Mock()
    mock_report_post_repo.list_posts_by_reason_and_count.return_value = fake_report_posts

    mock_post_service = Mock()
    mock_post_service.get_post.side_effect = [fake_post_1, fake_post_1, fake_post_2]

    mock_community_service = Mock()
    mock_community_service.get_member_association.return_value = fake_member

    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user

    service = ReportService(mock_tm)
    service.report_post_repo = mock_report_post_repo
    service.post_service = mock_post_service
    service.community_service = mock_community_service
    service.user_service = mock_user_service

    # Act
    result = service.list_post_brief_reports(fake_community_id, fake_pagination_params)

    # Assert
    mock_report_post_repo.list_posts_by_reason_and_count.assert_called_once_with(
        fake_community_id
    )
    assert mock_post_service.get_post.call_count == 3
    assert mock_community_service.get_member_association.call_count == 3
    assert mock_user_service.get_user.call_count == 3
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 3
    assert isinstance(result.items[0], PostBriefReport)
    assert result.items[0].post_id == fake_post_id_1
    assert result.items[0].title == 'Post Title 1'
    assert result.items[0].reason == ReportReasonEnum.SPAM
    assert result.items[0].report_count == 3
    assert result.items[0].likes_count == 10
    assert result.items[1].post_id == fake_post_id_1
    assert result.items[1].title == 'Post Title 1'
    assert result.items[1].reason == ReportReasonEnum.INAPPROPRIATE_CONTENT
    assert result.items[1].report_count == 2
    assert result.items[2].post_id == fake_post_id_2
    assert result.items[2].title == 'Post Title 2'
    assert result.items[2].reason == ReportReasonEnum.HATE_SPEECH
    assert result.items[2].report_count == 2
    assert result.total == 3
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10


@pytest.mark.unit
def test_list_comment_brief_reports_service_success():
    """
    Tests the `list_comment_brief_reports` method of ReportService.

    Scenario:
    - Given a valid community ID and pagination parameters
    - When the service lists brief reports for comments in a community
    - Then it should return a paginated response with comment brief report data
    """
    # Arrange
    fake_community_id = uuid4()
    fake_comment_id_1 = str(uuid4())
    fake_comment_id_2 = str(uuid4())
    fake_member_id = str(uuid4())
    fake_user_id = str(uuid4())
    fake_pagination_params = PaginationSearchParams(offset=0, limit=10)

    # Mock do member e user
    fake_member = Mock(spec=CommunityMember)
    fake_member.id = fake_member_id
    fake_member.user_id = fake_user_id
    fake_member.role = CommunityMemberRoleEnum.MODERATOR

    fake_user = Mock(spec=User)
    fake_user.name = 'Comment Author'
    fake_user.profile_image_url = 'https://example.com/author.jpg'

    # Mock dos comments
    fake_comment_1 = Mock()
    fake_comment_1.member = Mock()
    fake_comment_1.member.id = fake_member_id
    fake_comment_1.member.name = 'Comment Author'
    fake_comment_1.member.profile_image_url = 'https://example.com/author.jpg'
    fake_comment_1.member.member_role = CommunityMemberRoleEnum.MODERATOR
    fake_comment_1.content = 'Comment content 1'
    fake_comment_1.report_count = 3
    fake_comment_1.likes_count = 7
    fake_comment_1.comments_count = 2
    fake_comment_1.created_at = datetime.now(timezone.utc)

    fake_comment_2 = Mock()
    fake_comment_2.member = Mock()
    fake_comment_2.member.id = fake_member_id
    fake_comment_2.member.name = 'Comment Author'
    fake_comment_2.member.profile_image_url = 'https://example.com/author.jpg'
    fake_comment_2.member.member_role = CommunityMemberRoleEnum.MODERATOR
    fake_comment_2.content = 'Comment content 2'
    fake_comment_2.report_count = 1
    fake_comment_2.likes_count = 4
    fake_comment_2.comments_count = 0
    fake_comment_2.created_at = datetime.now(timezone.utc)

    # Mock dos dados do repositório - retorna tuplas (comment_id, reason, reports_count)
    # Cada tupla representa uma combinação única de (comment_id, reason)
    fake_report_comments = [
        (fake_comment_id_1, ReportReasonEnum.HATE_SPEECH, 2),
        (fake_comment_id_1, ReportReasonEnum.HARASSMENT, 1),
        (fake_comment_id_2, ReportReasonEnum.SPAM, 1),
    ]

    mock_tm = Mock()
    mock_report_comment_repo = Mock()
    mock_report_comment_repo.list_comments_by_reason_and_count.return_value = (
        fake_report_comments
    )

    mock_comment_service = Mock()
    mock_comment_service.get_comment.side_effect = [
        fake_comment_1,
        fake_comment_1,
        fake_comment_2,
    ]

    mock_community_service = Mock()
    mock_community_service.get_member_association.return_value = fake_member

    mock_user_service = Mock()
    mock_user_service.get_user.return_value = fake_user

    service = ReportService(mock_tm)
    service.report_comment_repo = mock_report_comment_repo
    service.comment_service = mock_comment_service
    service.community_service = mock_community_service
    service.user_service = mock_user_service

    # Act
    result = service.list_comment_brief_reports(
        fake_community_id, fake_pagination_params
    )

    # Assert
    mock_report_comment_repo.list_comments_by_reason_and_count.assert_called_once_with(
        fake_community_id
    )
    assert mock_comment_service.get_comment.call_count == 3
    # Não precisamos mais chamar get_member_association nem get_user
    # pois as informações já estão no comment.member
    assert result is not None
    assert result.items is not None
    assert len(result.items) == 3
    assert isinstance(result.items[0], CommentBriefReport)
    assert result.items[0].comment_id == fake_comment_id_1
    assert result.items[0].content == 'Comment content 1'
    assert result.items[0].reason == ReportReasonEnum.HATE_SPEECH
    assert result.items[0].report_count == 2
    assert result.items[0].likes_count == 7
    assert result.items[1].comment_id == fake_comment_id_1
    assert result.items[1].content == 'Comment content 1'
    assert result.items[1].reason == ReportReasonEnum.HARASSMENT
    assert result.items[1].report_count == 1
    assert result.items[2].comment_id == fake_comment_id_2
    assert result.items[2].content == 'Comment content 2'
    assert result.items[2].reason == ReportReasonEnum.SPAM
    assert result.items[2].report_count == 1
    assert result.total == 3
    assert result.has_more == False
    assert result.current_offset == 0
    assert result.current_limit == 10
