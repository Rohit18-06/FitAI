"""
Heart Rate record SQLAlchemy model.
Stores resting heart rate, workout zones, HRV, and cardiovascular metrics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class HeartRateRecord(Base):
    """Stores cardiovascular telemetry, resting HR, and zone metrics."""

    __tablename__ = "heart_rate_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    current_hr = Column(Integer, nullable=False, default=70)  # BPM
    average_hr = Column(Float, nullable=False, default=72.0)  # BPM
    resting_hr = Column(Integer, nullable=False, default=60)  # BPM
    max_hr = Column(Integer, nullable=False, default=180)  # BPM
    hrv_rmssd = Column(Float, nullable=True, default=55.0)  # Heart Rate Variability in ms
    vo2_max = Column(Float, nullable=True)  # mL/kg/min
    # Heart Rate Zones (Minutes spent in each zone)
    hr_zone_1_mins = Column(Integer, default=0, nullable=False)  # Zone 1 (<60% HRmax - Recovery)
    hr_zone_2_mins = Column(Integer, default=0, nullable=False)  # Zone 2 (60-70% - Endurance/Fat Burn)
    hr_zone_3_mins = Column(Integer, default=0, nullable=False)  # Zone 3 (70-80% - Aerobic)
    hr_zone_4_mins = Column(Integer, default=0, nullable=False)  # Zone 4 (80-90% - Anaerobic Threshold)
    hr_zone_5_mins = Column(Integer, default=0, nullable=False)  # Zone 5 (>90% - Maximum Effort)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="heart_rate_records")

    __table_args__ = (
        Index("ix_hr_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<HeartRateRecord(id={self.id}, user_id={self.user_id}, resting={self.resting_hr}bpm, avg={self.average_hr}bpm)>"
