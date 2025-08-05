import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.api.badges.schema import (
    BadgeCreate,
    BadgeResponse,
    BadgeUpdate,
    MemberBadgeCreate,
    MemberBadgeResponse,
)


def test_badge_create_schema():
    community_uuid = uuid.uuid4()
    badge = BadgeCreate(
        community_id=community_uuid,
        name="Badge de Resposta Schema",
        description="Detalhes da badge.",
        image_url="https://example.com/badge.png"
    )
    assert badge.model_dump() == {
        "community_id": community_uuid,
        "name": "Badge de Resposta Schema",
        "description": "Detalhes da badge.",
        "image_url": "https://example.com/badge.png"
    }


def test_badge_create_invalid_data():
    community_uuid = uuid.uuid4()
    with pytest.raises(ValidationError):
        BadgeCreate(name="", description="Desc", community_id=community_uuid)

    with pytest.raises(ValidationError):
        BadgeCreate(name="a" * 101, description="Desc", community_id=community_uuid)

    with pytest.raises(ValidationError):
        BadgeCreate(name="Valid Name", description="d" * 501, community_id=community_uuid)

    with pytest.raises(ValidationError):
        BadgeCreate(name="Valid Name", image_url="i" * 256, community_id=community_uuid)

    with pytest.raises(ValidationError):
        BadgeCreate(name="Valid Name", description="Valid Desc")


def test_badge_update_schema_valid():
    badge_update = BadgeUpdate(
        name="Nome Atualizado",
        description="Descrição Atualizada",
        image_url="/badges/updated.png"
    )
    assert badge_update.model_dump() == {
        "name": "Nome Atualizado",
        "description": "Descrição Atualizada",
        "image_url": "/badges/updated.png"
    }


def test_badge_response_schema():
    badge_uuid = uuid.uuid4()
    community_uuid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    badge_response = BadgeResponse(
        id=badge_uuid,
        community_id=community_uuid,
        name="Badge de Resposta Schema",
        description="Detalhes da badge.",
        image_url="/badges/response.png",
        created_at=now,
        updated_at=now,
    )
    assert badge_response.model_dump() == {
        "id": badge_uuid,
        "community_id": community_uuid,
        "name": "Badge de Resposta Schema",
        "description": "Detalhes da badge.",
        "image_url": "/badges/response.png",
        "created_at": now,
        "updated_at": now,
    }


def test_member_badge_create_schema():
    member_uuid = uuid.uuid4()
    badge_uuid = uuid.uuid4()

    member_badge_create = MemberBadgeCreate(
        member_id=member_uuid,
        badge_id=badge_uuid,
    )
    assert member_badge_create.model_dump() == {
        "member_id": member_uuid,
        "badge_id": badge_uuid,
    }


def test_member_badge_response_schema():
    member_uuid = uuid.uuid4()
    badge_uuid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    member_badge_response = MemberBadgeResponse(
        member_id=member_uuid,
        badge_id=badge_uuid,
        achieved_at=now,
    )
    assert member_badge_response.model_dump() == {
        "member_id": member_uuid,
        "badge_id": badge_uuid,
        "achieved_at": now,
    }