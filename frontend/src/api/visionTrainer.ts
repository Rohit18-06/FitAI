// ============================================================
// FitAI – AI Computer Vision Coaching 2.0 API Client
// Endpoints for Real-Time Pose Analysis, Live Coaching Sessions,
// Movement Library, Workout Automation, Adaptive Plans & Analytics
// ============================================================
import api from './client';
import type {
  PoseAnalyzeRequest,
  PoseAnalyzeResponse,
  LiveCoachSessionCreate,
  LiveCoachSessionResponse,
  MovementItemResponse,
  WorkoutAutomationRequest,
  WorkoutAutomationResponse,
  AdaptivePlanRequest,
  AdaptivePlanResponse,
  TrainerAnalyticsResponse,
} from '../types';

export const visionTrainerApi = {
  // ── Real-Time Pose Estimation & Movement Feedback ─────────────
  async analyzePose(data: PoseAnalyzeRequest): Promise<PoseAnalyzeResponse> {
    const res = await api.post<PoseAnalyzeResponse>('/pose/analyze', data);
    return res.data;
  },

  // ── Live AI Coach Session ─────────────────────────────────────
  async startLiveSession(data: LiveCoachSessionCreate): Promise<LiveCoachSessionResponse> {
    const res = await api.post<LiveCoachSessionResponse>('/live-coach/session', data);
    return res.data;
  },

  async getActiveSession(): Promise<LiveCoachSessionResponse | null> {
    const res = await api.get<LiveCoachSessionResponse | null>('/live-coach/session/active');
    return res.data;
  },

  async completeLiveSession(sessionId: number): Promise<LiveCoachSessionResponse> {
    const res = await api.post<LiveCoachSessionResponse>(`/live-coach/session/${sessionId}/complete`);
    return res.data;
  },

  // ── Adaptive Training System ──────────────────────────────────
  async generateAdaptivePlan(data: AdaptivePlanRequest): Promise<AdaptivePlanResponse> {
    const res = await api.post<AdaptivePlanResponse>('/adaptive-training/plan', data);
    return res.data;
  },

  // ── Smart Workout Automation ──────────────────────────────────
  async generateAutomatedWorkout(data: WorkoutAutomationRequest): Promise<WorkoutAutomationResponse> {
    const res = await api.post<WorkoutAutomationResponse>('/workout-automation/generate', data);
    return res.data;
  },

  // ── Movement Library (100+ Exercises) ─────────────────────────
  async listMovementLibrary(params?: {
    category?: string;
    difficulty?: string;
    search?: string;
    limit?: number;
  }): Promise<MovementItemResponse[]> {
    const res = await api.get<MovementItemResponse[]>('/movement-library', { params });
    return res.data;
  },

  async getMovementDetail(exerciseId: number): Promise<MovementItemResponse> {
    const res = await api.get<MovementItemResponse>(`/movement-library/${exerciseId}`);
    return res.data;
  },

  async seedMovementLibrary(): Promise<{ success: boolean; total_exercises: number }> {
    const res = await api.post<{ success: boolean; total_exercises: number }>('/movement-library/seed');
    return res.data;
  },

  // ── Studio Analytics ──────────────────────────────────────────
  async getStudioAnalytics(): Promise<TrainerAnalyticsResponse> {
    const res = await api.get<TrainerAnalyticsResponse>('/trainer/analytics');
    return res.data;
  },
};
