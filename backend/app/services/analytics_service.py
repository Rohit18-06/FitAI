"""
Analytics and progress tracking service.
Computes multi-day longitudinal trends, body composition delta, and milestone badges.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.bmi import BMIRecord
from app.models.calorie import CalorieRecord
from app.models.form_analysis import FormAnalysisRecord
from app.models.step import StepRecord
from app.models.user import User
from app.models.water import WaterRecord
from app.models.workout import WorkoutRecord
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Business logic for Analytics, Trends, and Milestones."""

    @classmethod
    def get_analytics_overview(
        cls,
        db: Session,
        user: User,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Produce daily time series, averages, and physical progress telemetry.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        start_date = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Pull raw records for period
        cals = (
            db.query(CalorieRecord)
            .filter(CalorieRecord.user_id == user.id, CalorieRecord.created_at >= start_date)
            .all()
        )
        waters = (
            db.query(WaterRecord)
            .filter(WaterRecord.user_id == user.id, WaterRecord.created_at >= start_date)
            .all()
        )
        steps = (
            db.query(StepRecord)
            .filter(StepRecord.user_id == user.id, StepRecord.created_at >= start_date)
            .all()
        )
        workouts = (
            db.query(WorkoutRecord)
            .filter(WorkoutRecord.user_id == user.id, WorkoutRecord.created_at >= start_date)
            .all()
        )
        bmis = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.asc())
            .all()
        )

        # Map by calendar date (str YYYY-MM-DD)
        daily_map: Dict[str, Dict[str, Any]] = {}
        for d_offset in range(days):
            day_str = (start_date + timedelta(days=d_offset)).strftime("%Y-%m-%d")
            daily_map[day_str] = {
                "date": day_str,
                "calories_consumed": 0.0,
                "water_liters": 0.0,
                "steps": 0,
                "workout_minutes": 0,
                "calories_burned": 0.0,
                "weight_kg": None,
            }

        for c in cals:
            ds = c.created_at.strftime("%Y-%m-%d")
            if ds in daily_map:
                daily_map[ds]["calories_consumed"] += c.calories

        for w in waters:
            ds = w.created_at.strftime("%Y-%m-%d")
            if ds in daily_map:
                daily_map[ds]["water_liters"] += w.liters

        for s in steps:
            ds = s.created_at.strftime("%Y-%m-%d")
            if ds in daily_map:
                daily_map[ds]["steps"] += s.steps
                daily_map[ds]["calories_burned"] += s.calories_burned

        for wo in workouts:
            ds = wo.created_at.strftime("%Y-%m-%d")
            if ds in daily_map:
                daily_map[ds]["workout_minutes"] += wo.duration_minutes
                daily_map[ds]["calories_burned"] += wo.calories_burned

        for b in bmis:
            ds = b.created_at.strftime("%Y-%m-%d")
            if ds in daily_map:
                daily_map[ds]["weight_kg"] = b.weight_kg

        trend_list = sorted(daily_map.values(), key=lambda x: x["date"])

        # Summary averages
        active_cal_days = [t["calories_consumed"] for t in trend_list if t["calories_consumed"] > 0]
        avg_cals = round(sum(active_cal_days) / len(active_cal_days), 1) if active_cal_days else 0.0

        active_step_days = [t["steps"] for t in trend_list if t["steps"] > 0]
        avg_steps = round(sum(active_step_days) / len(active_step_days)) if active_step_days else 0

        active_water_days = [t["water_liters"] for t in trend_list if t["water_liters"] > 0]
        avg_water = round(sum(active_water_days) / len(active_water_days), 2) if active_water_days else 0.0

        total_wo_min = sum(t["workout_minutes"] for t in trend_list)
        total_burned = sum(t["calories_burned"] for t in trend_list)

        # Progress telemetry
        start_wt, curr_wt, wt_delta = None, None, 0.0
        start_bmi, curr_bmi, bmi_delta = None, None, 0.0
        if bmis:
            start_wt = bmis[0].weight_kg
            curr_wt = bmis[-1].weight_kg
            wt_delta = round(curr_wt - start_wt, 2)
            start_bmi = bmis[0].bmi
            curr_bmi = bmis[-1].bmi
            bmi_delta = round(curr_bmi - start_bmi, 2)

        return {
            "user_id": user.id,
            "period_days": days,
            "summary": {
                "avg_daily_calories": avg_cals,
                "avg_daily_steps": avg_steps,
                "avg_daily_water_liters": avg_water,
                "total_workout_minutes": total_wo_min,
                "total_calories_burned": round(total_burned, 1),
            },
            "progress": {
                "start_weight_kg": start_wt,
                "current_weight_kg": curr_wt,
                "weight_delta_kg": wt_delta,
                "start_bmi": start_bmi,
                "current_bmi": curr_bmi,
                "bmi_delta": bmi_delta,
            },
            "daily_trends": trend_list,
        }

    @classmethod
    def get_user_milestones(cls, db: Session, user: User) -> Dict[str, Any]:
        """
        Evaluate and return all athletic and consistency achievement milestones.
        """
        # Collect counters
        total_workouts = db.query(WorkoutRecord).filter(WorkoutRecord.user_id == user.id).count()
        max_steps = (
            db.query(StepRecord.steps)
            .filter(StepRecord.user_id == user.id)
            .order_by(StepRecord.steps.desc())
            .first()
        )
        max_steps_val = max_steps[0] if max_steps else 0

        max_water = (
            db.query(WaterRecord.liters)
            .filter(WaterRecord.user_id == user.id)
            .order_by(WaterRecord.liters.desc())
            .first()
        )
        max_water_val = max_water[0] if max_water else 0.0

        form_analyses_count = (
            db.query(FormAnalysisRecord)
            .filter(FormAnalysisRecord.user_id == user.id)
            .count()
        )

        streaks = DashboardService._calculate_streaks(db, user)
        current_streak = streaks.get("current_streak_days", 0)
        longest_streak = streaks.get("longest_streak_days", 0)

        latest_bmi = (
            db.query(BMIRecord)
            .filter(BMIRecord.user_id == user.id)
            .order_by(BMIRecord.created_at.desc())
            .first()
        )

        milestone_defs = [
            {
                "id": "first_workout",
                "category": "workout",
                "title": "First Sweat",
                "description": "Log your first workout session in FitAI",
                "achieved": total_workouts >= 1,
                "progress_percentage": min(100, int((total_workouts / 1) * 100)),
                "badge_icon": "dumbbell",
            },
            {
                "id": "centurion_walker",
                "category": "steps",
                "title": "Centurion Walker",
                "description": "Surpass 10,000 steps in a single day",
                "achieved": max_steps_val >= 10000,
                "progress_percentage": min(100, int((max_steps_val / 10000) * 100)),
                "badge_icon": "shoe-prints",
            },
            {
                "id": "consistency_7_day",
                "category": "streak",
                "title": "Unstoppable Week",
                "description": "Maintain a 7-day continuous activity tracking streak",
                "achieved": longest_streak >= 7,
                "progress_percentage": min(100, int((longest_streak / 7) * 100)),
                "badge_icon": "fire",
            },
            {
                "id": "iron_habit",
                "category": "workout",
                "title": "Iron Habit",
                "description": "Complete 10 tracked workout sessions",
                "achieved": total_workouts >= 10,
                "progress_percentage": min(100, int((total_workouts / 10) * 100)),
                "badge_icon": "trophy",
            },
            {
                "id": "hydration_hero",
                "category": "water",
                "title": "Hydration Hero",
                "description": "Log at least 2.5 liters of water in a single day",
                "achieved": max_water_val >= 2.5,
                "progress_percentage": min(100, int((max_water_val / 2.5) * 100)),
                "badge_icon": "droplet",
            },
            {
                "id": "biomechanics_pioneer",
                "category": "form_analysis",
                "title": "Biomechanics Pioneer",
                "description": "Analyze your exercise technique with the Gemini Video Analyzer",
                "achieved": form_analyses_count >= 1,
                "progress_percentage": 100 if form_analyses_count >= 1 else 0,
                "badge_icon": "camera",
            },
            {
                "id": "healthy_bmi_zone",
                "category": "bmi",
                "title": "Optimal BMI Zone",
                "description": "Achieve and record a BMI within the Normal classification (18.5 – 24.9)",
                "achieved": latest_bmi is not None and latest_bmi.category == "Normal",
                "progress_percentage": 100 if (latest_bmi and latest_bmi.category == "Normal") else 50,
                "badge_icon": "heart-pulse",
            },
        ]

        achieved_cnt = sum(1 for m in milestone_defs if m["achieved"])
        return {
            "total_milestones": len(milestone_defs),
            "achieved_count": achieved_cnt,
            "milestones": milestone_defs,
        }
