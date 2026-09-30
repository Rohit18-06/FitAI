"""
Phase 9: AI Personal Trainer & Computer Vision Coaching 2.0 API Endpoints.
Covers real-time pose estimation, exercise recognition, rep counting,
live coach sessions, movement library, automated workouts, adaptive training,
and trainer studio analytics.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.vision_trainer import TrainerSession, MovementLibraryItem
from app.schemas.vision_trainer import (
    PoseAnalyzeRequest,
    PoseAnalyzeResponse,
    LiveCoachSessionCreate,
    LiveCoachSessionResponse,
    MovementItemResponse,
    WorkoutAutomationRequest,
    WorkoutAutomationResponse,
    AdaptivePlanRequest,
    AdaptivePlanResponse,
    TrainerAnalyticsResponse,
)
from app.services.vision_trainer_service import (
    LiveCoachService,
    AdaptiveTrainingService,
    SmartWorkoutAutomationService,
    MovementLibraryService,
    TrainerAnalyticsService,
)

router = APIRouter(tags=["AI Personal Trainer & Computer Vision Coaching 2.0"])


# ── Module 1, 2, 3, 4: Real-time Pose Estimation & Analysis ──────

@router.post(
    "/pose/analyze",
    response_model=PoseAnalyzeResponse,
    summary="Analyze pose landmarks in real time for exercise classification, rep count, form faults, and cues",
)
def analyze_pose(
    data: PoseAnalyzeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> PoseAnalyzeResponse:
    keypoints_dicts = [k.model_dump() for k in data.keypoints]
    result = LiveCoachService.process_frame(
        db=db,
        user_id=current_user.id,
        keypoints=keypoints_dicts,
        exercise_hint=data.exercise_hint,
        session_id=data.session_id,
    )
    return PoseAnalyzeResponse(**result)


# ── Module 5: Live AI Coach Sessions ─────────────────────────────

@router.post(
    "/live-coach/session",
    response_model=LiveCoachSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initialize a live AI Personal Trainer coaching session",
)
def start_live_session(
    data: LiveCoachSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> LiveCoachSessionResponse:
    session = LiveCoachService.start_session(
        db,
        user_id=current_user.id,
        exercise_name=data.exercise_name,
        target_reps=data.target_reps,
        target_sets=data.target_sets,
    )
    return session


@router.get(
    "/live-coach/session/active",
    response_model=Optional[LiveCoachSessionResponse],
    summary="Get current active live trainer session",
)
def get_active_session(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Optional[LiveCoachSessionResponse]:
    session = (
        db.query(TrainerSession)
        .filter(
            TrainerSession.user_id == current_user.id,
            TrainerSession.status == "in_progress",
        )
        .order_by(TrainerSession.started_at.desc())
        .first()
    )
    return session


@router.post(
    "/live-coach/session/{session_id}/complete",
    response_model=LiveCoachSessionResponse,
    summary="Complete a live trainer session",
)
def complete_live_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> LiveCoachSessionResponse:
    session = LiveCoachService.complete_session(db, current_user.id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session


# ── Module 7: Adaptive Training System ───────────────────────────

@router.post(
    "/adaptive-training/plan",
    response_model=AdaptivePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate adaptive training volume and progression adjustments based on biometrics",
)
def generate_adaptive_plan(
    data: AdaptivePlanRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AdaptivePlanResponse:
    plan = AdaptiveTrainingService.generate_plan(
        db,
        user_id=current_user.id,
        soreness_level=data.soreness_level,
        fatigue_score=data.fatigue_score,
    )
    return AdaptivePlanResponse(
        recovery_score=plan.recovery_score,
        adjustment_type=plan.adjustment_type,
        volume_multiplier=plan.volume_multiplier,
        recommended_reps_delta=plan.recommended_reps_delta,
        deload_recommended=plan.deload_recommended,
        recommendations=plan.recommendations or [],
    )


# ── Module 8: Smart Workout Automation ───────────────────────────

@router.post(
    "/workout-automation/generate",
    response_model=WorkoutAutomationResponse,
    summary="Automatically generate complete 4-block workout session",
)
def generate_automated_workout(
    data: WorkoutAutomationRequest,
    current_user: User = Depends(get_current_active_user),
) -> WorkoutAutomationResponse:
    workout = SmartWorkoutAutomationService.build_automated_workout(
        fitness_goal=data.fitness_goal,
        equipment=data.available_equipment,
        duration_min=data.time_minutes,
        fatigue_level=data.fatigue_level,
    )
    return WorkoutAutomationResponse(**workout)


# ── Module 9: AI Movement Library (100+ Exercises) ───────────────

@router.post(
    "/movement-library/seed",
    summary="Seed the database with 100+ exercises in the movement library",
)
def seed_movement_library(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    count = MovementLibraryService.seed_library(db)
    return {"success": True, "total_exercises": count}


@router.get(
    "/movement-library",
    response_model=List[MovementItemResponse],
    summary="List exercises from the 100+ movement library with optional filters",
)
def list_movements(
    category: Optional[str] = Query(None, description="Filter by category (Strength, Calisthenics, Mobility, Cardio, Plyometrics)"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Beginner, Intermediate, Advanced)"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=150),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[MovementItemResponse]:
    # Ensure library is seeded
    MovementLibraryService.seed_library(db)
    items = MovementLibraryService.list_exercises(db, category, difficulty, search, limit)
    return items


@router.get(
    "/movement-library/{exercise_id}",
    response_model=MovementItemResponse,
    summary="Get exercise movement details by ID",
)
def get_movement_detail(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> MovementItemResponse:
    item = MovementLibraryService.get_by_id(db, exercise_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found in library",
        )
    return item


# ── Module 11: Trainer Studio Analytics ──────────────────────────

@router.get(
    "/trainer/analytics",
    response_model=TrainerAnalyticsResponse,
    summary="Retrieve AI Trainer Studio analytics, form score progression, and rep distributions",
)
def get_studio_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TrainerAnalyticsResponse:
    analytics = TrainerAnalyticsService.get_user_analytics(db, current_user.id)
    return TrainerAnalyticsResponse(**analytics)
