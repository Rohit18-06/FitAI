"""
Calorie record request and response schemas.
Pydantic v2 syntax.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CalorieCreate(BaseModel):
    """Payload for POST /calories."""

    meal_name: str = Field(
        ..., min_length=1, max_length=255, description="Name of the meal or food item"
    )
    calories: float = Field(..., ge=0, description="Total calories")
    protein: float = Field(default=0.0, ge=0, description="Protein in grams")
    carbs: float = Field(default=0.0, ge=0, description="Carbohydrates in grams")
    fats: float = Field(default=0.0, ge=0, description="Fats in grams")

    model_config = {
        "json_schema_extra": {
            "example": {
                "meal_name": "Grilled Chicken Breast",
                "calories": 165.0,
                "protein": 31.0,
                "carbs": 0.0,
                "fats": 3.6,
            }
        }
    }


class CalorieResponse(BaseModel):
    """Calorie record returned in responses."""

    id: int
    user_id: int
    meal_name: str
    calories: float
    protein: float
    carbs: float
    fats: float
    created_at: datetime

    model_config = {"from_attributes": True}
