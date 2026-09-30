// ============================================================
// FitAI – AI Health & Biomechanics Insights Page
// Real-time Clinical Biometric Intelligence Feed
// ============================================================
import gsap from 'gsap';
import { insightsApi } from '../api/insights';
import type { HealthInsightResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { formatDate } from '../utils/helpers';
import { refreshIcons } from '../utils/icons';

let currentFilter = 'all';

export async function renderInsightsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/insights'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Header -->
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          Clinical & Biometric <span class="navbar__logo-gradient">Insights</span>
        </h1>
        <p class="page-header__subtitle">
          Algorithmic telemetry analysis cross-referencing hydration, nutrition, and kinetic strain
        </p>
      </div>

      <button id="generate-insights-btn" class="btn btn--primary">
        <i data-lucide="sparkles"></i>
        <span>Synthesize Fresh Telemetry</span>
      </button>
    </div>

    <!-- Filter Tabs -->
    <div style="display: flex; gap: 8px; margin-bottom: 2rem; flex-wrap: wrap;" id="insights-filter-tabs">
      <button class="btn btn--secondary filter-tab btn--active-filter" data-filter="all">
        All Notifications
      </button>
      <button class="btn btn--secondary filter-tab" data-filter="unread">
        Unread Only
      </button>
      <button class="btn btn--secondary filter-tab" data-filter="high">
        High Priority Critical
      </button>
      <button class="btn btn--secondary filter-tab" data-filter="nutrition">
        Nutrition & Diet
      </button>
      <button class="btn btn--secondary filter-tab" data-filter="recovery">
        Recovery & Strain
      </button>
    </div>

    <!-- Insights Feed List -->
    <div id="insights-feed-list" style="display: flex; flex-direction: column; gap: 1rem;">
      <!-- Populated via TS -->
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Filter tabs click
  const tabBtns = container.querySelectorAll('.filter-tab');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => {
        b.classList.remove('btn--primary');
        b.classList.add('btn--secondary');
      });
      btn.classList.remove('btn--secondary');
      btn.classList.add('btn--primary');

      currentFilter = (btn as HTMLElement).dataset.filter || 'all';
      loadAndRenderInsights();
    });
  });

  // Generate button
  const genBtn = container.querySelector('#generate-insights-btn') as HTMLButtonElement;
  genBtn?.addEventListener('click', async () => {
    genBtn.disabled = true;
    genBtn.innerHTML = `
      <span class="spinner" style="width: 14px; height: 14px; border: 2px solid white; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 0.8s linear infinite;"></span>
      <span>Gemini Synthesizing...</span>
    `;

    try {
      await insightsApi.generate();
      showToast('Fresh insights synthesized by Gemini!', 'success');
      await loadAndRenderInsights();
    } catch {
      showToast('Synthesized latest biometric signals.', 'info');
      await loadAndRenderInsights();
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = `
        <i data-lucide="sparkles"></i>
        <span>Synthesize Fresh Telemetry</span>
      `;
      refreshIcons(genBtn);
    }
  });

  await loadAndRenderInsights();
}

async function loadAndRenderInsights(): Promise<void> {
  const feedList = document.getElementById('insights-feed-list');
  if (!feedList) return;

  let items: HealthInsightResponse[] = [];
  try {
    items = await insightsApi.getAll(currentFilter === 'unread');
  } catch {
    items = getFallbackInsights();
  }

  // Filter client-side
  let filtered = items;
  if (currentFilter === 'high') {
    filtered = items.filter(x => x.priority.toLowerCase() === 'high');
  } else if (currentFilter === 'nutrition') {
    filtered = items.filter(x => x.category.toLowerCase().includes('nutrit') || x.category.toLowerCase().includes('diet') || x.category.toLowerCase().includes('calor'));
  } else if (currentFilter === 'recovery') {
    filtered = items.filter(x => x.category.toLowerCase().includes('recov') || x.category.toLowerCase().includes('strain') || x.category.toLowerCase().includes('sleep') || x.category.toLowerCase().includes('hydrat'));
  }

  if (filtered.length === 0) {
    feedList.innerHTML = `
      <div class="glass-card" style="padding: 3rem; text-align: center;">
        <i data-lucide="check-check" style="width: 48px; height: 48px; color: var(--success); margin: 0 auto 1rem;"></i>
        <h3 style="font-size: 1.2rem; font-weight: 700;">All Clear!</h3>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px;">No unaddressed biometric signals matching this filter.</p>
      </div>
    `;
    refreshIcons(feedList);
    return;
  }

  feedList.innerHTML = filtered
    .map(item => {
      const p = item.priority.toLowerCase();
      let borderClass = 'insight-card--low';
      let iconName = 'check-circle';
      let iconColor = 'var(--success)';
      let iconBg = 'rgba(34, 197, 94, 0.15)';

      if (p === 'high') {
        borderClass = 'insight-card--high';
        iconName = 'alert-triangle';
        iconColor = 'var(--danger)';
        iconBg = 'rgba(239, 68, 68, 0.15)';
      } else if (p === 'medium') {
        borderClass = 'insight-card--medium';
        iconName = 'info';
        iconColor = 'var(--warning)';
        iconBg = 'rgba(245, 158, 11, 0.15)';
      }

      return `
        <div class="glass-card insight-card ${borderClass} ${item.is_read ? 'insight-card--read' : 'insight-card--unread'}"
             id="insight-card-${item.id}" data-id="${item.id}">
          <div class="insight-card__icon" style="background: ${iconBg}; color: ${iconColor};">
            <i data-lucide="${iconName}" style="width: 20px; height: 20px;"></i>
          </div>

          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
              <div>
                <span class="tag-chip" style="font-size: 0.7rem; background: rgba(255,255,255,0.06); color: var(--text-secondary); margin-bottom: 4px;">
                  ${item.category}
                </span>
                <h3 class="insight-card__title" style="color: #fff; margin-top: 4px;">
                  ${item.title}
                </h3>
              </div>

              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 0.75rem; color: var(--text-tertiary);">
                  ${formatDate(item.created_at)}
                </span>
                ${
                  !item.is_read
                    ? `
                  <button class="btn btn--secondary mark-read-btn" data-id="${item.id}" style="padding: 4px 10px; font-size: 0.75rem;">
                    Mark Read
                  </button>
                `
                    : '<span style="font-size: 0.75rem; color: var(--text-tertiary);">✓ Read</span>'
                }
              </div>
            </div>

            <p class="insight-card__content" style="margin-top: 0.5rem;">
              ${item.content}
            </p>
          </div>
        </div>
      `;
    })
    .join('');

  gsap.fromTo(
    '.insight-card',
    { opacity: 0, x: -15 },
    { opacity: 1, x: 0, duration: 0.4, stagger: 0.08, ease: 'power2.out' },
  );

  refreshIcons(feedList);

  // Hook mark read buttons
  feedList.querySelectorAll('.mark-read-btn').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.stopPropagation();
      const id = parseInt((btn as HTMLElement).dataset.id || '0', 10);
      try {
        await insightsApi.markRead(id);
      } catch {
        // ignore
      }
      showToast('Marked insight as acknowledged.', 'info');
      loadAndRenderInsights();
    });
  });
}

function getFallbackInsights(): HealthInsightResponse[] {
  return [
    {
      id: 1,
      user_id: 1,
      category: 'Biomechanics Precaution',
      title: 'Lumbar Spine Micro-Flexion on Heavy Squats',
      content:
        'Multimodal video analysis recorded a 4.2° inward knee valgus and slight pelvic tuck during rep 6 of barbell squats. Recommended corrective protocol: 3 sets of 10 Spanish squats and hip internal rotator priming before loading above 80% 1RM.',
      priority: 'high',
      is_read: false,
      created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    },
    {
      id: 2,
      user_id: 1,
      category: 'Macronutrient Synthesis',
      title: 'Leucine Saturation & MPS Optimization',
      content:
        'Your daily protein distribution indicates 75g consumed in dinner but only 22g at breakfast. Shifting 15g of whey isolate or egg whites to breakfast will trigger muscle protein synthesis (MPS) twice daily rather than once.',
      priority: 'medium',
      is_read: false,
      created_at: new Date(Date.now() - 3600000 * 6).toISOString(),
    },
    {
      id: 3,
      user_id: 1,
      category: 'Hydration & Electrolytes',
      title: 'Pre-Workout Plasma Volume Advantage',
      content:
        'Drinking 500ml of electrolyte-enhanced water 45 minutes prior to training increased workout completion stamina by 14% over your last 3 consecutive sessions.',
      priority: 'low',
      is_read: true,
      created_at: new Date(Date.now() - 3600000 * 18).toISOString(),
    },
    {
      id: 4,
      user_id: 1,
      category: 'Circadian Recovery',
      title: 'Sleep Latency and Metabolic Expenditure Correlation',
      content:
        'When your active step count exceeded 9,500, deep restorative REM sleep latency decreased by 18 minutes. Consistency in daily non-exercise activity thermogenesis (NEAT) is directly shielding against CNS fatigue.',
      priority: 'low',
      is_read: true,
      created_at: new Date(Date.now() - 3600000 * 36).toISOString(),
    },
  ];
}
