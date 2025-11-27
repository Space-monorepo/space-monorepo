import pytest
import uuid

from app.api.search import schemas
from app.api.users.model import User
from app.api.post.model import Post


class TestUserSearchResultSchema:
    """Testes para o schema UserSearchResult."""

    def test_user_search_result_from_orm(self):
        """Testa a criação de uma instância a partir de um objeto ORM (User)."""
        mock_user_orm = User(
            id=uuid.uuid4(),
            name="ORM User",
            profile_image_url="http://example.com/orm.png",
            email="orm@test.com",
            hashed_password="abc"
        )

        result = schemas.UserSearchResult.from_orm(mock_user_orm)

        assert result.id == mock_user_orm.id
        assert result.name == mock_user_orm.name
        assert result.profile_image_url == mock_user_orm.profile_image_url
        assert result.type == "user"


class TestPostSearchResultSchema:
    """Testes para o schema PostSearchResult."""

    def test_post_search_result_from_orm(self):
        """Testa a criação de uma instância a partir de um objeto ORM (Post)."""
        community_id = uuid.uuid4()
        mock_post_orm = Post(
            id=uuid.uuid4(),
            title="ORM Post Title",
            content="Some content here.",
            user_id=uuid.uuid4(),
            community_id=community_id
        )

        result = schemas.PostSearchResult.from_orm(mock_post_orm)

        assert result.id == mock_post_orm.id
        assert result.title == mock_post_orm.title
        assert result.community_id == mock_post_orm.community_id
        assert result.type == "post"