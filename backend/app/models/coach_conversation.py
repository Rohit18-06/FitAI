"""
Coach conversation SQLAlchemy model.
Stores user prompts, AI coach responses, and token/source telemetry.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CoachConversation(Base):
    """Stores interactions with the personalized AI Fitness Coach."""

    __tablename__ = "coach_conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sources = Column(String(255), default="user_profile", nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="coach_conversations")

    __table_args__ = (
        Index("ix_coach_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CoachConversation(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"
