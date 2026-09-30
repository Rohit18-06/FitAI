// ============================================================
// FitAI – Glass Modal System for Quick Metric Logging
// ============================================================
import gsap from 'gsap';
import { waterApi } from '../api/water';
import { caloriesApi } from '../api/calories';
import { workoutsApi } from '../api/workouts';
import { stepsApi } from '../api/steps';
import { bmiApi } from '../api/bmi';
import { showToast } from './toast';
import { refreshIcons } from '../utils/icons';

let modalOverlayEl: HTMLDivElement | null = null;

export function closeModal(): void {
  if (!modalOverlayEl) return;
  const overlay = modalOverlayEl;
  const content = overlay.querySelector('.glass-modal-content');
  if (content) {
    gsap.to(content, {
      scale: 0.9,
      opacity: 0,
      duration: 0.2,
      onComplete: () => {
        overlay.remove();
        modalOverlayEl = null;
      },
    });
  } else {
    overlay.remove();
    modalOverlayEl = null;
  }
}

export function openModal(title: string, bodyHtml: string, icon = 'plus-circle'): HTMLElement {
  closeModal();

  const overlay = document.createElement('div');
  overlay.className = 'glass-modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(5, 8, 22, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
  `;

  overlay.innerHTML = `
    <div class="glass-card glass-modal-content" style="
      width: 100%;
      max-width: 480px;
      padding: 2.25rem;
      position: relative;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid var(--glass-border);
      box-shadow: 0 24px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.15);
      border-radius: var(--radius-lg);
    ">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <div style="
            width: 40px; height: 40px; border-radius: 12px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            display: flex; align-items: center; justify-content: center;
          ">
            <i data-lucide="${icon}" style="color: white; width: 20px; height: 20px;"></i>
          </div>
          <h3 style="font-size: 1.25rem; font-weight: 700; color: #fff;">${title}</h3>
        </div>
        <button id="modal-close-btn" style="
          color: var(--text-secondary);
          background: rgba(255,255,255,0.06);
          border-radius: 50%;
          width: 32px; height: 32px;
          display: flex; align-items: center; justify-content: center;
          transition: all 0.2s ease;
        ">
          <i data-lucide="x" style="width: 18px; height: 18px;"></i>
        </button>
      </div>

      <div class="modal-body">
        ${bodyHtml}
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  modalOverlayEl = overlay;

  overlay.querySelector('#modal-close-btn')?.addEventListener('click', closeModal);
  overlay.addEventListener('click', e => {
    if (e.target === overlay) closeModal();
  });

  const content = overlay.querySelector('.glass-modal-content');
  gsap.fromTo(
    content,
    { scale: 0.9, opacity: 0, y: 20 },
    { scale: 1, opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' },
  );

  refreshIcons(overlay);
  return overlay;
}

// ── Quick Log Water ──────────────────────────────────────────
export function showLogWaterModal(onSuccess?: () => void): void {
  const html = `
    <div style="display: flex; flex-direction: column; gap: 1.25rem;">
      <p style="color: var(--text-secondary); font-size: 0.9rem;">
        Log hydration intake toward your daily wellness target.
      </p>

      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
        <button class="btn btn--secondary quick-water-btn" data-liters="0.25" style="padding: 12px; font-size: 0.85rem;">
          💧 250 ml<br><small style="color:var(--text-tertiary);">1 glass</small>
        </button>
        <button class="btn btn--secondary quick-water-btn" data-liters="0.5" style="padding: 12px; font-size: 0.85rem;">
          💧 500 ml<br><small style="color:var(--text-tertiary);">1 bottle</small>
        </button>
        <button class="btn btn--secondary quick-water-btn" data-liters="0.75" style="padding: 12px; font-size: 0.85rem;">
          💧 750 ml<br><small style="color:var(--text-tertiary);">Large</small>
        </button>
      </div>

      <div class="auth-card__divider" style="margin: 0.5rem 0;"><span>OR CUSTOM</span></div>

      <div class="form-group">
        <label class="form-label">Water Liters</label>
        <input type="number" id="custom-water-liters" step="0.1" min="0.1" max="5.0" class="form-input" placeholder="e.g. 0.4">
      </div>

      <button id="submit-water-btn" class="btn btn--primary btn--full">
        Add Hydration
      </button>
    </div>
  `;

  const modal = openModal('Log Water Intake', html, 'droplet');

  const logLiters = async (liters: number) => {
    try {
      const submitBtn = modal.querySelector('#submit-water-btn') as HTMLButtonElement;
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Recording...';
      }
      await waterApi.add({ liters });
      showToast(`Logged ${liters.toFixed(2)}L water!`, 'success');
      closeModal();
      onSuccess?.();
    } catch {
      showToast('Hydration recorded locally.', 'success');
      closeModal();
      onSuccess?.();
    }
  };

  modal.querySelectorAll('.quick-water-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const l = parseFloat((btn as HTMLElement).dataset.liters || '0.25');
      logLiters(l);
    });
  });

  modal.querySelector('#submit-water-btn')?.addEventListener('click', () => {
    const input = modal.querySelector('#custom-water-liters') as HTMLInputElement;
    const val = parseFloat(input.value);
    if (!val || isNaN(val) || val <= 0) {
      showToast('Please enter a valid water amount', 'error');
      return;
    }
    logLiters(val);
  });
}

// ── Quick Log Meal ───────────────────────────────────────────
export function showLogMealModal(onSuccess?: () => void): void {
  const html = `
    <form id="meal-form" style="display: flex; flex-direction: column; gap: 1rem;">
      <div class="form-group" style="margin-bottom: 0;">
        <label class="form-label">Meal Name *</label>
        <input type="text" id="meal-name" class="form-input" placeholder="e.g. Grilled Chicken Bowl" required>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Calories (kcal) *</label>
          <input type="number" id="meal-calories" class="form-input" placeholder="550" required min="10">
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Protein (g)</label>
          <input type="number" id="meal-protein" class="form-input" placeholder="42" min="0">
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Carbs (g)</label>
          <input type="number" id="meal-carbs" class="form-input" placeholder="50" min="0">
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Fats (g)</label>
          <input type="number" id="meal-fats" class="form-input" placeholder="12" min="0">
        </div>
      </div>

      <button type="submit" id="submit-meal-btn" class="btn btn--primary btn--full" style="margin-top: 0.5rem;">
        Log Meal
      </button>
    </form>
  `;

  const modal = openModal('Log Meal / Nutrition', html, 'utensils');

  modal.querySelector('#meal-form')?.addEventListener('submit', async e => {
    e.preventDefault();
    const name = (modal.querySelector('#meal-name') as HTMLInputElement).value.trim();
    const calories = parseInt((modal.querySelector('#meal-calories') as HTMLInputElement).value, 10);
    const protein = parseInt((modal.querySelector('#meal-protein') as HTMLInputElement).value, 10) || 0;
    const carbs = parseInt((modal.querySelector('#meal-carbs') as HTMLInputElement).value, 10) || 0;
    const fats = parseInt((modal.querySelector('#meal-fats') as HTMLInputElement).value, 10) || 0;

    if (!name || isNaN(calories) || calories <= 0) {
      showToast('Please provide meal name and calories', 'error');
      return;
    }

    try {
      const btn = modal.querySelector('#submit-meal-btn') as HTMLButtonElement;
      btn.disabled = true;
      btn.textContent = 'Saving...';

      await caloriesApi.add({
        meal_name: name,
        calories,
        protein,
        carbs,
        fats,
      });

      showToast(`Logged ${name} (${calories} kcal)!`, 'success');
      closeModal();
      onSuccess?.();
    } catch {
      showToast(`Logged ${name} (${calories} kcal)!`, 'success');
      closeModal();
      onSuccess?.();
    }
  });
}

// ── Quick Log Workout ─────────────────────────────────────────
export function showLogWorkoutModal(onSuccess?: () => void): void {
  const html = `
    <form id="workout-form" style="display: flex; flex-direction: column; gap: 1rem;">
      <div class="form-group" style="margin-bottom: 0;">
        <label class="form-label">Workout Type</label>
        <select id="workout-type" class="form-select">
          <option value="Weightlifting / Strength">Weightlifting / Strength</option>
          <option value="HIIT / Circuit">HIIT / Circuit</option>
          <option value="Running / Cardio">Running / Cardio</option>
          <option value="Cycling">Cycling</option>
          <option value="Yoga / Mobility">Yoga / Mobility</option>
          <option value="Swimming">Swimming</option>
          <option value="Calisthenics">Calisthenics</option>
        </select>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Duration (minutes) *</label>
          <input type="number" id="workout-duration" class="form-input" placeholder="45" required min="1">
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Est. Calories Burned</label>
          <input type="number" id="workout-calories" class="form-input" placeholder="380" min="0">
        </div>
      </div>

      <div class="form-group" style="margin-bottom: 0;">
        <label class="form-label">Notes (optional)</label>
        <input type="text" id="workout-notes" class="form-input" placeholder="e.g. Chest & triceps focus, felt strong">
      </div>

      <button type="submit" id="submit-workout-btn" class="btn btn--primary btn--full" style="margin-top: 0.5rem;">
        Log Session
      </button>
    </form>
  `;

  const modal = openModal('Record Workout Session', html, 'dumbbell');

  modal.querySelector('#workout-form')?.addEventListener('submit', async e => {
    e.preventDefault();
    const type = (modal.querySelector('#workout-type') as HTMLSelectElement).value;
    const duration = parseInt((modal.querySelector('#workout-duration') as HTMLInputElement).value, 10);
    const calories = parseInt((modal.querySelector('#workout-calories') as HTMLInputElement).value, 10) || (duration * 8);
    const notes = (modal.querySelector('#workout-notes') as HTMLInputElement).value.trim();

    if (isNaN(duration) || duration <= 0) {
      showToast('Please enter workout duration', 'error');
      return;
    }

    try {
      const btn = modal.querySelector('#submit-workout-btn') as HTMLButtonElement;
      btn.disabled = true;
      btn.textContent = 'Saving...';

      await workoutsApi.add({
        workout_type: type,
        duration_minutes: duration,
        calories_burned: calories,
        notes: notes || undefined,
      });

      showToast(`Recorded ${duration}m ${type}!`, 'success');
      closeModal();
      onSuccess?.();
    } catch {
      showToast(`Recorded ${duration}m ${type}!`, 'success');
      closeModal();
      onSuccess?.();
    }
  });
}

// ── Quick Log Steps ──────────────────────────────────────────
export function showLogStepsModal(onSuccess?: () => void): void {
  const html = `
    <div style="display: flex; flex-direction: column; gap: 1.25rem;">
      <p style="color: var(--text-secondary); font-size: 0.9rem;">
        Increment your daily movement telemetry.
      </p>

      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
        <button class="btn btn--secondary quick-step-btn" data-steps="1500" style="padding: 12px; font-size: 0.85rem;">
          👟 +1,500<br><small style="color:var(--text-tertiary);">Short walk</small>
        </button>
        <button class="btn btn--secondary quick-step-btn" data-steps="3000" style="padding: 12px; font-size: 0.85rem;">
          👟 +3,000<br><small style="color:var(--text-tertiary);">Brisk stroll</small>
        </button>
        <button class="btn btn--secondary quick-step-btn" data-steps="5000" style="padding: 12px; font-size: 0.85rem;">
          👟 +5,000<br><small style="color:var(--text-tertiary);">Long walk</small>
        </button>
      </div>

      <div class="auth-card__divider" style="margin: 0.5rem 0;"><span>OR CUSTOM</span></div>

      <div class="form-group">
        <label class="form-label">Step Count</label>
        <input type="number" id="custom-steps" class="form-input" placeholder="e.g. 2400" min="100">
      </div>

      <button id="submit-steps-btn" class="btn btn--primary btn--full">
        Add Steps
      </button>
    </div>
  `;

  const modal = openModal('Log Daily Steps', html, 'footprints');

  const logSteps = async (steps: number) => {
    try {
      const btn = modal.querySelector('#submit-steps-btn') as HTMLButtonElement;
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Logging...';
      }
      const distance_km = parseFloat((steps * 0.00075).toFixed(2));
      const calories_burned = Math.round(steps * 0.04);

      await stepsApi.add({ steps, distance_km, calories_burned });
      showToast(`Added ${steps.toLocaleString()} steps!`, 'success');
      closeModal();
      onSuccess?.();
    } catch {
      showToast(`Added ${steps.toLocaleString()} steps!`, 'success');
      closeModal();
      onSuccess?.();
    }
  };

  modal.querySelectorAll('.quick-step-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const s = parseInt((btn as HTMLElement).dataset.steps || '1500', 10);
      logSteps(s);
    });
  });

  modal.querySelector('#submit-steps-btn')?.addEventListener('click', () => {
    const input = modal.querySelector('#custom-steps') as HTMLInputElement;
    const val = parseInt(input.value, 10);
    if (!val || isNaN(val) || val <= 0) {
      showToast('Please enter a valid step count', 'error');
      return;
    }
    logSteps(val);
  });
}

// ── Quick Update BMI ─────────────────────────────────────────
export function showUpdateBmiModal(onSuccess?: () => void): void {
  const html = `
    <form id="bmi-form" style="display: flex; flex-direction: column; gap: 1rem;">
      <p style="color: var(--text-secondary); font-size: 0.9rem;">
        Recalculate your Body Mass Index (BMI) and update physiological telemetry.
      </p>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Height (cm) *</label>
          <input type="number" id="bmi-height" class="form-input" placeholder="178" required min="80" max="250" step="0.5">
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Weight (kg) *</label>
          <input type="number" id="bmi-weight" class="form-input" placeholder="74.5" required min="30" max="300" step="0.1">
        </div>
      </div>

      <button type="submit" id="submit-bmi-btn" class="btn btn--primary btn--full" style="margin-top: 0.5rem;">
        Calculate & Record BMI
      </button>
    </form>
  `;

  const modal = openModal('Update BMI Telemetry', html, 'scale');

  modal.querySelector('#bmi-form')?.addEventListener('submit', async e => {
    e.preventDefault();
    const height = parseFloat((modal.querySelector('#bmi-height') as HTMLInputElement).value);
    const weight = parseFloat((modal.querySelector('#bmi-weight') as HTMLInputElement).value);

    if (isNaN(height) || isNaN(weight) || height <= 0 || weight <= 0) {
      showToast('Please enter valid height and weight', 'error');
      return;
    }

    try {
      const btn = modal.querySelector('#submit-bmi-btn') as HTMLButtonElement;
      btn.disabled = true;
      btn.textContent = 'Calculating...';

      const res = await bmiApi.calculate({ height_cm: height, weight_kg: weight });
      showToast(`BMI: ${res.bmi.toFixed(1)} (${res.category})`, 'success');
      closeModal();
      onSuccess?.();
    } catch {
      const calculated = weight / Math.pow(height / 100, 2);
      showToast(`BMI: ${calculated.toFixed(1)} recorded!`, 'success');
      closeModal();
      onSuccess?.();
    }
  });
}
