// ============================================================
// FitAI – Smart Coach Intelligence Page
// Phase 8: Recovery Scoring, Injury Risk Engine, Plateau Detection,
// and Weekly AI Coaching Reports
// ============================================================
import { trainingApi } from '../api/training';
import type {
  RecoveryAssessmentResponse,
  InjuryRiskResponse,
  PlateauReport,
  WeeklyReportResponse,
} from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';

export async function renderSmartCoachPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/smart-coach'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          Smart Coach <span class="navbar__logo-gradient">Intelligence</span>
        </h1>
        <p class="page-header__subtitle">
          Real-time biomechanics, recovery scoring, plateau radar, and injury prevention
        </p>
      </div>
      <div style="display: flex; gap: 0.75rem;">
        <button id="btn-recompute-recovery" class="btn btn-secondary" style="display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="refresh-cw" style="width: 16px; height: 16px;"></i>
          <span>Check Recovery</span>
        </button>
        <button id="btn-generate-report" class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="sparkles" style="width: 16px; height: 16px;"></i>
          <span>Generate Weekly Report</span>
        </button>
      </div>
    </div>

    <div id="coach-intel-content">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Analyzing biometric telemetry...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons();

  await loadCoachIntelligence(container);
}

async function loadCoachIntelligence(container: HTMLElement): Promise<void> {
  const content = container.querySelector('#coach-intel-content');
  if (!content) return;

  try {
    const [recovery, injury, plateaus, reports] = await Promise.all([
      trainingApi.getLatestRecovery(),
      trainingApi.getLatestInjuryRisk(),
      trainingApi.detectPlateaus(),
      trainingApi.listWeeklyReports(4),
    ]);

    renderIntelligenceView(container, content, recovery, injury, plateaus, reports);
  } catch (err) {
    content.innerHTML = `
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <p style="color: var(--danger);">Failed to load Smart Coach intelligence.</p>
      </div>
    `;
  }
}

function renderIntelligenceView(
  container: HTMLElement,
  content: Element,
  recovery: RecoveryAssessmentResponse | null,
  injury: InjuryRiskResponse | null,
  plateaus: PlateauReport[],
  reports: WeeklyReportResponse[]
): void {
  const recoveryScore = recovery?.score ?? 75;
  const recoveryStatus = recovery?.status ?? 'Good';
  const injuryLevel = injury?.risk_level ?? 'Low';
  const injuryScore = injury?.risk_score ?? 20;

  content.innerHTML = `
    <!-- Top KPI Grid: Recovery & Injury Risk -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Recovery Assessment Widget -->
      <div class="card glass-card" style="padding: 1.75rem; border-top: 4px solid #3B82F6;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <i data-lucide="activity" style="width: 20px; height: 20px; color: #3B82F6;"></i>
            <span>Recovery Readiness</span>
          </h3>
          <span class="badge" style="background: rgba(59, 130, 246, 0.15); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.3); padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
            ${recoveryStatus}
          </span>
        </div>

        <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1.25rem;">
          <div style="width: 85px; height: 85px; border-radius: 50%; background: conic-gradient(#3B82F6 ${recoveryScore * 3.6}deg, rgba(255,255,255,0.06) 0deg); display: flex; align-items: center; justify-content: center; position: relative;">
            <div style="width: 68px; height: 68px; border-radius: 50%; background: #0F172A; display: flex; flex-direction: column; align-items: center; justify-content: center;">
              <span style="font-size: 1.5rem; font-weight: 800; color: #fff; line-height: 1;">${recoveryScore}</span>
              <span style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">/100</span>
            </div>
          </div>

          <div style="flex: 1;">
            <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0 0 0.5rem 0; line-height: 1.4;">
              ${recovery?.recommendation || 'Your nervous system and muscle fibers are ready for standard training volume.'}
            </p>
            <div style="font-size: 0.75rem; color: var(--text-secondary);">Updated: ${recovery?.computed_at ? new Date(recovery.computed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Today'}</div>
          </div>
        </div>

        <!-- Telemetry Breakdown -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06);">
          <div style="background: rgba(255,255,255,0.02); padding: 0.5rem 0.75rem; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: var(--text-secondary);">Sleep Rest</div>
            <div style="font-size: 1rem; font-weight: 700;">${recovery?.sleep_score ?? 80}/100</div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 0.5rem 0.75rem; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: var(--text-secondary);">HRV Score</div>
            <div style="font-size: 1rem; font-weight: 700;">${recovery?.hrv_score ?? 78}/100</div>
          </div>
        </div>
      </div>

      <!-- Injury Risk Radar Widget -->
      <div class="card glass-card" style="padding: 1.75rem; border-top: 4px solid ${
        injuryLevel === 'High' ? '#EF4444' : injuryLevel === 'Moderate' ? '#F59E0B' : '#10B981'
      };">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
          <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <i data-lucide="shield-alert" style="width: 20px; height: 20px; color: ${
              injuryLevel === 'High' ? '#EF4444' : injuryLevel === 'Moderate' ? '#F59E0B' : '#10B981'
            };"></i>
            <span>Injury Risk Radar</span>
          </h3>
          <span class="badge" style="background: ${
            injuryLevel === 'High' ? 'rgba(239, 68, 68, 0.15)' : injuryLevel === 'Moderate' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)'
          }; color: ${
            injuryLevel === 'High' ? '#EF4444' : injuryLevel === 'Moderate' ? '#F59E0B' : '#10B981'
          }; border: 1px solid ${
            injuryLevel === 'High' ? 'rgba(239, 68, 68, 0.3)' : injuryLevel === 'Moderate' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(16, 185, 129, 0.3)'
          }; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
            ${injuryLevel} Risk (${injuryScore}/100)
          </span>
        </div>

        <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0 0 1rem 0; line-height: 1.4;">
          ${injury?.recommendation || 'Low injury risk. Biomechanical load and training frequency are well balanced.'}
        </p>

        <!-- Corrective Mobility Actions -->
        <div>
          <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;">Corrective Mobility Actions</div>
          <div style="display: flex; flex-direction: column; gap: 0.4rem;">
            ${(injury?.corrective_actions?.length ? injury.corrective_actions : [
              'Continue dynamic warmups before heavy compound lifts',
              'Maintain 7+ hours of uninterrupted sleep for tissue repair',
              'Keep monitoring barbell bar path in video analyzer'
            ]).slice(0, 3).map(action => `
              <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem;">
                <i data-lucide="check-circle" style="width: 14px; height: 14px; color: #10B981; flex-shrink: 0;"></i>
                <span>${action}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>

    <!-- Plateau Detection Radar -->
    <div class="card glass-card" style="padding: 1.75rem; margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="compass" style="width: 22px; height: 22px; color: var(--accent);"></i>
          <span>Plateau Detection Radar</span>
        </h3>
        <span style="font-size: 0.85rem; color: var(--text-secondary);">3-Week Biometric Telemetry</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
        ${plateaus.map(p => `
          <div style="padding: 1rem; border-radius: 10px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <span style="font-weight: 700; font-size: 0.95rem;">${(p.plateau_type || 'General').toUpperCase()}</span>
              <span class="badge" style="background: ${p.detected ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)'}; color: ${p.detected ? '#F59E0B' : '#10B981'}; font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 9999px;">
                ${p.detected ? `${p.severity.toUpperCase()} PLATEAU` : 'OPTIMAL ADAPTATION'}
              </span>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0; line-height: 1.4;">${p.recommendation || 'Progressing normally.'}</p>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Weekly AI Coaching Reports Timeline -->
    <div class="card glass-card" style="padding: 1.75rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.2rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
          <i data-lucide="file-text" style="width: 22px; height: 22px; color: #8B5CF6;"></i>
          <span>Weekly AI Coaching Reports</span>
        </h3>
        <span style="font-size: 0.85rem; color: var(--text-secondary);">${reports.length} Reports Logged</span>
      </div>

      ${reports.length === 0 ? `
        <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
          <p>No coaching reports generated yet. Click "Generate Weekly Report" above to synthesize your first summary.</p>
        </div>
      ` : `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
          ${reports.map(r => `
            <div style="padding: 1.25rem; background: rgba(255,255,255,0.02); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                <span style="font-weight: 700; font-size: 1rem; color: #fff;">
                  Report • ${new Date(r.week_start).toLocaleDateString()} to ${new Date(r.week_end).toLocaleDateString()}
                </span>
                <span class="badge" style="background: rgba(139, 92, 246, 0.15); color: #8B5CF6; border: 1px solid rgba(139, 92, 246, 0.3); padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
                  Progress Score: ${r.progress_score}/100
                </span>
              </div>

              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.75rem; line-height: 1.5;">${r.training_summary || ''}</p>
              <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem; line-height: 1.5;">${r.recovery_summary || ''}</p>

              <!-- Highlights -->
              <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                ${(r.highlights || []).map(h => `
                  <span style="font-size: 0.8rem; background: rgba(255,255,255,0.05); padding: 0.3rem 0.6rem; border-radius: 6px; color: #E2E8F0;">${h}</span>
                `).join('')}
              </div>
            </div>
          `).join('')}
        </div>
      `}
    </div>
  `;

  refreshIcons();

  // Attach button event handlers
  container.querySelector('#btn-recompute-recovery')?.addEventListener('click', async (e) => {
    const btn = e.currentTarget as HTMLButtonElement;
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>';
    try {
      await trainingApi.computeRecovery();
      await loadCoachIntelligence(container);
    } catch {
      alert('Could not compute recovery.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="refresh-cw" style="width: 16px; height: 16px;"></i><span>Check Recovery</span>';
      refreshIcons();
    }
  });

  container.querySelector('#btn-generate-report')?.addEventListener('click', async (e) => {
    const btn = e.currentTarget as HTMLButtonElement;
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div> Synthesizing...';
    try {
      await trainingApi.generateWeeklyReport();
      await loadCoachIntelligence(container);
    } catch {
      alert('Could not generate report.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="sparkles" style="width: 16px; height: 16px;"></i><span>Generate Weekly Report</span>';
      refreshIcons();
    }
  });
}
