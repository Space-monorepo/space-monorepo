from fastapi import FastAPI
from fastapi.middleware import cors

from app.core.exceptions import add_exception_handlers

from app.api.administration.routes import router as admin_router
from app.api.badges.routes import (
    router as badges_router,
    admin_router as badges_admin_router,
)
from app.api.chat.routes import router as chat_router
from app.api.comment.routes import router as comment_router
from app.api.communities.routes import router as communities_router
from app.api.moderation.routes import router as moderation_router
from app.api.post.routes import router as post_router
from app.api.rating.routes import router as rating_router
from app.api.users.routes import router as users_router
from app.api.search.routes import router as search_router

app = FastAPI(
    title='Space API',
    description='API for Space application',
    version='0.1.0',
)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
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
    badges_admin_router,
    rating_router,
    search_router,
]

for route in routes:
    app.include_router(route)


add_exception_handlers(app)
