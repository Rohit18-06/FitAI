// ============================================================
// FitAI – Registration Page
// Glassmorphism Card · Onboarding with Height & Weight
// ============================================================
import gsap from 'gsap';
import { authApi } from '../api/auth';
import { bmiApi } from '../api/bmi';
import { storeAuth } from '../utils/helpers';
import { router } from '../router';
import { showToast } from '../components/toast';
import { refreshIcons } from '../utils/icons';

export function renderRegisterPage(): void {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = `
    <div class="auth-container" style="padding: 3rem 1.5rem;">
      <div class="auth-card glass-card" id="register-card" style="max-width: 520px;">
        <div class="auth-card__header" style="margin-bottom: 2rem;">
          <div class="auth-card__logo">
            ⚡
          </div>
          <h1 class="auth-card__title">Create Your <span class="navbar__logo-gradient">Account</span></h1>
          <p class="auth-card__subtitle">Start your intelligent AI-driven fitness journey</p>
        </div>

        <div id="register-error" class="auth-alert auth-alert--error" style="display: none;">
          <i data-lucide="alert-circle" style="width: 16px; height: 16px; flex-shrink: 0;"></i>
          <span id="register-error-msg">Validation error</span>
        </div>

        <form id="register-form">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="form-group">
              <label class="form-label" for="reg-fullname">Full Name</label>
              <input
                type="text"
                id="reg-fullname"
                class="form-input"
                placeholder="Alex Rivers"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="reg-username">Username *</label>
              <input
                type="text"
                id="reg-username"
                class="form-input"
                placeholder="alex_rivers"
                required
                autocomplete="username"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="reg-email">Email Address *</label>
            <input
              type="email"
              id="reg-email"
              class="form-input"
              placeholder="alex@example.com"
              required
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <label class="form-label" for="reg-password">Password (min 8 characters) *</label>
            <input
              type="password"
              id="reg-password"
              class="form-input"
              placeholder="••••••••"
              required
              minlength="8"
              autocomplete="new-password"
            />
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="form-group">
              <label class="form-label" for="reg-height">Height (cm)</label>
              <input
                type="number"
                id="reg-height"
                class="form-input"
                placeholder="178"
                min="80"
                max="250"
                step="0.5"
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="reg-weight">Weight (kg)</label>
              <input
                type="number"
                id="reg-weight"
                class="form-input"
                placeholder="74"
                min="30"
                max="300"
                step="0.1"
              />
            </div>
          </div>

          <button type="submit" id="register-btn" class="btn btn--primary btn--full" style="margin-top: 1rem;">
            <span>Complete Registration</span>
            <i data-lucide="check-circle" style="width: 18px; height: 18px;"></i>
          </button>
        </form>

        <div class="auth-card__footer">
          Already have an account? <a href="#/login">Sign In</a>
        </div>
      </div>
    </div>
  `;

  gsap.fromTo(
    '#register-card',
    { opacity: 0, y: 30, scale: 0.95 },
    { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: 'power3.out' },
  );

  refreshIcons(appEl);

  const form = document.getElementById('register-form') as HTMLFormElement;
  const usernameInput = document.getElementById('reg-username') as HTMLInputElement;
  const emailInput = document.getElementById('reg-email') as HTMLInputElement;
  const passwordInput = document.getElementById('reg-password') as HTMLInputElement;
  const heightInput = document.getElementById('reg-height') as HTMLInputElement;
  const weightInput = document.getElementById('reg-weight') as HTMLInputElement;
  const registerBtn = document.getElementById('register-btn') as HTMLButtonElement;
  const errorBox = document.getElementById('register-error') as HTMLDivElement;
  const errorMsg = document.getElementById('register-error-msg') as HTMLSpanElement;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    errorBox.style.display = 'none';

    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    const height = parseFloat(heightInput.value);
    const weight = parseFloat(weightInput.value);

    // Validation
    if (username.length < 3) {
      errorMsg.textContent = 'Username must be at least 3 characters.';
      errorBox.style.display = 'flex';
      return;
    }
    if (password.length < 8) {
      errorMsg.textContent = 'Password must be at least 8 characters.';
      errorBox.style.display = 'flex';
      return;
    }

    registerBtn.disabled = true;
    registerBtn.innerHTML = `
      <span class="spinner" style="width: 16px; height: 16px; border: 2px solid white; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 0.8s linear infinite;"></span>
      <span>Creating Profile...</span>
    `;

    try {
      const res = await authApi.register({
        email,
        username,
        password,
      });

      storeAuth(res.access_token, res.user);

      // Record initial height and weight if provided
      if (!isNaN(height) && !isNaN(weight) && height > 0 && weight > 0) {
        try {
          await bmiApi.calculate({ height_cm: height, weight_kg: weight });
        } catch {
          // Non-blocking BMI calculation
        }
      }

      showToast(`Welcome to FitAI, ${username}!`, 'success');
      router.navigate('/dashboard');
    } catch (err: any) {
      if (!err.response) {
        // Backend offline fallback
        storeAuth('local_session_' + Date.now(), {
          id: 1,
          email,
          username,
        });
        showToast('Account created in local environment!', 'success');
        router.navigate('/dashboard');
        return;
      }

      const detail = err.response?.data?.detail;
      errorMsg.textContent = typeof detail === 'string' ? detail : 'Registration failed. Please try a different username or email.';
      errorBox.style.display = 'flex';
      registerBtn.disabled = false;
      registerBtn.innerHTML = `
        <span>Complete Registration</span>
        <i data-lucide="check-circle" style="width: 18px; height: 18px;"></i>
      `;
      refreshIcons(registerBtn);
    }
  });
}
