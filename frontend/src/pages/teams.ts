// ============================================================
// FitAI – Teams & Communities Page
// Phase 7: Team creation, browsing, and management
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { TeamResponse, TeamCreate } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';
import { showToast } from '../components/toast';

type TeamsTab = 'browse' | 'create';
let currentTab: TeamsTab = 'browse';

export async function renderTeamsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/teams'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-header__title">
        Teams & <span class="navbar__logo-gradient">Communities</span>
      </h1>
      <p class="page-header__subtitle">
        Join fitness crews, train together, and climb the ranks as a team
      </p>
    </div>

    <!-- Tabs -->
    <div style="
      display: inline-flex; background: rgba(255,255,255,0.04);
      padding: 4px; border-radius: var(--radius-full);
      border: 1px solid var(--glass-border); margin-bottom: 24px;
    ">
      <button class="chart-container__period-btn chart-container__period-btn--active" data-ttab="browse">
        <i data-lucide="users" style="width: 14px; height: 14px;"></i> Browse Teams
      </button>
      <button class="chart-container__period-btn" data-ttab="create">
        <i data-lucide="plus" style="width: 14px; height: 14px;"></i> Create Team
      </button>
    </div>

    <div id="teams-content">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading teams...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(container);

  container.querySelectorAll('[data-ttab]').forEach(btn => {
    btn.addEventListener('click', () => {
      currentTab = (btn as HTMLElement).dataset.ttab as TeamsTab;
      container.querySelectorAll('[data-ttab]').forEach(b => b.classList.remove('chart-container__period-btn--active'));
      btn.classList.add('chart-container__period-btn--active');
      renderTabContent(container);
    });
  });

  await renderTabContent(container);
  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

async function renderTabContent(container: HTMLElement): Promise<void> {
  const content = container.querySelector('#teams-content') as HTMLElement;
  if (!content) return;

  switch (currentTab) {
    case 'browse': return loadTeams(content);
    case 'create': return renderCreateForm(content);
  }
}

async function loadTeams(el: HTMLElement): Promise<void> {
  el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><div class="spinner" style="margin: 0 auto 1rem;"></div><p style="color: var(--text-secondary);">Loading teams...</p></div>`;

  try {
    const teams = await socialApi.listTeams();

    if (teams.length === 0) {
      el.innerHTML = `
        <div class="card glass-card" style="padding: 4rem; text-align: center;">
          <i data-lucide="users" style="width: 48px; height: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
          <h3 style="color: var(--text-primary); margin: 0 0 8px 0;">No teams yet</h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">Be the first to create a fitness team!</p>
        </div>
      `;
      refreshIcons(el);
      return;
    }

    const teamColors = ['#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#06B6D4'];

    el.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
        ${teams.map((t: TeamResponse, i: number) => {
          const color = teamColors[i % teamColors.length];
          return `
            <div class="card glass-card" style="padding: 0; overflow: hidden; opacity: 0; transform: translateY(12px);" data-anim="${i}">
              <!-- Gradient top -->
              <div style="height: 80px; background: linear-gradient(135deg, ${color}30, ${color}10); display: flex; align-items: center; justify-content: center;">
                <div style="
                  width: 56px; height: 56px; border-radius: 16px;
                  background: ${color}25; border: 2px solid ${color}50;
                  display: flex; align-items: center; justify-content: center;
                ">
                  <i data-lucide="shield" style="width: 28px; height: 28px; color: ${color};"></i>
                </div>
              </div>

              <div style="padding: 20px;">
                <h3 style="margin: 0 0 4px 0; font-size: 1.05rem; color: #fff; font-weight: 700;">${t.name}</h3>
                <p style="margin: 0 0 16px 0; font-size: 0.78rem; color: var(--text-tertiary);">
                  Created by ${t.owner_username || 'Unknown'}
                </p>
                ${t.description ? `<p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; margin: 0 0 16px 0;">${t.description}</p>` : ''}

                <!-- Stats -->
                <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                  <div style="display: flex; align-items: center; gap: 6px; font-size: 0.82rem; color: var(--text-secondary);">
                    <i data-lucide="users" style="width: 14px; height: 14px; color: ${color};"></i>
                    ${t.members_count} members
                  </div>
                  ${t.is_member ? `
                    <div style="display: flex; align-items: center; gap: 4px;">
                      <span style="padding: 2px 8px; border-radius: 999px; background: #10B98120; color: #10B981; font-size: 0.7rem; font-weight: 700;">
                        ✓ Member${t.my_role === 'owner' ? ' (Owner)' : t.my_role === 'admin' ? ' (Admin)' : ''}
                      </span>
                    </div>
                  ` : ''}
                </div>

                <!-- Action -->
                ${t.is_member
                  ? t.my_role !== 'owner'
                    ? `<button class="btn btn--outline" style="width: 100%; padding: 10px;" data-leave-team="${t.id}">Leave Team</button>`
                    : `<div style="text-align: center; font-size: 0.78rem; color: var(--text-tertiary);">You own this team</div>`
                  : `<button class="btn btn--primary" style="width: 100%; padding: 10px;" data-join-team="${t.id}">
                      <i data-lucide="user-plus" style="width: 14px; height: 14px;"></i> Join Team
                    </button>`
                }
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;

    refreshIcons(el);

    el.querySelectorAll('[data-anim]').forEach((card, i) => {
      gsap.to(card, { opacity: 1, y: 0, duration: 0.4, delay: i * 0.06, ease: 'power2.out' });
    });

    el.querySelectorAll('[data-join-team]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt((btn as HTMLElement).dataset.joinTeam!, 10);
        try {
          await socialApi.joinTeam(id);
          showToast('Joined team!', 'success');
          loadTeams(el);
        } catch { showToast('Failed to join team', 'error'); }
      });
    });

    el.querySelectorAll('[data-leave-team]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt((btn as HTMLElement).dataset.leaveTeam!, 10);
        try {
          await socialApi.leaveTeam(id);
          showToast('Left team', 'info');
          loadTeams(el);
        } catch { showToast('Failed to leave team', 'error'); }
      });
    });
  } catch {
    el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><p style="color: var(--danger);">Failed to load teams</p></div>`;
  }
}

function renderCreateForm(el: HTMLElement): void {
  el.innerHTML = `
    <div class="card glass-card" style="padding: 32px; max-width: 520px;">
      <h3 style="color: #fff; margin: 0 0 24px 0; font-size: 1.15rem;">
        <i data-lucide="shield-plus" style="width: 20px; height: 20px; vertical-align: -3px; color: var(--accent-purple);"></i>
        Create a Team
      </h3>

      <div style="display: flex; flex-direction: column; gap: 18px;">
        <div>
          <label class="label">Team Name</label>
          <input id="team-name" class="input" type="text" placeholder="e.g., Iron Warriors" style="width: 100%;">
        </div>
        <div>
          <label class="label">Description (optional)</label>
          <textarea id="team-desc" class="input" rows="3" placeholder="What's your team about?" style="width: 100%; resize: vertical;"></textarea>
        </div>
        <button id="team-submit" class="btn btn--primary" style="width: 100%; padding: 14px;">
          <i data-lucide="shield" style="width: 16px; height: 16px;"></i>
          Create Team
        </button>
      </div>
    </div>
  `;

  refreshIcons(el);

  el.querySelector('#team-submit')?.addEventListener('click', async () => {
    const name = (el.querySelector('#team-name') as HTMLInputElement).value.trim();
    const description = (el.querySelector('#team-desc') as HTMLTextAreaElement).value.trim();

    if (!name) {
      showToast('Team name is required', 'error');
      return;
    }

    const data: TeamCreate = { name, description: description || undefined };

    try {
      await socialApi.createTeam(data);
      showToast('Team created!', 'success');
      currentTab = 'browse';
      const parentContainer = el.closest('.main-content') as HTMLElement;
      if (parentContainer) {
        parentContainer.querySelectorAll('[data-ttab]').forEach(b => {
          b.classList.toggle('chart-container__period-btn--active', (b as HTMLElement).dataset.ttab === 'browse');
        });
        renderTabContent(parentContainer);
      }
    } catch { showToast('Failed to create team', 'error'); }
  });
}
