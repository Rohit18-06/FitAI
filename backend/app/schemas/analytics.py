"""
Analytics and progress tracking schemas using Pydantic v2.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class TrendDataPoint(BaseModel):
    """Historical data point for a single calendar day."""
    date: str = Field(..., description="Date string YYYY-MM-DD")
    calories_consumed: float = Field(default=0.0)
    water_liters: float = Field(default=0.0)
    steps: int = Field(default=0)
    workout_minutes: int = Field(default=0)
    calories_burned: float = Field(default=0.0)
    weight_kg: Optional[float] = None


class TrendsSummary(BaseModel):
    """Aggregated averages over the requested date range."""
    avg_daily_calories: float = Field(default=0.0)
    avg_daily_steps: int = Field(default=0)
    avg_daily_water_liters: float = Field(default=0.0)
    total_workout_minutes: int = Field(default=0)
    total_calories_burned: float = Field(default=0.0)


class ProgressTelemetry(BaseModel):
    """Weight and BMI progression over the timeline."""
    start_weight_kg: Optional[float] = None
    current_weight_kg: Optional[float] = None
    weight_delta_kg: float = Field(default=0.0)
    start_bmi: Optional[float] = None
    current_bmi: Optional[float] = None
    bmi_delta: float = Field(default=0.0)


class AnalyticsOverviewResponse(BaseModel):
    """Analytics response with multi-day trends, averages, and progression."""
    user_id: int
    period_days: int
    summary: TrendsSummary
    progress: ProgressTelemetry
    daily_trends: List[TrendDataPoint]


class MilestoneItem(BaseModel):
    """Achievement milestone for user consistency and athletic goals."""
    id: str
    category: str
    title: str
    description: str
    achieved: bool
    achieved_date: Optional[str] = None
    progress_percentage: int = Field(..., ge=0, le=100)
    badge_icon: str


class MilestonesResponse(BaseModel):
    """List of all available and achieved user milestones."""
    total_milestones: int
    achieved_count: int
    milestones: List[MilestoneItem]
