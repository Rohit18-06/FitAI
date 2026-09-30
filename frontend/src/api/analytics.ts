import api from './client';
import type { AnalyticsOverviewResponse, MilestonesResponse } from '../types';

export const analyticsApi = {
  getOverview: (days = 30) =>
    api.get<AnalyticsOverviewResponse>('/analytics/overview', { params: { days } }).then(r => r.data),

  getMilestones: () =>
    api.get<MilestonesResponse>('/analytics/milestones').then(r => r.data),
};
