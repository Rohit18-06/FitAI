"""
Calorie tracking routes.

POST /api/v1/calories          – log a calorie entry (protected)
GET  /api/v1/calories/history  – retrieve calorie history (protected)
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.calorie import CalorieCreate, CalorieResponse
from app.services.calorie_service import CalorieService

router = APIRouter(prefix="/calories", tags=["Calories"])


@router.post(
    "",
    response_model=CalorieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a calorie entry",
    responses={
        201: {"description": "Calorie entry saved"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def add_calorie(
    data: CalorieCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> CalorieResponse:
    """Log a meal or food item with its calorie and macro breakdown."""
    record = CalorieService.add_calorie_record(db, current_user, data)
    return CalorieResponse.model_validate(record)


@router.get(
    "/history",
    response_model=List[CalorieResponse],
    status_code=status.HTTP_200_OK,
    summary="Get calorie history",
    responses={
        200: {"description": "Calorie history returned"},
        401: {"description": "Unauthorized"},
    },
)
def get_calorie_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[CalorieResponse]:
    """Return the user's calorie records ordered newest-first."""
    records = CalorieService.get_calorie_history(db, current_user, limit=limit)
    return [CalorieResponse.model_validate(r) for r in records]
