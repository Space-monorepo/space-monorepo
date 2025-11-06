from fastapi import FastAPI

from app.api.badges.exceptions import add_badge_exception_handler
from app.api.chat.exceptions import add_chat_exception_handler
from app.api.comment.exceptions import add_comment_exception_handler
from app.api.communities.exceptions import add_community_exception_handler
from app.api.post.exceptions import add_post_exception_handler
from app.api.rating.exceptions import add_rating_exception_handler
from app.api.reports.exceptions import add_report_exception_handler
from app.api.reputation.exceptions import add_reputation_exception_handler
from app.api.users.exceptions import add_user_exception_handler


def add_exception_handlers(app: FastAPI):
    add_user_exception_handler(app)
    add_post_exception_handler(app)
    add_badge_exception_handler(app)
    add_community_exception_handler(app)
    add_comment_exception_handler(app)
    add_rating_exception_handler(app)
    add_chat_exception_handler(app)
    add_report_exception_handler(app)
    add_reputation_exception_handler(app)
