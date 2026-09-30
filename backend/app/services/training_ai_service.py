"""
Phase 8: AI Training Engine Service.
Adaptive progression, program generation, plateau detection,
recovery intelligence, injury risk, weekly reports, goal tracking.
"""

from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.training import (
    TrainingProgram, ProgramWeek, ProgramDay,
    ExerciseProgression, RecoveryAssessment, WeeklyReport,
    GoalTracking, BodyMeasurement, ProgressPhoto, InjuryRiskAssessment,
)
from app.models.workout import WorkoutRecord
from app.models.calorie import CalorieRecord
from app.models.water import WaterRecord
from app.models.step import StepRecord
from app.models.sleep_record import SleepRecord
from app.models.heart_rate_record import HeartRateRecord
from app.models.form_analysis import FormAnalysisRecord

logger = logging.getLogger(__name__)

_utcnow = lambda: datetime.now(timezone.utc).replace(tzinfo=None)


# ═══════════════════════════════════════════════════════════════
# TRAINING PROGRAM SERVICE
# ═══════════════════════════════════════════════════════════════

class TrainingProgramService:
    """Generates and manages adaptive AI training programs."""

    EXERCISE_DB: dict[str, list[dict]] = {
        "chest": [
            {"name": "Barbell Bench Press", "sets": 4, "reps": "8-10", "rest_seconds": 90},
            {"name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12", "rest_seconds": 75},
            {"name": "Cable Fly", "sets": 3, "reps": "12-15", "rest_seconds": 60},
            {"name": "Push-Ups", "sets": 3, "reps": "15-20", "rest_seconds": 45},
        ],
        "back": [
            {"name": "Barbell Rows", "sets": 4, "reps": "8-10", "rest_seconds": 90},
            {"name": "Pull-Ups", "sets": 3, "reps": "8-12", "rest_seconds": 90},
            {"name": "Seated Cable Row", "sets": 3, "reps": "10-12", "rest_seconds": 75},
            {"name": "Face Pulls", "sets": 3, "reps": "15-20", "rest_seconds": 45},
        ],
        "legs": [
            {"name": "Barbell Squat", "sets": 4, "reps": "6-8", "rest_seconds": 120},
            {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "rest_seconds": 90},
            {"name": "Leg Press", "sets": 3, "reps": "10-12", "rest_seconds": 90},
            {"name": "Walking Lunges", "sets": 3, "reps": "12 each", "rest_seconds": 60},
        ],
        "shoulders": [
            {"name": "Overhead Press", "sets": 4, "reps": "8-10", "rest_seconds": 90},
            {"name": "Lateral Raises", "sets": 3, "reps": "12-15", "rest_seconds": 45},
            {"name": "Rear Delt Fly", "sets": 3, "reps": "15-20", "rest_seconds": 45},
        ],
        "arms": [
            {"name": "Barbell Curl", "sets": 3, "reps": "10-12", "rest_seconds": 60},
            {"name": "Tricep Dips", "sets": 3, "reps": "10-12", "rest_seconds": 60},
            {"name": "Hammer Curl", "sets": 3, "reps": "12-15", "rest_seconds": 45},
            {"name": "Overhead Tricep Extension", "sets": 3, "reps": "12-15", "rest_seconds": 45},
        ],
        "core": [
            {"name": "Plank", "sets": 3, "reps": "60s", "rest_seconds": 30},
            {"name": "Cable Woodchop", "sets": 3, "reps": "12 each", "rest_seconds": 45},
            {"name": "Hanging Leg Raise", "sets": 3, "reps": "12-15", "rest_seconds": 45},
        ],
        "cardio": [
            {"name": "Treadmill Intervals", "sets": 1, "reps": "20 min", "rest_seconds": 0},
            {"name": "Rowing Machine", "sets": 1, "reps": "15 min", "rest_seconds": 0},
        ],
    }

    SPLIT_TEMPLATES: dict[int, list[list[str]]] = {
        3: [["chest", "shoulders", "core"], ["back", "arms"], ["legs", "core"]],
        4: [["chest", "shoulders"], ["back", "arms"], ["legs", "core"], ["shoulders", "arms", "cardio"]],
        5: [["chest"], ["back"], ["legs"], ["shoulders", "core"], ["arms", "cardio"]],
        6: [["chest"], ["back"], ["legs"], ["shoulders"], ["arms", "core"], ["legs", "cardio"]],
    }

    @staticmethod
    def generate_program(
        db: Session, user_id: int, fitness_goal: str, fitness_level: str,
        duration_weeks: int, days_per_week: int,
    ) -> TrainingProgram:
        """Generate a full multi-week training program."""
        # Deactivate previous programs
        db.query(TrainingProgram).filter(
            TrainingProgram.user_id == user_id,
            TrainingProgram.is_active == True,
        ).update({"is_active": False})

        title = f"{fitness_goal.replace('_', ' ').title()} — {duration_weeks}W Program"
        program = TrainingProgram(
            user_id=user_id, title=title, fitness_goal=fitness_goal,
            fitness_level=fitness_level, duration_weeks=duration_weeks,
            days_per_week=days_per_week, is_active=True,
            ai_notes=f"Auto-generated {fitness_level} {fitness_goal} program.",
        )
        db.add(program)
        db.flush()

        split = TrainingProgramService.SPLIT_TEMPLATES.get(
            days_per_week, TrainingProgramService.SPLIT_TEMPLATES[4]
        )

        for wk in range(1, duration_weeks + 1):
            is_deload = (wk % 4 == 0)
            intensity = 55.0 if is_deload else min(65.0 + (wk - 1) * 3.0, 90.0)
            vol_mod = 0.6 if is_deload else 1.0

            week = ProgramWeek(
                program_id=program.id, week_number=wk,
                theme="Deload" if is_deload else f"Progressive Overload Phase {math.ceil(wk / 4)}",
                intensity_pct=round(intensity, 1), volume_modifier=vol_mod,
            )
            db.add(week)
            db.flush()

            for d_idx, muscle_groups in enumerate(split):
                exercises = []
                for mg in muscle_groups:
                    for ex in TrainingProgramService.EXERCISE_DB.get(mg, [])[:3]:
                        exercises.append(ex.copy())

                day = ProgramDay(
                    week_id=week.id, day_number=d_idx + 1,
                    day_name=f"Day {d_idx + 1}",
                    focus=" / ".join(g.title() for g in muscle_groups),
                    exercises_json=exercises,
                    warmup_json=["5 min light cardio", "Dynamic stretching"],
                    cooldown_json=["Static stretching", "Foam rolling"],
                    estimated_duration_min=35 + len(exercises) * 5,
                )
                db.add(day)

        db.commit()
        db.refresh(program)
        return program

    @staticmethod
    def get_active_program(db: Session, user_id: int) -> TrainingProgram | None:
        return db.query(TrainingProgram).filter(
            TrainingProgram.user_id == user_id,
            TrainingProgram.is_active == True,
        ).order_by(desc(TrainingProgram.created_at)).first()

    @staticmethod
    def list_programs(db: Session, user_id: int) -> list[TrainingProgram]:
        return db.query(TrainingProgram).filter(
            TrainingProgram.user_id == user_id,
        ).order_by(desc(TrainingProgram.created_at)).all()

    @staticmethod
    def complete_day(db: Session, user_id: int, day_id: int) -> ProgramDay | None:
        day = db.query(ProgramDay).join(ProgramWeek).join(TrainingProgram).filter(
            ProgramDay.id == day_id,
            TrainingProgram.user_id == user_id,
        ).first()
        if day:
            day.completed = True
            day.completed_at = _utcnow()
            db.commit()
            db.refresh(day)
        return day


# ═══════════════════════════════════════════════════════════════
# EXERCISE PROGRESSION SERVICE
# ═══════════════════════════════════════════════════════════════

class ExerciseProgressionService:

    @staticmethod
    def _estimate_1rm(weight: float, reps: int) -> float:
        """Brzycki formula for 1RM estimation."""
        if reps <= 0 or weight <= 0:
            return 0.0
        return round(weight * (36.0 / (37.0 - reps)), 1) if reps < 37 else weight

    @staticmethod
    def log_progression(db: Session, user_id: int, data: dict) -> ExerciseProgression:
        one_rm = 0.0
        if data.get("weight_kg") and data.get("reps"):
            one_rm = ExerciseProgressionService._estimate_1rm(data["weight_kg"], data["reps"])

        entry = ExerciseProgression(
            user_id=user_id,
            exercise_name=data["exercise_name"],
            weight_kg=data.get("weight_kg"),
            sets=data.get("sets", 3),
            reps=data.get("reps", 10),
            rpe=data.get("rpe"),
            one_rep_max_est=one_rm if one_rm > 0 else None,
            notes=data.get("notes"),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_history(db: Session, user_id: int, exercise_name: str | None = None, limit: int = 50):
        q = db.query(ExerciseProgression).filter(ExerciseProgression.user_id == user_id)
        if exercise_name:
            q = q.filter(ExerciseProgression.exercise_name == exercise_name)
        return q.order_by(desc(ExerciseProgression.recorded_at)).limit(limit).all()


# ═══════════════════════════════════════════════════════════════
# RECOVERY AI SERVICE
# ═══════════════════════════════════════════════════════════════

class RecoveryAIService:
    """AI-driven recovery scoring engine."""

    @staticmethod
    def compute_recovery(db: Session, user_id: int) -> RecoveryAssessment:
        now = _utcnow()
        day_ago = now - timedelta(hours=24)

        # Sleep component
        sleep = db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id,
            SleepRecord.created_at >= day_ago,
        ).order_by(desc(SleepRecord.created_at)).first()

        sleep_score = 50
        if sleep:
            base = min(sleep.sleep_score, 100)
            duration_bonus = min(sleep.duration_hours / 8.0, 1.0) * 20
            deep_bonus = min(sleep.deep_sleep_hours / 2.0, 1.0) * 15
            sleep_score = int(min(base * 0.5 + duration_bonus + deep_bonus, 100))

        # HRV component
        hr = db.query(HeartRateRecord).filter(
            HeartRateRecord.user_id == user_id,
            HeartRateRecord.created_at >= day_ago,
        ).order_by(desc(HeartRateRecord.created_at)).first()

        hrv_score = 50
        rhr_score = 50
        if hr:
            if hr.hrv_rmssd and hr.hrv_rmssd > 0:
                hrv_score = int(min(hr.hrv_rmssd / 0.8, 100))
            if hr.resting_hr > 0:
                rhr_score = int(max(100 - (hr.resting_hr - 50) * 2, 10))

        # Workout load component
        recent_workouts = db.query(func.sum(WorkoutRecord.duration_minutes)).filter(
            WorkoutRecord.user_id == user_id,
            WorkoutRecord.created_at >= now - timedelta(days=3),
        ).scalar() or 0

        load_score = 80
        if recent_workouts > 180:
            load_score = 30
        elif recent_workouts > 120:
            load_score = 50
        elif recent_workouts > 60:
            load_score = 70

        # Weighted composite
        total = int(sleep_score * 0.35 + hrv_score * 0.25 + rhr_score * 0.20 + load_score * 0.20)
        total = max(0, min(total, 100))

        if total >= 85:
            status = "Optimal"
        elif total >= 70:
            status = "Good"
        elif total >= 50:
            status = "Moderate"
        elif total >= 30:
            status = "Fatigued"
        else:
            status = "Overtrained"

        recommendations = {
            "Optimal": "You're fully recovered. Great day for high-intensity training!",
            "Good": "Recovery is solid. You can push hard today with proper warm-up.",
            "Moderate": "Consider moderate intensity. Focus on technique over volume.",
            "Fatigued": "Take it easy. Light movement, yoga, or active recovery recommended.",
            "Overtrained": "Rest day strongly recommended. Focus on sleep and nutrition.",
        }

        assessment = RecoveryAssessment(
            user_id=user_id, score=total, status=status,
            sleep_score=sleep_score, hrv_score=hrv_score,
            resting_hr_score=rhr_score, workout_load_score=load_score,
            recommendation=recommendations[status],
            components_json={
                "sleep": {"score": sleep_score, "weight": 0.35},
                "hrv": {"score": hrv_score, "weight": 0.25},
                "resting_hr": {"score": rhr_score, "weight": 0.20},
                "workout_load": {"score": load_score, "weight": 0.20},
            },
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def get_history(db: Session, user_id: int, limit: int = 30):
        return db.query(RecoveryAssessment).filter(
            RecoveryAssessment.user_id == user_id,
        ).order_by(desc(RecoveryAssessment.computed_at)).limit(limit).all()


# ═══════════════════════════════════════════════════════════════
# PLATEAU DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════

class PlateauDetectionService:

    @staticmethod
    def detect_plateaus(db: Session, user_id: int) -> list[dict]:
        results = []
        now = _utcnow()
        lookback = now - timedelta(days=21)

        # Weight plateau
        measurements = db.query(BodyMeasurement).filter(
            BodyMeasurement.user_id == user_id,
            BodyMeasurement.measured_at >= lookback,
            BodyMeasurement.weight_kg.isnot(None),
        ).order_by(BodyMeasurement.measured_at).all()

        if len(measurements) >= 3:
            weights = [m.weight_kg for m in measurements]
            weight_range = max(weights) - min(weights)
            if weight_range < 0.5:
                results.append({
                    "detected": True, "plateau_type": "weight",
                    "duration_days": (measurements[-1].measured_at - measurements[0].measured_at).days,
                    "severity": "moderate" if weight_range < 0.3 else "mild",
                    "recommendation": "Consider adjusting caloric intake by ±200 calories. Add HIIT sessions or change training stimulus.",
                    "data_points": [{"date": str(m.measured_at.date()), "value": m.weight_kg} for m in measurements],
                })

        # Step activity decline
        recent_steps = db.query(StepRecord).filter(
            StepRecord.user_id == user_id,
            StepRecord.created_at >= lookback,
        ).order_by(StepRecord.created_at).all()

        if len(recent_steps) >= 7:
            half = len(recent_steps) // 2
            first_avg = sum(s.steps for s in recent_steps[:half]) / half
            second_avg = sum(s.steps for s in recent_steps[half:]) / (len(recent_steps) - half)
            if first_avg > 0 and second_avg / first_avg < 0.7:
                results.append({
                    "detected": True, "plateau_type": "activity_decline",
                    "duration_days": 14,
                    "severity": "moderate",
                    "recommendation": "Your activity has dropped. Try walking meetings, evening walks, or set step reminders.",
                })

        # Strength plateau (check exercise progressions)
        exercises = db.query(ExerciseProgression.exercise_name).filter(
            ExerciseProgression.user_id == user_id,
        ).distinct().limit(5).all()

        for (ex_name,) in exercises:
            records = db.query(ExerciseProgression).filter(
                ExerciseProgression.user_id == user_id,
                ExerciseProgression.exercise_name == ex_name,
                ExerciseProgression.recorded_at >= lookback,
                ExerciseProgression.one_rep_max_est.isnot(None),
            ).order_by(ExerciseProgression.recorded_at).all()

            if len(records) >= 3:
                maxes = [r.one_rep_max_est for r in records]
                rng = max(maxes) - min(maxes)
                if rng < 2.5:
                    results.append({
                        "detected": True, "plateau_type": "strength",
                        "duration_days": (records[-1].recorded_at - records[0].recorded_at).days,
                        "severity": "mild",
                        "recommendation": f"Strength plateau on {ex_name}. Try varying rep ranges, adding pauses, or changing grip width.",
                    })

        if not results:
            results.append({"detected": False, "plateau_type": None, "severity": "none",
                            "recommendation": "No plateaus detected. Keep up the great work!"})

        return results


PlateauDetectorService = PlateauDetectionService


# ═══════════════════════════════════════════════════════════════
# INJURY RISK ENGINE
# ═══════════════════════════════════════════════════════════════

class InjuryRiskService:

    @staticmethod
    def assess_risk(db: Session, user_id: int) -> InjuryRiskAssessment:
        factors = []
        risk_points = 0

        # 1. Video analyzer form scores
        analyses = db.query(FormAnalysisRecord).filter(
            FormAnalysisRecord.user_id == user_id,
        ).order_by(desc(FormAnalysisRecord.created_at)).limit(5).all()

        if analyses:
            avg_form = sum(a.form_score for a in analyses) / len(analyses)
            if avg_form < 50:
                risk_points += 30
                factors.append({"factor": "Poor form scores", "severity": "high", "detail": f"Average form score: {avg_form:.0f}/100"})
            elif avg_form < 70:
                risk_points += 15
                factors.append({"factor": "Moderate form quality", "severity": "medium", "detail": f"Average form score: {avg_form:.0f}/100"})

        # 2. Recovery status
        latest_recovery = db.query(RecoveryAssessment).filter(
            RecoveryAssessment.user_id == user_id,
        ).order_by(desc(RecoveryAssessment.computed_at)).first()

        if latest_recovery:
            if latest_recovery.score < 30:
                risk_points += 25
                factors.append({"factor": "Very low recovery", "severity": "high", "detail": f"Recovery score: {latest_recovery.score}/100"})
            elif latest_recovery.score < 50:
                risk_points += 12
                factors.append({"factor": "Below-average recovery", "severity": "medium", "detail": f"Recovery score: {latest_recovery.score}/100"})

        # 3. Workout frequency (overtraining)
        week_ago = _utcnow() - timedelta(days=7)
        workout_count = db.query(func.count(WorkoutRecord.id)).filter(
            WorkoutRecord.user_id == user_id,
            WorkoutRecord.created_at >= week_ago,
        ).scalar() or 0

        if workout_count >= 7:
            risk_points += 20
            factors.append({"factor": "No rest days this week", "severity": "high", "detail": f"{workout_count} workouts in 7 days"})
        elif workout_count >= 6:
            risk_points += 10
            factors.append({"factor": "High training frequency", "severity": "medium", "detail": f"{workout_count} workouts in 7 days"})

        # 4. Sleep deficit
        recent_sleep = db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id,
            SleepRecord.created_at >= week_ago,
        ).all()

        if recent_sleep:
            avg_sleep = sum(s.duration_hours for s in recent_sleep) / len(recent_sleep)
            if avg_sleep < 6:
                risk_points += 20
                factors.append({"factor": "Chronic sleep deficit", "severity": "high", "detail": f"Avg sleep: {avg_sleep:.1f}h"})
            elif avg_sleep < 7:
                risk_points += 8
                factors.append({"factor": "Suboptimal sleep", "severity": "medium", "detail": f"Avg sleep: {avg_sleep:.1f}h"})

        risk_score = min(risk_points, 100)

        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        corrective = []
        if risk_level == "High":
            corrective = ["Take a rest day immediately", "Focus on sleep and nutrition", "Consider a deload week", "Review exercise form with video analysis"]
        elif risk_level == "Moderate":
            corrective = ["Ensure at least 2 rest days per week", "Prioritize 7+ hours of sleep", "Use foam rolling and mobility work"]

        rec_map = {
            "High": "High injury risk detected. Reduce training intensity and volume immediately.",
            "Moderate": "Moderate risk. Pay attention to recovery and form quality.",
            "Low": "Low risk. You're training safely. Keep monitoring recovery.",
        }

        assessment = InjuryRiskAssessment(
            user_id=user_id, risk_level=risk_level, risk_score=risk_score,
            factors_json=factors, corrective_actions=corrective,
            recommendation=rec_map[risk_level],
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment


# ═══════════════════════════════════════════════════════════════
# BODY MEASUREMENT SERVICE
# ═══════════════════════════════════════════════════════════════

class BodyMeasurementService:

    @staticmethod
    def add_measurement(db: Session, user_id: int, data: dict) -> BodyMeasurement:
        m = BodyMeasurement(user_id=user_id, **data)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m

    @staticmethod
    def get_history(db: Session, user_id: int, limit: int = 50):
        return db.query(BodyMeasurement).filter(
            BodyMeasurement.user_id == user_id,
        ).order_by(desc(BodyMeasurement.measured_at)).limit(limit).all()

    @staticmethod
    def get_latest(db: Session, user_id: int) -> BodyMeasurement | None:
        return db.query(BodyMeasurement).filter(
            BodyMeasurement.user_id == user_id,
        ).order_by(desc(BodyMeasurement.measured_at)).first()


# ═══════════════════════════════════════════════════════════════
# PROGRESS PHOTO SERVICE
# ═══════════════════════════════════════════════════════════════

class ProgressPhotoService:

    @staticmethod
    def add_photo(db: Session, user_id: int, photo_type: str, filename: str, file_path: str,
                  notes: str | None = None) -> ProgressPhoto:
        photo = ProgressPhoto(
            user_id=user_id, photo_type=photo_type, filename=filename,
            file_path=file_path, notes=notes,
            ai_analysis="Photo uploaded. AI analysis will be available after processing.",
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo

    @staticmethod
    def list_photos(db: Session, user_id: int, limit: int = 50):
        return db.query(ProgressPhoto).filter(
            ProgressPhoto.user_id == user_id,
        ).order_by(desc(ProgressPhoto.taken_at)).limit(limit).all()


# ═══════════════════════════════════════════════════════════════
# GOAL TRACKING SERVICE
# ═══════════════════════════════════════════════════════════════

class GoalTrackingService:

    @staticmethod
    def create_goal(db: Session, user_id: int, data: dict) -> GoalTracking:
        goal = GoalTracking(
            user_id=user_id,
            goal_type=data["goal_type"],
            title=data["title"],
            description=data.get("description"),
            target_value=data.get("target_value"),
            unit=data.get("unit"),
            start_value=data.get("start_value", 0.0),
            current_value=data.get("start_value", 0.0),
            target_date=data.get("target_date"),
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update_progress(db: Session, user_id: int, goal_id: int, current_value: float) -> GoalTracking | None:
        goal = db.query(GoalTracking).filter(
            GoalTracking.id == goal_id,
            GoalTracking.user_id == user_id,
        ).first()
        if not goal:
            return None

        goal.current_value = current_value

        if goal.target_value and goal.target_value > 0:
            if goal.start_value is not None:
                total_range = abs(goal.target_value - goal.start_value)
                if total_range > 0:
                    progress = abs(current_value - goal.start_value) / total_range
                    goal.completion_pct = round(min(progress * 100, 100), 1)
            else:
                goal.completion_pct = round(min(current_value / goal.target_value * 100, 100), 1)

        if goal.completion_pct >= 100 and goal.status == "active":
            goal.status = "completed"
            goal.completed_at = _utcnow()

        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def list_goals(db: Session, user_id: int, status: str | None = None):
        q = db.query(GoalTracking).filter(GoalTracking.user_id == user_id)
        if status:
            q = q.filter(GoalTracking.status == status)
        return q.order_by(desc(GoalTracking.created_at)).all()

    @staticmethod
    def get_goal(db: Session, user_id: int, goal_id: int) -> GoalTracking | None:
        return db.query(GoalTracking).filter(
            GoalTracking.id == goal_id,
            GoalTracking.user_id == user_id,
        ).first()


# ═══════════════════════════════════════════════════════════════
# WEEKLY REPORT SERVICE
# ═══════════════════════════════════════════════════════════════

class WeeklyReportService:

    @staticmethod
    def generate_report(db: Session, user_id: int) -> WeeklyReport:
        now = _utcnow()
        week_start = now - timedelta(days=7)

        # Training summary
        workouts = db.query(WorkoutRecord).filter(
            WorkoutRecord.user_id == user_id,
            WorkoutRecord.created_at >= week_start,
        ).all()
        total_mins = sum(w.duration_minutes for w in workouts)
        total_cal_burned = sum(w.calories_burned or 0 for w in workouts)
        training_summary = (
            f"You completed {len(workouts)} workouts totalling {total_mins} minutes "
            f"and burned {total_cal_burned} calories this week."
        )

        # Nutrition summary
        meals = db.query(CalorieRecord).filter(
            CalorieRecord.user_id == user_id,
            CalorieRecord.created_at >= week_start,
        ).all()
        total_cal = sum(m.calories for m in meals)
        avg_daily_cal = total_cal / 7 if total_cal else 0
        nutrition_summary = f"Average daily intake: {avg_daily_cal:.0f} calories across {len(meals)} logged meals."

        # Sleep summary
        sleeps = db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id,
            SleepRecord.created_at >= week_start,
        ).all()
        avg_sleep = sum(s.duration_hours for s in sleeps) / len(sleeps) if sleeps else 0
        sleep_summary = f"Average sleep: {avg_sleep:.1f} hours per night ({len(sleeps)} nights tracked)."

        # Recovery summary
        recoveries = db.query(RecoveryAssessment).filter(
            RecoveryAssessment.user_id == user_id,
            RecoveryAssessment.computed_at >= week_start,
        ).all()
        avg_recovery = sum(r.score for r in recoveries) / len(recoveries) if recoveries else 0
        recovery_summary = f"Average recovery score: {avg_recovery:.0f}/100 across {len(recoveries)} assessments."

        # Progress score
        progress = 50
        if len(workouts) >= 3:
            progress += 15
        if avg_sleep >= 7:
            progress += 10
        if avg_recovery >= 70:
            progress += 15
        if avg_daily_cal > 0:
            progress += 10
        progress = min(progress, 100)

        highlights = []
        if len(workouts) >= 4:
            highlights.append(f"💪 Strong training week — {len(workouts)} sessions!")
        if avg_sleep >= 7.5:
            highlights.append(f"😴 Excellent sleep quality — {avg_sleep:.1f}h average")
        if avg_recovery >= 75:
            highlights.append(f"❤️ Great recovery — {avg_recovery:.0f}/100")

        recs = []
        if len(workouts) < 3:
            recs.append("Try to fit in at least 3 workouts next week.")
        if avg_sleep < 7:
            recs.append("Aim for 7+ hours of sleep for optimal recovery.")
        if avg_daily_cal == 0:
            recs.append("Log your meals to get better nutrition insights.")
        if not recs:
            recs.append("Keep it up! You're on track. Consider progressive overload.")

        report = WeeklyReport(
            user_id=user_id, week_start=week_start, week_end=now,
            training_summary=training_summary, recovery_summary=recovery_summary,
            nutrition_summary=nutrition_summary, sleep_summary=sleep_summary,
            progress_score=progress, highlights=highlights, recommendations=recs,
            ai_coach_notes=f"Weekly coaching report generated on {now.strftime('%Y-%m-%d')}.",
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def list_reports(db: Session, user_id: int, limit: int = 12):
        return db.query(WeeklyReport).filter(
            WeeklyReport.user_id == user_id,
        ).order_by(desc(WeeklyReport.created_at)).limit(limit).all()
