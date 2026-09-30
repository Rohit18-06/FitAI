"""
Phase 9: AI Personal Trainer & Computer Vision Coaching 2.0 Models.
Tracks real-time trainer sessions, pose analysis frames, movement library items,
and adaptive training recommendations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String,
    Text, Boolean, JSON, Index,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TrainerSession(Base):
    """Real-time AI workout session with live computer vision tracking."""
    __tablename__ = "trainer_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_name = Column(String(100), nullable=False, default="Squat")
    target_reps = Column(Integer, nullable=False, default=10)
    target_sets = Column(Integer, nullable=False, default=3)
    completed_reps = Column(Integer, nullable=False, default=0)
    completed_sets = Column(Integer, nullable=False, default=0)
    avg_form_score = Column(Float, nullable=False, default=100.0)
    avg_tempo = Column(Float, nullable=True)  # seconds per rep
    injury_risk_level = Column(String(50), nullable=False, default="LOW")
    status = Column(String(50), nullable=False, default="in_progress")  # in_progress, completed, paused
    feedback_history = Column(JSON, nullable=True, default=list)  # list of coaching prompts given
    started_at = Column(DateTime, default=_utcnow, nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="trainer_sessions")
    pose_logs = relationship("PoseAnalysisLog", back_populates="session", cascade="all, delete-orphan", lazy="select")

    __table_args__ = (Index("ix_trainer_user_status", "user_id", "status"),)


class PoseAnalysisLog(Base):
    """Detailed biometric frame-by-frame pose analysis log."""
    __tablename__ = "pose_analysis_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("trainer_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False, default=0.95)
    posture_score = Column(Float, nullable=False, default=100.0)
    rep_number = Column(Integer, nullable=False, default=0)
    stage = Column(String(50), nullable=True)  # start, inflection, lockout, eccentric, concentric
    joint_angles_json = Column(JSON, nullable=True, default=dict)
    mistakes_json = Column(JSON, nullable=True, default=list)
    corrections_json = Column(JSON, nullable=True, default=list)
    injury_risk = Column(String(50), nullable=False, default="LOW")
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    session = relationship("TrainerSession", back_populates="pose_logs")
    user = relationship("User", back_populates="pose_logs")

    @property
    def joint_angles(self) -> dict:
        return self.joint_angles_json or {}

    @property
    def mistakes(self) -> list:
        return self.mistakes_json or []

    @property
    def corrections(self) -> list:
        return self.corrections_json or []


class MovementLibraryItem(Base):
    """Exercise Movement Library with 100+ exercises, biomechanical coaching cues, and mistakes."""
    __tablename__ = "movement_library"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True, index=True)
    slug = Column(String(150), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # Strength, Cardio, Mobility, Calisthenics
    equipment = Column(String(100), nullable=False, default="Bodyweight")  # Bodyweight, Barbell, Dumbbell, etc.
    difficulty = Column(String(50), nullable=False, default="Intermediate")  # Beginner, Intermediate, Advanced
    primary_muscles = Column(JSON, nullable=False, default=list)
    secondary_muscles = Column(JSON, nullable=False, default=list)
    instructions = Column(JSON, nullable=False, default=list)  # step-by-step instructions
    common_mistakes = Column(JSON, nullable=False, default=list)
    coaching_cues = Column(JSON, nullable=False, default=list)
    demo_video_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)


class TrainerAdaptivePlan(Base):
    """AI adaptive training adjustments based on readiness, fatigue, and live performance."""
    __tablename__ = "trainer_adaptive_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recovery_score = Column(Integer, nullable=False, default=75)
    sleep_hours = Column(Float, nullable=True)
    hrv_ms = Column(Float, nullable=True)
    soreness_level = Column(String(50), nullable=True)
    adjustment_type = Column(String(50), nullable=False, default="maintain")  # increase_volume, decrease_volume, deload, maintain
    volume_multiplier = Column(Float, nullable=False, default=1.0)
    recommended_reps_delta = Column(Integer, nullable=False, default=0)
    deload_recommended = Column(Boolean, nullable=False, default=False)
    recommendations = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="adaptive_plans")
