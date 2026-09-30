// ============================================================
// FitAI – AI Personal Trainer & Smart Coaching API Client
// Endpoints for Training Programs, Progressions, Recovery,
// Plateaus, Injury Risk, Measurements, Goals, and Weekly Reports
// ============================================================
import api from './client';
import type {
  TrainingProgramCreate,
  TrainingProgramResponse,
  ExerciseProgressionCreate,
  ExerciseProgressionResponse,
  RecoveryAssessmentResponse,
  PlateauReport,
  InjuryRiskResponse,
  BodyMeasurementCreate,
  BodyMeasurementResponse,
  ProgressPhotoCreate,
  ProgressPhotoResponse,
  GoalCreate,
  GoalResponse,
  WeeklyReportResponse,
} from '../types';

export const trainingApi = {
  // ── Training Programs ─────────────────────────────────────────
  async generateProgram(data: TrainingProgramCreate): Promise<TrainingProgramResponse> {
    const res = await api.post<TrainingProgramResponse>('/training-programs', data);
    return res.data;
  },

  async listPrograms(): Promise<TrainingProgramResponse[]> {
    const res = await api.get<TrainingProgramResponse[]>('/training-programs');
    return res.data;
  },

  async getActiveProgram(): Promise<TrainingProgramResponse | null> {
    const res = await api.get<TrainingProgramResponse | null>('/training-programs/active');
    return res.data;
  },

  async completeDay(day_id: number): Promise<{ success: boolean; day_id: number; completed: boolean }> {
    const res = await api.post<{ success: boolean; day_id: number; completed: boolean }>('/training-programs/complete-day', { day_id });
    return res.data;
  },

  // ── Exercise Progressions ─────────────────────────────────────
  async logProgression(data: ExerciseProgressionCreate): Promise<ExerciseProgressionResponse> {
    const res = await api.post<ExerciseProgressionResponse>('/progressions', data);
    return res.data;
  },

  async getProgressions(exercise_name?: string): Promise<ExerciseProgressionResponse[]> {
    const params = exercise_name ? { exercise_name } : undefined;
    const res = await api.get<ExerciseProgressionResponse[]>('/progressions', { params });
    return res.data;
  },

  // ── Recovery Assessment ───────────────────────────────────────
  async computeRecovery(): Promise<RecoveryAssessmentResponse> {
    const res = await api.post<RecoveryAssessmentResponse>('/recovery-assessment/compute');
    return res.data;
  },

  async getLatestRecovery(): Promise<RecoveryAssessmentResponse | null> {
    const res = await api.get<RecoveryAssessmentResponse | null>('/recovery-assessment/latest');
    return res.data;
  },

  // ── Plateau Detection ─────────────────────────────────────────
  async detectPlateaus(): Promise<PlateauReport[]> {
    const res = await api.get<PlateauReport[]>('/plateaus');
    return res.data;
  },

  // ── Injury Risk Engine ────────────────────────────────────────
  async assessInjuryRisk(): Promise<InjuryRiskResponse> {
    const res = await api.post<InjuryRiskResponse>('/injury-risk/assess');
    return res.data;
  },

  async getLatestInjuryRisk(): Promise<InjuryRiskResponse | null> {
    const res = await api.get<InjuryRiskResponse | null>('/injury-risk/latest');
    return res.data;
  },

  // ── Body Measurements ─────────────────────────────────────────
  async addMeasurement(data: BodyMeasurementCreate): Promise<BodyMeasurementResponse> {
    const res = await api.post<BodyMeasurementResponse>('/measurements', data);
    return res.data;
  },

  async listMeasurements(limit = 30): Promise<BodyMeasurementResponse[]> {
    const res = await api.get<BodyMeasurementResponse[]>('/measurements', { params: { limit } });
    return res.data;
  },

  async getLatestMeasurement(): Promise<BodyMeasurementResponse | null> {
    const res = await api.get<BodyMeasurementResponse | null>('/measurements/latest');
    return res.data;
  },

  // ── Progress Photos ───────────────────────────────────────────
  async addProgressPhoto(data: ProgressPhotoCreate): Promise<ProgressPhotoResponse> {
    const res = await api.post<ProgressPhotoResponse>('/progress-photos', data);
    return res.data;
  },

  async listProgressPhotos(limit = 30): Promise<ProgressPhotoResponse[]> {
    const res = await api.get<ProgressPhotoResponse[]>('/progress-photos', { params: { limit } });
    return res.data;
  },

  // ── Goals ─────────────────────────────────────────────────────
  async createGoal(data: GoalCreate): Promise<GoalResponse> {
    const res = await api.post<GoalResponse>('/goals', data);
    return res.data;
  },

  async listGoals(status?: string): Promise<GoalResponse[]> {
    const params = status ? { status } : undefined;
    const res = await api.get<GoalResponse[]>('/goals', { params });
    return res.data;
  },

  async getGoal(goalId: number): Promise<GoalResponse> {
    const res = await api.get<GoalResponse>(`/goals/${goalId}`);
    return res.data;
  },

  async updateGoalProgress(goalId: number, current_value: number): Promise<GoalResponse> {
    const res = await api.patch<GoalResponse>(`/goals/${goalId}/progress`, { current_value });
    return res.data;
  },

  // ── Weekly Coaching Reports ───────────────────────────────────
  async generateWeeklyReport(): Promise<WeeklyReportResponse> {
    const res = await api.post<WeeklyReportResponse>('/weekly-reports/generate');
    return res.data;
  },

  async listWeeklyReports(limit = 12): Promise<WeeklyReportResponse[]> {
    const res = await api.get<WeeklyReportResponse[]>('/weekly-reports', { params: { limit } });
    return res.data;
  },
};
