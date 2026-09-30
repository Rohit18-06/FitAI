"""API v1 route aggregator."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    bmi,
    calories,
    workouts,
    water,
    steps,
    diet,
    workout_plans,
    video_analyzer,
    insights,
    dashboard,
    analytics,
    coach,
)

router = APIRouter(prefix="/v1")

# Core Trackers & Auth
router.include_router(auth.router)
router.include_router(bmi.router)
router.include_router(calories.router)
router.include_router(workouts.router)
router.include_router(water.router)
router.include_router(steps.router)

# AI Fitness Coach, Analytics & Dashboard
router.include_router(diet.router)
router.include_router(workout_plans.router)
router.include_router(video_analyzer.router)
router.include_router(insights.router)
router.include_router(dashboard.router)
router.include_router(analytics.router)
router.include_router(coach.router)

__all__ = ["router"]
