"""
Water intake record SQLAlchemy model.
SQLAlchemy 2.0 style.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WaterRecord(Base):
    """Stores individual water intake entries for a user."""

    __tablename__ = "water_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    glasses = Column(Integer, nullable=False, default=0)    # number of glasses
    liters = Column(Float, nullable=False)                  # volume in litres
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationship back to user
    user = relationship("User", back_populates="water_records")

    def __repr__(self) -> str:
        return (
            f"<WaterRecord(id={self.id}, user_id={self.user_id}, "
            f"glasses={self.glasses}, liters={self.liters})>"
        )
