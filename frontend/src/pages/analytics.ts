// ============================================================
// FitAI – Analytics & Achievement Milestones Page
// Full Telemetry Trends with Chart.js & Glass Visuals
// ============================================================
import gsap from 'gsap';
import {
  Chart,
  LineController,
  BarController,
  LineElement,
  PointElement,
  BarElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { analyticsApi } from '../api/analytics';
import type { AnalyticsOverviewResponse, MilestonesResponse, TrendDataPoint, MilestoneItem } from '../types';
import { renderNavbar } from '../components/navbar';
import { animateCounter } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

Chart.register(
  LineController,
  BarController,
  LineElement,
  PointElement,
  BarElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
);

let weightChart: Chart | null = null;
let calorieChart: Chart | null = null;
let activityChart: Chart | null = null;
let waterChart: Chart | null = null;
let currentPeriodDays = 14;

export async function renderAnalyticsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/analytics'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Page Header & Period Selector -->
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          Biometric & Kinetic <span class="navbar__logo-gradient">Analytics</span>
        </h1>
        <p class="page-header__subtitle">
          Longitudinal progress telemetry, metabolic expenditure, and achievement badges
        </p>
      </div>

      <div class="chart-container__period" style="background: rgba(255,255,255,0.04); padding: 4px; border-radius: var(--radius-full); border: 1px solid var(--glass-border);">
        <button class="chart-container__period-btn ${currentPeriodDays === 7 ? 'chart-container__period-btn--active' : ''}" data-days="7">
          7 Days
        </button>
        <button class="chart-container__period-btn ${currentPeriodDays === 14 ? 'chart-container__period-btn--active' : ''}" data-days="14">
          14 Days
        </button>
        <button class="chart-container__period-btn ${currentPeriodDays === 30 ? 'chart-container__period-btn--active' : ''}" data-days="30">
          30 Days
        </button>
      </div>
    </div>

    <!-- Summary Telemetry Cards Grid -->
    <div class="grid grid--3" style="margin-bottom: 2rem;" id="summary-telemetry-grid">
      <div class="metric-card glass-card">
        <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 600;">Avg Daily Energy</div>
        <div style="font-size: 2.2rem; font-weight: 900; margin: 0.5rem 0;" id="metric-avg-cal">0</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">Target: 2,400 kcal/day</div>
      </div>

      <div class="metric-card glass-card">
        <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 600;">Avg Daily Steps</div>
        <div style="font-size: 2.2rem; font-weight: 900; margin: 0.5rem 0; color: var(--accent-cyan);" id="metric-avg-steps">0</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">Active Movement Pace</div>
      </div>

      <div class="metric-card glass-card">
        <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 600;">Total Training Output</div>
        <div style="font-size: 2.2rem; font-weight: 900; margin: 0.5rem 0; color: var(--accent-blue);" id="metric-total-mins">0</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);"><span id="metric-total-burn">0</span> kcal expended</div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;">
      <!-- Chart 1: Weight & BMI -->
      <div class="glass-card chart-container">
        <div class="chart-container__header">
          <div>
            <h3 class="chart-container__title">Weight & BMI Telemetry</h3>
            <p style="font-size: 0.75rem; color: var(--text-secondary);">Historical body mass and body composition trend</p>
          </div>
          <span class="tag-chip" style="background: rgba(59, 130, 246, 0.15); color: var(--accent-blue);">
            Physiological
          </span>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="weightBmiChart"></canvas>
        </div>
      </div>

      <!-- Chart 2: Calories Consumed vs Burned -->
      <div class="glass-card chart-container">
        <div class="chart-container__header">
          <div>
            <h3 class="chart-container__title">Caloric Intake vs Expenditure</h3>
            <p style="font-size: 0.75rem; color: var(--text-secondary);">Energy balance and metabolic delta</p>
          </div>
          <span class="tag-chip" style="background: rgba(139, 92, 246, 0.15); color: var(--accent-purple);">
            Metabolic
          </span>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="caloriesChart"></canvas>
        </div>
      </div>

      <!-- Chart 3: Steps & Physical Activity -->
      <div class="glass-card chart-container">
        <div class="chart-container__header">
          <div>
            <h3 class="chart-container__title">Daily Step Volume</h3>
            <p style="font-size: 0.75rem; color: var(--text-secondary);">NEAT movement against 10,000 threshold</p>
          </div>
          <span class="tag-chip" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan);">
            Locomotion
          </span>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="activityChart"></canvas>
        </div>
      </div>

      <!-- Chart 4: Hydration Intake -->
      <div class="glass-card chart-container">
        <div class="chart-container__header">
          <div>
            <h3 class="chart-container__title">Daily Water Intake (Liters)</h3>
            <p style="font-size: 0.75rem; color: var(--text-secondary);">Hydration status against 3.0L goal</p>
          </div>
          <span class="tag-chip" style="background: rgba(34, 197, 94, 0.15); color: var(--success);">
            Hydration
          </span>
        </div>
        <div class="chart-canvas-wrap">
          <canvas id="waterChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Achievement Milestones Section -->
    <div style="margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2 style="font-size: 1.4rem; font-weight: 800; letter-spacing: -0.02em;">
            Milestone & Achievement <span class="navbar__logo-gradient">Badges</span>
          </h2>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">
            Gamified physical mastery unlocks and biological progression
          </p>
        </div>
        <div class="tag-chip" id="milestones-count-chip" style="background: rgba(34, 197, 94, 0.15); color: var(--success); font-size: 0.85rem; padding: 6px 14px;">
          3 / 6 Unlocked
        </div>
      </div>

      <div class="grid grid--3" id="milestones-grid">
        <!-- Populated via TS -->
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Period switch listeners
  container.querySelectorAll('.chart-container__period-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      container.querySelectorAll('.chart-container__period-btn').forEach(b => {
        b.classList.remove('chart-container__period-btn--active');
      });
      btn.classList.add('chart-container__period-btn--active');
      currentPeriodDays = parseInt((btn as HTMLElement).dataset.days || '14', 10);
      loadAnalyticsData();
    });
  });

  await loadAnalyticsData();
  await loadMilestonesData();
}

async function loadAnalyticsData(): Promise<void> {
  let data: AnalyticsOverviewResponse;
  try {
    data = await analyticsApi.getOverview(currentPeriodDays);
  } catch {
    data = getFallbackAnalytics(currentPeriodDays);
  }

  // Update summary numbers
  const avgCal = document.getElementById('metric-avg-cal');
  if (avgCal) animateCounter(avgCal, data.summary.avg_daily_calories, 1000, 0);

  const avgSteps = document.getElementById('metric-avg-steps');
  if (avgSteps) animateCounter(avgSteps, data.summary.avg_daily_steps, 1000, 0);

  const totalMins = document.getElementById('metric-total-mins');
  if (totalMins) animateCounter(totalMins, data.summary.total_workout_minutes, 1000, 0);

  const totalBurn = document.getElementById('metric-total-burn');
  if (totalBurn) totalBurn.textContent = data.summary.total_calories_burned.toLocaleString();

  // Render Charts
  renderWeightChart(data.daily_trends);
  renderCaloriesChart(data.daily_trends);
  renderActivityChart(data.daily_trends);
  renderWaterChart(data.daily_trends);
}

function renderWeightChart(trends: TrendDataPoint[]): void {
  const canvas = document.getElementById('weightBmiChart') as HTMLCanvasElement;
  if (!canvas) return;
  if (weightChart) weightChart.destroy();

  const labels = trends.map(t => t.date.slice(5));
  const weights = trends.map(t => t.weight_kg || 74.0);

  weightChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Weight (kg)',
          data: weights,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#3b82f6',
          pointRadius: 4,
        },
      ],
    },
    options: getChartOptions('kg'),
  });
}

function renderCaloriesChart(trends: TrendDataPoint[]): void {
  const canvas = document.getElementById('caloriesChart') as HTMLCanvasElement;
  if (!canvas) return;
  if (calorieChart) calorieChart.destroy();

  const labels = trends.map(t => t.date.slice(5));
  const consumed = trends.map(t => t.calories_consumed);
  const burned = trends.map(t => t.calories_burned);

  calorieChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Consumed (kcal)',
          data: consumed,
          backgroundColor: 'rgba(139, 92, 246, 0.65)',
          borderRadius: 6,
        },
        {
          label: 'Burned (kcal)',
          data: burned,
          backgroundColor: 'rgba(239, 68, 68, 0.65)',
          borderRadius: 6,
        },
      ],
    },
    options: getChartOptions('kcal'),
  });
}

function renderActivityChart(trends: TrendDataPoint[]): void {
  const canvas = document.getElementById('activityChart') as HTMLCanvasElement;
  if (!canvas) return;
  if (activityChart) activityChart.destroy();

  const labels = trends.map(t => t.date.slice(5));
  const steps = trends.map(t => t.steps);

  activityChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Steps',
          data: steps,
          backgroundColor: 'rgba(6, 182, 212, 0.65)',
          borderRadius: 6,
        },
      ],
    },
    options: getChartOptions('steps'),
  });
}

function renderWaterChart(trends: TrendDataPoint[]): void {
  const canvas = document.getElementById('waterChart') as HTMLCanvasElement;
  if (!canvas) return;
  if (waterChart) waterChart.destroy();

  const labels = trends.map(t => t.date.slice(5));
  const liters = trends.map(t => t.water_liters);

  waterChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Water Intake (Liters)',
          data: liters,
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.15)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#06b6d4',
          pointRadius: 4,
        },
      ],
    },
    options: getChartOptions('L'),
  });
}

function getChartOptions(unit: string): any {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#cbd5e1',
          font: { size: 11, family: 'Inter' },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#fff',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255, 255, 255, 0.15)',
        borderWidth: 1,
        padding: 10,
        callbacks: {
          label: (ctx: any) => ` ${ctx.dataset.label}: ${ctx.raw} ${unit}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { size: 10 } },
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { size: 10 } },
      },
    },
  };
}

async function loadMilestonesData(): Promise<void> {
  const grid = document.getElementById('milestones-grid');
  const chip = document.getElementById('milestones-count-chip');
  if (!grid) return;

  let res: MilestonesResponse;
  try {
    res = await analyticsApi.getMilestones();
  } catch {
    res = getFallbackMilestones();
  }

  if (chip) {
    chip.textContent = `${res.achieved_count} / ${res.total_milestones} Unlocked`;
  }

  grid.innerHTML = res.milestones
    .map((m: MilestoneItem) => {
      const isAchieved = m.achieved;
      return `
        <div class="glass-card milestone-card ${isAchieved ? 'milestone-card--achieved' : 'milestone-card--locked'}">
          <div class="milestone-card__badge">
            ${m.badge_icon}
          </div>

          <h4 class="milestone-card__title" style="color: ${isAchieved ? '#fff' : 'var(--text-secondary)'};">
            ${m.title}
          </h4>

          <p class="milestone-card__desc">
            ${m.description}
          </p>

          ${
            isAchieved
              ? `<div class="milestone-card__date">✓ Achieved ${m.achieved_date || 'Recently'}</div>`
              : `
              <div style="margin-top: 0.5rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 4px;">
                  <span>Progress</span>
                  <span>${m.progress_percentage}%</span>
                </div>
                <div class="progress-bar" style="height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden;">
                  <div style="width: ${m.progress_percentage}%; height: 100%; background: var(--accent-blue);"></div>
                </div>
              </div>
            `
          }
        </div>
      `;
    })
    .join('');

  gsap.fromTo(
    '.milestone-card',
    { opacity: 0, scale: 0.95 },
    { opacity: 1, scale: 1, duration: 0.5, stagger: 0.08, ease: 'power2.out' },
  );

  refreshIcons(grid);
}

function getFallbackAnalytics(days: number): AnalyticsOverviewResponse {
  const trends: TrendDataPoint[] = [];
  const now = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 86400000);
    const dateStr = d.toISOString().slice(0, 10);
    trends.push({
      date: dateStr,
      calories_consumed: Math.round(2100 + Math.sin(i) * 300),
      water_liters: parseFloat((2.4 + Math.cos(i) * 0.7).toFixed(1)),
      steps: Math.round(8000 + Math.sin(i * 1.5) * 2500),
      workout_minutes: i % 2 === 0 ? 55 : 0,
      calories_burned: i % 2 === 0 ? 460 : 180,
      weight_kg: parseFloat((74.6 - ((days - i) * 0.06)).toFixed(1)),
    });
  }

  return {
    user_id: 1,
    period_days: days,
    summary: {
      avg_daily_calories: 2240,
      avg_daily_steps: 8850,
      avg_daily_water_liters: 2.6,
      total_workout_minutes: 385,
      total_calories_burned: 3200,
    },
    progress: {
      start_weight_kg: 75.2,
      current_weight_kg: 74.0,
      weight_delta_kg: -1.2,
      start_bmi: 23.2,
      current_bmi: 22.8,
      bmi_delta: -0.4,
    },
    daily_trends: trends,
  };
}

function getFallbackMilestones(): MilestonesResponse {
  return {
    total_milestones: 6,
    achieved_count: 4,
    milestones: [
      {
        id: 'm1',
        category: 'Workouts',
        title: 'First Workout Logged',
        description: 'Completed and recorded your inaugural training protocol with FitAI.',
        achieved: true,
        achieved_date: 'March 14, 2026',
        progress_percentage: 100,
        badge_icon: '🏆',
      },
      {
        id: 'm2',
        category: 'Locomotion',
        title: '10,000 Step Benchmark',
        description: 'Exceeded ten thousand daily steps for exceptional non-exercise thermogenesis.',
        achieved: true,
        achieved_date: 'March 18, 2026',
        progress_percentage: 100,
        badge_icon: '👟',
      },
      {
        id: 'm3',
        category: 'Biomechanics',
        title: 'Biomechanics Pioneer',
        description: 'Uploaded video recording and received Gemini spatial keypoint kinematic critique.',
        achieved: true,
        achieved_date: 'March 22, 2026',
        progress_percentage: 100,
        badge_icon: '📹',
      },
      {
        id: 'm4',
        category: 'Body Composition',
        title: 'Healthy BMI Zone',
        description: 'Maintained physiological Body Mass Index strictly within the optimal 18.5 - 24.9 window.',
        achieved: true,
        achieved_date: 'March 25, 2026',
        progress_percentage: 100,
        badge_icon: '⚖️',
      },
      {
        id: 'm5',
        category: 'Hydration',
        title: 'Hydration Virtuoso',
        description: 'Hit 3.0+ Liters of daily hydration for 7 consecutive days in a row.',
        achieved: false,
        achieved_date: null,
        progress_percentage: 71,
        badge_icon: '💧',
      },
      {
        id: 'm6',
        category: 'Hypertrophy',
        title: 'Iron Consistency Legend',
        description: 'Log 20 completed workout protocols across the current training block.',
        achieved: false,
        achieved_date: null,
        progress_percentage: 45,
        badge_icon: '⚡',
      },
    ],
  };
}
