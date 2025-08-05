import uuid

import pytest

from app.communities.exceptions import CommunityMemberNotFoundError, CommunityNotFoundError
from app.communities.model import Community, CommunityMember
from app.communities.schema import (
    CommunityCreate,
    CommunityTypeEnum,
    CommunityUpdate,
    CommunityMemberRoleEnum,
    CommunityMemberStatusEnum,
    CommunityMemberCreate
)
from app.communities.service import CommunityService
from app.utils.schema import PaginationSearchParams


def test_create_community_service(session_sql, transaction_manager):
    community = CommunityCreate(
        name='Test Community',
        description='Test Description',
        type_community=CommunityTypeEnum.UNIVERSITY,
    )

    community = CommunityService(transaction_manager).create_community(community)
    assert community.id is not None
    assert community.name == 'Test Community'
    assert community.description == 'Test Description'
    assert community.type_community == CommunityTypeEnum.UNIVERSITY

    community_db = session_sql.query(Community).filter(Community.id == community.id).first()
    assert community_db is not None
    assert community_db.name == 'Test Community'
    assert community_db.description == 'Test Description'


def test_get_community_by_id_service(transaction_manager, community_on_db):
    community = CommunityService(transaction_manager).get_community(community_on_db.id)
    assert community is not None
    assert community.id == community_on_db.id
    assert community.name == community_on_db.name
    assert community.description == community_on_db.description
    assert community.type_community == community_on_db.type_community


def test_get_community_by_id_not_found(transaction_manager):
    random_id = uuid.uuid4()
    with pytest.raises(CommunityNotFoundError):
        CommunityService(transaction_manager).get_community(random_id)


def test_list_communities_service(transaction_manager, community_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    communities = CommunityService(transaction_manager).list_communities(params)
    assert communities is not None
    assert communities.items is not None
    assert len(communities.items) > 0
    assert str(communities.items[0].id) == str(community_on_db.id)
    assert communities.items[0].name == community_on_db.name


def test_get_community_by_name_service(transaction_manager, community_on_db):
    params = PaginationSearchParams(offset=0, limit=10, search=community_on_db.name)
    communities = CommunityService(transaction_manager).list_communities(params)
    assert communities is not None
    assert communities.items is not None
    assert len(communities.items) > 0
    assert str(communities.items[0].id) == str(community_on_db.id)
    assert communities.items[0].name == community_on_db.name


def test_update_community_service(session_sql, transaction_manager, community_on_db):
    community_update = CommunityUpdate(
        name='Updated Community',
        description='Updated Description',
        type_community=CommunityTypeEnum.COMMERCIAL
    )

    community = CommunityService(transaction_manager).update_community(community_on_db.id, community_update)
    assert community is not None
    assert community.name == 'Updated Community'
    assert community.description == 'Updated Description'
    assert community.type_community == CommunityTypeEnum.COMMERCIAL

    community_db = session_sql.query(Community).filter(Community.id == community_on_db.id).first()
    assert community_db is not None
    assert community_db.name == 'Updated Community'
    assert community_db.description == 'Updated Description'
    assert community_db.type_community == CommunityTypeEnum.COMMERCIAL


def test_update_community_partial_service(session_sql, transaction_manager, community_on_db):
    partial_update = CommunityUpdate(name='Partially Updated Community')

    community = CommunityService(transaction_manager).update_community(community_on_db.id, partial_update)
    assert community is not None
    assert community.name == 'Partially Updated Community'
    assert community.description == community_on_db.description
    assert community.type_community == community_on_db.type_community

    community_db = session_sql.query(Community).filter(Community.id == community_on_db.id).first()
    assert community_db is not None
    assert community_db.name == 'Partially Updated Community'
    assert community_db.description == community_on_db.description


def test_delete_community_service_as_admin(session_sql, transaction_manager, community_on_db):
    result = CommunityService(transaction_manager).delete_community(community_on_db.id)
    assert result is True

    community_db = session_sql.query(Community).filter(Community.id == community_on_db.id).first()
    assert community_db is None


def test_delete_community_service_not_found(transaction_manager):
    random_id = uuid.uuid4()
    with pytest.raises(CommunityNotFoundError):
        CommunityService(transaction_manager).delete_community(random_id)


def test_list_members_service(transaction_manager, community_on_db, community_member_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    members = CommunityService(transaction_manager).list_members(community_on_db.id, params)
    assert members is not None
    assert members.items is not None
    assert len(members.items) > 0
    assert str(members.items[0].user_id) == str(community_member_on_db.user_id)
    assert str(members.items[0].community_id) == str(community_member_on_db.community_id)
    assert members.items[0].role == community_member_on_db.role


def test_list_user_communities_service(transaction_manager, community_on_db, community_member_on_db, user_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    communities = CommunityService(transaction_manager).list_user_communities(user_on_db.id, params)
    assert communities is not None
    assert communities.items is not None
    assert len(communities.items) > 0
    assert str(communities.items[0].id) == str(community_on_db.id)
    assert communities.items[0].name == community_on_db.name


def test_get_member_association_service(transaction_manager, community_on_db, community_member_on_db, user_on_db):
    member = CommunityService(transaction_manager).get_member_association(user_on_db.id, community_on_db.id)
    assert member is not None
    assert member.user_id == user_on_db.id
    assert member.community_id == community_on_db.id
    assert member.role == CommunityMemberRoleEnum.ADMIN


def test_list_moderators_service(transaction_manager, community_on_db, moderator_member_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    moderators = CommunityService(transaction_manager).list_moderators(community_on_db.id, params)

    assert moderators is not None
    assert moderators.items is not None
    assert len(moderators.items) > 0

    moderator_exists = False
    for m in moderators.items:
        if (str(m.user_id) == str(moderator_member_on_db.user_id) and
            str(m.community_id) == str(community_on_db.id) and
            m.role == moderator_member_on_db.role):
            moderator_exists = True
            break

    assert moderator_exists is True

    total = moderators.total or 0
    limit = params.limit or 10

    assert moderators.has_more == (total > limit)
    assert moderators.current_offset == (params.offset or 0)
    assert moderators.current_limit == (params.limit or 10)


def test_create_member_service(session_sql, transaction_manager, community_on_db, user_on_db):
    member = CommunityMemberCreate(
        user_id=user_on_db.id,
        community_id=community_on_db.id,
        role=CommunityMemberRoleEnum.MEMBER,
        reputation=10,
        status_participation=CommunityMemberStatusEnum.ACTIVE,
    )

    member = CommunityService(transaction_manager).create_member(member)
    assert member is not None
    assert member.user_id == user_on_db.id
    assert member.community_id == community_on_db.id
    assert member.role == CommunityMemberRoleEnum.MEMBER
    assert member.reputation == 10
    assert member.status_participation == CommunityMemberStatusEnum.ACTIVE


def test_remove_member_service(session_sql, transaction_manager, community_member_on_db):
    result = CommunityService(transaction_manager).remove_member(community_member_on_db.id)
    assert result is True

    member_db = session_sql.query(CommunityMember).filter(
        CommunityMember.id == community_member_on_db.id
    ).first()
    assert member_db is None


def test_update_member_role_to_admin_service(session_sql, transaction_manager, moderator_member_on_db):
    updated_member = CommunityService(transaction_manager).update_member_role(
        moderator_member_on_db.id, CommunityMemberRoleEnum.ADMIN
    )

    assert updated_member is not None
    assert updated_member.role == CommunityMemberRoleEnum.ADMIN
    assert updated_member.reputation == moderator_member_on_db.reputation

    member_db = session_sql.query(CommunityMember).filter(
        CommunityMember.user_id == moderator_member_on_db.user_id,
        CommunityMember.community_id == moderator_member_on_db.community_id
    ).first()
    assert member_db is not None
    assert member_db.role == CommunityMemberRoleEnum.ADMIN


def test_update_member_role_member_not_found_service(transaction_manager, community_on_db):
    with pytest.raises(CommunityMemberNotFoundError):
        CommunityService(transaction_manager).update_member_role(
            uuid.uuid4(), CommunityMemberRoleEnum.MODERATOR
        )


