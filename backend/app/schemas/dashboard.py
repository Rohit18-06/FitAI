"""
Dashboard schemas using Pydantic v2.
Aggregates health, nutrition, workout, and streak telemetry.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.health_insight import HealthInsightResponse


class TodayOverview(BaseModel):
    """Real-time metrics for today."""
    calories_consumed: float = Field(default=0.0)
    calories_target: float = Field(default=2200.0)
    calories_remaining: float = Field(default=2200.0)
    water_liters: float = Field(default=0.0)
    water_target_liters: float = Field(default=2.5)
    steps_count: int = Field(default=0)
    steps_target: int = Field(default=10000)
    workout_minutes: int = Field(default=0)
    calories_burned: float = Field(default=0.0)


class BMIStatus(BaseModel):
    """Latest recorded BMI telemetry."""
    current_bmi: Optional[float] = None
    category: Optional[str] = "Not Recorded"
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


class WeeklyAdherence(BaseModel):
    """Weekly consistency and goal completion stats."""
    overall_score: int = Field(default=100, ge=0, le=100, description="0–100% adherence score")
    workout_days_completed: int = Field(default=0)
    target_workout_days: int = Field(default=4)
    water_target_met_days: int = Field(default=0)
    calorie_target_met_days: int = Field(default=0)


class StreakStats(BaseModel):
    """Tracking consistency streaks."""
    current_streak_days: int = Field(default=0)
    longest_streak_days: int = Field(default=0)
    total_active_days: int = Field(default=0)


class DashboardOverviewResponse(BaseModel):
    """Full comprehensive dashboard response."""
    user_id: int
    username: str
    today: TodayOverview
    bmi_status: BMIStatus
    weekly_adherence: WeeklyAdherence
    streaks: StreakStats
    active_diet_plan_title: Optional[str] = None
    active_workout_plan_title: Optional[str] = None
    recent_insights: List[HealthInsightResponse] = Field(default_factory=list)
