"""
Workout plan API routes.
POST /api/v1/workout-plans/generate          – generate new workout routine
GET  /api/v1/workout-plans/active            – retrieve active workout routine
GET  /api/v1/workout-plans/history           – retrieve past workout routines
PUT  /api/v1/workout-plans/{plan_id}/activate – activate a historical routine
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.workout_plan import WorkoutPlanCreate, WorkoutPlanResponse
from app.services.workout_generator_service import WorkoutGeneratorService

router = APIRouter(prefix="/workout-plans", tags=["AI Workout Generator"])


@router.post(
    "/generate",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate and activate a new AI Workout Routine",
)
def generate_workout_plan(
    data: WorkoutPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkoutPlanResponse:
    """Generate a periodized training program using Gemini AI with fallback."""
    return WorkoutGeneratorService.generate_workout_plan(db, current_user, data)


@router.get(
    "/active",
    response_model=Optional[WorkoutPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve current active workout routine",
)
def get_active_workout_plan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[WorkoutPlanResponse]:
    """Return the client's currently active workout routine."""
    return WorkoutGeneratorService.get_active_workout_plan(db, current_user)


@router.get(
    "/history",
    response_model=List[WorkoutPlanResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve workout routine history",
)
def get_workout_plan_history(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[WorkoutPlanResponse]:
    """Return past generated workout programs."""
    return WorkoutGeneratorService.get_workout_plan_history(db, current_user, limit=limit)


@router.put(
    "/{plan_id}/activate",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate a specific historical workout routine",
)
def activate_workout_plan(
    plan_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkoutPlanResponse:
    """Make an existing program the active workout plan."""
    return WorkoutGeneratorService.activate_workout_plan(db, current_user, plan_id)
