// ============================================================
// FitAI – User Profile & Biometric Settings Page
// ============================================================
import gsap from 'gsap';
import { getStoredUser, clearAuth } from '../utils/helpers';
import { renderNavbar } from '../components/navbar';
import { router } from '../router';
import { showToast } from '../components/toast';
import { refreshIcons } from '../utils/icons';

export function renderProfilePage(): void {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  const user = getStoredUser();
  const userName = user?.username || 'Alex Rivers';
  const userEmail = user?.email || 'alex.rivers@fitai.com';
  const initial = userName.charAt(0).toUpperCase();

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/profile'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Profile Header Card -->
    <div class="glass-card profile-header" id="profile-banner">
      <div class="profile-avatar">
        ${initial}
      </div>
      <div>
        <h1 class="profile-info__name">${userName}</h1>
        <div class="profile-info__email">${userEmail}</div>
        <div class="profile-info__joined">
          Member of FitAI Titanium Tier • Activated 2026
        </div>
      </div>
    </div>

    <!-- Profile Settings Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.5rem;">
      <!-- Biometric Targets Card -->
      <div class="glass-card" style="padding: 2rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px;">
          <span>🎯</span> Daily Biometric Targets
        </h3>

        <form id="targets-form">
          <div class="form-group">
            <label class="form-label">Daily Calorie Target (kcal)</label>
            <input type="number" id="target-cal" class="form-input" value="2400" min="1200" max="6000">
          </div>

          <div class="form-group">
            <label class="form-label">Daily Water Target (Liters)</label>
            <input type="number" id="target-water" step="0.1" class="form-input" value="3.0" min="1.0" max="8.0">
          </div>

          <div class="form-group">
            <label class="form-label">Daily Step Target</label>
            <input type="number" id="target-steps" class="form-input" value="10000" min="2000" max="30000">
          </div>

          <button type="submit" class="btn btn--primary btn--full" style="margin-top: 1rem;">
            Update Daily Targets
          </button>
        </form>
      </div>

      <!-- Anthropometric Stats Card -->
      <div class="glass-card" style="padding: 2rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px;">
          <span>⚖️</span> Anthropometrics & Stature
        </h3>

        <form id="stature-form">
          <div class="form-group">
            <label class="form-label">Current Stature Height (cm)</label>
            <input type="number" id="stature-height" class="form-input" value="180" min="90" max="250">
          </div>

          <div class="form-group">
            <label class="form-label">Goal Target Weight (kg)</label>
            <input type="number" id="stature-weight" step="0.5" class="form-input" value="76.0" min="35" max="200">
          </div>

          <div class="form-group">
            <label class="form-label">Primary Training Modality</label>
            <select class="form-select">
              <option selected>Hypertrophy & Strength (Powerbuilding)</option>
              <option>Powerlifting Specialized</option>
              <option>Olympic Weightlifting</option>
              <option>Functional Cross-Training</option>
            </select>
          </div>

          <button type="submit" class="btn btn--secondary btn--full" style="margin-top: 1rem;">
            Save Physical Telemetry
          </button>
        </form>
      </div>

      <!-- Account Security & Session -->
      <div class="glass-card" style="padding: 2rem; grid-column: 1 / -1;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem; color: var(--danger);">
          Account Session & Security
        </h3>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1.5rem;">
          End current session, revoke biometric token from this workstation, and return to authentication.
        </p>

        <button id="profile-logout-btn" class="btn btn--danger">
          <i data-lucide="log-out"></i>
          <span>Sign Out of FitAI</span>
        </button>
      </div>
    </div>
  `;

  appEl.appendChild(container);

  gsap.fromTo(
    '#profile-banner',
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' },
  );

  refreshIcons(appEl);

  container.querySelector('#targets-form')?.addEventListener('submit', e => {
    e.preventDefault();
    showToast('Daily biometric targets updated successfully!', 'success');
  });

  container.querySelector('#stature-form')?.addEventListener('submit', e => {
    e.preventDefault();
    showToast('Physical telemetry updated!', 'success');
  });

  container.querySelector('#profile-logout-btn')?.addEventListener('click', () => {
    clearAuth();
    showToast('Logged out of session', 'info');
    router.navigate('/login');
  });
}
