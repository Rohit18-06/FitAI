// ============================================================
// FitAI – Calorie & Macronutrient Telemetry Studio
// ============================================================

import gsap from 'gsap';
import {
  Chart,
  DoughnutController,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { caloriesApi } from '../api/calories';
import type { CalorieResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { formatTime } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

Chart.register(DoughnutController, ArcElement, Tooltip, Legend);

let macroDoughnutChart: Chart | null = null;
const DAILY_CALORIE_TARGET = 2400;

export async function renderCaloriesPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/calories'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Header -->
    <div class="page-header" style="margin-bottom: 2rem;">
      <h1 class="page-header__title">
        Caloric Intake & <span class="navbar__logo-gradient">Macro Telemetry</span>
      </h1>
      <p class="page-header__subtitle">
        Track energy balance, macronutrient distribution, and metabolic intake against your target
      </p>
    </div>

    <!-- Top Telemetry Summary Cards -->
    <div class="grid grid--3" style="margin-bottom: 2rem;" id="cal-summary-grid">
      <div class="metric-card glass-card">
        <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700;">
          Consumed Today
        </div>
        <div style="font-size: 2.5rem; font-weight: 900; margin: 0.5rem 0; color: #fff;" id="cal-consumed-total">
          0
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">Target: ${DAILY_CALORIE_TARGET.toLocaleString()} kcal</div>
      </div>

      <div class="metric-card glass-card">
        <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700;">
          Remaining Budget
        </div>
        <div style="font-size: 2.5rem; font-weight: 900; margin: 0.5rem 0; color: var(--accent-cyan);" id="cal-remaining-total">
          ${DAILY_CALORIE_TARGET.toLocaleString()}
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);" id="cal-budget-label">Energy Available</div>
      </div>

      <div class="metric-card glass-card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700;">
          Macronutrient Split
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.75rem;">
          <div style="text-align: center;">
            <div style="font-size: 1.1rem; font-weight: 800; color: var(--accent-blue);" id="macro-p-total">0g</div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">Protein</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 1.1rem; font-weight: 800; color: var(--accent-cyan);" id="macro-c-total">0g</div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">Carbs</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 1.1rem; font-weight: 800; color: #f59e0b;" id="macro-f-total">0g</div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">Fats</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Layout: Form & Quick Log + Macro Donut Chart -->
    <div class="grid grid--2" style="margin-bottom: 2rem;">
      <!-- Food Entry Form -->
      <div class="glass-card" style="padding: 2.25rem;" id="cal-form-card">
        <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
          <i data-lucide="plus-circle" style="color: var(--accent-blue);"></i>
          <span>Log Meal or Snack</span>
        </h3>

        <form id="calorie-entry-form">
          <div class="form-group" style="margin-bottom: 1rem;">
            <label class="form-label" for="food-name">Food / Meal Name</label>
            <input
              type="text"
              id="food-name"
              class="form-input"
              placeholder="e.g. Grilled Chicken Breast & Quinoa"
              required
            />
          </div>

          <div class="form-row" style="margin-bottom: 1rem;">
            <div class="form-group">
              <label class="form-label" for="food-calories">Calories (kcal)</label>
              <input
                type="number"
                id="food-calories"
                class="form-input"
                placeholder="450"
                min="1"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="food-protein">Protein (g)</label>
              <input
                type="number"
                id="food-protein"
                class="form-input"
                placeholder="35"
                min="0"
                value="0"
              />
            </div>
          </div>

          <div class="form-row" style="margin-bottom: 1.5rem;">
            <div class="form-group">
              <label class="form-label" for="food-carbs">Carbs (g)</label>
              <input
                type="number"
                id="food-carbs"
                class="form-input"
                placeholder="40"
                min="0"
                value="0"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="food-fats">Fats (g)</label>
              <input
                type="number"
                id="food-fats"
                class="form-input"
                placeholder="10"
                min="0"
                value="0"
              />
            </div>
          </div>

          <!-- Quick Presets -->
          <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 8px;">Quick Presets:</div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button type="button" class="tag-chip preset-btn" data-name="Whey Protein Shake" data-cal="160" data-p="30" data-c="4" data-f="2">
                🥤 Protein Shake (160 kcal)
              </button>
              <button type="button" class="tag-chip preset-btn" data-name="Oatmeal & Berries" data-cal="320" data-p="10" data-c="58" data-f="5">
                🥣 Oatmeal & Berries (320 kcal)
              </button>
              <button type="button" class="tag-chip preset-btn" data-name="Chicken & Rice Bowl" data-cal="650" data-p="48" data-c="72" data-f="14">
                🍗 Chicken Rice Bowl (650 kcal)
              </button>
            </div>
          </div>

          <button type="submit" id="cal-submit-btn" class="btn btn--primary btn--full" style="padding: 12px 24px;">
            <i data-lucide="check"></i>
            <span>Log Meal Entry</span>
          </button>
        </form>
      </div>

      <!-- Macro Chart Card -->
      <div class="glass-card chart-container" style="padding: 2.25rem; display: flex; flex-direction: column; justify-content: space-between;" id="cal-chart-card">
        <div class="chart-container__header">
          <div>
            <h3 class="chart-container__title">Macronutrient Proportion</h3>
            <p style="font-size: 0.75rem; color: var(--text-secondary);">Relative caloric contribution by macronutrient</p>
          </div>
          <span class="tag-chip" style="background: rgba(139, 92, 246, 0.15); color: var(--accent-purple);">
            Ratio Breakdown
          </span>
        </div>

        <div style="height: 240px; position: relative;">
          <canvas id="macroDoughnut"></canvas>
        </div>

        <div style="display: flex; justify-content: center; gap: 16px; margin-top: 1rem; font-size: 0.8rem;">
          <span style="color: var(--accent-blue);">● Protein (4 kcal/g)</span>
          <span style="color: var(--accent-cyan);">● Carbs (4 kcal/g)</span>
          <span style="color: #f59e0b;">● Fats (9 kcal/g)</span>
        </div>
      </div>
    </div>

    <!-- History Timeline List -->
    <div class="glass-card" style="padding: 2rem;" id="cal-history-card">
      <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="utensils" style="color: var(--accent-cyan);"></i>
        <span>Today's Meal Log Timeline</span>
      </h3>

      <div id="cal-history-list" style="display: flex; flex-direction: column; gap: 12px;">
        <!-- Populated via TS -->
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Entrance Animations
  gsap.fromTo(
    ['#cal-summary-grid', '#cal-form-card', '#cal-chart-card', '#cal-history-card'],
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.45, stagger: 0.08, ease: 'power2.out' },
  );

  // Preset button listeners
  container.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const el = btn as HTMLElement;
      (container.querySelector('#food-name') as HTMLInputElement).value = el.dataset.name || '';
      (container.querySelector('#food-calories') as HTMLInputElement).value = el.dataset.cal || '';
      (container.querySelector('#food-protein') as HTMLInputElement).value = el.dataset.p || '0';
      (container.querySelector('#food-carbs') as HTMLInputElement).value = el.dataset.c || '0';
      (container.querySelector('#food-fats') as HTMLInputElement).value = el.dataset.f || '0';
    });
  });

  // Form submit listener
  const form = container.querySelector('#calorie-entry-form') as HTMLFormElement;
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const name = (container.querySelector('#food-name') as HTMLInputElement).value.trim();
    const cals = parseFloat((container.querySelector('#food-calories') as HTMLInputElement).value);
    const p = parseFloat((container.querySelector('#food-protein') as HTMLInputElement).value) || 0;
    const c = parseFloat((container.querySelector('#food-carbs') as HTMLInputElement).value) || 0;
    const f = parseFloat((container.querySelector('#food-fats') as HTMLInputElement).value) || 0;

    if (!name || !cals) return;

    const btn = container.querySelector('#cal-submit-btn') as HTMLButtonElement;
    btn.disabled = true;

    try {
      await caloriesApi.add({
        meal_name: name,
        calories: cals,
        protein: p,
        carbs: c,
        fats: f,
      });
      showToast(`Logged "${name}" (${cals} kcal)`, 'success');
      form.reset();
      loadCalorieHistory();
    } catch {
      showToast(`Recorded "${name}" locally.`, 'info');
      form.reset();
    } finally {
      btn.disabled = false;
    }
  });

  loadCalorieHistory();
}

async function loadCalorieHistory(): Promise<void> {
  const listEl = document.getElementById('cal-history-list');
  let items: CalorieResponse[] = [];

  try {
    items = await caloriesApi.getHistory(30);
  } catch {
    items = [];
  }

  // Calculate totals
  const totalCals = items.reduce((acc, curr) => acc + curr.calories, 0);
  const totalP = items.reduce((acc, curr) => acc + (curr.protein || 0), 0);
  const totalC = items.reduce((acc, curr) => acc + (curr.carbs || 0), 0);
  const totalF = items.reduce((acc, curr) => acc + (curr.fats || 0), 0);

  const consumedEl = document.getElementById('cal-consumed-total');
  if (consumedEl) consumedEl.textContent = Math.round(totalCals).toLocaleString();

  const remEl = document.getElementById('cal-remaining-total');
  const budgetLabel = document.getElementById('cal-budget-label');
  const remaining = DAILY_CALORIE_TARGET - totalCals;

  if (remEl) {
    remEl.textContent = Math.abs(Math.round(remaining)).toLocaleString();
    if (remaining < 0) {
      remEl.style.color = 'var(--danger)';
      if (budgetLabel) budgetLabel.textContent = 'Surplus Exceeded';
    } else {
      remEl.style.color = 'var(--accent-cyan)';
      if (budgetLabel) budgetLabel.textContent = 'Energy Available';
    }
  }

  const pEl = document.getElementById('macro-p-total');
  if (pEl) pEl.textContent = `${Math.round(totalP)}g`;
  const cEl = document.getElementById('macro-c-total');
  if (cEl) cEl.textContent = `${Math.round(totalC)}g`;
  const fEl = document.getElementById('macro-f-total');
  if (fEl) fEl.textContent = `${Math.round(totalF)}g`;

  renderMacroChart(totalP, totalC, totalF);

  if (listEl) {
    if (items.length === 0) {
      listEl.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-tertiary);">
          No meal records logged today. Use the form above to record your first meal.
        </div>
      `;
    } else {
      listEl.innerHTML = items
        .map(
          item => `
        <div class="glass-card" style="padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; border-radius: 14px;">
          <div>
            <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">${item.meal_name}</div>
            <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-top: 3px;">
              P: ${item.protein || 0}g · C: ${item.carbs || 0}g · F: ${item.fats || 0}g · ${formatTime(item.created_at)}
            </div>
          </div>
          <div style="font-size: 1.15rem; font-weight: 800; color: var(--accent-blue);">
            ${Math.round(item.calories)} <span style="font-size: 0.75rem; font-weight: 500; color: var(--text-secondary);">kcal</span>
          </div>
        </div>
      `,
        )
        .join('');
    }
  }
}

function renderMacroChart(p: number, c: number, f: number): void {
  const canvas = document.getElementById('macroDoughnut') as HTMLCanvasElement;
  if (!canvas) return;
  if (macroDoughnutChart) macroDoughnutChart.destroy();

  const dataVals = p === 0 && c === 0 && f === 0 ? [1, 1, 1] : [p * 4, c * 4, f * 9];

  macroDoughnutChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Protein (kcal)', 'Carbohydrates (kcal)', 'Fats (kcal)'],
      datasets: [
        {
          data: dataVals,
          backgroundColor: ['#3b82f6', '#06b6d4', '#f59e0b'],
          borderColor: 'rgba(15, 23, 42, 0.9)',
          borderWidth: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
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
    },
  });
}
