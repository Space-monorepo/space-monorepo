from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.post.model import Post
from app.api.users.model import User

from . import schemas


class SearchService:
    @staticmethod
    def perform_search(db: Session, query: str) -> list:
        search_term = f'%{query}%'
        results = []
        users = (
            db.query(User)
            .filter(
                or_(
                    User.name.ilike(search_term),
                )
            )
            .limit(10)
            .all()
        )

        for user in users:
            results.append(schemas.UserSearchResult.from_orm(user))

        posts = (
            db.query(Post)
            .filter(or_(Post.title.ilike(search_term), Post.content.ilike(search_term)))
            .limit(10)
            .all()
        )

        for post in posts:
            results.append(schemas.PostSearchResult.from_orm(post))

        return results
