"""
Diet plan schemas using Pydantic v2.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class MealItem(BaseModel):
    """Single food item within a meal."""
    food_name: str = Field(..., description="Name of food or ingredient")
    serving_size: str = Field(..., description="Portion size e.g. '150g' or '1 cup'")
    calories: float = Field(..., ge=0, description="Estimated calories")
    protein_g: float = Field(default=0.0, ge=0, description="Protein in grams")
    carbs_g: float = Field(default=0.0, ge=0, description="Carbohydrates in grams")
    fats_g: float = Field(default=0.0, ge=0, description="Fats in grams")
    notes: Optional[str] = Field(default=None, description="Culinary or prep notes")


class Meal(BaseModel):
    """Structured meal (Breakfast, Lunch, Dinner, Snack)."""
    meal_type: str = Field(..., description="Breakfast, Lunch, Dinner, or Snack")
    name: str = Field(..., description="Name or title of meal")
    target_calories: float = Field(..., ge=0, description="Caloric target for this meal")
    items: List[MealItem] = Field(default_factory=list, description="Foods included")
    recipe_steps: List[str] = Field(default_factory=list, description="Quick prep instructions")


class DietPlanCreate(BaseModel):
    """Request payload to generate a new AI diet plan."""
    fitness_goal: str = Field(
        default="maintenance",
        description="Goal: weight_loss, muscle_gain, maintenance, or endurance",
    )
    dietary_preference: str = Field(
        default="omnivore",
        description="Preference: omnivore, vegetarian, vegan, keto, paleo, pescatarian, mediterranean",
    )
    target_calories: Optional[float] = Field(
        default=None,
        ge=800,
        le=6000,
        description="Optional manual target calories. If omitted, calculated from profile.",
    )
    allergies_or_restrictions: List[str] = Field(
        default_factory=list,
        description="List of allergens or disliked ingredients e.g. ['peanuts', 'dairy', 'gluten']",
    )
    meals_per_day: int = Field(
        default=3,
        ge=2,
        le=6,
        description="Number of meals per day (2–6)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "fitness_goal": "muscle_gain",
                "dietary_preference": "omnivore",
                "target_calories": 2500,
                "allergies_or_restrictions": ["shellfish"],
                "meals_per_day": 4,
            }
        }
    }


class DietPlanResponse(BaseModel):
    """Response returned when a diet plan is generated or retrieved."""
    id: int
    user_id: int
    title: str
    fitness_goal: str
    dietary_preference: str
    target_calories: float
    target_protein_g: float
    target_carbs_g: float
    target_fats_g: float
    meals: List[Meal]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("meals", mode="before")
    @classmethod
    def parse_meals(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v
