"""
Water intake tracking service.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.water import WaterRecord
from app.schemas.water import WaterCreate

logger = logging.getLogger(__name__)

_DAILY_GOAL_LITERS: float = 2.0  # WHO recommendation default


def _today_range() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


class WaterService:
    """Business logic for water intake tracking."""

    @staticmethod
    def add_water_intake(
        db: Session,
        user: User,
        data: WaterCreate,
    ) -> WaterRecord:
        """
        Persist a new water intake record and return it.

        Raises
        ------
        HTTPException 500
            On database failure.
        """
        record = WaterRecord(
            user_id=user.id,
            glasses=data.glasses,
            liters=data.liters,
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save water record for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save water record",
            ) from exc

        logger.info(
            "Water record saved: user_id=%s glasses=%d liters=%.3f",
            user.id, data.glasses, data.liters,
        )
        return record

    @staticmethod
    def get_today_water(db: Session, user: User) -> dict:
        """
        Return today's aggregated water intake.

        Returns
        -------
        dict with keys: total_glasses, total_liters, goal_liters, progress_pct, records
        """
        start, end = _today_range()
        records: List[WaterRecord] = (
            db.query(WaterRecord)
            .filter(
                WaterRecord.user_id == user.id,
                WaterRecord.created_at >= start,
                WaterRecord.created_at < end,
            )
            .order_by(WaterRecord.created_at.desc())
            .all()
        )

        total_liters = round(sum(r.liters for r in records), 3)
        total_glasses = sum(r.glasses for r in records)
        progress_pct = round((total_liters / _DAILY_GOAL_LITERS) * 100, 1)

        return {
            "total_glasses": total_glasses,
            "total_liters": total_liters,
            "goal_liters": _DAILY_GOAL_LITERS,
            "progress_pct": min(progress_pct, 100.0),
            "records": records,
        }

    @staticmethod
    def get_water_history(
        db: Session,
        user: User,
        limit: int = 50,
    ) -> List[WaterRecord]:
        """
        Return up to *limit* water records for *user*, newest first.
        """
        return (
            db.query(WaterRecord)
            .filter(WaterRecord.user_id == user.id)
            .order_by(WaterRecord.created_at.desc())
            .limit(limit)
            .all()
        )
