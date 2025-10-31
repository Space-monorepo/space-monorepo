import uuid
from datetime import datetime

import pytest

from app.api.reports.schema import (
    Author,
    CommentBriefReport,
    MemberBriefReport,
    ModerationVotesCreate,
    ModerationVotesResponse,
    PostBriefReport,
    ReportCommentCreate,
    ReportCreate,
    ReportMemberCreate,
    ReportPostCreate,
    ReportReasonEnum,
    ReportResponse,
    ReportTypeEnum,
    VoteTypeEnum,
)


@pytest.mark.unit
def test_report_schema():
    id = str(uuid.uuid4())
    reporter_id = str(uuid.uuid4())
    type = ReportTypeEnum.MEMBER_REPORT
    reason = ReportReasonEnum.DISCRIMINATION
    description = 'The description of the report'
    created_at = datetime.now()

    report = ReportCreate(
        reporter_id=reporter_id,
        type=type,
        reason=reason,
        description=description,
    )

    assert report.model_dump() == {
        'reporter_id': reporter_id,
        'type': type,
        'reason': reason,
        'description': description,
    }

    author = Author(
        id=reporter_id,
        name='John Doe',
        profile_picture='https://example.com/image.jpg',
        role='admin',
    )

    report_response = ReportResponse(
        id=id,
        reporter=author,
        type=type,
        reason=reason,
        description=description,
        created_at=created_at,
    )

    assert report_response.model_dump() == {
        'id': id,
        'reporter': author.model_dump(),
        'type': type,
        'reason': reason,
        'description': description,
        'created_at': created_at,
    }


@pytest.mark.unit
def test_report_member_schema():
    report_id = str(uuid.uuid4())
    member_id = str(uuid.uuid4())
    reporter_id = str(uuid.uuid4())
    reason = ReportReasonEnum.DISCRIMINATION
    community_id = str(uuid.uuid4())
    created_at = datetime.now()

    report_member = ReportMemberCreate(
        report_id=report_id,
        member_id=member_id,
        community_id=community_id,
    )

    assert report_member.model_dump() == {
        'report_id': report_id,
        'member_id': member_id,
        'community_id': community_id,
    }

    author = Author(
        id=reporter_id,
        name='John Doe',
        profile_picture='https://example.com/image.jpg',
        role='admin',
    )
    reports_count = 10
    member_reputation = 100
    member_popularity = 0.5

    member_brief_report = MemberBriefReport(
        member=author,
        reason=reason,
        reports_count=reports_count,
        member_reputation=member_reputation,
        member_popularity=member_popularity,
        member_entry_date=created_at,
    )

    assert member_brief_report.model_dump() == {
        'member': author.model_dump(),
        'reason': reason,
        'reports_count': reports_count,
        'member_reputation': member_reputation,
        'member_popularity': member_popularity,
        'member_entry_date': created_at,
    }


@pytest.mark.unit
def test_report_post_schema():
    id = str(uuid.uuid4())
    report_id = str(uuid.uuid4())
    post_id = str(uuid.uuid4())
    reporter_id = str(uuid.uuid4())
    type = ReportTypeEnum.POST_REPORT
    reason = ReportReasonEnum.DISCRIMINATION
    description = 'The description of the report'
    community_id = str(uuid.uuid4())
    created_at = datetime.now()

    report_post = ReportPostCreate(
        report_id=report_id,
        post_id=post_id,
        community_id=community_id,
    )

    assert report_post.model_dump() == {
        'report_id': report_id,
        'post_id': post_id,
        'community_id': community_id,
    }

    author = Author(
        id=reporter_id,
        name='John Doe',
        profile_picture='https://example.com/image.jpg',
        role='admin',
    )
    report_count = 10
    likes_count = 10
    comments_count = 10
    access_count = 10
    published_at = datetime.now()

    post_brief_report = PostBriefReport(
        post_id=post_id,
        member=author,
        reason=reason,
        title='Title of the post',
        content='Content of the post',
        image_url='https://example.com/image.jpg',
        report_count=report_count,
        likes_count=likes_count,
        comments_count=comments_count,
        access_count=access_count,
        published_at=published_at,
    )

    assert post_brief_report.model_dump() == {
        'post_id': post_id,
        'member': author.model_dump(),
        'reason': reason,
        'title': 'Title of the post',
        'content': 'Content of the post',
        'image_url': 'https://example.com/image.jpg',
        'report_count': report_count,
        'likes_count': likes_count,
        'comments_count': comments_count,
        'access_count': access_count,
        'published_at': published_at,
    }


@pytest.mark.unit
def test_report_comment_schema():
    id = str(uuid.uuid4())
    report_id = str(uuid.uuid4())
    comment_id = str(uuid.uuid4())
    reporter_id = str(uuid.uuid4())
    type = ReportTypeEnum.COMMENT_REPORT
    reason = ReportReasonEnum.DISCRIMINATION
    description = 'The description of the report'
    community_id = str(uuid.uuid4())
    created_at = datetime.now()

    report_comment = ReportCommentCreate(
        report_id=report_id,
        comment_id=comment_id,
        community_id=community_id,
    )

    assert report_comment.model_dump() == {
        'report_id': report_id,
        'comment_id': comment_id,
        'community_id': community_id,
    }

    author = Author(
        id=reporter_id,
        name='John Doe',
        profile_picture='https://example.com/image.jpg',
        role='admin',
    )
    report_count = 10
    likes_count = 10
    access_count = 10
    published_at = datetime.now()

    comment_brief_report = CommentBriefReport(
        comment_id=comment_id,
        member=author,
        reason=reason,
        content='Content of the comment',
        report_count=report_count,
        likes_count=likes_count,
        access_count=access_count,
        published_at=published_at,
    )

    assert comment_brief_report.model_dump() == {
        'comment_id': comment_id,
        'member': author.model_dump(),
        'reason': reason,
        'content': 'Content of the comment',
        'report_count': report_count,
        'likes_count': likes_count,
        'access_count': access_count,
        'published_at': published_at,
    }


@pytest.mark.unit
def test_moderation_votes_schema():
    id = str(uuid.uuid4())
    report_id = str(uuid.uuid4())
    moderator_id = str(uuid.uuid4())
    vote = VoteTypeEnum.SUSPEND
    created_at = datetime.now()

    moderation_votes = ModerationVotesCreate(
        report_id=report_id,
        moderator_id=moderator_id,
        vote=vote,
    )

    assert moderation_votes.model_dump() == {
        'report_id': report_id,
        'moderator_id': moderator_id,
        'vote': vote,
    }

    moderation_votes_response = ModerationVotesResponse(
        id=id,
        report_id=report_id,
        moderator_id=moderator_id,
        vote=vote,
        created_at=created_at,
    )

    assert moderation_votes_response.model_dump() == {
        'id': id,
        'report_id': report_id,
        'moderator_id': moderator_id,
        'vote': vote,
        'created_at': created_at,
    }
