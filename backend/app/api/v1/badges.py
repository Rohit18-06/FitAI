"""
Phase 7 – Badges & Achievements API endpoints.
Covers Badges catalog, user badges, and achievement leveling overview.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.social import (
    BadgeResponse,
    AchievementsOverviewResponse,
    UserLevelResponse,
)
from app.services.social_service import BadgeService, XPService

router = APIRouter(tags=["Badges & Achievements"])


@router.get(
    "/badges",
    response_model=List[BadgeResponse],
    summary="List all badges with user earned status",
)
def list_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[BadgeResponse]:
    badges = BadgeService.get_all(db, current_user)
    return [BadgeResponse(**b) for b in badges]


@router.get(
    "/badges/my",
    response_model=List[BadgeResponse],
    summary="List only badges unlocked by current user",
)
def get_my_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[BadgeResponse]:
    badges = BadgeService.get_my_badges(db, current_user)
    return [BadgeResponse(**b) for b in badges]


@router.get(
    "/achievements",
    response_model=AchievementsOverviewResponse,
    summary="Get athlete achievements, badge count, and XP level progression",
)
def get_achievements(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AchievementsOverviewResponse:
    all_badges = BadgeService.get_all(db, current_user)
    earned = [b for b in all_badges if b["is_earned"]]
    lvl = XPService.get_or_create(db, current_user.id)

    cur_lvl_min = (lvl.level ** 2) * 100
    next_lvl = ((lvl.level + 1) ** 2) * 100
    denom = max(1, next_lvl - cur_lvl_min)
    pct = min(100.0, max(0.0, ((lvl.xp - cur_lvl_min) / denom) * 100.0))

    level_resp = UserLevelResponse(
        id=lvl.id,
        user_id=lvl.user_id,
        xp=lvl.xp,
        level=lvl.level,
        total_workouts=lvl.total_workouts,
        total_steps=lvl.total_steps,
        total_calories_burned=lvl.total_calories_burned,
        next_level_xp=next_lvl,
        progress_percent=round(pct, 1),
    )

    return AchievementsOverviewResponse(
        total_badges=len(all_badges),
        earned_count=len(earned),
        badges=[BadgeResponse(**b) for b in all_badges],
        user_level=level_resp,
    )
