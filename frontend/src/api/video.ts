import api from './client';
import type { FormAnalysisResponse } from '../types';

export const videoApi = {
  analyze: (exerciseName: string, file?: File) => {
    const formData = new FormData();
    formData.append('exercise_name', exerciseName);
    if (file) {
      formData.append('file', file);
    }
    return api.post<FormAnalysisResponse>('/video/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    }).then(r => r.data);
  },

  getHistory: (limit = 20) =>
    api.get<FormAnalysisResponse[]>('/video/history', { params: { limit } }).then(r => r.data),

  getById: (id: number) =>
    api.get<FormAnalysisResponse>(`/video/${id}`).then(r => r.data),
};
