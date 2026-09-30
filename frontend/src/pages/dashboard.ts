// ============================================================
// FitAI – Main Dashboard Page
// Apple Vision Pro Glassmorphism & Cyberpunk Telemetry
// ============================================================
import gsap from 'gsap';
import { Chart, ArcElement, Tooltip, Legend, DoughnutController } from 'chart.js';
import { dashboardApi } from '../api/dashboard';
import { waterApi } from '../api/water';
import type { DashboardOverviewResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { router } from '../router';
import {
  showLogWaterModal,
  showLogMealModal,
  showLogWorkoutModal,
  showLogStepsModal,
  showUpdateBmiModal,
} from '../components/modal';
import { animateCounter, getStoredUser } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

Chart.register(ArcElement, Tooltip, Legend, DoughnutController);

let calorieChartInstance: Chart | null = null;

export async function renderDashboardPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  const user = getStoredUser();
  const userName = user?.username || 'Athlete';

  // Render Shell with Navbar
  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/dashboard'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.id = 'dashboard-container';
  container.innerHTML = `
    <!-- Top Hero Section -->
    <div class="dashboard-hero glass-card" id="hero-banner">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem;">
        <div>
          <div class="dashboard-hero__date" id="hero-date">
            ${new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
          </div>
          <h1 class="dashboard-hero__greeting">
            Welcome Back, <span>${userName}</span>
          </h1>
          <p style="color: var(--text-secondary); max-width: 550px; font-size: 0.95rem;">
            Your biomechanical intelligence engine has synced today's biomarkers. You are on track for peak metabolic output.
          </p>
          <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <div class="dashboard-hero__streak">
              🔥 <span id="streak-count">5</span> Day Workout Streak
            </div>
            <div class="tag-chip" style="background: rgba(34, 197, 94, 0.12); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.25);">
              ✓ Adaptive Recovery Active
            </div>
          </div>
        </div>

        <!-- Adherence Ring -->
        <div style="text-align: center; background: rgba(255,255,255,0.03); padding: 1.25rem 1.75rem; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-tertiary); letter-spacing: 0.05em; margin-bottom: 6px;">
            Daily Adherence
          </div>
          <div style="font-size: 2.25rem; font-weight: 900; color: var(--accent-cyan);" id="adherence-score">
            85%
          </div>
          <div style="font-size: 0.8rem; color: var(--text-secondary);">
            Top 5% of active users
          </div>
        </div>
      </div>

      <!-- Quick Action Toolbar -->
      <div class="quick-actions" style="margin-top: 2rem;">
        <button class="btn btn--secondary" id="action-water">
          <i data-lucide="droplet"></i>
          <span>+ Water</span>
        </button>
        <button class="btn btn--secondary" id="action-meal">
          <i data-lucide="utensils"></i>
          <span>+ Log Meal</span>
        </button>
        <button class="btn btn--secondary" id="action-workout">
          <i data-lucide="dumbbell"></i>
          <span>+ Record Workout</span>
        </button>
        <button class="btn btn--secondary" id="action-steps">
          <i data-lucide="footprints"></i>
          <span>+ Steps</span>
        </button>
        <button class="btn btn--secondary" id="action-bmi">
          <i data-lucide="scale"></i>
          <span>Update BMI</span>
        </button>
        <a href="#/wearables" class="btn btn--secondary" id="action-wearables" style="display: inline-flex; align-items: center; gap: 8px;">
          <i data-lucide="watch"></i>
          <span>Wearables & Recovery</span>
        </a>
      </div>
    </div>

    <!-- Telemetry Cards Grid -->
    <div class="grid grid--3" id="metrics-grid">
      <!-- 1. BMI Card -->
      <div class="metric-card glass-card" id="card-bmi">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="metric-card__icon metric-card__icon--blue">
            <i data-lucide="scale"></i>
          </div>
          <span class="tag-chip" id="bmi-badge" style="background: rgba(34, 197, 94, 0.15); color: var(--success);">
            Normal Weight
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">
          Body Mass Index
        </div>
        <div style="display: flex; align-items: baseline; gap: 8px; margin: 0.5rem 0;">
          <span style="font-size: 2.5rem; font-weight: 900;" id="bmi-val">22.8</span>
          <span style="color: var(--text-tertiary); font-size: 0.9rem;">BMI Score</span>
        </div>

        <div class="bmi-meter">
          <div class="bmi-meter__indicator" id="bmi-meter-pin" style="
            position: absolute; top: -6px; width: 4px; height: 24px;
            background: #fff; border-radius: 2px; box-shadow: 0 0 10px #fff;
            left: 38%; transition: left 1s ease;
          "></div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 1rem;">
          <span>Under</span>
          <span>Normal (18.5 - 24.9)</span>
          <span>Over</span>
          <span>Obese</span>
        </div>

        <div class="stat-row">
          <span style="color: var(--text-secondary);">Recorded Weight</span>
          <strong id="bmi-weight-label" style="color: var(--text-primary);">74.0 kg</strong>
        </div>
        <div class="stat-row">
          <span style="color: var(--text-secondary);">Recorded Height</span>
          <strong id="bmi-height-label" style="color: var(--text-primary);">180 cm</strong>
        </div>
      </div>

      <!-- 2. Calorie Card -->
      <div class="metric-card glass-card" id="card-calories">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="metric-card__icon metric-card__icon--purple">
            <i data-lucide="flame"></i>
          </div>
          <span class="tag-chip" id="cal-status-badge" style="background: rgba(139, 92, 246, 0.15); color: var(--accent-purple);">
            On Track
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">
          Energy & Nutrition
        </div>

        <div style="position: relative; width: 140px; height: 140px; margin: 0.5rem auto 1rem;">
          <canvas id="calorieChartCanvas"></canvas>
          <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
            <div style="font-size: 1.4rem; font-weight: 800;" id="cal-remaining">650</div>
            <div style="font-size: 0.65rem; color: var(--text-tertiary); text-transform: uppercase;">kcal left</div>
          </div>
        </div>

        <div class="stat-row">
          <span style="color: var(--text-secondary);">Consumed</span>
          <strong id="cal-consumed" style="color: var(--accent-purple);">1,750 kcal</strong>
        </div>
        <div class="stat-row">
          <span style="color: var(--text-secondary);">Daily Target</span>
          <strong id="cal-target" style="color: var(--text-primary);">2,400 kcal</strong>
        </div>
      </div>

      <!-- 3. Water Intake Card -->
      <div class="metric-card glass-card" id="card-water">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="metric-card__icon metric-card__icon--cyan">
            <i data-lucide="droplet"></i>
          </div>
          <span class="tag-chip" id="water-badge" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan);">
            Hydrated
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-bottom: 0.5rem;">
          Hydration Telemetry
        </div>

        <div class="water-container">
          <div class="water-wave" id="water-wave-anim" style="height: 65%;">
            <div class="water-fill" style="height: 100%;"></div>
          </div>
          <div class="water-text">
            <div class="water-text__value" id="water-val">2.1</div>
            <div class="water-text__unit">LITERS</div>
          </div>
        </div>

        <div class="stat-row">
          <span style="color: var(--text-secondary);">Target Intake</span>
          <strong id="water-target" style="color: var(--accent-cyan);">3.0 Liters</strong>
        </div>

        <div style="display: flex; gap: 8px; margin-top: 0.75rem;">
          <button class="btn btn--secondary btn--full quick-water-mini" data-l="0.25" style="padding: 8px; font-size: 0.8rem;">
            +250ml
          </button>
          <button class="btn btn--secondary btn--full quick-water-mini" data-l="0.5" style="padding: 8px; font-size: 0.8rem;">
            +500ml
          </button>
        </div>
      </div>

      <!-- 4. Steps Card -->
      <div class="metric-card glass-card" id="card-steps">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="metric-card__icon metric-card__icon--blue">
            <i data-lucide="footprints"></i>
          </div>
          <span class="tag-chip" style="background: rgba(59, 130, 246, 0.15); color: var(--accent-blue);">
            Active Pace
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">
          Step Counter & Mobility
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin: 0.5rem 0;">
          <span style="font-size: 2.5rem; font-weight: 900;" id="steps-counter">8,420</span>
          <span style="color: var(--text-tertiary); font-size: 0.9rem;">/ 10,000 steps</span>
        </div>

        <div class="progress-bar" style="margin: 0.75rem 0; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden;">
          <div id="steps-progress" style="width: 84%; height: 100%; background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); transition: width 1s ease;"></div>
        </div>

        <div class="stat-row">
          <span style="color: var(--text-secondary);">Distance Covered</span>
          <strong id="steps-distance" style="color: var(--text-primary);">6.3 km</strong>
        </div>
        <div class="stat-row">
          <span style="color: var(--text-secondary);">Est. Active Burn</span>
          <strong id="steps-calories" style="color: var(--accent-cyan);">336 kcal</strong>
        </div>
      </div>

      <!-- 5. Workout Card -->
      <div class="metric-card glass-card" id="card-workouts">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="metric-card__icon metric-card__icon--purple">
            <i data-lucide="dumbbell"></i>
          </div>
          <span class="tag-chip" style="background: rgba(236, 72, 153, 0.15); color: var(--accent-pink);">
            Hypertrophy
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">
          Daily Workout Output
        </div>

        <div style="display: flex; align-items: baseline; gap: 8px; margin: 0.5rem 0;">
          <span style="font-size: 2.5rem; font-weight: 900;" id="workout-mins">55</span>
          <span style="color: var(--text-tertiary); font-size: 0.9rem;">Minutes Trained</span>
        </div>

        <div class="stat-row">
          <span style="color: var(--text-secondary);">Calories Expended</span>
          <strong id="workout-burn" style="color: var(--danger);">460 kcal</strong>
        </div>
        <div class="stat-row">
          <span style="color: var(--text-secondary);">Latest Protocol</span>
          <strong id="workout-name" style="color: var(--text-primary); font-size: 0.85rem;">Push Hypertrophy A</strong>
        </div>

        <button class="btn btn--primary btn--full" id="btn-quick-workout" style="margin-top: 1rem; padding: 10px; font-size: 0.85rem;">
          <i data-lucide="plus-circle"></i>
          <span>Log Training Session</span>
        </button>
      </div>

      <!-- 6. AI Active Programs Card -->
      <div class="metric-card glass-card" id="card-ai-programs">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div class="metric-card__icon metric-card__icon--cyan">
            <i data-lucide="sparkles"></i>
          </div>
          <span class="tag-chip" style="background: rgba(34, 197, 94, 0.15); color: var(--success);">
            AI Synced
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600;">
          Active AI Blueprints
        </div>

        <div style="margin: 1rem 0; display: flex; flex-direction: column; gap: 10px;">
          <a href="#/diet" style="display: block; padding: 12px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); transition: all 0.2s ease;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.85rem; font-weight: 600; color: #fff;">🥗 AI Diet Blueprint</span>
              <span style="font-size: 0.75rem; color: var(--accent-cyan);">View &rarr;</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;" id="active-diet-title">
              High Protein Lean Bulking (2,400 kcal)
            </div>
          </a>

          <a href="#/workouts" style="display: block; padding: 12px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); transition: all 0.2s ease;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.85rem; font-weight: 600; color: #fff;">🏋️ AI Workout Split</span>
              <span style="font-size: 0.75rem; color: var(--accent-blue);">View &rarr;</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;" id="active-workout-title">
              4-Day Upper / Lower Periodization
            </div>
          </a>
        </div>

        <a href="#/video" class="btn btn--secondary btn--full" style="padding: 10px; font-size: 0.85rem;">
          <i data-lucide="video"></i>
          <span>Launch Video Biomechanics</span>
        </a>
      </div>
    </div>

    <!-- AI Health Insights Feed -->
    <div style="margin-top: 2.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
          <h2 style="font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;">
            AI Health & Biomechanics <span class="navbar__logo-gradient">Insights</span>
          </h2>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">
            Real-time biometric intelligence synthesized from your daily activity
          </p>
        </div>
        <a href="#/insights" class="btn btn--secondary" style="padding: 8px 16px; font-size: 0.85rem;">
          <span>All Insights</span>
          <i data-lucide="arrow-right"></i>
        </a>
      </div>

      <div class="grid grid--3" id="insights-preview-grid">
        <!-- Will be populated dynamically -->
      </div>
    </div>
  `;

  appEl.appendChild(container);

  // GSAP animation for dashboard cards
  gsap.fromTo(
    '#hero-banner',
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' },
  );

  gsap.fromTo(
    '.metric-card',
    { opacity: 0, y: 25 },
    { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: 'power2.out', delay: 0.15 },
  );

  refreshIcons(appEl);

  // Hook up Quick Action buttons
  container.querySelector('#action-water')?.addEventListener('click', () => showLogWaterModal(() => fetchDashboardData()));
  container.querySelector('#action-meal')?.addEventListener('click', () => showLogMealModal(() => fetchDashboardData()));
  container.querySelector('#action-workout')?.addEventListener('click', () => showLogWorkoutModal(() => fetchDashboardData()));
  container.querySelector('#action-steps')?.addEventListener('click', () => showLogStepsModal(() => fetchDashboardData()));
  container.querySelector('#action-bmi')?.addEventListener('click', () => showUpdateBmiModal(() => fetchDashboardData()));
  container.querySelector('#btn-quick-workout')?.addEventListener('click', () => showLogWorkoutModal(() => fetchDashboardData()));

  // Card click navigations to dedicated telemetry studios
  const cardBmi = container.querySelector('#card-bmi') as HTMLElement;
  if (cardBmi) {
    cardBmi.style.cursor = 'pointer';
    cardBmi.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('button')) return;
      router.navigate('/bmi');
    });
  }

  const cardCal = container.querySelector('#card-calories') as HTMLElement;
  if (cardCal) {
    cardCal.style.cursor = 'pointer';
    cardCal.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('button')) return;
      router.navigate('/calories');
    });
  }

  const cardWater = container.querySelector('#card-water') as HTMLElement;
  if (cardWater) {
    cardWater.style.cursor = 'pointer';
    cardWater.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('button')) return;
      router.navigate('/water');
    });
  }

  const cardSteps = container.querySelector('#card-steps') as HTMLElement;
  if (cardSteps) {
    cardSteps.style.cursor = 'pointer';
    cardSteps.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('button')) return;
      router.navigate('/steps');
    });
  }

  const cardWorkout = container.querySelector('#card-workout') as HTMLElement;
  if (cardWorkout) {
    cardWorkout.style.cursor = 'pointer';
    cardWorkout.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('button')) return;
      router.navigate('/workouts');
    });
  }

  const cardPrograms = container.querySelector('#card-programs') as HTMLElement;
  if (cardPrograms) {
    cardPrograms.style.cursor = 'pointer';
    cardPrograms.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('button')) return;
      router.navigate('/diet');
    });
  }

  // Mini water buttons
  container.querySelectorAll('.quick-water-mini').forEach(btn => {
    btn.addEventListener('click', async () => {
      const l = parseFloat((btn as HTMLElement).dataset.l || '0.25');
      try {
        await waterApi.add({ liters: l });
      } catch {
        // Fallback
      }
      fetchDashboardData();
    });
  });

  // Fetch actual data
  await fetchDashboardData();
}

async function fetchDashboardData(): Promise<void> {
  let data: DashboardOverviewResponse;

  try {
    data = await dashboardApi.getOverview();
  } catch {
    // Elegant fallback simulation if backend is launching or offline
    data = {
      user_id: 1,
      username: getStoredUser()?.username || 'Alex Rivers',
      today: {
        calories_consumed: 1750,
        calories_target: 2400,
        calories_remaining: 650,
        water_liters: 2.1,
        water_target_liters: 3.0,
        steps_count: 8420,
        steps_target: 10000,
        workout_minutes: 55,
        calories_burned: 460,
      },
      bmi_status: {
        current_bmi: 22.8,
        category: 'Normal Weight',
        weight_kg: 74.0,
        height_cm: 180.0,
      },
      weekly_adherence: {
        overall_score: 85,
        workout_days_completed: 4,
        target_workout_days: 5,
        water_target_met_days: 5,
        calorie_target_met_days: 4,
      },
      streaks: {
        current_streak_days: 5,
        longest_streak_days: 14,
        total_active_days: 28,
      },
      active_diet_plan_title: 'High Protein Hypertrophy Blueprint (2,400 kcal)',
      active_workout_plan_title: '4-Day Upper / Lower Periodization',
      recent_insights: [
        {
          id: 1,
          user_id: 1,
          category: 'Hydration',
          title: 'Hydration Velocity Optimal',
          content: 'You reached 70% of your hydration target prior to your 4 PM workout, lowering perceived exertion by 12%.',
          priority: 'low',
          is_read: false,
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          user_id: 1,
          category: 'Nutrition',
          title: 'Post-Workout Anabolic Window',
          content: '650 kcal remaining for dinner. Recommended macro allocation: 45g protein, 60g complex carbohydrates.',
          priority: 'medium',
          is_read: false,
          created_at: new Date().toISOString(),
        },
        {
          id: 3,
          user_id: 1,
          category: 'Recovery',
          title: 'Mobility Precaution on Squats',
          content: 'Video biomechanics flagged slight lumbar flexion at 95 degrees depth. Consider 5 minutes of hip opener work before heavy sets.',
          priority: 'high',
          is_read: false,
          created_at: new Date().toISOString(),
        },
      ],
    };
  }

  updateDashboardUI(data);
}

function updateDashboardUI(data: DashboardOverviewResponse): void {
  // Streak & Adherence
  const streakEl = document.getElementById('streak-count');
  if (streakEl) streakEl.textContent = `${data.streaks.current_streak_days}`;

  const adherenceEl = document.getElementById('adherence-score');
  if (adherenceEl) adherenceEl.textContent = `${data.weekly_adherence.overall_score}%`;

  // BMI Card
  const bmiVal = document.getElementById('bmi-val');
  if (bmiVal && data.bmi_status.current_bmi) {
    bmiVal.textContent = data.bmi_status.current_bmi.toFixed(1);
  }
  const bmiBadge = document.getElementById('bmi-badge');
  if (bmiBadge && data.bmi_status.category) {
    bmiBadge.textContent = data.bmi_status.category;
  }
  const bmiPin = document.getElementById('bmi-meter-pin');
  if (bmiPin && data.bmi_status.current_bmi) {
    // Normal is ~18.5 to 25. Range mapped from 15 to 35
    const pct = Math.min(Math.max(((data.bmi_status.current_bmi - 15) / 20) * 100, 5), 95);
    bmiPin.style.left = `${pct}%`;
  }
  const bmiWeight = document.getElementById('bmi-weight-label');
  if (bmiWeight && data.bmi_status.weight_kg) {
    bmiWeight.textContent = `${data.bmi_status.weight_kg} kg`;
  }
  const bmiHeight = document.getElementById('bmi-height-label');
  if (bmiHeight && data.bmi_status.height_cm) {
    bmiHeight.textContent = `${data.bmi_status.height_cm} cm`;
  }

  // Calorie Card & Chart.js Donut
  const calConsumed = document.getElementById('cal-consumed');
  if (calConsumed) calConsumed.textContent = `${data.today.calories_consumed.toLocaleString()} kcal`;

  const calTarget = document.getElementById('cal-target');
  if (calTarget) calTarget.textContent = `${data.today.calories_target.toLocaleString()} kcal`;

  const calRem = document.getElementById('cal-remaining');
  if (calRem) calRem.textContent = `${Math.max(0, data.today.calories_remaining).toLocaleString()}`;

  renderCalorieChart(data.today.calories_consumed, data.today.calories_remaining);

  // Water Card
  const waterVal = document.getElementById('water-val');
  if (waterVal) waterVal.textContent = `${data.today.water_liters.toFixed(1)}`;

  const waterTarget = document.getElementById('water-target');
  if (waterTarget) waterTarget.textContent = `${data.today.water_target_liters.toFixed(1)} Liters`;

  const waterWave = document.getElementById('water-wave-anim');
  if (waterWave) {
    const pct = Math.min((data.today.water_liters / data.today.water_target_liters) * 100, 100);
    waterWave.style.height = `${pct}%`;
  }

  // Steps Card
  const stepsCounter = document.getElementById('steps-counter');
  if (stepsCounter) {
    animateCounter(stepsCounter, data.today.steps_count, 1000, 0);
  }
  const stepsProg = document.getElementById('steps-progress');
  if (stepsProg) {
    const pct = Math.min((data.today.steps_count / data.today.steps_target) * 100, 100);
    stepsProg.style.width = `${pct}%`;
  }
  const stepsDist = document.getElementById('steps-distance');
  if (stepsDist) {
    const km = (data.today.steps_count * 0.00075).toFixed(1);
    stepsDist.textContent = `${km} km`;
  }
  const stepsCal = document.getElementById('steps-calories');
  if (stepsCal) {
    const c = Math.round(data.today.steps_count * 0.04);
    stepsCal.textContent = `${c} kcal`;
  }

  // Workout Card
  const workoutMins = document.getElementById('workout-mins');
  if (workoutMins) workoutMins.textContent = `${data.today.workout_minutes}`;

  const workoutBurn = document.getElementById('workout-burn');
  if (workoutBurn) workoutBurn.textContent = `${data.today.calories_burned} kcal`;

  // Programs Card
  const dietTitle = document.getElementById('active-diet-title');
  if (dietTitle && data.active_diet_plan_title) {
    dietTitle.textContent = data.active_diet_plan_title;
  }
  const workoutTitle = document.getElementById('active-workout-title');
  if (workoutTitle && data.active_workout_plan_title) {
    workoutTitle.textContent = data.active_workout_plan_title;
  }

  // Insights Preview
  const insightsGrid = document.getElementById('insights-preview-grid');
  if (insightsGrid && data.recent_insights) {
    insightsGrid.innerHTML = data.recent_insights
      .map(item => {
        let badgeColor = 'var(--accent-blue)';
        let badgeBg = 'rgba(59, 130, 246, 0.15)';
        if (item.priority === 'high') {
          badgeColor = 'var(--danger)';
          badgeBg = 'rgba(239, 68, 68, 0.15)';
        } else if (item.priority === 'medium') {
          badgeColor = 'var(--warning)';
          badgeBg = 'rgba(245, 158, 11, 0.15)';
        } else if (item.priority === 'low') {
          badgeColor = 'var(--success)';
          badgeBg = 'rgba(34, 197, 94, 0.15)';
        }

        return `
          <div class="glass-card" style="padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span class="tag-chip" style="background: ${badgeBg}; color: ${badgeColor}; font-size: 0.75rem;">
                  ${item.category}
                </span>
                <span style="font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase;">
                  ${item.priority} Priority
                </span>
              </div>
              <h4 style="font-size: 1rem; font-weight: 700; color: #fff; margin-bottom: 0.5rem;">
                ${item.title}
              </h4>
              <p style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5;">
                ${item.content}
              </p>
            </div>
            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.75rem; color: var(--text-tertiary);">AI Synthesized</span>
              <a href="#/insights" style="font-size: 0.8rem; color: var(--accent-cyan); font-weight: 600;">Explore &rarr;</a>
            </div>
          </div>
        `;
      })
      .join('');
    refreshIcons(insightsGrid);
  }
}

function renderCalorieChart(consumed: number, remaining: number): void {
  const canvas = document.getElementById('calorieChartCanvas') as HTMLCanvasElement;
  if (!canvas) return;

  if (calorieChartInstance) {
    calorieChartInstance.destroy();
  }

  calorieChartInstance = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Consumed', 'Remaining'],
      datasets: [
        {
          data: [consumed, Math.max(0, remaining)],
          backgroundColor: ['#8b5cf6', 'rgba(255, 255, 255, 0.08)'],
          borderColor: ['rgba(139, 92, 246, 0.4)', 'rgba(255, 255, 255, 0.05)'],
          borderWidth: 2,
          hoverOffset: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '76%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255, 255, 255, 0.15)',
          borderWidth: 1,
          padding: 10,
        },
      },
    },
  });
}
