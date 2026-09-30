// ============================================================
// FitAI – Body Composition & Goals Page
// Phase 8: Goal Tracking, Body Measurements, Progress Photos,
// and Physical Transformation Telemetry
// ============================================================
import { trainingApi } from '../api/training';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';

export async function renderBodyGoalsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/body-goals'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          Body Composition & <span class="navbar__logo-gradient">Goals</span>
        </h1>
        <p class="page-header__subtitle">
          Track body measurements, set ambitious milestones, and monitor physique progression
        </p>
      </div>
      <div style="display: flex; gap: 0.75rem;">
        <button id="btn-open-goal-modal" class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="target" style="width: 18px; height: 18px;"></i>
          <span>Create New Goal</span>
        </button>
        <button id="btn-open-measure-modal" class="btn btn-secondary" style="display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="ruler" style="width: 18px; height: 18px;"></i>
          <span>Log Measurements</span>
        </button>
      </div>
    </div>

    <!-- Create Goal Modal -->
    <div id="goal-modal" class="modal-backdrop" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(8px); z-index: 9999; align-items: center; justify-content: center; padding: 1rem;">
      <div class="card glass-card" style="max-width: 480px; width: 100%; border: 1px solid rgba(255,255,255,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <i data-lucide="target" style="width: 20px; height: 20px; color: var(--accent);"></i>
            <span>Set New Fitness Goal</span>
          </h3>
          <button id="btn-close-goal-modal" style="background: none; border: none; color: var(--text-secondary); cursor: pointer;">
            <i data-lucide="x" style="width: 20px; height: 20px;"></i>
          </button>
        </div>

        <form id="goal-form">
          <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Goal Type</label>
            <select id="goal-type" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);">
              <option value="weight_loss">Weight Loss</option>
              <option value="muscle_gain">Muscle Building</option>
              <option value="strength">Strength Milestone</option>
              <option value="endurance">Endurance Milestone</option>
            </select>
          </div>

          <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Title</label>
            <input type="text" id="goal-title" placeholder="e.g. Cut to 75 kg with 12% body fat" required class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Start</label>
              <input type="number" id="goal-start" step="0.1" placeholder="85" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Target</label>
              <input type="number" id="goal-target" step="0.1" placeholder="75" required class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Unit</label>
              <input type="text" id="goal-unit" value="kg" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <button type="submit" id="btn-submit-goal" class="btn btn-primary" style="width: 100%; padding: 0.8rem; font-weight: 600;">
            Save Fitness Goal
          </button>
        </form>
      </div>
    </div>

    <!-- Log Measurements Modal -->
    <div id="measure-modal" class="modal-backdrop" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(8px); z-index: 9999; align-items: center; justify-content: center; padding: 1rem;">
      <div class="card glass-card" style="max-width: 480px; width: 100%; border: 1px solid rgba(255,255,255,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h3 style="font-size: 1.25rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <i data-lucide="ruler" style="width: 20px; height: 20px; color: #10B981;"></i>
            <span>Log Body Measurements</span>
          </h3>
          <button id="btn-close-measure-modal" style="background: none; border: none; color: var(--text-secondary); cursor: pointer;">
            <i data-lucide="x" style="width: 20px; height: 20px;"></i>
          </button>
        </div>

        <form id="measure-form">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Weight (kg)</label>
              <input type="number" id="m-weight" step="0.1" placeholder="78.5" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Body Fat (%)</label>
              <input type="number" id="m-fat" step="0.1" placeholder="14.5" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Chest (cm)</label>
              <input type="number" id="m-chest" step="0.5" placeholder="102" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Waist (cm)</label>
              <input type="number" id="m-waist" step="0.5" placeholder="81" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Arms (cm)</label>
              <input type="number" id="m-arms" step="0.5" placeholder="38" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">Thighs (cm)</label>
              <input type="number" id="m-thighs" step="0.5" placeholder="58" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <button type="submit" id="btn-submit-measure" class="btn btn-primary" style="width: 100%; padding: 0.8rem; font-weight: 600;">
            Record Measurements
          </button>
        </form>
      </div>
    </div>

    <!-- Active Goals Section -->
    <div style="margin-bottom: 2.5rem;">
      <h2 style="font-size: 1.35rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
        <i data-lucide="flag" style="width: 22px; height: 22px; color: var(--accent);"></i>
        <span>Active Milestones & Goals</span>
      </h2>
      <div id="goals-list-container">
        <div class="card glass-card" style="padding: 2.5rem; text-align: center;">
          <div class="spinner" style="margin: 0 auto 1rem;"></div>
          <p style="color: var(--text-secondary);">Loading goals...</p>
        </div>
      </div>
    </div>

    <!-- Measurements & Progress Photos Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
      <!-- Latest Measurements Snapshot -->
      <div class="card glass-card" style="padding: 1.75rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0 0 1.25rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="ruler" style="width: 20px; height: 20px; color: #10B981;"></i>
          <span>Biometric Measurements</span>
        </h3>
        <div id="measurements-container">
          <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">Loading measurements...</div>
        </div>
      </div>

      <!-- Progress Photos Snapshot -->
      <div class="card glass-card" style="padding: 1.75rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0 0 1.25rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="camera" style="width: 20px; height: 20px; color: #EC4899;"></i>
          <span>Transformation Photos</span>
        </h3>
        <div id="photos-container">
          <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">Loading progress photos...</div>
        </div>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons();

  // Modal toggle wiring
  const goalModal = container.querySelector('#goal-modal') as HTMLElement;
  const measureModal = container.querySelector('#measure-modal') as HTMLElement;

  container.querySelector('#btn-open-goal-modal')?.addEventListener('click', () => {
    goalModal.style.display = 'flex';
    refreshIcons();
  });
  container.querySelector('#btn-close-goal-modal')?.addEventListener('click', () => {
    goalModal.style.display = 'none';
  });

  container.querySelector('#btn-open-measure-modal')?.addEventListener('click', () => {
    measureModal.style.display = 'flex';
    refreshIcons();
  });
  container.querySelector('#btn-close-measure-modal')?.addEventListener('click', () => {
    measureModal.style.display = 'none';
  });

  // Goal Form submit
  const goalForm = container.querySelector('#goal-form') as HTMLFormElement;
  goalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const goal_type = (goalForm.querySelector('#goal-type') as HTMLSelectElement).value;
      const title = (goalForm.querySelector('#goal-title') as HTMLInputElement).value;
      const start_value = parseFloat((goalForm.querySelector('#goal-start') as HTMLInputElement).value) || undefined;
      const target_value = parseFloat((goalForm.querySelector('#goal-target') as HTMLInputElement).value) || undefined;
      const unit = (goalForm.querySelector('#goal-unit') as HTMLInputElement).value || 'kg';

      await trainingApi.createGoal({
        goal_type,
        title,
        start_value,
        target_value,
        unit,
      });

      goalModal.style.display = 'none';
      goalForm.reset();
      await loadGoals(container);
    } catch {
      alert('Could not save goal.');
    }
  });

  // Measurement Form submit
  const measureForm = container.querySelector('#measure-form') as HTMLFormElement;
  measureForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const weight_kg = parseFloat((measureForm.querySelector('#m-weight') as HTMLInputElement).value) || undefined;
      const body_fat_pct = parseFloat((measureForm.querySelector('#m-fat') as HTMLInputElement).value) || undefined;
      const chest_cm = parseFloat((measureForm.querySelector('#m-chest') as HTMLInputElement).value) || undefined;
      const waist_cm = parseFloat((measureForm.querySelector('#m-waist') as HTMLInputElement).value) || undefined;
      const left_arm_cm = parseFloat((measureForm.querySelector('#m-arms') as HTMLInputElement).value) || undefined;
      const left_thigh_cm = parseFloat((measureForm.querySelector('#m-thighs') as HTMLInputElement).value) || undefined;

      await trainingApi.addMeasurement({
        weight_kg,
        body_fat_pct,
        chest_cm,
        waist_cm,
        left_arm_cm,
        left_thigh_cm,
      });

      measureModal.style.display = 'none';
      measureForm.reset();
      await loadMeasurements(container);
    } catch {
      alert('Could not record measurements.');
    }
  });

  await Promise.all([loadGoals(container), loadMeasurements(container), loadPhotos(container)]);
}

async function loadGoals(container: HTMLElement): Promise<void> {
  const gContainer = container.querySelector('#goals-list-container');
  if (!gContainer) return;

  try {
    const goals = await trainingApi.listGoals();
    if (goals.length === 0) {
      gContainer.innerHTML = `
        <div class="card glass-card" style="padding: 2.5rem; text-align: center; color: var(--text-secondary);">
          <p>No fitness goals set yet. Click "Create New Goal" above to define your targets!</p>
        </div>
      `;
      return;
    }

    gContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem;">
        ${goals
          .map(
            (g) => `
          <div class="card glass-card" style="padding: 1.5rem; border-left: 4px solid ${
            g.status === 'completed' ? '#10B981' : 'var(--accent)'
          };">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
              <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase;">
                ${g.goal_type.replace('_', ' ')}
              </span>
              <span class="badge" style="background: ${
                g.status === 'completed' ? 'rgba(16,185,129,0.15)' : 'rgba(59,130,246,0.15)'
              }; color: ${
                g.status === 'completed' ? '#10B981' : 'var(--accent)'
              }; font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 9999px;">
                ${g.status.toUpperCase()}
              </span>
            </div>

            <h4 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 1rem 0;">${g.title}</h4>

            <div style="margin-bottom: 0.75rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem;">
                <span style="color: var(--text-secondary);">Progress</span>
                <span style="font-weight: 700; color: #fff;">${g.completion_pct}%</span>
              </div>
              <div style="width: 100%; height: 7px; background: rgba(255,255,255,0.08); border-radius: 9999px; overflow: hidden;">
                <div style="height: 100%; width: ${g.completion_pct}%; background: linear-gradient(90deg, var(--accent), #10B981); border-radius: 9999px;"></div>
              </div>
            </div>

            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
              <span>Current: <strong>${g.current_value} ${g.unit || ''}</strong></span>
              <span>Target: <strong>${g.target_value ?? '--'} ${g.unit || ''}</strong></span>
            </div>

            <!-- Quick update form -->
            <div style="display: flex; gap: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.75rem;">
              <input type="number" step="0.1" placeholder="New value" class="quick-val-input" data-goal-id="${g.id}" style="flex: 1; padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.85rem; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
              <button class="btn btn-secondary btn-update-goal" data-goal-id="${g.id}" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">
                Update
              </button>
            </div>
          </div>
        `
          )
          .join('')}
      </div>
    `;

    // Attach quick update buttons
    gContainer.querySelectorAll('.btn-update-goal').forEach((btn) => {
      btn.addEventListener('click', async (e) => {
        const goalId = parseInt((e.currentTarget as HTMLElement).getAttribute('data-goal-id') || '0', 10);
        const input = gContainer.querySelector(`.quick-val-input[data-goal-id="${goalId}"]`) as HTMLInputElement;
        const newVal = parseFloat(input?.value);
        if (!isNaN(newVal) && goalId) {
          try {
            await trainingApi.updateGoalProgress(goalId, newVal);
            await loadGoals(container);
          } catch {
            alert('Could not update goal.');
          }
        }
      });
    });
  } catch {
    gContainer.innerHTML = '<p style="color: var(--danger); text-align: center;">Failed to load goals.</p>';
  }
}

async function loadMeasurements(container: HTMLElement): Promise<void> {
  const mContainer = container.querySelector('#measurements-container');
  if (!mContainer) return;

  try {
    const latest = await trainingApi.getLatestMeasurement();
    if (!latest) {
      mContainer.innerHTML = `
        <div style="text-align: center; padding: 1.5rem; color: var(--text-secondary); font-size: 0.9rem;">
          No measurements logged yet. Click "Log Measurements" above to record your current metrics.
        </div>
      `;
      return;
    }

    mContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem;">
        <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px;">
          <div style="font-size: 0.75rem; color: var(--text-secondary);">Weight</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #fff;">${latest.weight_kg != null ? `${latest.weight_kg} kg` : '--'}</div>
        </div>
        <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px;">
          <div style="font-size: 0.75rem; color: var(--text-secondary);">Body Fat</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #fff;">${latest.body_fat_pct != null ? `${latest.body_fat_pct}%` : '--'}</div>
        </div>
        <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px;">
          <div style="font-size: 0.75rem; color: var(--text-secondary);">Chest</div>
          <div style="font-size: 1.1rem; font-weight: 600;">${latest.chest_cm != null ? `${latest.chest_cm} cm` : '--'}</div>
        </div>
        <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px;">
          <div style="font-size: 0.75rem; color: var(--text-secondary);">Waist</div>
          <div style="font-size: 1.1rem; font-weight: 600;">${latest.waist_cm != null ? `${latest.waist_cm} cm` : '--'}</div>
        </div>
      </div>
      <div style="font-size: 0.8rem; color: var(--text-secondary); text-align: right;">
        Logged: ${new Date(latest.measured_at).toLocaleDateString()}
      </div>
    `;
  } catch {
    mContainer.innerHTML = '<p style="color: var(--danger); text-align: center;">Failed to load measurements.</p>';
  }
}

async function loadPhotos(container: HTMLElement): Promise<void> {
  const pContainer = container.querySelector('#photos-container');
  if (!pContainer) return;

  try {
    const photos = await trainingApi.listProgressPhotos(6);
    if (photos.length === 0) {
      pContainer.innerHTML = `
        <div style="text-align: center; padding: 1.5rem; color: var(--text-secondary); font-size: 0.9rem;">
          No progress photos saved yet. Track your weekly physique changes with private photos and AI body composition insights.
        </div>
      `;
      return;
    }

    pContainer.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;">
        ${photos
          .map(
            (p) => `
          <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 0.75rem; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
            <div style="width: 100%; aspect-ratio: 1; border-radius: 6px; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem; color: var(--text-secondary);">
              <i data-lucide="image" style="width: 24px; height: 24px;"></i>
            </div>
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">${p.photo_type}</div>
            <div style="font-size: 0.7rem; color: var(--text-secondary);">${new Date(p.taken_at).toLocaleDateString()}</div>
          </div>
        `
          )
          .join('')}
      </div>
    `;
    refreshIcons();
  } catch {
    pContainer.innerHTML = '<p style="color: var(--danger); text-align: center;">Failed to load photos.</p>';
  }
}
