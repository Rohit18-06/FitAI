"""
Pydantic schemas for Sleep, Heart Rate, Recovery, Personal Records, and Notifications.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Sleep ──────────────────────────────────────────────────────────────

class SleepCreate(BaseModel):
    """Payload to log a sleep record."""
    duration_hours: float = Field(..., ge=0, le=24, description="Total sleep time in hours")
    deep_sleep_hours: float = Field(default=0.0, ge=0, le=24)
    rem_sleep_hours: float = Field(default=0.0, ge=0, le=24)
    sleep_score: int = Field(default=75, ge=0, le=100)
    bed_time: Optional[datetime] = None
    wake_time: Optional[datetime] = None


class SleepResponse(BaseModel):
    """Sleep record returned to client."""
    id: int
    user_id: int
    duration_hours: float
    deep_sleep_hours: float
    rem_sleep_hours: float
    light_sleep_hours: float
    sleep_score: int
    bed_time: datetime
    wake_time: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Heart Rate ─────────────────────────────────────────────────────────

class HeartRateCreate(BaseModel):
    """Payload to log a heart rate reading."""
    current_hr: int = Field(..., ge=30, le=240, description="Current heart rate BPM")
    resting_hr: int = Field(default=60, ge=30, le=150)
    max_hr: int = Field(default=180, ge=60, le=250)
    hrv_rmssd: Optional[float] = Field(default=None, ge=0)
    vo2_max: Optional[float] = Field(default=None, ge=15, le=95)
    zone_1_mins: int = Field(default=0, ge=0)
    zone_2_mins: int = Field(default=0, ge=0)
    zone_3_mins: int = Field(default=0, ge=0)
    zone_4_mins: int = Field(default=0, ge=0)
    zone_5_mins: int = Field(default=0, ge=0)


class HeartRateResponse(BaseModel):
    """Heart rate record returned to client."""
    id: int
    user_id: int
    current_hr: int
    average_hr: float
    resting_hr: int
    max_hr: int
    hrv_rmssd: Optional[float] = None
    vo2_max: Optional[float] = None
    hr_zone_1_mins: int
    hr_zone_2_mins: int
    hr_zone_3_mins: int
    hr_zone_4_mins: int
    hr_zone_5_mins: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Recovery ───────────────────────────────────────────────────────────

class RecoveryResponse(BaseModel):
    """Recovery score and breakdown."""
    recovery_score: int
    status: str
    recommendation: str
    components: Dict[str, Any]
    latest_sleep: Dict[str, Any]
    latest_hr: Dict[str, Any]
    computed_at: datetime


# ── Personal Records ──────────────────────────────────────────────────

class PersonalRecordCreate(BaseModel):
    """Payload to log a personal record."""
    record_type: str = Field(..., min_length=2, max_length=50, description="Type: longest_run, fastest_5k, most_steps, etc.")
    record_name: str = Field(..., min_length=2, max_length=100, description="Display name e.g. 'Longest Run'")
    value: float = Field(..., ge=0)
    unit: str = Field(..., min_length=1, max_length=20, description="Unit: km, min, steps, kcal, kg")
    notes: Optional[str] = Field(default=None, max_length=500)


class PersonalRecordResponse(BaseModel):
    """Personal record returned to client."""
    id: int
    user_id: int
    record_type: str
    record_name: str
    value: float
    unit: str
    notes: Optional[str] = None
    achieved_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Notifications ─────────────────────────────────────────────────────

class NotificationCreate(BaseModel):
    """Payload to create a notification."""
    type: str = Field(..., description="hydration_reminder, workout_reminder, sleep_reminder, recovery_alert, achievement")
    title: str = Field(..., min_length=2, max_length=150)
    message: str = Field(..., min_length=2, max_length=1000)
    priority: str = Field(default="medium", description="high, medium, low")
    action_url: Optional[str] = Field(default=None, max_length=100)


class NotificationResponse(BaseModel):
    """Notification returned to client."""
    id: int
    user_id: int
    type: str
    title: str
    message: str
    priority: str
    action_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
