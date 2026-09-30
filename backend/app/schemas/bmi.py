"""
BMI request and response schemas.
Pydantic v2 syntax.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BMICreate(BaseModel):
    """Payload for POST /bmi/calculate."""

    height_cm: float = Field(
        ..., gt=50, lt=300, description="Height in centimetres (50–300)"
    )
    weight_kg: float = Field(
        ..., gt=1, lt=700, description="Weight in kilograms (1–700)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {"height_cm": 175.0, "weight_kg": 70.0}
        }
    }


class BMIResponse(BaseModel):
    """BMI record returned in responses."""

    id: int
    user_id: int
    height_cm: float
    weight_kg: float
    bmi: float
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}
