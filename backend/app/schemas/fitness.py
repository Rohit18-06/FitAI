"""Fitness tracking Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WorkoutCreate(BaseModel):
    """Schema for creating a workout entry."""
    exercise_name: str = Field(..., min_length=2, max_length=255, description="Name of the exercise")
    sets: int = Field(..., ge=1, le=100, description="Number of sets")
    reps: int = Field(..., ge=1, le=1000, description="Number of repetitions")
    weight_kg: float = Field(default=0.0, ge=0, description="Weight in kilograms")
    duration_minutes: int = Field(..., ge=1, le=480, description="Duration in minutes")
    calories_burned: float = Field(..., ge=0, description="Estimated calories burned")


class WorkoutResponse(WorkoutCreate):
    """Response schema for workout data."""
    id: int
    user_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class CalorieCreate(BaseModel):
    """Schema for creating a calorie log entry."""
    food_name: str = Field(..., min_length=2, max_length=255, description="Name of the food")
    calories: float = Field(..., ge=0, description="Total calories")
    protein_g: float = Field(..., ge=0, description="Protein in grams")
    carbs_g: float = Field(..., ge=0, description="Carbohydrates in grams")
    fat_g: float = Field(..., ge=0, description="Fat in grams")
    meal_type: str = Field(..., description="Meal type (breakfast, lunch, dinner, snack)")


class CalorieResponse(CalorieCreate):
    """Response schema for calorie log data."""
    id: int
    user_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class WaterCreate(BaseModel):
    """Schema for creating a water intake log entry."""
    amount_ml: float = Field(..., gt=0, le=10000, description="Amount in milliliters")


class WaterResponse(WaterCreate):
    """Response schema for water log data."""
    id: int
    user_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class StepCreate(BaseModel):
    """Schema for creating a step count log entry."""
    steps: int = Field(..., ge=0, le=1000000, description="Number of steps")


class StepResponse(StepCreate):
    """Response schema for step log data."""
    id: int
    user_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class BMIResponse(BaseModel):
    """Response schema for BMI calculation."""
    id: int = Field(..., description="BMI history record ID")
    user_id: int
    bmi: float = Field(..., description="Calculated BMI value")
    category: str = Field(..., description="BMI category")
    created_at: datetime

    class Config:
        from_attributes = True
