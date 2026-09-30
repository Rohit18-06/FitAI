import api from './client';
import type { DashboardOverviewResponse } from '../types';

export const dashboardApi = {
  getOverview: () =>
    api.get<DashboardOverviewResponse>('/dashboard').then(r => r.data),
};
