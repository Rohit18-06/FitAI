"""Pydantic schemas for request/response validation."""

# Auth
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    Token,
    UserResponse,
    LoginResponse,
)

# Tracker schemas
from app.schemas.bmi import BMICreate, BMIResponse
from app.schemas.calorie import CalorieCreate, CalorieResponse
from app.schemas.workout import WorkoutCreate, WorkoutResponse
from app.schemas.water import WaterCreate, WaterResponse
from app.schemas.step import StepCreate, StepResponse

# AI Coach & Dashboard & Analytics schemas
from app.schemas.diet_plan import (
    MealItem,
    Meal,
    DietPlanCreate,
    DietPlanResponse,
)
from app.schemas.workout_plan import (
    ExerciseItem,
    DailyRoutine,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
)
from app.schemas.form_analysis import (
    KeypointCheck,
    FormAnalysisResponse,
)
from app.schemas.health_insight import HealthInsightResponse
from app.schemas.dashboard import (
    TodayOverview,
    BMIStatus,
    WeeklyAdherence,
    StreakStats,
    DashboardOverviewResponse,
)
from app.schemas.analytics import (
    TrendDataPoint,
    TrendsSummary,
    ProgressTelemetry,
    AnalyticsOverviewResponse,
    MilestoneItem,
    MilestonesResponse,
)

# AI Fitness Coach schemas
from app.schemas.coach import (
    CoachChatRequest,
    CoachChatResponse,
    CoachConversationItem,
    ConversationHistoryResponse,
    CoachSidebarStats,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "Token",
    "UserResponse",
    "LoginResponse",
    # BMI
    "BMICreate",
    "BMIResponse",
    # Calorie
    "CalorieCreate",
    "CalorieResponse",
    # Workout
    "WorkoutCreate",
    "WorkoutResponse",
    # Water
    "WaterCreate",
    "WaterResponse",
    # Steps
    "StepCreate",
    "StepResponse",
    # Diet Plan
    "MealItem",
    "Meal",
    "DietPlanCreate",
    "DietPlanResponse",
    # Workout Plan
    "ExerciseItem",
    "DailyRoutine",
    "WorkoutPlanCreate",
    "WorkoutPlanResponse",
    # Form Analysis
    "KeypointCheck",
    "FormAnalysisResponse",
    # Health Insights
    "HealthInsightResponse",
    # Dashboard
    "TodayOverview",
    "BMIStatus",
    "WeeklyAdherence",
    "StreakStats",
    "DashboardOverviewResponse",
    # Analytics
    "TrendDataPoint",
    "TrendsSummary",
    "ProgressTelemetry",
    "AnalyticsOverviewResponse",
    "MilestoneItem",
    "MilestonesResponse",
    # Coach
    "CoachChatRequest",
    "CoachChatResponse",
    "CoachConversationItem",
    "ConversationHistoryResponse",
    "CoachSidebarStats",
]
