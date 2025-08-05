from app.core.config import settings
from app.core.database import Base, engine
from app.users.model import User
from app.post.model import ( 
    Post, 
    CampaignPost, 
    ComplaintPost, 
    PollPosts, 
    PollOptions, 
    PostFeedback, 
    PostLikes, 
    CampaignParticipants
)
from app.communities.model import CommunityMember, Community
from app.badges.model import Badge, MemberBadge
from app.rating.model import Rating
from app.comment.model import Comment, CommentLikes


if settings.TEST_MODE:
    Base.metadata.create_all(bind=engine)
