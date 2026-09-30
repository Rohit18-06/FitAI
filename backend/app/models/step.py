"""
Step count record SQLAlchemy model.
SQLAlchemy 2.0 style.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class StepRecord(Base):
    """Stores daily step count entries for a user."""

    __tablename__ = "step_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    steps = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=False, default=0.0)
    calories_burned = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationship back to user
    user = relationship("User", back_populates="step_records")

    def __repr__(self) -> str:
        return (
            f"<StepRecord(id={self.id}, user_id={self.user_id}, "
            f"steps={self.steps}, distance_km={self.distance_km})>"
        )
