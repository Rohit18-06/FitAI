import api from './client';
import type { DietPlanCreate, DietPlanResponse } from '../types';

export const dietApi = {
  generate: (data: DietPlanCreate) =>
    api.post<DietPlanResponse>('/diet/generate', data).then(r => r.data),

  getActive: () =>
    api.get<DietPlanResponse | null>('/diet/active').then(r => r.data),

  getHistory: (limit = 10) =>
    api.get<DietPlanResponse[]>('/diet/history', { params: { limit } }).then(r => r.data),

  activate: (planId: number) =>
    api.put<DietPlanResponse>(`/diet/${planId}/activate`).then(r => r.data),
};
