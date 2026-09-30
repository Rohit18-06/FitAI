"""
Workout record request and response schemas.
Pydantic v2 syntax.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    """Payload for POST /workouts."""

    workout_type: str = Field(
        ..., min_length=1, max_length=255, description="Type/name of the workout"
    )
    duration_minutes: int = Field(
        ..., ge=1, le=480, description="Duration in minutes (1–480)"
    )
    calories_burned: float = Field(
        default=0.0, ge=0, description="Estimated calories burned"
    )
    notes: Optional[str] = Field(
        default=None, max_length=1000, description="Optional workout notes"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "workout_type": "Running",
                "duration_minutes": 30,
                "calories_burned": 300.0,
                "notes": "Morning run in the park",
            }
        }
    }


class WorkoutResponse(BaseModel):
    """Workout record returned in responses."""

    id: int
    user_id: int
    workout_type: str
    duration_minutes: int
    calories_burned: float
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
