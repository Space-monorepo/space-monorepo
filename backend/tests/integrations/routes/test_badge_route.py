import pytest
from uuid import uuid4
from fastapi import status
from starlette.testclient import TestClient
import sqlite3
import uuid

from app.main import app
from app.core.database import get_db
from app.api.communities.model import Community, CommunityMember
from app.api.badges.model import Badge, MemberBadge
from app.api.users.model import User

# Este adaptador está correto para gravar, mas a leitura é o que causa o problema.
# A solução está em como passamos os dados para os modelos, não aqui.
sqlite3.register_adapter(uuid.UUID, lambda u: str(u))

ADMIN_PREFIX = '/admin/badges'
PUBLIC_PREFIX = '/badges'


@pytest.fixture
def test_app(session_sql):
    """Cria uma aplicação usando a sessão de teste"""

    def override_get_db():
        try:
            yield session_sql
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Cliente HTTP sem autenticação"""
    return TestClient(test_app)


@pytest.fixture
def authenticate_client(client, session_sql):
    """Cliente autenticado como administrador"""
    admin_user = User(
        id=uuid4(),
        email=f"admin-{uuid4()}@test.com",
        name="Test Admin",
        hashed_password="pw"
    )
    if hasattr(admin_user, 'status'):
        admin_user.status = 'admin'

    session_sql.add(admin_user)
    session_sql.commit()
    session_sql.refresh(admin_user)

    client.headers["Authorization"] = f"Bearer admin-token"
    return client


@pytest.fixture
def authenticate_member_client(client, session_sql):
    """Cliente autenticado como membro comum"""
    user_id_obj = uuid4()
    user = User(
        id=user_id_obj,
        email=f"member-{user_id_obj}@test.com",
        name="Test Member",
        hashed_password="pw"
    )
    session_sql.add(user)
    session_sql.commit()
    session_sql.refresh(user)

    client.headers["Authorization"] = f"Bearer member-token"
    # Retornamos o objeto UUID original para uso nos testes
    return client, user_id_obj


# --- TESTES DE ADMIN ---

@pytest.mark.integration
def test_admin_can_create_badge(authenticate_client, session_sql):
    community_id_obj = uuid4()
    community = Community(id=community_id_obj, name='Comm Create Test', type_community='public')
    session_sql.add(community)
    session_sql.commit()

    badge_data = {
        'community_id': str(community_id_obj),
        'name': f'Badge Criado {uuid4()}',
        'description': 'Desc.',
    }

    response = authenticate_client.post(f'{ADMIN_PREFIX}/', json=badge_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['name'] == badge_data['name']


@pytest.mark.integration
def test_admin_cannot_create_duplicate_badge(authenticate_client, session_sql):
    # CORREÇÃO: Armazenar o UUID da comunidade em uma variável
    community_id_obj = uuid4()
    community_obj = Community(id=community_id_obj, name='Comm Dupe Test', type_community='public')
    session_sql.add(community_obj)
    session_sql.commit()

    badge_obj = Badge(id=uuid4(), community_id=community_id_obj, name='Badge Duplicado')
    session_sql.add(badge_obj)
    session_sql.commit()

    badge_data = {'community_id': str(community_id_obj), 'name': 'Badge Duplicado'}
    response = authenticate_client.post(f'{ADMIN_PREFIX}/', json=badge_data)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.integration
def test_admin_can_update_badge(authenticate_client, session_sql):
    # CORREÇÃO: Armazenar o UUID da comunidade em uma variável
    community_id_obj = uuid4()
    community_obj = Community(id=community_id_obj, name='Comm Update Test', type_community='public')
    session_sql.add(community_obj)
    session_sql.commit()

    badge_id_obj = uuid4()
    badge_obj = Badge(id=badge_id_obj, community_id=community_id_obj, name='Badge Original')
    session_sql.add(badge_obj)
    session_sql.commit()

    update_data = {'name': 'Nome Atualizado'}
    response = authenticate_client.patch(f'{ADMIN_PREFIX}/{badge_id_obj}', json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == update_data['name']


@pytest.mark.integration
def test_admin_can_delete_badge(authenticate_client, session_sql):
    # CORREÇÃO: Armazenar o UUID da comunidade em uma variável
    community_id_obj = uuid4()
    community_obj = Community(id=community_id_obj, name='Comm Delete Test', type_community='public')
    session_sql.add(community_obj)
    session_sql.commit()

    badge_id_obj = uuid4()
    badge_obj = Badge(id=badge_id_obj, community_id=community_id_obj, name='Badge para deletar')
    session_sql.add(badge_obj)
    session_sql.commit()

    response = authenticate_client.delete(f'{ADMIN_PREFIX}/{badge_id_obj}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_admin_can_assign_and_revoke_badge(authenticate_client, session_sql):
    # CORREÇÃO: Armazenar todos os UUIDs em variáveis
    user_id_obj = uuid4()
    user_obj = User(
        id=user_id_obj,
        email=f'user-{user_id_obj}@test.com',
        name='Test User',
        hashed_password='pw',
    )
    session_sql.add(user_obj)
    session_sql.commit()

    community_id_obj = uuid4()
    community_obj = Community(id=community_id_obj, name='Comm Assign Test', type_community='public')
    session_sql.add(community_obj)
    session_sql.commit()

    member_id_obj = uuid4()
    member_obj = CommunityMember(
        id=member_id_obj,
        user_id=user_id_obj,
        community_id=community_id_obj,
        role='member'
    )
    session_sql.add(member_obj)
    session_sql.commit()

    badge_id_obj = uuid4()
    badge_obj = Badge(id=badge_id_obj, community_id=community_id_obj, name='Badge para Atribuir')
    session_sql.add(badge_obj)
    session_sql.commit()

    assign_data = {'member_id': str(member_id_obj), 'badge_id': str(badge_id_obj)}
    response_assign = authenticate_client.post(f'{ADMIN_PREFIX}/assign', json=assign_data)
    assert response_assign.status_code == status.HTTP_201_CREATED

    response_revoke = authenticate_client.delete(f'{ADMIN_PREFIX}/revoke/{member_id_obj}/{badge_id_obj}')
    assert response_revoke.status_code == status.HTTP_204_NO_CONTENT


# --- TESTES DE MEMBRO ---

@pytest.mark.integration
def test_member_can_get_badge(authenticate_member_client, session_sql):
    client, user_id_on_db = authenticate_member_client

    # CORREÇÃO: Armazenar os UUIDs para garantir o tipo correto
    community_id_obj = uuid4()
    community_obj = Community(id=community_id_obj, name='Comm Get Test', type_community='public')
    session_sql.add(community_obj)
    session_sql.commit()

    member_link = CommunityMember(
        id=uuid4(),
        user_id=user_id_on_db,
        community_id=community_id_obj,
        role='member'
    )
    session_sql.add(member_link)
    session_sql.commit()

    badge_id_obj = uuid4()
    badge_obj = Badge(id=badge_id_obj, community_id=community_id_obj, name='Badge para Get')
    session_sql.add(badge_obj)
    session_sql.commit()

    response = client.get(f'{PUBLIC_PREFIX}/{badge_id_obj}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(badge_id_obj)


@pytest.mark.integration
def test_member_gets_404_for_non_existent_badge(authenticate_member_client):
    client, _ = authenticate_member_client
    response = client.get(f'{PUBLIC_PREFIX}/{uuid4()}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_member_can_list_badges_from_community(authenticate_member_client, session_sql):
    client, user_id_on_db = authenticate_member_client

    community_id_obj = uuid4()
    community = Community(id=community_id_obj, name='Comm List Test', type_community='public')
    session_sql.add(community)
    session_sql.commit()

    member_link = CommunityMember(
        id=uuid4(),
        user_id=user_id_on_db,
        community_id=community_id_obj,
        role='member'
    )
    session_sql.add(member_link)
    session_sql.commit()

    response = client.get(f'{PUBLIC_PREFIX}/?community_id={community_id_obj}')
    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response.json()


@pytest.mark.integration
def test_member_can_list_badges_for_a_member(authenticate_member_client, session_sql):
    client, user_id_on_db = authenticate_member_client

    # CORREÇÃO: Usar variáveis para todos os UUIDs
    community_id_obj = uuid4()
    community_obj = Community(id=community_id_obj, name='Comm List Member Test', type_community='public')
    session_sql.add(community_obj)
    session_sql.commit()

    auth_member_link = CommunityMember(
        id=uuid4(),
        user_id=user_id_on_db,
        community_id=community_id_obj,
        role='member'
    )
    session_sql.add(auth_member_link)
    session_sql.commit()

    user_target_id = uuid4()
    user_target = User(
        id=user_target_id,
        email=f'user-{user_target_id}@test.com',
        name='T. User Target',
        hashed_password='pw'
    )
    session_sql.add(user_target)
    session_sql.commit()

    member_target_id = uuid4()
    member_target = CommunityMember(
        id=member_target_id,
        user_id=user_target_id,
        community_id=community_id_obj,
        role='member'
    )
    session_sql.add(member_target)
    session_sql.commit()

    badge_id_obj = uuid4()
    badge_obj = Badge(
        id=badge_id_obj,
        community_id=community_id_obj,
        name='Badge para Listar'
    )
    session_sql.add(badge_obj)
    session_sql.commit()

    member_badge = MemberBadge(
        member_id=member_target_id,
        badge_id=badge_id_obj
    )
    session_sql.add(member_badge)
    session_sql.commit()

    response = client.get(f'{PUBLIC_PREFIX}/member/{member_target_id}')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['id'] == str(badge_id_obj)