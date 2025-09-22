from app.core.config import settings
from app.core.database import Base, engine
from app.api.users.model import User
from app.api.post.model import (
    Post,
    CampaignPost,
    ComplaintPost,
    PollPosts,
    PollOptions,
    PostFeedback,
    PostLikes,
    CampaignParticipants
)
from app.api.communities.model import CommunityMember, Community
from app.api.badges.model import Badge, MemberBadge
from app.api.rating.model import Rating
from app.api.comment.model import Comment, CommentLikes
from app.api.chat.model import Conversation, Message, MessageAttachment


Base.metadata.create_all(bind=engine)
