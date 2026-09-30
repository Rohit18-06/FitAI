"""
Diet plan service.
Orchestrates AI diet generation, persistence, and active plan management.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bmi import BMIRecord
from app.models.diet_plan import DietPlan
from app.models.user import User
from app.schemas.diet_plan import DietPlanCreate
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class DietService:
    """Business logic for AI Diet Planner."""

    @staticmethod
    def _compute_default_calories(db: Session, user: User, goal: str) -> float:
        """Estimate TDEE from latest BMI record or sensible standard defaults."""
        latest_bmi = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.desc())
            .first()
        )
        if latest_bmi:
            weight = latest_bmi.weight_kg
            height = latest_bmi.height_cm
            # Mifflin-St Jeor estimate (assuming moderate activity 1.45)
            bmr = (10.0 * weight) + (6.25 * height) - (5.0 * 28) + 5
            tdee = bmr * 1.45
        else:
            tdee = 2200.0

        if goal == "weight_loss":
            return max(1200.0, round(tdee - 500.0, 0))
        elif goal == "muscle_gain":
            return round(tdee + 350.0, 0)
        elif goal == "endurance":
            return round(tdee + 200.0, 0)
        return round(tdee, 0)

    @classmethod
    def create_diet_plan(
        cls,
        db: Session,
        user: User,
        data: DietPlanCreate,
    ) -> DietPlan:
        """
        Generate and persist a new tailored AI Diet Plan for the user.
        Deactivates previous active plans.
        """
        target_calories = data.target_calories
        if target_calories is None or target_calories <= 0:
            target_calories = cls._compute_default_calories(db, user, data.fitness_goal)

        latest_bmi = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.desc())
            .first()
        )
        weight_kg = latest_bmi.weight_kg if latest_bmi else 70.0

        # Generate plan via Gemini or sports science engine
        plan_data = GeminiService.generate_diet_plan(
            goal=data.fitness_goal,
            preference=data.dietary_preference,
            target_calories=target_calories,
            allergies=data.allergies_or_restrictions,
            meals_per_day=data.meals_per_day,
            user_weight_kg=weight_kg,
        )

        try:
            # Set older plans to inactive
            db.query(DietPlan).filter(
                DietPlan.user_id == user.id,
                DietPlan.is_active == True,
            ).update({"is_active": False})

            # Create new record
            record = DietPlan(
                user_id=user.id,
                title=plan_data.get("title", f"{data.fitness_goal.title()} Meal Plan"),
                fitness_goal=data.fitness_goal,
                dietary_preference=data.dietary_preference,
                target_calories=target_calories,
                target_protein_g=float(plan_data.get("target_protein_g", 120.0)),
                target_carbs_g=float(plan_data.get("target_carbs_g", 250.0)),
                target_fats_g=float(plan_data.get("target_fats_g", 60.0)),
                meals=json.dumps(plan_data.get("meals", [])),
                is_active=True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.info("Diet plan created id=%s for user_id=%s", record.id, user.id)
            return record
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save diet plan for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate and save diet plan",
            ) from exc

    @staticmethod
    def get_active_diet_plan(db: Session, user: User) -> Optional[DietPlan]:
        """Retrieve the currently active diet plan for the user."""
        return (
            db.query(DietPlan)
            .filter(DietPlan.user_id == user.id, DietPlan.is_active == True)
            .order_by(DietPlan.created_at.desc())
            .first()
        )

    @staticmethod
    def get_diet_plan_history(db: Session, user: User, limit: int = 10) -> List[DietPlan]:
        """Retrieve past diet plans for the user."""
        return (
            db.query(DietPlan)
            .filter(DietPlan.user_id == user.id)
            .order_by(DietPlan.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def activate_diet_plan(db: Session, user: User, plan_id: int) -> DietPlan:
        """Mark a specific historical plan as active and deactivate others."""
        plan = (
            db.query(DietPlan)
            .filter(DietPlan.id == plan_id, DietPlan.user_id == user.id)
            .first()
        )
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diet plan not found",
            )
        try:
            db.query(DietPlan).filter(
                DietPlan.user_id == user.id,
                DietPlan.is_active == True,
            ).update({"is_active": False})
            plan.is_active = True
            db.commit()
            db.refresh(plan)
            return plan
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to activate diet plan %s for user %s", plan_id, user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not activate diet plan",
            ) from exc
