// ============================================================
// FitAI – Achievements & Badges Page
// Phase 7: XP progression, badge collection, level display
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { AchievementsOverviewResponse, BadgeResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';
import { animateCounter } from '../utils/helpers';

const BADGE_CATEGORY_COLORS: Record<string, string> = {
  workout: '#3B82F6',
  steps: '#10B981',
  streak: '#EF4444',
  nutrition: '#F59E0B',
  social: '#8B5CF6',
  milestone: '#EC4899',
  special: '#06B6D4',
  default: '#64748B',
};

export async function renderAchievementsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/achievements'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-header__title">
        Achievements & <span class="navbar__logo-gradient">Badges</span>
      </h1>
      <p class="page-header__subtitle">
        Track your XP progression, collect badges, and level up your fitness journey
      </p>
    </div>

    <div id="achievements-content">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading achievements...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);

  try {
    const data: AchievementsOverviewResponse = await socialApi.getAchievements();
    renderAchievementsContent(container, data);
  } catch {
    const content = container.querySelector('#achievements-content');
    if (content) {
      content.innerHTML = `
        <div class="card glass-card" style="padding: 3rem; text-align: center;">
          <p style="color: var(--danger);">Failed to load achievements. Please try again.</p>
        </div>
      `;
    }
  }

  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

function renderAchievementsContent(container: HTMLElement, data: AchievementsOverviewResponse): void {
  const content = container.querySelector('#achievements-content') as HTMLElement;
  if (!content) return;

  const { user_level, badges, total_badges, earned_count } = data;
  const xpProgress = user_level.progress_percent || 0;
  const earnedBadges = badges.filter(b => b.is_earned);
  const lockedBadges = badges.filter(b => !b.is_earned);

  content.innerHTML = `
    <!-- Level & XP Hero Card -->
    <div class="card glass-card" style="padding: 0; overflow: hidden; margin-bottom: 28px;">
      <div style="
        padding: 32px; 
        background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(139,92,246,0.08), rgba(6,182,212,0.06));
      ">
        <div style="display: flex; align-items: center; gap: 28px; flex-wrap: wrap;">
          <!-- Level Circle -->
          <div style="position: relative; flex-shrink: 0;">
            <svg width="120" height="120" viewBox="0 0 120 120" style="transform: rotate(-90deg);">
              <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
              <circle cx="60" cy="60" r="52" fill="none" stroke="url(#xp-grad)" stroke-width="8"
                stroke-linecap="round"
                stroke-dasharray="${2 * Math.PI * 52}"
                stroke-dashoffset="${2 * Math.PI * 52 * (1 - xpProgress / 100)}"
                style="transition: stroke-dashoffset 1.5s ease-out;"
              />
              <defs>
                <linearGradient id="xp-grad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#3B82F6"/>
                  <stop offset="50%" stop-color="#8B5CF6"/>
                  <stop offset="100%" stop-color="#06B6D4"/>
                </linearGradient>
              </defs>
            </svg>
            <div style="
              position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(0deg);
              text-align: center;
            ">
              <div style="font-size: 2rem; font-weight: 900; color: #fff; line-height: 1;" data-counter="${user_level.level}">0</div>
              <div style="font-size: 0.65rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">Level</div>
            </div>
          </div>

          <!-- XP Stats -->
          <div style="flex: 1; min-width: 200px;">
            <h2 style="margin: 0 0 8px 0; font-size: 1.4rem; color: #fff; font-weight: 800;">
              <span data-counter="${user_level.xp}">0</span> XP
            </h2>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span style="font-size: 0.78rem; color: var(--text-secondary);">Progress to Level ${user_level.level + 1}</span>
              <span style="font-size: 0.78rem; color: var(--accent-cyan); font-weight: 700;">${xpProgress.toFixed(0)}%</span>
            </div>
            <div style="height: 8px; border-radius: 99px; background: rgba(255,255,255,0.08); overflow: hidden;">
              <div id="xp-progress-bar" style="height: 100%; border-radius: 99px; width: 0%; background: linear-gradient(90deg, #3B82F6, #8B5CF6, #06B6D4); transition: width 1.5s ease-out;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 6px;">
              <span style="font-size: 0.7rem; color: var(--text-tertiary);">${user_level.xp} XP</span>
              <span style="font-size: 0.7rem; color: var(--text-tertiary);">${user_level.next_level_xp} XP</span>
            </div>
          </div>

          <!-- Achievement Summary -->
          <div style="display: flex; gap: 16px; flex-shrink: 0;">
            <div style="text-align: center; padding: 16px 20px; background: rgba(255,255,255,0.04); border-radius: 16px; border: 1px solid rgba(255,255,255,0.06);">
              <div style="font-size: 1.5rem; font-weight: 900; color: #FBBF24;" data-counter="${earned_count}">0</div>
              <div style="font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em;">Earned</div>
            </div>
            <div style="text-align: center; padding: 16px 20px; background: rgba(255,255,255,0.04); border-radius: 16px; border: 1px solid rgba(255,255,255,0.06);">
              <div style="font-size: 1.5rem; font-weight: 900; color: var(--text-primary);" data-counter="${total_badges}">0</div>
              <div style="font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em;">Total</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Telemetry -->
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; margin-bottom: 28px;">
      ${renderStatCard('Workouts', user_level.total_workouts, 'dumbbell', '#8B5CF6')}
      ${renderStatCard('Steps', user_level.total_steps, 'footprints', '#3B82F6')}
      ${renderStatCard('Calories', user_level.total_calories_burned, 'flame', '#EF4444')}
    </div>

    <!-- Earned Badges -->
    ${earnedBadges.length > 0 ? `
      <h3 style="color: #fff; margin: 0 0 16px 0; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="award" style="width: 20px; height: 20px; color: #FBBF24;"></i>
        Earned Badges
        <span style="font-size: 0.75rem; color: var(--accent-cyan); font-weight: 600;">(${earnedBadges.length})</span>
      </h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px;">
        ${earnedBadges.map((b, i) => renderBadgeCard(b, i, true)).join('')}
      </div>
    ` : ''}

    <!-- Locked Badges -->
    ${lockedBadges.length > 0 ? `
      <h3 style="color: var(--text-secondary); margin: 0 0 16px 0; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="lock" style="width: 18px; height: 18px; color: var(--text-tertiary);"></i>
        Locked Badges
        <span style="font-size: 0.75rem; color: var(--text-tertiary); font-weight: 600;">(${lockedBadges.length})</span>
      </h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;">
        ${lockedBadges.map((b, i) => renderBadgeCard(b, i + earnedBadges.length, false)).join('')}
      </div>
    ` : ''}
  `;

  refreshIcons(content);

  // Animate XP bar
  setTimeout(() => {
    const bar = content.querySelector('#xp-progress-bar') as HTMLElement;
    if (bar) bar.style.width = `${xpProgress}%`;
  }, 100);

  // Counter animations
  content.querySelectorAll('[data-counter]').forEach(el => {
    const target = parseInt((el as HTMLElement).dataset.counter!, 10);
    animateCounter(el as HTMLElement, target, 1200);
  });

  // Stagger badge cards
  content.querySelectorAll('[data-anim]').forEach((el, i) => {
    gsap.to(el, { opacity: 1, y: 0, scale: 1, duration: 0.4, delay: i * 0.04, ease: 'back.out(1.2)' });
  });
}

function renderStatCard(label: string, value: number, icon: string, color: string): string {
  return `
    <div class="card glass-card" style="padding: 16px; text-align: center;">
      <i data-lucide="${icon}" style="width: 20px; height: 20px; color: ${color}; margin-bottom: 8px;"></i>
      <div style="font-size: 1.2rem; font-weight: 800; color: #fff;" data-counter="${value}">0</div>
      <div style="font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em;">${label}</div>
    </div>
  `;
}

function renderBadgeCard(badge: BadgeResponse, index: number, isEarned: boolean): string {
  const color = BADGE_CATEGORY_COLORS[badge.category] || BADGE_CATEGORY_COLORS.default;

  return `
    <div class="card glass-card" style="
      padding: 24px; text-align: center;
      opacity: 0; transform: translateY(8px) scale(0.95);
      ${!isEarned ? 'opacity: 0.5; filter: grayscale(0.7);' : ''}
      transition: all 0.3s ease;
    " data-anim="${index}">
      <div style="
        width: 56px; height: 56px; margin: 0 auto 14px;
        border-radius: 50%; 
        background: ${isEarned ? `linear-gradient(135deg, ${color}30, ${color}15)` : 'rgba(255,255,255,0.04)'};
        border: 2px solid ${isEarned ? color + '50' : 'rgba(255,255,255,0.08)'};
        display: flex; align-items: center; justify-content: center;
        font-size: 1.6rem;
      ">
        ${badge.icon || '🏆'}
      </div>
      <h4 style="margin: 0 0 6px 0; font-size: 0.88rem; color: ${isEarned ? '#fff' : 'var(--text-secondary)'}; font-weight: 700;">
        ${badge.name}
      </h4>
      <p style="margin: 0 0 10px 0; font-size: 0.72rem; color: var(--text-tertiary); line-height: 1.4;">
        ${badge.description}
      </p>
      <div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
        <span style="
          font-size: 0.7rem; font-weight: 700;
          padding: 2px 8px; border-radius: 999px;
          background: ${color}15; color: ${color};
        ">
          +${badge.xp_reward} XP
        </span>
        ${isEarned && badge.earned_at ? `
          <span style="font-size: 0.65rem; color: var(--text-tertiary);">
            ${new Date(badge.earned_at).toLocaleDateString()}
          </span>
        ` : ''}
      </div>
    </div>
  `;
}
