// ============================================================
// FitAI – Complete TypeScript Type Definitions
// Mirrors all backend Pydantic v2 schemas
// ============================================================

// ── Auth ──────────────────────────────────────────────────────
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// ── BMI ───────────────────────────────────────────────────────
export interface BMICreate {
  height_cm: number;
  weight_kg: number;
}

export interface BMIResponse {
  id: number;
  user_id: number;
  height_cm: number;
  weight_kg: number;
  bmi: number;
  category: string;
  created_at: string;
}

// ── Calories ──────────────────────────────────────────────────
export interface CalorieCreate {
  meal_name: string;
  calories: number;
  protein?: number;
  carbs?: number;
  fats?: number;
}

export interface CalorieResponse {
  id: number;
  user_id: number;
  meal_name: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  created_at: string;
}

// ── Water ─────────────────────────────────────────────────────
export interface WaterCreate {
  glasses?: number;
  liters?: number;
}

export interface WaterResponse {
  id: number;
  user_id: number;
  glasses: number;
  liters: number;
  created_at: string;
}

// ── Steps ─────────────────────────────────────────────────────
export interface StepCreate {
  steps: number;
  distance_km?: number;
  calories_burned?: number;
}

export interface StepResponse {
  id: number;
  user_id: number;
  steps: number;
  distance_km: number;
  calories_burned: number;
  created_at: string;
}

// ── Workouts ──────────────────────────────────────────────────
export interface WorkoutCreate {
  workout_type: string;
  duration_minutes: number;
  calories_burned?: number;
  notes?: string;
}

export interface WorkoutResponse {
  id: number;
  user_id: number;
  workout_type: string;
  duration_minutes: number;
  calories_burned: number;
  notes: string | null;
  created_at: string;
}

// ── Diet Plan ─────────────────────────────────────────────────
export interface MealItem {
  food_name: string;
  serving_size: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fats_g: number;
  notes?: string | null;
}

export interface Meal {
  meal_type: string;
  name: string;
  target_calories: number;
  items: MealItem[];
  recipe_steps: string[];
}

export interface DietPlanCreate {
  fitness_goal?: string;
  dietary_preference?: string;
  target_calories?: number | null;
  allergies_or_restrictions?: string[];
  meals_per_day?: number;
}

export interface DietPlanResponse {
  id: number;
  user_id: number;
  title: string;
  fitness_goal: string;
  dietary_preference: string;
  target_calories: number;
  target_protein_g: number;
  target_carbs_g: number;
  target_fats_g: number;
  meals: Meal[];
  is_active: boolean;
  created_at: string;
}

// ── Workout Plan ──────────────────────────────────────────────
export interface ExerciseItem {
  name: string;
  target_muscle: string;
  sets: number;
  reps: string;
  rest_seconds: number;
  coaching_tips: string;
}

export interface DailyRoutine {
  day_number: number;
  day_name: string;
  focus: string;
  warmup: string[];
  exercises: ExerciseItem[];
  cooldown: string[];
}

export interface WorkoutPlanCreate {
  fitness_level?: string;
  fitness_goal?: string;
  days_per_week?: number;
  equipment?: string;
  focus_areas?: string[];
  injuries_or_limitations?: string[];
}

export interface WorkoutPlanResponse {
  id: number;
  user_id: number;
  title: string;
  fitness_level: string;
  fitness_goal: string;
  days_per_week: number;
  equipment: string;
  routines: DailyRoutine[];
  is_active: boolean;
  created_at: string;
}

// ── Form / Video Analysis ─────────────────────────────────────
export interface KeypointCheck {
  joint_or_segment: string;
  status: string;
  metric_or_angle: string | null;
  feedback: string;
}

export interface FormAnalysisResponse {
  id: number;
  user_id: number;
  exercise_name: string;
  video_filename: string | null;
  form_score: number;
  rep_count: number;
  posture_summary: string;
  keypoint_checks: KeypointCheck[];
  injury_risk_level: string;
  recommendations: string[];
  created_at: string;
}

// ── Health Insights ───────────────────────────────────────────
export interface HealthInsightResponse {
  id: number;
  user_id: number;
  category: string;
  title: string;
  content: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

// ── Dashboard ─────────────────────────────────────────────────
export interface TodayOverview {
  calories_consumed: number;
  calories_target: number;
  calories_remaining: number;
  water_liters: number;
  water_target_liters: number;
  steps_count: number;
  steps_target: number;
  workout_minutes: number;
  calories_burned: number;
}

export interface BMIStatus {
  current_bmi: number | null;
  category: string | null;
  weight_kg: number | null;
  height_cm: number | null;
}

export interface WeeklyAdherence {
  overall_score: number;
  workout_days_completed: number;
  target_workout_days: number;
  water_target_met_days: number;
  calorie_target_met_days: number;
}

export interface StreakStats {
  current_streak_days: number;
  longest_streak_days: number;
  total_active_days: number;
}

export interface DashboardOverviewResponse {
  user_id: number;
  username: string;
  today: TodayOverview;
  bmi_status: BMIStatus;
  weekly_adherence: WeeklyAdherence;
  streaks: StreakStats;
  active_diet_plan_title: string | null;
  active_workout_plan_title: string | null;
  recent_insights: HealthInsightResponse[];
}

// ── Analytics ─────────────────────────────────────────────────
export interface TrendDataPoint {
  date: string;
  calories_consumed: number;
  water_liters: number;
  steps: number;
  workout_minutes: number;
  calories_burned: number;
  weight_kg: number | null;
}

export interface TrendsSummary {
  avg_daily_calories: number;
  avg_daily_steps: number;
  avg_daily_water_liters: number;
  total_workout_minutes: number;
  total_calories_burned: number;
}

export interface ProgressTelemetry {
  start_weight_kg: number | null;
  current_weight_kg: number | null;
  weight_delta_kg: number;
  start_bmi: number | null;
  current_bmi: number | null;
  bmi_delta: number;
}

export interface AnalyticsOverviewResponse {
  user_id: number;
  period_days: number;
  summary: TrendsSummary;
  progress: ProgressTelemetry;
  daily_trends: TrendDataPoint[];
}

export interface MilestoneItem {
  id: string;
  category: string;
  title: string;
  description: string;
  achieved: boolean;
  achieved_date: string | null;
  progress_percentage: number;
  badge_icon: string;
}

export interface MilestonesResponse {
  total_milestones: number;
  achieved_count: number;
  milestones: MilestoneItem[];
}

// ── AI Fitness Coach ──────────────────────────────────────────
export interface CoachChatRequest {
  message: string;
}

export interface CoachChatResponse {
  id: number;
  message: string;
  response: string;
  sources: string[];
  tokens_used: number;
  created_at: string;
}

export interface CoachConversationItem {
  id: number;
  user_id: number;
  message: string;
  response: string;
  sources: string[];
  tokens_used: number;
  created_at: string;
}

export interface ConversationHistoryResponse {
  conversations: CoachConversationItem[];
  total: number;
}

export interface CoachSidebarStats {
  bmi: number | null;
  bmi_category: string | null;
  weight_kg: number | null;
  calories_today: number;
  calorie_target: number;
  water_liters_today: number;
  water_target: number;
  steps_today: number;
  step_target: number;
  workout_minutes_today: number;
  current_streak: number;
  active_diet_plan: string | null;
  active_workout_plan: string | null;
}

// ── Phase 6: Wearables & Health Intelligence ──────────────────
export interface WearableConnectRequest {
  provider: string;
  device_name: string;
  device_identifier?: string;
  battery_level?: number;
}

export interface WearableDeviceResponse {
  id: number;
  user_id: number;
  provider: string;
  device_name: string;
  device_identifier?: string | null;
  battery_level: number;
  is_connected: boolean;
  last_sync: string;
  created_at: string;
}

export interface HealthConnectSyncPayload {
  provider?: string;
  steps?: number;
  calories_burned?: number;
  distance_km?: number;
  active_minutes?: number;
  heart_rate?: number;
  resting_heart_rate?: number;
  hrv_rmssd?: number;
  sleep_duration_hours?: number;
  deep_sleep_hours?: number;
  rem_sleep_hours?: number;
  sleep_score?: number;
  weight_kg?: number;
  height_cm?: number;
  body_fat_pct?: number;
  vo2_max?: number;
}

export interface HealthConnectSyncResponse {
  synced: boolean;
  provider: string;
  records_updated: Record<string, any>;
  timestamp: string;
}

export interface HealthConnectStatusResponse {
  connected: boolean;
  active_devices_count: number;
  connected_providers: string[];
  last_sync: string | null;
  supported_providers: string[];
}

export interface SleepCreate {
  duration_hours: number;
  deep_sleep_hours?: number;
  rem_sleep_hours?: number;
  sleep_score?: number;
  bed_time?: string;
  wake_time?: string;
}

export interface SleepResponse {
  id: number;
  user_id: number;
  duration_hours: number;
  deep_sleep_hours: number;
  rem_sleep_hours: number;
  light_sleep_hours: number;
  sleep_score: number;
  bed_time: string;
  wake_time: string;
  created_at: string;
}

export interface HeartRateCreate {
  current_hr: number;
  resting_hr?: number;
  max_hr?: number;
  hrv_rmssd?: number;
  vo2_max?: number;
  zone_1_mins?: number;
  zone_2_mins?: number;
  zone_3_mins?: number;
  zone_4_mins?: number;
  zone_5_mins?: number;
}

export interface HeartRateResponse {
  id: number;
  user_id: number;
  current_hr: number;
  average_hr: number;
  resting_hr: number;
  max_hr: number;
  hrv_rmssd?: number | null;
  vo2_max?: number | null;
  hr_zone_1_mins: number;
  hr_zone_2_mins: number;
  hr_zone_3_mins: number;
  hr_zone_4_mins: number;
  hr_zone_5_mins: number;
  created_at: string;
}

export interface RecoveryResponse {
  recovery_score: number;
  status: string;
  recommendation: string;
  components: Record<string, any>;
  latest_sleep: Record<string, any>;
  latest_hr: Record<string, any>;
  computed_at: string;
}

export interface PersonalRecordCreate {
  record_type: string;
  record_name: string;
  value: number;
  unit: string;
  notes?: string;
}

export interface PersonalRecordResponse {
  id: number;
  user_id: number;
  record_type: string;
  record_name: string;
  value: number;
  unit: string;
  notes?: string | null;
  achieved_at: string;
  created_at: string;
}

export interface NotificationCreate {
  type: string;
  title: string;
  message: string;
  priority?: string;
  action_url?: string;
}

export interface NotificationResponse {
  id: number;
  user_id: number;
  type: string;
  title: string;
  message: string;
  priority: string;
  action_url?: string | null;
  is_read: boolean;
  created_at: string;
}

// ── Phase 7: Social Fitness Ecosystem ────────────────────────
export interface FriendshipResponse {
  id: number;
  requester_id: number;
  receiver_id: number;
  status: string;
  requester_username?: string | null;
  receiver_username?: string | null;
  friend_user_id?: number;
  friend_username?: string;
  friend_avatar?: string | null;
  friend_bio?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserSearchResponse {
  id: number;
  username: string;
  bio?: string | null;
  avatar?: string | null;
  level: number;
  is_friend: boolean;
  friend_status?: string | null;
  is_following: boolean;
}

export interface FollowResponse {
  id: number;
  follower_id: number;
  following_id: number;
  username: string;
  bio?: string | null;
  avatar?: string | null;
  created_at: string;
}

export interface ActivityFeedResponse {
  id: number;
  user_id: number;
  username: string;
  avatar?: string | null;
  activity_type: string;
  title: string;
  description?: string | null;
  metadata_json?: string | null;
  created_at: string;
}

export interface ChallengeCreate {
  title: string;
  description?: string;
  challenge_type: string;
  target_value: number;
  duration_days?: number;
  reward_xp?: number;
}

export interface ChallengeParticipantResponse {
  id: number;
  challenge_id: number;
  user_id: number;
  username?: string | null;
  progress: number;
  completed: boolean;
  joined_at: string;
}

export interface ChallengeResponse {
  id: number;
  title: string;
  description?: string | null;
  challenge_type: string;
  target_value: number;
  duration_days: number;
  reward_xp: number;
  created_by?: number | null;
  creator_username?: string | null;
  start_date: string;
  end_date: string;
  is_active: boolean;
  participants_count: number;
  my_progress?: number | null;
  is_joined: boolean;
  is_completed: boolean;
}

export interface UserLevelResponse {
  id: number;
  user_id: number;
  xp: number;
  level: number;
  total_workouts: number;
  total_steps: number;
  total_calories_burned: number;
  next_level_xp: number;
  progress_percent: number;
}

export interface BadgeResponse {
  id: number;
  name: string;
  description: string;
  icon: string;
  category: string;
  xp_reward: number;
  is_earned?: boolean;
  earned_at?: string | null;
}

export interface AchievementsOverviewResponse {
  total_badges: number;
  earned_count: number;
  badges: BadgeResponse[];
  user_level: UserLevelResponse;
}

export interface TeamCreate {
  name: string;
  description?: string;
}

export interface TeamMemberResponse {
  id: number;
  team_id: number;
  user_id: number;
  username: string;
  role: string;
  joined_at: string;
}

export interface TeamResponse {
  id: number;
  name: string;
  description?: string | null;
  owner_id: number;
  owner_username?: string | null;
  members_count: number;
  is_member: boolean;
  my_role?: string | null;
  created_at: string;
  members?: TeamMemberResponse[] | null;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  avatar?: string | null;
  value: number;
  unit: string;
  level: number;
}

export interface PublicProfileResponse {
  username: string;
  avatar?: string | null;
  bio?: string | null;
  level: number;
  xp: number;
  badges: BadgeResponse[];
  followers: number;
  following: number;
  current_streak: number;
  recovery_score: number;
  total_workouts: number;
  total_steps: number;
  is_following: boolean;
  is_friend: boolean;
}

// ═══════════════════════════════════════════════════════════════
// Phase 8: AI Personal Trainer & Smart Coaching Types
// ═══════════════════════════════════════════════════════════════

export interface ProgramDayExercise {
  name: string;
  sets: number;
  reps: string;
  rest_seconds: number;
  notes?: string | null;
}

export interface ProgramDayResponse {
  id: number;
  day_number: number;
  day_name: string;
  focus: string;
  exercises: ProgramDayExercise[];
  warmup: string[];
  cooldown: string[];
  estimated_duration_min: number;
  completed: boolean;
  completed_at?: string | null;
}

export interface ProgramWeekResponse {
  id: number;
  week_number: number;
  theme?: string | null;
  intensity_pct: number;
  volume_modifier: number;
  notes?: string | null;
  days: ProgramDayResponse[];
}

export interface TrainingProgramCreate {
  fitness_goal: string;
  fitness_level: string;
  duration_weeks: number;
  days_per_week: number;
}

export interface TrainingProgramResponse {
  id: number;
  user_id: number;
  title: string;
  description?: string | null;
  fitness_goal: string;
  fitness_level: string;
  duration_weeks: number;
  days_per_week: number;
  is_active: boolean;
  ai_notes?: string | null;
  weeks: ProgramWeekResponse[];
  created_at: string;
  updated_at: string;
}

export interface ExerciseProgressionCreate {
  exercise_name: string;
  weight_kg?: number;
  sets: number;
  reps: number;
  rpe?: number;
  notes?: string;
}

export interface ExerciseProgressionResponse {
  id: number;
  user_id: number;
  exercise_name: string;
  weight_kg?: number | null;
  sets: number;
  reps: number;
  rpe?: number | null;
  one_rep_max_est?: number | null;
  notes?: string | null;
  recorded_at: string;
}

export interface RecoveryAssessmentResponse {
  id: number;
  user_id: number;
  score: number;
  status: string;
  sleep_score?: number | null;
  hrv_score?: number | null;
  resting_hr_score?: number | null;
  workout_load_score?: number | null;
  recommendation?: string | null;
  components: Record<string, any>;
  computed_at: string;
}

export interface PlateauReport {
  detected: boolean;
  plateau_type?: string | null;
  duration_days: number;
  severity: string;
  recommendation?: string | null;
  data_points: Array<{ date: string; value: number }>;
}

export interface InjuryRiskFactor {
  factor: string;
  severity: string;
  detail: string;
}

export interface InjuryRiskResponse {
  id: number;
  user_id: number;
  risk_level: string;
  risk_score: number;
  factors: InjuryRiskFactor[];
  corrective_actions: string[];
  mobility_notes?: string | null;
  recommendation?: string | null;
  assessed_at: string;
}

export interface BodyMeasurementCreate {
  weight_kg?: number;
  body_fat_pct?: number;
  chest_cm?: number;
  waist_cm?: number;
  hips_cm?: number;
  neck_cm?: number;
  left_arm_cm?: number;
  right_arm_cm?: number;
  left_thigh_cm?: number;
  right_thigh_cm?: number;
  notes?: string;
}

export interface BodyMeasurementResponse {
  id: number;
  user_id: number;
  weight_kg?: number | null;
  body_fat_pct?: number | null;
  chest_cm?: number | null;
  waist_cm?: number | null;
  hips_cm?: number | null;
  neck_cm?: number | null;
  left_arm_cm?: number | null;
  right_arm_cm?: number | null;
  left_thigh_cm?: number | null;
  right_thigh_cm?: number | null;
  notes?: string | null;
  measured_at: string;
}

export interface ProgressPhotoCreate {
  photo_type: string;
  filename: string;
  file_path?: string;
  notes?: string;
}

export interface ProgressPhotoResponse {
  id: number;
  user_id: number;
  photo_type: string;
  filename: string;
  ai_analysis?: string | null;
  body_fat_estimate?: number | null;
  muscle_score?: number | null;
  notes?: string | null;
  taken_at: string;
}

export interface GoalCreate {
  goal_type: string;
  title: string;
  description?: string;
  target_value?: number;
  unit?: string;
  start_value?: number;
  target_date?: string;
}

export interface GoalResponse {
  id: number;
  user_id: number;
  goal_type: string;
  title: string;
  description?: string | null;
  target_value?: number | null;
  current_value: number;
  unit?: string | null;
  start_value?: number | null;
  completion_pct: number;
  status: string;
  target_date?: string | null;
  completed_at?: string | null;
  milestones: any[];
  created_at: string;
  updated_at: string;
}

export interface WeeklyReportResponse {
  id: number;
  user_id: number;
  week_start: string;
  week_end: string;
  training_summary?: string | null;
  recovery_summary?: string | null;
  nutrition_summary?: string | null;
  sleep_summary?: string | null;
  progress_score: number;
  highlights: string[];
  recommendations: string[];
  ai_coach_notes?: string | null;
  created_at: string;
}

// ═══════════════════════════════════════════════════════════════
// Phase 9: AI Computer Vision Coaching 2.0 Types
// ═══════════════════════════════════════════════════════════════

export interface Keypoint2D {
  x: number;
  y: number;
  z?: number;
  visibility?: number;
}

export interface PoseAnalyzeRequest {
  keypoints: Keypoint2D[];
  exercise_hint?: string;
  session_id?: number;
  frame_timestamp_ms?: number;
}

export interface PoseAnalyzeResponse {
  exercise: string;
  confidence: number;
  posture_score: number;
  rep_count: number;
  stage: string;
  joint_angles: Record<string, number>;
  mistakes: string[];
  corrections: string[];
  injury_risk: string;
  coach_cue: string;
  fps?: number;
}

export interface LiveCoachSessionCreate {
  exercise_name: string;
  target_reps?: number;
  target_sets?: number;
}

export interface LiveCoachSessionResponse {
  id: number;
  user_id: number;
  exercise_name: string;
  target_reps: number;
  target_sets: number;
  completed_reps: number;
  completed_sets: number;
  avg_form_score: number;
  avg_tempo?: number | null;
  injury_risk_level: string;
  status: string;
  feedback_history: string[];
  started_at: string;
  ended_at?: string | null;
}

export interface MovementItemResponse {
  id: number;
  name: string;
  slug: string;
  category: string;
  equipment: string;
  difficulty: string;
  primary_muscles: string[];
  secondary_muscles: string[];
  instructions: string[];
  common_mistakes: string[];
  coaching_cues: string[];
  demo_video_url?: string | null;
}

export interface WorkoutExerciseItem {
  name: string;
  target_sets: number;
  target_reps: string;
  rest_seconds: number;
  tempo: string;
  notes?: string | null;
}

export interface WorkoutRoutineBlock {
  block_name: string;
  estimated_duration_min: number;
  exercises: WorkoutExerciseItem[];
}

export interface WorkoutAutomationRequest {
  target_muscle?: string;
  intensity?: string;
  duration_minutes?: number;
}

export interface WorkoutAutomationResponse {
  session_title: string;
  total_duration_min: number;
  coaching_focus: string;
  flow: WorkoutRoutineBlock[];
}

export interface AdaptivePlanRequest {
  soreness_level?: string;
  fatigue_score?: number;
}

export interface AdaptivePlanResponse {
  recovery_score: number;
  adjustment_type: string;
  volume_multiplier: number;
  recommended_reps_delta: number;
  deload_recommended: boolean;
  recommendations: string[];
}

export interface TrainerAnalyticsResponse {
  total_sessions: number;
  total_reps_logged: number;
  overall_avg_form_score: number;
  form_score_history: Array<{
    date: string;
    exercise: string;
    score: number;
    reps: number;
  }>;
  volume_by_exercise: Record<string, number>;
  injury_risk_distribution: Record<string, number>;
}



