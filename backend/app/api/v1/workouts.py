"""
Workout tracking routes.

POST /api/v1/workouts          – log a workout session (protected)
GET  /api/v1/workouts/history  – retrieve workout history (protected)
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.workout import WorkoutCreate, WorkoutResponse
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post(
    "",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a workout session",
    responses={
        201: {"description": "Workout logged"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def add_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkoutResponse:
    """Log a new workout session with type, duration, and optional notes."""
    record = WorkoutService.add_workout(db, current_user, data)
    return WorkoutResponse.model_validate(record)


@router.get(
    "/history",
    response_model=List[WorkoutResponse],
    status_code=status.HTTP_200_OK,
    summary="Get workout history",
    responses={
        200: {"description": "Workout history returned"},
        401: {"description": "Unauthorized"},
    },
)
def get_workout_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[WorkoutResponse]:
    """Return the user's workout records ordered newest-first."""
    records = WorkoutService.get_workout_history(db, current_user, limit=limit)
    return [WorkoutResponse.model_validate(r) for r in records]
