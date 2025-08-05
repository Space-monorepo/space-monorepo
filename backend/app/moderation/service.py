from app.post.service import PostService
from app.post.schemas import PostStatusEnum, PostResponse
from app.users.schema import UserResponse
from app.users.service import UserService
#from app.post.schemas import CommentResponse
#from app.post.service import CommentService

class ModerationService:
    def __init__(self, db):
        self.db = db
    
    def moderate_post(self, post_id: str, new_status: PostStatusEnum) -> PostResponse | bool:
        post = PostService(self.db).get_post_by_id(post_id)
        if new_status == 'rejected':
            return PostService(self.db).delete_post(post_id)
        post.status = new_status
        return PostService(self.db).update_post(post_id, post)
    
    def suspend_user(self, user_id: str) -> UserResponse:
        user = UserService(self.db).get_user_by_id(user_id)
        user.status = 'suspended'
        return UserService(self.db).update_user(user_id, user)
    
    def unsuspend_user(self, user_id: str) -> UserResponse:
        user = UserService(self.db).get_user_by_id(user_id)
        user.status = 'active'
        return UserService(self.db).update_user(user_id, user)
    
    # def suspend_comment(self, comment_id: str) -> CommentResponse:
    #     comment = CommentService(self.db).get_comment_by_id(comment_id)
    #     comment.status = 'suspended'
    #     return CommentService(self.db).update_comment(comment_id, comment)
    
    # def unsuspend_comment(self, comment_id: str) -> CommentResponse:
    #     comment = CommentService(self.db).get_comment_by_id(comment_id)
    #     comment.status = 'active'
    #     return CommentService(self.db).update_comment(comment_id, comment)
