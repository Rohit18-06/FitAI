"""
Step counter routes.

POST /api/v1/steps          – log a step count entry (protected)
GET  /api/v1/steps/history  – retrieve step history (protected)
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.step import StepCreate, StepResponse
from app.services.step_service import StepService

router = APIRouter(prefix="/steps", tags=["Steps"])


@router.post(
    "",
    response_model=StepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a step count entry",
    responses={
        201: {"description": "Steps logged"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def add_steps(
    data: StepCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> StepResponse:
    """Log a step count entry with optional distance and calories."""
    record = StepService.add_steps(db, current_user, data)
    return StepResponse.model_validate(record)


@router.get(
    "/history",
    response_model=List[StepResponse],
    status_code=status.HTTP_200_OK,
    summary="Get step history",
    responses={
        200: {"description": "Step history returned"},
        401: {"description": "Unauthorized"},
    },
)
def get_step_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[StepResponse]:
    """Return the user's step records ordered newest-first."""
    records = StepService.get_step_history(db, current_user, limit=limit)
    return [StepResponse.model_validate(r) for r in records]
