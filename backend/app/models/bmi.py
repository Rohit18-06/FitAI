"""
BMI record SQLAlchemy model.
SQLAlchemy 2.0 style.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BMIRecord(Base):
    """Stores every BMI measurement taken by a user."""

    __tablename__ = "bmi_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    # "Underweight" | "Normal" | "Overweight" | "Obese"
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationship back to user
    user = relationship("User", back_populates="bmi_records")

    def __repr__(self) -> str:
        return (
            f"<BMIRecord(id={self.id}, user_id={self.user_id}, "
            f"bmi={self.bmi}, category={self.category!r})>"
        )
