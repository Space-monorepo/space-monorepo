from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import MongoClient
from typing import List

from app.auth.deps import require_roles
from app.core.database import get_db
from app.moderation.service import ModerationService
from app.post.schemas import PostResponse, PostStatusEnum
from app.users.schema import UserResponse

router = APIRouter(prefix='/moderation', tags=['moderation'])

@router.get('/posts/{community_id}', response_model=List[PostResponse])
def list_posts_under_analysis(
    community_id: str, 
    status_filter: str = None, 
    db: MongoClient = Depends(get_db), 
    roles = Depends(require_roles(["admin", "moderator"]))
):
    try:
        return ModerationService(db).list_posts_under_analysis(community_id, status_filter)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch('/posts/{post_id}', response_model=PostResponse)
def moderate_post(
    post_id: str, 
    new_status: PostStatusEnum, 
    db: MongoClient = Depends(get_db), 
    roles = Depends(require_roles(["admin", "moderator"]))
) -> PostResponse:
    try:
        return ModerationService(db).moderate_post(post_id, new_status)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch('/users/{user_id}/suspend', response_model=UserResponse)
def suspend_user(
    user_id: str, 
    db: MongoClient = Depends(get_db), 
    roles = Depends(require_roles(["admin"]))
) -> UserResponse:
    try:
        return ModerationService(db).suspend_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch('/users/{user_id}/unsuspend', response_model=UserResponse)
def unsuspend_user(
    user_id: str, 
    db: MongoClient = Depends(get_db), 
    roles = Depends(require_roles(["admin"]))
) -> UserResponse:
    try:
        return ModerationService(db).unsuspend_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# @router.patch('/comments/{comment_id}/suspend', response_model=CommentResponse)
# def suspend_comment(
#     comment_id: str, 
#     db: MongoClient = Depends(get_db), 
#     roles = Depends(require_roles(["admin", "moderator"]))
# ) -> CommentResponse:
#     try:
#         return ModerationService(db).suspend_comment(comment_id)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# @router.patch('/comments/{comment_id}/unsuspend', response_model=CommentResponse)
# def unsuspend_comment(
#     comment_id: str, 
#     db: MongoClient = Depends(get_db), 
#     roles = Depends(require_roles(["admin", "moderator"]))
# ) -> CommentResponse:
#     try:
#         return ModerationService(db).unsuspend_comment(comment_id)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))