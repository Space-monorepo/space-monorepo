from fastapi import FastAPI

from app.administration.routes import router as admin_router
from app.users.routes import router as users_router
from app.post.routes import router as post_router
from app.comment.routes import router as comment_router
from app.communities.routes import router as communities_router
from app.chat.routes import router as chat_router
from app.moderation.routes import router as moderation_router
from app.rating.routes import router as rating_router
from app.core.exceptions import add_exception_handlers
from app.badges.routes import router as badges_router

app = FastAPI(
    title='Space API',
    description='API for Space application',
    version='0.1.0',
)

routes = [
    admin_router,
    users_router,
    post_router,
    comment_router,
    communities_router,
    chat_router,
    moderation_router,
    badges_router,
    rating_router
]

for route in routes:
    app.include_router(route)


add_exception_handlers(app)
