// ============================================================
// FitAI – Water & Cellular Hydration Telemetry Studio
// ============================================================

import gsap from 'gsap';
import { waterApi } from '../api/water';
import type { WaterResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { formatTime } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

const DAILY_WATER_GOAL_L = 3.0;

export async function renderWaterPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/water'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Header -->
    <div class="page-header" style="margin-bottom: 2rem;">
      <h1 class="page-header__title">
        Cellular & Systemic <span class="navbar__logo-gradient">Hydration</span>
      </h1>
      <p class="page-header__subtitle">
        Maintain peak athletic performance, osmotic balance, and metabolic filtration
      </p>
    </div>

    <!-- Main Hydration Visualizer & Controls Grid -->
    <div class="grid grid--2" style="margin-bottom: 2rem;">
      <!-- Wave Tank Card -->
      <div class="glass-card" style="padding: 2.25rem; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; position: relative; overflow: hidden;" id="water-tank-card">
        <span style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-tertiary); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 1rem;">
          Today's Hydration Volume
        </span>

        <!-- Fluid Tank Graphic -->
        <div style="width: 180px; height: 260px; border-radius: 90px; border: 4px solid rgba(6, 182, 212, 0.4); position: relative; overflow: hidden; background: rgba(15, 23, 42, 0.6); box-shadow: 0 0 30px rgba(6, 182, 212, 0.15) inset;">
          <!-- Animated Liquid Fill -->
          <div id="water-fill-level" style="position: absolute; bottom: 0; left: 0; right: 0; height: 35%; background: linear-gradient(180deg, rgba(6, 182, 212, 0.8) 0%, rgba(59, 130, 246, 0.9) 100%); transition: height 0.8s cubic-bezier(0.34, 1.56, 0.64, 1); box-shadow: 0 0 20px rgba(6, 182, 212, 0.6);">
            <div style="position: absolute; top: -10px; left: 0; right: 0; height: 20px; background: rgba(255,255,255,0.3); border-radius: 50%; opacity: 0.7;"></div>
          </div>

          <!-- Counter Text Overlay -->
          <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 2; pointer-events: none;">
            <div style="font-size: 3rem; font-weight: 900; line-height: 1; color: #fff; text-shadow: 0 2px 10px rgba(0,0,0,0.7);" id="water-liters-text">
              0.00
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; color: rgba(255,255,255,0.85); margin-top: 4px;">
              Liters
            </div>
            <div style="font-size: 0.75rem; color: rgba(255,255,255,0.65); margin-top: 2px;" id="water-pct-text">
              0% of 3.0L
            </div>
          </div>
        </div>

        <div style="margin-top: 1.5rem; display: flex; gap: 16px; font-size: 0.85rem; color: var(--text-secondary);">
          <span>🎯 Goal: <strong>${DAILY_WATER_GOAL_L.toFixed(1)} Liters</strong></span>
          <span>🥛 Glasses: <strong id="water-glasses-count">0</strong></span>
        </div>
      </div>

      <!-- Quick Log & Custom Entry Card -->
      <div class="glass-card" style="padding: 2.25rem; display: flex; flex-direction: column; justify-content: space-between;" id="water-actions-card">
        <div>
          <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="droplet" style="color: var(--accent-cyan);"></i>
            <span>Log Hydration Intake</span>
          </h3>

          <!-- Quick Increment Buttons -->
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 2rem;">
            <button type="button" class="btn btn--secondary quick-water-btn" data-liters="0.25" data-glasses="1" style="padding: 16px; flex-direction: column; gap: 4px;">
              <span style="font-size: 1.2rem; font-weight: 800; color: var(--accent-cyan);">+250 mL</span>
              <span style="font-size: 0.75rem; color: var(--text-tertiary);">1 Small Glass</span>
            </button>
            <button type="button" class="btn btn--secondary quick-water-btn" data-liters="0.50" data-glasses="2" style="padding: 16px; flex-direction: column; gap: 4px;">
              <span style="font-size: 1.2rem; font-weight: 800; color: var(--accent-blue);">+500 mL</span>
              <span style="font-size: 0.75rem; color: var(--text-tertiary);">Standard Bottle</span>
            </button>
            <button type="button" class="btn btn--secondary quick-water-btn" data-liters="0.75" data-glasses="3" style="padding: 16px; flex-direction: column; gap: 4px;">
              <span style="font-size: 1.2rem; font-weight: 800; color: var(--accent-purple);">+750 mL</span>
              <span style="font-size: 0.75rem; color: var(--text-tertiary);">Sports Flask</span>
            </button>
            <button type="button" class="btn btn--secondary quick-water-btn" data-liters="1.00" data-glasses="4" style="padding: 16px; flex-direction: column; gap: 4px;">
              <span style="font-size: 1.2rem; font-weight: 800; color: var(--success);">+1,000 mL</span>
              <span style="font-size: 0.75rem; color: var(--text-tertiary);">Hydration Jug</span>
            </button>
          </div>

          <!-- Custom Volume Form -->
          <form id="custom-water-form">
            <label class="form-label" for="custom-water-input">Custom Volume (mL)</label>
            <div style="display: flex; gap: 8px;">
              <input
                type="number"
                id="custom-water-input"
                class="form-input"
                placeholder="350"
                min="50"
                max="3000"
                step="50"
                required
              />
              <button type="submit" class="btn btn--primary" style="white-space: nowrap; padding: 0 20px;">
                <i data-lucide="plus"></i>
                <span>Add</span>
              </button>
            </div>
          </form>
        </div>

        <div style="padding-top: 1.5rem; border-top: 1px solid var(--glass-border); margin-top: 1.5rem; font-size: 0.78rem; color: var(--text-tertiary); line-height: 1.5;">
          💡 <em>Olympic Guideline</em>: Ingest 500 mL 2 hours before high-intensity workouts and replace 250 mL per 30 minutes of heavy sweating.
        </div>
      </div>
    </div>

    <!-- History Log Table -->
    <div class="glass-card" style="padding: 2rem;" id="water-history-card">
      <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="history" style="color: var(--accent-cyan);"></i>
        <span>Today's Intake Timestamp Log</span>
      </h3>

      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
          <thead>
            <tr style="border-bottom: 1px solid var(--glass-border); color: var(--text-tertiary); font-size: 0.75rem; text-transform: uppercase;">
              <th style="padding: 12px 16px;">Time</th>
              <th style="padding: 12px 16px;">Volume (Liters)</th>
              <th style="padding: 12px 16px;">Volume (mL)</th>
              <th style="padding: 12px 16px;">Glasses</th>
            </tr>
          </thead>
          <tbody id="water-history-tbody">
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
    ['#water-tank-card', '#water-actions-card', '#water-history-card'],
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.45, stagger: 0.08, ease: 'power2.out' },
  );

  // Quick buttons listeners
  container.querySelectorAll('.quick-water-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const el = btn as HTMLElement;
      const liters = parseFloat(el.dataset.liters || '0.25');
      const glasses = parseInt(el.dataset.glasses || '1', 10);
      await logWaterIntake(liters, glasses);
    });
  });

  // Custom form listener
  const form = container.querySelector('#custom-water-form') as HTMLFormElement;
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const mlInput = container.querySelector('#custom-water-input') as HTMLInputElement;
    const ml = parseFloat(mlInput.value);
    if (!ml) return;
    const liters = ml / 1000.0;
    const glasses = Math.max(1, Math.round(ml / 250));
    await logWaterIntake(liters, glasses);
    mlInput.value = '';
  });

  loadWaterHistory();
}

async function logWaterIntake(liters: number, glasses: number): Promise<void> {
  try {
    await waterApi.add({ liters, glasses });
    showToast(`Logged +${liters >= 1 ? `${liters}L` : `${Math.round(liters * 1000)}mL`} water!`, 'success');
    loadWaterHistory();
  } catch {
    showToast(`Added +${liters}L locally.`, 'info');
  }
}

async function loadWaterHistory(): Promise<void> {
  const tbody = document.getElementById('water-history-tbody');
  let items: WaterResponse[] = [];

  try {
    items = await waterApi.getHistory(30);
  } catch {
    items = [];
  }

  const totalLiters = items.reduce((acc, curr) => acc + curr.liters, 0);
  const totalGlasses = items.reduce((acc, curr) => acc + curr.glasses, 0);

  const fillEl = document.getElementById('water-fill-level');
  const litersEl = document.getElementById('water-liters-text');
  const pctEl = document.getElementById('water-pct-text');
  const glassesEl = document.getElementById('water-glasses-count');

  if (litersEl) litersEl.textContent = totalLiters.toFixed(2);
  if (glassesEl) glassesEl.textContent = `${totalGlasses}`;

  const pct = Math.min(100, Math.round((totalLiters / DAILY_WATER_GOAL_L) * 100));
  if (pctEl) pctEl.textContent = `${pct}% of ${DAILY_WATER_GOAL_L}L`;

  if (fillEl) {
    fillEl.style.height = `${Math.max(8, pct)}%`;
  }

  if (tbody) {
    if (items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" style="padding: 2rem; text-align: center; color: var(--text-tertiary);">
            No hydration entries logged today. Click an intake button above to hydrate.
          </td>
        </tr>
      `;
    } else {
      tbody.innerHTML = items
        .map(
          item => `
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
          <td style="padding: 12px 16px; color: var(--text-secondary);">${formatTime(item.created_at)}</td>
          <td style="padding: 12px 16px; font-weight: 700; color: var(--accent-cyan);">${item.liters.toFixed(2)} L</td>
          <td style="padding: 12px 16px;">${Math.round(item.liters * 1000)} mL</td>
          <td style="padding: 12px 16px;">🥛 ${item.glasses}</td>
        </tr>
      `,
        )
        .join('');
    }
  }
}
