"""
Workout record SQLAlchemy model.
SQLAlchemy 2.0 style.
"""

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WorkoutRecord(Base):
    """Stores individual workout sessions for a user."""

    __tablename__ = "workout_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workout_type = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationship back to user
    user = relationship("User", back_populates="workout_records")

    def __repr__(self) -> str:
        return (
            f"<WorkoutRecord(id={self.id}, user_id={self.user_id}, "
            f"type={self.workout_type!r}, duration={self.duration_minutes}min)>"
        )
