"""
Analytics and progress tracking routes.
GET /api/v1/analytics/overview   – multi-day trends, averages, weight progression
GET /api/v1/analytics/milestones – athletic and consistency achievement badges
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsOverviewResponse, MilestonesResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Progress Tracking"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get multi-day trend analytics and progress deltas",
)
def get_analytics_overview(
    days: int = Query(default=30, ge=7, le=365, description="Number of days to analyze (7–365)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalyticsOverviewResponse:
    """Retrieve daily time-series telemetry, averages, and weight/BMI progress."""
    return AnalyticsService.get_analytics_overview(db, current_user, days=days)


@router.get(
    "/milestones",
    response_model=MilestonesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user achievement milestones and badges",
)
def get_milestones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MilestonesResponse:
    """Evaluate and retrieve athletic badges and consistency milestones."""
    return AnalyticsService.get_user_milestones(db, current_user)
