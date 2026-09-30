"""
Phase 7 – Social Fitness Ecosystem Service Layer.
Production implementations for:
- FriendshipService
- FollowService
- ActivityFeedService
- XPService
- BadgeService
- ChallengeService
- TeamService
- LeaderboardService
- SocialProfileService
"""

import json
import math
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func, or_, and_
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.notification import Notification
from app.models.social import (
    Friendship,
    Follow,
    ActivityFeed,
    Challenge,
    ChallengeParticipant,
    UserLevel,
    Badge,
    UserBadge,
    Team,
    TeamMember,
)
from app.models.workout import WorkoutRecord
from app.models.step import StepRecord
from app.models.heart_rate_record import HeartRateRecord
from app.models.sleep_record import SleepRecord
from app.schemas.social import (
    ChallengeCreate,
    TeamCreate,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ══════════════════════════════════════════════════════════════════════
# 1 · XP & LEVELING SERVICE
# ══════════════════════════════════════════════════════════════════════

class XPService:
    """Manages athlete experience points and dynamic level calculations."""

    XP_WORKOUT = 50
    XP_STEP_GOAL = 25
    XP_WATER_GOAL = 15
    XP_CHALLENGE = 200
    XP_PERSONAL_RECORD = 100

    @staticmethod
    def calculate_level(xp: int) -> int:
        """Level formula: level = max(1, floor(sqrt(xp / 100)))."""
        if xp <= 0:
            return 1
        return max(1, int(math.floor(math.sqrt(xp / 100.0))))

    @staticmethod
    def get_next_level_xp(level: int) -> int:
        """Target XP required for next level."""
        return ((level + 1) ** 2) * 100

    @staticmethod
    def get_or_create(db: Session, user_id: int) -> UserLevel:
        lvl = db.query(UserLevel).filter(UserLevel.user_id == user_id).first()
        if not lvl:
            lvl = UserLevel(
                user_id=user_id,
                xp=0,
                level=1,
                total_workouts=0,
                total_steps=0,
                total_calories_burned=0.0,
            )
            db.add(lvl)
            db.commit()
            db.refresh(lvl)
        return lvl

    @classmethod
    def award_xp(
        cls,
        db: Session,
        user_id: int,
        amount: int,
        reason: str = "activity",
        increment_workouts: int = 0,
        increment_steps: int = 0,
        increment_calories: float = 0.0,
    ) -> UserLevel:
        lvl = cls.get_or_create(db, user_id)
        old_level = lvl.level

        lvl.xp += max(0, amount)
        new_level = cls.calculate_level(lvl.xp)
        lvl.level = new_level
        lvl.total_workouts += increment_workouts
        lvl.total_steps += increment_steps
        lvl.total_calories_burned += increment_calories
        lvl.updated_at = _utcnow()

        db.commit()
        db.refresh(lvl)

        # Notify level-up if promoted
        if new_level > old_level:
            notif = Notification(
                user_id=user_id,
                type="achievement",
                title="Level Up!",
                message=f"Congratulations! You reached Level {new_level} with {lvl.xp} XP.",
                priority="high",
                action_url="#/achievements",
            )
            db.add(notif)
            db.commit()

        return lvl


# ══════════════════════════════════════════════════════════════════════
# 2 · BADGES & ACHIEVEMENTS SERVICE
# ══════════════════════════════════════════════════════════════════════

class BadgeService:
    """Manages athletic badges and milestones."""

    DEFAULT_BADGES = [
        {"name": "First Workout", "description": "Complete your first logged workout session", "icon": "dumbbell", "category": "workout", "xp_reward": 50},
        {"name": "10K Walker", "description": "Reach 10,000 steps in a single day", "icon": "footprints", "category": "steps", "xp_reward": 75},
        {"name": "Hydration Hero", "description": "Hit your daily water intake target", "icon": "droplet", "category": "nutrition", "xp_reward": 50},
        {"name": "Consistency King", "description": "Maintain a 7-day fitness streak", "icon": "flame", "category": "streak", "xp_reward": 150},
        {"name": "Recovery Master", "description": "Achieve a Recovery Score of 85% or higher", "icon": "heart-pulse", "category": "recovery", "xp_reward": 100},
        {"name": "AI Athlete", "description": "Complete an AI biomechanic video form analysis or coach consultation", "icon": "bot", "category": "ai", "xp_reward": 100},
        {"name": "Challenge Champion", "description": "Successfully complete any community challenge", "icon": "trophy", "category": "challenge", "xp_reward": 200},
    ]

    @classmethod
    def ensure_defaults(cls, db: Session) -> None:
        """Seed default badges if not present."""
        for b_data in cls.DEFAULT_BADGES:
            exists = db.query(Badge).filter(Badge.name == b_data["name"]).first()
            if not exists:
                badge = Badge(**b_data)
                db.add(badge)
        db.commit()

    @classmethod
    def get_all(cls, db: Session, user: Optional[User] = None) -> List[Dict[str, Any]]:
        cls.ensure_defaults(db)
        badges = db.query(Badge).order_by(Badge.id.asc()).all()
        user_badge_ids = {}
        if user:
            ub_records = db.query(UserBadge).filter(UserBadge.user_id == user.id).all()
            user_badge_ids = {ub.badge_id: ub.earned_at for ub in ub_records}

        out = []
        for b in badges:
            earned_at = user_badge_ids.get(b.id)
            out.append({
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "category": b.category,
                "xp_reward": b.xp_reward,
                "is_earned": earned_at is not None,
                "earned_at": earned_at,
            })
        return out

    @classmethod
    def get_my_badges(cls, db: Session, user: User) -> List[Dict[str, Any]]:
        all_badges = cls.get_all(db, user)
        return [b for b in all_badges if b["is_earned"]]

    @classmethod
    def unlock_badge(cls, db: Session, user_id: int, badge_name: str) -> Optional[UserBadge]:
        cls.ensure_defaults(db)
        badge = db.query(Badge).filter(Badge.name == badge_name).first()
        if not badge:
            return None

        existing = db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id,
        ).first()
        if existing:
            return existing

        ub = UserBadge(user_id=user_id, badge_id=badge.id, earned_at=_utcnow())
        db.add(ub)
        db.commit()
        db.refresh(ub)

        # Award badge XP
        XPService.award_xp(db, user_id, badge.xp_reward, reason=f"Badge: {badge.name}")

        # Post activity feed
        user = db.query(User).filter(User.id == user_id).first()
        uname = user.username if user else "Athlete"
        ActivityFeedService.log_activity(
            db,
            user_id=user_id,
            activity_type="badge",
            title=f"Unlocked {badge.name}!",
            description=f"{uname} earned the '{badge.name}' badge (+{badge.xp_reward} XP)",
            metadata={"badge_id": badge.id, "badge_name": badge.name, "icon": badge.icon},
        )

        # Dispatch notification
        notif = Notification(
            user_id=user_id,
            type="achievement",
            title="Badge Unlocked!",
            message=f"You earned the {badge.name} badge (+{badge.xp_reward} XP)!",
            priority="high",
            action_url="#/achievements",
        )
        db.add(notif)
        db.commit()

        return ub


# ══════════════════════════════════════════════════════════════════════
# 3 · ACTIVITY FEED SERVICE
# ══════════════════════════════════════════════════════════════════════

class ActivityFeedService:
    """Timeline feed for social achievements and fitness activities."""

    @staticmethod
    def log_activity(
        db: Session,
        user_id: int,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ActivityFeed:
        meta_str = json.dumps(metadata) if metadata else None
        feed_item = ActivityFeed(
            user_id=user_id,
            activity_type=activity_type,
            title=title,
            description=description,
            metadata_json=meta_str,
            created_at=_utcnow(),
        )
        db.add(feed_item)
        db.commit()
        db.refresh(feed_item)
        return feed_item

    @staticmethod
    def get_global_feed(db: Session, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        items = (
            db.query(ActivityFeed)
            .order_by(desc(ActivityFeed.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        out = []
        for it in items:
            out.append({
                "id": it.id,
                "user_id": it.user_id,
                "username": it.user.username if it.user else "Athlete",
                "avatar": getattr(it.user, "avatar", None),
                "activity_type": it.activity_type,
                "title": it.title,
                "description": it.description,
                "metadata_json": it.metadata_json,
                "created_at": it.created_at,
            })
        return out

    @staticmethod
    def get_friends_feed(db: Session, user: User, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        # Find friends and followed user IDs
        friend_ids = set()
        friends_req = db.query(Friendship.receiver_id).filter(
            Friendship.requester_id == user.id, Friendship.status == "accepted"
        ).all()
        friends_rec = db.query(Friendship.requester_id).filter(
            Friendship.receiver_id == user.id, Friendship.status == "accepted"
        ).all()
        for (r_id,) in friends_req:
            friend_ids.add(r_id)
        for (r_id,) in friends_rec:
            friend_ids.add(r_id)

        following_q = db.query(Follow.following_id).filter(Follow.follower_id == user.id).all()
        for (f_id,) in following_q:
            friend_ids.add(f_id)

        # Include self in friends feed
        friend_ids.add(user.id)

        items = (
            db.query(ActivityFeed)
            .filter(ActivityFeed.user_id.in_(friend_ids))
            .order_by(desc(ActivityFeed.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        out = []
        for it in items:
            out.append({
                "id": it.id,
                "user_id": it.user_id,
                "username": it.user.username if it.user else "Athlete",
                "avatar": getattr(it.user, "avatar", None),
                "activity_type": it.activity_type,
                "title": it.title,
                "description": it.description,
                "metadata_json": it.metadata_json,
                "created_at": it.created_at,
            })
        return out


# ══════════════════════════════════════════════════════════════════════
# 4 · FRIENDSHIP SERVICE
# ══════════════════════════════════════════════════════════════════════

class FriendshipService:
    """Manages friend requests and bidirectional friendships."""

    @staticmethod
    def request_friend(db: Session, user: User, receiver_id: int) -> Friendship:
        if user.id == receiver_id:
            raise ValueError("You cannot send a friend request to yourself")

        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise ValueError("Target user not found")

        # Check existing
        existing = db.query(Friendship).filter(
            or_(
                and_(Friendship.requester_id == user.id, Friendship.receiver_id == receiver_id),
                and_(Friendship.requester_id == receiver_id, Friendship.receiver_id == user.id),
            )
        ).first()

        if existing:
            if existing.status == "accepted":
                raise ValueError("You are already friends")
            if existing.status == "pending":
                if existing.requester_id == user.id:
                    raise ValueError("Friend request already sent")
                else:
                    # Accept automatically if both sent
                    existing.status = "accepted"
                    existing.updated_at = _utcnow()
                    db.commit()
                    db.refresh(existing)
                    return existing
            # If rejected, reset to pending
            existing.requester_id = user.id
            existing.receiver_id = receiver_id
            existing.status = "pending"
            existing.updated_at = _utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        friendship = Friendship(
            requester_id=user.id,
            receiver_id=receiver_id,
            status="pending",
            created_at=_utcnow(),
            updated_at=_utcnow(),
        )
        db.add(friendship)
        db.commit()
        db.refresh(friendship)

        # Notify receiver
        notif = Notification(
            user_id=receiver_id,
            type="achievement",
            title="New Friend Request",
            message=f"{user.username} sent you a friend request!",
            priority="medium",
            action_url="#/friends",
        )
        db.add(notif)
        db.commit()

        return friendship

    @staticmethod
    def accept_friend(db: Session, user: User, friendship_id: int) -> Friendship:
        friendship = db.query(Friendship).filter(
            Friendship.id == friendship_id,
            Friendship.receiver_id == user.id,
        ).first()

        if not friendship:
            raise ValueError("Friend request not found or not addressed to you")

        friendship.status = "accepted"
        friendship.updated_at = _utcnow()
        db.commit()
        db.refresh(friendship)

        # Notify requester
        notif = Notification(
            user_id=friendship.requester_id,
            type="achievement",
            title="Friend Request Accepted",
            message=f"{user.username} accepted your friend request!",
            priority="medium",
            action_url="#/friends",
        )
        db.add(notif)
        db.commit()

        # Log activity
        ActivityFeedService.log_activity(
            db,
            user_id=user.id,
            activity_type="friend",
            title="Connected with a friend",
            description=f"{user.username} is now friends with {friendship.requester.username}",
        )

        return friendship

    @staticmethod
    def reject_friend(db: Session, user: User, friendship_id: int) -> Friendship:
        friendship = db.query(Friendship).filter(
            Friendship.id == friendship_id,
            Friendship.receiver_id == user.id,
        ).first()

        if not friendship:
            raise ValueError("Friend request not found or not addressed to you")

        friendship.status = "rejected"
        friendship.updated_at = _utcnow()
        db.commit()
        db.refresh(friendship)
        return friendship

    @staticmethod
    def remove_friend(db: Session, user: User, friendship_id: int) -> bool:
        friendship = db.query(Friendship).filter(
            Friendship.id == friendship_id,
            or_(Friendship.requester_id == user.id, Friendship.receiver_id == user.id),
        ).first()

        if not friendship:
            raise ValueError("Friendship not found")

        db.delete(friendship)
        db.commit()
        return True

    @staticmethod
    def get_friends(db: Session, user: User) -> List[Dict[str, Any]]:
        relations = db.query(Friendship).filter(
            Friendship.status == "accepted",
            or_(Friendship.requester_id == user.id, Friendship.receiver_id == user.id),
        ).all()

        out = []
        for f in relations:
            other = f.receiver if f.requester_id == user.id else f.requester
            out.append({
                "id": f.id,
                "requester_id": f.requester_id,
                "receiver_id": f.receiver_id,
                "status": f.status,
                "requester_username": f.requester.username if f.requester else None,
                "receiver_username": f.receiver.username if f.receiver else None,
                "friend_user_id": other.id,
                "friend_username": other.username,
                "friend_avatar": getattr(other, "avatar", None),
                "friend_bio": getattr(other, "bio", None),
                "created_at": f.created_at,
                "updated_at": f.updated_at,
            })
        return out

    @staticmethod
    def get_pending(db: Session, user: User) -> List[Dict[str, Any]]:
        incoming = db.query(Friendship).filter(
            Friendship.receiver_id == user.id,
            Friendship.status == "pending",
        ).all()

        return [
            {
                "id": f.id,
                "requester_id": f.requester_id,
                "receiver_id": f.receiver_id,
                "status": f.status,
                "requester_username": f.requester.username if f.requester else None,
                "receiver_username": user.username,
                "created_at": f.created_at,
                "updated_at": f.updated_at,
            }
            for f in incoming
        ]

    @staticmethod
    def search_users(db: Session, current_user: User, query_str: str) -> List[Dict[str, Any]]:
        if not query_str.strip():
            return []

        users = (
            db.query(User)
            .filter(
                User.id != current_user.id,
                User.username.ilike(f"%{query_str}%"),
            )
            .limit(20)
            .all()
        )

        out = []
        for u in users:
            # check friendship
            rel = db.query(Friendship).filter(
                or_(
                    and_(Friendship.requester_id == current_user.id, Friendship.receiver_id == u.id),
                    and_(Friendship.requester_id == u.id, Friendship.receiver_id == current_user.id),
                )
            ).first()

            # check following
            is_fol = db.query(Follow).filter(
                Follow.follower_id == current_user.id,
                Follow.following_id == u.id,
            ).first() is not None

            lvl = db.query(UserLevel).filter(UserLevel.user_id == u.id).first()

            out.append({
                "id": u.id,
                "username": u.username,
                "bio": getattr(u, "bio", None),
                "avatar": getattr(u, "avatar", None),
                "level": lvl.level if lvl else 1,
                "is_friend": rel.status == "accepted" if rel else False,
                "friend_status": rel.status if rel else None,
                "is_following": is_fol,
            })
        return out


# ══════════════════════════════════════════════════════════════════════
# 5 · FOLLOW SYSTEM SERVICE
# ══════════════════════════════════════════════════════════════════════

class FollowService:
    """Manages social athlete follow / following relationships."""

    @staticmethod
    def follow(db: Session, current_user: User, target_user_id: int) -> Follow:
        if current_user.id == target_user_id:
            raise ValueError("You cannot follow yourself")

        target = db.query(User).filter(User.id == target_user_id).first()
        if not target:
            raise ValueError("User not found")

        existing = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == target_user_id,
        ).first()

        if existing:
            return existing

        follow = Follow(
            follower_id=current_user.id,
            following_id=target_user_id,
            created_at=_utcnow(),
        )
        db.add(follow)
        db.commit()
        db.refresh(follow)

        # Notify target
        notif = Notification(
            user_id=target_user_id,
            type="achievement",
            title="New Follower",
            message=f"{current_user.username} started following your athletic journey!",
            priority="low",
            action_url=f"#/profile/{current_user.username}",
        )
        db.add(notif)
        db.commit()

        return follow

    @staticmethod
    def unfollow(db: Session, current_user: User, target_user_id: int) -> bool:
        follow = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == target_user_id,
        ).first()

        if not follow:
            raise ValueError("Not currently following this user")

        db.delete(follow)
        db.commit()
        return True

    @staticmethod
    def get_followers(db: Session, user: User) -> List[Dict[str, Any]]:
        relations = db.query(Follow).filter(Follow.following_id == user.id).all()
        return [
            {
                "id": f.id,
                "follower_id": f.follower_id,
                "following_id": f.following_id,
                "username": f.follower.username if f.follower else "Athlete",
                "avatar": getattr(f.follower, "avatar", None),
                "bio": getattr(f.follower, "bio", None),
                "created_at": f.created_at,
            }
            for f in relations
        ]

    @staticmethod
    def get_following(db: Session, user: User) -> List[Dict[str, Any]]:
        relations = db.query(Follow).filter(Follow.follower_id == user.id).all()
        return [
            {
                "id": f.id,
                "follower_id": f.follower_id,
                "following_id": f.following_id,
                "username": f.following.username if f.following else "Athlete",
                "avatar": getattr(f.following, "avatar", None),
                "bio": getattr(f.following, "bio", None),
                "created_at": f.created_at,
            }
            for f in relations
        ]


# ══════════════════════════════════════════════════════════════════════
# 6 · CHALLENGE SERVICE
# ══════════════════════════════════════════════════════════════════════

class ChallengeService:
    """Manages community challenges, enrollment, and progress scoring."""

    @staticmethod
    def create(db: Session, user: User, data: ChallengeCreate) -> Challenge:
        start_date = _utcnow()
        end_date = start_date + timedelta(days=data.duration_days)

        challenge = Challenge(
            title=data.title,
            description=data.description,
            challenge_type=data.challenge_type,
            target_value=data.target_value,
            duration_days=data.duration_days,
            reward_xp=data.reward_xp,
            created_by=user.id,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            created_at=start_date,
        )
        db.add(challenge)
        db.commit()
        db.refresh(challenge)

        # Creator automatically joins challenge
        part = ChallengeParticipant(
            challenge_id=challenge.id,
            user_id=user.id,
            progress=0.0,
            completed=False,
            joined_at=start_date,
        )
        db.add(part)
        db.commit()

        # Activity feed
        ActivityFeedService.log_activity(
            db,
            user_id=user.id,
            activity_type="challenge",
            title=f"Created Challenge: {challenge.title}",
            description=f"Join the '{challenge.title}' challenge to earn +{challenge.reward_xp} XP!",
            metadata={"challenge_id": challenge.id, "target": challenge.target_value, "type": challenge.challenge_type},
        )

        return challenge

    @staticmethod
    def get_all(db: Session, user: Optional[User] = None) -> List[Dict[str, Any]]:
        challenges = db.query(Challenge).order_by(desc(Challenge.created_at)).all()
        out = []
        for ch in challenges:
            parts = ch.participants
            user_part = next((p for p in parts if user and p.user_id == user.id), None)
            out.append({
                "id": ch.id,
                "title": ch.title,
                "description": ch.description,
                "challenge_type": ch.challenge_type,
                "target_value": ch.target_value,
                "duration_days": ch.duration_days,
                "reward_xp": ch.reward_xp,
                "created_by": ch.created_by,
                "creator_username": ch.creator.username if ch.creator else "FitAI Official",
                "start_date": ch.start_date,
                "end_date": ch.end_date,
                "is_active": ch.is_active,
                "participants_count": len(parts),
                "my_progress": user_part.progress if user_part else None,
                "is_joined": user_part is not None,
                "is_completed": user_part.completed if user_part else False,
            })
        return out

    @staticmethod
    def get_by_id(db: Session, challenge_id: int, user: Optional[User] = None) -> Dict[str, Any]:
        ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not ch:
            raise ValueError("Challenge not found")

        parts = ch.participants
        user_part = next((p for p in parts if user and p.user_id == user.id), None)
        return {
            "id": ch.id,
            "title": ch.title,
            "description": ch.description,
            "challenge_type": ch.challenge_type,
            "target_value": ch.target_value,
            "duration_days": ch.duration_days,
            "reward_xp": ch.reward_xp,
            "created_by": ch.created_by,
            "creator_username": ch.creator.username if ch.creator else "FitAI Official",
            "start_date": ch.start_date,
            "end_date": ch.end_date,
            "is_active": ch.is_active,
            "participants_count": len(parts),
            "my_progress": user_part.progress if user_part else None,
            "is_joined": user_part is not None,
            "is_completed": user_part.completed if user_part else False,
        }

    @staticmethod
    def join(db: Session, user: User, challenge_id: int) -> ChallengeParticipant:
        ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not ch:
            raise ValueError("Challenge not found")

        existing = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user.id,
        ).first()

        if existing:
            return existing

        part = ChallengeParticipant(
            challenge_id=challenge_id,
            user_id=user.id,
            progress=0.0,
            completed=False,
            joined_at=_utcnow(),
        )
        db.add(part)
        db.commit()
        db.refresh(part)
        return part

    @staticmethod
    def leave(db: Session, user: User, challenge_id: int) -> bool:
        part = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user.id,
        ).first()

        if not part:
            raise ValueError("You are not participating in this challenge")

        db.delete(part)
        db.commit()
        return True

    @staticmethod
    def get_my(db: Session, user: User) -> List[Dict[str, Any]]:
        all_challenges = ChallengeService.get_all(db, user)
        return [c for c in all_challenges if c["is_joined"]]

    @staticmethod
    def update_progress(
        db: Session,
        user_id: int,
        challenge_type: str,
        delta: float,
    ) -> List[ChallengeParticipant]:
        """Increments progress for all active challenges of this type for user."""
        parts = (
            db.query(ChallengeParticipant)
            .join(Challenge, Challenge.id == ChallengeParticipant.challenge_id)
            .filter(
                ChallengeParticipant.user_id == user_id,
                ChallengeParticipant.completed.is_(False),
                Challenge.is_active.is_(True),
                Challenge.challenge_type == challenge_type,
            )
            .all()
        )

        updated = []
        for p in parts:
            p.progress += delta
            ch = p.challenge
            if p.progress >= ch.target_value and not p.completed:
                p.completed = True
                # Award challenge reward XP
                XPService.award_xp(db, user_id, ch.reward_xp, reason=f"Completed {ch.title}")
                # Unlock Challenge Champion badge
                BadgeService.unlock_badge(db, user_id, "Challenge Champion")

                # Activity feed
                user = db.query(User).filter(User.id == user_id).first()
                uname = user.username if user else "Athlete"
                ActivityFeedService.log_activity(
                    db,
                    user_id=user_id,
                    activity_type="challenge",
                    title=f"Completed Challenge: {ch.title}!",
                    description=f"{uname} conquered the {ch.title} challenge (+{ch.reward_xp} XP)!",
                )

                # Dispatch notification
                notif = Notification(
                    user_id=user_id,
                    type="achievement",
                    title="Challenge Completed!",
                    message=f"You completed the '{ch.title}' challenge and earned +{ch.reward_xp} XP!",
                    priority="high",
                    action_url="#/challenges",
                )
                db.add(notif)
            updated.append(p)

        db.commit()
        return updated


# ══════════════════════════════════════════════════════════════════════
# 7 · TEAMS & COMMUNITIES SERVICE
# ══════════════════════════════════════════════════════════════════════

class TeamService:
    """Manages fitness teams, crews, and memberships."""

    @staticmethod
    def create(db: Session, user: User, data: TeamCreate) -> Team:
        existing = db.query(Team).filter(Team.name == data.name).first()
        if existing:
            raise ValueError(f"A team named '{data.name}' already exists")

        team = Team(
            name=data.name,
            description=data.description,
            owner_id=user.id,
            created_at=_utcnow(),
        )
        db.add(team)
        db.commit()
        db.refresh(team)

        # Creator is owner
        member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role="owner",
            joined_at=_utcnow(),
        )
        db.add(member)
        db.commit()

        # Activity
        ActivityFeedService.log_activity(
            db,
            user_id=user.id,
            activity_type="team",
            title=f"Founded Team: {team.name}",
            description=f"{user.username} founded a new community team: {team.name}",
        )

        return team

    @staticmethod
    def get_all(db: Session, user: Optional[User] = None) -> List[Dict[str, Any]]:
        teams = db.query(Team).order_by(desc(Team.created_at)).all()
        out = []
        for t in teams:
            members = t.members
            my_mem = next((m for m in members if user and m.user_id == user.id), None)
            out.append({
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "owner_id": t.owner_id,
                "owner_username": t.owner.username if t.owner else "Unknown",
                "members_count": len(members),
                "is_member": my_mem is not None,
                "my_role": my_mem.role if my_mem else None,
                "created_at": t.created_at,
            })
        return out

    @staticmethod
    def get_by_id(db: Session, team_id: int, user: Optional[User] = None) -> Dict[str, Any]:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        members = team.members
        my_mem = next((m for m in members if user and m.user_id == user.id), None)
        member_items = [
            {
                "id": m.id,
                "team_id": m.team_id,
                "user_id": m.user_id,
                "username": m.user.username if m.user else "Athlete",
                "role": m.role,
                "joined_at": m.joined_at,
            }
            for m in members
        ]

        return {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "owner_id": team.owner_id,
            "owner_username": team.owner.username if team.owner else "Unknown",
            "members_count": len(members),
            "is_member": my_mem is not None,
            "my_role": my_mem.role if my_mem else None,
            "created_at": team.created_at,
            "members": member_items,
        }

    @staticmethod
    def join(db: Session, user: User, team_id: int) -> TeamMember:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        existing = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id,
        ).first()

        if existing:
            return existing

        member = TeamMember(
            team_id=team_id,
            user_id=user.id,
            role="member",
            joined_at=_utcnow(),
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def leave(db: Session, user: User, team_id: int) -> bool:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id,
        ).first()

        if not member:
            raise ValueError("You are not a member of this team")

        if member.role == "owner":
            # If owner leaves and other members exist, promote next member or delete team
            other = db.query(TeamMember).filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id != user.id,
            ).first()
            if other:
                other.role = "owner"
                team.owner_id = other.user_id
            else:
                db.delete(team)
                db.commit()
                return True

        db.delete(member)
        db.commit()
        return True


# ══════════════════════════════════════════════════════════════════════
# 8 · LEADERBOARDS SERVICE
# ══════════════════════════════════════════════════════════════════════

class LeaderboardService:
    """Computes ranked leaderboards across steps, workouts, XP, recovery, and streaks."""

    @staticmethod
    def get_steps_leaderboard(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        # Sum steps per user
        results = (
            db.query(
                User.id,
                User.username,
                User.avatar,
                func.coalesce(func.sum(StepRecord.steps), 0).label("total_steps"),
            )
            .outerjoin(StepRecord, StepRecord.user_id == User.id)
            .group_by(User.id, User.username, User.avatar)
            .order_by(desc("total_steps"))
            .limit(limit)
            .all()
        )

        out = []
        for rank, (u_id, uname, av, steps_sum) in enumerate(results, start=1):
            lvl = db.query(UserLevel).filter(UserLevel.user_id == u_id).first()
            out.append({
                "rank": rank,
                "user_id": u_id,
                "username": uname,
                "avatar": av,
                "value": float(steps_sum),
                "unit": "steps",
                "level": lvl.level if lvl else 1,
            })
        return out

    @staticmethod
    def get_workouts_leaderboard(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        results = (
            db.query(
                User.id,
                User.username,
                User.avatar,
                func.count(WorkoutRecord.id).label("workout_count"),
            )
            .outerjoin(WorkoutRecord, WorkoutRecord.user_id == User.id)
            .group_by(User.id, User.username, User.avatar)
            .order_by(desc("workout_count"))
            .limit(limit)
            .all()
        )

        out = []
        for rank, (u_id, uname, av, w_count) in enumerate(results, start=1):
            lvl = db.query(UserLevel).filter(UserLevel.user_id == u_id).first()
            out.append({
                "rank": rank,
                "user_id": u_id,
                "username": uname,
                "avatar": av,
                "value": float(w_count),
                "unit": "workouts",
                "level": lvl.level if lvl else 1,
            })
        return out

    @staticmethod
    def get_xp_leaderboard(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        results = (
            db.query(
                User.id,
                User.username,
                User.avatar,
                func.coalesce(UserLevel.xp, 0).label("total_xp"),
                func.coalesce(UserLevel.level, 1).label("user_level"),
            )
            .outerjoin(UserLevel, UserLevel.user_id == User.id)
            .order_by(desc("total_xp"))
            .limit(limit)
            .all()
        )

        out = []
        for rank, (u_id, uname, av, xp_sum, lvl_val) in enumerate(results, start=1):
            out.append({
                "rank": rank,
                "user_id": u_id,
                "username": uname,
                "avatar": av,
                "value": float(xp_sum),
                "unit": "XP",
                "level": int(lvl_val),
            })
        return out

    @staticmethod
    def get_recovery_leaderboard(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        # Latest sleep quality score or latest sleep score as recovery ranking proxy
        results = (
            db.query(
                User.id,
                User.username,
                User.avatar,
                func.coalesce(func.max(SleepRecord.sleep_score), 75).label("best_recovery"),
            )
            .outerjoin(SleepRecord, SleepRecord.user_id == User.id)
            .group_by(User.id, User.username, User.avatar)
            .order_by(desc("best_recovery"))
            .limit(limit)
            .all()
        )

        out = []
        for rank, (u_id, uname, av, rec_score) in enumerate(results, start=1):
            lvl = db.query(UserLevel).filter(UserLevel.user_id == u_id).first()
            out.append({
                "rank": rank,
                "user_id": u_id,
                "username": uname,
                "avatar": av,
                "value": float(rec_score),
                "unit": "%",
                "level": lvl.level if lvl else 1,
            })
        return out

    @staticmethod
    def get_streaks_leaderboard(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        # Total distinct active days as athletic streak proxy
        results = (
            db.query(
                User.id,
                User.username,
                User.avatar,
                func.coalesce(func.count(func.distinct(func.date(WorkoutRecord.created_at))), 0).label("streak_days"),
            )
            .outerjoin(WorkoutRecord, WorkoutRecord.user_id == User.id)
            .group_by(User.id, User.username, User.avatar)
            .order_by(desc("streak_days"))
            .limit(limit)
            .all()
        )

        out = []
        for rank, (u_id, uname, av, streak_val) in enumerate(results, start=1):
            lvl = db.query(UserLevel).filter(UserLevel.user_id == u_id).first()
            out.append({
                "rank": rank,
                "user_id": u_id,
                "username": uname,
                "avatar": av,
                "value": float(max(1, streak_val)),
                "unit": "days",
                "level": lvl.level if lvl else 1,
            })
        return out


# ══════════════════════════════════════════════════════════════════════
# 9 · SOCIAL PROFILE SERVICE
# ══════════════════════════════════════════════════════════════════════

class SocialProfileService:
    """Aggregates and formats complete public athlete profile data."""

    @staticmethod
    def get_public_profile(db: Session, username: str, current_user: Optional[User] = None) -> Dict[str, Any]:
        target = db.query(User).filter(User.username == username).first()
        if not target:
            raise ValueError(f"Athlete profile '{username}' not found")

        # XP & Level
        lvl = XPService.get_or_create(db, target.id)

        # Badges
        badges = BadgeService.get_my_badges(db, target)

        # Follow counts
        followers_count = db.query(Follow).filter(Follow.following_id == target.id).count()
        following_count = db.query(Follow).filter(Follow.follower_id == target.id).count()

        # Workouts count
        total_workouts = db.query(WorkoutRecord).filter(WorkoutRecord.user_id == target.id).count()

        # Steps count
        step_sum = db.query(func.sum(StepRecord.steps)).filter(StepRecord.user_id == target.id).scalar() or 0

        # Latest recovery
        latest_sleep = db.query(SleepRecord).filter(SleepRecord.user_id == target.id).order_by(desc(SleepRecord.created_at)).first()
        recovery_score = latest_sleep.sleep_score if latest_sleep else 80

        # Streak calculation
        streak_days = db.query(func.count(func.distinct(func.date(WorkoutRecord.created_at)))).filter(
            WorkoutRecord.user_id == target.id
        ).scalar() or 1

        is_following = False
        is_friend = False
        if current_user and current_user.id != target.id:
            is_following = db.query(Follow).filter(
                Follow.follower_id == current_user.id,
                Follow.following_id == target.id,
            ).first() is not None

            rel = db.query(Friendship).filter(
                Friendship.status == "accepted",
                or_(
                    and_(Friendship.requester_id == current_user.id, Friendship.receiver_id == target.id),
                    and_(Friendship.requester_id == target.id, Friendship.receiver_id == current_user.id),
                ),
            ).first()
            is_friend = rel is not None

        return {
            "username": target.username,
            "avatar": getattr(target, "avatar", None),
            "bio": getattr(target, "bio", None),
            "level": lvl.level,
            "xp": lvl.xp,
            "badges": badges,
            "followers": followers_count,
            "following": following_count,
            "current_streak": max(1, streak_days),
            "recovery_score": recovery_score,
            "total_workouts": total_workouts,
            "total_steps": int(step_sum),
            "is_following": is_following,
            "is_friend": is_friend,
        }
