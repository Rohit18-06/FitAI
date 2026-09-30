"""
Calorie record SQLAlchemy model.
SQLAlchemy 2.0 style with macronutrient columns.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CalorieRecord(Base):
    """Stores individual meal / food calorie entries for a user."""

    __tablename__ = "calorie_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    meal_name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False, default=0.0)   # grams
    carbs = Column(Float, nullable=False, default=0.0)     # grams
    fats = Column(Float, nullable=False, default=0.0)      # grams
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationship back to user
    user = relationship("User", back_populates="calorie_records")

    def __repr__(self) -> str:
        return (
            f"<CalorieRecord(id={self.id}, user_id={self.user_id}, "
            f"meal={self.meal_name!r}, calories={self.calories})>"
        )
