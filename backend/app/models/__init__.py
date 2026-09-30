"""Database models for FitAI application."""

from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.calorie import CalorieRecord
from app.models.workout import WorkoutRecord
from app.models.water import WaterRecord
from app.models.step import StepRecord
from app.models.diet_plan import DietPlan
from app.models.workout_plan import WorkoutPlan
from app.models.form_analysis import FormAnalysisRecord
from app.models.health_insight import HealthInsight
from app.models.coach_conversation import CoachConversation

__all__ = [
    "User",
    "BMIRecord",
    "CalorieRecord",
    "WorkoutRecord",
    "WaterRecord",
    "StepRecord",
    "DietPlan",
    "WorkoutPlan",
    "FormAnalysisRecord",
    "HealthInsight",
    "CoachConversation",
]
