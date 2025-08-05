import uuid

import pytest

from app.api.badges.exceptions import (
    BadgeAlreadyExistsError,
    BadgeNotFoundError,
    MemberAlreadyHasBadgeError,
    MemberBadgeNotFoundError,
)
from app.api.badges.schema import BadgeUpdate, MemberBadgeCreate
from app.api.badges.service import BadgeService
from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.utils.schema import PaginationSearchParams


def test_get_badge_service(transaction_manager, badge_on_db):
    service = BadgeService(transaction_manager)
    badge = service.get_badge(badge_on_db.id)
    assert badge is not None
    assert badge.id == badge_on_db.id
    assert badge.name == badge_on_db.name
    assert badge.description == badge_on_db.description
    assert badge.community_id == badge_on_db.community_id


def test_get_badge_not_found_service(transaction_manager):
    service = BadgeService(transaction_manager)
    with pytest.raises(BadgeNotFoundError):
        service.get_badge(uuid.uuid4())


def test_update_badge_service(transaction_manager, badge_on_db):
    service = BadgeService(transaction_manager)
    badge = service.update_badge(
        badge_on_db.id, BadgeUpdate(name='New Name', description='New Description')
    )
    assert badge is not None
    assert badge.id == badge_on_db.id
    assert badge.name == 'New Name'
    assert badge.description == 'New Description'
    assert badge.community_id == badge_on_db.community_id


def test_update_badge_name_conflict_service(
    transaction_manager, badge_on_db, secondary_badge_on_db
):
    service = BadgeService(transaction_manager)
    with pytest.raises(BadgeAlreadyExistsError):
        service.update_badge(
            badge_on_db.id, BadgeUpdate(name=secondary_badge_on_db.name)
        )


def test_delete_badge_service(transaction_manager, badge_on_db):
    service = BadgeService(transaction_manager)
    result = service.delete_badge(badge_on_db.id)
    assert result is True
    with pytest.raises(BadgeNotFoundError):
        service.get_badge(badge_on_db.id)


def test_list_badges_service(
    transaction_manager, community_on_db, badge_on_db, secondary_badge_on_db
):
    service = BadgeService(transaction_manager)
    params = PaginationSearchParams(offset=0, limit=10)
    badges = service.list_badges(community_on_db.id, params)
    assert len(badges.items) == 2
    assert badges.items[0].id == badge_on_db.id
    assert badges.items[1].id == secondary_badge_on_db.id


def test_assign_badge_to_user_service(
    transaction_manager, community_member_on_db, badge_on_db
):
    service = BadgeService(transaction_manager)
    member_badge = MemberBadgeCreate(
        member_id=community_member_on_db.id,
        badge_id=badge_on_db.id,
        community_id=community_member_on_db.community_id,
    )
    assignment = service.assign_badge_to_user(member_badge)
    assert assignment is not None
    assert assignment.member_id == community_member_on_db.id
    assert assignment.badge_id == badge_on_db.id


def test_assign_badge_user_already_has_service(
    transaction_manager, member_badge_assignment_on_db
):
    service = BadgeService(transaction_manager)
    member_badge = MemberBadgeCreate(
        member_id=member_badge_assignment_on_db.member_id,
        badge_id=member_badge_assignment_on_db.badge_id,
    )
    with pytest.raises(MemberAlreadyHasBadgeError):
        service.assign_badge_to_user(member_badge)


def test_assign_badge_user_not_found_service(
    transaction_manager, community_member_on_db, badge_on_db
):
    service = BadgeService(transaction_manager)
    member_badge = MemberBadgeCreate(
        member_id=uuid.uuid4(),
        badge_id=badge_on_db.id,
    )
    with pytest.raises(CommunityMemberNotFoundError):
        service.assign_badge_to_user(member_badge)


def test_assign_badge_not_found_service(
    transaction_manager, community_member_on_db, badge_on_db
):
    service = BadgeService(transaction_manager)
    member_badge = MemberBadgeCreate(
        member_id=community_member_on_db.id,
        badge_id=uuid.uuid4(),
    )
    with pytest.raises(BadgeNotFoundError):
        service.assign_badge_to_user(member_badge)


def test_revoke_badge_from_user_service(
    transaction_manager, member_badge_assignment_on_db
):
    service = BadgeService(transaction_manager)
    result = service.revoke_badge_from_user(
        member_badge_assignment_on_db.member_id, member_badge_assignment_on_db.badge_id
    )
    assert result is True
    with pytest.raises(MemberBadgeNotFoundError):
        service.revoke_badge_from_user(
            member_badge_assignment_on_db.member_id,
            member_badge_assignment_on_db.badge_id,
        )


def test_revoke_badge_not_assigned_service(
    transaction_manager, community_member_on_db, badge_on_db
):
    service = BadgeService(transaction_manager)
    with pytest.raises(MemberBadgeNotFoundError):
        service.revoke_badge_from_user(
            community_member_on_db.id,
            badge_on_db.id,
        )


def test_list_badges_for_user_service(
    transaction_manager, member_badge_assignment_on_db, badge_on_db
):
    service = BadgeService(transaction_manager)
    badges = service.list_badges_for_member(member_badge_assignment_on_db.member_id)
    assert len(badges) == 1
    assert badges[0].id == member_badge_assignment_on_db.badge_id
    assert badges[0].name == badge_on_db.name
    assert badges[0].description == badge_on_db.description
    assert badges[0].community_id == badge_on_db.community_id
