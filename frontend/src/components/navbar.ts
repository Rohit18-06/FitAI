// ============================================================
// FitAI – Glass Navigation Component
// Apple Vision Pro & Linear inspired sticky header
// Includes Wearables navigation & Live Notification Bell Panel
// ============================================================
import { router } from '../router';
import { clearAuth, getStoredUser } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';
import { integrationsApi } from '../api/integrations';
import type { NotificationResponse } from '../types';

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
    { label: 'Wearables', path: '/wearables', icon: 'watch' },
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

    <div style="display: flex; align-items: center; gap: 12px; position: relative;">
      <!-- Notification Bell -->
      <div style="position: relative;">
        <button id="nav-notif-btn" class="navbar__link" style="padding: 8px; position: relative; border-radius: 50%;" title="Notifications">
          <i data-lucide="bell" style="width: 18px; height: 18px;"></i>
          <span id="nav-notif-badge" style="display: none; position: absolute; top: 2px; right: 2px; width: 16px; height: 16px; background: #ef4444; color: #fff; font-size: 10px; font-weight: 800; border-radius: 50%; display: flex; align-items: center; justify-content: center; line-height: 1;">0</span>
        </button>

        <!-- Notification Dropdown Panel -->
        <div id="nav-notif-dropdown" class="card glass-card" style="display: none; position: absolute; right: 0; top: calc(100% + 10px); width: 340px; max-height: 420px; overflow-y: auto; z-index: 1000; padding: 1rem; box-shadow: 0 16px 40px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.12); backdrop-filter: blur(20px);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span style="font-weight: 700; font-size: 0.9rem; color: #fff;">Notifications</span>
              <span id="nav-notif-panel-count" class="badge" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; font-size: 0.7rem; padding: 2px 6px; border-radius: 9999px;">0</span>
            </div>
            <button id="nav-notif-readall-btn" style="font-size: 0.75rem; color: var(--accent-cyan); background: none; border: none; cursor: pointer;">
              Mark all read
            </button>
          </div>
          <div id="nav-notif-list" style="display: flex; flex-direction: column; gap: 8px;">
            <div style="text-align: center; padding: 1.5rem 0; color: var(--text-tertiary); font-size: 0.8rem;">
              No unread notifications
            </div>
          </div>
        </div>
      </div>

      <!-- User Profile Badge -->
      <div class="navbar__link" style="padding: 6px 12px; background: rgba(255,255,255,0.04); cursor: default;">
        <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--success); display: inline-block;"></span>
        <span style="font-weight: 600; color: var(--text-primary); font-size: 0.85rem;">${userName}</span>
      </div>

      <!-- Logout Button -->
      <button class="navbar__logout" id="nav-logout" title="Sign Out">
        <i data-lucide="log-out"></i>
        <span>Logout</span>
      </button>

      <!-- Hamburger -->
      <div class="navbar__hamburger" id="nav-hamburger">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>

    <!-- Mobile Drawer -->
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

  // Notification Bell toggle
  const notifBtn = nav.querySelector('#nav-notif-btn');
  const notifDropdown = nav.querySelector('#nav-notif-dropdown') as HTMLElement | null;
  const notifBadge = nav.querySelector('#nav-notif-badge') as HTMLElement | null;
  const notifList = nav.querySelector('#nav-notif-list') as HTMLElement | null;
  const notifPanelCount = nav.querySelector('#nav-notif-panel-count') as HTMLElement | null;
  const readAllBtn = nav.querySelector('#nav-notif-readall-btn') as HTMLElement | null;

  notifBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!notifDropdown) return;
    const isVisible = notifDropdown.style.display === 'block';
    notifDropdown.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) {
      loadNotifications();
    }
  });

  // Close dropdown on outside click
  document.addEventListener('click', (e) => {
    if (notifDropdown && !notifDropdown.contains(e.target as Node) && notifBtn && !notifBtn.contains(e.target as Node)) {
      notifDropdown.style.display = 'none';
    }
  });

  async function loadNotifications(): Promise<void> {
    try {
      const unread = await integrationsApi.listUnreadNotifications(10);
      updateNotifUI(unread);
    } catch {
      // Ignore background fetch error
    }
  }

  function updateNotifUI(unread: NotificationResponse[]): void {
    if (notifBadge) {
      if (unread.length > 0) {
        notifBadge.style.display = 'flex';
        notifBadge.innerText = `${unread.length}`;
      } else {
        notifBadge.style.display = 'none';
      }
    }

    if (notifPanelCount) {
      notifPanelCount.innerText = `${unread.length} new`;
    }

    if (!notifList) return;

    if (unread.length === 0) {
      notifList.innerHTML = `
        <div style="text-align: center; padding: 1.5rem 0; color: var(--text-tertiary); font-size: 0.8rem;">
          No unread notifications
        </div>
      `;
      return;
    }

    notifList.innerHTML = unread.map(item => `
      <div class="notif-item" data-notif-id="${item.id}" style="padding: 8px 10px; background: rgba(255,255,255,0.04); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); cursor: pointer; transition: background 0.2s ease;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2px;">
          <span style="font-size: 0.85rem; font-weight: 700; color: #fff;">${item.title}</span>
          <span style="font-size: 0.7rem; color: ${item.priority === 'high' ? '#ef4444' : '#60a5fa'}; text-transform: uppercase; font-weight: 600;">${item.priority}</span>
        </div>
        <p style="font-size: 0.75rem; color: var(--text-secondary); line-height: 1.3;">${item.message}</p>
      </div>
    `).join('');

    notifList.querySelectorAll('.notif-item').forEach(itemEl => {
      itemEl.addEventListener('click', async () => {
        const id = parseInt((itemEl as HTMLElement).dataset.notifId!, 10);
        try {
          await integrationsApi.markNotificationRead(id);
          await loadNotifications();
        } catch {}
      });
    });
  }

  readAllBtn?.addEventListener('click', async (e) => {
    e.stopPropagation();
    try {
      await integrationsApi.markAllNotificationsRead();
      await loadNotifications();
    } catch {}
  });

  // Initial background count check
  integrationsApi.getUnreadCount().then(res => {
    if (notifBadge && res.unread_count > 0) {
      notifBadge.style.display = 'flex';
      notifBadge.innerText = `${res.unread_count}`;
    }
  }).catch(() => {});

  // Refresh icons
  refreshIcons(nav);

  return nav;
}
