"""
Video analyzer service for exercise movement critique.
Orchestrates Gemini multimodal video inspection and biomechanical screens.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.form_analysis import FormAnalysisRecord
from app.models.user import User
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class VideoAnalyzerService:
    """Business logic for Gemini Exercise Form Analyzer."""

    @classmethod
    def analyze_exercise_video(
        cls,
        db: Session,
        user: User,
        exercise_name: str,
        video_bytes: bytes,
        filename: str,
    ) -> FormAnalysisRecord:
        """
        Analyze uploaded video or frame sequence and persist evaluation.
        """
        if not exercise_name or not exercise_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exercise name is required for form analysis.",
            )

        # Call Gemini or Biomechanical engine
        analysis = GeminiService.analyze_exercise_video(
            exercise_name=exercise_name.strip(),
            video_bytes=video_bytes,
            filename=filename,
        )

        try:
            record = FormAnalysisRecord(
                user_id=user.id,
                exercise_name=exercise_name.strip().title(),
                video_filename=filename,
                form_score=float(analysis.get("form_score", 85.0)),
                rep_count=int(analysis.get("rep_count", 0)),
                posture_summary=analysis.get("posture_summary", "Exercise form evaluated"),
                detailed_feedback=json.dumps(analysis.get("keypoint_checks", [])),
                injury_risk_level=analysis.get("injury_risk_level", "low"),
                recommendations=json.dumps(analysis.get("recommendations", [])),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.info("Form analysis recorded id=%s for user_id=%s, exercise=%s", record.id, user.id, exercise_name)
            return record
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save form analysis for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save form analysis result",
            ) from exc

    @staticmethod
    def get_analysis_history(
        db: Session,
        user: User,
        limit: int = 20,
    ) -> List[FormAnalysisRecord]:
        """Retrieve historical exercise form evaluations for the user."""
        return (
            db.query(FormAnalysisRecord)
            .filter(FormAnalysisRecord.user_id == user.id)
            .order_by(FormAnalysisRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_analysis_by_id(
        db: Session,
        user: User,
        analysis_id: int,
    ) -> FormAnalysisRecord:
        """Retrieve single form analysis record."""
        record = (
            db.query(FormAnalysisRecord)
            .filter(FormAnalysisRecord.id == analysis_id, FormAnalysisRecord.user_id == user.id)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form analysis record not found",
            )
        return record
