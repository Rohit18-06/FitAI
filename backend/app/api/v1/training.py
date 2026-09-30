"""
Phase 8: AI Personal Trainer & Smart Coaching API Endpoints.
Covers exercise progressions, recovery assessment, plateau detection,
injury risk, body measurements, progress photos, goal tracking, and weekly reports.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.training import (
    ExerciseProgression,
    RecoveryAssessment,
    GoalTracking,
    BodyMeasurement,
    ProgressPhoto,
    InjuryRiskAssessment,
)
from app.schemas.training import (
    ExerciseProgressionCreate,
    ExerciseProgressionResponse,
    RecoveryAssessmentResponse,
    PlateauReport,
    InjuryRiskResponse,
    BodyMeasurementCreate,
    BodyMeasurementResponse,
    ProgressPhotoCreate,
    ProgressPhotoResponse,
    GoalCreate,
    GoalUpdateProgress,
    GoalResponse,
    WeeklyReportResponse,
)
from app.services.training_ai_service import (
    ExerciseProgressionService,
    RecoveryAIService,
    PlateauDetectorService,
    InjuryRiskService,
    BodyMeasurementService,
    ProgressPhotoService,
    GoalTrackingService,
    WeeklyReportService,
)

router = APIRouter(tags=["AI Personal Trainer & Smart Coaching"])


# ── Exercise Progression ─────────────────────────────────────────

@router.post(
    "/progressions",
    response_model=ExerciseProgressionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log exercise progression and calculate estimated 1RM",
)
def log_progression(
    data: ExerciseProgressionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ExerciseProgressionResponse:
    entry = ExerciseProgressionService.log_progression(
        db, current_user.id, data.model_dump()
    )
    return entry


@router.get(
    "/progressions",
    response_model=List[ExerciseProgressionResponse],
    summary="List exercise progression history",
)
def get_progressions(
    exercise_name: Optional[str] = Query(None, description="Filter by exercise name"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ExerciseProgressionResponse]:
    entries = ExerciseProgressionService.get_history(
        db, current_user.id, exercise_name=exercise_name, limit=limit
    )
    return entries


# ── Recovery Assessment ──────────────────────────────────────────

@router.post(
    "/recovery-assessment/compute",
    response_model=RecoveryAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compute AI recovery assessment score from sleep, HRV, and workouts",
)
def compute_recovery_assessment(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RecoveryAssessmentResponse:
    assessment = RecoveryAIService.compute_recovery(db, current_user.id)
    return assessment


@router.get(
    "/recovery-assessment/latest",
    response_model=Optional[RecoveryAssessmentResponse],
    summary="Get the most recent AI recovery assessment",
)
def get_latest_recovery_assessment(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Optional[RecoveryAssessmentResponse]:
    assessment = (
        db.query(RecoveryAssessment)
        .filter(RecoveryAssessment.user_id == current_user.id)
        .order_by(RecoveryAssessment.computed_at.desc())
        .first()
    )
    return assessment


# ── Plateau Detection ────────────────────────────────────────────

@router.get(
    "/plateaus",
    response_model=List[PlateauReport],
    summary="Detect fitness, weight, and strength plateaus",
)
def detect_plateaus(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[PlateauReport]:
    reports = PlateauDetectorService.detect_plateaus(db, current_user.id)
    return [PlateauReport(**r) for r in reports]


# ── Injury Risk Engine ───────────────────────────────────────────

@router.post(
    "/injury-risk/assess",
    response_model=InjuryRiskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assess injury risk based on form analysis, training load, and recovery",
)
def assess_injury_risk(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> InjuryRiskResponse:
    assessment = InjuryRiskService.assess_risk(db, current_user.id)
    return assessment


@router.get(
    "/injury-risk/latest",
    response_model=Optional[InjuryRiskResponse],
    summary="Get the latest injury risk assessment",
)
def get_latest_injury_risk(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Optional[InjuryRiskResponse]:
    assessment = (
        db.query(InjuryRiskAssessment)
        .filter(InjuryRiskAssessment.user_id == current_user.id)
        .order_by(InjuryRiskAssessment.assessed_at.desc())
        .first()
    )
    return assessment


# ── Body Measurements ────────────────────────────────────────────

@router.post(
    "/measurements",
    response_model=BodyMeasurementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record body measurements",
)
def add_measurement(
    data: BodyMeasurementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> BodyMeasurementResponse:
    measurement = BodyMeasurementService.add_measurement(
        db, current_user.id, data.model_dump(exclude_unset=True)
    )
    return measurement


@router.get(
    "/measurements",
    response_model=List[BodyMeasurementResponse],
    summary="List body measurement history",
)
def list_measurements(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[BodyMeasurementResponse]:
    return BodyMeasurementService.get_history(db, current_user.id, limit=limit)


@router.get(
    "/measurements/latest",
    response_model=Optional[BodyMeasurementResponse],
    summary="Get latest body measurement",
)
def get_latest_measurement(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Optional[BodyMeasurementResponse]:
    return BodyMeasurementService.get_latest(db, current_user.id)


# ── Progress Photos ──────────────────────────────────────────────

@router.post(
    "/progress-photos",
    response_model=ProgressPhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload or record progress photo",
)
def add_progress_photo(
    data: ProgressPhotoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ProgressPhotoResponse:
    photo = ProgressPhotoService.add_photo(
        db,
        current_user.id,
        photo_type=data.photo_type,
        filename=data.filename,
        file_path=data.file_path or f"uploads/{data.filename}",
        notes=data.notes,
    )
    return photo


@router.get(
    "/progress-photos",
    response_model=List[ProgressPhotoResponse],
    summary="List progress photos",
)
def list_progress_photos(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[ProgressPhotoResponse]:
    return ProgressPhotoService.list_photos(db, current_user.id, limit=limit)


# ── Goal Tracking ────────────────────────────────────────────────

@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fitness goal",
)
def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = GoalTrackingService.create_goal(db, current_user.id, data.model_dump())
    return goal


@router.get(
    "/goals",
    response_model=List[GoalResponse],
    summary="List user fitness goals",
)
def list_goals(
    goal_status: Optional[str] = Query(None, alias="status", description="Filter by status (active, completed, paused)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[GoalResponse]:
    return GoalTrackingService.list_goals(db, current_user.id, status=goal_status)


@router.get(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Get goal details by ID",
)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = GoalTrackingService.get_goal(db, current_user.id, goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    return goal


@router.patch(
    "/goals/{goal_id}/progress",
    response_model=GoalResponse,
    summary="Update goal current progress value",
)
def update_goal_progress(
    goal_id: int,
    data: GoalUpdateProgress,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = GoalTrackingService.update_progress(db, current_user.id, goal_id, data.current_value)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
    return goal


# ── Weekly Reports ───────────────────────────────────────────────

@router.post(
    "/weekly-reports/generate",
    response_model=WeeklyReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate comprehensive AI weekly coaching report",
)
def generate_weekly_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WeeklyReportResponse:
    report = WeeklyReportService.generate_report(db, current_user.id)
    return report


@router.get(
    "/weekly-reports",
    response_model=List[WeeklyReportResponse],
    summary="List past weekly coaching reports",
)
def list_weekly_reports(
    limit: int = Query(12, ge=1, le=52),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[WeeklyReportResponse]:
    return WeeklyReportService.list_reports(db, current_user.id, limit=limit)
