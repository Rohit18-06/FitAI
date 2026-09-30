import api from './client';
import type { StepCreate, StepResponse } from '../types';

export const stepsApi = {
  add: (data: StepCreate) =>
    api.post<StepResponse>('/steps', data).then(r => r.data),

  getHistory: (limit = 50) =>
    api.get<StepResponse[]>('/steps/history', { params: { limit } }).then(r => r.data),
};
