"""
AI Fitness Coach API routes.
POST   /api/v1/coach/chat     – Chat with personalized AI fitness coach
GET    /api/v1/coach/history  – Retrieve historical coaching conversations
DELETE /api/v1/coach/history  – Clear conversation history
GET    /api/v1/coach/stats    – Retrieve today's telemetry stats for the coach sidebar
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.coach import (
    CoachChatRequest,
    CoachChatResponse,
    ConversationHistoryResponse,
    CoachSidebarStats,
)
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["AI Fitness Coach"])


@router.post(
    "/chat",
    response_model=CoachChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the AI Fitness Coach a question",
)
def coach_chat(
    data: CoachChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CoachChatResponse:
    """
    Submits a user query to the AI Fitness Coach.
    The coach ingests the user's complete physiological records (BMI, calories,
    workouts, water, steps, active plans, video biomechanics, and clinical insights)
    to synthesize a personalized, actionable critique.
    """
    return CoachService.process_chat_message(
        db=db, user=current_user, message=data.message.strip()
    )


@router.get(
    "/history",
    response_model=ConversationHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve coach conversation history",
)
def get_coach_history(
    limit: int = Query(default=30, ge=1, le=100, description="Max messages to fetch"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationHistoryResponse:
    """Fetches user conversation history with the AI Fitness Coach."""
    return CoachService.get_conversation_history(
        db=db, user=current_user, limit=limit, offset=offset
    )


@router.delete(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Clear coach conversation history",
)
def clear_coach_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Permanently deletes conversation history for the authenticated user."""
    deleted_count = CoachService.clear_conversation_history(db=db, user=current_user)
    return {
        "message": "Conversation history cleared successfully",
        "deleted_count": deleted_count,
    }


@router.get(
    "/stats",
    response_model=CoachSidebarStats,
    status_code=status.HTTP_200_OK,
    summary="Get today's quick telemetry for coach sidebar",
)
def get_coach_sidebar_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CoachSidebarStats:
    """Returns today's biometric and compliance summary for the coach sidebar."""
    return CoachService.get_sidebar_stats(db=db, user=current_user)
