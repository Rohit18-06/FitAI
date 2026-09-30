"""
Pydantic schemas for Wearable and Health Connect integrations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WearableConnectRequest(BaseModel):
    """Payload to connect a smartwatch or fitness provider."""
    provider: str = Field(..., description="Provider name: garmin, fitbit, apple_health, samsung_health, health_connect")
    device_name: str = Field(..., description="Device name e.g. 'Garmin Forerunner 965'")
    device_identifier: Optional[str] = Field(default=None, description="Optional hardware UUID / Serial")
    battery_level: Optional[int] = Field(default=100, ge=0, le=100)


class WearableDeviceResponse(BaseModel):
    """Information for a connected wearable device."""
    id: int
    user_id: int
    provider: str
    device_name: str
    device_identifier: Optional[str] = None
    battery_level: Optional[int] = 100
    is_connected: bool
    last_sync: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthConnectSyncPayload(BaseModel):
    """Payload incoming from Android Health Connect, Google Fit, or Apple Health."""
    provider: str = Field(default="health_connect", description="Source provider: health_connect, apple_health, google_fit")
    steps: Optional[int] = Field(default=None, ge=0)
    calories_burned: Optional[float] = Field(default=None, ge=0)
    distance_km: Optional[float] = Field(default=None, ge=0)
    active_minutes: Optional[int] = Field(default=None, ge=0)
    heart_rate: Optional[int] = Field(default=None, ge=30, le=240)
    resting_heart_rate: Optional[int] = Field(default=None, ge=30, le=150)
    hrv_rmssd: Optional[float] = Field(default=None, ge=0)
    sleep_duration_hours: Optional[float] = Field(default=None, ge=0, le=24)
    deep_sleep_hours: Optional[float] = Field(default=None, ge=0)
    rem_sleep_hours: Optional[float] = Field(default=None, ge=0)
    sleep_score: Optional[int] = Field(default=None, ge=0, le=100)
    weight_kg: Optional[float] = Field(default=None, ge=20, le=350)
    height_cm: Optional[float] = Field(default=None, ge=50, le=260)
    body_fat_pct: Optional[float] = Field(default=None, ge=2, le=70)
    vo2_max: Optional[float] = Field(default=None, ge=15, le=95)


class HealthConnectSyncResponse(BaseModel):
    """Status response returned after syncing Health Connect payload."""
    synced: bool
    provider: str
    records_updated: Dict[str, Any]
    timestamp: datetime


class HealthConnectStatusResponse(BaseModel):
    """Overview of user's wearable and Health Connect sync state."""
    connected: bool
    active_devices_count: int
    connected_providers: List[str]
    last_sync: Optional[datetime] = None
    supported_providers: List[str]
