import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.users.model import User
from app.api.post.model import Post
from app.api.communities.model import Community, CommunityMember
# Importa o Enum correto do schema
from app.api.communities.schema import CommunityTypeEnum, CommunityMemberRoleEnum


def test_search_returns_users_and_posts_same_community(
    authenticate_client: TestClient, 
    user_on_db: User, 
    post_on_db: Post
):
    """
    Testa se a busca encontra itens da MESMA comunidade que o usuário logado.
    Verifica também se o community_id está presente nos posts retornados.
    """
    response = authenticate_client.get("/search/?q=Test")

    assert response.status_code == 200
    results = response.json()

    # Verifica se o post esperado está nos resultados
    post_results = [item for item in results if item.get('type') == 'post']
    result_titles = [item.get('title') for item in post_results]
    assert post_on_db.title in result_titles
    
    # Verifica se todos os posts têm community_id
    for post_result in post_results:
        assert 'community_id' in post_result, "community_id deve estar presente no resultado do post"
        assert post_result['community_id'] is not None, "community_id não deve ser None"


def test_search_ignores_other_community_items(
    authenticate_client: TestClient,
    session_sql: Session,
    user_on_db: User
):
    """
    Testa a restrição: Não deve encontrar usuários ou posts de comunidades 
    que o usuário logado NÃO participa.
    """
    # 1. Criar uma nova comunidade "estranha"
    other_community = Community(
        name="Secret Community",
        description="Private",
        # CORREÇÃO: Usando 'CLUB' que é um valor válido no seu Enum
        type_community=CommunityTypeEnum.CLUB
    )
    session_sql.add(other_community)
    session_sql.flush()
    session_sql.refresh(other_community)

    # 2. Criar um usuário "estranho" nessa comunidade
    other_user = User(
        email="stranger@test.com",
        username="stranger",
        name="Stranger User",
        hashed_password="123"
    )
    session_sql.add(other_user)
    session_sql.flush()
    session_sql.refresh(other_user)

    other_member = CommunityMember(
        user_id=other_user.id,
        community_id=other_community.id,
        role=CommunityMemberRoleEnum.MEMBER
    )
    session_sql.add(other_member)

    # 3. Criar um post nessa comunidade "estranha"
    other_post = Post(
        community_id=other_community.id,
        user_id=other_user.id,
        user_role_in_community="MEMBER",
        type_post="DISCUSSION",
        title="Stranger Post Content",
        content="Segredo"
    )
    session_sql.add(other_post)
    session_sql.commit()

    # 4. O usuário logado (authenticate_client / user_on_db) NÃO está na "Secret Community".
    # Buscar por "Stranger" deve retornar vazio.
    response = authenticate_client.get("/search/?q=Stranger")
    
    assert response.status_code == 200
    results = response.json()
    
    # Verifica nomes e títulos encontrados
    found_names = [r.get('name') for r in results if r.get('type') == 'user']
    found_titles = [r.get('title') for r in results if r.get('type') == 'post']

    assert "Stranger User" not in found_names
    assert "Stranger Post Content" not in found_titles


def test_search_no_results(authenticate_client: TestClient):
    """Testa se a busca por um termo inexistente retorna lista vazia."""
    response = authenticate_client.get("/search/?q=NonExistentTerm")
    assert response.status_code == 200
    assert response.json() == []


def test_search_query_too_short(authenticate_client: TestClient):
    """Testa validação de tamanho mínimo."""
    response = authenticate_client.get("/search/?q=ab")
    assert response.status_code == 422


def test_search_unauthenticated(client_sql: TestClient):
    """Testa se acesso sem login retorna 401."""
    response = client_sql.get("/search/?q=Test")
    assert response.status_code == 401