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
    integrations,
    social,
    challenges,
    badges,
    teams,
    leaderboards,
    profiles,
    training_programs,
    training,
    vision_trainer,
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

# Phase 6 – Wearables & Real-Time Health Intelligence
router.include_router(integrations.router)

# Phase 7 – Social Fitness Ecosystem
router.include_router(social.router)
router.include_router(challenges.router)
router.include_router(badges.router)
router.include_router(teams.router)
router.include_router(leaderboards.router)
router.include_router(profiles.router)

# Phase 8 – AI Personal Trainer & Smart Coaching
router.include_router(training_programs.router)
router.include_router(training.router)

# Phase 9 – AI Computer Vision Coaching 2.0
router.include_router(vision_trainer.router)

__all__ = ["router"]
