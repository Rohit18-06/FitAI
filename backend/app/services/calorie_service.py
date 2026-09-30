"""
Calorie tracking service.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.calorie import CalorieRecord
from app.models.user import User
from app.schemas.calorie import CalorieCreate

logger = logging.getLogger(__name__)


def _today_range() -> tuple[datetime, datetime]:
    """Return (start_of_today_utc, start_of_tomorrow_utc)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


class CalorieService:
    """Business logic for calorie tracking."""

    @staticmethod
    def add_calorie_record(
        db: Session,
        user: User,
        data: CalorieCreate,
    ) -> CalorieRecord:
        """
        Persist a new calorie entry and return it.

        Raises
        ------
        HTTPException 500
            On database failure.
        """
        record = CalorieRecord(
            user_id=user.id,
            meal_name=data.meal_name,
            calories=data.calories,
            protein=data.protein,
            carbs=data.carbs,
            fats=data.fats,
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save calorie record for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save calorie record",
            ) from exc

        logger.info(
            "Calorie record saved: user_id=%s meal=%s kcal=%.1f",
            user.id, data.meal_name, data.calories,
        )
        return record

    @staticmethod
    def get_daily_calories(db: Session, user: User) -> dict:
        """
        Return today's aggregate calorie and macro totals.

        Returns
        -------
        dict with keys: total_calories, total_protein, total_carbs, total_fats, records
        """
        start, end = _today_range()

        records: List[CalorieRecord] = (
            db.query(CalorieRecord)
            .filter(
                CalorieRecord.user_id == user.id,
                CalorieRecord.created_at >= start,
                CalorieRecord.created_at < end,
            )
            .order_by(CalorieRecord.created_at.desc())
            .all()
        )

        return {
            "total_calories": round(sum(r.calories for r in records), 2),
            "total_protein": round(sum(r.protein for r in records), 2),
            "total_carbs": round(sum(r.carbs for r in records), 2),
            "total_fats": round(sum(r.fats for r in records), 2),
            "records": records,
        }

    @staticmethod
    def get_calorie_history(
        db: Session,
        user: User,
        limit: int = 50,
    ) -> List[CalorieRecord]:
        """
        Return up to *limit* calorie records for *user*, newest first.
        """
        return (
            db.query(CalorieRecord)
            .filter(CalorieRecord.user_id == user.id)
            .order_by(CalorieRecord.created_at.desc())
            .limit(limit)
            .all()
        )
