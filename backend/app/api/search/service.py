from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.communities.model import CommunityMember  # Necessário para o join
from app.api.post.model import Post
from app.api.users.model import User

from . import schemas


class SearchService:
    @staticmethod
    def perform_search(db: Session, query: str, current_user: User) -> list:
        search_term = f'%{query}%'
        results = []

        my_community_ids = [
            membership.community_id for membership in current_user.community_memberships
        ]

        if not my_community_ids:
            return []

        users = (
            db.query(User)
            .join(CommunityMember, CommunityMember.user_id == User.id)
            .filter(
                CommunityMember.community_id.in_(my_community_ids),
                User.id != current_user.id,
                or_(
                    User.name.ilike(search_term),
                ),
            )
            .distinct()
            .limit(10)
            .all()
        )

        for user in users:
            results.append(schemas.UserSearchResult.from_orm(user))

        posts = (
            db.query(Post)
            .filter(
                Post.community_id.in_(my_community_ids),
                or_(Post.title.ilike(search_term), Post.content.ilike(search_term)),
            )
            .limit(10)
            .all()
        )

        for post in posts:
            results.append(schemas.PostSearchResult.from_orm(post))

        return results
