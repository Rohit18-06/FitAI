import api from './client';
import type { BMICreate, BMIResponse } from '../types';

export const bmiApi = {
  calculate: (data: BMICreate) =>
    api.post<BMIResponse>('/bmi/calculate', data).then(r => r.data),

  getHistory: (limit = 50) =>
    api.get<BMIResponse[]>('/bmi/history', { params: { limit } }).then(r => r.data),
};
