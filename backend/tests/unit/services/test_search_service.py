import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.api.search.service import SearchService
from app.api.users.model import User
from app.api.post.model import Post
from app.api.search import schemas


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


class TestSearchService:

    def test_perform_search_returns_users_and_posts(self, mock_db_session):
        mock_user = User(id="a1b2c3d4-e5f6-7890-1234-567890abcdef", name="Test User")
        mock_post = Post(id="f1e2d3c4-b5a6-7890-1234-567890abcdea", title="A Test Post")

        mock_db_session.query.return_value.filter.return_value.limit.return_value.all.side_effect = [
            [mock_user],
            [mock_post]
        ]

        search_service = SearchService()
        query = "Test"

        results = search_service.perform_search(db=mock_db_session, query=query)

        assert len(results) == 2

        user_result = next((item for item in results if isinstance(item, schemas.UserSearchResult)), None)
        assert user_result is not None
        assert user_result.name == mock_user.name
        assert user_result.type == "user"

        post_result = next((item for item in results if isinstance(item, schemas.PostSearchResult)), None)
        assert post_result is not None
        assert post_result.title == mock_post.title
        assert post_result.type == "post"

    def test_perform_search_no_results(self, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        search_service = SearchService()
        query = "NonExistentTerm"

        results = search_service.perform_search(db=mock_db_session, query=query)

        assert len(results) == 0
        assert results == []