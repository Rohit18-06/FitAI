"""
Phase 4 End-to-End Test Suite: AI Fitness Coach.
Validates Dashboard Analytics, AI Diet Planner, AI Workout Generator,
Gemini Video Analyzer, Health Insights, and Analytics APIs.
"""

import sys
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import init_db


def run_phase4_tests():
    print("=" * 65)
    print("[RUNNING] FITAI PHASE 4: AI FITNESS COACH VERIFICATION SUITE")
    print("=" * 65)

    # 1. Database Init
    print("\n[STEP 1] Database Initialization...")
    assert init_db() is True, "Database initialization failed"
    print(" Database ready.")

    client = TestClient(app)

    # 2. System Endpoints
    print("\n[STEP 2] System Health & Root Endpoints...")
    r = client.get("/")
    assert r.status_code == 200, r.text
    print(f" GET / -> {r.json()['app']} v{r.json()['version']}")

    r = client.get("/health")
    assert r.status_code == 200, r.text
    assert r.json()["success"] is True
    print(" GET /health -> healthy")

    # 3. Authentication
    print("\n[STEP 3] User Authentication & Token Acquisition...")
    email = "coach_athlete@fitai.com"
    password = "AthletePassword2026!"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": "coachathlete",
            "password": password,
            "full_name": "Pro Coach Athlete",
        },
    )
    if reg_res.status_code == 201:
        token = reg_res.json()["access_token"]
        print(" User registered successfully.")
    else:
        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        print(" User logged in successfully.")

    headers = {"Authorization": f"Bearer {token}"}

    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200, me_res.text
    user_info = me_res.json()
    print(f" Authenticated user: {user_info['username']} (ID: {user_info['id']})")

    # 4. Telemetry Baseline Setup
    print("\n[STEP 4] Setting Up Baseline Telemetry for Dashboard & Analytics...")
    # BMI
    client.post("/api/v1/bmi/calculate", json={"height_cm": 182.0, "weight_kg": 78.0}, headers=headers)
    # Calories
    client.post(
        "/api/v1/calories",
        json={
            "meal_name": "Protein Shake & Granola",
            "calories": 480.0,
            "protein": 35.0,
            "carbs": 55.0,
            "fats": 12.0,
        },
        headers=headers,
    )
    # Workouts
    client.post(
        "/api/v1/workouts",
        json={
            "workout_type": "Compound Strength",
            "duration_minutes": 50,
            "calories_burned": 420.0,
            "notes": "Squats and presses",
        },
        headers=headers,
    )
    # Water
    client.post("/api/v1/water", json={"glasses": 8, "liters": 2.0}, headers=headers)
    # Steps
    client.post("/api/v1/steps", json={"steps": 10500, "distance_km": 7.8, "calories_burned": 410.0}, headers=headers)
    print(" Telemetry baseline records logged.")

    # 5. AI Diet Planner
    print("\n[STEP 5] Testing AI Diet Planner...")
    diet_payload = {
        "fitness_goal": "muscle_gain",
        "dietary_preference": "omnivore",
        "target_calories": 2600.0,
        "allergies_or_restrictions": ["peanuts"],
        "meals_per_day": 4,
    }
    r = client.post("/api/v1/diet/generate", json=diet_payload, headers=headers)
    assert r.status_code == 201, f"Diet generation failed: {r.text}"
    diet_plan = r.json()
    assert diet_plan["is_active"] is True
    assert diet_plan["target_calories"] == 2600.0
    assert len(diet_plan["meals"]) >= 3
    first_meal = diet_plan["meals"][0]
    print(f" POST /api/v1/diet/generate -> Plan '{diet_plan['title']}' created with {len(diet_plan['meals'])} meals.")
    print(f"   First Meal: {first_meal['name']} ({first_meal['meal_type']}) - {first_meal['target_calories']} kcal")

    r = client.get("/api/v1/diet/active", headers=headers)
    assert r.status_code == 200, r.text
    active_diet = r.json()
    assert active_diet["id"] == diet_plan["id"]
    print(f" GET /api/v1/diet/active -> Active Plan ID {active_diet['id']}")

    r = client.get("/api/v1/diet/history", headers=headers)
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 1
    print(f" GET /api/v1/diet/history -> {len(r.json())} plan(s) in history.")

    # 6. AI Workout Generator
    print("\n[STEP 6] Testing AI Workout Generator...")
    wo_payload = {
        "fitness_level": "intermediate",
        "fitness_goal": "hypertrophy",
        "days_per_week": 4,
        "equipment": "full_gym",
        "focus_areas": ["chest", "back", "legs"],
        "injuries_or_limitations": ["knee sensitivity"],
    }
    r = client.post("/api/v1/workout-plans/generate", json=wo_payload, headers=headers)
    assert r.status_code == 201, f"Workout routine generation failed: {r.text}"
    workout_plan = r.json()
    assert workout_plan["is_active"] is True
    assert workout_plan["days_per_week"] == 4
    assert len(workout_plan["routines"]) == 4
    first_routine = workout_plan["routines"][0]
    print(f" POST /api/v1/workout-plans/generate -> Plan '{workout_plan['title']}' with {len(workout_plan['routines'])} daily routines.")
    print(f"   Day 1 Focus: {first_routine['day_name']} ({len(first_routine['exercises'])} exercises prescribed)")

    r = client.get("/api/v1/workout-plans/active", headers=headers)
    assert r.status_code == 200, r.text
    active_wo = r.json()
    assert active_wo["id"] == workout_plan["id"]
    print(f" GET /api/v1/workout-plans/active -> Active Plan ID {active_wo['id']}")

    r = client.get("/api/v1/workout-plans/history", headers=headers)
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 1
    print(f" GET /api/v1/workout-plans/history -> {len(r.json())} program(s) in history.")

    # 7. Gemini Video Form Analyzer
    print("\n[STEP 7] Testing Gemini Video Form Analyzer...")
    # Direct JSON analysis
    direct_req = {
        "exercise_name": "Barbell Back Squat",
        "filename": "squat_set_1.mp4",
        "video_base64": None,
    }
    r = client.post("/api/v1/video/analyze-direct", json=direct_req, headers=headers)
    assert r.status_code == 201, f"Direct video analysis failed: {r.text}"
    analysis = r.json()
    assert analysis["form_score"] > 0
    assert analysis["exercise_name"] == "Barbell Back Squat"
    assert len(analysis["keypoint_checks"]) >= 1
    print(f" POST /api/v1/video/analyze-direct -> Score: {analysis['form_score']}/100, Reps: {analysis['rep_count']}")
    print(f"   Summary: {analysis['posture_summary']}")
    print(f"   Injury Risk: {analysis['injury_risk_level']}")

    # Multipart file upload analysis
    mock_video_bytes = b"fake_mp4_header_for_biomechanical_screen_testing"
    files = {"file": ("squat_recording.mp4", mock_video_bytes, "video/mp4")}
    data = {"exercise_name": "Push-Up"}
    r = client.post("/api/v1/video/analyze", data=data, files=files, headers=headers)
    assert r.status_code == 201, f"Multipart video analysis failed: {r.text}"
    upload_analysis = r.json()
    print(f" POST /api/v1/video/analyze (Multipart) -> Push-Up Score: {upload_analysis['form_score']}/100")

    r = client.get("/api/v1/video/history", headers=headers)
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 2
    print(f" GET /api/v1/video/history -> {len(r.json())} critique records found.")

    r = client.get(f"/api/v1/video/{analysis['id']}", headers=headers)
    assert r.status_code == 200, r.text
    print(f" GET /api/v1/video/{analysis['id']} -> Verified specific critique retrieval.")

    # 8. Health Insights
    print("\n[STEP 8] Testing AI Health Insights...")
    r = client.post("/api/v1/insights/generate", headers=headers)
    assert r.status_code == 200, f"Insight generation failed: {r.text}"
    insights = r.json()
    assert len(insights) >= 1
    first_insight = insights[0]
    print(f" POST /api/v1/insights/generate -> {len(insights)} insight(s) generated.")
    print(f"   Headline: [{first_insight['category'].upper()}] {first_insight['title']}")

    r = client.get("/api/v1/insights", headers=headers)
    assert r.status_code == 200, r.text
    print(f" GET /api/v1/insights -> {len(r.json())} insight(s) retrieved.")

    r = client.put(f"/api/v1/insights/{first_insight['id']}/read", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["is_read"] is True
    print(f" PUT /api/v1/insights/{first_insight['id']}/read -> Marked insight as read.")

    # 9. Dashboard Analytics
    print("\n[STEP 9] Testing Dashboard Analytics Aggregation...")
    r = client.get("/api/v1/dashboard", headers=headers)
    assert r.status_code == 200, f"Dashboard retrieval failed: {r.text}"
    dash = r.json()
    assert dash["today"]["calories_consumed"] > 0
    assert dash["today"]["workout_minutes"] > 0
    assert dash["bmi_status"]["current_bmi"] is not None
    assert dash["streaks"]["total_active_days"] >= 1
    assert dash["active_diet_plan_title"] is not None
    assert dash["active_workout_plan_title"] is not None
    print(f" GET /api/v1/dashboard -> OK")
    print(f"   Today: {dash['today']['calories_consumed']}/{dash['today']['calories_target']} kcal, {dash['today']['water_liters']}L water, {dash['today']['steps_count']} steps")
    print(f"   Adherence Score: {dash['weekly_adherence']['overall_score']}%")
    print(f"   Active Diet: {dash['active_diet_plan_title']}")
    print(f"   Active Workout: {dash['active_workout_plan_title']}")
    print(f"   Streaks: Current={dash['streaks']['current_streak_days']} days, Longest={dash['streaks']['longest_streak_days']} days")

    # 10. Analytics & Milestones
    print("\n[STEP 10] Testing Analytics Trends & Milestones...")
    r = client.get("/api/v1/analytics/overview?days=14", headers=headers)
    assert r.status_code == 200, f"Analytics overview failed: {r.text}"
    analytics_data = r.json()
    assert len(analytics_data["daily_trends"]) == 14
    assert analytics_data["period_days"] == 14
    print(f" GET /api/v1/analytics/overview -> 14-day trend generated.")
    print(f"   Averages: {analytics_data['summary']['avg_daily_calories']} kcal/day, {analytics_data['summary']['avg_daily_steps']} steps/day")
    print(f"   Total Workouts: {analytics_data['summary']['total_workout_minutes']} min, {analytics_data['summary']['total_calories_burned']} kcal burned")

    r = client.get("/api/v1/analytics/milestones", headers=headers)
    assert r.status_code == 200, f"Milestones failed: {r.text}"
    ms = r.json()
    assert ms["total_milestones"] >= 7
    print(f" GET /api/v1/analytics/milestones -> {ms['achieved_count']} of {ms['total_milestones']} milestones achieved:")
    for m in ms["milestones"]:
        status_tag = "[ACHIEVED]" if m["achieved"] else "[PENDING]"
        print(f"   {status_tag} {m['title']} ({m['progress_percentage']}%) - {m['description']}")

    print("\n" + "=" * 65)
    print("[SUCCESS] ALL 10 PHASE 4 MODULES & ENDPOINTS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    run_phase4_tests()
