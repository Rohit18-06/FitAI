"""
Phase 6 Test Suite — Wearables & Real-Time Health Intelligence.

Tests cover:
  ✓ Wearable device connect / disconnect / list
  ✓ Health Connect sync (steps, heart rate, sleep)
  ✓ Health Connect status
  ✓ Sleep logging / history / analytics
  ✓ Heart rate logging / history / analytics
  ✓ Recovery score computation
  ✓ Personal record add / list / best
  ✓ Notification create / list / unread / count / mark read / mark all read
  ✓ Edge cases & validation

Run:
    cd d:\\FitAI\\backend
    venv\\Scripts\\python.exe -m pytest tests\\test_phase6.py -v
"""

import pytest
import sys
import os

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# ── Test DB ────────────────────────────────────────────────────────────
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

def _register_and_login(email="test@fitai.dev", password="Test123!@#"):
    """Register + login, return bearer header."""
    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email.split("@")[0],
        "password": password,
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ══════════════════════════════════════════════════════════════════════
# 1 · WEARABLE DEVICES
# ══════════════════════════════════════════════════════════════════════

def test_connect_device():
    headers = _register_and_login("dev1@test.com")
    resp = client.post("/api/v1/integrations/devices/connect", json={
        "provider": "health_connect",
        "device_name": "Pixel Watch 3",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["provider"] == "health_connect"
    assert data["device_name"] == "Pixel Watch 3"
    assert data["is_connected"] is True


def test_connect_device_unsupported_provider():
    headers = _register_and_login("dev2@test.com")
    resp = client.post("/api/v1/integrations/devices/connect", json={
        "provider": "unknown_brand",
        "device_name": "MyWatch",
    }, headers=headers)
    assert resp.status_code == 400


def test_list_devices_empty():
    headers = _register_and_login("dev3@test.com")
    resp = client.get("/api/v1/integrations/devices", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_devices_after_connect():
    headers = _register_and_login("dev4@test.com")
    client.post("/api/v1/integrations/devices/connect", json={
        "provider": "garmin",
        "device_name": "Forerunner 965",
    }, headers=headers)
    resp = client.get("/api/v1/integrations/devices", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_disconnect_device():
    headers = _register_and_login("dev5@test.com")
    create_resp = client.post("/api/v1/integrations/devices/connect", json={
        "provider": "fitbit",
        "device_name": "Charge 6",
    }, headers=headers)
    device_id = create_resp.json()["id"]
    resp = client.post(f"/api/v1/integrations/devices/{device_id}/disconnect", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_connected"] is False


def test_disconnect_device_not_found():
    headers = _register_and_login("dev6@test.com")
    resp = client.post("/api/v1/integrations/devices/99999/disconnect", headers=headers)
    assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════
# 2 · HEALTH CONNECT STATUS
# ══════════════════════════════════════════════════════════════════════

def test_status_no_devices():
    headers = _register_and_login("status1@test.com")
    resp = client.get("/api/v1/integrations/status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is False
    assert data["active_devices_count"] == 0


def test_status_with_device():
    headers = _register_and_login("status2@test.com")
    client.post("/api/v1/integrations/devices/connect", json={
        "provider": "health_connect",
        "device_name": "Galaxy Watch 6",
    }, headers=headers)
    resp = client.get("/api/v1/integrations/status", headers=headers)
    data = resp.json()
    assert data["connected"] is True
    assert data["active_devices_count"] >= 1
    assert "health_connect" in data["connected_providers"]


# ══════════════════════════════════════════════════════════════════════
# 3 · HEALTH CONNECT SYNC
# ══════════════════════════════════════════════════════════════════════

def test_sync_steps_and_hr():
    headers = _register_and_login("sync1@test.com")
    # connect device first
    client.post("/api/v1/integrations/devices/connect", json={
        "provider": "health_connect",
        "device_name": "Pixel Watch 3",
    }, headers=headers)
    resp = client.post("/api/v1/integrations/sync", json={
        "provider": "health_connect",
        "steps": 8500,
        "calories_burned": 320.5,
        "heart_rate": 72,
        "resting_heart_rate": 58,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["synced"] is True
    assert "steps" in data["records_updated"]
    assert "heart_rate" in data["records_updated"]


def test_sync_sleep_data():
    headers = _register_and_login("sync2@test.com")
    resp = client.post("/api/v1/integrations/sync", json={
        "provider": "google_fit",
        "sleep_duration_hours": 7.5,
        "deep_sleep_hours": 1.8,
        "rem_sleep_hours": 1.5,
        "sleep_score": 85,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["synced"] is True
    assert "sleep" in data["records_updated"]
    assert data["records_updated"]["sleep"]["score"] == 85


# ══════════════════════════════════════════════════════════════════════
# 4 · SLEEP
# ══════════════════════════════════════════════════════════════════════

def test_log_sleep():
    headers = _register_and_login("sleep1@test.com")
    resp = client.post("/api/v1/integrations/sleep", json={
        "duration_hours": 7.2,
        "deep_sleep_hours": 1.5,
        "rem_sleep_hours": 1.8,
        "sleep_score": 82,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["duration_hours"] == 7.2
    assert data["sleep_score"] == 82
    assert data["light_sleep_hours"] == pytest.approx(7.2 - 1.5 - 1.8, abs=0.1)


def test_sleep_history():
    headers = _register_and_login("sleep2@test.com")
    for i in range(3):
        client.post("/api/v1/integrations/sleep", json={
            "duration_hours": 6.0 + i,
            "sleep_score": 70 + i * 5,
        }, headers=headers)
    resp = client.get("/api/v1/integrations/sleep/history", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_sleep_analytics_empty():
    headers = _register_and_login("sleep3@test.com")
    resp = client.get("/api/v1/integrations/sleep/analytics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] == 0
    assert data["trend"] == "insufficient_data"


def test_sleep_analytics_with_data():
    headers = _register_and_login("sleep4@test.com")
    for i in range(5):
        client.post("/api/v1/integrations/sleep", json={
            "duration_hours": 7.0,
            "deep_sleep_hours": 1.5,
            "rem_sleep_hours": 1.5,
            "sleep_score": 80,
        }, headers=headers)
    resp = client.get("/api/v1/integrations/sleep/analytics?days=7", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] == 5
    assert data["avg_duration"] == 7.0
    assert data["avg_score"] == 80


# ══════════════════════════════════════════════════════════════════════
# 5 · HEART RATE
# ══════════════════════════════════════════════════════════════════════

def test_log_heart_rate():
    headers = _register_and_login("hr1@test.com")
    resp = client.post("/api/v1/integrations/heart-rate", json={
        "current_hr": 72,
        "resting_hr": 58,
        "max_hr": 185,
        "hrv_rmssd": 55.0,
        "vo2_max": 48.5,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["current_hr"] == 72
    assert data["resting_hr"] == 58
    assert data["hrv_rmssd"] == 55.0


def test_hr_history():
    headers = _register_and_login("hr2@test.com")
    for i in range(4):
        client.post("/api/v1/integrations/heart-rate", json={
            "current_hr": 70 + i,
            "resting_hr": 55 + i,
        }, headers=headers)
    resp = client.get("/api/v1/integrations/heart-rate/history", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 4


def test_hr_analytics():
    headers = _register_and_login("hr3@test.com")
    for i in range(3):
        client.post("/api/v1/integrations/heart-rate", json={
            "current_hr": 72,
            "resting_hr": 58,
            "hrv_rmssd": 50.0 + i,
        }, headers=headers)
    resp = client.get("/api/v1/integrations/heart-rate/analytics?days=7", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] == 3
    assert data["avg_resting_hr"] == 58


# ══════════════════════════════════════════════════════════════════════
# 6 · RECOVERY
# ══════════════════════════════════════════════════════════════════════

def test_recovery_no_data():
    headers = _register_and_login("rec1@test.com")
    resp = client.get("/api/v1/integrations/recovery", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["recovery_score"] <= 100
    assert data["status"] in ("Excellent", "Good", "Moderate", "Low")


def test_recovery_with_sleep_and_hr():
    headers = _register_and_login("rec2@test.com")
    client.post("/api/v1/integrations/sleep", json={
        "duration_hours": 8.0,
        "deep_sleep_hours": 2.0,
        "rem_sleep_hours": 2.0,
        "sleep_score": 90,
    }, headers=headers)
    client.post("/api/v1/integrations/heart-rate", json={
        "current_hr": 60,
        "resting_hr": 52,
        "hrv_rmssd": 65.0,
    }, headers=headers)
    resp = client.get("/api/v1/integrations/recovery", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["recovery_score"] >= 60
    assert data["latest_sleep"]["duration"] == 8.0
    assert data["latest_hr"]["resting_hr"] == 52


# ══════════════════════════════════════════════════════════════════════
# 7 · PERSONAL RECORDS
# ══════════════════════════════════════════════════════════════════════

def test_add_personal_record():
    headers = _register_and_login("pr1@test.com")
    resp = client.post("/api/v1/integrations/records", json={
        "record_type": "longest_run",
        "record_name": "Longest Run",
        "value": 15.5,
        "unit": "km",
        "notes": "Half marathon training",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["record_type"] == "longest_run"
    assert data["value"] == 15.5


def test_list_personal_records():
    headers = _register_and_login("pr2@test.com")
    client.post("/api/v1/integrations/records", json={
        "record_type": "most_steps",
        "record_name": "Most Steps",
        "value": 25000,
        "unit": "steps",
    }, headers=headers)
    resp = client.get("/api/v1/integrations/records", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_best_records():
    headers = _register_and_login("pr3@test.com")
    client.post("/api/v1/integrations/records", json={
        "record_type": "heaviest_lift",
        "record_name": "Heaviest Deadlift",
        "value": 120,
        "unit": "kg",
    }, headers=headers)
    client.post("/api/v1/integrations/records", json={
        "record_type": "heaviest_lift",
        "record_name": "Heaviest Deadlift",
        "value": 140,
        "unit": "kg",
    }, headers=headers)
    resp = client.get("/api/v1/integrations/records/best", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["value"] == 140


# ══════════════════════════════════════════════════════════════════════
# 8 · NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════

def test_create_notification():
    headers = _register_and_login("notif1@test.com")
    resp = client.post("/api/v1/integrations/notifications", json={
        "type": "hydration_reminder",
        "title": "Drink Water!",
        "message": "You haven't logged water in 3 hours.",
        "priority": "high",
        "action_url": "#/water",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "hydration_reminder"
    assert data["is_read"] is False


def test_list_notifications():
    headers = _register_and_login("notif2@test.com")
    client.post("/api/v1/integrations/notifications", json={
        "type": "workout_reminder",
        "title": "Time to train",
        "message": "Your scheduled workout starts in 30 min.",
    }, headers=headers)
    resp = client.get("/api/v1/integrations/notifications", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_unread_notifications():
    headers = _register_and_login("notif3@test.com")
    client.post("/api/v1/integrations/notifications", json={
        "type": "recovery_alert",
        "title": "Low Recovery",
        "message": "Your recovery is low. Consider rest.",
    }, headers=headers)
    resp = client.get("/api/v1/integrations/notifications/unread", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_unread_count():
    headers = _register_and_login("notif4@test.com")
    for _ in range(3):
        client.post("/api/v1/integrations/notifications", json={
            "type": "achievement",
            "title": "New PR!",
            "message": "You set a new personal record!",
        }, headers=headers)
    resp = client.get("/api/v1/integrations/notifications/count", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["unread_count"] == 3


def test_mark_read():
    headers = _register_and_login("notif5@test.com")
    create_resp = client.post("/api/v1/integrations/notifications", json={
        "type": "sleep_reminder",
        "title": "Bedtime",
        "message": "Time to sleep!",
    }, headers=headers)
    notif_id = create_resp.json()["id"]
    resp = client.put(f"/api/v1/integrations/notifications/{notif_id}/read", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True


def test_mark_all_read():
    headers = _register_and_login("notif6@test.com")
    for _ in range(4):
        client.post("/api/v1/integrations/notifications", json={
            "type": "hydration_reminder",
            "title": "Drink!",
            "message": "Stay hydrated.",
        }, headers=headers)
    resp = client.put("/api/v1/integrations/notifications/read-all", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["marked_read"] == 4

    count_resp = client.get("/api/v1/integrations/notifications/count", headers=headers)
    assert count_resp.json()["unread_count"] == 0


# ══════════════════════════════════════════════════════════════════════
# 9 · RECONNECT SAME DEVICE
# ══════════════════════════════════════════════════════════════════════

def test_reconnect_same_device():
    headers = _register_and_login("recon1@test.com")
    resp1 = client.post("/api/v1/integrations/devices/connect", json={
        "provider": "garmin",
        "device_name": "Venu 3",
    }, headers=headers)
    device_id = resp1.json()["id"]

    # disconnect
    client.post(f"/api/v1/integrations/devices/{device_id}/disconnect", headers=headers)

    # reconnect same device
    resp2 = client.post("/api/v1/integrations/devices/connect", json={
        "provider": "garmin",
        "device_name": "Venu 3",
    }, headers=headers)
    assert resp2.status_code == 201
    assert resp2.json()["is_connected"] is True
    assert resp2.json()["id"] == device_id  # should reuse same record


# ══════════════════════════════════════════════════════════════════════
# 10 · AUTH GUARD
# ══════════════════════════════════════════════════════════════════════

def test_no_auth_returns_401():
    resp = client.get("/api/v1/integrations/devices")
    assert resp.status_code == 401
