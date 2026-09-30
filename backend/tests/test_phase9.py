"""
Phase 9 Test Suite — AI Personal Trainer & Computer Vision Coaching 2.0.

Tests cover:
  ✓ Real-Time Pose Estimation & Biomechanical Angle Computations
  ✓ Exercise Recognition Engine (Squat, Push Up, Pull Up, Deadlift, Bicep Curl, etc.)
  ✓ Intelligent Rep Counter & State Machine (inflection, lockout, tempo)
  ✓ Biomechanical Form Correction Engine (knee valgus, depth, spine neutrality)
  ✓ Live AI Coach Session Lifecycle (Start, Live Frame Ingestion, Complete)
  ✓ Injury Risk Detection Engine (LOW, MEDIUM, HIGH)
  ✓ Adaptive Training Volume & Deload Recommendations
  ✓ Smart Workout Automation (Warmup -> Main -> Accessory -> Cooldown)
  ✓ AI Movement Library (100+ Exercises, Search, Detail)
  ✓ Studio Analytics & Form Score Progression
  ✓ Authentication Guards (401 when unauthenticated)

Run:
    cd d:\\FitAI\\backend
    venv\\Scripts\\python.exe -m pytest tests\\test_phase9.py -v
"""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# ── In-Memory Isolated Test DB ─────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client: TestClient, username: str = "cv_athlete", email: str = "cv@fitai.com") -> str:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Password123!",
            "full_name": "CV Athlete",
        },
    )
    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def make_dummy_keypoints(knee_angle: float = 175.0, hip_angle: float = 170.0, elbow_angle: float = 165.0) -> list[dict]:
    """Generates 33 mock landmarks representing an athlete."""
    kps = []
    for i in range(33):
        kps.append({"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.99})

    # Set shoulders (11, 12), hips (23, 24), knees (25, 26), ankles (27, 28)
    kps[11] = {"x": 0.45, "y": 0.25, "z": 0.0, "visibility": 0.99}
    kps[12] = {"x": 0.55, "y": 0.25, "z": 0.0, "visibility": 0.99}
    kps[13] = {"x": 0.40, "y": 0.40, "z": 0.0, "visibility": 0.99}
    kps[14] = {"x": 0.60, "y": 0.40, "z": 0.0, "visibility": 0.99}
    kps[15] = {"x": 0.40, "y": 0.55, "z": 0.0, "visibility": 0.99}
    kps[16] = {"x": 0.60, "y": 0.55, "z": 0.0, "visibility": 0.99}
    kps[23] = {"x": 0.46, "y": 0.50, "z": 0.0, "visibility": 0.99}
    kps[24] = {"x": 0.54, "y": 0.50, "z": 0.0, "visibility": 0.99}
    kps[25] = {"x": 0.46, "y": 0.70, "z": 0.0, "visibility": 0.99}
    kps[26] = {"x": 0.54, "y": 0.70, "z": 0.0, "visibility": 0.99}
    kps[27] = {"x": 0.46, "y": 0.90, "z": 0.0, "visibility": 0.99}
    kps[28] = {"x": 0.54, "y": 0.90, "z": 0.0, "visibility": 0.99}
    return kps


# ═══════════════════════════════════════════════════════════════════════
# 1. POSE ESTIMATION & REAL-TIME FRAME ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def test_pose_estimation_and_angles(client: TestClient):
    token = register_and_login(client, "pose_user", "pose@fitai.com")
    headers = auth_header(token)

    kps = make_dummy_keypoints()
    payload = {
        "keypoints": kps,
        "exercise_hint": "Squat",
    }
    res = client.post("/api/v1/pose/analyze", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["exercise"] == "Squat"
    assert "joint_angles" in data
    assert "left_knee" in data["joint_angles"]
    assert "right_knee" in data["joint_angles"]
    assert "torso_angle" in data["joint_angles"]
    assert 0 <= data["posture_score"] <= 100
    assert data["injury_risk"] in ["LOW", "MEDIUM", "HIGH"]
    assert "coach_cue" in data


# ═══════════════════════════════════════════════════════════════════════
# 2. EXERCISE RECOGNITION ENGINE
# ═══════════════════════════════════════════════════════════════════════

def test_exercise_recognition_engine(client: TestClient):
    token = register_and_login(client, "recog_user", "recog@fitai.com")
    headers = auth_header(token)

    exercises = ["Squat", "Push Up", "Pull Up", "Deadlift", "Bicep Curl", "Shoulder Press", "Lunges", "Plank"]
    for ex in exercises:
        res = client.post(
            "/api/v1/pose/analyze",
            json={"keypoints": make_dummy_keypoints(), "exercise_hint": ex},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["exercise"] == ex
        assert res.json()["confidence"] >= 0.80


# ═══════════════════════════════════════════════════════════════════════
# 3. REP COUNTER & FINITE STATE MACHINE
# ═══════════════════════════════════════════════════════════════════════

def test_rep_counter_fsm(client: TestClient):
    token = register_and_login(client, "rep_user", "reps@fitai.com")
    headers = auth_header(token)

    # 1. Start session
    sess_res = client.post(
        "/api/v1/live-coach/session",
        json={"exercise_name": "Squat", "target_reps": 5, "target_sets": 1},
        headers=headers,
    )
    assert sess_res.status_code == 201
    sess_id = sess_res.json()["id"]

    # 2. Top position (Lockout ~175°)
    kps_top = make_dummy_keypoints()
    res1 = client.post(
        "/api/v1/pose/analyze",
        json={"keypoints": kps_top, "exercise_hint": "Squat", "session_id": sess_id},
        headers=headers,
    )
    assert res1.status_code == 200
    assert res1.json()["rep_count"] == 0

    # 3. Bottom position (Inflection point: deep squat)
    kps_bot = make_dummy_keypoints()
    # Bend both knees and lower hips
    kps_bot[23] = {"x": 0.46, "y": 0.70, "z": 0.0, "visibility": 0.99}
    kps_bot[24] = {"x": 0.54, "y": 0.70, "z": 0.0, "visibility": 0.99}
    kps_bot[25] = {"x": 0.25, "y": 0.75, "z": 0.0, "visibility": 0.99}
    kps_bot[26] = {"x": 0.75, "y": 0.75, "z": 0.0, "visibility": 0.99}
    kps_bot[27] = {"x": 0.46, "y": 0.90, "z": 0.0, "visibility": 0.99}
    kps_bot[28] = {"x": 0.54, "y": 0.90, "z": 0.0, "visibility": 0.99}
    res2 = client.post(
        "/api/v1/pose/analyze",
        json={"keypoints": kps_bot, "exercise_hint": "Squat", "session_id": sess_id},
        headers=headers,
    )
    assert res2.status_code == 200

    # 4. Return to top (Lockout completed)
    res3 = client.post(
        "/api/v1/pose/analyze",
        json={"keypoints": kps_top, "exercise_hint": "Squat", "session_id": sess_id},
        headers=headers,
    )
    assert res3.status_code == 200
    assert res3.json()["rep_count"] >= 1


# ═══════════════════════════════════════════════════════════════════════
# 4. FORM CORRECTION & INJURY RISK DETECTION
# ═══════════════════════════════════════════════════════════════════════

def test_form_correction_and_injury_detection(client: TestClient):
    token = register_and_login(client, "form_user", "form@fitai.com")
    headers = auth_header(token)

    # Knee valgus simulation (knees pinch inward while ankles stay wide)
    kps_valgus = make_dummy_keypoints()
    kps_valgus[25] = {"x": 0.49, "y": 0.70, "z": 0.0}  # left knee in
    kps_valgus[26] = {"x": 0.51, "y": 0.70, "z": 0.0}  # right knee in
    kps_valgus[27] = {"x": 0.40, "y": 0.90, "z": 0.0}  # left ankle wide
    kps_valgus[28] = {"x": 0.60, "y": 0.90, "z": 0.0}  # right ankle wide

    res = client.post(
        "/api/v1/pose/analyze",
        json={"keypoints": kps_valgus, "exercise_hint": "Squat"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["posture_score"] < 100.0
    assert len(data["mistakes"]) > 0
    assert "valgus" in data["mistakes"][0].lower()
    assert len(data["corrections"]) > 0
    assert data["injury_risk"] in ["MEDIUM", "HIGH"]


# ═══════════════════════════════════════════════════════════════════════
# 5. LIVE AI COACH SESSION LIFECYCLE
# ═══════════════════════════════════════════════════════════════════════

def test_live_coach_session_lifecycle(client: TestClient):
    token = register_and_login(client, "session_user", "session@fitai.com")
    headers = auth_header(token)

    # Start session
    start_res = client.post(
        "/api/v1/live-coach/session",
        json={"exercise_name": "Barbell Back Squat", "target_reps": 12, "target_sets": 4},
        headers=headers,
    )
    assert start_res.status_code == 201
    session = start_res.json()
    sess_id = session["id"]
    assert session["status"] == "in_progress"

    # Get active session
    active_res = client.get("/api/v1/live-coach/session/active", headers=headers)
    assert active_res.status_code == 200
    assert active_res.json()["id"] == sess_id

    # Complete session
    comp_res = client.post(f"/api/v1/live-coach/session/{sess_id}/complete", headers=headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "completed"
    assert comp_res.json()["ended_at"] is not None


# ═══════════════════════════════════════════════════════════════════════
# 6. ADAPTIVE TRAINING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def test_adaptive_training_system(client: TestClient):
    token = register_and_login(client, "adapt_user", "adapt@fitai.com")
    headers = auth_header(token)

    # 1. Standard readiness
    res = client.post(
        "/api/v1/adaptive-training/plan",
        json={"soreness_level": "mild"},
        headers=headers,
    )
    assert res.status_code == 201
    plan = res.json()
    assert plan["adjustment_type"] in ["increase_volume", "maintain", "decrease_volume", "deload"]
    assert plan["volume_multiplier"] > 0
    assert isinstance(plan["recommendations"], list)
    assert len(plan["recommendations"]) > 0

    # 2. High soreness triggers reduction / deload
    res_sore = client.post(
        "/api/v1/adaptive-training/plan",
        json={"soreness_level": "high"},
        headers=headers,
    )
    assert res_sore.status_code == 201
    plan_sore = res_sore.json()
    assert plan_sore["recovery_score"] < plan["recovery_score"]


# ═══════════════════════════════════════════════════════════════════════
# 7. SMART WORKOUT AUTOMATION
# ═══════════════════════════════════════════════════════════════════════

def test_smart_workout_automation(client: TestClient):
    token = register_and_login(client, "auto_user", "auto@fitai.com")
    headers = auth_header(token)

    payload = {
        "fitness_goal": "hypertrophy",
        "available_equipment": ["Barbell", "Dumbbell"],
        "time_minutes": 45,
        "fatigue_level": "low",
    }
    res = client.post("/api/v1/workout-automation/generate", json=payload, headers=headers)
    assert res.status_code == 200
    workout = res.json()
    assert "session_title" in workout
    assert workout["total_duration_min"] == 45
    assert len(workout["flow"]) == 4  # Warmup, Main, Accessory, Cooldown
    assert workout["flow"][0]["block_name"] == "Dynamic Activation & Mobility"
    assert len(workout["flow"][1]["exercises"]) > 0


# ═══════════════════════════════════════════════════════════════════════
# 8. AI MOVEMENT LIBRARY (100+ EXERCISES)
# ═══════════════════════════════════════════════════════════════════════

def test_movement_library_100_plus(client: TestClient):
    token = register_and_login(client, "lib_user", "lib@fitai.com")
    headers = auth_header(token)

    # 1. Seed library
    seed_res = client.post("/api/v1/movement-library/seed", headers=headers)
    assert seed_res.status_code == 200
    assert seed_res.json()["total_exercises"] >= 100

    # 2. List movements
    list_res = client.get("/api/v1/movement-library?limit=110", headers=headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 100

    # 3. Filter by category
    filter_res = client.get("/api/v1/movement-library?category=Strength", headers=headers)
    assert filter_res.status_code == 200
    assert len(filter_res.json()) > 0

    # 4. Search by name
    search_res = client.get("/api/v1/movement-library?search=Squat", headers=headers)
    assert search_res.status_code == 200
    assert any("squat" in ex["name"].lower() for ex in search_res.json())

    # 5. Detail retrieval
    item_id = items[0]["id"]
    detail_res = client.get(f"/api/v1/movement-library/{item_id}", headers=headers)
    assert detail_res.status_code == 200
    item = detail_res.json()
    assert "instructions" in item
    assert "common_mistakes" in item
    assert "coaching_cues" in item


# ═══════════════════════════════════════════════════════════════════════
# 9. TRAINER STUDIO ANALYTICS
# ═══════════════════════════════════════════════════════════════════════

def test_trainer_studio_analytics(client: TestClient):
    token = register_and_login(client, "studio_user", "studio@fitai.com")
    headers = auth_header(token)

    res = client.get("/api/v1/trainer/analytics", headers=headers)
    assert res.status_code == 200
    analytics = res.json()
    assert "total_sessions" in analytics
    assert "total_reps_logged" in analytics
    assert "overall_avg_form_score" in analytics
    assert isinstance(analytics["form_score_history"], list)
    assert isinstance(analytics["volume_by_exercise"], dict)
    assert isinstance(analytics["injury_risk_distribution"], dict)


# ═══════════════════════════════════════════════════════════════════════
# 10. AUTHENTICATION GUARDS
# ═══════════════════════════════════════════════════════════════════════

def test_auth_guards_phase9(client: TestClient):
    assert client.post("/api/v1/pose/analyze", json={}).status_code in [401, 403]
    assert client.post("/api/v1/live-coach/session", json={}).status_code in [401, 403]
    assert client.get("/api/v1/live-coach/session/active").status_code in [401, 403]
    assert client.post("/api/v1/adaptive-training/plan", json={}).status_code in [401, 403]
    assert client.post("/api/v1/workout-automation/generate", json={}).status_code in [401, 403]
    assert client.get("/api/v1/movement-library").status_code in [401, 403]
    assert client.get("/api/v1/trainer/analytics").status_code in [401, 403]
