"""
Health insights API routes.
POST /api/v1/insights/generate     – trigger health insight analysis
GET  /api/v1/insights              – retrieve user's insights
PUT  /api/v1/insights/{id}/read    – mark insight as read
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.health_insight import HealthInsightResponse
from app.services.health_insight_service import HealthInsightService

router = APIRouter(prefix="/insights", tags=["Health Insights"])


@router.post(
    "/generate",
    response_model=List[HealthInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate fresh AI health insights from latest telemetry",
)
def generate_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[HealthInsightResponse]:
    """Analyze current telemetry and generate actionable coaching insights."""
    return HealthInsightService.generate_insights_for_user(db, current_user)


@router.get(
    "",
    response_model=List[HealthInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve user health insights",
)
def get_insights(
    unread_only: bool = Query(default=False, description="Filter only unread insights"),
    limit: int = Query(default=15, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[HealthInsightResponse]:
    """Retrieve coaching insights."""
    return HealthInsightService.get_user_insights(
        db, current_user, limit=limit, unread_only=unread_only
    )


@router.put(
    "/{insight_id}/read",
    response_model=HealthInsightResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark health insight as read",
)
def mark_insight_read(
    insight_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HealthInsightResponse:
    """Acknowledge or mark insight as read."""
    return HealthInsightService.mark_insight_as_read(db, current_user, insight_id)
