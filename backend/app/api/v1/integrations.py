"""
Phase 6 – Wearables & Real-Time Health Intelligence API routes.

Endpoints:
  POST   /api/v1/integrations/devices/connect        – Connect a wearable device
  POST   /api/v1/integrations/devices/{id}/disconnect – Disconnect a device
  GET    /api/v1/integrations/devices                 – List connected devices
  GET    /api/v1/integrations/status                  – Health Connect status
  POST   /api/v1/integrations/sync                    – Sync Health Connect payload

  POST   /api/v1/integrations/sleep                   – Log sleep record
  GET    /api/v1/integrations/sleep/history            – Sleep history
  GET    /api/v1/integrations/sleep/analytics          – Sleep analytics

  POST   /api/v1/integrations/heart-rate              – Log heart rate
  GET    /api/v1/integrations/heart-rate/history        – HR history
  GET    /api/v1/integrations/heart-rate/analytics      – HR analytics

  GET    /api/v1/integrations/recovery                – Recovery score

  POST   /api/v1/integrations/records                 – Add personal record
  GET    /api/v1/integrations/records                 – List personal records
  GET    /api/v1/integrations/records/best            – Best per type

  GET    /api/v1/integrations/notifications           – All notifications
  GET    /api/v1/integrations/notifications/unread    – Unread notifications
  GET    /api/v1/integrations/notifications/count     – Unread count
  POST   /api/v1/integrations/notifications           – Create notification
  PUT    /api/v1/integrations/notifications/{id}/read – Mark one read
  PUT    /api/v1/integrations/notifications/read-all  – Mark all read
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.database import get_db
from app.models.user import User

from app.schemas.wearable import (
    WearableConnectRequest,
    WearableDeviceResponse,
    HealthConnectSyncPayload,
    HealthConnectSyncResponse,
    HealthConnectStatusResponse,
)
from app.schemas.phase6 import (
    SleepCreate,
    SleepResponse,
    HeartRateCreate,
    HeartRateResponse,
    RecoveryResponse,
    PersonalRecordCreate,
    PersonalRecordResponse,
    NotificationCreate,
    NotificationResponse,
)
from app.services.wearable_service import (
    WearableDeviceService,
    HealthConnectSyncService,
    SleepService,
    HeartRateService,
    RecoveryService,
    PersonalRecordService,
    NotificationService,
)

router = APIRouter(prefix="/integrations", tags=["Wearables & Integrations"])


# ═══════════════════════════════════════════════════════════════════════
# DEVICES
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/devices/connect",
    response_model=WearableDeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect a wearable device",
)
def connect_device(
    data: WearableConnectRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WearableDeviceResponse:
    device = WearableDeviceService.connect_device(db, current_user, data)
    return WearableDeviceResponse.model_validate(device)


@router.post(
    "/devices/{device_id}/disconnect",
    response_model=WearableDeviceResponse,
    summary="Disconnect a wearable device",
)
def disconnect_device(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WearableDeviceResponse:
    device = WearableDeviceService.disconnect_device(db, current_user, device_id)
    return WearableDeviceResponse.model_validate(device)


@router.get(
    "/devices",
    response_model=List[WearableDeviceResponse],
    summary="List connected wearable devices",
)
def list_devices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[WearableDeviceResponse]:
    devices = WearableDeviceService.get_devices(db, current_user)
    return [WearableDeviceResponse.model_validate(d) for d in devices]


@router.get(
    "/status",
    response_model=HealthConnectStatusResponse,
    summary="Health Connect integration status",
)
def get_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> HealthConnectStatusResponse:
    return HealthConnectStatusResponse(**WearableDeviceService.get_status(db, current_user))


# ═══════════════════════════════════════════════════════════════════════
# HEALTH CONNECT SYNC
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/sync",
    response_model=HealthConnectSyncResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sync data from Health Connect / Google Fit / Apple Health",
)
def sync_health_data(
    payload: HealthConnectSyncPayload,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> HealthConnectSyncResponse:
    result = HealthConnectSyncService.sync(db, current_user, payload)
    return HealthConnectSyncResponse(**result)


# ═══════════════════════════════════════════════════════════════════════
# SLEEP
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/sleep",
    response_model=SleepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a sleep record",
)
def log_sleep(
    data: SleepCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SleepResponse:
    record = SleepService.log_sleep(
        db, current_user,
        duration_hours=data.duration_hours,
        deep_sleep_hours=data.deep_sleep_hours,
        rem_sleep_hours=data.rem_sleep_hours,
        sleep_score=data.sleep_score,
        bed_time=data.bed_time,
        wake_time=data.wake_time,
    )
    return SleepResponse.model_validate(record)


@router.get(
    "/sleep/history",
    response_model=List[SleepResponse],
    summary="Get sleep history",
)
def get_sleep_history(
    limit: int = Query(default=30, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[SleepResponse]:
    records = SleepService.get_history(db, current_user, limit=limit)
    return [SleepResponse.model_validate(r) for r in records]


@router.get(
    "/sleep/analytics",
    summary="Get sleep analytics",
)
def get_sleep_analytics(
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    return SleepService.get_analytics(db, current_user, days=days)


# ═══════════════════════════════════════════════════════════════════════
# HEART RATE
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/heart-rate",
    response_model=HeartRateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a heart rate reading",
)
def log_heart_rate(
    data: HeartRateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> HeartRateResponse:
    zone_mins = {
        1: data.zone_1_mins, 2: data.zone_2_mins, 3: data.zone_3_mins,
        4: data.zone_4_mins, 5: data.zone_5_mins,
    }
    record = HeartRateService.log_heart_rate(
        db, current_user,
        current_hr=data.current_hr,
        resting_hr=data.resting_hr,
        max_hr=data.max_hr,
        hrv_rmssd=data.hrv_rmssd,
        vo2_max=data.vo2_max,
        zone_mins=zone_mins,
    )
    return HeartRateResponse.model_validate(record)


@router.get(
    "/heart-rate/history",
    response_model=List[HeartRateResponse],
    summary="Get heart rate history",
)
def get_hr_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[HeartRateResponse]:
    records = HeartRateService.get_history(db, current_user, limit=limit)
    return [HeartRateResponse.model_validate(r) for r in records]


@router.get(
    "/heart-rate/analytics",
    summary="Get heart rate analytics",
)
def get_hr_analytics(
    days: int = Query(default=7, ge=1, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    return HeartRateService.get_analytics(db, current_user, days=days)


# ═══════════════════════════════════════════════════════════════════════
# RECOVERY
# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/recovery",
    response_model=RecoveryResponse,
    summary="Get recovery score",
)
def get_recovery(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RecoveryResponse:
    result = RecoveryService.compute_score(db, current_user)
    return RecoveryResponse(**result)


# ═══════════════════════════════════════════════════════════════════════
# PERSONAL RECORDS
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/records",
    response_model=PersonalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a personal record",
)
def add_personal_record(
    data: PersonalRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> PersonalRecordResponse:
    record = PersonalRecordService.add_record(
        db, current_user,
        record_type=data.record_type,
        record_name=data.record_name,
        value=data.value,
        unit=data.unit,
        notes=data.notes,
    )
    return PersonalRecordResponse.model_validate(record)


@router.get(
    "/records",
    response_model=List[PersonalRecordResponse],
    summary="List all personal records",
)
def list_personal_records(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[PersonalRecordResponse]:
    records = PersonalRecordService.get_all(db, current_user)
    return [PersonalRecordResponse.model_validate(r) for r in records]


@router.get(
    "/records/best",
    summary="Get best personal record per type",
)
def get_best_records(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[dict]:
    return PersonalRecordService.get_best_per_type(db, current_user)


# ═══════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════

@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification",
)
def create_notification(
    data: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    notif = NotificationService.create(
        db, current_user,
        type=data.type,
        title=data.title,
        message=data.message,
        priority=data.priority,
        action_url=data.action_url,
    )
    return NotificationResponse.model_validate(notif)


@router.get(
    "/notifications",
    response_model=List[NotificationResponse],
    summary="List all notifications",
)
def list_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[NotificationResponse]:
    notifs = NotificationService.get_all(db, current_user, limit=limit)
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.get(
    "/notifications/unread",
    response_model=List[NotificationResponse],
    summary="List unread notifications",
)
def list_unread_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[NotificationResponse]:
    notifs = NotificationService.get_unread(db, current_user, limit=limit)
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.get(
    "/notifications/count",
    summary="Get unread notification count",
)
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    count = NotificationService.get_unread_count(db, current_user)
    return {"unread_count": count}


@router.put(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    notif = NotificationService.mark_read(db, current_user, notification_id)
    return NotificationResponse.model_validate(notif)


@router.put(
    "/notifications/read-all",
    summary="Mark all notifications as read",
)
def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    count = NotificationService.mark_all_read(db, current_user)
    return {"marked_read": count}
