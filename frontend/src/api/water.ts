import api from './client';
import type { WaterCreate, WaterResponse } from '../types';

export const waterApi = {
  add: (data: WaterCreate) =>
    api.post<WaterResponse>('/water', data).then(r => r.data),

  getHistory: (limit = 50) =>
    api.get<WaterResponse[]>('/water/history', { params: { limit } }).then(r => r.data),
};
