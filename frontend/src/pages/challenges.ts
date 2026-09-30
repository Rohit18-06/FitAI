// ============================================================
// FitAI – Challenges Page
// Phase 7: Browse, join, and track fitness challenges
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { ChallengeResponse, ChallengeCreate } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';
import { showToast } from '../components/toast';

type ChallengeTab = 'browse' | 'mine' | 'create';
let currentTab: ChallengeTab = 'browse';

const TYPE_ICONS: Record<string, string> = {
  steps: 'footprints',
  workouts: 'dumbbell',
  calories: 'flame',
  distance: 'map-pin',
  streak: 'zap',
  default: 'target',
};

const TYPE_COLORS: Record<string, string> = {
  steps: '#3B82F6',
  workouts: '#8B5CF6',
  calories: '#EF4444',
  distance: '#10B981',
  streak: '#F59E0B',
  default: '#06B6D4',
};

function daysRemaining(endDate: string): number {
  const diff = new Date(endDate).getTime() - Date.now();
  return Math.max(0, Math.ceil(diff / 86400000));
}

function renderChallengeCard(c: ChallengeResponse, index: number): string {
  const icon = TYPE_ICONS[c.challenge_type] || TYPE_ICONS.default;
  const color = TYPE_COLORS[c.challenge_type] || TYPE_COLORS.default;
  const remaining = daysRemaining(c.end_date);
  const progressPct = c.my_progress != null ? Math.min(100, (c.my_progress / c.target_value) * 100) : 0;

  return `
    <div class="card glass-card" style="padding: 0; overflow: hidden; opacity: 0; transform: translateY(12px);" data-anim="${index}">
      <!-- Color accent bar -->
      <div style="height: 4px; background: linear-gradient(90deg, ${color}, ${color}80);"></div>

      <div style="padding: 24px;">
        <!-- Header -->
        <div style="display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px;">
          <div style="
            width: 48px; height: 48px; border-radius: 14px;
            background: ${color}15; border: 1px solid ${color}30;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
          ">
            <i data-lucide="${icon}" style="width: 22px; height: 22px; color: ${color};"></i>
          </div>
          <div style="flex: 1; min-width: 0;">
            <h3 style="margin: 0 0 4px 0; font-size: 1rem; color: #fff; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${c.title}
            </h3>
            <p style="margin: 0; font-size: 0.78rem; color: var(--text-tertiary);">
              by ${c.creator_username || 'FitAI'} · ${c.challenge_type}
            </p>
          </div>
          ${c.is_active
            ? `<span style="padding: 4px 10px; border-radius: 999px; background: #10B98120; color: #10B981; font-size: 0.7rem; font-weight: 700;">ACTIVE</span>`
            : `<span style="padding: 4px 10px; border-radius: 999px; background: #EF444420; color: #EF4444; font-size: 0.7rem; font-weight: 700;">ENDED</span>`
          }
        </div>

        ${c.description ? `<p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; margin: 0 0 16px 0;">${c.description}</p>` : ''}

        <!-- Stats Row -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
          <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 10px;">
            <div style="font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Target</div>
            <div style="font-size: 1rem; font-weight: 800; color: ${color};">${c.target_value.toLocaleString()}</div>
          </div>
          <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 10px;">
            <div style="font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Reward</div>
            <div style="font-size: 1rem; font-weight: 800; color: #FBBF24;">${c.reward_xp} XP</div>
          </div>
          <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 10px;">
            <div style="font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">${remaining > 0 ? 'Days Left' : 'Status'}</div>
            <div style="font-size: 1rem; font-weight: 800; color: ${remaining <= 3 && remaining > 0 ? '#EF4444' : 'var(--text-primary)'};">
              ${remaining > 0 ? remaining : 'Ended'}
            </div>
          </div>
        </div>

        <!-- Progress (if joined) -->
        ${c.is_joined ? `
          <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span style="font-size: 0.75rem; color: var(--text-secondary);">Your Progress</span>
              <span style="font-size: 0.75rem; font-weight: 700; color: ${c.is_completed ? '#10B981' : color};">
                ${c.is_completed ? '✓ Completed' : `${progressPct.toFixed(0)}%`}
              </span>
            </div>
            <div style="height: 6px; border-radius: 99px; background: rgba(255,255,255,0.06); overflow: hidden;">
              <div style="height: 100%; border-radius: 99px; width: ${progressPct}%; background: linear-gradient(90deg, ${color}, ${color}cc); transition: width 0.5s ease;"></div>
            </div>
          </div>
        ` : ''}

        <!-- Footer -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.78rem; color: var(--text-tertiary);">
            <i data-lucide="users" style="width: 14px; height: 14px; display: inline; vertical-align: -2px;"></i>
            ${c.participants_count} participants
          </span>
          ${c.is_joined
            ? `<button class="btn btn--outline" style="padding: 8px 18px; font-size: 0.8rem;" data-leave="${c.id}">Leave</button>`
            : c.is_active
              ? `<button class="btn btn--primary" style="padding: 8px 18px; font-size: 0.8rem;" data-join="${c.id}">
                  <i data-lucide="swords" style="width: 14px; height: 14px;"></i> Join Challenge
                </button>`
              : ''
          }
        </div>
      </div>
    </div>
  `;
}

export async function renderChallengesPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/challenges'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-header__title">
        Fitness <span class="navbar__logo-gradient">Challenges</span>
      </h1>
      <p class="page-header__subtitle">
        Push your limits with community challenges and earn XP rewards
      </p>
    </div>

    <!-- Tabs -->
    <div style="
      display: inline-flex; background: rgba(255,255,255,0.04);
      padding: 4px; border-radius: var(--radius-full);
      border: 1px solid var(--glass-border); margin-bottom: 24px;
    ">
      <button class="chart-container__period-btn chart-container__period-btn--active" data-ctab="browse">
        <i data-lucide="compass" style="width: 14px; height: 14px;"></i> Browse All
      </button>
      <button class="chart-container__period-btn" data-ctab="mine">
        <i data-lucide="flag" style="width: 14px; height: 14px;"></i> My Challenges
      </button>
      <button class="chart-container__period-btn" data-ctab="create">
        <i data-lucide="plus" style="width: 14px; height: 14px;"></i> Create
      </button>
    </div>

    <div id="challenges-content">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading challenges...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(container);

  container.querySelectorAll('[data-ctab]').forEach(btn => {
    btn.addEventListener('click', () => {
      currentTab = (btn as HTMLElement).dataset.ctab as ChallengeTab;
      container.querySelectorAll('[data-ctab]').forEach(b => b.classList.remove('chart-container__period-btn--active'));
      btn.classList.add('chart-container__period-btn--active');
      renderContent(container);
    });
  });

  await renderContent(container);
  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

async function renderContent(container: HTMLElement): Promise<void> {
  const content = container.querySelector('#challenges-content') as HTMLElement;
  if (!content) return;

  switch (currentTab) {
    case 'browse': return loadChallenges(content, 'all');
    case 'mine': return loadChallenges(content, 'mine');
    case 'create': return renderCreateForm(content);
  }
}

async function loadChallenges(el: HTMLElement, mode: 'all' | 'mine'): Promise<void> {
  el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><div class="spinner" style="margin: 0 auto 1rem;"></div><p style="color: var(--text-secondary);">Loading...</p></div>`;

  try {
    const challenges = mode === 'mine'
      ? await socialApi.getMyChallenges()
      : await socialApi.listChallenges();

    if (challenges.length === 0) {
      el.innerHTML = `
        <div class="card glass-card" style="padding: 4rem; text-align: center;">
          <i data-lucide="target" style="width: 48px; height: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
          <h3 style="color: var(--text-primary); margin: 0 0 8px 0;">
            ${mode === 'mine' ? 'No challenges joined' : 'No challenges available'}
          </h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">
            ${mode === 'mine' ? 'Browse and join challenges to see them here!' : 'Be the first to create a challenge!'}
          </p>
        </div>
      `;
      refreshIcons(el);
      return;
    }

    el.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px;">
        ${challenges.map((c, i) => renderChallengeCard(c, i)).join('')}
      </div>
    `;

    refreshIcons(el);

    // Animate
    el.querySelectorAll('[data-anim]').forEach((card, i) => {
      gsap.to(card, { opacity: 1, y: 0, duration: 0.4, delay: i * 0.06, ease: 'power2.out' });
    });

    // Join
    el.querySelectorAll('[data-join]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt((btn as HTMLElement).dataset.join!, 10);
        try {
          await socialApi.joinChallenge(id);
          showToast('Joined challenge!', 'success');
          loadChallenges(el, mode);
        } catch { showToast('Failed to join', 'error'); }
      });
    });

    // Leave
    el.querySelectorAll('[data-leave]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt((btn as HTMLElement).dataset.leave!, 10);
        try {
          await socialApi.leaveChallenge(id);
          showToast('Left challenge', 'info');
          loadChallenges(el, mode);
        } catch { showToast('Failed to leave', 'error'); }
      });
    });
  } catch {
    el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><p style="color: var(--danger);">Failed to load challenges</p></div>`;
  }
}

function renderCreateForm(el: HTMLElement): void {
  el.innerHTML = `
    <div class="card glass-card" style="padding: 32px; max-width: 600px;">
      <h3 style="color: #fff; margin: 0 0 24px 0; font-size: 1.15rem;">
        <i data-lucide="plus-circle" style="width: 20px; height: 20px; vertical-align: -3px; color: var(--accent-blue);"></i>
        Create a Challenge
      </h3>

      <div style="display: flex; flex-direction: column; gap: 18px;">
        <div>
          <label class="label">Challenge Title</label>
          <input id="ch-title" class="input" type="text" placeholder="e.g., 10K Steps Daily Challenge" style="width: 100%;">
        </div>
        <div>
          <label class="label">Description</label>
          <textarea id="ch-desc" class="input" rows="3" placeholder="Describe the challenge..." style="width: 100%; resize: vertical;"></textarea>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div>
            <label class="label">Type</label>
            <select id="ch-type" class="input" style="width: 100%;">
              <option value="steps">Steps</option>
              <option value="workouts">Workouts</option>
              <option value="calories">Calories</option>
              <option value="distance">Distance</option>
              <option value="streak">Streak</option>
            </select>
          </div>
          <div>
            <label class="label">Target Value</label>
            <input id="ch-target" class="input" type="number" placeholder="e.g., 10000" min="1" style="width: 100%;">
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div>
            <label class="label">Duration (days)</label>
            <input id="ch-duration" class="input" type="number" placeholder="7" min="1" max="365" value="7" style="width: 100%;">
          </div>
          <div>
            <label class="label">XP Reward</label>
            <input id="ch-xp" class="input" type="number" placeholder="100" min="0" value="100" style="width: 100%;">
          </div>
        </div>
        <button id="ch-submit" class="btn btn--primary" style="width: 100%; padding: 14px;">
          <i data-lucide="rocket" style="width: 16px; height: 16px;"></i>
          Launch Challenge
        </button>
      </div>
    </div>
  `;

  refreshIcons(el);

  el.querySelector('#ch-submit')?.addEventListener('click', async () => {
    const title = (el.querySelector('#ch-title') as HTMLInputElement).value.trim();
    const description = (el.querySelector('#ch-desc') as HTMLTextAreaElement).value.trim();
    const challenge_type = (el.querySelector('#ch-type') as HTMLSelectElement).value;
    const target_value = parseInt((el.querySelector('#ch-target') as HTMLInputElement).value, 10);
    const duration_days = parseInt((el.querySelector('#ch-duration') as HTMLInputElement).value, 10);
    const reward_xp = parseInt((el.querySelector('#ch-xp') as HTMLInputElement).value, 10);

    if (!title || !target_value) {
      showToast('Title and target are required', 'error');
      return;
    }

    const data: ChallengeCreate = { title, description, challenge_type, target_value, duration_days, reward_xp };

    try {
      await socialApi.createChallenge(data);
      showToast('Challenge created!', 'success');
      currentTab = 'browse';
      const parentContainer = el.closest('.main-content') as HTMLElement;
      if (parentContainer) {
        parentContainer.querySelectorAll('[data-ctab]').forEach(b => {
          b.classList.toggle('chart-container__period-btn--active', (b as HTMLElement).dataset.ctab === 'browse');
        });
        renderContent(parentContainer);
      }
    } catch { showToast('Failed to create challenge', 'error'); }
  });
}
