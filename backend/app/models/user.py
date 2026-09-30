"""
User SQLAlchemy model.
SQLAlchemy 2.0 style with full relationship declarations and indexes.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    bio = Column(String(500), nullable=True, default="")
    avatar = Column(String(500), nullable=True, default="")
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    # Relationships (cascade delete so child records are removed with user)
    bmi_records = relationship(
        "BMIRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    calorie_records = relationship(
        "CalorieRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    workout_records = relationship(
        "WorkoutRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    water_records = relationship(
        "WaterRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    step_records = relationship(
        "StepRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    diet_plans = relationship(
        "DietPlan", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    workout_plans = relationship(
        "WorkoutPlan", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    form_analyses = relationship(
        "FormAnalysisRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    health_insights = relationship(
        "HealthInsight", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    coach_conversations = relationship(
        "CoachConversation", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    wearable_devices = relationship(
        "WearableDevice", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    sleep_records = relationship(
        "SleepRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    heart_rate_records = relationship(
        "HeartRateRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    personal_records = relationship(
        "PersonalRecord", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    # Phase 8: AI Personal Trainer
    training_programs = relationship(
        "TrainingProgram", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    exercise_progressions = relationship(
        "ExerciseProgression", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    recovery_assessments = relationship(
        "RecoveryAssessment", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    weekly_reports = relationship(
        "WeeklyReport", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    goals = relationship(
        "GoalTracking", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    body_measurements = relationship(
        "BodyMeasurement", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    progress_photos = relationship(
        "ProgressPhoto", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    injury_assessments = relationship(
        "InjuryRiskAssessment", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    # Phase 9: AI Computer Vision Trainer 2.0
    trainer_sessions = relationship(
        "TrainerSession", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    pose_logs = relationship(
        "PoseAnalysisLog", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    adaptive_plans = relationship(
        "TrainerAdaptivePlan", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r}, username={self.username!r})>"
