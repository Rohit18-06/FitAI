import api from './client';
import type { HealthInsightResponse } from '../types';

export const insightsApi = {
  generate: () =>
    api.post<HealthInsightResponse[]>('/insights/generate').then(r => r.data),

  getAll: (unreadOnly = false, limit = 15) =>
    api.get<HealthInsightResponse[]>('/insights', { params: { unread_only: unreadOnly, limit } }).then(r => r.data),

  markRead: (id: number) =>
    api.put<HealthInsightResponse>(`/insights/${id}/read`).then(r => r.data),
};
