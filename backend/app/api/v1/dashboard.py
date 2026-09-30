"""
Dashboard API routes.
GET /api/v1/dashboard – aggregate overview of metrics, targets, streaks, and adherence
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get(
    "",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated dashboard overview",
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardOverviewResponse:
    """
    Produce real-time aggregated overview combining:
    - Today's consumed vs target metrics
    - BMI and weight tracking
    - 7-day adherence score
    - Activity streaks
    - Active diet & workout plans
    - Recent AI insights
    """
    return DashboardService.get_dashboard_overview(db, current_user)
