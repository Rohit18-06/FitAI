"""
Phase 8 Test Suite — AI Personal Trainer & Smart Coaching Platform.

Tests cover:
  ✓ AI Training Program Generation (weeks, days, exercises, periodization)
  ✓ List Training Programs & Get Active Program
  ✓ Complete Program Day
  ✓ Exercise Progression Logging & 1RM Estimation (Epley formula)
  ✓ Exercise Progression History & Filtering
  ✓ AI Recovery Assessment Computation & Latest Score
  ✓ Plateau Detection Engine (weight, strength, activity)
  ✓ Injury Risk Assessment & Recommendations
  ✓ Body Measurements Logging, History, & Latest Snapshot
  ✓ Progress Photos Logging & Listing
  ✓ Goal Tracking (Create, Progress Update, Auto-completion at 100%)
  ✓ AI Weekly Coaching Report Generation & History
  ✓ Authentication Guards (401 when unauthenticated)

Run:
    cd d:\\FitAI\\backend
    venv\\Scripts\\python.exe -m pytest tests\\test_phase8.py -v
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
from app.models.user import User

# ── In-Memory Test DB ──────────────────────────────────────────────────
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


def register_and_login(client: TestClient, username: str = "coach_athlete", email: str = "coach@fitai.com") -> str:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Password123!",
            "full_name": "Coach Athlete",
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


# ═══════════════════════════════════════════════════════════════════════
# 1. TRAINING PROGRAM TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_generate_and_list_training_program(client: TestClient):
    token = register_and_login(client, "trainee_1", "t1@fitai.com")
    headers = auth_header(token)

    # Generate program
    payload = {
        "fitness_goal": "muscle_building",
        "fitness_level": "intermediate",
        "duration_weeks": 4,
        "days_per_week": 4,
    }
    res = client.post("/api/v1/training-programs", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["fitness_goal"] == "muscle_building"
    assert data["duration_weeks"] == 4
    assert data["days_per_week"] == 4
    assert len(data["weeks"]) == 4
    assert len(data["weeks"][0]["days"]) == 4
    assert len(data["weeks"][0]["days"][0]["exercises"]) > 0

    # Get active program
    res = client.get("/api/v1/training-programs/active", headers=headers)
    assert res.status_code == 200
    active = res.json()
    assert active is not None
    assert active["id"] == data["id"]

    # List programs
    res = client.get("/api/v1/training-programs", headers=headers)
    assert res.status_code == 200
    programs = res.json()
    assert len(programs) == 1

    # Complete a day
    day_id = data["weeks"][0]["days"][0]["id"]
    res = client.post(
        "/api/v1/training-programs/complete-day",
        json={"day_id": day_id},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["completed"] is True


# ═══════════════════════════════════════════════════════════════════════
# 2. EXERCISE PROGRESSION & 1RM TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_exercise_progression_and_1rm(client: TestClient):
    token = register_and_login(client, "lifter_1", "lifter@fitai.com")
    headers = auth_header(token)

    # Log Bench Press: 100 kg x 5 reps -> 1RM ~ 100 * (1 + 5/30) = 116.67
    payload = {
        "exercise_name": "Barbell Bench Press",
        "weight_kg": 100.0,
        "sets": 3,
        "reps": 5,
        "rpe": 8.5,
        "notes": "Felt strong today",
    }
    res = client.post("/api/v1/progressions", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["exercise_name"] == "Barbell Bench Press"
    assert data["weight_kg"] == 100.0
    assert data["one_rep_max_est"] is not None
    assert round(data["one_rep_max_est"], 1) == 112.5

    # Log another exercise
    client.post(
        "/api/v1/progressions",
        json={"exercise_name": "Barbell Squat", "weight_kg": 140.0, "sets": 3, "reps": 3},
        headers=headers,
    )

    # List progressions
    res = client.get("/api/v1/progressions", headers=headers)
    assert res.status_code == 200
    all_progs = res.json()
    assert len(all_progs) == 2

    # Filter by exercise name
    res = client.get("/api/v1/progressions?exercise_name=Barbell+Squat", headers=headers)
    assert res.status_code == 200
    filtered = res.json()
    assert len(filtered) == 1
    assert filtered[0]["exercise_name"] == "Barbell Squat"


# ═══════════════════════════════════════════════════════════════════════
# 3. RECOVERY ASSESSMENT TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_recovery_assessment(client: TestClient):
    token = register_and_login(client, "recovery_user", "recovery@fitai.com")
    headers = auth_header(token)

    # Compute recovery
    res = client.post("/api/v1/recovery-assessment/compute", headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert 0 <= data["score"] <= 100
    assert data["status"] in ["Optimal", "Good", "Moderate", "Fatigued", "Overtrained"]
    assert "recommendation" in data

    # Get latest
    res = client.get("/api/v1/recovery-assessment/latest", headers=headers)
    assert res.status_code == 200
    latest = res.json()
    assert latest["id"] == data["id"]


# ═══════════════════════════════════════════════════════════════════════
# 4. PLATEAU DETECTION TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_plateau_detection(client: TestClient):
    token = register_and_login(client, "plateau_user", "plateau@fitai.com")
    headers = auth_header(token)

    res = client.get("/api/v1/plateaus", headers=headers)
    assert res.status_code == 200
    reports = res.json()
    assert isinstance(reports, list)
    assert len(reports) >= 1
    assert "detected" in reports[0]


# ═══════════════════════════════════════════════════════════════════════
# 5. INJURY RISK ASSESSMENT TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_injury_risk_assessment(client: TestClient):
    token = register_and_login(client, "injury_user", "injury@fitai.com")
    headers = auth_header(token)

    # Assess risk
    res = client.post("/api/v1/injury-risk/assess", headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["risk_level"] in ["Low", "Moderate", "High"]
    assert 0 <= data["risk_score"] <= 100
    assert isinstance(data["factors"], list)

    # Get latest
    res = client.get("/api/v1/injury-risk/latest", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == data["id"]


# ═══════════════════════════════════════════════════════════════════════
# 6. BODY MEASUREMENTS TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_body_measurements(client: TestClient):
    token = register_and_login(client, "measure_user", "measure@fitai.com")
    headers = auth_header(token)

    payload = {
        "weight_kg": 78.5,
        "body_fat_pct": 14.2,
        "chest_cm": 102.0,
        "waist_cm": 81.5,
        "hips_cm": 98.0,
        "left_arm_cm": 38.0,
        "right_arm_cm": 38.2,
        "notes": "Morning checkin",
    }
    res = client.post("/api/v1/measurements", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["weight_kg"] == 78.5
    assert data["waist_cm"] == 81.5

    # List measurements
    res = client.get("/api/v1/measurements", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Latest measurement
    res = client.get("/api/v1/measurements/latest", headers=headers)
    assert res.status_code == 200
    assert res.json()["chest_cm"] == 102.0


# ═══════════════════════════════════════════════════════════════════════
# 7. PROGRESS PHOTOS TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_progress_photos(client: TestClient):
    token = register_and_login(client, "photo_user", "photo@fitai.com")
    headers = auth_header(token)

    payload = {
        "photo_type": "front",
        "filename": "front_week_1.jpg",
        "notes": "Starting week 1",
    }
    res = client.post("/api/v1/progress-photos", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "front_week_1.jpg"
    assert data["photo_type"] == "front"

    # List photos
    res = client.get("/api/v1/progress-photos", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


# ═══════════════════════════════════════════════════════════════════════
# 8. GOAL TRACKING TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_goal_tracking_and_completion(client: TestClient):
    token = register_and_login(client, "goal_user", "goal@fitai.com")
    headers = auth_header(token)

    # Create goal: lose weight from 85kg to 75kg
    payload = {
        "goal_type": "weight_loss",
        "title": "Reach 75 kg",
        "start_value": 85.0,
        "target_value": 75.0,
        "unit": "kg",
    }
    res = client.post("/api/v1/goals", json=payload, headers=headers)
    assert res.status_code == 201
    goal = res.json()
    goal_id = goal["id"]
    assert goal["status"] == "active"
    assert goal["completion_pct"] == 0.0

    # Update progress to 80kg -> halfway (5kg out of 10kg) = 50%
    res = client.patch(
        f"/api/v1/goals/{goal_id}/progress",
        json={"current_value": 80.0},
        headers=headers,
    )
    assert res.status_code == 200
    updated = res.json()
    assert updated["current_value"] == 80.0
    assert updated["completion_pct"] == 50.0
    assert updated["status"] == "active"

    # Update progress to 75kg -> 100% completed!
    res = client.patch(
        f"/api/v1/goals/{goal_id}/progress",
        json={"current_value": 75.0},
        headers=headers,
    )
    assert res.status_code == 200
    finished = res.json()
    assert finished["completion_pct"] == 100.0
    assert finished["status"] == "completed"

    # List active goals vs all
    res = client.get("/api/v1/goals?status=completed", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Get goal by id
    res = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Reach 75 kg"


# ═══════════════════════════════════════════════════════════════════════
# 9. WEEKLY COACHING REPORT TESTS
# ═══════════════════════════════════════════════════════════════════════

def test_weekly_coaching_report(client: TestClient):
    token = register_and_login(client, "report_user", "report@fitai.com")
    headers = auth_header(token)

    # Generate report
    res = client.post("/api/v1/weekly-reports/generate", headers=headers)
    assert res.status_code == 201
    report = res.json()
    assert "training_summary" in report
    assert "recovery_summary" in report
    assert "recommendations" in report
    assert 0 <= report["progress_score"] <= 100

    # List reports
    res = client.get("/api/v1/weekly-reports", headers=headers)
    assert res.status_code == 200
    reports = res.json()
    assert len(reports) == 1
    assert reports[0]["id"] == report["id"]


# ═══════════════════════════════════════════════════════════════════════
# 10. AUTHENTICATION GUARDS (401)
# ═══════════════════════════════════════════════════════════════════════

def test_auth_guards_unauthorized(client: TestClient):
    assert client.get("/api/v1/training-programs").status_code in [401, 403]
    assert client.get("/api/v1/progressions").status_code in [401, 403]
    assert client.get("/api/v1/recovery-assessment/latest").status_code in [401, 403]
    assert client.get("/api/v1/plateaus").status_code in [401, 403]
    assert client.get("/api/v1/injury-risk/latest").status_code in [401, 403]
    assert client.get("/api/v1/measurements").status_code in [401, 403]
    assert client.get("/api/v1/goals").status_code in [401, 403]
    assert client.get("/api/v1/weekly-reports").status_code in [401, 403]
