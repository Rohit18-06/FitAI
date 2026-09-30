"""
BMI routes.

POST /api/v1/bmi/calculate  – calculate & save a BMI reading (protected)
GET  /api/v1/bmi/history    – retrieve BMI history (protected)
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.bmi import BMICreate, BMIResponse
from app.services.bmi_service import BMIService

router = APIRouter(prefix="/bmi", tags=["BMI"])


@router.post(
    "/calculate",
    response_model=BMIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate BMI and save the record",
    responses={
        201: {"description": "BMI calculated and saved"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def calculate_bmi(
    data: BMICreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> BMIResponse:
    """
    Calculate the user's BMI from height and weight, persist the record,
    and return the result including the WHO category.

    Categories:
    - **Underweight**: BMI < 18.5
    - **Normal**: 18.5 ≤ BMI < 25
    - **Overweight**: 25 ≤ BMI < 30
    - **Obese**: BMI ≥ 30
    """
    record = BMIService.save_bmi_record(db, current_user, data)
    return BMIResponse.model_validate(record)


@router.get(
    "/history",
    response_model=List[BMIResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve BMI history",
    responses={
        200: {"description": "BMI history returned"},
        401: {"description": "Unauthorized"},
    },
)
def get_bmi_history(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[BMIResponse]:
    """Return the user's BMI records ordered newest-first."""
    records = BMIService.get_bmi_history(db, current_user, limit=limit)
    return [BMIResponse.model_validate(r) for r in records]
