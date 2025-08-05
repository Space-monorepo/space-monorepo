from typing import List
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.comment.model import Comment, CommentLikes
from app.comment.schema import CommentStatusEnum
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
            Comment.post_id == post_id,
            Comment.parent_id.is_(None)
        )

        if params.status:
            query = query.filter(Comment.status.in_(params.status))

        if params.name:
            query = query.filter(Comment.content.ilike(f'%{params.name}%'))

        total = query.count()
        query = query.order_by(desc(Comment.created_at))
        comments = query.offset(params.offset).limit(params.limit).all()

        return comments, total

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
            Comment.post_id == post_id,
            Comment.status == CommentStatusEnum.REPORTED
        )

        total = query.count()
        comments = query.offset(params.offset).limit(params.limit).all()
        return comments, total

    def list_suspended_comments(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = self.session.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.status == CommentStatusEnum.SUSPENDED
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
            f'Model {self.model.__qualname__} with comment_id {model.comment_id} and user_id {model.user_id} saved successfully'
        )
        return model

    def delete(self, model: CommentLikes) -> bool:
        """Override delete method to handle composite key logging"""
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {self.model.__qualname__} with comment_id {model.comment_id} and user_id {model.user_id} deleted successfully'
        )
        return True

    def get_by_comment_and_user(self, comment_id: UUID, user_id: UUID) -> CommentLikes | None:
        like = (
            self.session.query(CommentLikes)
            .filter(
                CommentLikes.comment_id == comment_id,
                CommentLikes.user_id == user_id
            )
            .first()
        )
        if like:
            self.logger.debug(
                f'Model {CommentLikes.__qualname__} with comment_id {comment_id} and user_id {user_id} retrieved successfully'
            )
        else:
            self.logger.warning(
                f'Model {CommentLikes.__qualname__} with comment_id {comment_id} and user_id {user_id} not found'
            )
        return like

    def list_by_comment(self, comment_id: UUID) -> List[CommentLikes]:
        likes = (
            self.session.query(CommentLikes)
            .filter(CommentLikes.comment_id == comment_id)
            .all()
        )
        
        self.logger.debug(
            f'Retrieved {len(likes)} likes for comment {comment_id}'
        )
        return likes

    def list_user_liked_comments(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> tuple[List[Comment], int]:
        query = (
            self.session.query(Comment)
            .join(CommentLikes, CommentLikes.comment_id == Comment.id)
            .filter(CommentLikes.user_id == user_id)
        )

        total = query.count()
        query = query.order_by(desc(CommentLikes.created_at))
        comments = query.offset(params.offset).limit(params.limit).all()
        return comments, total