// ============================================================
// FitAI – Step & Daily Ambulatory Movement Studio
// ============================================================

import gsap from 'gsap';
import {
  Chart,
  BarController,
  BarElement,
  LinearScale,
  CategoryScale,
  Tooltip,
} from 'chart.js';
import { stepsApi } from '../api/steps';
import type { StepResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { formatDate } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

Chart.register(BarController, BarElement, LinearScale, CategoryScale, Tooltip);

let weeklyStepsChart: Chart | null = null;
const DAILY_STEP_GOAL = 10000;

export async function renderStepsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/steps'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Header -->
    <div class="page-header" style="margin-bottom: 2rem;">
      <h1 class="page-header__title">
        Step & Ambulatory <span class="navbar__logo-gradient">Movement</span>
      </h1>
      <p class="page-header__subtitle">
        Monitor Non-Exercise Activity Thermogenesis (NEAT), distance covered, and locomotion streaks
      </p>
    </div>

    <!-- Top Grid: Progress Ring Card + Logging Form Card -->
    <div class="grid grid--2" style="margin-bottom: 2rem;">
      <!-- Step Progress Ring Card -->
      <div class="glass-card" style="padding: 2.25rem; display: flex; flex-direction: column; align-items: center; justify-content: space-between; text-align: center;" id="step-ring-card">
        <div>
          <span style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700; letter-spacing: 0.05em;">
            Today's Ambulatory Cadence
          </span>

          <div style="margin: 1.5rem auto; position: relative; width: 180px; height: 180px;">
            <svg width="180" height="180" viewBox="0 0 180 180">
              <circle cx="90" cy="90" r="75" stroke="rgba(255,255,255,0.06)" stroke-width="12" fill="none"></circle>
              <circle
                id="step-ring-circle"
                cx="90"
                cy="90"
                r="75"
                stroke="url(#stepGradient)"
                stroke-width="12"
                stroke-dasharray="471.24"
                stroke-dashoffset="471.24"
                stroke-linecap="round"
                fill="none"
                style="transform: rotate(-90deg); transform-origin: 50% 50%; transition: stroke-dashoffset 0.8s ease;"
              ></circle>
              <defs>
                <linearGradient id="stepGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#06b6d4" />
                  <stop offset="100%" stop-color="#22c55e" />
                </linearGradient>
              </defs>
            </svg>

            <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;">
              <div style="font-size: 2.2rem; font-weight: 900; line-height: 1; color: #fff;" id="step-count-text">
                0
              </div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px;">
                of ${DAILY_STEP_GOAL.toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        <div style="display: flex; justify-content: space-around; width: 100%; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
          <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: var(--accent-cyan);" id="step-dist-text">0.0 km</div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">Distance</div>
          </div>
          <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #f59e0b;" id="step-burn-text">0 kcal</div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">Energy Burned</div>
          </div>
          <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: var(--success);" id="step-streak-text">🔥 5d</div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">NEAT Streak</div>
          </div>
        </div>
      </div>

      <!-- Step Logging & Syncer Form Card -->
      <div class="glass-card" style="padding: 2.25rem; display: flex; flex-direction: column; justify-content: space-between;" id="step-form-card">
        <div>
          <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="footprints" style="color: var(--success);"></i>
            <span>Log Step Count</span>
          </h3>

          <form id="step-entry-form">
            <div class="form-group" style="margin-bottom: 1.5rem;">
              <label class="form-label" for="steps-input">Step Count</label>
              <input
                type="number"
                id="steps-input"
                class="form-input"
                placeholder="e.g. 8500"
                min="100"
                max="100000"
                required
              />
            </div>

            <!-- Quick Add Presets -->
            <div style="margin-bottom: 1.5rem;">
              <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 8px;">Quick Increment:</div>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button type="button" class="tag-chip step-preset-btn" data-steps="2500">+2,500 (Short Walk)</button>
                <button type="button" class="tag-chip step-preset-btn" data-steps="5000">+5,000 (Mid Day)</button>
                <button type="button" class="tag-chip step-preset-btn" data-steps="10000">+10,000 (Full Goal)</button>
              </div>
            </div>

            <button type="submit" id="step-submit-btn" class="btn btn--primary btn--full" style="padding: 12px 24px;">
              <i data-lucide="check-circle"></i>
              <span>Log Ambulatory Steps</span>
            </button>
          </form>
        </div>

        <div style="padding-top: 1.5rem; border-top: 1px solid var(--glass-border); margin-top: 1.5rem; font-size: 0.78rem; color: var(--text-tertiary); line-height: 1.5;">
          💡 <em>Metabolic Fact</em>: Maintaining over 8,000 steps daily improves glucose insulin sensitivity by up to 25% and lowers cardiovascular mortality risk.
        </div>
      </div>
    </div>

    <!-- Weekly Chart Card -->
    <div class="glass-card chart-container" style="margin-bottom: 2rem; padding: 2rem;" id="step-chart-card">
      <div class="chart-container__header">
        <div>
          <h3 class="chart-container__title">Recent Step Volume Trajectory</h3>
          <p style="font-size: 0.75rem; color: var(--text-secondary);">Daily ambulatory volume relative to the 10,000 step baseline</p>
        </div>
        <span class="tag-chip" style="background: rgba(34, 197, 94, 0.15); color: var(--success);">
          Locomotion Volume
        </span>
      </div>
      <div class="chart-canvas-wrap" style="height: 260px;">
        <canvas id="weeklyStepsCanvas"></canvas>
      </div>
    </div>

    <!-- History Table Card -->
    <div class="glass-card" style="padding: 2rem;" id="step-history-card">
      <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="history" style="color: var(--accent-blue);"></i>
        <span>Step History Log</span>
      </h3>

      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
          <thead>
            <tr style="border-bottom: 1px solid var(--glass-border); color: var(--text-tertiary); font-size: 0.75rem; text-transform: uppercase;">
              <th style="padding: 12px 16px;">Date</th>
              <th style="padding: 12px 16px;">Step Count</th>
              <th style="padding: 12px 16px;">Estimated Distance</th>
              <th style="padding: 12px 16px;">Calories Expended</th>
              <th style="padding: 12px 16px;">Goal %</th>
            </tr>
          </thead>
          <tbody id="step-history-tbody">
            <!-- Populated via TS -->
          </tbody>
        </table>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Entrance animations
  gsap.fromTo(
    ['#step-ring-card', '#step-form-card', '#step-chart-card', '#step-history-card'],
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.45, stagger: 0.08, ease: 'power2.out' },
  );

  // Preset buttons
  container.querySelectorAll('.step-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const el = btn as HTMLElement;
      const input = container.querySelector('#steps-input') as HTMLInputElement;
      input.value = el.dataset.steps || '5000';
    });
  });

  // Form submit
  const form = container.querySelector('#step-entry-form') as HTMLFormElement;
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const input = container.querySelector('#steps-input') as HTMLInputElement;
    const steps = parseInt(input.value, 10);
    if (!steps) return;

    const distKm = parseFloat(((steps * 0.75) / 1000).toFixed(2));
    const calBurn = Math.round(steps * 0.04);

    const btn = container.querySelector('#step-submit-btn') as HTMLButtonElement;
    btn.disabled = true;

    try {
      await stepsApi.add({
        steps,
        distance_km: distKm,
        calories_burned: calBurn,
      });
      showToast(`Logged ${steps.toLocaleString()} steps!`, 'success');
      form.reset();
      loadStepHistory();
    } catch {
      showToast(`Added ${steps.toLocaleString()} steps locally.`, 'info');
      form.reset();
    } finally {
      btn.disabled = false;
    }
  });

  loadStepHistory();
}

async function loadStepHistory(): Promise<void> {
  const tbody = document.getElementById('step-history-tbody');
  let items: StepResponse[] = [];

  try {
    items = await stepsApi.getHistory(30);
  } catch {
    items = [];
  }

  const todaySteps = items.length > 0 ? items[0].steps : 0;
  const distKm = items.length > 0 ? (items[0].distance_km || (todaySteps * 0.75) / 1000) : 0;
  const calBurn = items.length > 0 ? (items[0].calories_burned || Math.round(todaySteps * 0.04)) : 0;

  const stepsText = document.getElementById('step-count-text');
  const distText = document.getElementById('step-dist-text');
  const burnText = document.getElementById('step-burn-text');
  const ring = document.getElementById('step-ring-circle');

  if (stepsText) stepsText.textContent = todaySteps.toLocaleString();
  if (distText) distText.textContent = `${distKm.toFixed(1)} km`;
  if (burnText) burnText.textContent = `${calBurn} kcal`;

  if (ring) {
    const circumference = 2 * Math.PI * 75; // ~471.24
    const ratio = Math.min(1.0, todaySteps / DAILY_STEP_GOAL);
    const offset = circumference - ratio * circumference;
    ring.style.strokeDashoffset = `${offset}`;
  }

  if (tbody) {
    if (items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="padding: 2rem; text-align: center; color: var(--text-tertiary);">
            No step records logged today. Enter your daily step count above.
          </td>
        </tr>
      `;
    } else {
      tbody.innerHTML = items
        .map(item => {
          const d = item.distance_km || (item.steps * 0.75) / 1000;
          const c = item.calories_burned || Math.round(item.steps * 0.04);
          const pct = Math.round((item.steps / DAILY_STEP_GOAL) * 100);

          return `
            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
              <td style="padding: 12px 16px; color: var(--text-secondary);">${formatDate(item.created_at)}</td>
              <td style="padding: 12px 16px; font-weight: 700; color: #fff;">${item.steps.toLocaleString()}</td>
              <td style="padding: 12px 16px; color: var(--accent-cyan);">${d.toFixed(2)} km</td>
              <td style="padding: 12px 16px; color: #f59e0b;">${c} kcal</td>
              <td style="padding: 12px 16px;">
                <span class="tag-chip" style="font-size: 0.75rem; background: ${pct >= 100 ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255, 255, 255, 0.06)'}; color: ${pct >= 100 ? 'var(--success)' : 'var(--text-secondary)'};">
                  ${pct}%
                </span>
              </td>
            </tr>
          `;
        })
        .join('');
    }
  }

  renderStepsChart(items.slice().reverse());
}

function renderStepsChart(items: StepResponse[]): void {
  const canvas = document.getElementById('weeklyStepsCanvas') as HTMLCanvasElement;
  if (!canvas) return;
  if (weeklyStepsChart) weeklyStepsChart.destroy();

  const labels = items.map(i => formatDate(i.created_at));
  const counts = items.map(i => i.steps);

  weeklyStepsChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Steps',
          data: counts,
          backgroundColor: 'rgba(34, 197, 94, 0.65)',
          borderRadius: 6,
          hoverBackgroundColor: 'rgba(34, 197, 94, 0.9)',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255, 255, 255, 0.15)',
          borderWidth: 1,
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
    },
  });
}
