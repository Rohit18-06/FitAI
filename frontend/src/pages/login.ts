// ============================================================
// FitAI – Login Page
// Glassmorphism Centered Card · Apple Vision Pro Aesthetic
// ============================================================
import gsap from 'gsap';
import { authApi } from '../api/auth';
import { storeAuth } from '../utils/helpers';
import { router } from '../router';
import { showToast } from '../components/toast';
import { refreshIcons } from '../utils/icons';

export function renderLoginPage(): void {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = `
    <div class="auth-container">
      <div class="auth-card glass-card" id="login-card">
        <div class="auth-card__header">
          <div class="auth-card__logo">
            ⚡
          </div>
          <h1 class="auth-card__title">Welcome to <span class="navbar__logo-gradient">FitAI</span></h1>
          <p class="auth-card__subtitle">Multimodal AI Fitness Coach & Biomechanics Studio</p>
        </div>

        <div id="login-error" class="auth-alert auth-alert--error" style="display: none;">
          <i data-lucide="alert-circle" style="width: 16px; height: 16px; flex-shrink: 0;"></i>
          <span id="login-error-msg">Invalid email or password</span>
        </div>

        <form id="login-form">
          <div class="form-group">
            <label class="form-label" for="login-email">Email Address</label>
            <input
              type="email"
              id="login-email"
              class="form-input"
              placeholder="athlete@fitai.com"
              required
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <label class="form-label" for="login-password" style="margin-bottom: 0;">Password</label>
              <a href="javascript:void(0)" id="demo-fill-btn" style="font-size: 0.75rem; color: var(--accent-cyan); font-weight: 600;">
                ⚡ Fill Demo Credentials
              </a>
            </div>
            <input
              type="password"
              id="login-password"
              class="form-input"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
          </div>

          <button type="submit" id="login-btn" class="btn btn--primary btn--full" style="margin-top: 1rem;">
            <span>Sign In</span>
            <i data-lucide="arrow-right" style="width: 18px; height: 18px;"></i>
          </button>
        </form>

        <div class="auth-card__divider">
          <span>OR CONTINUE AS GUEST</span>
        </div>

        <button type="button" id="guest-access-btn" class="btn btn--secondary btn--full">
          <i data-lucide="sparkles" style="width: 16px; height: 16px;"></i>
          <span>Instant Demo Experience</span>
        </button>

        <div class="auth-card__footer">
          Don't have an account? <a href="#/register">Create Account</a>
        </div>
      </div>
    </div>
  `;

  // GSAP reveal animation
  gsap.fromTo(
    '#login-card',
    { opacity: 0, y: 30, scale: 0.95 },
    { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: 'power3.out' },
  );

  refreshIcons(appEl);

  const form = document.getElementById('login-form') as HTMLFormElement;
  const emailInput = document.getElementById('login-email') as HTMLInputElement;
  const passwordInput = document.getElementById('login-password') as HTMLInputElement;
  const loginBtn = document.getElementById('login-btn') as HTMLButtonElement;
  const errorBox = document.getElementById('login-error') as HTMLDivElement;
  const errorMsg = document.getElementById('login-error-msg') as HTMLSpanElement;
  const demoFillBtn = document.getElementById('demo-fill-btn');
  const guestAccessBtn = document.getElementById('guest-access-btn');

  // Fill demo credentials
  demoFillBtn?.addEventListener('click', () => {
    emailInput.value = 'demo@fitai.com';
    passwordInput.value = 'FitAI2026!';
    emailInput.focus();
  });

  // Guest instant access
  guestAccessBtn?.addEventListener('click', () => {
    storeAuth('demo_token_' + Date.now(), {
      id: 1,
      email: 'alex.rivers@fitai.com',
      username: 'Alex Rivers',
    });
    showToast('Welcome to FitAI Demo Suite!', 'success');
    router.navigate('/dashboard');
  });

  // Handle Login submission
  form.addEventListener('submit', async e => {
    e.preventDefault();
    errorBox.style.display = 'none';

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
      errorMsg.textContent = 'Please provide both email and password';
      errorBox.style.display = 'flex';
      return;
    }

    loginBtn.disabled = true;
    loginBtn.innerHTML = `
      <span class="spinner" style="width: 16px; height: 16px; border: 2px solid white; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 0.8s linear infinite;"></span>
      <span>Authenticating...</span>
    `;

    try {
      const res = await authApi.login({ email, password });
      storeAuth(res.access_token, res.user);
      showToast(`Welcome back, ${res.user.username}!`, 'success');
      router.navigate('/dashboard');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      // If server unreachable or error, allow seamless demo fallback or show error
      if (!err.response) {
        // Backend might be offline; grant local test session with clear toast notification
        storeAuth('local_session_token', {
          id: 1,
          email,
          username: email.split('@')[0],
        });
        showToast('Connected in Offline/Demo mode', 'info');
        router.navigate('/dashboard');
        return;
      }
      errorMsg.textContent = typeof detail === 'string' ? detail : 'Invalid email or password.';
      errorBox.style.display = 'flex';
      loginBtn.disabled = false;
      loginBtn.innerHTML = `
        <span>Sign In</span>
        <i data-lucide="arrow-right" style="width: 18px; height: 18px;"></i>
      `;
      refreshIcons(loginBtn);
    }
  });
}
