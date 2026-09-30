"""
Step counter service.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.step import StepRecord
from app.schemas.step import StepCreate

logger = logging.getLogger(__name__)

_DAILY_STEP_GOAL: int = 10_000  # common health recommendation


def _today_range() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


class StepService:
    """Business logic for step counter tracking."""

    @staticmethod
    def add_steps(
        db: Session,
        user: User,
        data: StepCreate,
    ) -> StepRecord:
        """
        Persist a new step record and return it.

        Raises
        ------
        HTTPException 500
            On database failure.
        """
        record = StepRecord(
            user_id=user.id,
            steps=data.steps,
            distance_km=data.distance_km,
            calories_burned=data.calories_burned,
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save step record for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save step record",
            ) from exc

        logger.info(
            "Step record saved: user_id=%s steps=%d distance=%.2fkm",
            user.id, data.steps, data.distance_km,
        )
        return record

    @staticmethod
    def get_today_steps(db: Session, user: User) -> dict:
        """
        Return today's aggregated step data.

        Returns
        -------
        dict with keys: total_steps, total_distance_km, total_calories_burned,
                        goal_steps, progress_pct, records
        """
        start, end = _today_range()
        records: List[StepRecord] = (
            db.query(StepRecord)
            .filter(
                StepRecord.user_id == user.id,
                StepRecord.created_at >= start,
                StepRecord.created_at < end,
            )
            .order_by(StepRecord.created_at.desc())
            .all()
        )

        total_steps = sum(r.steps for r in records)
        total_distance = round(sum(r.distance_km for r in records), 3)
        total_calories = round(sum(r.calories_burned for r in records), 2)
        progress_pct = round((total_steps / _DAILY_STEP_GOAL) * 100, 1)

        return {
            "total_steps": total_steps,
            "total_distance_km": total_distance,
            "total_calories_burned": total_calories,
            "goal_steps": _DAILY_STEP_GOAL,
            "progress_pct": min(progress_pct, 100.0),
            "records": records,
        }

    @staticmethod
    def get_step_history(
        db: Session,
        user: User,
        limit: int = 50,
    ) -> List[StepRecord]:
        """
        Return up to *limit* step records for *user*, newest first.
        """
        return (
            db.query(StepRecord)
            .filter(StepRecord.user_id == user.id)
            .order_by(StepRecord.created_at.desc())
            .limit(limit)
            .all()
        )
