// ============================================================
// FitAI – Social Activity Feed Page
// Phase 7: Real-time social activity timeline
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { ActivityFeedResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';

type FeedTab = 'global' | 'friends';

let currentTab: FeedTab = 'global';

const ACTIVITY_ICONS: Record<string, string> = {
  workout: 'dumbbell',
  badge: 'award',
  personal_record: 'trophy',
  challenge_joined: 'swords',
  challenge_completed: 'flag',
  team_joined: 'users',
  follow: 'user-plus',
  streak: 'flame',
  default: 'activity',
};

const ACTIVITY_COLORS: Record<string, string> = {
  workout: '#3B82F6',
  badge: '#F59E0B',
  personal_record: '#10B981',
  challenge_joined: '#8B5CF6',
  challenge_completed: '#06B6D4',
  team_joined: '#EC4899',
  follow: '#6366F1',
  streak: '#EF4444',
  default: '#64748B',
};

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

function getInitials(username: string): string {
  return username.slice(0, 2).toUpperCase();
}

function renderFeedItem(item: ActivityFeedResponse, index: number): string {
  const icon = ACTIVITY_ICONS[item.activity_type] || ACTIVITY_ICONS.default;
  const color = ACTIVITY_COLORS[item.activity_type] || ACTIVITY_COLORS.default;
  const initials = getInitials(item.username);

  return `
    <div class="feed-item" style="
      display: flex; gap: 16px; padding: 20px; 
      background: rgba(255,255,255,0.04); 
      border: 1px solid rgba(255,255,255,0.06); 
      border-radius: 16px;
      transition: all 0.3s ease;
      opacity: 0; transform: translateY(12px);
      cursor: pointer;
    " data-feed-idx="${index}" data-username="${item.username}">
      <!-- User Avatar -->
      <div style="
        width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, ${color}40, ${color}20);
        border: 2px solid ${color}50;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 0.85rem; color: ${color};
        flex-shrink: 0;
      ">
        ${item.avatar ? `<img src="${item.avatar}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;" alt="">` : initials}
      </div>

      <!-- Content -->
      <div style="flex: 1; min-width: 0;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
          <span style="font-weight: 700; color: #fff; font-size: 0.9rem;">${item.username}</span>
          <div style="
            display: inline-flex; align-items: center; gap: 4px; 
            padding: 2px 8px; border-radius: 999px; 
            background: ${color}20; color: ${color}; 
            font-size: 0.7rem; font-weight: 600;
          ">
            <i data-lucide="${icon}" style="width: 12px; height: 12px;"></i>
            ${item.activity_type.replace(/_/g, ' ')}
          </div>
        </div>
        <h4 style="margin: 0 0 4px 0; font-size: 0.95rem; color: var(--text-primary); font-weight: 600;">
          ${item.title}
        </h4>
        ${item.description ? `<p style="margin: 0; font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">${item.description}</p>` : ''}
        <span style="font-size: 0.72rem; color: var(--text-tertiary); margin-top: 8px; display: block;">
          ${timeAgo(item.created_at)}
        </span>
      </div>
    </div>
  `;
}

export async function renderSocialPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/social'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Page Header -->
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          Social <span class="navbar__logo-gradient">Feed</span>
        </h1>
        <p class="page-header__subtitle">
          See what your community is doing — workouts, badges, personal records & more
        </p>
      </div>

      <div style="display: flex; gap: 8px;">
        <a href="#/friends" class="btn btn--outline" style="text-decoration: none;">
          <i data-lucide="user-plus" style="width: 16px; height: 16px;"></i>
          Friends
        </a>
        <a href="#/challenges" class="btn btn--outline" style="text-decoration: none;">
          <i data-lucide="swords" style="width: 16px; height: 16px;"></i>
          Challenges
        </a>
      </div>
    </div>

    <!-- Feed Tabs -->
    <div style="
      display: inline-flex; background: rgba(255,255,255,0.04); 
      padding: 4px; border-radius: var(--radius-full); 
      border: 1px solid var(--glass-border); margin-bottom: 24px;
    ">
      <button class="chart-container__period-btn ${currentTab === 'global' ? 'chart-container__period-btn--active' : ''}" data-tab="global">
        <i data-lucide="globe" style="width: 14px; height: 14px;"></i>
        Global
      </button>
      <button class="chart-container__period-btn ${currentTab === 'friends' ? 'chart-container__period-btn--active' : ''}" data-tab="friends">
        <i data-lucide="heart" style="width: 14px; height: 14px;"></i>
        Friends
      </button>
    </div>

    <!-- Feed Container -->
    <div id="feed-container" style="display: flex; flex-direction: column; gap: 12px;">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading activity feed...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(container);

  // Tab switching
  container.querySelectorAll('[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      currentTab = (btn as HTMLElement).dataset.tab as FeedTab;
      container.querySelectorAll('[data-tab]').forEach(b => b.classList.remove('chart-container__period-btn--active'));
      btn.classList.add('chart-container__period-btn--active');
      loadFeed(container);
    });
  });

  // Click on feed item to go to profile
  container.addEventListener('click', (e) => {
    const item = (e.target as HTMLElement).closest('[data-username]') as HTMLElement | null;
    if (item?.dataset.username) {
      window.location.hash = `#/athlete/${item.dataset.username}`;
    }
  });

  await loadFeed(container);

  // Entrance animation
  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

async function loadFeed(container: HTMLElement): Promise<void> {
  const feedContainer = container.querySelector('#feed-container');
  if (!feedContainer) return;

  feedContainer.innerHTML = `
    <div class="card glass-card" style="padding: 3rem; text-align: center;">
      <div class="spinner" style="margin: 0 auto 1rem;"></div>
      <p style="color: var(--text-secondary);">Loading activity feed...</p>
    </div>
  `;

  try {
    const items: ActivityFeedResponse[] = currentTab === 'friends'
      ? await socialApi.getFriendsFeed(50)
      : await socialApi.getGlobalFeed(50);

    if (items.length === 0) {
      feedContainer.innerHTML = `
        <div class="card glass-card" style="padding: 4rem; text-align: center;">
          <i data-lucide="${currentTab === 'friends' ? 'heart' : 'globe'}" style="width: 48px; height: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
          <h3 style="color: var(--text-primary); margin: 0 0 8px 0;">${currentTab === 'friends' ? 'No friend activity yet' : 'No activity yet'}</h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">
            ${currentTab === 'friends'
              ? 'Add some friends to see their activities here!'
              : 'Start working out and tracking your fitness to create activity!'}
          </p>
          ${currentTab === 'friends' ? '<a href="#/friends" class="btn btn--primary" style="margin-top: 1rem; text-decoration: none;">Find Friends</a>' : ''}
        </div>
      `;
      refreshIcons(feedContainer as HTMLElement);
      return;
    }

    feedContainer.innerHTML = items.map((item, i) => renderFeedItem(item, i)).join('');
    refreshIcons(feedContainer as HTMLElement);

    // Stagger animation
    feedContainer.querySelectorAll('.feed-item').forEach((el, i) => {
      gsap.to(el, {
        opacity: 1, y: 0, duration: 0.4,
        delay: i * 0.06, ease: 'power2.out',
      });
    });
  } catch {
    feedContainer.innerHTML = `
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <i data-lucide="wifi-off" style="width: 40px; height: 40px; color: var(--danger); margin-bottom: 16px;"></i>
        <h3 style="color: var(--text-primary);">Unable to load feed</h3>
        <p style="color: var(--text-secondary); font-size: 0.85rem;">Please try again later.</p>
      </div>
    `;
    refreshIcons(feedContainer as HTMLElement);
  }
}
