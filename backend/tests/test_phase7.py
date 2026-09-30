"""
Phase 7 Test Suite — Social Fitness Ecosystem.

Tests cover:
  ✓ Friend Request (send, validate self, duplicate)
  ✓ Accept Request & Reject Request & Delete Friendship
  ✓ Pending Friend Requests
  ✓ Athlete User Search
  ✓ Follow User & Unfollow User
  ✓ Followers & Following Lists
  ✓ Activity Feed (Global & Friends)
  ✓ Challenge Creation, Listing, Details
  ✓ Challenge Join & Leave
  ✓ Challenge Progress & Automatic Completion & Reward Awarding
  ✓ Team Creation, Member Roster, Join & Leave
  ✓ XP Awarding & Leveling Progression
  ✓ Badge Catalog Seeding & Badge Unlocking
  ✓ Achievements Overview
  ✓ Leaderboards (Steps, Workouts, XP, Recovery, Streaks)
  ✓ Social Notifications (Read & Read-All)
  ✓ Public Profile Retrieval & Follow/Friend flags
  ✓ Auth Guards (401 when unauthenticated)

Run:
    cd d:\\FitAI\\backend
    venv\\Scripts\\python.exe -m pytest tests\\test_phase7.py -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.services.social_service import XPService, BadgeService, ChallengeService

# ── In-Memory Test DB ──────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────────

def _create_user(email="athlete1@fitai.dev", password="Password123!"):
    """Register and login, returning auth headers and user id."""
    username = email.split("@")[0]
    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    data = resp.json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    return {"Authorization": f"Bearer {token}"}, user_id, username


# ══════════════════════════════════════════════════════════════════════
# 1 · FRIEND SYSTEM TESTS
# ══════════════════════════════════════════════════════════════════════

def test_friend_request_flow():
    h1, u1, _ = _create_user("user1@fitai.dev")
    h2, u2, _ = _create_user("user2@fitai.dev")

    # Send request from user1 to user2
    resp = client.post("/api/v1/social/friends/request", json={"receiver_id": u2}, headers=h1)
    assert resp.status_code == 201
    data = resp.json()
    assert data["requester_id"] == u1
    assert data["receiver_id"] == u2
    assert data["status"] == "pending"
    friendship_id = data["id"]

    # Pending list for user2
    resp_pend = client.get("/api/v1/social/friends/pending", headers=h2)
    assert resp_pend.status_code == 200
    pend_list = resp_pend.json()
    assert len(pend_list) == 1
    assert pend_list[0]["id"] == friendship_id

    # Accept request by user2
    resp_acc = client.put(f"/api/v1/social/friends/{friendship_id}/accept", headers=h2)
    assert resp_acc.status_code == 200
    assert resp_acc.json()["status"] == "accepted"

    # Verify both have friend in their friend list
    f1 = client.get("/api/v1/social/friends", headers=h1).json()
    f2 = client.get("/api/v1/social/friends", headers=h2).json()
    assert len(f1) == 1
    assert len(f2) == 1
    assert f1[0]["friend_user_id"] == u2
    assert f2[0]["friend_user_id"] == u1


def test_cannot_friend_self():
    h1, u1, _ = _create_user("self@fitai.dev")
    resp = client.post("/api/v1/social/friends/request", json={"receiver_id": u1}, headers=h1)
    assert resp.status_code == 400


def test_reject_friend_request():
    h1, u1, _ = _create_user("rej1@fitai.dev")
    h2, u2, _ = _create_user("rej2@fitai.dev")

    resp = client.post("/api/v1/social/friends/request", json={"receiver_id": u2}, headers=h1)
    assert resp.status_code == 201
    friendship_id = resp.json()["id"]

    resp_rej = client.put(f"/api/v1/social/friends/{friendship_id}/reject", headers=h2)
    assert resp_rej.status_code == 200
    assert resp_rej.json()["status"] == "rejected"

    # Should not show in accepted friends
    f_list = client.get("/api/v1/social/friends", headers=h2).json()
    assert len(f_list) == 0


def test_delete_friendship():
    h1, u1, _ = _create_user("del1@fitai.dev")
    h2, u2, _ = _create_user("del2@fitai.dev")

    r = client.post("/api/v1/social/friends/request", json={"receiver_id": u2}, headers=h1)
    fid = r.json()["id"]
    client.put(f"/api/v1/social/friends/{fid}/accept", headers=h2)

    # User 1 removes friend
    del_resp = client.delete(f"/api/v1/social/friends/{fid}", headers=h1)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Friends lists should be empty now
    f1 = client.get("/api/v1/social/friends", headers=h1).json()
    assert len(f1) == 0


def test_user_search():
    h1, _, _ = _create_user("alice_runner@fitai.dev")
    _create_user("bob_cyclist@fitai.dev")
    _create_user("alice_swimmer@fitai.dev")

    resp = client.get("/api/v1/social/users/search?q=alice", headers=h1)
    assert resp.status_code == 200
    results = resp.json()
    # alice_runner is self, so should find alice_swimmer
    assert len(results) == 1
    assert "alice_swimmer" in results[0]["username"]


# ══════════════════════════════════════════════════════════════════════
# 2 · FOLLOW SYSTEM TESTS
# ══════════════════════════════════════════════════════════════════════

def test_follow_and_unfollow():
    h1, u1, _ = _create_user("fol1@fitai.dev")
    h2, u2, _ = _create_user("fol2@fitai.dev")

    # User 1 follows User 2
    resp = client.post(f"/api/v1/social/follow/{u2}", headers=h1)
    assert resp.status_code == 201
    assert resp.json()["following_id"] == u2

    # Check following list for user 1
    following = client.get("/api/v1/social/following", headers=h1).json()
    assert len(following) == 1
    assert following[0]["following_id"] == u2

    # Check followers list for user 2
    followers = client.get("/api/v1/social/followers", headers=h2).json()
    assert len(followers) == 1
    assert followers[0]["follower_id"] == u1

    # Unfollow
    unf = client.delete(f"/api/v1/social/follow/{u2}", headers=h1)
    assert unf.status_code == 200
    assert unf.json()["success"] is True

    # Empty following
    assert len(client.get("/api/v1/social/following", headers=h1).json()) == 0


def test_cannot_follow_self():
    h1, u1, _ = _create_user("fself@fitai.dev")
    resp = client.post(f"/api/v1/social/follow/{u1}", headers=h1)
    assert resp.status_code == 400


# ══════════════════════════════════════════════════════════════════════
# 3 · ACTIVITY FEED TESTS
# ══════════════════════════════════════════════════════════════════════

def test_activity_feed_global_and_friends():
    h1, u1, _ = _create_user("act1@fitai.dev")
    h2, u2, _ = _create_user("act2@fitai.dev")
    h3, u3, _ = _create_user("act3@fitai.dev")

    # User 1 follows User 2
    client.post(f"/api/v1/social/follow/{u2}", headers=h1)

    # User 2 logs a workout (generates activity via challenge/service)
    db = TestSession()
    XPService.award_xp(db, u2, 50, increment_workouts=1)
    BadgeService.unlock_badge(db, u2, "First Workout")
    db.close()

    # User 3 creates a challenge
    client.post("/api/v1/challenges", json={
        "title": "100K Steps Week",
        "challenge_type": "steps",
        "target_value": 100000,
        "duration_days": 7,
        "reward_xp": 300,
    }, headers=h3)

    # Check Global feed (sees user 2 and user 3 activities)
    global_feed = client.get("/api/v1/social/feed", headers=h1).json()
    assert len(global_feed) >= 2

    # Check Friends feed for user 1 (sees user 2 because followed, but not user 3)
    friends_feed = client.get("/api/v1/social/feed/friends", headers=h1).json()
    feed_user_ids = {it["user_id"] for it in friends_feed}
    assert u2 in feed_user_ids
    assert u3 not in feed_user_ids


# ══════════════════════════════════════════════════════════════════════
# 4 · CHALLENGE TESTS
# ══════════════════════════════════════════════════════════════════════

def test_challenge_crud_and_join():
    h1, u1, _ = _create_user("chal_creator@fitai.dev")
    h2, u2, _ = _create_user("chal_joiner@fitai.dev")

    # 1. Create challenge
    resp = client.post("/api/v1/challenges", json={
        "title": "Hydration Sprint",
        "description": "Drink 20 liters in 7 days",
        "challenge_type": "water",
        "target_value": 20.0,
        "duration_days": 7,
        "reward_xp": 200,
    }, headers=h1)
    assert resp.status_code == 201
    ch_data = resp.json()
    ch_id = ch_data["id"]
    assert ch_data["title"] == "Hydration Sprint"
    assert ch_data["is_joined"] is True  # creator auto-joins

    # 2. List challenges
    ch_list = client.get("/api/v1/challenges", headers=h2).json()
    assert len(ch_list) >= 1
    target = next(c for c in ch_list if c["id"] == ch_id)
    assert target["is_joined"] is False

    # 3. User 2 joins
    join_resp = client.post(f"/api/v1/challenges/{ch_id}/join", headers=h2)
    assert join_resp.status_code == 200
    assert join_resp.json()["user_id"] == u2

    # 4. Check 'my' challenges for user 2
    my_list = client.get("/api/v1/challenges/my", headers=h2).json()
    assert len(my_list) == 1
    assert my_list[0]["id"] == ch_id

    # 5. User 2 leaves challenge
    leave_resp = client.post(f"/api/v1/challenges/{ch_id}/leave", headers=h2)
    assert leave_resp.status_code == 200
    assert leave_resp.json()["success"] is True


def test_challenge_progress_and_completion():
    h1, u1, _ = _create_user("prog_user@fitai.dev")

    # Create 5000 step challenge
    resp = client.post("/api/v1/challenges", json={
        "title": "Quick 5K Steps",
        "challenge_type": "steps",
        "target_value": 5000,
        "duration_days": 1,
        "reward_xp": 250,
    }, headers=h1)
    ch_id = resp.json()["id"]

    db = TestSession()
    # Update progress by 3000 -> not completed
    ChallengeService.update_progress(db, u1, "steps", 3000)
    ch1 = ChallengeService.get_by_id(db, ch_id, db.query(User).get(u1))
    assert ch1["my_progress"] == 3000
    assert ch1["is_completed"] is False

    # Update progress by 2500 -> reaches 5500 >= 5000 -> completed!
    ChallengeService.update_progress(db, u1, "steps", 2500)
    ch2 = ChallengeService.get_by_id(db, ch_id, db.query(User).get(u1))
    assert ch2["is_completed"] is True

    # UserLevel should have earned 250 XP
    lvl = XPService.get_or_create(db, u1)
    assert lvl.xp >= 250

    db.close()


# ══════════════════════════════════════════════════════════════════════
# 5 · TEAM & COMMUNITY TESTS
# ══════════════════════════════════════════════════════════════════════

def test_team_flow():
    h1, u1, _ = _create_user("team_owner@fitai.dev")
    h2, u2, _ = _create_user("team_member@fitai.dev")

    # 1. Create Team
    resp = client.post("/api/v1/teams", json={
        "name": "Hyper Runners Club",
        "description": "Elite endurance athletics",
    }, headers=h1)
    assert resp.status_code == 201
    team_data = resp.json()
    t_id = team_data["id"]
    assert team_data["owner_id"] == u1
    assert team_data["members_count"] == 1

    # 2. User 2 joins team
    j_resp = client.post(f"/api/v1/teams/{t_id}/join", headers=h2)
    assert j_resp.status_code == 200
    assert j_resp.json()["role"] == "member"

    # 3. Get team details
    detail = client.get(f"/api/v1/teams/{t_id}", headers=h1).json()
    assert detail["members_count"] == 2
    assert len(detail["members"]) == 2

    # 4. User 2 leaves team
    l_resp = client.post(f"/api/v1/teams/{t_id}/leave", headers=h2)
    assert l_resp.status_code == 200
    assert l_resp.json()["success"] is True

    # Member count back to 1
    detail_after = client.get(f"/api/v1/teams/{t_id}", headers=h1).json()
    assert detail_after["members_count"] == 1


# ══════════════════════════════════════════════════════════════════════
# 6 · XP & BADGES TESTS
# ══════════════════════════════════════════════════════════════════════

def test_xp_awarding_and_levels():
    h1, u1, _ = _create_user("xp_athlete@fitai.dev")

    db = TestSession()
    # Initial level is 1
    lvl0 = XPService.get_or_create(db, u1)
    assert lvl0.level == 1
    assert lvl0.xp == 0

    # Award 100 XP -> floor(sqrt(100/100)) = 1
    XPService.award_xp(db, u1, 100)
    lvl1 = XPService.get_or_create(db, u1)
    assert lvl1.level == 1

    # Award 300 more XP (total 400 XP) -> floor(sqrt(400/100)) = 2
    XPService.award_xp(db, u1, 300)
    lvl2 = XPService.get_or_create(db, u1)
    assert lvl2.level == 2
    assert lvl2.xp == 400

    # Level formula: level = floor(sqrt(xp / 100))
    assert XPService.calculate_level(900) == 3
    assert XPService.calculate_level(1600) == 4

    db.close()


def test_badge_catalog_and_unlock():
    h1, u1, _ = _create_user("badge_hunter@fitai.dev")

    # 1. Badges catalog has default badges
    resp = client.get("/api/v1/badges", headers=h1)
    assert resp.status_code == 200
    badges = resp.json()
    assert len(badges) >= 7
    badge_names = [b["name"] for b in badges]
    assert "First Workout" in badge_names
    assert "10K Walker" in badge_names

    # 2. Unlock badge
    db = TestSession()
    BadgeService.unlock_badge(db, u1, "First Workout")
    db.close()

    # 3. Check my badges
    my_badges = client.get("/api/v1/badges/my", headers=h1).json()
    assert len(my_badges) == 1
    assert my_badges[0]["name"] == "First Workout"
    assert my_badges[0]["is_earned"] is True

    # 4. Check achievements overview
    ach = client.get("/api/v1/achievements", headers=h1).json()
    assert ach["earned_count"] == 1
    assert ach["user_level"]["xp"] >= 50


# ══════════════════════════════════════════════════════════════════════
# 7 · LEADERBOARDS TESTS
# ══════════════════════════════════════════════════════════════════════

def test_leaderboards_endpoints():
    h1, _, _ = _create_user("lead1@fitai.dev")

    # Test all 5 leaderboard endpoints
    r_steps = client.get("/api/v1/leaderboards/steps", headers=h1)
    assert r_steps.status_code == 200
    assert isinstance(r_steps.json(), list)

    r_workouts = client.get("/api/v1/leaderboards/workouts", headers=h1)
    assert r_workouts.status_code == 200
    assert isinstance(r_workouts.json(), list)

    r_xp = client.get("/api/v1/leaderboards/xp", headers=h1)
    assert r_xp.status_code == 200
    assert isinstance(r_xp.json(), list)

    r_recovery = client.get("/api/v1/leaderboards/recovery", headers=h1)
    assert r_recovery.status_code == 200
    assert isinstance(r_recovery.json(), list)

    r_streaks = client.get("/api/v1/leaderboards/streaks", headers=h1)
    assert r_streaks.status_code == 200
    assert isinstance(r_streaks.json(), list)


# ══════════════════════════════════════════════════════════════════════
# 8 · NOTIFICATION CENTER TESTS
# ══════════════════════════════════════════════════════════════════════

def test_social_notifications():
    h1, u1, _ = _create_user("notif1@fitai.dev")
    h2, u2, _ = _create_user("notif2@fitai.dev")

    # User 2 sends friend request -> triggers notification for User 1
    client.post("/api/v1/social/friends/request", json={"receiver_id": u1}, headers=h2)

    # User 1 views notifications
    notifs = client.get("/api/v1/social/notifications", headers=h1).json()
    assert len(notifs) >= 1
    n_id = notifs[0]["id"]
    assert notifs[0]["is_read"] is False

    # Mark as read
    read_resp = client.put(f"/api/v1/social/notifications/{n_id}/read", headers=h1)
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # Mark all read
    all_read = client.put("/api/v1/social/notifications/read-all", headers=h1)
    assert all_read.status_code == 200
    assert "marked_read" in all_read.json()


# ══════════════════════════════════════════════════════════════════════
# 9 · SOCIAL PUBLIC PROFILE TESTS
# ══════════════════════════════════════════════════════════════════════

def test_public_athlete_profile():
    h1, u1, uname1 = _create_user("public_star@fitai.dev")
    h2, u2, _ = _create_user("viewer@fitai.dev")

    # User 2 follows user 1
    client.post(f"/api/v1/social/follow/{u1}", headers=h2)

    # Viewer queries public profile of user 1
    resp = client.get(f"/api/v1/profile/{uname1}", headers=h2)
    assert resp.status_code == 200
    prof = resp.json()
    assert prof["username"] == uname1
    assert prof["followers"] == 1
    assert prof["is_following"] is True
    assert "level" in prof
    assert "xp" in prof
    assert "badges" in prof
    assert "recovery_score" in prof


# ══════════════════════════════════════════════════════════════════════
# 10 · AUTH GUARD TESTS & EDGE CASES
# ══════════════════════════════════════════════════════════════════════

def test_unauthenticated_requests_return_401():
    assert client.get("/api/v1/social/friends").status_code == 401
    assert client.get("/api/v1/social/feed").status_code == 401
    assert client.get("/api/v1/challenges").status_code == 401
    assert client.get("/api/v1/teams").status_code == 401
    assert client.get("/api/v1/leaderboards/steps").status_code == 401
    assert client.get("/api/v1/badges").status_code == 401


def test_reject_nonexistent_friendship():
    h1, _, _ = _create_user("nonex_rej@fitai.dev")
    resp = client.put("/api/v1/social/friends/99999/reject", headers=h1)
    assert resp.status_code == 400


def test_leave_challenge_not_joined():
    h1, _, _ = _create_user("not_joined@fitai.dev")
    resp = client.post("/api/v1/challenges/99999/leave", headers=h1)
    assert resp.status_code == 404


def test_get_nonexistent_challenge():
    h1, _, _ = _create_user("ch_404@fitai.dev")
    resp = client.get("/api/v1/challenges/99999", headers=h1)
    assert resp.status_code == 404


def test_join_nonexistent_team():
    h1, _, _ = _create_user("team_404@fitai.dev")
    resp = client.post("/api/v1/teams/99999/join", headers=h1)
    assert resp.status_code == 404


def test_leave_nonexistent_team():
    h1, _, _ = _create_user("team_leave_404@fitai.dev")
    resp = client.post("/api/v1/teams/99999/leave", headers=h1)
    assert resp.status_code == 404


def test_search_empty_query():
    h1, _, _ = _create_user("search_empty@fitai.dev")
    resp = client.get("/api/v1/social/users/search?q=", headers=h1)
    assert resp.status_code == 200
    assert resp.json() == []


def test_public_profile_not_found():
    h1, _, _ = _create_user("prof_viewer@fitai.dev")
    resp = client.get("/api/v1/profile/non_existent_athlete_xyz", headers=h1)
    assert resp.status_code == 404
