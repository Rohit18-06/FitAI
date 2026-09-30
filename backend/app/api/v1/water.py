"""
Water intake routes.

POST /api/v1/water          – log water intake (protected)
GET  /api/v1/water/history  – retrieve water history (protected)
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.water import WaterCreate, WaterResponse
from app.services.water_service import WaterService

router = APIRouter(prefix="/water", tags=["Water"])


@router.post(
    "",
    response_model=WaterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log water intake",
    responses={
        201: {"description": "Water intake logged"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def add_water(
    data: WaterCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WaterResponse:
    """
    Log a water intake entry.

    Supply **glasses**, **liters**, or both — the missing value will be
    automatically derived (1 glass ≈ 0.25 L).
    """
    record = WaterService.add_water_intake(db, current_user, data)
    return WaterResponse.model_validate(record)


@router.get(
    "/history",
    response_model=List[WaterResponse],
    status_code=status.HTTP_200_OK,
    summary="Get water intake history",
    responses={
        200: {"description": "Water history returned"},
        401: {"description": "Unauthorized"},
    },
)
def get_water_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[WaterResponse]:
    """Return the user's water records ordered newest-first."""
    records = WaterService.get_water_history(db, current_user, limit=limit)
    return [WaterResponse.model_validate(r) for r in records]
