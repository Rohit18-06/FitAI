import api from './client';
import type { WorkoutPlanCreate, WorkoutPlanResponse } from '../types';

export const workoutPlansApi = {
  generate: (data: WorkoutPlanCreate) =>
    api.post<WorkoutPlanResponse>('/workout-plans/generate', data).then(r => r.data),

  getActive: () =>
    api.get<WorkoutPlanResponse | null>('/workout-plans/active').then(r => r.data),

  getHistory: (limit = 10) =>
    api.get<WorkoutPlanResponse[]>('/workout-plans/history', { params: { limit } }).then(r => r.data),
};
