"""
Phase 7 – Social Fitness Ecosystem Pydantic Schemas.
Covers Friends, Follows, ActivityFeed, Challenges, XP, Badges, Teams, Leaderboards, and Profiles.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Friends & Search ───────────────────────────────────────────────────

class FriendRequestCreate(BaseModel):
    """Payload to request friendship."""
    receiver_id: int = Field(..., description="Target user ID to add as friend")


class FriendshipResponse(BaseModel):
    """Friendship relationship record."""
    id: int
    requester_id: int
    receiver_id: int
    status: str
    requester_username: Optional[str] = None
    receiver_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSearchResponse(BaseModel):
    """User summary returned from athlete search."""
    id: int
    username: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    level: int = 1
    is_friend: bool = False
    friend_status: Optional[str] = None
    is_following: bool = False


# ── Follow System ──────────────────────────────────────────────────────

class FollowResponse(BaseModel):
    """Follow relation record."""
    id: int
    follower_id: int
    following_id: int
    username: str
    bio: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Activity Feed ──────────────────────────────────────────────────────

class ActivityFeedResponse(BaseModel):
    """Activity feed timeline item."""
    id: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    activity_type: str
    title: str
    description: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Challenges ─────────────────────────────────────────────────────────

class ChallengeCreate(BaseModel):
    """Payload to create a community challenge."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    challenge_type: str = Field(..., description="steps, water, workouts, calories, distance, sleep, recovery")
    target_value: float = Field(..., gt=0)
    duration_days: int = Field(default=7, ge=1, le=90)
    reward_xp: int = Field(default=200, ge=10, le=5000)


class ChallengeParticipantResponse(BaseModel):
    """Participant state in a challenge."""
    id: int
    challenge_id: int
    user_id: int
    username: Optional[str] = None
    progress: float
    completed: bool
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChallengeResponse(BaseModel):
    """Challenge details."""
    id: int
    title: str
    description: Optional[str] = None
    challenge_type: str
    target_value: float
    duration_days: int
    reward_xp: int
    created_by: Optional[int] = None
    creator_username: Optional[str] = None
    start_date: datetime
    end_date: datetime
    is_active: bool
    participants_count: int = 0
    my_progress: Optional[float] = None
    is_joined: bool = False
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)


# ── XP & User Levels ───────────────────────────────────────────────────

class UserLevelResponse(BaseModel):
    """Athlete XP and leveling progression."""
    id: int
    user_id: int
    xp: int
    level: int
    total_workouts: int
    total_steps: int
    total_calories_burned: float
    next_level_xp: int
    progress_percent: float

    model_config = ConfigDict(from_attributes=True)


# ── Badges & Achievements ──────────────────────────────────────────────

class BadgeResponse(BaseModel):
    """Badge representation."""
    id: int
    name: str
    description: str
    icon: str
    category: str
    xp_reward: int
    is_earned: bool = False
    earned_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AchievementsOverviewResponse(BaseModel):
    """Summary of all badges and athlete progression."""
    total_badges: int
    earned_count: int
    badges: List[BadgeResponse]
    user_level: UserLevelResponse


# ── Teams & Communities ────────────────────────────────────────────────

class TeamCreate(BaseModel):
    """Payload to create an athletic team."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class TeamMemberResponse(BaseModel):
    """Team member roster item."""
    id: int
    team_id: int
    user_id: int
    username: str
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamResponse(BaseModel):
    """Team details and member count."""
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    owner_username: Optional[str] = None
    members_count: int = 0
    is_member: bool = False
    my_role: Optional[str] = None
    created_at: datetime
    members: Optional[List[TeamMemberResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# ── Leaderboards ───────────────────────────────────────────────────────

class LeaderboardEntry(BaseModel):
    """Leaderboard ranking row."""
    rank: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    value: float
    unit: str
    level: int = 1


# ── Social Public Profile ──────────────────────────────────────────────

class PublicProfileResponse(BaseModel):
    """Complete public athlete profile."""
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    level: int = 1
    xp: int = 0
    badges: List[BadgeResponse] = []
    followers: int = 0
    following: int = 0
    current_streak: int = 0
    recovery_score: int = 0
    total_workouts: int = 0
    total_steps: int = 0
    is_following: bool = False
    is_friend: bool = False
