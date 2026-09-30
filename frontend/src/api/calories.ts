import api from './client';
import type { CalorieCreate, CalorieResponse } from '../types';

export const caloriesApi = {
  add: (data: CalorieCreate) =>
    api.post<CalorieResponse>('/calories', data).then(r => r.data),

  getHistory: (limit = 50) =>
    api.get<CalorieResponse[]>('/calories/history', { params: { limit } }).then(r => r.data),
};
