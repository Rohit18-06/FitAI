"""
Notification SQLAlchemy model.
Supports hydration reminders, workout reminders, sleep reminders, and recovery alerts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Notification(Base):
    """Stores proactive clinical & athletic notifications for users."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # hydration_reminder, workout_reminder, sleep_reminder, recovery_alert
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="medium", nullable=False)  # high, medium, low
    action_url = Column(String(100), nullable=True)  # e.g. "#/water", "#/recovery", "#/workouts"
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notification_user_read", "user_id", "is_read"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type!r}, read={self.is_read})>"
