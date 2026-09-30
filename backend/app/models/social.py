"""
Phase 7 – Social Fitness Ecosystem SQLAlchemy Models.
Includes Friendship, Follow, ActivityFeed, Challenge, ChallengeParticipant,
UserLevel, Badge, UserBadge, Team, and TeamMember.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Friendship(Base):
    """Represents a friend relationship between two users."""

    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    requester_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, accepted, rejected, blocked
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    requester = relationship("User", foreign_keys=[requester_id], backref="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_friend_requests")

    __table_args__ = (
        UniqueConstraint("requester_id", "receiver_id", name="uq_friendship_requester_receiver"),
        Index("ix_friendship_status_receiver", "receiver_id", "status"),
    )


class Follow(Base):
    """Represents an athlete follow relationship."""

    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    follower_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    following_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    follower = relationship("User", foreign_keys=[follower_id], backref="following_relations")
    following = relationship("User", foreign_keys=[following_id], backref="follower_relations")

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow_follower_following"),
    )


class ActivityFeed(Base):
    """Social timeline event generated from workouts, badges, PRs, and milestones."""

    __tablename__ = "activity_feed"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    activity_type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", backref="activities")


class Challenge(Base):
    """Community fitness challenge."""

    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    challenge_type = Column(String(50), nullable=False, index=True)  # steps, water, workouts, calories, distance, sleep, recovery
    target_value = Column(Float, nullable=False)
    duration_days = Column(Integer, default=7, nullable=False)
    reward_xp = Column(Integer, default=200, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(DateTime, default=_utcnow, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("ChallengeParticipant", back_populates="challenge", cascade="all, delete-orphan")


class ChallengeParticipant(Base):
    """Participant in a community challenge."""

    __tablename__ = "challenge_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    challenge_id = Column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    progress = Column(Float, default=0.0, nullable=False)
    completed = Column(Boolean, default=False, nullable=False, index=True)
    joined_at = Column(DateTime, default=_utcnow, nullable=False)

    challenge = relationship("Challenge", back_populates="participants")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("challenge_id", "user_id", name="uq_challenge_participant"),
    )


class UserLevel(Base):
    """XP progression and level status for an athlete."""

    __tablename__ = "user_levels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    total_workouts = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, default=0, nullable=False)
    total_calories_burned = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User", backref="level_info")


class Badge(Base):
    """Achievement badge specification."""

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(100), default="award", nullable=False)
    category = Column(String(50), default="general", nullable=False)
    xp_reward = Column(Integer, default=100, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)


class UserBadge(Base):
    """Badge unlocked by an athlete."""

    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_id = Column(
        Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    earned_at = Column(DateTime, default=_utcnow, nullable=False)

    user = relationship("User", backref="user_badges")
    badge = relationship("Badge")

    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),
    )


class Team(Base):
    """Community club or athletic team."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """Member roster for a team."""

    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(20), default="member", nullable=False)  # owner, admin, member
    joined_at = Column(DateTime, default=_utcnow, nullable=False)

    team = relationship("Team", back_populates="members")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_member"),
    )
