import logging
from typing import List
from uuid import UUID

from app.api.comment.exceptions import (
    CommentLikesNotFoundError,
    CommentNotFoundError,
    CommentSuspendedError,
    UnexpectedCommentError,
)
from app.api.comment.model import Comment, CommentLikes
from app.api.comment.schema import (
    CommentAuthor,
    CommentCreate,
    CommentResponse,
    CommentStatusEnum,
    CommentUpdate,
    PostRelated,
)
from app.api.communities.schema import CommunityMemberResponse
from app.api.communities.service import CommunityService
from app.api.notifications.service import NotificationService
from app.api.post.exceptions import PostNotFoundError
from app.api.reputation.schema import POPULARITY_POINTS, PopularityActionEnum
from app.api.reputation.service import ReputationService
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams


class CommentService:
    REPORT_THRESHOLD = 10

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.comment_repo = tm.get_comment_repository()
        self.comment_likes_repo = tm.get_comment_likes_repository()
        self.post_repo = tm.get_post_repository()
        self.member_repo = tm.get_member_repository()
        self.community_service = CommunityService(tm)
        self.reputation_service = ReputationService(tm)

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

    def _map_comment_to_response(
        self, comment: Comment, replies_map: dict = None
    ) -> CommentResponse:
        """
        Mapeia um comentário para response.
        Se replies_map for fornecido, inclui replies recursivamente.
        """
        # Pega o role diretamente do membro
        member_role = comment.member.role if comment.member else None

        response = CommentResponse(
            id=comment.id,
            post=PostRelated(
                id=comment.post_id, title=comment.post.title if comment.post else None
            ),
            member=CommentAuthor(
                id=comment.member_id,
                name=comment.member.user.name,
                profile_image_url=comment.member.user.profile_image_url,
                member_role=member_role,
            ),
            content=comment.content,
            status=comment.status,
            likes_count=comment.likes_count,
            report_count=comment.report_count,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            replies=[],
        )

        # Se temos um mapa de replies, adiciona as replies recursivamente
        if replies_map and comment.id in replies_map:
            response.replies = [
                self._map_comment_to_response(reply, replies_map)
                for reply in replies_map[comment.id]
            ]

        return response

    def create_comment(self, comment_create: CommentCreate) -> CommentResponse:
        self._get_post(comment_create.post_id)

        parent_comment = None
        if comment_create.parent_id:
            parent_comment = self._get_comment(comment_create.parent_id)

        try:
            comment = Comment(**comment_create.model_dump())
            comment_saved = self.comment_repo.save(comment)
            post = self._get_post(comment_create.post_id)
            post.comments_count += 1

            commenter_member = self.community_service.get_member(comment_saved.member_id)
            post_author_member = self.community_service.get_member_association(
                post.user_id, post.community_id
            )
            self.reputation_service.reward_comment_creation_to_member(
                commenter_member.id, post_author_member.id
            )
            self.post_repo.save(post)

            try:
                notification_service = NotificationService(self.tm)
                actor = self.tm.get_user_repository().get_by_id(comment_create.user_id)
                post_author = post.user

                if post_author and post_author.id != actor.id:
                    notification_service.create_interaction_notification(
                        recipient=post_author,
                        actor=actor,
                        interaction_type='comment',
                        post_title=post.title or 'sua publicação',
                        comment_content=comment_create.content,
                    )

                if parent_comment:
                    parent_author = parent_comment.user
                    if parent_author and parent_author.id not in {
                        actor.id,
                        post_author.id,
                    }:
                        notification_service.create_interaction_notification(
                            recipient=parent_author,
                            actor=actor,
                            interaction_type='reply',
                            post_title=post.title or 'sua publicação',
                            comment_content=comment_create.content,
                        )
            except Exception as e:
                logging.warning(f'Falha ao criar notificação de comentário: {e}')

            return self._map_comment_to_response(comment_saved)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error creating comment') from e

    def get_comment(self, comment_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        return self._map_comment_to_response(comment)

    def _get_replies_for_comments(
        self, comment_ids: list, status_filter=None
    ) -> List[Comment]:
        """Busca recursivamente todas as replies para uma lista de comentários."""
        if not comment_ids:
            return []

        # Busca replies diretas
        query = self.comment_repo.session.query(Comment).filter(
            Comment.parent_id.in_(comment_ids)
        )

        if status_filter:
            query = query.filter(Comment.status.in_(status_filter))

        direct_replies = query.order_by(Comment.created_at).all()

        # Busca replies das replies recursivamente
        reply_ids = [reply.id for reply in direct_replies]
        nested_replies = self._get_replies_for_comments(reply_ids, status_filter)

        return direct_replies + nested_replies

    def list_comments_by_post(
        self, post_id: UUID, params: PaginationSearchParams, include_replies: bool = True
    ) -> PaginationResponse[CommentResponse]:
        self._get_post(post_id)

        if not include_replies:
            # Versão simples sem replies aninhadas
            comments, total = self.comment_repo.list_comments_by_post(post_id, params)
            return PaginationResponse(
                items=[self._map_comment_to_response(comment) for comment in comments],
                total=total,
                has_more=total > (params.offset or 0) + (params.limit or 10),
                current_offset=params.offset or 0,
                current_limit=params.limit or 10,
            )

        # Versão com replies aninhadas
        # Primeiro, busca os comentários principais paginados
        main_comments, total = self.comment_repo.list_comments_by_post(post_id, params)

        if not main_comments:
            return PaginationResponse(
                items=[],
                total=total,
                has_more=False,
                current_offset=params.offset or 0,
                current_limit=params.limit or 10,
            )

        # Busca todas as replies dos comentários principais
        main_comment_ids = [comment.id for comment in main_comments]
        all_replies = self._get_replies_for_comments(main_comment_ids, params.status)

        # Organiza as replies por parent_id
        replies_map = {}
        for reply in all_replies:
            if reply.parent_id not in replies_map:
                replies_map[reply.parent_id] = []
            replies_map[reply.parent_id].append(reply)

        # Mapeia os comentários principais com suas replies
        items = [
            self._map_comment_to_response(comment, replies_map)
            for comment in main_comments
        ]

        return PaginationResponse(
            items=items,
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

    def update_comment(
        self, comment_id: UUID, comment_update: CommentUpdate
    ) -> CommentResponse:
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

    def get_like(self, comment_id: UUID, member_id: UUID) -> CommentLikes:
        like = self.comment_likes_repo.get_by_comment_and_member(comment_id, member_id)
        if not like:
            raise CommentLikesNotFoundError('Comment likes not found')
        return like

    def like_comment(self, comment_id: UUID, member_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        comment.likes_count += 1
        try:
            like = CommentLikes(comment_id=comment_id, member_id=member_id)
            self.comment_likes_repo.save(like)
            comment = self.comment_repo.save(comment)

            try:
                notification_service = NotificationService(self.tm)
                recipient = comment.user
                actor = self.tm.get_user_repository().get_by_id(member_id)

                if recipient and actor and recipient.id != actor.id:
                    notification_service.create_interaction_notification(
                        recipient=recipient,
                        actor=actor,
                        interaction_type='like',
                        post_title=comment.post.title or 'seu comentário',
                    )
            except Exception as e:
                logging.warning(f'Falha ao criar notificação de like em comentário: {e}')
                comment_author_member = self.community_service.get_member(
                    comment.member_id
                )
                self.reputation_service.reward_comment_like_to_member(
                    member_id, comment_author_member.id
                )

            comment_author_member = self.community_service.get_member(comment.member_id)
            self.reputation_service.reward_comment_like_to_member(
                member_id, comment_author_member.id
            )
            return self._map_comment_to_response(comment)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error liking comment') from e

    def unlike_comment(self, comment_id: UUID, member_id: UUID) -> CommentResponse:
        comment = self._get_comment(comment_id)
        like = self.get_like(comment_id, member_id)

        try:
            if comment.likes_count > 0:
                comment.likes_count -= 1
            self.comment_likes_repo.delete(like)
            comment = self.comment_repo.save(comment)

            comment_author_member = self.community_service.get_member(comment.member_id)
            comment_author_member.popularity -= POPULARITY_POINTS[
                PopularityActionEnum.RECEIVE_LIKE
            ]
            comment_author_member.popularity = max(0, comment_author_member.popularity)
            self.community_service.member_repo.save(comment_author_member)

            liker = self.community_service.get_member(member_id)
            liker.popularity -= POPULARITY_POINTS[PopularityActionEnum.LIKE]
            self.community_service.member_repo.save(liker)
            return self._map_comment_to_response(comment)
        except Exception as e:
            raise UnexpectedCommentError('Unexpected error unliking comment') from e

    def list_likes_comment(self, comment_id: UUID) -> list[CommunityMemberResponse]:
        self._get_comment(comment_id)
        members = self.comment_likes_repo.list_by_comment(comment_id)
        members_response = []
        for member in members:
            members_response.append(
                self.community_service._map_member_to_response(member)
            )
        return members_response

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
