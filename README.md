# FitAI ⚡ — AI Personal Trainer & Health Intelligence Platform

FitAI is an end-to-end, production-grade AI fitness platform combining computer-vision form analysis, wearable health intelligence, sports-science periodized training, social fitness networks, and generative coaching.

---

## 🚀 System Architecture & Capabilities

FitAI is developed across 8 core engineering phases:

- **Phase 1: Foundation & Security** — FastAPI asynchronous architecture, SQLite/PostgreSQL engine, Argon2/Bcrypt hashing, JWT Bearer authentication.
- **Phase 2: Authentication & Athlete Profiles** — User registration, credential security, profile customisation, token blacklisting.
- **Phase 3: Core Trackers** — Telemetry for BMI categories, Calorie & Macronutrient tracking, Water hydration, Steps, and logged Workouts.
- **Phase 4: AI Generators & Computer Vision** — Gemini-powered Diet Planner, Workout Generator, and automated Video Form Analyzer.
- **Phase 5: AI Fitness Coach** — Real-time conversational AI coaching assistant grounded in athlete telemetry with glassmorphism UI.
- **Phase 6: Wearables & Real-Time Health Intelligence** — Health Connect, Google Fit, and Apple Health ingestion, sleep stage analytics, HRV/Resting HR, and Personal Records.
- **Phase 7: Social Fitness Ecosystem** — Friendships, follower networks, global & friend activity feeds, interactive challenges, teams, and XP/Badge gamification.
- **Phase 8: AI Personal Trainer & Smart Coaching Platform** — Multi-week sports-science periodization, daily recovery readiness scoring, biomechanical injury risk radar, automated 21-day plateau detection, progressive overload 1RM calculations (Brzycki formula), and weekly AI coaching reports.

---

## 🛠 Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, SQLite / PostgreSQL, PyJWT, Pytest.
- **Frontend**: TypeScript, Vite, Vanilla CSS (Glassmorphism design system), GSAP animations, Lucide icons, Chart.js.
- **AI & Sports Science**: Google Gemini API, Brzycki 1RM formula, Biomechanical risk engine, Rolling-window plateau analysis.

---

## 🏁 Quickstart Guide

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations / start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive Swagger documentation will be available at:
`http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

The web application will open at:
`http://localhost:5173`

---

## 🧪 Testing

Run backend integration test suites:

```bash
cd backend
venv\Scripts\python -m pytest tests/test_phase8.py -v
```

Run frontend typechecking & production build:

```bash
cd frontend
npx tsc --noEmit
npm run build
```

---

## 📚 Key Documentation

- [System Architecture (ARCHITECTURE.md)](ARCHITECTURE.md)
- [Backend API Documentation (backend/API_DOCUMENTATION.md)](backend/API_DOCUMENTATION.md)
- [Backend Development Guide (backend/README.md)](backend/README.md)
