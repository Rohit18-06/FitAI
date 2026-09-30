"""
Dashboard service.
Aggregates live health telemetry, daily targets, weekly adherence, streaks, and insights.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Set

from sqlalchemy.orm import Session

from app.models.bmi import BMIRecord
from app.models.calorie import CalorieRecord
from app.models.diet_plan import DietPlan
from app.models.step import StepRecord
from app.models.user import User
from app.models.water import WaterRecord
from app.models.workout import WorkoutRecord
from app.models.workout_plan import WorkoutPlan
from app.services.health_insight_service import HealthInsightService

logger = logging.getLogger(__name__)


def _today_bounds() -> tuple[datetime, datetime]:
    """Return start of today and start of tomorrow in UTC."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


class DashboardService:
    """Aggregates all modules for the central Dashboard view."""

    @classmethod
    def get_dashboard_overview(cls, db: Session, user: User) -> Dict[str, Any]:
        """
        Produce real-time aggregated dashboard telemetry.
        """
        start_today, end_today = _today_bounds()

        # 1. Active Plans
        active_diet = (
            db.query(DietPlan)
            .filter(DietPlan.user_id == user.id, DietPlan.is_active == True)
            .order_by(DietPlan.created_at.desc())
            .first()
        )
        active_workout = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.is_active == True)
            .order_by(WorkoutPlan.created_at.desc())
            .first()
        )

        cal_target = active_diet.target_calories if active_diet else 2200.0
        water_target = 2.5
        steps_target = 10000

        # 2. Today's Totals
        today_cals = sum(
            r.calories for r in db.query(CalorieRecord)
            .filter(CalorieRecord.user_id == user.id, CalorieRecord.created_at >= start_today, CalorieRecord.created_at < end_today)
            .all()
        )
        today_water = sum(
            r.liters for r in db.query(WaterRecord)
            .filter(WaterRecord.user_id == user.id, WaterRecord.created_at >= start_today, WaterRecord.created_at < end_today)
            .all()
        )
        today_steps = sum(
            r.steps for r in db.query(StepRecord)
            .filter(StepRecord.user_id == user.id, StepRecord.created_at >= start_today, StepRecord.created_at < end_today)
            .all()
        )
        today_workouts = (
            db.query(WorkoutRecord)
            .filter(WorkoutRecord.user_id == user.id, WorkoutRecord.created_at >= start_today, WorkoutRecord.created_at < end_today)
            .all()
        )
        today_wo_min = sum(r.duration_minutes for r in today_workouts)
        today_wo_burned = sum(r.calories_burned for r in today_workouts)

        # 3. Latest BMI
        latest_bmi = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.desc())
            .first()
        )

        # 4. Weekly Adherence (Last 7 days)
        seven_days_ago = start_today - timedelta(days=6)
        recent_workouts = (
            db.query(WorkoutRecord)
            .filter(WorkoutRecord.user_id == user.id, WorkoutRecord.created_at >= seven_days_ago)
            .all()
        )
        workout_days = len(set(r.created_at.date() for r in recent_workouts))

        recent_water = (
            db.query(WaterRecord)
            .filter(WaterRecord.user_id == user.id, WaterRecord.created_at >= seven_days_ago)
            .all()
        )
        water_by_day: Dict[Any, float] = {}
        for w in recent_water:
            d = w.created_at.date()
            water_by_day[d] = water_by_day.get(d, 0.0) + w.liters
        water_met_days = sum(1 for liters in water_by_day.values() if liters >= 2.0)

        recent_cals = (
            db.query(CalorieRecord)
            .filter(CalorieRecord.user_id == user.id, CalorieRecord.created_at >= seven_days_ago)
            .all()
        )
        cals_by_day: Dict[Any, float] = {}
        for c in recent_cals:
            d = c.created_at.date()
            cals_by_day[d] = cals_by_day.get(d, 0.0) + c.calories
        cal_met_days = sum(1 for cals in cals_by_day.values() if abs(cals - cal_target) <= 400)

        target_wo_days = active_workout.days_per_week if active_workout else 4
        # Calculate adherence percentage
        wo_ratio = min(1.0, workout_days / max(1, target_wo_days))
        water_ratio = min(1.0, water_met_days / 7.0)
        cal_ratio = min(1.0, cal_met_days / 7.0)
        overall_score = round(((wo_ratio * 0.4) + (water_ratio * 0.3) + (cal_ratio * 0.3)) * 100)

        # 5. Streak Calculation
        streak_stats = cls._calculate_streaks(db, user)

        # 6. Insights (Generate fresh if none exist)
        insights = HealthInsightService.get_user_insights(db, user, limit=3)
        if not insights:
            insights = HealthInsightService.generate_insights_for_user(db, user)[:3]

        return {
            "user_id": user.id,
            "username": user.username,
            "today": {
                "calories_consumed": round(today_cals, 1),
                "calories_target": cal_target,
                "calories_remaining": max(0.0, round(cal_target - today_cals, 1)),
                "water_liters": round(today_water, 2),
                "water_target_liters": water_target,
                "steps_count": today_steps,
                "steps_target": steps_target,
                "workout_minutes": today_wo_min,
                "calories_burned": round(today_wo_burned, 1),
            },
            "bmi_status": {
                "current_bmi": latest_bmi.bmi if latest_bmi else None,
                "category": latest_bmi.category if latest_bmi else "Not Recorded",
                "weight_kg": latest_bmi.weight_kg if latest_bmi else None,
                "height_cm": latest_bmi.height_cm if latest_bmi else None,
            },
            "weekly_adherence": {
                "overall_score": overall_score,
                "workout_days_completed": workout_days,
                "target_workout_days": target_wo_days,
                "water_target_met_days": water_met_days,
                "calorie_target_met_days": cal_met_days,
            },
            "streaks": streak_stats,
            "active_diet_plan_title": active_diet.title if active_diet else None,
            "active_workout_plan_title": active_workout.title if active_workout else None,
            "recent_insights": insights,
        }

    @classmethod
    def _calculate_streaks(cls, db: Session, user: User) -> Dict[str, int]:
        """Calculates current and longest activity logging streak in days."""
        # Collect distinct active dates across all tables
        active_dates: Set[datetime.date] = set()

        for model in [CalorieRecord, WaterRecord, WorkoutRecord, StepRecord, BMIRecord]:
            rows = db.query(model.created_at).filter(model.user_id == user.id).all()
            for (dt,) in rows:
                if dt:
                    active_dates.add(dt.date())

        if not active_dates:
            return {"current_streak_days": 0, "longest_streak_days": 0, "total_active_days": 0}

        sorted_dates = sorted(active_dates)
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        # Check current streak
        current_streak = 0
        pivot = today if today in active_dates else (yesterday if yesterday in active_dates else None)

        if pivot:
            curr = pivot
            while curr in active_dates:
                current_streak += 1
                curr -= timedelta(days=1)

        # Check longest streak
        longest_streak = 0
        temp_streak = 0
        prev_date = None

        for d in sorted_dates:
            if prev_date is None:
                temp_streak = 1
            elif d == prev_date + timedelta(days=1):
                temp_streak += 1
            elif d == prev_date:
                pass
            else:
                temp_streak = 1
            prev_date = d
            if temp_streak > longest_streak:
                longest_streak = temp_streak

        return {
            "current_streak_days": current_streak,
            "longest_streak_days": max(longest_streak, current_streak),
            "total_active_days": len(active_dates),
        }
