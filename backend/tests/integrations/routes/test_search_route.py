from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importar os modelos é uma boa prática para clareza
from app.api.users.model import User
from app.api.post.model import Post


def test_search_returns_users_and_posts(
    client: TestClient, user_on_db: User, post_on_db: Post
):
    """
    Testa se a busca por um termo comum ('Test') retorna o usuário e o post
    criados pelas fixtures.
    (user_on_db.name = 'testuser', post_on_db.title = 'Test Post')
    """
    # O usuário 'testuser' e o post 'Test Post' já foram criados pelas fixtures.
    # A busca por 'Test' deve encontrar ambos.
    response = client.get("/search/?q=Test")

    # Asserts da resposta
    assert response.status_code == 200
    results = response.json()

    # Deve encontrar 2 resultados: o usuário e o post
    assert len(results) >= 2  # Usamos >= caso outros testes criem itens com 'Test'

    # Verifica se os nomes/títulos esperados estão nos resultados
    result_names = [item.get('name') for item in results if item.get('type') == 'user']
    result_titles = [item.get('title') for item in results if item.get('type') == 'post']

    assert user_on_db.name in result_names
    assert post_on_db.title in result_titles


def test_search_no_results(client: TestClient):
    """Testa se a busca por um termo inexistente retorna uma lista vazia."""
    response = client.get("/search/?q=ThisTermShouldNotExist123")

    assert response.status_code == 200
    assert response.json() == []


def test_search_query_too_short(client: TestClient):
    """Testa se a busca com um termo muito curto retorna erro de validação 422."""
    response = client.get("/search/?q=ab")  # Menor que o min_length=3

    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "String should have at least 3 characters" in data["detail"][0]["msg"]


def test_search_is_case_insensitive(
    client: TestClient, user_on_db: User
):
    """Testa se a busca ignora maiúsculas/minúsculas usando o usuário da fixture."""
    # O nome do usuário da fixture é 'testuser'
    response = client.get("/search/?q=TESTUSER")  # Busca em maiúsculas

    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1

    # Confirma que encontrou o usuário, independentemente do case
    user_found = any(
        item.get('name') == 'testuser' and item.get('type') == 'user'
        for item in results
    )
    assert user_found
    