"""
BMI service: calculation, categorisation, persistence, and history.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bmi import BMIRecord
from app.models.user import User
from app.schemas.bmi import BMICreate

logger = logging.getLogger(__name__)


class BMIService:
    """Business logic for BMI tracking."""

    # ------------------------------------------------------------------
    # Category thresholds (lower bound inclusive, upper bound exclusive)
    # ------------------------------------------------------------------
    _CATEGORIES: list[tuple[float, float, str]] = [
        (0.0,  18.5, "Underweight"),
        (18.5, 25.0, "Normal"),
        (25.0, 30.0, "Overweight"),
        (30.0, float("inf"), "Obese"),
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_bmi(height_cm: float, weight_kg: float) -> float:
        """
        Return the BMI value (rounded to 2 decimal places).

        Parameters
        ----------
        height_cm : Height in centimetres
        weight_kg : Weight in kilograms
        """
        if height_cm <= 0:
            raise ValueError("height_cm must be positive")
        height_m = height_cm / 100.0
        return round(weight_kg / (height_m ** 2), 2)

    @staticmethod
    def bmi_category(bmi: float) -> str:
        """
        Return the WHO BMI category string for a given *bmi* value.

        Categories
        ----------
        Underweight : < 18.5
        Normal      : 18.5 – 24.9
        Overweight  : 25.0 – 29.9
        Obese       : ≥ 30
        """
        for low, high, label in BMIService._CATEGORIES:
            if low <= bmi < high:
                return label
        return "Obese"  # fallback for bmi >= 30

    @staticmethod
    def save_bmi_record(db: Session, user: User, data: BMICreate) -> BMIRecord:
        """
        Calculate BMI from *data*, persist the record, and return it.

        Raises
        ------
        HTTPException 500
            If the database write fails.
        """
        bmi_value = BMIService.calculate_bmi(data.height_cm, data.weight_kg)
        category = BMIService.bmi_category(bmi_value)

        record = BMIRecord(
            user_id=user.id,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            bmi=bmi_value,
            category=category,
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save BMI record for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save BMI record",
            ) from exc

        logger.info(
            "BMI record saved: user_id=%s bmi=%.2f category=%s",
            user.id, bmi_value, category,
        )
        return record

    @staticmethod
    def get_bmi_history(
        db: Session,
        user: User,
        limit: int = 50,
    ) -> List[BMIRecord]:
        """
        Return up to *limit* BMI records for *user*, newest first.
        """
        return (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.desc())
            .limit(limit)
            .all()
        )
