"""
Personal Record SQLAlchemy model.
Tracks peak athletic achievements: Longest Run, Fastest 5K, Most Steps, Most Calories, Longest Workout.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PersonalRecord(Base):
    """Stores peak athletic milestones and lifetime personal records."""

    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    record_type = Column(String(50), nullable=False)  # longest_run, fastest_5k, most_steps, most_calories, longest_workout, heaviest_lift
    record_name = Column(String(100), nullable=False)  # Display title e.g. "Longest Run", "Most Steps in a Day"
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # "km", "min", "steps", "kcal", "kg"
    notes = Column(Text, nullable=True)
    achieved_at = Column(DateTime, default=_utcnow, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="personal_records")

    __table_args__ = (
        Index("ix_pr_user_type", "user_id", "record_type"),
    )

    def __repr__(self) -> str:
        return f"<PersonalRecord(id={self.id}, user_id={self.user_id}, type={self.record_type!r}, value={self.value} {self.unit})>"
