"""
Sleep record SQLAlchemy model.
Stores circadian telemetry, sleep architecture stages, and sleep quality scores.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SleepRecord(Base):
    """Stores daily sleep architecture and sleep scoring metrics."""

    __tablename__ = "sleep_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    duration_hours = Column(Float, nullable=False)  # Total sleep time in hours
    deep_sleep_hours = Column(Float, nullable=False, default=0.0)  # Stage 3/4 Slow-Wave Sleep
    rem_sleep_hours = Column(Float, nullable=False, default=0.0)  # Rapid Eye Movement
    light_sleep_hours = Column(Float, nullable=False, default=0.0)
    sleep_score = Column(Integer, nullable=False, default=80)  # 0 to 100 quality score
    bed_time = Column(DateTime, nullable=False)
    wake_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="sleep_records")

    __table_args__ = (
        Index("ix_sleep_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SleepRecord(id={self.id}, user_id={self.user_id}, duration={self.duration_hours}h, score={self.sleep_score})>"
