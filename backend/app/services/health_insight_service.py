"""
Health insights service.
Synthesizes user metrics across all modules into AI health insights.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bmi import BMIRecord
from app.models.calorie import CalorieRecord
from app.models.health_insight import HealthInsight
from app.models.step import StepRecord
from app.models.user import User
from app.models.water import WaterRecord
from app.models.workout import WorkoutRecord
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


def _today_range() -> tuple[datetime, datetime]:
    """Return start of today and start of tomorrow in UTC."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


class HealthInsightService:
    """Business logic for AI Health Insights and Correlations."""

    @classmethod
    def generate_insights_for_user(
        cls,
        db: Session,
        user: User,
    ) -> List[HealthInsight]:
        """
        Gathers latest telemetry, queries Gemini/heuristic engine, and persists new insights.
        """
        start, end = _today_range()

        # Telemetry aggregation
        cal_records = (
            db.query(CalorieRecord)
            .filter(CalorieRecord.user_id == user.id, CalorieRecord.created_at >= start, CalorieRecord.created_at < end)
            .all()
        )
        total_cals = sum(r.calories for r in cal_records)

        water_records = (
            db.query(WaterRecord)
            .filter(WaterRecord.user_id == user.id, WaterRecord.created_at >= start, WaterRecord.created_at < end)
            .all()
        )
        total_water = sum(r.liters for r in water_records)

        step_records = (
            db.query(StepRecord)
            .filter(StepRecord.user_id == user.id, StepRecord.created_at >= start, StepRecord.created_at < end)
            .all()
        )
        total_steps = sum(r.steps for r in step_records)

        wo_records = (
            db.query(WorkoutRecord)
            .filter(WorkoutRecord.user_id == user.id, WorkoutRecord.created_at >= start, WorkoutRecord.created_at < end)
            .all()
        )
        total_wo_min = sum(r.duration_minutes for r in wo_records)
        total_burned = sum(r.calories_burned for r in wo_records)

        latest_bmi = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.desc())
            .first()
        )

        telemetry = {
            "today": {
                "calories_consumed": total_cals,
                "calories_target": 2200.0,
                "water_liters": round(total_water, 2),
                "steps_count": total_steps,
                "workout_minutes": total_wo_min,
                "calories_burned": total_burned,
            },
            "bmi": {
                "value": latest_bmi.bmi if latest_bmi else None,
                "category": latest_bmi.category if latest_bmi else None,
                "weight_kg": latest_bmi.weight_kg if latest_bmi else None,
            }
        }

        raw_insights = GeminiService.generate_health_insights(telemetry)
        created_records = []

        try:
            for item in raw_insights:
                title = item.get("title", "Health Observation")
                # Avoid inserting duplicate insight on the same day
                existing = (
                    db.query(HealthInsight)
                    .filter(
                        HealthInsight.user_id == user.id,
                        HealthInsight.title == title,
                        HealthInsight.created_at >= start,
                    )
                    .first()
                )
                if not existing:
                    rec = HealthInsight(
                        user_id=user.id,
                        category=item.get("category", "general"),
                        title=title,
                        content=item.get("content", ""),
                        priority=item.get("priority", "medium"),
                        is_read=False,
                    )
                    db.add(rec)
                    created_records.append(rec)

            db.commit()
            for r in created_records:
                db.refresh(r)

            logger.info("Generated %d new health insights for user_id=%s", len(created_records), user.id)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to store generated insights for user_id=%s", user.id)

        # Return latest active insights
        return (
            db.query(HealthInsight)
            .filter(HealthInsight.user_id == user.id)
            .order_by(HealthInsight.created_at.desc())
            .limit(10)
            .all()
        )

    @staticmethod
    def get_user_insights(
        db: Session,
        user: User,
        limit: int = 15,
        unread_only: bool = False,
    ) -> List[HealthInsight]:
        """Retrieve user insights with optional filtering."""
        query = db.query(HealthInsight).filter(HealthInsight.user_id == user.id)
        if unread_only:
            query = query.filter(HealthInsight.is_read == False)
        return query.order_by(HealthInsight.created_at.desc()).limit(limit).all()

    @staticmethod
    def mark_insight_as_read(
        db: Session,
        user: User,
        insight_id: int,
    ) -> HealthInsight:
        """Mark insight as read."""
        insight = (
            db.query(HealthInsight)
            .filter(HealthInsight.id == insight_id, HealthInsight.user_id == user.id)
            .first()
        )
        if not insight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health insight not found",
            )
        try:
            insight.is_read = True
            db.commit()
            db.refresh(insight)
            return insight
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to mark insight %s read", insight_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not update insight status",
            ) from exc
