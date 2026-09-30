"""
Exercise form analysis schemas using Pydantic v2.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class KeypointCheck(BaseModel):
    """Specific joint or posture assessment."""
    joint_or_segment: str = Field(..., description="Anatomical point e.g. 'Lumbar Spine' or 'Knees'")
    status: str = Field(..., description="optimal, acceptable, or needs_correction")
    metric_or_angle: Optional[str] = Field(default=None, description="Observation e.g. '88 degrees depth'")
    feedback: str = Field(..., description="Detailed observation for this point")


class FormAnalysisResponse(BaseModel):
    """Result of an exercise video or movement pattern evaluation."""
    id: int
    user_id: int
    exercise_name: str
    video_filename: Optional[str] = None
    form_score: float = Field(..., ge=0, le=100, description="Overall biomechanical score (0–100)")
    rep_count: int = Field(default=0, ge=0, description="Detected repetitions completed with valid range")
    posture_summary: str = Field(..., description="High-level feedback headline")
    keypoint_checks: List[KeypointCheck] = Field(default_factory=list, description="Breakdown per body region")
    injury_risk_level: str = Field(..., description="low, medium, or high")
    recommendations: List[str] = Field(default_factory=list, description="Actionable cues for improvement")
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("keypoint_checks", mode="before")
    @classmethod
    def parse_keypoints(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict) and "keypoint_checks" in parsed:
                    return parsed["keypoint_checks"]
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return []
        return v

    @field_validator("recommendations", mode="before")
    @classmethod
    def parse_recommendations(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                # If stored as plain string lines
                return [line.strip("- *") for line in v.split("\n") if line.strip()]
        return v
