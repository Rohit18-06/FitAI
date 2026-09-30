"""Fitness tracking models for workouts, calories, water, steps, and BMI."""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base


class MealTypeEnum(str, Enum):
    """Meal type enumeration."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class BMICategoryEnum(str, Enum):
    """BMI category enumeration."""
    UNDERWEIGHT = "underweight"
    NORMAL = "normal"
    OVERWEIGHT = "overweight"
    OBESE = "obese"


class Workout(Base):
    """
    Workout model representing a logged exercise session.
    
    Fields:
        exercise_name: Name of the exercise (e.g., "Bench Press")
        sets: Number of sets performed
        reps: Number of repetitions per set
        weight_kg: Weight used (in kilograms, 0 if bodyweight)
        duration_minutes: Duration of the exercise session
        calories_burned: Estimated calories burned
        recorded_at: Timestamp of the workout
    """
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_name = Column(String(255), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, default=0.0, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="workouts")

    def __repr__(self) -> str:
        return f"<Workout(id={self.id}, user_id={self.user_id}, exercise={self.exercise_name})>"


class CalorieLog(Base):
    """
    Calorie log model representing a logged food entry.
    
    Fields:
        food_name: Name of the food item
        calories: Total calories in the food
        protein_g: Protein content in grams
        carbs_g: Carbohydrate content in grams
        fat_g: Fat content in grams
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        recorded_at: Timestamp of the log entry
    """
    __tablename__ = "calorie_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    meal_type = Column(SQLEnum(MealTypeEnum), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="calorie_logs")

    def __repr__(self) -> str:
        return f"<CalorieLog(id={self.id}, user_id={self.user_id}, food={self.food_name})>"


class WaterLog(Base):
    """
    Water intake log model.
    
    Fields:
        amount_ml: Amount of water logged in milliliters
        recorded_at: Timestamp of the log entry
    """
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_ml = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="water_logs")

    def __repr__(self) -> str:
        return f"<WaterLog(id={self.id}, user_id={self.user_id}, amount={self.amount_ml}ml)>"


class StepLog(Base):
    """
    Step count log model.
    
    Fields:
        steps: Number of steps recorded
        recorded_at: Timestamp of the log entry
    """
    __tablename__ = "step_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    steps = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="step_logs")

    def __repr__(self) -> str:
        return f"<StepLog(id={self.id}, user_id={self.user_id}, steps={self.steps})>"


class BMIHistory(Base):
    """
    BMI history model for tracking BMI calculations over time.
    
    Fields:
        bmi: Calculated BMI value
        category: BMI category (underweight, normal, overweight, obese)
        created_at: Timestamp of the BMI calculation
    """
    __tablename__ = "bmi_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bmi = Column(Float, nullable=False)
    category = Column(SQLEnum(BMICategoryEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="bmi_history")

    def __repr__(self) -> str:
        return f"<BMIHistory(id={self.id}, user_id={self.user_id}, bmi={self.bmi}, category={self.category})>"
