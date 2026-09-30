import api from './client';
import type { WorkoutCreate, WorkoutResponse } from '../types';

export const workoutsApi = {
  add: (data: WorkoutCreate) =>
    api.post<WorkoutResponse>('/workouts', data).then(r => r.data),

  getHistory: (limit = 50) =>
    api.get<WorkoutResponse[]>('/workouts/history', { params: { limit } }).then(r => r.data),
};
