"""
Workout plan schemas using Pydantic v2.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class ExerciseItem(BaseModel):
    """Specific exercise with sets, reps, and coaching cues."""
    name: str = Field(..., description="Exercise name e.g. 'Barbell Back Squat'")
    target_muscle: str = Field(..., description="Target muscle group e.g. 'Quadriceps, Glutes'")
    sets: int = Field(..., ge=1, le=10, description="Number of sets")
    reps: str = Field(..., description="Reps or duration e.g. '8-10' or '45s'")
    rest_seconds: int = Field(default=60, ge=0, le=300, description="Rest period between sets")
    coaching_tips: str = Field(..., description="Form cue e.g. 'Keep chest up and knees tracking over toes'")


class DailyRoutine(BaseModel):
    """Daily workout routine within a multi-day plan."""
    day_number: int = Field(..., ge=1, le=7, description="Day number (1 to 7)")
    day_name: str = Field(..., description="Title e.g. 'Day 1: Upper Body Power'")
    focus: str = Field(..., description="Focus area e.g. 'Chest, Shoulders, Triceps'")
    warmup: List[str] = Field(default_factory=list, description="Warmup drills")
    exercises: List[ExerciseItem] = Field(default_factory=list, description="Prescribed exercises")
    cooldown: List[str] = Field(default_factory=list, description="Cooldown stretches")


class WorkoutPlanCreate(BaseModel):
    """Request payload to generate a customized AI workout routine."""
    fitness_level: str = Field(
        default="intermediate",
        description="Level: beginner, intermediate, or advanced",
    )
    fitness_goal: str = Field(
        default="hypertrophy",
        description="Goal: strength, hypertrophy, fat_loss, endurance, or general_health",
    )
    days_per_week: int = Field(
        default=4,
        ge=1,
        le=7,
        description="Days per week available to train (1–7)",
    )
    equipment: str = Field(
        default="full_gym",
        description="Available equipment: full_gym, dumbbells, bodyweight_only, or resistance_bands",
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Optional focus areas e.g. ['core', 'legs', 'back']",
    )
    injuries_or_limitations: List[str] = Field(
        default_factory=list,
        description="Optional restrictions e.g. ['lower back pain', 'wrist injury']",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "fitness_level": "intermediate",
                "fitness_goal": "hypertrophy",
                "days_per_week": 4,
                "equipment": "full_gym",
                "focus_areas": ["chest", "arms"],
                "injuries_or_limitations": ["knee sensitivity"],
            }
        }
    }


class WorkoutPlanResponse(BaseModel):
    """Response returned when a workout plan is generated or retrieved."""
    id: int
    user_id: int
    title: str
    fitness_level: str
    fitness_goal: str
    days_per_week: int
    equipment: str
    routines: List[DailyRoutine]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("routines", mode="before")
    @classmethod
    def parse_routines(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v
