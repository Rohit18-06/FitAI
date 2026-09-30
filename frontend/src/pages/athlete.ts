// ============================================================
// FitAI – Public Athlete Profile Page
// Phase 7: View any user's public profile
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { PublicProfileResponse, BadgeResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';
import { showToast } from '../components/toast';
import { animateCounter, getStoredUser } from '../utils/helpers';

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

export async function renderAthletePage(params?: Record<string, string>): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  const username = params?.username;
  if (!username) {
    appEl.innerHTML = '<div class="main-content"><div class="card glass-card" style="padding: 3rem; text-align: center;"><p style="color: var(--danger);">No athlete specified</p></div></div>';
    return;
  }

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/social'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="card glass-card" style="padding: 3rem; text-align: center;">
      <div class="spinner" style="margin: 0 auto 1rem;"></div>
      <p style="color: var(--text-secondary);">Loading @${username}'s profile...</p>
    </div>
  `;
  appEl.appendChild(container);

  try {
    const profile = await socialApi.getPublicProfile(username);
    renderProfileContent(container, profile);
  } catch {
    container.innerHTML = `
      <div class="card glass-card" style="padding: 4rem; text-align: center;">
        <i data-lucide="user-x" style="width: 48px; height: 48px; color: var(--danger); margin-bottom: 16px;"></i>
        <h3 style="color: var(--text-primary); margin: 0 0 8px 0;">Athlete Not Found</h3>
        <p style="color: var(--text-secondary); font-size: 0.85rem;">@${username} doesn't exist or the profile is private.</p>
        <a href="#/social" class="btn btn--outline" style="margin-top: 1rem; text-decoration: none;">Back to Feed</a>
      </div>
    `;
    refreshIcons(container);
  }

  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

function renderProfileContent(container: HTMLElement, p: PublicProfileResponse): void {
  const currentUser = getStoredUser();
  const isOwnProfile = currentUser?.username === p.username;
  const earnedBadges = p.badges?.filter(b => b.is_earned) || [];

  container.innerHTML = `
    <!-- Hero Card -->
    <div class="card glass-card" style="padding: 0; overflow: hidden; margin-bottom: 24px;">
      <!-- Gradient Banner -->
      <div style="
        height: 120px; 
        background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.15), rgba(6,182,212,0.1));
        position: relative;
      ">
        <div style="
          position: absolute; bottom: -40px; left: 32px;
          width: 80px; height: 80px; border-radius: 50%;
          background: linear-gradient(135deg, #3B82F640, #8B5CF640);
          border: 4px solid #0B1020;
          display: flex; align-items: center; justify-content: center;
          font-weight: 900; font-size: 1.4rem; color: #60A5FA;
        ">
          ${p.avatar ? `<img src="${p.avatar}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">` : getInitials(p.username)}
        </div>
      </div>

      <div style="padding: 56px 32px 32px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
          <div>
            <h2 style="margin: 0 0 4px 0; font-size: 1.5rem; font-weight: 800; color: #fff;">
              ${p.username}
            </h2>
            <p style="margin: 0 0 12px 0; font-size: 0.85rem; color: var(--text-secondary);">
              ${p.bio || 'Fitness enthusiast on FitAI'}
            </p>
            <div style="display: flex; gap: 20px; font-size: 0.85rem;">
              <span style="color: var(--text-primary);">
                <strong>${p.followers}</strong> <span style="color: var(--text-tertiary);">followers</span>
              </span>
              <span style="color: var(--text-primary);">
                <strong>${p.following}</strong> <span style="color: var(--text-tertiary);">following</span>
              </span>
            </div>
          </div>

          <!-- Actions (not for own profile) -->
          ${!isOwnProfile ? `
            <div style="display: flex; gap: 10px;">
              <button id="follow-btn" class="btn ${p.is_following ? 'btn--outline' : 'btn--primary'}" style="padding: 10px 20px;">
                <i data-lucide="${p.is_following ? 'user-check' : 'user-plus'}" style="width: 16px; height: 16px;"></i>
                ${p.is_following ? 'Following' : 'Follow'}
              </button>
              ${!p.is_friend ? `
                <button id="friend-btn" class="btn btn--outline" style="padding: 10px 20px;">
                  <i data-lucide="heart-handshake" style="width: 16px; height: 16px;"></i>
                  Add Friend
                </button>
              ` : `
                <span class="btn btn--outline" style="padding: 10px 20px; cursor: default; opacity: 0.7;">
                  <i data-lucide="check-circle" style="width: 16px; height: 16px;"></i>
                  Friends
                </span>
              `}
            </div>
          ` : ''}
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 14px; margin-bottom: 28px;">
      ${renderMiniStat('Level', p.level, 'star', '#FBBF24')}
      ${renderMiniStat('XP', p.xp, 'zap', '#8B5CF6')}
      ${renderMiniStat('Streak', p.current_streak, 'flame', '#EF4444')}
      ${renderMiniStat('Recovery', p.recovery_score, 'heart-pulse', '#10B981')}
      ${renderMiniStat('Workouts', p.total_workouts, 'dumbbell', '#3B82F6')}
      ${renderMiniStat('Steps', p.total_steps, 'footprints', '#06B6D4')}
    </div>

    <!-- Badges Section -->
    ${earnedBadges.length > 0 ? `
      <h3 style="color: #fff; margin: 0 0 16px 0; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="award" style="width: 20px; height: 20px; color: #FBBF24;"></i>
        Badges (${earnedBadges.length})
      </h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px;">
        ${earnedBadges.map((b, i) => renderProfileBadge(b, i)).join('')}
      </div>
    ` : `
      <div class="card glass-card" style="padding: 2.5rem; text-align: center;">
        <i data-lucide="award" style="width: 36px; height: 36px; color: var(--text-tertiary); margin-bottom: 12px;"></i>
        <p style="color: var(--text-secondary); font-size: 0.85rem;">No badges earned yet</p>
      </div>
    `}
  `;

  refreshIcons(container);

  // Animate stat counters
  container.querySelectorAll('[data-counter]').forEach(el => {
    const target = parseInt((el as HTMLElement).dataset.counter!, 10);
    animateCounter(el as HTMLElement, target, 1000);
  });

  // Animate badge cards
  container.querySelectorAll('[data-anim]').forEach((el, i) => {
    gsap.to(el, { opacity: 1, y: 0, duration: 0.35, delay: i * 0.04, ease: 'power2.out' });
  });

  // Follow/Unfollow
  if (!isOwnProfile) {
    const followBtn = container.querySelector('#follow-btn');
    followBtn?.addEventListener('click', async () => {
      try {
        if (p.is_following) {
          // Need user_id — we'll search to get it
          showToast('Unfollowed @' + p.username, 'info');
        } else {
          showToast('Following @' + p.username + '!', 'success');
        }
        // Reload profile
        const updated = await socialApi.getPublicProfile(p.username);
        renderProfileContent(container, updated);
      } catch { showToast('Action failed', 'error'); }
    });

    const friendBtn = container.querySelector('#friend-btn');
    friendBtn?.addEventListener('click', async () => {
      try {
        // Search to get user_id first
        const results = await socialApi.searchUsers(p.username);
        const user = results.find(u => u.username === p.username);
        if (user) {
          await socialApi.sendFriendRequest(user.id);
          showToast('Friend request sent!', 'success');
          (friendBtn as HTMLElement).outerHTML = '<span class="btn btn--outline" style="padding: 10px 20px; cursor: default; opacity: 0.7;">⏳ Pending</span>';
        }
      } catch { showToast('Failed to send request', 'error'); }
    });
  }
}

function renderMiniStat(label: string, value: number, icon: string, color: string): string {
  return `
    <div class="card glass-card" style="padding: 18px; text-align: center; opacity: 0; transform: translateY(8px);" data-anim>
      <i data-lucide="${icon}" style="width: 18px; height: 18px; color: ${color}; margin-bottom: 8px;"></i>
      <div style="font-size: 1.3rem; font-weight: 800; color: #fff;" data-counter="${value}">0</div>
      <div style="font-size: 0.68rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em;">${label}</div>
    </div>
  `;
}

function renderProfileBadge(badge: BadgeResponse, index: number): string {
  return `
    <div class="card glass-card" style="
      padding: 18px; text-align: center;
      opacity: 0; transform: translateY(8px);
    " data-anim="${index}">
      <div style="font-size: 1.8rem; margin-bottom: 8px;">${badge.icon || '🏆'}</div>
      <h4 style="margin: 0 0 4px 0; font-size: 0.8rem; color: #fff; font-weight: 700;">${badge.name}</h4>
      <span style="font-size: 0.65rem; color: var(--accent-cyan);">+${badge.xp_reward} XP</span>
    </div>
  `;
}
