from typing import List
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.comment.model import Comment, CommentLikes
from app.api.comment.schema import CommentStatusEnum
from app.api.communities.model import CommunityMember
from app.core.repository import BaseRepository
from app.utils.schema import PaginationSearchParams


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: Session):
        super().__init__(Comment, session)
        self.session = session

    def list_comments_by_post(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = self.session.query(Comment).filter(
            Comment.post_id == post_id, Comment.parent_id.is_(None)
        )

        if params.status:
            query = query.filter(Comment.status.in_(params.status))

        if params.name:
            query = query.filter(Comment.content.ilike(f'%{params.name}%'))

        total = query.count()
        query = query.order_by(desc(Comment.created_at))
        comments = query.offset(params.offset).limit(params.limit).all()

        return comments, total

    def list_all_comments_by_post(
        self, post_id: UUID, status_filter=None
    ) -> List[Comment]:
        """Busca todos os comentários do post para montar a árvore de replies."""
        query = self.session.query(Comment).filter(Comment.post_id == post_id)

        if status_filter:
            query = query.filter(Comment.status.in_(status_filter))

        query = query.order_by(Comment.created_at)
        return query.all()

    def list_comments_by_user(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = self.session.query(Comment).filter(Comment.user_id == user_id)

        if params.status:
            query = query.filter(Comment.status.in_(params.status))

        total = query.count()
        query = query.order_by(desc(Comment.created_at))
        comments = query.offset(params.offset).limit(params.limit).all()

        return comments, total

    def list_replies_by_parent(
        self, parent_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = self.session.query(Comment).filter(Comment.parent_id == parent_id)

        if params.status:
            query = query.filter(Comment.status.in_(params.status))

        total = query.count()
        query = query.order_by(Comment.created_at)
        comments = query.offset(params.offset).limit(params.limit).all()

        return comments, total

    def list_reported_comments(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = self.session.query(Comment).filter(
            Comment.post_id == post_id, Comment.status == CommentStatusEnum.REPORTED
        )

        total = query.count()
        comments = query.offset(params.offset).limit(params.limit).all()
        return comments, total

    def list_suspended_comments(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = self.session.query(Comment).filter(
            Comment.post_id == post_id, Comment.status == CommentStatusEnum.SUSPENDED
        )

        total = query.count()
        comments = query.offset(params.offset).limit(params.limit).all()
        return comments, total


class CommentLikesRepository(BaseRepository[CommentLikes]):
    def __init__(self, session: Session):
        super().__init__(CommentLikes, session)
        self.session = session

    def save(self, model: CommentLikes) -> CommentLikes:
        """Override save method to handle composite key logging"""
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {self.model.__qualname__} with comment_id {model.comment_id} and member_id {model.member_id} saved successfully'
        )
        return model

    def delete(self, model: CommentLikes) -> bool:
        """Override delete method to handle composite key logging"""
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {self.model.__qualname__} with comment_id {model.comment_id} and member_id {model.member_id} deleted successfully'
        )
        return True

    def get_by_comment_and_member(
        self, comment_id: UUID, member_id: UUID
    ) -> CommentLikes | None:
        like = (
            self.session.query(CommentLikes)
            .filter(
                CommentLikes.comment_id == comment_id,
                CommentLikes.member_id == member_id,
            )
            .first()
        )
        if like:
            self.logger.debug(
                f'Model {CommentLikes.__qualname__} with comment_id {comment_id} and member_id {member_id} retrieved successfully'
            )
        else:
            self.logger.warning(
                f'Model {CommentLikes.__qualname__} with comment_id {comment_id} and member_id {member_id} not found'
            )
        return like

    def list_by_comment(self, comment_id: UUID) -> List[CommunityMember]:
        likes = (
            self.session.query(CommunityMember)
            .join(CommentLikes, CommunityMember.id == CommentLikes.member_id)
            .filter(CommentLikes.comment_id == comment_id)
            .all()
        )

        self.logger.debug(f'Retrieved {len(likes)} likes for comment {comment_id}')
        return likes
