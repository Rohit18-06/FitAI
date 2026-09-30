"""
Phase 7 – Leaderboards API endpoints.
Rankings for Steps, Workouts, XP, Recovery, and Streaks.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.social import LeaderboardEntry
from app.services.social_service import LeaderboardService

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


@router.get(
    "/steps",
    response_model=List[LeaderboardEntry],
    summary="Leaderboard ranked by total steps",
)
def get_steps_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[LeaderboardEntry]:
    results = LeaderboardService.get_steps_leaderboard(db, limit=limit)
    return [LeaderboardEntry(**r) for r in results]


@router.get(
    "/workouts",
    response_model=List[LeaderboardEntry],
    summary="Leaderboard ranked by logged workout count",
)
def get_workouts_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[LeaderboardEntry]:
    results = LeaderboardService.get_workouts_leaderboard(db, limit=limit)
    return [LeaderboardEntry(**r) for r in results]


@router.get(
    "/xp",
    response_model=List[LeaderboardEntry],
    summary="Leaderboard ranked by total athlete XP",
)
def get_xp_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[LeaderboardEntry]:
    results = LeaderboardService.get_xp_leaderboard(db, limit=limit)
    return [LeaderboardEntry(**r) for r in results]


@router.get(
    "/recovery",
    response_model=List[LeaderboardEntry],
    summary="Leaderboard ranked by recovery & sleep readiness",
)
def get_recovery_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[LeaderboardEntry]:
    results = LeaderboardService.get_recovery_leaderboard(db, limit=limit)
    return [LeaderboardEntry(**r) for r in results]


@router.get(
    "/streaks",
    response_model=List[LeaderboardEntry],
    summary="Leaderboard ranked by active workout streak days",
)
def get_streaks_leaderboard(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[LeaderboardEntry]:
    results = LeaderboardService.get_streaks_leaderboard(db, limit=limit)
    return [LeaderboardEntry(**r) for r in results]
