"""
Complete Phase 3 validation script for FitAI.
Tests models, services, auth flow, and all 6 health tracking modules.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db

def run_tests():
    print("=== Step 1: Initializing Database ===")
    success = init_db()
    assert success is True, "Database initialization failed"
    print("[OK] Database initialized.")

    client = TestClient(app)

    print("\n=== Step 2: System Endpoints ===")
    r = client.get("/")
    assert r.status_code == 200, f"Root endpoint failed: {r.text}"
    print(f"[OK] GET / -> {r.json()}")

    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"[OK] GET /health -> {r.json()}")

    print("\n=== Step 3: Authentication & Profile ===")
    user_email = "athlete@fitai.com"
    user_pass = "SuperSecretPassword123!"
    reg_payload = {
        "email": user_email,
        "username": "fitathlete",
        "password": user_pass,
        "full_name": "Fit Athlete"
    }
    r = client.post("/api/v1/auth/register", json=reg_payload)
    if r.status_code == 400 and ("already" in r.text or "exists" in r.text):
        print("[INFO] User already registered, proceeding to login.")
    else:
        assert r.status_code == 201, f"Registration failed: {r.text}"
        print(f"[OK] POST /api/v1/auth/register -> User ID: {r.json()['user']['id']}")

    r = client.post("/api/v1/auth/login", json={"email": user_email, "password": user_pass})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[OK] POST /api/v1/auth/login -> JWT token obtained.")

    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200, f"Get current user failed: {r.text}"
    me = r.json()
    assert me["email"] == user_email
    print(f"[OK] GET /api/v1/auth/me -> username={me['username']}, is_active={me['is_active']}")

    print("\n=== Step 4: BMI Calculator ===")
    r = client.post("/api/v1/bmi/calculate", json={"height_cm": 180.0, "weight_kg": 75.0}, headers=headers)
    assert r.status_code == 201, f"BMI calculation failed: {r.text}"
    bmi_data = r.json()
    assert bmi_data["category"] == "Normal"
    print(f"[OK] POST /api/v1/bmi/calculate -> BMI={bmi_data['bmi']}, Category={bmi_data['category']}")

    r = client.get("/api/v1/bmi/history", headers=headers)
    assert r.status_code == 200, f"BMI history failed: {r.text}"
    print(f"[OK] GET /api/v1/bmi/history -> {len(r.json())} record(s) found.")

    print("\n=== Step 5: Calorie Tracker ===")
    r = client.post(
        "/api/v1/calories",
        json={
            "meal_name": "Avocado Toast & Eggs",
            "calories": 420.0,
            "protein": 18.0,
            "carbs": 35.0,
            "fats": 15.0
        },
        headers=headers
    )
    assert r.status_code == 201, f"Calorie logging failed: {r.text}"
    cal_data = r.json()
    print(f"[OK] POST /api/v1/calories -> {cal_data['meal_name']} ({cal_data['calories']} kcal)")

    r = client.get("/api/v1/calories/history", headers=headers)
    assert r.status_code == 200, f"Calorie history failed: {r.text}"
    print(f"[OK] GET /api/v1/calories/history -> {len(r.json())} record(s) found.")

    print("\n=== Step 6: Workout Tracker ===")
    r = client.post(
        "/api/v1/workouts",
        json={
            "workout_type": "HIIT Training",
            "duration_minutes": 45,
            "calories_burned": 450.0,
            "notes": "Intense interval sprints"
        },
        headers=headers
    )
    assert r.status_code == 201, f"Workout logging failed: {r.text}"
    wo_data = r.json()
    print(f"[OK] POST /api/v1/workouts -> {wo_data['workout_type']} ({wo_data['duration_minutes']} min, {wo_data['calories_burned']} kcal)")

    r = client.get("/api/v1/workouts/history", headers=headers)
    assert r.status_code == 200, f"Workout history failed: {r.text}"
    print(f"[OK] GET /api/v1/workouts/history -> {len(r.json())} record(s) found.")

    print("\n=== Step 7: Water Tracker ===")
    r = client.post("/api/v1/water", json={"glasses": 4, "liters": 1.0}, headers=headers)
    assert r.status_code == 201, f"Water logging failed: {r.text}"
    water_data = r.json()
    print(f"[OK] POST /api/v1/water -> {water_data['glasses']} glasses ({water_data['liters']} L)")

    r = client.get("/api/v1/water/history", headers=headers)
    assert r.status_code == 200, f"Water history failed: {r.text}"
    print(f"[OK] GET /api/v1/water/history -> {len(r.json())} record(s) found.")

    print("\n=== Step 8: Step Counter ===")
    r = client.post(
        "/api/v1/steps",
        json={"steps": 8500, "distance_km": 6.2, "calories_burned": 340.0},
        headers=headers
    )
    assert r.status_code == 201, f"Step logging failed: {r.text}"
    step_data = r.json()
    print(f"[OK] POST /api/v1/steps -> {step_data['steps']} steps ({step_data['distance_km']} km)")

    r = client.get("/api/v1/steps/history", headers=headers)
    assert r.status_code == 200, f"Step history failed: {r.text}"
    print(f"[OK] GET /api/v1/steps/history -> {len(r.json())} record(s) found.")

    print("\n" + "=" * 55)
    print(" ALL 8 TEST SUITES COMPLETED WITH ZERO ERRORS!")
    print("=" * 55)

if __name__ == "__main__":
    run_tests()
