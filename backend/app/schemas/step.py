"""
Step count request and response schemas.
Pydantic v2 syntax.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StepCreate(BaseModel):
    """Payload for POST /steps."""

    steps: int = Field(
        ..., ge=0, le=200_000, description="Number of steps taken"
    )
    distance_km: float = Field(
        default=0.0, ge=0, description="Distance covered in kilometres"
    )
    calories_burned: float = Field(
        default=0.0, ge=0, description="Estimated calories burned"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "steps": 8500,
                "distance_km": 6.2,
                "calories_burned": 280.0,
            }
        }
    }


class StepResponse(BaseModel):
    """Step record returned in responses."""

    id: int
    user_id: int
    steps: int
    distance_km: float
    calories_burned: float
    created_at: datetime

    model_config = {"from_attributes": True}
