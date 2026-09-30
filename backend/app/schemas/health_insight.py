"""
Health insights schemas using Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class HealthInsightResponse(BaseModel):
    """Personalized insight produced by the AI Fitness Coach."""
    id: int
    user_id: int
    category: str = Field(..., description="nutrition, workout, hydration, recovery, general")
    title: str = Field(..., description="Insight headline")
    content: str = Field(..., description="Actionable observation and advice")
    priority: str = Field(default="medium", description="high, medium, or low")
    is_read: bool = Field(default=False)
    created_at: datetime

    model_config = {"from_attributes": True}
