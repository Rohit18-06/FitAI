// ============================================================
// FitAI – BMI Calculator & Physiological Composition Studio
// ============================================================

import gsap from 'gsap';
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Filler,
} from 'chart.js';
import { bmiApi } from '../api/bmi';
import type { BMIResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { formatDate } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler);

let bmiHistoryChart: Chart | null = null;

export async function renderBMIPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/bmi'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Header -->
    <div class="page-header" style="margin-bottom: 2rem;">
      <h1 class="page-header__title">
        BMI & Body Composition <span class="navbar__logo-gradient">Telemetry</span>
      </h1>
      <p class="page-header__subtitle">
        Track your Body Mass Index, historical weight deltas, and anthropometric categorization
      </p>
    </div>

    <!-- Top Grid: Calculator Card + Animated Gauge Card -->
    <div class="grid grid--2" style="margin-bottom: 2rem;">
      <!-- Calculator Form Card -->
      <div class="glass-card" style="padding: 2.25rem;" id="bmi-calc-card">
        <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
          <i data-lucide="scale" style="color: var(--accent-cyan);"></i>
          <span>Calculate & Log BMI</span>
        </h3>

        <form id="bmi-calc-form">
          <div class="form-group" style="margin-bottom: 1.5rem;">
            <label class="form-label" for="bmi-height">Height (cm)</label>
            <div style="position: relative;">
              <input
                type="number"
                id="bmi-height"
                class="form-input"
                placeholder="178"
                step="0.5"
                min="50"
                max="260"
                required
                value="178"
              />
              <span style="position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); font-size: 0.85rem;">cm</span>
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 2rem;">
            <label class="form-label" for="bmi-weight">Weight (kg)</label>
            <div style="position: relative;">
              <input
                type="number"
                id="bmi-weight"
                class="form-input"
                placeholder="75.0"
                step="0.1"
                min="20"
                max="300"
                required
                value="75.0"
              />
              <span style="position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); font-size: 0.85rem;">kg</span>
            </div>
          </div>

          <button type="submit" id="bmi-submit-btn" class="btn btn--primary btn--full" style="padding: 12px 24px;">
            <i data-lucide="calculator"></i>
            <span>Calculate & Record BMI</span>
          </button>
        </form>
      </div>

      <!-- Animated Gauge / Result Card -->
      <div class="glass-card" style="padding: 2.25rem; display: flex; flex-direction: column; justify-content: space-between; text-align: center;" id="bmi-gauge-card">
        <div>
          <span style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700; letter-spacing: 0.05em;">
            Current Physiological Index
          </span>

          <div style="margin: 1.5rem 0;">
            <div style="font-size: 4rem; font-weight: 900; line-height: 1; letter-spacing: -0.03em;" id="bmi-val-display">
              --
            </div>
            <div style="margin-top: 0.75rem;">
              <span class="tag-chip" id="bmi-cat-pill" style="font-size: 0.9rem; padding: 6px 18px; background: rgba(59, 130, 246, 0.15); color: var(--accent-blue);">
                Awaiting Input
              </span>
            </div>
          </div>
        </div>

        <!-- Metric Reference Spectrum -->
        <div>
          <div style="height: 10px; border-radius: 5px; background: linear-gradient(90deg, #06b6d4 0%, #22c55e 30%, #f59e0b 65%, #ef4444 100%); margin-bottom: 0.75rem; position: relative;">
            <div id="bmi-pointer" style="position: absolute; top: -4px; left: 40%; width: 4px; height: 18px; background: #fff; border-radius: 2px; box-shadow: 0 0 10px #fff; transition: left 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);"></div>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--text-tertiary);">
            <span>&lt; 18.5 Under</span>
            <span>18.5–24.9 Normal</span>
            <span>25–29.9 Over</span>
            <span>30+ Obese</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart: Longitudinal BMI & Weight Progress -->
    <div class="glass-card chart-container" style="margin-bottom: 2rem; padding: 2rem;" id="bmi-chart-card">
      <div class="chart-container__header">
        <div>
          <h3 class="chart-container__title">Historical Weight & Composition Trajectory</h3>
          <p style="font-size: 0.75rem; color: var(--text-secondary);">Longitudinal body mass records logged over time</p>
        </div>
        <span class="tag-chip" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan);">
          Biometric Trend
        </span>
      </div>
      <div class="chart-canvas-wrap" style="height: 280px;">
        <canvas id="bmiTrendChart"></canvas>
      </div>
    </div>

    <!-- History Table Card -->
    <div class="glass-card" style="padding: 2rem;" id="bmi-history-card">
      <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="history" style="color: var(--accent-blue);"></i>
        <span>BMI Measurement Log History</span>
      </h3>

      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
          <thead>
            <tr style="border-bottom: 1px solid var(--glass-border); color: var(--text-tertiary); font-size: 0.75rem; text-transform: uppercase;">
              <th style="padding: 12px 16px;">Date</th>
              <th style="padding: 12px 16px;">Height</th>
              <th style="padding: 12px 16px;">Weight</th>
              <th style="padding: 12px 16px;">BMI</th>
              <th style="padding: 12px 16px;">Classification</th>
            </tr>
          </thead>
          <tbody id="bmi-history-tbody">
            <!-- Populated via TS -->
          </tbody>
        </table>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Animate Entrance
  gsap.fromTo(
    ['#bmi-calc-card', '#bmi-gauge-card', '#bmi-chart-card', '#bmi-history-card'],
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.45, stagger: 0.08, ease: 'power2.out' },
  );

  // Form submit handler
  const form = container.querySelector('#bmi-calc-form') as HTMLFormElement;
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const height = parseFloat((container.querySelector('#bmi-height') as HTMLInputElement).value);
    const weight = parseFloat((container.querySelector('#bmi-weight') as HTMLInputElement).value);

    if (!height || !weight) return;

    const btn = container.querySelector('#bmi-submit-btn') as HTMLButtonElement;
    btn.disabled = true;

    try {
      const res = await bmiApi.calculate({ height_cm: height, weight_kg: weight });
      updateBMIDisplay(res.bmi, res.category);
      showToast(`BMI Logged: ${res.bmi.toFixed(1)} (${res.category})`, 'success');
      loadBMIHistory();
    } catch {
      // Local calculation fallback
      const bmiVal = weight / Math.pow(height / 100, 2);
      let cat = 'Normal';
      if (bmiVal < 18.5) cat = 'Underweight';
      else if (bmiVal >= 25 && bmiVal < 30) cat = 'Overweight';
      else if (bmiVal >= 30) cat = 'Obese';

      updateBMIDisplay(bmiVal, cat);
      showToast(`BMI Calculated: ${bmiVal.toFixed(1)} (${cat})`, 'success');
    } finally {
      btn.disabled = false;
    }
  });

  loadBMIHistory();
}

function updateBMIDisplay(bmi: number, category: string): void {
  const valEl = document.getElementById('bmi-val-display');
  const catPill = document.getElementById('bmi-cat-pill');
  const pointer = document.getElementById('bmi-pointer');

  if (valEl) {
    valEl.textContent = bmi.toFixed(1);
    gsap.fromTo(valEl, { scale: 0.8 }, { scale: 1, duration: 0.35, ease: 'back.out(2)' });
  }

  if (catPill) {
    catPill.textContent = category;
    let bg = 'rgba(59, 130, 246, 0.15)';
    let color = 'var(--accent-blue)';
    if (category.toLowerCase().includes('normal')) {
      bg = 'rgba(34, 197, 94, 0.15)';
      color = 'var(--success)';
    } else if (category.toLowerCase().includes('overweight')) {
      bg = 'rgba(245, 158, 11, 0.15)';
      color = 'var(--warning)';
    } else if (category.toLowerCase().includes('obese')) {
      bg = 'rgba(239, 68, 68, 0.15)';
      color = 'var(--danger)';
    }
    catPill.style.background = bg;
    catPill.style.color = color;
  }

  if (pointer) {
    // Clamp between 15 and 35 BMI into 0-100%
    const pct = Math.min(100, Math.max(0, ((bmi - 15) / (35 - 15)) * 100));
    pointer.style.left = `${pct}%`;
  }
}

async function loadBMIHistory(): Promise<void> {
  const tbody = document.getElementById('bmi-history-tbody');
  let history: BMIResponse[] = [];

  try {
    history = await bmiApi.getHistory(20);
  } catch {
    history = [];
  }

  if (history.length > 0) {
    const latest = history[0];
    updateBMIDisplay(latest.bmi, latest.category);

    if (tbody) {
      tbody.innerHTML = history
        .map(
          item => `
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.2s ease;">
          <td style="padding: 12px 16px; color: var(--text-secondary);">${formatDate(item.created_at)}</td>
          <td style="padding: 12px 16px;">${item.height_cm} cm</td>
          <td style="padding: 12px 16px; font-weight: 600;">${item.weight_kg} kg</td>
          <td style="padding: 12px 16px; font-weight: 700; color: var(--accent-cyan);">${item.bmi.toFixed(1)}</td>
          <td style="padding: 12px 16px;">
            <span class="tag-chip" style="font-size: 0.75rem; padding: 2px 10px;">${item.category}</span>
          </td>
        </tr>
      `,
        )
        .join('');
    }

    renderBMITrendChart(history.slice().reverse());
  } else {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="padding: 2rem; text-align: center; color: var(--text-tertiary);">
            No BMI measurements recorded yet. Enter height and weight above to create your baseline log.
          </td>
        </tr>
      `;
    }
  }
}

function renderBMITrendChart(items: BMIResponse[]): void {
  const canvas = document.getElementById('bmiTrendChart') as HTMLCanvasElement;
  if (!canvas) return;
  if (bmiHistoryChart) bmiHistoryChart.destroy();

  const labels = items.map(i => formatDate(i.created_at));
  const weights = items.map(i => i.weight_kg);

  bmiHistoryChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Weight (kg)',
          data: weights,
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: '#06b6d4',
          pointRadius: 5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
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
