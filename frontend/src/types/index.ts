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

