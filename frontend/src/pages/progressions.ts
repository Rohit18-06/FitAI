// ============================================================
// FitAI – Progressive Overload & 1RM Tracker Page
// Phase 8: Log strength progressions, Brzycki 1RM formula,
// RPE rating, and progressive overload history
// ============================================================
import { trainingApi } from '../api/training';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';

export async function renderProgressionsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/progressions'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-header__title">
        Progressive Overload & <span class="navbar__logo-gradient">1RM Radar</span>
      </h1>
      <p class="page-header__subtitle">
        Track barbell strength gains, log sets/reps/RPE, and automatically project 1-Rep Max benchmarks
      </p>
    </div>

    <!-- Quick Log Lift & 1RM Estimator Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Log Form -->
      <div class="card glass-card" style="padding: 1.75rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0 0 1.25rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="plus-circle" style="width: 20px; height: 20px; color: var(--accent);"></i>
          <span>Log Set & Overload</span>
        </h3>

        <form id="progression-form">
          <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Exercise</label>
            <input type="text" id="log-exercise" placeholder="e.g. Barbell Bench Press" required class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Weight (kg)</label>
              <input type="number" id="log-weight" step="0.5" placeholder="80" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Reps</label>
              <input type="number" id="log-reps" value="8" min="1" max="50" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Sets</label>
              <input type="number" id="log-sets" value="3" min="1" max="10" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">RPE (1-10)</label>
              <input type="number" id="log-rpe" step="0.5" min="1" max="10" placeholder="8.0" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <button type="submit" id="btn-submit-progression" class="btn btn-primary" style="width: 100%; padding: 0.8rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            <i data-lucide="check" style="width: 16px; height: 16px;"></i>
            <span>Log Lift Record</span>
          </button>
        </form>
      </div>

      <!-- Live 1RM Calculator Preview Card -->
      <div class="card glass-card" style="padding: 1.75rem; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid var(--accent);">
        <div>
          <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <i data-lucide="gauge" style="width: 20px; height: 20px; color: var(--accent);"></i>
            <span>1RM Live Projector</span>
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.5rem; line-height: 1.4;">
            Calculated via the sports-science <strong>Brzycki Formula</strong> (weight × 36 / (37 - reps)).
          </p>

          <div style="text-align: center; padding: 2rem 1rem; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 700; margin-bottom: 0.25rem;">Estimated 1-Rep Max</div>
            <div id="live-1rm-val" style="font-size: 3rem; font-weight: 800; color: var(--accent); line-height: 1.1;">--</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary);">kilograms</div>
          </div>
        </div>

        <div style="margin-top: 1.5rem; font-size: 0.8rem; color: var(--text-secondary); border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem;">
          💡 Pro Tip: For compound lifts (squats, bench, deadlifts), keeping RPE between 7.5 and 8.5 optimizes neuromuscular adaptation without systemic CNS burnout.
        </div>
      </div>
    </div>

    <!-- History Table Card -->
    <div class="card glass-card" style="padding: 1.75rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="history" style="width: 20px; height: 20px; color: #10B981;"></i>
          <span>Progression History</span>
        </h3>
        <input type="text" id="filter-exercise" placeholder="Filter by exercise name..." class="input-field" style="padding: 0.5rem 0.75rem; font-size: 0.85rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); width: 220px;" />
      </div>

      <div id="progression-history-container">
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
          <div class="spinner" style="margin: 0 auto 1rem;"></div>
          <p>Loading progressions...</p>
        </div>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons();

  // Setup Live 1RM preview
  const weightInput = container.querySelector('#log-weight') as HTMLInputElement;
  const repsInput = container.querySelector('#log-reps') as HTMLInputElement;
  const live1rmEl = container.querySelector('#live-1rm-val') as HTMLElement;

  function updateLive1RM() {
    const w = parseFloat(weightInput.value) || 0;
    const r = parseInt(repsInput.value, 10) || 0;
    if (w > 0 && r > 0 && r < 37) {
      const est = Math.round(w * (36.0 / (37.0 - r)) * 10) / 10;
      live1rmEl.textContent = `${est}`;
    } else {
      live1rmEl.textContent = '--';
    }
  }

  weightInput.addEventListener('input', updateLive1RM);
  repsInput.addEventListener('input', updateLive1RM);

  // Form submit
  const form = container.querySelector('#progression-form') as HTMLFormElement;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('#btn-submit-progression') as HTMLButtonElement;
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>';

    try {
      const exercise_name = (form.querySelector('#log-exercise') as HTMLInputElement).value;
      const weight_kg = parseFloat((form.querySelector('#log-weight') as HTMLInputElement).value) || undefined;
      const reps = parseInt((form.querySelector('#log-reps') as HTMLInputElement).value, 10) || 10;
      const sets = parseInt((form.querySelector('#log-sets') as HTMLInputElement).value, 10) || 3;
      const rpe = parseFloat((form.querySelector('#log-rpe') as HTMLInputElement).value) || undefined;

      await trainingApi.logProgression({
        exercise_name,
        weight_kg,
        reps,
        sets,
        rpe,
      });

      form.reset();
      updateLive1RM();
      await loadHistory(container);
    } catch {
      alert('Could not log progression.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="check" style="width: 16px; height: 16px;"></i><span>Log Lift Record</span>';
      refreshIcons();
    }
  });

  // Filter input
  const filterInput = container.querySelector('#filter-exercise') as HTMLInputElement;
  filterInput.addEventListener('input', () => {
    loadHistory(container, filterInput.value.trim());
  });

  await loadHistory(container);
}

async function loadHistory(container: HTMLElement, filter?: string): Promise<void> {
  const histContainer = container.querySelector('#progression-history-container');
  if (!histContainer) return;

  try {
    const list = await trainingApi.getProgressions(filter || undefined);
    if (list.length === 0) {
      histContainer.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
          <p>No progression entries recorded yet. Use the form above to log your first lift!</p>
        </div>
      `;
      return;
    }

    histContainer.innerHTML = `
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
          <thead>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.08); color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase;">
              <th style="padding: 0.75rem 1rem;">Exercise</th>
              <th style="padding: 0.75rem 1rem;">Weight</th>
              <th style="padding: 0.75rem 1rem;">Sets × Reps</th>
              <th style="padding: 0.75rem 1rem;">Est. 1RM</th>
              <th style="padding: 0.75rem 1rem;">RPE</th>
              <th style="padding: 0.75rem 1rem;">Date</th>
            </tr>
          </thead>
          <tbody>
            ${list
              .map(
                (p) => `
              <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.2s;">
                <td style="padding: 0.85rem 1rem; font-weight: 600; color: #fff;">${p.exercise_name}</td>
                <td style="padding: 0.85rem 1rem;">${p.weight_kg != null ? `${p.weight_kg} kg` : '--'}</td>
                <td style="padding: 0.85rem 1rem; color: var(--text-secondary);">${p.sets} × ${p.reps}</td>
                <td style="padding: 0.85rem 1rem; font-weight: 700; color: var(--accent);">
                  ${p.one_rep_max_est != null ? `${p.one_rep_max_est} kg` : '--'}
                </td>
                <td style="padding: 0.85rem 1rem;">
                  ${
                    p.rpe != null
                      ? `<span class="badge" style="background: rgba(59, 130, 246, 0.15); color: var(--accent); padding: 0.2rem 0.5rem; border-radius: 6px; font-size: 0.75rem;">@ ${p.rpe}</span>`
                      : '--'
                  }
                </td>
                <td style="padding: 0.85rem 1rem; color: var(--text-secondary); font-size: 0.8rem;">
                  ${new Date(p.recorded_at).toLocaleDateString()}
                </td>
              </tr>
            `
              )
              .join('')}
          </tbody>
        </table>
      </div>
    `;
    refreshIcons();
  } catch {
    histContainer.innerHTML = '<p style="color: var(--danger); text-align: center;">Failed to load progression history.</p>';
  }
}
