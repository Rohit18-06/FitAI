"""
Wearable & Health Intelligence service.
Manages device connections, Health Connect data sync, sleep/HR telemetry,
personal records, notifications, and recovery score calculations.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.wearable_device import WearableDevice
from app.models.sleep_record import SleepRecord
from app.models.heart_rate_record import HeartRateRecord
from app.models.personal_record import PersonalRecord
from app.models.notification import Notification
from app.models.step import StepRecord
from app.models.calorie import CalorieRecord
from app.schemas.wearable import (
    WearableConnectRequest,
    HealthConnectSyncPayload,
)

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = [
    "health_connect", "garmin", "fitbit",
    "apple_health", "samsung_health", "google_fit",
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _today_range() -> tuple[datetime, datetime]:
    now = _utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)


# ---------------------------------------------------------------------------
# Device Management
# ---------------------------------------------------------------------------

class WearableDeviceService:
    """Manage wearable device connections."""

    @staticmethod
    def connect_device(
        db: Session, user: User, data: WearableConnectRequest,
    ) -> WearableDevice:
        if data.provider not in SUPPORTED_PROVIDERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider '{data.provider}'. Supported: {SUPPORTED_PROVIDERS}",
            )

        existing = (
            db.query(WearableDevice)
            .filter(
                WearableDevice.user_id == user.id,
                WearableDevice.provider == data.provider,
                WearableDevice.device_name == data.device_name,
            )
            .first()
        )
        if existing:
            existing.is_connected = True
            existing.battery_level = data.battery_level
            existing.last_sync = _utcnow()
            db.commit()
            db.refresh(existing)
            return existing

        device = WearableDevice(
            user_id=user.id,
            provider=data.provider,
            device_name=data.device_name,
            device_identifier=data.device_identifier,
            battery_level=data.battery_level,
            is_connected=True,
            last_sync=_utcnow(),
        )
        try:
            db.add(device)
            db.commit()
            db.refresh(device)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to connect device for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not connect wearable device",
            ) from exc
        return device

    @staticmethod
    def disconnect_device(db: Session, user: User, device_id: int) -> WearableDevice:
        device = (
            db.query(WearableDevice)
            .filter(WearableDevice.id == device_id, WearableDevice.user_id == user.id)
            .first()
        )
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        device.is_connected = False
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def get_devices(db: Session, user: User) -> List[WearableDevice]:
        return (
            db.query(WearableDevice)
            .filter(WearableDevice.user_id == user.id)
            .order_by(WearableDevice.last_sync.desc())
            .all()
        )

    @staticmethod
    def get_status(db: Session, user: User) -> dict:
        devices = (
            db.query(WearableDevice)
            .filter(WearableDevice.user_id == user.id)
            .all()
        )
        connected = [d for d in devices if d.is_connected]
        providers = list(set(d.provider for d in connected))
        last_sync = max((d.last_sync for d in connected), default=None) if connected else None
        return {
            "connected": len(connected) > 0,
            "active_devices_count": len(connected),
            "connected_providers": providers,
            "last_sync": last_sync,
            "supported_providers": SUPPORTED_PROVIDERS,
        }


# ---------------------------------------------------------------------------
# Health Connect Sync
# ---------------------------------------------------------------------------

class HealthConnectSyncService:
    """Process Health Connect / Google Fit / Apple Health sync payloads."""

    @staticmethod
    def sync(
        db: Session, user: User, payload: HealthConnectSyncPayload,
    ) -> dict:
        records_updated: Dict[str, Any] = {}
        now = _utcnow()

        # --- Steps ---
        if payload.steps is not None:
            step = StepRecord(
                user_id=user.id,
                steps=payload.steps,
                distance_km=payload.distance_km or 0.0,
                calories_burned=payload.calories_burned or 0.0,
            )
            db.add(step)
            records_updated["steps"] = payload.steps

        # --- Calories ---
        if payload.calories_burned is not None and "steps" not in records_updated:
            cal = CalorieRecord(
                user_id=user.id,
                food_name=f"Wearable Sync ({payload.provider})",
                calories=0.0,
                protein=0.0,
                carbs=0.0,
                fat=0.0,
            )
            db.add(cal)
            records_updated["calories_burned"] = payload.calories_burned

        # --- Heart Rate ---
        if payload.heart_rate is not None or payload.resting_heart_rate is not None:
            hr = HeartRateRecord(
                user_id=user.id,
                current_hr=payload.heart_rate or 72,
                average_hr=float(payload.heart_rate or 72),
                resting_hr=payload.resting_heart_rate or 60,
                max_hr=int((payload.heart_rate or 72) * 1.15),
                hrv_rmssd=payload.hrv_rmssd,
                vo2_max=payload.vo2_max,
            )
            db.add(hr)
            records_updated["heart_rate"] = {
                "current": payload.heart_rate,
                "resting": payload.resting_heart_rate,
                "hrv": payload.hrv_rmssd,
                "vo2_max": payload.vo2_max,
            }

        # --- Sleep ---
        if payload.sleep_duration_hours is not None:
            sleep = SleepRecord(
                user_id=user.id,
                duration_hours=payload.sleep_duration_hours,
                deep_sleep_hours=payload.deep_sleep_hours or 0.0,
                rem_sleep_hours=payload.rem_sleep_hours or 0.0,
                light_sleep_hours=max(
                    0.0,
                    payload.sleep_duration_hours
                    - (payload.deep_sleep_hours or 0.0)
                    - (payload.rem_sleep_hours or 0.0),
                ),
                sleep_score=payload.sleep_score or 75,
                bed_time=now - timedelta(hours=payload.sleep_duration_hours),
                wake_time=now,
            )
            db.add(sleep)
            records_updated["sleep"] = {
                "duration": payload.sleep_duration_hours,
                "score": payload.sleep_score or 75,
            }

        # --- Update device last_sync ---
        device = (
            db.query(WearableDevice)
            .filter(
                WearableDevice.user_id == user.id,
                WearableDevice.provider == payload.provider,
                WearableDevice.is_connected == True,  # noqa: E712
            )
            .first()
        )
        if device:
            device.last_sync = now

        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.exception("Health Connect sync failed for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Sync failed",
            ) from exc

        return {
            "synced": True,
            "provider": payload.provider,
            "records_updated": records_updated,
            "timestamp": now,
        }


# ---------------------------------------------------------------------------
# Sleep Analytics
# ---------------------------------------------------------------------------

class SleepService:
    """Sleep record management and analytics."""

    @staticmethod
    def log_sleep(
        db: Session, user: User,
        duration_hours: float,
        deep_sleep_hours: float = 0.0,
        rem_sleep_hours: float = 0.0,
        sleep_score: int = 75,
        bed_time: Optional[datetime] = None,
        wake_time: Optional[datetime] = None,
    ) -> SleepRecord:
        now = _utcnow()
        record = SleepRecord(
            user_id=user.id,
            duration_hours=duration_hours,
            deep_sleep_hours=deep_sleep_hours,
            rem_sleep_hours=rem_sleep_hours,
            light_sleep_hours=max(0.0, duration_hours - deep_sleep_hours - rem_sleep_hours),
            sleep_score=sleep_score,
            bed_time=bed_time or (now - timedelta(hours=duration_hours)),
            wake_time=wake_time or now,
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to log sleep for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save sleep record",
            ) from exc
        return record

    @staticmethod
    def get_history(db: Session, user: User, limit: int = 30) -> List[SleepRecord]:
        return (
            db.query(SleepRecord)
            .filter(SleepRecord.user_id == user.id)
            .order_by(SleepRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_analytics(db: Session, user: User, days: int = 7) -> dict:
        cutoff = _utcnow() - timedelta(days=days)
        records = (
            db.query(SleepRecord)
            .filter(SleepRecord.user_id == user.id, SleepRecord.created_at >= cutoff)
            .order_by(SleepRecord.created_at.desc())
            .all()
        )
        if not records:
            return {
                "period_days": days,
                "total_records": 0,
                "avg_duration": 0.0,
                "avg_deep_sleep": 0.0,
                "avg_rem_sleep": 0.0,
                "avg_score": 0,
                "best_score": 0,
                "worst_score": 0,
                "trend": "insufficient_data",
                "daily": [],
            }

        avg_dur = round(sum(r.duration_hours for r in records) / len(records), 2)
        avg_deep = round(sum(r.deep_sleep_hours for r in records) / len(records), 2)
        avg_rem = round(sum(r.rem_sleep_hours for r in records) / len(records), 2)
        scores = [r.sleep_score for r in records]
        avg_score = round(sum(scores) / len(scores))

        # Trend: compare first half vs second half
        mid = len(records) // 2
        if mid > 0:
            first_avg = sum(r.sleep_score for r in records[:mid]) / mid
            second_avg = sum(r.sleep_score for r in records[mid:]) / (len(records) - mid)
            trend = "improving" if first_avg > second_avg else ("declining" if first_avg < second_avg else "stable")
        else:
            trend = "stable"

        daily = [
            {
                "date": r.created_at.strftime("%Y-%m-%d"),
                "duration": r.duration_hours,
                "deep": r.deep_sleep_hours,
                "rem": r.rem_sleep_hours,
                "light": r.light_sleep_hours,
                "score": r.sleep_score,
            }
            for r in records
        ]

        return {
            "period_days": days,
            "total_records": len(records),
            "avg_duration": avg_dur,
            "avg_deep_sleep": avg_deep,
            "avg_rem_sleep": avg_rem,
            "avg_score": avg_score,
            "best_score": max(scores),
            "worst_score": min(scores),
            "trend": trend,
            "daily": daily,
        }


# ---------------------------------------------------------------------------
# Heart Rate Analytics
# ---------------------------------------------------------------------------

class HeartRateService:
    """Heart rate telemetry management and analytics."""

    @staticmethod
    def log_heart_rate(
        db: Session, user: User,
        current_hr: int,
        resting_hr: int = 60,
        max_hr: int = 180,
        hrv_rmssd: Optional[float] = None,
        vo2_max: Optional[float] = None,
        zone_mins: Optional[Dict[int, int]] = None,
    ) -> HeartRateRecord:
        record = HeartRateRecord(
            user_id=user.id,
            current_hr=current_hr,
            average_hr=float(current_hr),
            resting_hr=resting_hr,
            max_hr=max_hr,
            hrv_rmssd=hrv_rmssd,
            vo2_max=vo2_max,
            hr_zone_1_mins=(zone_mins or {}).get(1, 0),
            hr_zone_2_mins=(zone_mins or {}).get(2, 0),
            hr_zone_3_mins=(zone_mins or {}).get(3, 0),
            hr_zone_4_mins=(zone_mins or {}).get(4, 0),
            hr_zone_5_mins=(zone_mins or {}).get(5, 0),
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to log heart rate for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save heart rate record",
            ) from exc
        return record

    @staticmethod
    def get_history(db: Session, user: User, limit: int = 50) -> List[HeartRateRecord]:
        return (
            db.query(HeartRateRecord)
            .filter(HeartRateRecord.user_id == user.id)
            .order_by(HeartRateRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_analytics(db: Session, user: User, days: int = 7) -> dict:
        cutoff = _utcnow() - timedelta(days=days)
        records = (
            db.query(HeartRateRecord)
            .filter(HeartRateRecord.user_id == user.id, HeartRateRecord.created_at >= cutoff)
            .order_by(HeartRateRecord.created_at.desc())
            .all()
        )
        if not records:
            return {
                "period_days": days,
                "total_records": 0,
                "avg_resting_hr": 0,
                "avg_hrv": 0.0,
                "avg_vo2_max": None,
                "min_resting_hr": 0,
                "max_recorded_hr": 0,
                "zone_distribution": {},
                "trend": "insufficient_data",
                "daily": [],
            }

        avg_resting = round(sum(r.resting_hr for r in records) / len(records))
        hrvs = [r.hrv_rmssd for r in records if r.hrv_rmssd is not None]
        avg_hrv = round(sum(hrvs) / len(hrvs), 1) if hrvs else 0.0
        vo2s = [r.vo2_max for r in records if r.vo2_max is not None]
        avg_vo2 = round(sum(vo2s) / len(vo2s), 1) if vo2s else None

        total_z1 = sum(r.hr_zone_1_mins for r in records)
        total_z2 = sum(r.hr_zone_2_mins for r in records)
        total_z3 = sum(r.hr_zone_3_mins for r in records)
        total_z4 = sum(r.hr_zone_4_mins for r in records)
        total_z5 = sum(r.hr_zone_5_mins for r in records)

        resting_list = [r.resting_hr for r in records]
        mid = len(records) // 2
        if mid > 0:
            first_avg = sum(r.resting_hr for r in records[:mid]) / mid
            second_avg = sum(r.resting_hr for r in records[mid:]) / (len(records) - mid)
            trend = "improving" if first_avg < second_avg else ("declining" if first_avg > second_avg else "stable")
        else:
            trend = "stable"

        daily = [
            {
                "date": r.created_at.strftime("%Y-%m-%d"),
                "current_hr": r.current_hr,
                "resting_hr": r.resting_hr,
                "max_hr": r.max_hr,
                "hrv": r.hrv_rmssd,
                "vo2_max": r.vo2_max,
            }
            for r in records
        ]

        return {
            "period_days": days,
            "total_records": len(records),
            "avg_resting_hr": avg_resting,
            "avg_hrv": avg_hrv,
            "avg_vo2_max": avg_vo2,
            "min_resting_hr": min(resting_list),
            "max_recorded_hr": max(r.max_hr for r in records),
            "zone_distribution": {
                "zone_1_recovery": total_z1,
                "zone_2_fat_burn": total_z2,
                "zone_3_aerobic": total_z3,
                "zone_4_anaerobic": total_z4,
                "zone_5_max_effort": total_z5,
            },
            "trend": trend,
            "daily": daily,
        }


# ---------------------------------------------------------------------------
# Recovery Score
# ---------------------------------------------------------------------------

class RecoveryService:
    """Compute a holistic recovery score (0-100) from sleep, HR, HRV data."""

    @staticmethod
    def compute_score(db: Session, user: User) -> dict:
        now = _utcnow()
        yesterday = now - timedelta(hours=24)

        # Latest sleep
        sleep = (
            db.query(SleepRecord)
            .filter(SleepRecord.user_id == user.id, SleepRecord.created_at >= yesterday)
            .order_by(SleepRecord.created_at.desc())
            .first()
        )

        # Latest HR
        hr = (
            db.query(HeartRateRecord)
            .filter(HeartRateRecord.user_id == user.id, HeartRateRecord.created_at >= yesterday)
            .order_by(HeartRateRecord.created_at.desc())
            .first()
        )

        # Sub-scores
        sleep_sub = 50  # default
        if sleep:
            duration_score = min(sleep.duration_hours / 8.0, 1.0) * 40
            quality_score = (sleep.sleep_score / 100.0) * 30
            deep_score = min(sleep.deep_sleep_hours / 2.0, 1.0) * 30
            sleep_sub = round(duration_score + quality_score + deep_score)

        hr_sub = 50
        if hr:
            # Lower resting HR is better (40bpm ideal athlete, 100 very unfit)
            resting_score = max(0, min(40, 100 - hr.resting_hr)) / 40 * 50
            hrv_score = 0
            if hr.hrv_rmssd is not None:
                hrv_score = min(hr.hrv_rmssd / 80.0, 1.0) * 50
            else:
                hrv_score = 25  # neutral if no HRV data
            hr_sub = round(resting_score + hrv_score)

        recovery_score = round(sleep_sub * 0.6 + hr_sub * 0.4)
        recovery_score = max(0, min(100, recovery_score))

        if recovery_score >= 80:
            status_label = "Excellent"
            recommendation = "You're fully recovered. Great day for high-intensity training!"
        elif recovery_score >= 60:
            status_label = "Good"
            recommendation = "Recovery is solid. Moderate to high intensity workouts are appropriate."
        elif recovery_score >= 40:
            status_label = "Moderate"
            recommendation = "Consider lighter activity today. Focus on mobility or low-intensity cardio."
        else:
            status_label = "Low"
            recommendation = "Rest and recovery recommended. Focus on sleep, hydration, and stretching."

        return {
            "recovery_score": recovery_score,
            "status": status_label,
            "recommendation": recommendation,
            "components": {
                "sleep_score": sleep_sub,
                "cardiovascular_score": hr_sub,
                "sleep_weight": 0.6,
                "hr_weight": 0.4,
            },
            "latest_sleep": {
                "duration": sleep.duration_hours if sleep else None,
                "score": sleep.sleep_score if sleep else None,
                "deep_sleep": sleep.deep_sleep_hours if sleep else None,
            },
            "latest_hr": {
                "resting_hr": hr.resting_hr if hr else None,
                "hrv": hr.hrv_rmssd if hr else None,
                "vo2_max": hr.vo2_max if hr else None,
            },
            "computed_at": now,
        }


# ---------------------------------------------------------------------------
# Personal Records
# ---------------------------------------------------------------------------

class PersonalRecordService:
    """Track lifetime athletic personal records."""

    @staticmethod
    def add_record(
        db: Session, user: User,
        record_type: str,
        record_name: str,
        value: float,
        unit: str,
        notes: Optional[str] = None,
    ) -> PersonalRecord:
        # Check if this beats an existing record of the same type
        existing = (
            db.query(PersonalRecord)
            .filter(
                PersonalRecord.user_id == user.id,
                PersonalRecord.record_type == record_type,
            )
            .order_by(PersonalRecord.value.desc())
            .first()
        )

        record = PersonalRecord(
            user_id=user.id,
            record_type=record_type,
            record_name=record_name,
            value=value,
            unit=unit,
            notes=notes,
            achieved_at=_utcnow(),
        )
        try:
            db.add(record)
            db.commit()
            db.refresh(record)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to add personal record for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save personal record",
            ) from exc

        is_new_pr = existing is None or value > existing.value
        return record

    @staticmethod
    def get_all(db: Session, user: User) -> List[PersonalRecord]:
        return (
            db.query(PersonalRecord)
            .filter(PersonalRecord.user_id == user.id)
            .order_by(PersonalRecord.achieved_at.desc())
            .all()
        )

    @staticmethod
    def get_best_per_type(db: Session, user: User) -> List[dict]:
        """Return the best record per type."""
        all_records = (
            db.query(PersonalRecord)
            .filter(PersonalRecord.user_id == user.id)
            .all()
        )
        best: Dict[str, PersonalRecord] = {}
        for r in all_records:
            if r.record_type not in best or r.value > best[r.record_type].value:
                best[r.record_type] = r
        return [
            {
                "record_type": r.record_type,
                "record_name": r.record_name,
                "value": r.value,
                "unit": r.unit,
                "achieved_at": r.achieved_at.isoformat() if r.achieved_at else None,
            }
            for r in best.values()
        ]


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationService:
    """Manage proactive user notifications."""

    @staticmethod
    def create(
        db: Session, user: User,
        type: str, title: str, message: str,
        priority: str = "medium",
        action_url: Optional[str] = None,
    ) -> Notification:
        notif = Notification(
            user_id=user.id,
            type=type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
        )
        try:
            db.add(notif)
            db.commit()
            db.refresh(notif)
        except Exception as exc:
            db.rollback()
            logger.exception("Failed to create notification for user_id=%s", user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create notification",
            ) from exc
        return notif

    @staticmethod
    def get_unread(db: Session, user: User, limit: int = 20) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user.id, Notification.is_read == False)  # noqa: E712
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_all(db: Session, user: User, limit: int = 50) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_read(db: Session, user: User, notification_id: int) -> Notification:
        notif = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user.id)
            .first()
        )
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif.is_read = True
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_read(db: Session, user: User) -> int:
        count = (
            db.query(Notification)
            .filter(Notification.user_id == user.id, Notification.is_read == False)  # noqa: E712
            .update({"is_read": True})
        )
        db.commit()
        return count

    @staticmethod
    def get_unread_count(db: Session, user: User) -> int:
        return (
            db.query(func.count(Notification.id))
            .filter(Notification.user_id == user.id, Notification.is_read == False)  # noqa: E712
            .scalar()
        )
