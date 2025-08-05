from uuid import UUID

from app.comment.exceptions import (
    CommentLikesNotFoundError,
    CommentNotFoundError,
    CommentSuspendedError,
    UnexpectedCommentError,
)
from app.comment.model import Comment, CommentLikes
from app.comment.schema import (
    CommentAuthor,
    CommentCreate,
    CommentLikeResponse,
    CommentResponse,
    CommentStatusEnum,
    CommentUpdate,
    PostRelated,
)
from app.core.transaction import TransactionManager
from app.post.exceptions import PostNotFoundError
from app.utils.schema import PaginationResponse, PaginationSearchParams


class CommentService:
    REPORT_THRESHOLD = 10

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.comment_repo = tm.get_comment_repository()
        self.comment_likes_repo = tm.get_comment_likes_repository()
        self.post_repo = tm.get_post_repository()

    def _get_comment(self, comment_id: UUID) -> Comment:
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError('Comment not found')
        return comment

    def _get_post(self, post_id: UUID):
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError('Post not found')
        return post

    @staticmethod
    def _map_comment_to_response(comment: Comment) -> CommentResponse:
        return CommentResponse(
            id=comment.id,
            post=PostRelated(
                id=comment.post_id,
                title=comment.post.title if comment.post else None
            ),
            user=CommentAuthor(
                id=comment.user_id,
                name=comment.user.name,
                profile_image_url=comment.user.profile_image_url,
            ),
            content=comment.content,
            status=comment.status,
            likes_count=comment.likes_count,
            report_count=comment.report_count,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            replies=[]
        )

    def create_comment(self, comment_create: CommentCreate) -> CommentResponse:
        self._get_post(comment_create.post_id)
        
        if comment_create.parent_id:
            self._get_comment(comment_create.parent_id)
    
        try:
            comment = Comment(**comment_create.model_dump())
            comment_saved = self.comment_repo.save(comment)
    
            post = self._get_post(comment_create.post_id)
            post.comments_count += 1
            self.post_repo.save(post)
    
            return self._map_comment_to_response(comment_saved)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error creating comment') from e

    def get_comment(self, comment_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        return self._map_comment_to_response(comment)

    def list_comments_by_post(
        self, post_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommentResponse]:
        self._get_post(post_id)
        comments, total = self.comment_repo.list_comments_by_post(post_id, params)
        return PaginationResponse(
            items=[self._map_comment_to_response(comment) for comment in comments],
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_comments_by_user(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommentResponse]:
        comments, total = self.comment_repo.list_comments_by_user(user_id, params)
        return PaginationResponse(
            items=[self._map_comment_to_response(comment) for comment in comments],
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_replies_by_parent(
        self, parent_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommentResponse]:
        self._get_comment(parent_id)
        replies, total = self.comment_repo.list_replies_by_parent(parent_id, params)
        return PaginationResponse(
            items=[self._map_comment_to_response(reply) for reply in replies],
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def update_comment(self, comment_id: UUID, comment_update: CommentUpdate) -> CommentResponse:
        comment = self._get_comment(comment_id)
        
        if comment_update.content:
            comment.content = comment_update.content
        if comment_update.status:
            comment.status = comment_update.status
            
        try:
            comment = self.comment_repo.save(comment)
            comment_saved = self._get_comment(comment.id)
            return self._map_comment_to_response(comment_saved)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error updating comment') from e

    def delete_comment(self, comment_id: UUID) -> bool:
        comment = self._get_comment(comment_id)
        
        try:
            post = self._get_post(comment.post_id)
            if post.comments_count > 0:
                post.comments_count -= 1
                self.post_repo.save(post)
            
            return self.comment_repo.delete(comment)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error deleting comment') from e

    def get_like(self, comment_id: UUID, user_id: UUID) -> CommentLikes:
        like = self.comment_likes_repo.get_by_comment_and_user(comment_id, user_id)
        if not like:
            raise CommentLikesNotFoundError('Comment likes not found')
        return like

    def like_comment(self, comment_id: UUID, user_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        comment.likes_count += 1
        try:
            like = CommentLikes(comment_id=comment_id, user_id=user_id)
            self.comment_likes_repo.save(like)
            comment = self.comment_repo.save(comment)
            return self._map_comment_to_response(comment)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error liking comment') from e

    def unlike_comment(self, comment_id: UUID, user_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        like = self.get_like(comment_id, user_id)
        
        try:
            if comment.likes_count > 0:
                comment.likes_count -= 1
            self.comment_likes_repo.delete(like)
            comment = self.comment_repo.save(comment)
            return self._map_comment_to_response(comment)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error unliking comment') from e

    def list_likes_comment(self, comment_id: UUID) -> list[CommentLikeResponse]:
        self._get_comment(comment_id)
        likes = self.comment_likes_repo.list_by_comment(comment_id)
        return [
            CommentLikeResponse(
                comment_id=like.comment_id,
                user_id=like.user_id,
                created_at=like.created_at
            )
            for like in likes
        ]

    def report_comment(self, comment_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        
        if comment.status == CommentStatusEnum.SUSPENDED:
            raise CommentSuspendedError('Comment is already suspended')
        
        comment.report_count += 1
        if comment.report_count >= self.REPORT_THRESHOLD:
            comment.status = CommentStatusEnum.REPORTED
            
        try:
            comment = self.comment_repo.save(comment)
            return self._map_comment_to_response(comment)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error reporting comment') from e

    def list_user_liked_comments(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommentResponse]:
        comments, total = self.comment_likes_repo.list_user_liked_comments(user_id, params)
        return PaginationResponse(
            items=[self._map_comment_to_response(comment) for comment in comments],
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )