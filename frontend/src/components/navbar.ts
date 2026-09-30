// ============================================================
// FitAI – Glass Navigation Component
// Apple Vision Pro & Linear inspired sticky header
// ============================================================
import { router } from '../router';
import { clearAuth, getStoredUser } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

export function renderNavbar(activePath = '/dashboard'): HTMLElement {
  let nav = document.getElementById('main-navbar');
  if (!nav) {
    nav = document.createElement('nav');
    nav.id = 'main-navbar';
    nav.className = 'navbar';
  }

  const user = getStoredUser();
  const userName = user?.username || 'Athlete';

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: 'layout-dashboard' },
    { label: 'AI Coach', path: '/coach', icon: 'bot' },
    { label: 'AI Diet', path: '/diet', icon: 'utensils' },
    { label: 'Workouts', path: '/workouts', icon: 'dumbbell' },
    { label: 'Video Analyzer', path: '/video', icon: 'video' },
    { label: 'Analytics', path: '/analytics', icon: 'chart-spline' },
    { label: 'Insights', path: '/insights', icon: 'sparkles' },
    { label: 'Profile', path: '/profile', icon: 'user' },
  ];

  const menuHtml = navItems
    .map(
      item => `
      <a href="#${item.path}" class="navbar__link ${
        activePath === item.path ? 'navbar__link--active' : ''
      }">
        <i data-lucide="${item.icon}"></i>
        <span>${item.label}</span>
      </a>
    `,
    )
    .join('');

  nav.innerHTML = `
    <div class="navbar__logo" id="nav-logo">
      <div class="navbar__logo-icon">⚡</div>
      <span>Fit<span class="navbar__logo-gradient">AI</span></span>
    </div>

    <div class="navbar__menu">
      ${menuHtml}
    </div>

    <div style="display: flex; align-items: center; gap: 12px;">
      <div class="navbar__link" style="padding: 6px 12px; background: rgba(255,255,255,0.04); cursor: default;">
        <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--success); display: inline-block;"></span>
        <span style="font-weight: 600; color: var(--text-primary); font-size: 0.85rem;">${userName}</span>
      </div>
      <button class="navbar__logout" id="nav-logout" title="Sign Out">
        <i data-lucide="log-out"></i>
        <span>Logout</span>
      </button>
      <div class="navbar__hamburger" id="nav-hamburger">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>

    <div class="navbar__mobile-menu" id="nav-mobile-menu">
      ${menuHtml}
      <button class="navbar__logout" id="nav-mobile-logout" style="margin-top: 1rem; width: 100%; justify-content: center;">
        <i data-lucide="log-out"></i>
        <span>Logout</span>
      </button>
    </div>
  `;

  // Logo navigation
  nav.querySelector('#nav-logo')?.addEventListener('click', () => {
    router.navigate('/dashboard');
  });

  // Logout handler
  const handleLogout = () => {
    clearAuth();
    router.navigate('/login');
  };
  nav.querySelector('#nav-logout')?.addEventListener('click', handleLogout);
  nav.querySelector('#nav-mobile-logout')?.addEventListener('click', handleLogout);

  // Hamburger toggle
  const hamburger = nav.querySelector('#nav-hamburger');
  const mobileMenu = nav.querySelector('#nav-mobile-menu');
  hamburger?.addEventListener('click', () => {
    mobileMenu?.classList.toggle('active');
  });

  // Close mobile menu on item click
  mobileMenu?.querySelectorAll('.navbar__link').forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.remove('active');
    });
  });

  // Refresh icons
  refreshIcons(nav);

  return nav;
}
