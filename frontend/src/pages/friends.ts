// ============================================================
// FitAI – Friends & Connections Page
// Phase 7: Friend management, search, requests
// ============================================================
import gsap from 'gsap';
import { socialApi } from '../api/social';
import type { FriendshipResponse, UserSearchResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';
import { showToast } from '../components/toast';

type FriendsTab = 'friends' | 'requests' | 'search';
let activeTab: FriendsTab = 'friends';

function getInitials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

export async function renderFriendsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/friends'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header">
      <h1 class="page-header__title">
        Friends & <span class="navbar__logo-gradient">Connections</span>
      </h1>
      <p class="page-header__subtitle">
        Find athletes, send friend requests, and grow your fitness network
      </p>
    </div>

    <!-- Tabs -->
    <div style="
      display: inline-flex; background: rgba(255,255,255,0.04); 
      padding: 4px; border-radius: var(--radius-full);
      border: 1px solid var(--glass-border); margin-bottom: 24px;
    ">
      <button class="chart-container__period-btn chart-container__period-btn--active" data-ftab="friends">
        <i data-lucide="users" style="width: 14px; height: 14px;"></i>
        My Friends
      </button>
      <button class="chart-container__period-btn" data-ftab="requests">
        <i data-lucide="inbox" style="width: 14px; height: 14px;"></i>
        Requests
        <span id="req-badge" style="background: #ef4444; color: #fff; font-size: 0.65rem; padding: 1px 6px; border-radius: 999px; margin-left: 4px; display: none;"></span>
      </button>
      <button class="chart-container__period-btn" data-ftab="search">
        <i data-lucide="search" style="width: 14px; height: 14px;"></i>
        Find Athletes
      </button>
    </div>

    <!-- Content -->
    <div id="friends-content">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(container);

  // Tab switching
  container.querySelectorAll('[data-ftab]').forEach(btn => {
    btn.addEventListener('click', () => {
      activeTab = (btn as HTMLElement).dataset.ftab as FriendsTab;
      container.querySelectorAll('[data-ftab]').forEach(b => b.classList.remove('chart-container__period-btn--active'));
      btn.classList.add('chart-container__period-btn--active');
      renderTabContent(container);
    });
  });

  // Load pending count
  try {
    const pending = await socialApi.getPendingRequests();
    if (pending.length > 0) {
      const badge = container.querySelector('#req-badge') as HTMLElement;
      if (badge) {
        badge.textContent = `${pending.length}`;
        badge.style.display = 'inline';
      }
    }
  } catch { /* ignore */ }

  await renderTabContent(container);
  gsap.fromTo(container, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' });
}

async function renderTabContent(container: HTMLElement): Promise<void> {
  const content = container.querySelector('#friends-content') as HTMLElement;
  if (!content) return;

  switch (activeTab) {
    case 'friends': return renderFriendsList(content);
    case 'requests': return renderPendingRequests(content);
    case 'search': return renderSearchUI(content);
  }
}

async function renderFriendsList(el: HTMLElement): Promise<void> {
  el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><div class="spinner" style="margin: 0 auto 1rem;"></div><p style="color: var(--text-secondary);">Loading friends...</p></div>`;

  try {
    const friends: any[] = await socialApi.getFriends();

    if (friends.length === 0) {
      el.innerHTML = `
        <div class="card glass-card" style="padding: 4rem; text-align: center;">
          <i data-lucide="users" style="width: 48px; height: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
          <h3 style="color: var(--text-primary); margin: 0 0 8px 0;">No friends yet</h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">Search for athletes to connect with!</p>
        </div>
      `;
      refreshIcons(el);
      return;
    }

    el.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">
        ${friends.map((f: FriendshipResponse, i: number) => `
          <div class="card glass-card" style="padding: 20px; opacity: 0; transform: translateY(12px);" data-anim="${i}">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div style="
                width: 50px; height: 50px; border-radius: 50%;
                background: linear-gradient(135deg, #3B82F640, #8B5CF640);
                border: 2px solid rgba(59,130,246,0.4);
                display: flex; align-items: center; justify-content: center;
                font-weight: 800; font-size: 0.85rem; color: #60A5FA;
                flex-shrink: 0;
              ">
                ${f.friend_avatar ? `<img src="${f.friend_avatar}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">` : getInitials(f.friend_username || 'UN')}
              </div>
              <div style="flex: 1; min-width: 0;">
                <a href="#/athlete/${f.friend_username}" style="
                  font-weight: 700; color: #fff; text-decoration: none; font-size: 0.95rem;
                  display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
                ">${f.friend_username || 'Unknown'}</a>
                <p style="margin: 4px 0 0; font-size: 0.78rem; color: var(--text-tertiary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  ${f.friend_bio || 'Fitness enthusiast'}
                </p>
              </div>
              <button class="btn btn--outline" style="padding: 6px 12px; font-size: 0.75rem;" data-remove-id="${f.id}">
                <i data-lucide="user-minus" style="width: 14px; height: 14px;"></i>
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    refreshIcons(el);
    animateCards(el);

    // Remove friend
    el.querySelectorAll('[data-remove-id]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = parseInt((btn as HTMLElement).dataset.removeId!, 10);
        try {
          await socialApi.removeFriend(id);
          showToast('Friend removed', 'info');
          renderFriendsList(el);
        } catch { showToast('Failed to remove friend', 'error'); }
      });
    });
  } catch {
    el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><p style="color: var(--danger);">Failed to load friends</p></div>`;
  }
}

async function renderPendingRequests(el: HTMLElement): Promise<void> {
  el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><div class="spinner" style="margin: 0 auto 1rem;"></div><p style="color: var(--text-secondary);">Loading requests...</p></div>`;

  try {
    const requests = await socialApi.getPendingRequests();

    if (requests.length === 0) {
      el.innerHTML = `
        <div class="card glass-card" style="padding: 4rem; text-align: center;">
          <i data-lucide="inbox" style="width: 48px; height: 48px; color: var(--text-tertiary); margin-bottom: 16px;"></i>
          <h3 style="color: var(--text-primary); margin: 0 0 8px 0;">No pending requests</h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">You're all caught up!</p>
        </div>
      `;
      refreshIcons(el);
      return;
    }

    el.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 12px;">
        ${requests.map((r, i) => `
          <div class="card glass-card" style="padding: 20px; opacity: 0; transform: translateY(12px);" data-anim="${i}">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div style="
                width: 50px; height: 50px; border-radius: 50%;
                background: linear-gradient(135deg, #F59E0B40, #EF444440);
                border: 2px solid rgba(245,158,11,0.4);
                display: flex; align-items: center; justify-content: center;
                font-weight: 800; font-size: 0.85rem; color: #FBBF24;
                flex-shrink: 0;
              ">
                ${getInitials(r.requester_username || 'UN')}
              </div>
              <div style="flex: 1;">
                <span style="font-weight: 700; color: #fff; font-size: 0.95rem;">${r.requester_username || 'Unknown'}</span>
                <p style="margin: 4px 0 0; font-size: 0.78rem; color: var(--text-tertiary);">Wants to be your friend</p>
              </div>
              <div style="display: flex; gap: 8px;">
                <button class="btn btn--primary" style="padding: 8px 16px; font-size: 0.8rem;" data-accept-id="${r.id}">
                  <i data-lucide="check" style="width: 14px; height: 14px;"></i> Accept
                </button>
                <button class="btn btn--outline" style="padding: 8px 16px; font-size: 0.8rem;" data-reject-id="${r.id}">
                  <i data-lucide="x" style="width: 14px; height: 14px;"></i>
                </button>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    refreshIcons(el);
    animateCards(el);

    // Accept
    el.querySelectorAll('[data-accept-id]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt((btn as HTMLElement).dataset.acceptId!, 10);
        try {
          await socialApi.acceptFriendRequest(id);
          showToast('Friend request accepted!', 'success');
          renderPendingRequests(el);
        } catch { showToast('Failed to accept', 'error'); }
      });
    });

    // Reject
    el.querySelectorAll('[data-reject-id]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = parseInt((btn as HTMLElement).dataset.rejectId!, 10);
        try {
          await socialApi.rejectFriendRequest(id);
          showToast('Request declined', 'info');
          renderPendingRequests(el);
        } catch { showToast('Failed to decline', 'error'); }
      });
    });
  } catch {
    el.innerHTML = `<div class="card glass-card" style="padding: 3rem; text-align: center;"><p style="color: var(--danger);">Failed to load requests</p></div>`;
  }
}

function renderSearchUI(el: HTMLElement): void {
  el.innerHTML = `
    <div class="card glass-card" style="padding: 24px;">
      <div style="display: flex; gap: 12px; margin-bottom: 24px;">
        <div style="flex: 1; position: relative;">
          <i data-lucide="search" style="width: 18px; height: 18px; position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary);"></i>
          <input id="user-search-input" type="text" class="input" placeholder="Search by username..."
            style="padding-left: 42px; width: 100%; background: rgba(255,255,255,0.04);">
        </div>
        <button id="user-search-btn" class="btn btn--primary" style="flex-shrink: 0;">
          Search
        </button>
      </div>
      <div id="search-results" style="display: flex; flex-direction: column; gap: 12px;">
        <div style="text-align: center; padding: 3rem 0;">
          <i data-lucide="search" style="width: 40px; height: 40px; color: var(--text-tertiary); margin-bottom: 12px;"></i>
          <p style="color: var(--text-secondary); font-size: 0.85rem;">Search for athletes to connect with</p>
        </div>
      </div>
    </div>
  `;

  refreshIcons(el);

  const input = el.querySelector('#user-search-input') as HTMLInputElement;
  const btn = el.querySelector('#user-search-btn') as HTMLButtonElement;

  const doSearch = async () => {
    const q = input.value.trim();
    if (q.length < 2) {
      showToast('Enter at least 2 characters', 'info');
      return;
    }
    const results = el.querySelector('#search-results') as HTMLElement;
    results.innerHTML = `<div style="text-align: center; padding: 2rem;"><div class="spinner" style="margin: 0 auto;"></div></div>`;

    try {
      const users: UserSearchResponse[] = await socialApi.searchUsers(q);

      if (users.length === 0) {
        results.innerHTML = `<div style="text-align: center; padding: 3rem 0;"><p style="color: var(--text-secondary);">No athletes found for "${q}"</p></div>`;
        return;
      }

      results.innerHTML = users.map((u, i) => `
        <div class="glass-card" style="
          padding: 16px; border-radius: 12px; 
          background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
          display: flex; align-items: center; gap: 14px;
          opacity: 0; transform: translateY(8px);
        " data-anim="${i}">
          <div style="
            width: 44px; height: 44px; border-radius: 50%;
            background: linear-gradient(135deg, #6366F140, #8B5CF640);
            border: 2px solid rgba(99,102,241,0.4);
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 0.8rem; color: #A78BFA;
            flex-shrink: 0;
          ">
            ${u.avatar ? `<img src="${u.avatar}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">` : getInitials(u.username)}
          </div>
          <div style="flex: 1; min-width: 0;">
            <a href="#/athlete/${u.username}" style="font-weight: 700; color: #fff; text-decoration: none; font-size: 0.9rem;">${u.username}</a>
            <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
              <span style="font-size: 0.72rem; color: var(--accent-cyan); font-weight: 600;">Level ${u.level}</span>
              ${u.bio ? `<span style="font-size: 0.72rem; color: var(--text-tertiary);">· ${u.bio}</span>` : ''}
            </div>
          </div>
          <div style="display: flex; gap: 8px; flex-shrink: 0;">
            ${u.is_friend
              ? '<span style="font-size: 0.75rem; color: var(--success); font-weight: 600;">✓ Friends</span>'
              : u.friend_status === 'pending'
                ? '<span style="font-size: 0.75rem; color: #FBBF24; font-weight: 600;">⏳ Pending</span>'
                : `<button class="btn btn--primary" style="padding: 6px 14px; font-size: 0.75rem;" data-add-friend="${u.id}">
                    <i data-lucide="user-plus" style="width: 13px; height: 13px;"></i> Add
                  </button>`
            }
            ${u.is_following
              ? `<button class="btn btn--outline" style="padding: 6px 14px; font-size: 0.75rem;" data-unfollow="${u.id}">Unfollow</button>`
              : `<button class="btn btn--outline" style="padding: 6px 14px; font-size: 0.75rem;" data-follow="${u.id}">Follow</button>`
            }
          </div>
        </div>
      `).join('');

      refreshIcons(results);
      animateCards(results);

      // Add friend
      results.querySelectorAll('[data-add-friend]').forEach(b => {
        b.addEventListener('click', async () => {
          const uid = parseInt((b as HTMLElement).dataset.addFriend!, 10);
          try {
            await socialApi.sendFriendRequest(uid);
            showToast('Friend request sent!', 'success');
            (b as HTMLElement).outerHTML = '<span style="font-size:0.75rem;color:#FBBF24;font-weight:600;">⏳ Pending</span>';
          } catch { showToast('Failed to send request', 'error'); }
        });
      });

      // Follow
      results.querySelectorAll('[data-follow]').forEach(b => {
        b.addEventListener('click', async () => {
          const uid = parseInt((b as HTMLElement).dataset.follow!, 10);
          try {
            await socialApi.followUser(uid);
            showToast('Following!', 'success');
            (b as HTMLElement).outerHTML = `<button class="btn btn--outline" style="padding:6px 14px;font-size:0.75rem;" disabled>Following</button>`;
          } catch { showToast('Failed to follow', 'error'); }
        });
      });

      // Unfollow
      results.querySelectorAll('[data-unfollow]').forEach(b => {
        b.addEventListener('click', async () => {
          const uid = parseInt((b as HTMLElement).dataset.unfollow!, 10);
          try {
            await socialApi.unfollowUser(uid);
            showToast('Unfollowed', 'info');
            (b as HTMLElement).outerHTML = `<button class="btn btn--outline" style="padding:6px 14px;font-size:0.75rem;" disabled>Follow</button>`;
          } catch { showToast('Failed to unfollow', 'error'); }
        });
      });
    } catch {
      results.innerHTML = `<div style="text-align: center; padding: 2rem;"><p style="color: var(--danger);">Search failed. Try again.</p></div>`;
    }
  };

  btn.addEventListener('click', doSearch);
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') doSearch(); });
}

function animateCards(parent: HTMLElement): void {
  parent.querySelectorAll('[data-anim]').forEach((el, i) => {
    gsap.to(el, { opacity: 1, y: 0, duration: 0.35, delay: i * 0.05, ease: 'power2.out' });
  });
}
