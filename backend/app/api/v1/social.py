"""
Phase 7 – Social API endpoints.
Covers Friends, Follows, Activity Feed, and Social Notifications.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.social import (
    FriendRequestCreate,
    FriendshipResponse,
    UserSearchResponse,
    FollowResponse,
    ActivityFeedResponse,
)
from app.schemas.phase6 import NotificationResponse
from app.services.social_service import (
    FriendshipService,
    FollowService,
    ActivityFeedService,
)
from app.services.wearable_service import NotificationService

router = APIRouter(prefix="/social", tags=["Social Fitness"])


# ═══════════════════════════════════════════════════════════════════════
# FRIEND SYSTEM
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/friends/request",
    response_model=FriendshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send friend request",
)
def request_friend(
    data: FriendRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FriendshipResponse:
    try:
        friendship = FriendshipService.request_friend(db, current_user, data.receiver_id)
        return FriendshipResponse(
            id=friendship.id,
            requester_id=friendship.requester_id,
            receiver_id=friendship.receiver_id,
            status=friendship.status,
            requester_username=friendship.requester.username if friendship.requester else None,
            receiver_username=friendship.receiver.username if friendship.receiver else None,
            created_at=friendship.created_at,
            updated_at=friendship.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/friends/{friendship_id}/accept",
    response_model=FriendshipResponse,
    summary="Accept friend request",
)
def accept_friend(
    friendship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FriendshipResponse:
    try:
        friendship = FriendshipService.accept_friend(db, current_user, friendship_id)
        return FriendshipResponse(
            id=friendship.id,
            requester_id=friendship.requester_id,
            receiver_id=friendship.receiver_id,
            status=friendship.status,
            requester_username=friendship.requester.username if friendship.requester else None,
            receiver_username=friendship.receiver.username if friendship.receiver else None,
            created_at=friendship.created_at,
            updated_at=friendship.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/friends/{friendship_id}/reject",
    response_model=FriendshipResponse,
    summary="Reject friend request",
)
def reject_friend(
    friendship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FriendshipResponse:
    try:
        friendship = FriendshipService.reject_friend(db, current_user, friendship_id)
        return FriendshipResponse(
            id=friendship.id,
            requester_id=friendship.requester_id,
            receiver_id=friendship.receiver_id,
            status=friendship.status,
            requester_username=friendship.requester.username if friendship.requester else None,
            receiver_username=friendship.receiver.username if friendship.receiver else None,
            created_at=friendship.created_at,
            updated_at=friendship.updated_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/friends/{friendship_id}",
    summary="Remove a friend or cancel friend request",
)
def remove_friend(
    friendship_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        FriendshipService.remove_friend(db, current_user, friendship_id)
        return {"success": True, "message": "Friendship removed"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/friends",
    summary="List all accepted friends",
)
def get_friends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[dict]:
    return FriendshipService.get_friends(db, current_user)


@router.get(
    "/friends/pending",
    response_model=List[FriendshipResponse],
    summary="List incoming pending friend requests",
)
def get_pending_requests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[FriendshipResponse]:
    requests = FriendshipService.get_pending(db, current_user)
    return [FriendshipResponse(**r) for r in requests]


@router.get(
    "/users/search",
    response_model=List[UserSearchResponse],
    summary="Search athletes by username",
)
def search_users(
    q: str = Query(default="", description="Search query"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[UserSearchResponse]:
    results = FriendshipService.search_users(db, current_user, q)
    return [UserSearchResponse(**r) for r in results]


# ═══════════════════════════════════════════════════════════════════════
# FOLLOW SYSTEM
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/follow/{user_id}",
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Follow an athlete",
)
def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FollowResponse:
    try:
        follow = FollowService.follow(db, current_user, user_id)
        return FollowResponse(
            id=follow.id,
            follower_id=follow.follower_id,
            following_id=follow.following_id,
            username=follow.following.username if follow.following else "Athlete",
            bio=getattr(follow.following, "bio", None),
            avatar=getattr(follow.following, "avatar", None),
            created_at=follow.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/follow/{user_id}",
    summary="Unfollow an athlete",
)
def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        FollowService.unfollow(db, current_user, user_id)
        return {"success": True, "message": "Unfollowed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/followers",
    response_model=List[FollowResponse],
    summary="List athletes who follow you",
)
def get_followers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[FollowResponse]:
    followers = FollowService.get_followers(db, current_user)
    return [FollowResponse(**f) for f in followers]


@router.get(
    "/following",
    response_model=List[FollowResponse],
    summary="List athletes you follow",
)
def get_following(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[FollowResponse]:
    following = FollowService.get_following(db, current_user)
    return [FollowResponse(**f) for f in following]


# ═══════════════════════════════════════════════════════════════════════
# ACTIVITY FEED
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/feed",
    response_model=List[ActivityFeedResponse],
    summary="Global public activity feed",
)
def get_global_feed(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ActivityFeedResponse]:
    items = ActivityFeedService.get_global_feed(db, limit=limit, offset=offset)
    return [ActivityFeedResponse(**it) for it in items]


@router.get(
    "/feed/friends",
    response_model=List[ActivityFeedResponse],
    summary="Friends and following activity feed",
)
def get_friends_feed(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ActivityFeedResponse]:
    items = ActivityFeedService.get_friends_feed(db, current_user, limit=limit, offset=offset)
    return [ActivityFeedResponse(**it) for it in items]


# ═══════════════════════════════════════════════════════════════════════
# SOCIAL NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/notifications",
    response_model=List[NotificationResponse],
    summary="List social notifications",
)
def get_social_notifications(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[NotificationResponse]:
    notifs = NotificationService.get_all(db, current_user, limit=limit)
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.put(
    "/notifications/{id}/read",
    response_model=NotificationResponse,
    summary="Mark social notification as read",
)
def mark_notification_read(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    notif = NotificationService.mark_read(db, current_user, id)
    return NotificationResponse.model_validate(notif)


@router.put(
    "/notifications/read-all",
    summary="Mark all social notifications as read",
)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    count = NotificationService.mark_all_read(db, current_user)
    return {"marked_read": count}
