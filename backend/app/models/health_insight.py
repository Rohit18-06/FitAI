"""
Health insight SQLAlchemy model.
Stores synthesized AI coach insights, correlations, and tips.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class HealthInsight(Base):
    """Personalized health and performance insight generated for a user."""

    __tablename__ = "health_insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False)  # nutrition, workout, hydration, recovery, general
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")  # high, medium, low
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="health_insights")

    def __repr__(self) -> str:
        return (
            f"<HealthInsight(id={self.id}, user_id={self.user_id}, "
            f"category={self.category!r}, priority={self.priority!r})>"
        )
