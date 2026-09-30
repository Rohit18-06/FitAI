"""
Diet plan API routes.
POST /api/v1/diet/generate          – generate new AI diet plan
GET  /api/v1/diet/active            – retrieve active diet plan
GET  /api/v1/diet/history           – retrieve past diet plans
PUT  /api/v1/diet/{plan_id}/activate – activate a historical plan
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.diet_plan import DietPlanCreate, DietPlanResponse
from app.services.diet_service import DietService

router = APIRouter(prefix="/diet", tags=["AI Diet Planner"])


@router.post(
    "/generate",
    response_model=DietPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate and activate a new AI Diet Plan",
)
def generate_diet_plan(
    data: DietPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DietPlanResponse:
    """Generate a scientifically balanced meal plan using Gemini AI with fallback."""
    return DietService.create_diet_plan(db, current_user, data)


@router.get(
    "/active",
    response_model=Optional[DietPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve current active diet plan",
)
def get_active_diet_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[DietPlanResponse]:
    """Return the client's currently active meal plan."""
    return DietService.get_active_diet_plan(db, current_user)


@router.get(
    "/history",
    response_model=List[DietPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve diet plan history",
)
def get_diet_plan_history(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DietPlanResponse]:
    """Return past generated diet plans."""
    return DietService.get_diet_plan_history(db, current_user, limit=limit)


@router.put(
    "/{plan_id}/activate",
    response_model=DietPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate a specific historical diet plan",
)
def activate_diet_plan(
    plan_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DietPlanResponse:
    """Make an existing plan the active plan."""
    return DietService.activate_diet_plan(db, current_user, plan_id)
