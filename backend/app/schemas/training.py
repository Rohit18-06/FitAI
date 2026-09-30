"""
Phase 8: Pydantic v2 schemas for AI Personal Trainer.
Covers training programs, recovery, goals, measurements, photos,
weekly reports, injury risk, and exercise progression.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Training Program ─────────────────────────────────────────

class ProgramDayExercise(BaseModel):
    name: str
    sets: int = 3
    reps: str = "10"
    rest_seconds: int = 60
    notes: str | None = None

class ProgramDayResponse(BaseModel):
    id: int
    day_number: int
    day_name: str
    focus: str
    exercises: list[ProgramDayExercise] = []
    warmup: list[str] = []
    cooldown: list[str] = []
    estimated_duration_min: int
    completed: bool
    completed_at: datetime | None = None
    model_config = {"from_attributes": True}

class ProgramWeekResponse(BaseModel):
    id: int
    week_number: int
    theme: str | None = None
    intensity_pct: float
    volume_modifier: float
    notes: str | None = None
    days: list[ProgramDayResponse] = []
    model_config = {"from_attributes": True}

class TrainingProgramCreate(BaseModel):
    fitness_goal: str = "general_fitness"
    fitness_level: str = "intermediate"
    duration_weeks: int = Field(default=4, ge=1, le=16)
    days_per_week: int = Field(default=4, ge=1, le=7)

class TrainingProgramResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None = None
    fitness_goal: str
    fitness_level: str
    duration_weeks: int
    days_per_week: int
    is_active: bool
    ai_notes: str | None = None
    weeks: list[ProgramWeekResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class CompleteDayRequest(BaseModel):
    day_id: int


# ── Exercise Progression ──────────────────────────────────────

class ExerciseProgressionCreate(BaseModel):
    exercise_name: str
    weight_kg: float | None = None
    sets: int = Field(default=3, ge=1)
    reps: int = Field(default=10, ge=1)
    rpe: float | None = Field(default=None, ge=1, le=10)
    notes: str | None = None

class ExerciseProgressionResponse(BaseModel):
    id: int
    user_id: int
    exercise_name: str
    weight_kg: float | None = None
    sets: int
    reps: int
    rpe: float | None = None
    one_rep_max_est: float | None = None
    notes: str | None = None
    recorded_at: datetime
    model_config = {"from_attributes": True}


# ── Recovery Assessment ───────────────────────────────────────

class RecoveryAssessmentResponse(BaseModel):
    id: int
    user_id: int
    score: int
    status: str
    sleep_score: int | None = None
    hrv_score: int | None = None
    resting_hr_score: int | None = None
    workout_load_score: int | None = None
    recommendation: str | None = None
    components: dict[str, Any] = {}
    computed_at: datetime
    model_config = {"from_attributes": True}


# ── Weekly Report ─────────────────────────────────────────────

class WeeklyReportResponse(BaseModel):
    id: int
    user_id: int
    week_start: datetime
    week_end: datetime
    training_summary: str | None = None
    recovery_summary: str | None = None
    nutrition_summary: str | None = None
    sleep_summary: str | None = None
    progress_score: int
    highlights: list[str] = []
    recommendations: list[str] = []
    ai_coach_notes: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Goal Tracking ─────────────────────────────────────────────

class GoalCreate(BaseModel):
    goal_type: str
    title: str
    description: str | None = None
    target_value: float | None = None
    unit: str | None = None
    start_value: float | None = None
    target_date: datetime | None = None

class GoalUpdateProgress(BaseModel):
    current_value: float

class GoalResponse(BaseModel):
    id: int
    user_id: int
    goal_type: str
    title: str
    description: str | None = None
    target_value: float | None = None
    current_value: float
    unit: str | None = None
    start_value: float | None = None
    completion_pct: float
    status: str
    target_date: datetime | None = None
    completed_at: datetime | None = None
    milestones: list[dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Body Measurement ──────────────────────────────────────────

class BodyMeasurementCreate(BaseModel):
    weight_kg: float | None = None
    body_fat_pct: float | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hips_cm: float | None = None
    neck_cm: float | None = None
    left_arm_cm: float | None = None
    right_arm_cm: float | None = None
    left_thigh_cm: float | None = None
    right_thigh_cm: float | None = None
    notes: str | None = None

class BodyMeasurementResponse(BaseModel):
    id: int
    user_id: int
    weight_kg: float | None = None
    body_fat_pct: float | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hips_cm: float | None = None
    neck_cm: float | None = None
    left_arm_cm: float | None = None
    right_arm_cm: float | None = None
    left_thigh_cm: float | None = None
    right_thigh_cm: float | None = None
    notes: str | None = None
    measured_at: datetime
    model_config = {"from_attributes": True}


# ── Progress Photo ────────────────────────────────────────────

class ProgressPhotoCreate(BaseModel):
    photo_type: str = "front"  # front, back, side
    filename: str
    file_path: str = ""
    notes: str | None = None

class ProgressPhotoResponse(BaseModel):
    id: int
    user_id: int
    photo_type: str
    filename: str
    ai_analysis: str | None = None
    body_fat_estimate: float | None = None
    muscle_score: int | None = None
    notes: str | None = None
    taken_at: datetime
    model_config = {"from_attributes": True}


# ── Injury Risk ───────────────────────────────────────────────

class InjuryRiskResponse(BaseModel):
    id: int
    user_id: int
    risk_level: str
    risk_score: int
    factors: list[dict[str, Any]] = []
    corrective_actions: list[str] = []
    mobility_notes: str | None = None
    recommendation: str | None = None
    assessed_at: datetime
    model_config = {"from_attributes": True}


# ── Plateau Detection ─────────────────────────────────────────

class PlateauReport(BaseModel):
    detected: bool
    plateau_type: str | None = None
    duration_days: int = 0
    severity: str = "none"  # none/mild/moderate/severe
    recommendation: str | None = None
    data_points: list[dict[str, Any]] = []
