"""
Workout tracking service.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout import WorkoutRecord
from app.schemas.workout import WorkoutCreate

logger = logging.getLogger(__name__)


def _today_range() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


class WorkoutService:
    """Business logic for workout tracking."""

    @staticmethod
    def add_workout(
        db: Session,
        user: User,
        data: WorkoutCreate,
    ) -> WorkoutRecord:
        """
        Persist a new workout record and return it.

        Raises
        ------
        HTTPException 500
            On database failure.
        """
        record = WorkoutRecord(
            user_id=user.id,
            workout_type=data.workout_type,
            duration_minutes=data.duration_minutes,
            calories_burned=data.calories_burned,
            notes=data.notes,
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save workout for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save workout record",
            ) from exc

        logger.info(
            "Workout saved: user_id=%s type=%s duration=%dmin",
            user.id, data.workout_type, data.duration_minutes,
        )
        return record

    @staticmethod
    def get_workout_history(
        db: Session,
        user: User,
        limit: int = 50,
    ) -> List[WorkoutRecord]:
        """
        Return up to *limit* workout records for *user*, newest first.
        """
        return (
            db.query(WorkoutRecord)
            .filter(WorkoutRecord.user_id == user.id)
            .order_by(WorkoutRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_total_workout_minutes(db: Session, user: User) -> int:
        """
        Return the total number of workout minutes logged by *user* today.
        """
        start, end = _today_range()
        records = (
            db.query(WorkoutRecord)
            .filter(
                WorkoutRecord.user_id == user.id,
                WorkoutRecord.created_at >= start,
                WorkoutRecord.created_at < end,
            )
            .all()
        )
        return sum(r.duration_minutes for r in records)
