import api from './client';
import type {
  CoachChatResponse,
  ConversationHistoryResponse,
  CoachSidebarStats,
} from '../types';

export const coachApi = {
  chat: (message: string) =>
    api.post<CoachChatResponse>('/coach/chat', { message }).then(r => r.data),

  getHistory: (limit = 30, offset = 0) =>
    api
      .get<ConversationHistoryResponse>('/coach/history', {
        params: { limit, offset },
      })
      .then(r => r.data),

  clearHistory: () =>
    api.delete<{ message: string; deleted_count: number }>('/coach/history').then(r => r.data),

  getSidebarStats: () =>
    api.get<CoachSidebarStats>('/coach/stats').then(r => r.data),
};
