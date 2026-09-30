// ============================================================
// FitAI – Leaderboards Page
// Phase 7: Multi-category competitive rankings
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { LeaderboardEntry } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';
import { getStoredUser } from '../utils/helpers';

type LBCategory = 'xp' | 'steps' | 'workouts' | 'recovery' | 'streaks';

const CATEGORIES: { key: LBCategory; label: string; icon: string; color: string; unit: string }[] = [
  { key: 'xp', label: 'XP', icon: 'zap', color: '#F59E0B', unit: 'xp' },
  { key: 'steps', label: 'Steps', icon: 'footprints', color: '#3B82F6', unit: 'steps' },
  { key: 'workouts', label: 'Workouts', icon: 'dumbbell', color: '#8B5CF6', unit: 'sessions' },
  { key: 'recovery', label: 'Recovery', icon: 'heart-pulse', color: '#10B981', unit: 'score' },
  { key: 'streaks', label: 'Streaks', icon: 'flame', color: '#EF4444', unit: 'days' },
];

let currentCategory: LBCategory = 'xp';

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

function formatValue(val: number): string {
  if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
  if (val >= 1000) return `${(val / 1000).toFixed(1)}K`;
  return val.toLocaleString();
}

function renderMedal(rank: number): string {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return `<span style="font-weight: 700; color: var(--text-tertiary); font-size: 0.85rem;">#${rank}</span>`;
}

export async function renderLeaderboardsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/leaderboards'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-header__title">
        Global <span class="navbar__logo-gradient">Leaderboards</span>
      </h1>
      <p class="page-header__subtitle">
        Compete with athletes worldwide across 5 fitness dimensions
      </p>
    </div>

    <!-- Category Tabs -->
    <div style="
      display: flex; flex-wrap: wrap; gap: 10px;
      margin-bottom: 28px;
    ">
      ${CATEGORIES.map(cat => `
        <button class="lb-cat-btn ${cat.key === currentCategory ? 'lb-cat-btn--active' : ''}" data-lbcat="${cat.key}" style="
          display: inline-flex; align-items: center; gap: 8px;
          padding: 10px 20px; border-radius: var(--radius-full);
          border: 1px solid ${cat.key === currentCategory ? cat.color + '60' : 'rgba(255,255,255,0.08)'};
          background: ${cat.key === currentCategory ? cat.color + '15' : 'rgba(255,255,255,0.04)'};
          color: ${cat.key === currentCategory ? cat.color : 'var(--text-secondary)'};
          font-weight: 600; font-size: 0.85rem; cursor: pointer;
          transition: all 0.25s ease;
        ">
          <i data-lucide="${cat.icon}" style="width: 16px; height: 16px;"></i>
          ${cat.label}
        </button>
      `).join('')}
    </div>

    <!-- Leaderboard Table -->
    <div id="lb-content" class="card glass-card" style="padding: 0; overflow: hidden;">
      <div style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading leaderboard...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(container);

  // Tab click handlers
  container.querySelectorAll('[data-lbcat]').forEach(btn => {
    btn.addEventListener('click', () => {
      const cat = (btn as HTMLElement).dataset.lbcat as LBCategory;
      currentCategory = cat;
      const catInfo = CATEGORIES.find(c => c.key === cat)!;

      container.querySelectorAll('[data-lbcat]').forEach(b => {
        const bCat = (b as HTMLElement).dataset.lbcat as LBCategory;
        const bInfo = CATEGORIES.find(c => c.key === bCat)!;
        const isActive = bCat === cat;
        (b as HTMLElement).style.borderColor = isActive ? bInfo.color + '60' : 'rgba(255,255,255,0.08)';
        (b as HTMLElement).style.background = isActive ? bInfo.color + '15' : 'rgba(255,255,255,0.04)';
        (b as HTMLElement).style.color = isActive ? bInfo.color : 'var(--text-secondary)';
      });

      loadLeaderboard(container, catInfo);
    });
  });

  await loadLeaderboard(container, CATEGORIES[0]);
  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

async function loadLeaderboard(
  container: HTMLElement,
  cat: { key: LBCategory; label: string; icon: string; color: string; unit: string }
): Promise<void> {
  const content = container.querySelector('#lb-content') as HTMLElement;
  if (!content) return;

  content.innerHTML = `<div style="padding: 3rem; text-align: center;"><div class="spinner" style="margin: 0 auto 1rem;"></div><p style="color: var(--text-secondary);">Loading ${cat.label} leaderboard...</p></div>`;

  try {
    let entries: LeaderboardEntry[];
    switch (cat.key) {
      case 'xp': entries = await socialApi.getXPLeaderboard(20); break;
      case 'steps': entries = await socialApi.getStepsLeaderboard(20); break;
      case 'workouts': entries = await socialApi.getWorkoutsLeaderboard(20); break;
      case 'recovery': entries = await socialApi.getRecoveryLeaderboard(20); break;
      case 'streaks': entries = await socialApi.getStreaksLeaderboard(20); break;
    }

    if (!entries || entries.length === 0) {
      content.innerHTML = `
        <div style="padding: 4rem; text-align: center;">
          <i data-lucide="${cat.icon}" style="width: 48px; height: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
          <h3 style="color: var(--text-primary);">No rankings yet</h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">Be the first to claim the top spot!</p>
        </div>
      `;
      refreshIcons(content);
      return;
    }

    const currentUser = getStoredUser();
    const currentUsername = currentUser?.username;

    content.innerHTML = `
      <!-- Header -->
      <div style="
        display: grid; grid-template-columns: 60px 1fr 100px 80px;
        padding: 14px 20px; font-size: 0.75rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
        color: var(--text-tertiary); border-bottom: 1px solid rgba(255,255,255,0.06);
        background: rgba(255,255,255,0.02);
      ">
        <span>Rank</span>
        <span>Athlete</span>
        <span style="text-align: right;">${cat.unit}</span>
        <span style="text-align: right;">Level</span>
      </div>

      ${entries.map((entry, i) => {
        const isMe = currentUsername && entry.username === currentUsername;
        return `
          <div class="lb-row" style="
            display: grid; grid-template-columns: 60px 1fr 100px 80px;
            align-items: center; padding: 14px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            background: ${isMe ? cat.color + '08' : entry.rank <= 3 ? 'rgba(255,255,255,0.02)' : 'transparent'};
            opacity: 0; transform: translateX(-12px);
            cursor: pointer; transition: background 0.2s ease;
          " data-anim="${i}" data-username="${entry.username}">
            <div style="text-align: center; font-size: 1.2rem;">
              ${renderMedal(entry.rank)}
            </div>
            <div style="display: flex; align-items: center; gap: 12px; min-width: 0;">
              <div style="
                width: 40px; height: 40px; border-radius: 50%;
                background: linear-gradient(135deg, ${cat.color}30, ${cat.color}15);
                border: 2px solid ${isMe ? cat.color : 'rgba(255,255,255,0.08)'};
                display: flex; align-items: center; justify-content: center;
                font-weight: 800; font-size: 0.75rem; color: ${cat.color};
                flex-shrink: 0;
              ">
                ${entry.avatar ? `<img src="${entry.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">` : getInitials(entry.username)}
              </div>
              <div style="min-width: 0;">
                <span style="font-weight: ${isMe ? '800' : '600'}; color: ${isMe ? cat.color : '#fff'}; font-size: 0.9rem; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  ${entry.username}${isMe ? ' (You)' : ''}
                </span>
              </div>
            </div>
            <span style="
              text-align: right; font-weight: 700; font-size: 0.95rem;
              color: ${entry.rank <= 3 ? cat.color : 'var(--text-primary)'};
              font-variant-numeric: tabular-nums;
            ">
              ${formatValue(entry.value)}
            </span>
            <div style="
              text-align: right; display: inline-flex; align-items: center; justify-content: flex-end; gap: 4px;
              font-size: 0.8rem; color: var(--accent-cyan); font-weight: 600;
            ">
              <i data-lucide="star" style="width: 12px; height: 12px;"></i>
              ${entry.level}
            </div>
          </div>
        `;
      }).join('')}
    `;

    refreshIcons(content);

    // Animate rows
    content.querySelectorAll('[data-anim]').forEach((el, i) => {
      gsap.to(el, { opacity: 1, x: 0, duration: 0.35, delay: i * 0.04, ease: 'power2.out' });
    });

    // Click to profile
    content.querySelectorAll('[data-username]').forEach(row => {
      row.addEventListener('click', () => {
        const u = (row as HTMLElement).dataset.username;
        if (u) window.location.hash = `#/athlete/${u}`;
      });
    });
  } catch {
    content.innerHTML = `
      <div style="padding: 3rem; text-align: center;">
        <p style="color: var(--danger);">Failed to load leaderboard</p>
      </div>
    `;
  }
}
