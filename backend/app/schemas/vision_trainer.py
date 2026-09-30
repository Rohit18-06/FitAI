"""
Phase 9: Pydantic v2 schemas for AI Personal Trainer & Computer Vision Coaching 2.0.
Covers real-time pose estimation, exercise recognition, rep counting,
form corrections, live coach sessions, movement library, smart workout automation,
adaptive training, and studio analytics.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


# ── Keypoints & Pose Estimation ──────────────────────────────────

class Keypoint2D(BaseModel):
    x: float
    y: float
    z: Optional[float] = 0.0
    visibility: Optional[float] = 1.0


class PoseAnalyzeRequest(BaseModel):
    keypoints: List[Keypoint2D] = []
    exercise_hint: Optional[str] = None
    session_id: Optional[int] = None
    frame_timestamp_ms: Optional[float] = None
    image_base64: Optional[str] = None


class JointAnglesMap(BaseModel):
    left_knee: Optional[float] = None
    right_knee: Optional[float] = None
    left_hip: Optional[float] = None
    right_hip: Optional[float] = None
    left_elbow: Optional[float] = None
    right_elbow: Optional[float] = None
    left_shoulder: Optional[float] = None
    right_shoulder: Optional[float] = None
    torso_angle: Optional[float] = None


class PoseAnalyzeResponse(BaseModel):
    exercise: str
    confidence: float
    posture_score: float
    rep_count: int
    stage: str
    joint_angles: dict[str, float]
    mistakes: List[str]
    corrections: List[str]
    injury_risk: str  # LOW, MEDIUM, HIGH
    coach_cue: str
    fps: Optional[float] = None


# ── Exercise Recognition & Rep Counter ───────────────────────────

class ExerciseRecognitionResponse(BaseModel):
    exercise: str
    confidence: float
    rep_count: int
    stage: str


class RepCounterResponse(BaseModel):
    reps: int
    sets: int
    avg_tempo: float
    current_stage: str


class FormCorrectionResponse(BaseModel):
    exercise: str
    form_score: float
    mistakes: List[str]
    corrections: List[str]
    injury_risk: str


# ── Live AI Coach Session ────────────────────────────────────────

class LiveCoachSessionCreate(BaseModel):
    exercise_name: str = "Squat"
    target_reps: int = Field(default=10, ge=1, le=100)
    target_sets: int = Field(default=3, ge=1, le=10)


class LiveCoachSessionResponse(BaseModel):
    id: int
    user_id: int
    exercise_name: str
    target_reps: int
    target_sets: int
    completed_reps: int
    completed_sets: int
    avg_form_score: float
    avg_tempo: Optional[float] = None
    injury_risk_level: str
    status: str
    feedback_history: List[str] = []
    started_at: datetime
    ended_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LiveCoachCueResponse(BaseModel):
    cue: str
    speech_text: str
    tone: str  # encouraging, corrective, urgent


# ── Movement Library ─────────────────────────────────────────────

class MovementItemResponse(BaseModel):
    id: int
    name: str
    slug: str
    category: str
    equipment: str
    difficulty: str
    primary_muscles: List[str] = []
    secondary_muscles: List[str] = []
    instructions: List[str] = []
    common_mistakes: List[str] = []
    coaching_cues: List[str] = []
    demo_video_url: Optional[str] = None
    model_config = {"from_attributes": True}


# ── Smart Workout Automation ─────────────────────────────────────

class WorkoutAutomationRequest(BaseModel):
    fitness_goal: str = "hypertrophy"
    available_equipment: List[str] = ["Dumbbell", "Barbell", "Bodyweight"]
    time_minutes: int = Field(default=45, ge=15, le=120)
    fatigue_level: str = "low"  # low, moderate, high


class WorkoutExerciseItem(BaseModel):
    name: str
    target_sets: int
    target_reps: str
    rest_seconds: int
    tempo: str
    notes: Optional[str] = None


class WorkoutRoutineBlock(BaseModel):
    block_name: str  # Warmup, Main Workout, Accessory Work, Cooldown
    estimated_duration_min: int
    exercises: List[WorkoutExerciseItem] = []


class WorkoutAutomationResponse(BaseModel):
    session_title: str
    total_duration_min: int
    coaching_focus: str
    flow: List[WorkoutRoutineBlock] = []


# ── Adaptive Training System ─────────────────────────────────────

class AdaptivePlanRequest(BaseModel):
    soreness_level: str = "mild"
    fatigue_score: Optional[int] = None


class AdaptivePlanResponse(BaseModel):
    recovery_score: int
    adjustment_type: str  # increase_volume, decrease_volume, deload, maintain
    volume_multiplier: float
    recommended_reps_delta: int
    deload_recommended: bool
    recommendations: List[str] = []


# ── Trainer Studio Analytics ─────────────────────────────────────

class TrainerAnalyticsResponse(BaseModel):
    total_sessions: int
    total_reps_logged: int
    overall_avg_form_score: float
    form_score_history: List[dict[str, Any]] = []
    volume_by_exercise: dict[str, int] = {}
    injury_risk_distribution: dict[str, int] = {}
