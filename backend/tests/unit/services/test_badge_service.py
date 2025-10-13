import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime

from app.api.badges.exceptions import (
    BadgeAlreadyExistsError,
    BadgeNotFoundError,
    MemberAlreadyHasBadgeError,
    MemberBadgeNotFoundError,
    CannotDeleteSystemBadgeError,
)
from app.api.badges.schema import (
    BadgeUpdate,
    MemberBadgeCreate,
    BadgeResponse,
    BadgeCreate,
)
from app.api.badges.service import BadgeService
from app.api.badges.model import Badge, MemberBadge
from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.utils.schema import PaginationSearchParams, PaginationResponse


@pytest.mark.unit
def test_create_badge_service_success():
    """
    Tests the `create_badge` method of BadgeService.

    Scenario:
    - Given a valid badge creation request for a name that doesn't exist in the community
    - When the service creates the badge and saves it to the repository
    - Then it should return the created badge
    """
    # Arrange
    fake_community_id = uuid4()
    # Criamos um objeto BadgeCreate a partir dos dados
    fake_badge_create_obj = BadgeCreate(
        name='Super Badge',
        description='A really cool badge',
        community_id=fake_community_id,
        image_url='http://example.com/img.png',
    )

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_community_service = Mock()

    # Community exists, badge name is unique
    mock_community_service.get_community.return_value = Mock()
    mock_badge_repo.get_by_name_and_community.return_value = None

    fake_created_badge = Mock(spec=Badge)
    fake_created_badge.id = uuid4()
    # Atribuímos os valores do objeto de criação ao mock de resposta
    for key, value in fake_badge_create_obj.model_dump().items():
        setattr(fake_created_badge, key, value)

    mock_badge_repo.save.return_value = fake_created_badge

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo
    service.community_service = mock_community_service

    # Act
    # Passamos o OBJETO BadgeCreate, não mais o dicionário
    result = service.create_badge(fake_badge_create_obj)

    # Assert
    mock_community_service.get_community.assert_called_once_with(fake_community_id)
    mock_badge_repo.get_by_name_and_community.assert_called_once_with(
        fake_badge_create_obj.name, fake_community_id
    )
    mock_badge_repo.save.assert_called_once()
    assert result is not None
    assert result.id == fake_created_badge.id
    assert result.name == fake_badge_create_obj.name


@pytest.mark.unit
def test_get_badge_service_success():
    """
    Tests the `get_badge` method of BadgeService.

    Scenario:
    - Given a valid badge ID
    - When the service retrieves the badge from the repository
    - Then it should return the expected badge
    """
    # Arrange
    fake_badge_id = uuid4()

    fake_badge = Mock(spec=Badge)
    fake_badge.id = fake_badge_id
    fake_badge.name = 'Test Badge'
    fake_badge.description = 'Test Description'
    fake_badge.community_id = uuid4()

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.get_by_id.return_value = fake_badge

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act
    result = service.get_badge(fake_badge_id)

    # Assert
    mock_badge_repo.get_by_id.assert_called_once_with(fake_badge_id)
    assert result is not None
    assert result.id == fake_badge_id
    assert result.name == 'Test Badge'


@pytest.mark.unit
def test_get_badge_not_found_service():
    """
    Tests the `get_badge` method of BadgeService when badge is not found.

    Scenario:
    - Given an invalid badge ID
    - When the service attempts to retrieve the badge
    - Then it should raise a BadgeNotFoundError
    """
    # Arrange
    fake_badge_id = uuid4()

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.get_by_id.return_value = None

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act & Assert
    with pytest.raises(BadgeNotFoundError):
        service.get_badge(fake_badge_id)
    mock_badge_repo.get_by_id.assert_called_once_with(fake_badge_id)


@pytest.mark.unit
def test_update_badge_service_success():
    """
    Tests the `update_badge` method of BadgeService.

    Scenario:
    - Given a valid badge ID and update data with a new unique name
    - When the service updates the badge
    - Then it should return the updated badge
    """
    # Arrange
    fake_badge_id = uuid4()
    fake_community_id = uuid4()

    fake_update_data = BadgeUpdate(name='New Name', description='New Description')

    fake_existing_badge = Mock(spec=Badge)
    fake_existing_badge.id = fake_badge_id
    fake_existing_badge.community_id = fake_community_id
    fake_existing_badge.name = 'Old Name'
    fake_existing_badge.description = 'Old Description'

    fake_saved_badge = Mock(spec=Badge)
    fake_saved_badge.id = fake_badge_id
    fake_saved_badge.community_id = fake_community_id
    fake_saved_badge.name = 'New Name'
    fake_saved_badge.description = 'New Description'

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.get_by_id.return_value = fake_existing_badge
    mock_badge_repo.get_by_name_and_community.return_value = None  # No name conflict
    mock_badge_repo.save.return_value = fake_saved_badge

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act
    result = service.update_badge(fake_badge_id, fake_update_data)

    # Assert
    mock_badge_repo.get_by_id.assert_called_once_with(fake_badge_id)
    mock_badge_repo.get_by_name_and_community.assert_called_once_with(
        'New Name', fake_community_id
    )
    mock_badge_repo.save.assert_called_once_with(fake_existing_badge)
    assert fake_existing_badge.name == 'New Name'  # Check if object was modified
    assert fake_existing_badge.description == 'New Description'
    assert result.name == 'New Name'


@pytest.mark.unit
def test_update_badge_name_conflict_service():
    """
    Tests the `update_badge` method when a name conflict occurs.

    Scenario:
    - Given a valid badge ID and update data with a name that already exists
    - When the service attempts to update the badge
    - Then it should raise a BadgeAlreadyExistsError
    """
    # Arrange
    fake_badge_id = uuid4()
    fake_community_id = uuid4()

    fake_update_data = BadgeUpdate(name='Existing Name')

    fake_existing_badge = Mock(spec=Badge)
    fake_existing_badge.id = fake_badge_id
    fake_existing_badge.community_id = fake_community_id
    fake_existing_badge.name = 'Old Name'

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.get_by_id.return_value = fake_existing_badge
    # Name conflict found
    mock_badge_repo.get_by_name_and_community.return_value = Mock(spec=Badge)

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act & Assert
    with pytest.raises(BadgeAlreadyExistsError):
        service.update_badge(fake_badge_id, fake_update_data)


@pytest.mark.unit
def test_delete_badge_service_success():
    """
    Tests the `delete_badge` method of BadgeService.

    Scenario:
    - Given a valid, non-system badge ID
    - When the service deletes the badge from the repository
    - Then it should return True
    """
    # Arrange
    fake_badge_id = uuid4()

    fake_badge_to_delete = Mock(spec=Badge)
    fake_badge_to_delete.id = fake_badge_id
    fake_badge_to_delete.name = 'Custom Badge'  # Not a system badge

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.get_by_id.return_value = fake_badge_to_delete
    mock_badge_repo.delete.return_value = True

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act
    result = service.delete_badge(fake_badge_id)

    # Assert
    mock_badge_repo.get_by_id.assert_called_once_with(fake_badge_id)
    mock_badge_repo.delete.assert_called_once_with(fake_badge_to_delete)
    assert result is True


@pytest.mark.unit
def test_delete_system_badge_service_fail():
    """
    Tests the `delete_badge` method of BadgeService for a system badge.

    Scenario:
    - Given a system badge ID
    - When the service attempts to delete the badge
    - Then it should raise a CannotDeleteSystemBadgeError
    """
    # Arrange
    fake_badge_id = uuid4()

    fake_system_badge = Mock(spec=Badge)
    fake_system_badge.id = fake_badge_id
    fake_system_badge.name = 'Líder'  # A system badge

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.get_by_id.return_value = fake_system_badge

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act & Assert
    with pytest.raises(CannotDeleteSystemBadgeError):
        service.delete_badge(fake_badge_id)


@pytest.mark.unit
def test_list_badges_service_success():
    """
    Tests the `list_badges` method of BadgeService.

    Scenario:
    - Given a valid community ID and pagination parameters
    - When the service lists badges from the repository
    - Then it should return a paginated response with the expected badges
    """
    # Arrange
    fake_community_id = uuid4()
    fake_params = PaginationSearchParams(offset=0, limit=10)

    # Criamos mock_badge_1 e preenchemos com dados válidos
    mock_badge_1 = Mock(spec=Badge)
    mock_badge_1.id = uuid4()
    mock_badge_1.community_id = fake_community_id
    mock_badge_1.name = 'Badge 1'
    mock_badge_1.description = 'Description 1'
    mock_badge_1.image_url = 'http://example.com/1.png'
    mock_badge_1.created_at = datetime.now()
    mock_badge_1.updated_at = datetime.now()

    # Criamos mock_badge_2 e preenchemos com dados válidos
    mock_badge_2 = Mock(spec=Badge)
    mock_badge_2.id = uuid4()
    mock_badge_2.community_id = fake_community_id
    mock_badge_2.name = 'Badge 2'
    mock_badge_2.description = 'Description 2'
    mock_badge_2.image_url = 'http://example.com/2.png'
    mock_badge_2.created_at = datetime.now()
    mock_badge_2.updated_at = datetime.now()

    fake_badges_list = [mock_badge_1, mock_badge_2]

    mock_tm = Mock()
    mock_badge_repo = Mock()
    mock_badge_repo.list_all.return_value = (fake_badges_list, 2)

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo

    # Act
    result = service.list_badges(fake_community_id, fake_params)

    # Assert
    mock_badge_repo.list_all.assert_called_once_with(fake_community_id, fake_params)
    assert isinstance(result, PaginationResponse)
    assert len(result.items) == 2
    assert isinstance(result.items[0], BadgeResponse)
    assert result.total == 2
    assert not result.has_more
    assert result.items[0].name == 'Badge 1'
    assert result.items[1].name == 'Badge 2'


@pytest.mark.unit
def test_assign_badge_to_user_service_success():
    """
    Tests the `assign_badge_to_user` method of BadgeService.

    Scenario:
    - Given a valid member and badge ID where the member does not have the badge yet
    - When the service assigns the badge to the member
    - Then it should return the created MemberBadge assignment
    """
    # Arrange
    fake_member_id = uuid4()
    fake_badge_id = uuid4()
    fake_assignment_data = MemberBadgeCreate(
        member_id=fake_member_id, badge_id=fake_badge_id
    )

    fake_saved_assignment = Mock(spec=MemberBadge)
    fake_saved_assignment.member_id = fake_member_id
    fake_saved_assignment.badge_id = fake_badge_id
    fake_saved_assignment.achieved_at = datetime.now()

    mock_tm = Mock()
    mock_member_badge_repo = Mock()
    mock_badge_repo = Mock()
    mock_community_service = Mock()

    # Pre-conditions are met
    mock_community_service.get_member.return_value = Mock()
    mock_badge_repo.get_by_id.return_value = Mock(spec=Badge)
    mock_member_badge_repo.get_by_member_badge.return_value = (
        None  # No existing assignment
    )

    mock_member_badge_repo.save.return_value = fake_saved_assignment

    service = BadgeService(mock_tm)
    service.badge_repo = mock_badge_repo
    service.member_badge_repo = mock_member_badge_repo
    service.community_service = mock_community_service

    # Act
    result = service.assign_badge_to_user(fake_assignment_data)

    # Assert
    mock_community_service.get_member.assert_called_once_with(fake_member_id)
    mock_badge_repo.get_by_id.assert_called_once_with(fake_badge_id)
    mock_member_badge_repo.get_by_member_badge.assert_called_once_with(
        member_id=fake_member_id, badge_id=fake_badge_id
    )
    mock_member_badge_repo.save.assert_called_once()
    assert result.member_id == fake_member_id
    assert result.badge_id == fake_badge_id


@pytest.mark.unit
def test_assign_badge_user_already_has_service():
    """
    Tests assigning a badge that the user already has.

    Scenario:
    - Given a member and badge ID where the assignment already exists
    - When the service attempts to assign the badge again
    - Then it should raise MemberAlreadyHasBadgeError
    """
    # Arrange
    fake_member_id = uuid4()
    fake_badge_id = uuid4()
    fake_assignment_data = MemberBadgeCreate(
        member_id=fake_member_id, badge_id=fake_badge_id
    )

    mock_tm = Mock()
    mock_member_badge_repo = Mock()

    # Pre-conditions
    mock_member_badge_repo.get_by_member_badge.return_value = Mock(
        spec=MemberBadge
    )  # Assignment exists

    service = BadgeService(mock_tm)
    service.member_badge_repo = mock_member_badge_repo
    # Mocking other dependencies to isolate the logic
    service.community_service = Mock()
    service.badge_repo = Mock()

    # Act & Assert
    with pytest.raises(MemberAlreadyHasBadgeError):
        service.assign_badge_to_user(fake_assignment_data)


@pytest.mark.unit
def test_assign_badge_user_not_found_service():
    """
    Tests assigning a badge to a non-existent member.

    Scenario:
    - Given an invalid member ID and a valid badge ID
    - When the service attempts to assign the badge
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    fake_badge_id = uuid4()
    fake_assignment_data = MemberBadgeCreate(member_id=uuid4(), badge_id=fake_badge_id)

    mock_tm = Mock()
    mock_community_service = Mock()
    # Member not found
    mock_community_service.get_member.side_effect = CommunityMemberNotFoundError

    service = BadgeService(mock_tm)
    service.community_service = mock_community_service

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service.assign_badge_to_user(fake_assignment_data)


@pytest.mark.unit
def test_revoke_badge_from_user_service_success():
    """
    Tests the `revoke_badge_from_user` method of BadgeService.

    Scenario:
    - Given a member and badge ID for an existing assignment
    - When the service revokes the badge
    - Then it should return True
    """
    # Arrange
    fake_member_id = uuid4()
    fake_badge_id = uuid4()

    fake_existing_assignment = Mock(spec=MemberBadge)

    mock_tm = Mock()
    mock_member_badge_repo = Mock()
    mock_member_badge_repo.get_by_member_badge.return_value = fake_existing_assignment
    mock_member_badge_repo.delete.return_value = True

    service = BadgeService(mock_tm)
    service.member_badge_repo = mock_member_badge_repo

    # Act
    result = service.revoke_badge_from_user(fake_member_id, fake_badge_id)

    # Assert
    mock_member_badge_repo.get_by_member_badge.assert_called_once_with(
        member_id=fake_member_id, badge_id=fake_badge_id
    )
    mock_member_badge_repo.delete.assert_called_once_with(fake_existing_assignment)
    assert result is True


@pytest.mark.unit
def test_revoke_badge_not_assigned_service():
    """
    Tests revoking a badge that has not been assigned to the user.

    Scenario:
    - Given a member and badge ID where no assignment exists
    - When the service attempts to revoke the badge
    - Then it should raise MemberBadgeNotFoundError
    """
    # Arrange
    fake_member_id = uuid4()
    fake_badge_id = uuid4()

    mock_tm = Mock()
    mock_member_badge_repo = Mock()
    mock_member_badge_repo.get_by_member_badge.return_value = (
        None  # Assignment does not exist
    )

    service = BadgeService(mock_tm)
    service.member_badge_repo = mock_member_badge_repo

    # Act & Assert
    with pytest.raises(MemberBadgeNotFoundError):
        service.revoke_badge_from_user(fake_member_id, fake_badge_id)


@pytest.mark.unit
def test_list_badges_for_user_service_success():
    """
    Tests the `list_badges_for_member` method of BadgeService.

    Scenario:
    - Given a valid member ID
    - When the service retrieves the member's badges via a direct query
    - Then it should return a list of their badges
    """
    # Arrange
    fake_member_id = uuid4()

    fake_badge_1 = Mock(spec=Badge)
    fake_badge_2 = Mock(spec=Badge)
    expected_badges = [fake_badge_1, fake_badge_2]

    mock_tm = Mock()
    mock_community_service = Mock()
    mock_badge_repo = Mock()

    # O serviço ainda valida se o membro existe
    mock_community_service.get_member.return_value = Mock()

    # >> AQUI ESTÁ A CORREÇÃO <<
    # Simulamos a nova cadeia de chamadas de consulta para retornar a lista esperada
    mock_badge_repo.session.query.return_value.join.return_value.filter.return_value.all.return_value = expected_badges

    service = BadgeService(mock_tm)
    # Atribuímos os mocks à instância do serviço
    service.community_service = mock_community_service
    service.badge_repo = mock_badge_repo

    # Act
    result = service.list_badges_for_member(fake_member_id)

    # Assert
    mock_community_service.get_member.assert_called_once_with(fake_member_id)
    # Verificamos se a consulta foi chamada
    mock_badge_repo.session.query.assert_called_once_with(Badge)
    assert result is not None
    assert len(result) == 2
    assert result == expected_badges
