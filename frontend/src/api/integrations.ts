// ============================================================
// FitAI – Integrations & Wearables API Client
// Endpoints for Devices, Health Connect Sync, Sleep, HR,
// Recovery, Personal Records, and Notifications
// ============================================================
import api from './client';
import type {
  WearableDeviceResponse,
  WearableConnectRequest,
  HealthConnectStatusResponse,
  HealthConnectSyncPayload,
  HealthConnectSyncResponse,
  SleepCreate,
  SleepResponse,
  HeartRateCreate,
  HeartRateResponse,
  RecoveryResponse,
  PersonalRecordCreate,
  PersonalRecordResponse,
  NotificationCreate,
  NotificationResponse,
} from '../types';

export const integrationsApi = {
  // ── Wearable Devices ──────────────────────────────────────────
  async connectDevice(data: WearableConnectRequest): Promise<WearableDeviceResponse> {
    const res = await api.post<WearableDeviceResponse>('/integrations/devices/connect', data);
    return res.data;
  },

  async disconnectDevice(deviceId: number): Promise<WearableDeviceResponse> {
    const res = await api.post<WearableDeviceResponse>(`/integrations/devices/${deviceId}/disconnect`);
    return res.data;
  },

  async listDevices(): Promise<WearableDeviceResponse[]> {
    const res = await api.get<WearableDeviceResponse[]>('/integrations/devices');
    return res.data;
  },

  async getHealthConnectStatus(): Promise<HealthConnectStatusResponse> {
    const res = await api.get<HealthConnectStatusResponse>('/integrations/status');
    return res.data;
  },

  async syncHealthData(payload: HealthConnectSyncPayload): Promise<HealthConnectSyncResponse> {
    const res = await api.post<HealthConnectSyncResponse>('/integrations/sync', payload);
    return res.data;
  },

  // ── Sleep ─────────────────────────────────────────────────────
  async logSleep(data: SleepCreate): Promise<SleepResponse> {
    const res = await api.post<SleepResponse>('/integrations/sleep', data);
    return res.data;
  },

  async getSleepHistory(limit = 30): Promise<SleepResponse[]> {
    const res = await api.get<SleepResponse[]>('/integrations/sleep/history', { params: { limit } });
    return res.data;
  },

  async getSleepAnalytics(days = 7): Promise<any> {
    const res = await api.get('/integrations/sleep/analytics', { params: { days } });
    return res.data;
  },

  // ── Heart Rate ────────────────────────────────────────────────
  async logHeartRate(data: HeartRateCreate): Promise<HeartRateResponse> {
    const res = await api.post<HeartRateResponse>('/integrations/heart-rate', data);
    return res.data;
  },

  async getHeartRateHistory(limit = 50): Promise<HeartRateResponse[]> {
    const res = await api.get<HeartRateResponse[]>('/integrations/heart-rate/history', { params: { limit } });
    return res.data;
  },

  async getHeartRateAnalytics(days = 7): Promise<any> {
    const res = await api.get('/integrations/heart-rate/analytics', { params: { days } });
    return res.data;
  },

  // ── Recovery ──────────────────────────────────────────────────
  async getRecoveryScore(): Promise<RecoveryResponse> {
    const res = await api.get<RecoveryResponse>('/integrations/recovery');
    return res.data;
  },

  // ── Personal Records ──────────────────────────────────────────
  async addPersonalRecord(data: PersonalRecordCreate): Promise<PersonalRecordResponse> {
    const res = await api.post<PersonalRecordResponse>('/integrations/records', data);
    return res.data;
  },

  async listPersonalRecords(): Promise<PersonalRecordResponse[]> {
    const res = await api.get<PersonalRecordResponse[]>('/integrations/records');
    return res.data;
  },

  async getBestRecords(): Promise<any[]> {
    const res = await api.get<any[]>('/integrations/records/best');
    return res.data;
  },

  // ── Notifications ─────────────────────────────────────────────
  async createNotification(data: NotificationCreate): Promise<NotificationResponse> {
    const res = await api.post<NotificationResponse>('/integrations/notifications', data);
    return res.data;
  },

  async listNotifications(limit = 50): Promise<NotificationResponse[]> {
    const res = await api.get<NotificationResponse[]>('/integrations/notifications', { params: { limit } });
    return res.data;
  },

  async listUnreadNotifications(limit = 20): Promise<NotificationResponse[]> {
    const res = await api.get<NotificationResponse[]>('/integrations/notifications/unread', { params: { limit } });
    return res.data;
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    const res = await api.get<{ unread_count: number }>('/integrations/notifications/count');
    return res.data;
  },

  async markNotificationRead(id: number): Promise<NotificationResponse> {
    const res = await api.put<NotificationResponse>(`/integrations/notifications/${id}/read`);
    return res.data;
  },

  async markAllNotificationsRead(): Promise<{ marked_read: number }> {
    const res = await api.put<{ marked_read: number }>('/integrations/notifications/read-all');
    return res.data;
  },
};
