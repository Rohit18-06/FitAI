"""
Pydantic schemas for AI Fitness Coach interactions.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CoachChatRequest(BaseModel):
    """Payload for asking the AI Fitness Coach a question."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question or fitness prompt (e.g. 'Why am I not losing weight?')",
        examples=["Why am I not losing weight?"],
    )


class CoachChatResponse(BaseModel):
    """Structured response from the AI Fitness Coach."""
    id: int
    message: str
    response: str
    sources: List[str] = Field(
        default_factory=list,
        description="Telemetry sources referenced (e.g. ['bmi', 'calories', 'workouts'])",
    )
    tokens_used: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoachConversationItem(BaseModel):
    """Single historical conversation turn."""
    id: int
    user_id: int
    message: str
    response: str
    sources: List[str] = Field(default_factory=list)
    tokens_used: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationHistoryResponse(BaseModel):
    """Paginated conversation history list."""
    conversations: List[CoachConversationItem]
    total: int

    model_config = ConfigDict(from_attributes=True)


class CoachSidebarStats(BaseModel):
    """Today's biometric and compliance summary for the coach sidebar."""
    bmi: Optional[float] = None
    bmi_category: Optional[str] = None
    weight_kg: Optional[float] = None
    calories_today: float = 0.0
    calorie_target: float = 2400.0
    water_liters_today: float = 0.0
    water_target: float = 3.0
    steps_today: int = 0
    step_target: int = 10000
    workout_minutes_today: int = 0
    current_streak: int = 0
    active_diet_plan: Optional[str] = None
    active_workout_plan: Optional[str] = None
