"""
Workout generator service.
Orchestrates AI workout routine generation, persistence, and plan management.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.workout_plan import WorkoutPlan
from app.models.user import User
from app.schemas.workout_plan import WorkoutPlanCreate
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class WorkoutGeneratorService:
    """Business logic for AI Workout Plan Generator."""

    @classmethod
    def generate_workout_plan(
        cls,
        db: Session,
        user: User,
        data: WorkoutPlanCreate,
    ) -> WorkoutPlan:
        """
        Generate and persist a new tailored AI Workout Plan for the user.
        Deactivates previous active plans.
        """
        # Call Gemini or periodized training logic
        plan_data = GeminiService.generate_workout_plan(
            level=data.fitness_level,
            goal=data.fitness_goal,
            days_per_week=data.days_per_week,
            equipment=data.equipment,
            focus_areas=data.focus_areas,
            injuries=data.injuries_or_limitations,
        )

        try:
            # Set older plans to inactive
            db.query(WorkoutPlan).filter(
                WorkoutPlan.user_id == user.id,
                WorkoutPlan.is_active == True,
            ).update({"is_active": False})

            record = WorkoutPlan(
                user_id=user.id,
                title=plan_data.get("title", f"{data.fitness_goal.title()} {data.days_per_week}-Day Program"),
                fitness_level=data.fitness_level,
                fitness_goal=data.fitness_goal,
                days_per_week=data.days_per_week,
                equipment=data.equipment,
                routines=json.dumps(plan_data.get("routines", [])),
                is_active=True,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.info("Workout plan created id=%s for user_id=%s", record.id, user.id)
            return record
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save workout plan for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate and save workout plan",
            ) from exc

    @staticmethod
    def get_active_workout_plan(db: Session, user: User) -> Optional[WorkoutPlan]:
        """Retrieve currently active workout plan for the user."""
        return (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.is_active == True)
            .order_by(WorkoutPlan.created_at.desc())
            .first()
        )

    @staticmethod
    def get_workout_plan_history(db: Session, user: User, limit: int = 10) -> List[WorkoutPlan]:
        """Retrieve past workout plans for the user."""
        return (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user.id)
            .order_by(WorkoutPlan.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def activate_workout_plan(db: Session, user: User, plan_id: int) -> WorkoutPlan:
        """Mark a specific historical routine as active and deactivate others."""
        plan = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
            .first()
        )
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout plan not found",
            )
        try:
            db.query(WorkoutPlan).filter(
                WorkoutPlan.user_id == user.id,
                WorkoutPlan.is_active == True,
            ).update({"is_active": False})
            plan.is_active = True
            db.commit()
            db.refresh(plan)
            return plan
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to activate workout plan %s for user %s", plan_id, user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not activate workout plan",
            ) from exc
