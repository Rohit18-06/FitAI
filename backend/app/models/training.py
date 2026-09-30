"""
Phase 8: AI Personal Trainer models.
Training Programs, Recovery, Goals, Measurements, Progress Photos,
Weekly Reports, Injury Risk, and Exercise Progression.
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


# ── Training Program ─────────────────────────────────────────
class TrainingProgram(Base):
    """AI-generated multi-week training program."""
    __tablename__ = "training_programs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    fitness_goal = Column(String(100), nullable=False, default="general_fitness")
    fitness_level = Column(String(50), nullable=False, default="intermediate")
    duration_weeks = Column(Integer, nullable=False, default=4)
    days_per_week = Column(Integer, nullable=False, default=4)
    is_active = Column(Boolean, default=True, nullable=False)
    ai_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User", back_populates="training_programs")
    weeks = relationship("ProgramWeek", back_populates="program", cascade="all, delete-orphan", lazy="select")

    __table_args__ = (Index("ix_training_user_active", "user_id", "is_active"),)


class ProgramWeek(Base):
    """One week within a training program."""
    __tablename__ = "program_weeks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    theme = Column(String(100), nullable=True)  # e.g. "Hypertrophy", "Deload"
    intensity_pct = Column(Float, nullable=False, default=70.0)  # % of 1RM / max effort
    volume_modifier = Column(Float, nullable=False, default=1.0)  # multiplier
    notes = Column(Text, nullable=True)

    program = relationship("TrainingProgram", back_populates="weeks")
    days = relationship("ProgramDay", back_populates="week", cascade="all, delete-orphan", lazy="select")


class ProgramDay(Base):
    """Single training day within a week."""
    __tablename__ = "program_days"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    week_id = Column(Integer, ForeignKey("program_weeks.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    day_name = Column(String(50), nullable=False, default="Day 1")
    focus = Column(String(100), nullable=False, default="Full Body")
    exercises_json = Column(JSON, nullable=False, default=list)  # [{name, sets, reps, rest_s, notes}]
    warmup_json = Column(JSON, nullable=True, default=list)
    cooldown_json = Column(JSON, nullable=True, default=list)
    estimated_duration_min = Column(Integer, nullable=False, default=45)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    week = relationship("ProgramWeek", back_populates="days")


# ── Exercise Progression ──────────────────────────────────────
class ExerciseProgression(Base):
    """Tracks progressive overload for individual exercises."""
    __tablename__ = "exercise_progressions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_name = Column(String(150), nullable=False)
    weight_kg = Column(Float, nullable=True)
    sets = Column(Integer, nullable=False, default=3)
    reps = Column(Integer, nullable=False, default=10)
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion 1-10
    one_rep_max_est = Column(Float, nullable=True)  # Estimated 1RM
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="exercise_progressions")

    __table_args__ = (Index("ix_progression_user_exercise", "user_id", "exercise_name"),)


# ── Recovery Assessment ───────────────────────────────────────
class RecoveryAssessment(Base):
    """AI-computed daily recovery assessment."""
    __tablename__ = "recovery_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False, default=75)  # 0-100
    status = Column(String(50), nullable=False, default="Good")  # Optimal/Good/Moderate/Fatigued/Overtrained
    sleep_score = Column(Integer, nullable=True)
    hrv_score = Column(Integer, nullable=True)
    resting_hr_score = Column(Integer, nullable=True)
    workout_load_score = Column(Integer, nullable=True)
    recommendation = Column(Text, nullable=True)
    components_json = Column(JSON, nullable=True, default=dict)
    computed_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="recovery_assessments")

    __table_args__ = (Index("ix_recovery_user_date", "user_id", "computed_at"),)

    @property
    def components(self) -> dict:
        return self.components_json or {}


# ── Weekly Report ─────────────────────────────────────────────
class WeeklyReport(Base):
    """AI-generated weekly coaching report."""
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    training_summary = Column(Text, nullable=True)
    recovery_summary = Column(Text, nullable=True)
    nutrition_summary = Column(Text, nullable=True)
    sleep_summary = Column(Text, nullable=True)
    progress_score = Column(Integer, nullable=False, default=50)  # 0-100
    highlights = Column(JSON, nullable=True, default=list)
    recommendations = Column(JSON, nullable=True, default=list)
    ai_coach_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="weekly_reports")


# ── Goal Tracking ─────────────────────────────────────────────
class GoalTracking(Base):
    """User fitness goals with AI-tracked progress."""
    __tablename__ = "goal_tracking"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_type = Column(String(100), nullable=False)  # lose_weight, gain_muscle, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=True)
    start_value = Column(Float, nullable=True)
    completion_pct = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="active")  # active/completed/paused/cancelled
    target_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    milestones_json = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    user = relationship("User", back_populates="goals")

    __table_args__ = (Index("ix_goal_user_status", "user_id", "status"),)

    @property
    def milestones(self) -> list:
        return self.milestones_json or []


# ── Body Measurement ─────────────────────────────────────────
class BodyMeasurement(Base):
    """Body measurement snapshots for progress tracking."""
    __tablename__ = "body_measurements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=True)
    body_fat_pct = Column(Float, nullable=True)
    chest_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hips_cm = Column(Float, nullable=True)
    neck_cm = Column(Float, nullable=True)
    left_arm_cm = Column(Float, nullable=True)
    right_arm_cm = Column(Float, nullable=True)
    left_thigh_cm = Column(Float, nullable=True)
    right_thigh_cm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    measured_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="body_measurements")

    __table_args__ = (Index("ix_measurement_user_date", "user_id", "measured_at"),)


# ── Progress Photo ────────────────────────────────────────────
class ProgressPhoto(Base):
    """Progress photos with AI physique analysis."""
    __tablename__ = "progress_photos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    photo_type = Column(String(50), nullable=False, default="front")  # front/side/back
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    ai_analysis = Column(Text, nullable=True)
    body_fat_estimate = Column(Float, nullable=True)
    muscle_score = Column(Integer, nullable=True)  # 0-100
    notes = Column(Text, nullable=True)
    taken_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="progress_photos")


# ── Injury Risk Assessment ────────────────────────────────────
class InjuryRiskAssessment(Base):
    """AI-generated injury risk analysis."""
    __tablename__ = "injury_risk_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_level = Column(String(50), nullable=False, default="Low")  # Low/Moderate/High
    risk_score = Column(Integer, nullable=False, default=20)  # 0-100
    factors_json = Column(JSON, nullable=True, default=list)
    corrective_actions = Column(JSON, nullable=True, default=list)
    mobility_notes = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    assessed_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="injury_assessments")

    __table_args__ = (Index("ix_injury_user_date", "user_id", "assessed_at"),)

    @property
    def factors(self) -> list:
        return self.factors_json or []
