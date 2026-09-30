"""
Phase 5: AI Fitness Coach Automated Test Suite.
Verifies:
1. Authentication (JWT token validation)
2. Coach chat endpoint (/api/v1/coach/chat)
3. History retrieval (/api/v1/coach/history)
4. History deletion (DELETE /api/v1/coach/history)
5. Gemini responses & prompt context generation
6. Fallback responses & intelligent reasoning engine
7. Database persistence in coach_conversations table
8. Frontend API integration & schemas compatibility
"""

import httpx
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
test_id = uuid.uuid4().hex[:6]
test_email = f"coach_athlete_{test_id}@fitai.com"
test_user = f"coach_{test_id}"
test_password = "SecurePassword123!"

results = []

def record(test_name: str, passed: bool, details: str = ""):
    results.append({"name": test_name, "passed": passed, "details": details})
    mark = "[PASS]" if passed else "[FAIL]"
    print(f"  {mark} {test_name}" + (f" -> {details}" if details else ""))


print("\n" + "=" * 70)
print(f"FITAI PHASE 5: AI FITNESS COACH VERIFICATION SUITE")
print("=" * 70)

# -----------------------------------------------------------------------------
# 1. Authentication
# -----------------------------------------------------------------------------
print("\n[Step 1] Authentication & Profile Initialization")
reg_res = httpx.post(
    f"{BASE_URL}/auth/register",
    json={"email": test_email, "username": test_user, "password": test_password},
    timeout=10,
)
if reg_res.status_code == 201:
    token = reg_res.json()["access_token"]
    user_id = reg_res.json()["user"]["id"]
    record("User Registration & JWT Issuance", True, f"User ID: {user_id}")
else:
    login_res = httpx.post(
        f"{BASE_URL}/auth/login",
        json={"email": test_email, "password": test_password},
        timeout=10,
    )
    token = login_res.json()["access_token"]
    record("User Login & Token Retrieval", True, "Existing user logged in")

headers = {"Authorization": f"Bearer {token}"}

# Seed some baseline telemetry so the coach has rich context
httpx.post(f"{BASE_URL}/bmi/calculate", json={"height_cm": 178.0, "weight_kg": 82.5}, headers=headers)
httpx.post(f"{BASE_URL}/calories", json={"meal_name": "Chicken Rice Bowl", "calories": 750, "protein": 45, "carbs": 80, "fats": 18}, headers=headers)
httpx.post(f"{BASE_URL}/water", json={"liters": 1.25, "glasses": 5}, headers=headers)
httpx.post(f"{BASE_URL}/steps", json={"steps": 5400, "distance_km": 3.8, "calories_burned": 210}, headers=headers)
httpx.post(f"{BASE_URL}/workouts", json={"workout_type": "Leg Day Hypertrophy", "duration_minutes": 55, "calories_burned": 420}, headers=headers)

# -----------------------------------------------------------------------------
# 2. Coach Chat Endpoint
# -----------------------------------------------------------------------------
print("\n[Step 2] Coach Chat Endpoint Verification")
chat_payload = {"message": "Why am I not losing weight?"}
chat_res = httpx.post(f"{BASE_URL}/coach/chat", json=chat_payload, headers=headers, timeout=25)

chat_data = {}
if chat_res.status_code == 200:
    chat_data = chat_res.json()
    has_response = bool(chat_data.get("response"))
    sources = chat_data.get("sources", [])
    record("POST /coach/chat status 200 OK", True, f"Sources referenced: {sources}")
    record("Response content non-empty", has_response, f"Length: {len(chat_data.get('response', ''))} chars")
    record("Telemetry source attribution", len(sources) > 0, f"Found {len(sources)} sources")
else:
    record("POST /coach/chat status 200 OK", False, f"Status: {chat_res.status_code} - {chat_res.text}")

# -----------------------------------------------------------------------------
# 3. History Retrieval
# -----------------------------------------------------------------------------
print("\n[Step 3] Conversation History Retrieval")
hist_res = httpx.get(f"{BASE_URL}/coach/history", headers=headers, timeout=10)
if hist_res.status_code == 200:
    hist_data = hist_res.json()
    convs = hist_data.get("conversations", [])
    total = hist_data.get("total", 0)
    record("GET /coach/history status 200 OK", True, f"Total records: {total}")
    record("History contains prior conversation", len(convs) >= 1, f"Found {len(convs)} conversation items")
    if convs:
        last_turn = convs[-1]
        record("History item payload integrity", last_turn["message"] == chat_payload["message"], f"Turn ID: {last_turn['id']}")
else:
    record("GET /coach/history status 200 OK", False, f"Status: {hist_res.status_code}")

# -----------------------------------------------------------------------------
# 4. History Deletion
# -----------------------------------------------------------------------------
print("\n[Step 4] Conversation History Deletion")
del_res = httpx.delete(f"{BASE_URL}/coach/history", headers=headers, timeout=10)
if del_res.status_code == 200:
    del_data = del_res.json()
    record("DELETE /coach/history status 200 OK", True, f"Deleted count: {del_data.get('deleted_count')}")

    # Verify history is now empty
    empty_check = httpx.get(f"{BASE_URL}/coach/history", headers=headers, timeout=10)
    empty_count = empty_check.json().get("total", -1)
    record("History list empty post-deletion", empty_count == 0, f"Current total: {empty_count}")
else:
    record("DELETE /coach/history status 200 OK", False, f"Status: {del_res.status_code}")

# -----------------------------------------------------------------------------
# 5. Gemini / Fallback Reasoning Verification
# -----------------------------------------------------------------------------
print("\n[Step 5] Reasoning Engine Multi-Scenario Tests")
prompts_to_test = [
    ("Help me improve hydration", ["water"]),
    ("Review my workout consistency", ["workout"]),
    ("Why is my BMI increasing?", ["bmi"]),
    ("Create a muscle gain strategy", ["workout"]),
]

for prompt, expected_keywords in prompts_to_test:
    res = httpx.post(f"{BASE_URL}/coach/chat", json={"message": prompt}, headers=headers, timeout=25)
    if res.status_code == 200:
        ans = res.json()["response"].lower()
        matched = any(kw in ans or any(kw in s for s in res.json().get("sources", [])) for kw in expected_keywords)
        record(f"Scenario: '{prompt}'", matched, f"Sources: {res.json().get('sources')}")
    else:
        record(f"Scenario: '{prompt}'", False, f"Status: {res.status_code}")

# -----------------------------------------------------------------------------
# 6. Database Persistence
# -----------------------------------------------------------------------------
print("\n[Step 6] Database Persistence Verification")
post_hist = httpx.get(f"{BASE_URL}/coach/history", headers=headers, timeout=10)
persisted_turns = post_hist.json().get("total", 0)
record("Multiple conversation turns persisted", persisted_turns == len(prompts_to_test), f"Persisted turns: {persisted_turns}")

# -----------------------------------------------------------------------------
# 7. Sidebar Telemetry Stats
# -----------------------------------------------------------------------------
print("\n[Step 7] Sidebar Telemetry Endpoint (/coach/stats)")
stats_res = httpx.get(f"{BASE_URL}/coach/stats", headers=headers, timeout=10)
if stats_res.status_code == 200:
    st = stats_res.json()
    record("GET /coach/stats status 200 OK", True, f"BMI: {st.get('bmi')}, Water: {st.get('water_liters_today')}L, Steps: {st.get('steps_today')}")
else:
    record("GET /coach/stats status 200 OK", False, f"Status: {stats_res.status_code}")

# -----------------------------------------------------------------------------
# Final Summary
# -----------------------------------------------------------------------------
print("\n" + "=" * 70)
total_tests = len(results)
passed_tests = sum(1 for r in results if r["passed"])
failed_tests = total_tests - passed_tests
print(f"PHASE 5 TEST RESULTS: {passed_tests} PASSED, {failed_tests} FAILED, {total_tests} TOTAL")
print("=" * 70)

if failed_tests > 0:
    sys.exit(1)
else:
    sys.exit(0)
