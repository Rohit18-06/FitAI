"""
Wearable Device SQLAlchemy model.
Supports Garmin, Fitbit, Samsung Health, Apple Watch, and Health Connect.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WearableDevice(Base):
    """User connected wearable devices and health provider integrations."""

    __tablename__ = "wearable_devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # health_connect, garmin, fitbit, apple_health, samsung_health
    device_name = Column(String(100), nullable=False)  # e.g. "Garmin Forerunner 965", "Apple Watch Ultra 2"
    device_identifier = Column(String(100), nullable=True)  # serial / UUID
    battery_level = Column(Integer, nullable=True, default=100)  # percentage 0-100
    is_connected = Column(Boolean, default=True, nullable=False)
    last_sync = Column(DateTime, default=_utcnow, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="wearable_devices")

    __table_args__ = (
        Index("ix_wearable_user_provider", "user_id", "provider"),
    )

    def __repr__(self) -> str:
        return f"<WearableDevice(id={self.id}, user_id={self.user_id}, provider={self.provider!r}, connected={self.is_connected})>"
