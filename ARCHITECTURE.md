# FitAI - AI-Powered Fitness Coach
## Complete Architecture Documentation

---

## PHASE 1: PROJECT ARCHITECTURE

### 1. COMPLETE FOLDER STRUCTURE

```
fitai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Button.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardLayout.tsx
│   │   │   │   ├── StatsCard.tsx
│   │   │   │   └── ChartCard.tsx
│   │   │   ├── trackers/
│   │   │   │   ├── BMICalculator.tsx
│   │   │   │   ├── WorkoutTracker.tsx
│   │   │   │   ├── CalorieTracker.tsx
│   │   │   │   ├── WaterTracker.tsx
│   │   │   │   └── StepTracker.tsx
│   │   │   ├── analytics/
│   │   │   │   ├── AnalyticsDashboard.tsx
│   │   │   │   ├── WeightTrendChart.tsx
│   │   │   │   ├── CalorieTrendChart.tsx
│   │   │   │   └── WorkoutFrequencyChart.tsx
│   │   │   ├── ai/
│   │   │   │   ├── DietPlanner.tsx
│   │   │   │   ├── WorkoutPlanner.tsx
│   │   │   │   ├── FitnessCoachChat.tsx
│   │   │   │   └── VideoAnalyzer.tsx
│   │   │   └── reports/
│   │   │       └── ReportGenerator.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── BMI.tsx
│   │   │   ├── Workouts.tsx
│   │   │   ├── Calories.tsx
│   │   │   ├── Water.tsx
│   │   │   ├── Steps.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── DietPlan.tsx
│   │   │   ├── WorkoutPlan.tsx
│   │   │   ├── FitnessCoach.tsx
│   │   │   ├── VideoAnalysis.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── NotFound.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useFitness.ts
│   │   │   ├── useAI.ts
│   │   │   └── useQuery.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── fitness.service.ts
│   │   │   ├── ai.service.ts
│   │   │   └── analytics.service.ts
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── fitnessStore.ts
│   │   │   └── uiStore.ts
│   │   ├── types/
│   │   │   ├── index.ts
│   │   │   ├── auth.ts
│   │   │   ├── fitness.ts
│   │   │   └── ai.ts
│   │   ├── utils/
│   │   │   ├── validators.ts
│   │   │   ├── formatters.ts
│   │   │   └── constants.ts
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   └── animations.css
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   │   ├── favicon.ico
│   │   └── assets/
│   ├── .env.example
│   ├── .env.local
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── README.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── bmi.py
│   │   │   │   │   ├── workouts.py
│   │   │   │   │   ├── calories.py
│   │   │   │   │   ├── water.py
│   │   │   │   │   ├── steps.py
│   │   │   │   │   ├── diet_plan.py
│   │   │   │   │   ├── workout_plan.py
│   │   │   │   │   ├── chat.py
│   │   │   │   │   ├── video_analysis.py
│   │   │   │   │   └── analytics.py
│   │   │   │   └── dependencies.py
│   │   │   └── health.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── bmi.py
│   │   │   ├── workout.py
│   │   │   ├── calorie.py
│   │   │   ├── water.py
│   │   │   ├── step.py
│   │   │   ├── diet_plan.py
│   │   │   ├── workout_plan.py
│   │   │   ├── chat_message.py
│   │   │   └── video_analysis.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── bmi.py
│   │   │   ├── workout.py
│   │   │   ├── calorie.py
│   │   │   ├── water.py
│   │   │   ├── step.py
│   │   │   ├── diet_plan.py
│   │   │   ├── workout_plan.py
│   │   │   ├── chat.py
│   │   │   └── video_analysis.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── fitness_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── cloudinary_service.py
│   │   │   └── analytics_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── formatters.py
│   │       └── constants.py
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_fitness.py
│   │   └── test_ai.py
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── main.py
│   ├── README.md
│   └── docker-compose.yml
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT.md
│   ├── SETUP_GUIDE.md
│   └── DATABASE_SCHEMA.md
│
└── README.md
```

---

## 2. SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                    FitAI SYSTEM ARCHITECTURE                │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   Frontend (React)   │
│   - Vite + TS        │
│   - TailwindCSS      │
│   - Shadcn UI        │
│   - React Query      │
│   - Zustand Store    │
└──────────────┬───────┘
               │ HTTPS
               ▼
┌──────────────────────────────────────────────────────────────┐
│                    API Gateway / CORS                        │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Route Handlers (v1/endpoints)                         │  │
│  │  - Auth, Users, BMI, Workouts, Calories, Water, Steps │  │
│  │  - Diet/Workout Plans, Chat, Video Analysis, Analytics│  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Services Layer                                        │  │
│  │  - AuthService, FitnessService, AIService             │  │
│  │  - GeminiService, CloudinaryService                   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  JWT Authentication & Security                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────┬───────────────────────────────────────────────┘
               │
               ├──────────────┬──────────────┬──────────────┐
               ▼              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
        │PostgreSQL│   │ Gemini   │   │Cloudinary│   │ JWT      │
        │Database  │   │ API 2.5  │   │ Storage  │   │ Secrets  │
        └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

## 3. DATABASE SCHEMA (ER DIAGRAM)

```
User
├── id (PK)
├── email (UNIQUE)
├── username (UNIQUE)
├── password_hash
├── first_name
├── last_name
├── age
├── gender (ENUM: M, F, Other)
├── height_cm
├── weight_kg
├── fitness_goal (ENUM)
├── experience_level (ENUM)
├── created_at
├── updated_at
└── is_active

BMI Record
├── id (PK)
├── user_id (FK → User)
├── weight_kg
├── height_cm
├── bmi_score
├── category (ENUM)
├── recorded_at

Workout
├── id (PK)
├── user_id (FK → User)
├── exercise_name
├── sets
├── reps
├── weight_kg
├── duration_minutes
├── calories_burned
├── recorded_at

Calorie Entry
├── id (PK)
├── user_id (FK → User)
├── food_name
├── calories
├── protein_g
├── carbs_g
├── fat_g
├── meal_type (ENUM: breakfast, lunch, dinner, snack)
├── recorded_at

Water Entry
├── id (PK)
├── user_id (FK → User)
├── amount_ml
├── recorded_at

Step Entry
├── id (PK)
├── user_id (FK → User)
├── steps
├── recorded_at

Diet Plan
├── id (PK)
├── user_id (FK → User)
├── goal
├── breakfast
├── lunch
├── dinner
├── snacks
├── daily_calories
├── created_at
├── valid_until

Workout Plan
├── id (PK)
├── user_id (FK → User)
├── goal
├── experience_level
├── days_per_week
├── plan_data (JSON)
├── created_at
├── valid_until

Chat Message
├── id (PK)
├── user_id (FK → User)
├── role (ENUM: user, assistant)
├── content
├── created_at

Video Analysis
├── id (PK)
├── user_id (FK → User)
├── exercise_name
├── video_url (Cloudinary)
├── form_score
├── strengths (JSON Array)
├── issues (JSON Array)
├── improvements (JSON Array)
├── injury_risk
├── analysis_data (JSON)
├── created_at
```

---

## 4. API DESIGN

### Authentication Endpoints
```
POST   /api/v1/auth/register          → Register user
POST   /api/v1/auth/login             → Login & get JWT token
POST   /api/v1/auth/refresh           → Refresh token
POST   /api/v1/auth/logout            → Logout
```

### User Endpoints
```
GET    /api/v1/users/me               → Get current user
PUT    /api/v1/users/me               → Update profile
```

### Fitness Tracking Endpoints
```
POST   /api/v1/bmi                    → Record BMI
GET    /api/v1/bmi/history            → Get BMI records

POST   /api/v1/workouts               → Log workout
GET    /api/v1/workouts               → Get workouts
GET    /api/v1/workouts/{id}          → Get workout details

POST   /api/v1/calories               → Log calories
GET    /api/v1/calories               → Get calorie entries

POST   /api/v1/water                  → Log water intake
GET    /api/v1/water                  → Get water entries

POST   /api/v1/steps                  → Log steps
GET    /api/v1/steps                  → Get step entries
```

### AI Features Endpoints
```
POST   /api/v1/diet-plan              → Generate diet plan
GET    /api/v1/diet-plan/current      → Get current diet plan

POST   /api/v1/workout-plan           → Generate workout plan
GET    /api/v1/workout-plan/current   → Get current workout plan

POST   /api/v1/chat                   → Send message to AI coach
GET    /api/v1/chat/history           → Get chat history

POST   /api/v1/video-analysis/upload  → Upload video for analysis
GET    /api/v1/video-analysis/{id}    → Get analysis results
```

### Analytics Endpoints
```
GET    /api/v1/analytics/dashboard    → Get dashboard data
GET    /api/v1/analytics/weight-trend → Get weight trend data
GET    /api/v1/analytics/bmi-trend    → Get BMI trend data
GET    /api/v1/analytics/calories-trend
GET    /api/v1/analytics/workouts-frequency
GET    /api/v1/analytics/water-intake
GET    /api/v1/analytics/steps-trend
```

### Report Endpoints
```
GET    /api/v1/reports/pdf            → Generate & download PDF report
```

---

## 5. AUTHENTICATION FLOW

```
┌─────────────┐
│ User        │
└──────┬──────┘
       │
       │ 1. POST /auth/register or /auth/login
       │    (email, password)
       ▼
┌──────────────────────────────────────┐
│ Backend - Hash Password (bcrypt)     │
│         - Verify Credentials         │
│         - Generate JWT Token         │
└──────┬───────────────────────────────┘
       │
       │ 2. Return JWT Token
       │    (Access Token + Refresh Token)
       ▼
┌──────────────────────────────────────┐
│ Frontend - Store in Zustand Store    │
│          - Set in Request Headers    │
└──────┬───────────────────────────────┘
       │
       │ 3. Protected Requests
       │    Header: Authorization: Bearer <token>
       ▼
┌──────────────────────────────────────┐
│ Backend - Verify JWT                 │
│         - Extract user_id            │
│         - Process Request            │
└──────┬───────────────────────────────┘
       │
       │ 4. Return Protected Data
       ▼
┌──────────────┐
│ User Data    │
└──────────────┘

Token Refresh Flow:
- Access Token: 15 minutes
- Refresh Token: 7 days
- Auto-refresh on 401 response
```

---

## 6. FRONTEND ROUTING PLAN

```
/                          → Landing (redirect to /dashboard if authenticated)
/login                     → Login page
/register                  → Registration page

/dashboard                 → Main dashboard

Fitness Tracking:
/fitness/bmi               → BMI calculator & history
/fitness/workouts          → Workout logger & history
/fitness/calories          → Calorie tracker & log food
/fitness/water             → Water intake tracker
/fitness/steps             → Step counter tracker

AI Features:
/ai/diet-plan              → AI Diet Planner
/ai/workout-plan           → AI Workout Planner
/ai/coach                  → AI Fitness Coach Chat
/ai/video-analysis         → Video Form Analysis

Analytics:
/analytics                 → Dashboard with all charts

Reports:
/reports                   → Generate & download PDF

Settings:
/settings                  → User profile & preferences

Not Found:
404                        → 404 page
```

---

## 7. ENVIRONMENT VARIABLES

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
```

### Backend (.env)
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fitai_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Gemini
GEMINI_API_KEY=your-gemini-api-key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# CORS
CORS_ORIGINS=http://localhost:5173,https://yourdomain.com

# Environment
ENVIRONMENT=development
```

---

## 8. DEPLOYMENT ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
        ┌────────────────────────┐
        │  Vercel (Frontend)     │
        │  - React + Vite Build  │
        │  - Static Hosting      │
        │  - CDN Optimization    │
        └────────────┬───────────┘
                     │ API Calls
                     ▼
        ┌────────────────────────┐
        │   Render (Backend)     │
        │  - FastAPI Server      │
        │  - Auto-restart        │
        │  - Environment Config  │
        └────────────┬───────────┘
                     │
                ┌────┴────┬─────────┬──────────┐
                ▼         ▼         ▼          ▼
        ┌──────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
        │PostgreSQL│ │Gemini│ │Cloudy │ │External  │
        │ (Hosted) │ │ API  │ │Storage │ │Services  │
        └──────────┘ └──────┘ └────────┘ └──────────┘
```

---

## TECH STACK SUMMARY

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + Vite | UI Framework + Build Tool |
| Frontend | TypeScript | Type Safety |
| Frontend | TailwindCSS | Styling |
| Frontend | Shadcn UI | Component Library |
| Frontend | React Query | Server State Management |
| Frontend | Zustand | Client State Management |
| Frontend | React Hook Form | Form Management |
| Frontend | Zod | Schema Validation |
| Frontend | Recharts | Data Visualization |
| Backend | FastAPI | Web Framework |
| Backend | SQLAlchemy | ORM |
| Backend | Alembic | Migrations |
| Backend | Pydantic | Data Validation |
| Backend | JWT | Authentication |
| Backend | bcrypt | Password Hashing |
| Database | PostgreSQL | Primary Data Store |
| AI | Gemini 2.5 Flash | AI/ML Services |
| Storage | Cloudinary | Video/Image Storage |
| Deployment | Vercel | Frontend Hosting |
| Deployment | Render | Backend Hosting |

---

## SECURITY IMPLEMENTATION

✅ JWT Authentication with refresh tokens
✅ Password hashing with bcrypt
✅ Input validation (Pydantic + Zod)
✅ CORS configuration
✅ Rate limiting on API endpoints
✅ Secure file uploads to Cloudinary
✅ Environment variables for all secrets
✅ HTTPS enforced in production
✅ SQL injection prevention via SQLAlchemy ORM
✅ XSS protection via React escaping

---

## PHASE 1 CHECKLIST

- ✅ Complete folder structure defined
- ✅ System architecture diagram created
- ✅ Database schema designed (ER Diagram)
- ✅ API endpoints designed
- ✅ Authentication flow documented
- ✅ Frontend routing plan created
- ✅ Environment variables defined
- ✅ Deployment architecture documented
- ✅ Tech stack finalized
- ✅ Security measures outlined

---

**NEXT STEP:** Proceed to Phase 2 - Backend Foundation
**STATUS:** ⏳ Awaiting approval to proceed with Phase 2

