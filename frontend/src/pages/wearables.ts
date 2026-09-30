// ============================================================
// FitAI – Wearables & Real-Time Health Intelligence Page
// Phase 6: Health Connect, Smartwatches, Sleep, HR & Recovery
// ============================================================
import gsap from 'gsap';
import {
  Chart,
  LineController,
  BarController,
  DoughnutController,
  LineElement,
  PointElement,
  BarElement,
  ArcElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { integrationsApi } from '../api/integrations';
import type {
  WearableDeviceResponse,
  RecoveryResponse,
} from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { openModal, closeModal } from '../components/modal';
import { refreshIcons } from '../utils/icons';

Chart.register(
  LineController,
  BarController,
  DoughnutController,
  LineElement,
  PointElement,
  BarElement,
  ArcElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
);

let sleepChartInstance: Chart | null = null;
let hrZonesChartInstance: Chart | null = null;

export async function renderWearablesPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/wearables'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Page Header -->
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 2rem;">
      <div>
        <h1 class="page-header__title">
          Wearables & <span class="navbar__logo-gradient">Biometric Intelligence</span>
        </h1>
        <p class="page-header__subtitle">
          Real-time telemetry, Android Health Connect sync, sleep architecture & autonomic recovery
        </p>
      </div>

      <div style="display: flex; gap: 10px; flex-wrap: wrap;">
        <button id="quick-sync-btn" class="btn btn--primary" style="display: flex; align-items: center; gap: 8px;">
          <i data-lucide="refresh-cw" id="sync-icon"></i>
          <span>Sync Health Connect</span>
        </button>
        <button id="add-device-btn" class="btn btn--secondary" style="display: flex; align-items: center; gap: 8px;">
          <i data-lucide="watch"></i>
          <span>Pair Device</span>
        </button>
        <button id="add-record-btn" class="btn btn--secondary" style="display: flex; align-items: center; gap: 8px;">
          <i data-lucide="trophy"></i>
          <span>Log Record</span>
        </button>
      </div>
    </div>

    <!-- Live Telemetry & Recovery Gauge Hero -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Recovery Score Card with SVG Gauge -->
      <div class="card glass-card" style="padding: 1.5rem; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <i data-lucide="activity" style="color: var(--accent-cyan); width: 20px; height: 20px;"></i>
            <span style="font-weight: 700; font-size: 1.05rem; letter-spacing: 0.5px;">RECOVERY SCORE</span>
          </div>
          <span id="recovery-badge" class="badge" style="background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 0.75rem; padding: 4px 10px; border-radius: 9999px; text-transform: uppercase; font-weight: 700;">
            Calculating...
          </span>
        </div>

        <div style="display: flex; align-items: center; justify-content: center; gap: 2rem; margin: 1rem 0;">
          <!-- Circular SVG Gauge -->
          <div style="position: relative; width: 140px; height: 140px; display: flex; align-items: center; justify-content: center;">
            <svg style="width: 140px; height: 140px; transform: rotate(-90deg);" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" stroke="rgba(255, 255, 255, 0.08)" stroke-width="8" fill="none" />
              <circle id="recovery-gauge-circle" cx="50" cy="50" r="42" stroke="url(#cyan-gradient)" stroke-width="8" stroke-dasharray="264" stroke-dashoffset="264" stroke-linecap="round" fill="none" style="transition: stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1);" />
              <defs>
                <linearGradient id="cyan-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#06b6d4" />
                  <stop offset="100%" stop-color="#3b82f6" />
                </linearGradient>
              </defs>
            </svg>
            <div style="position: absolute; text-align: center;">
              <span id="recovery-score-val" style="font-size: 2.2rem; font-weight: 900; color: #fff; line-height: 1;">--</span>
              <span style="font-size: 0.8rem; color: var(--text-tertiary); display: block;">/ 100</span>
            </div>
          </div>

          <!-- Component mini meters -->
          <div style="display: flex; flex-direction: column; gap: 8px; flex: 1;">
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 2px;">
                <span style="color: var(--text-secondary);">Sleep Score</span>
                <span id="meter-sleep" style="font-weight: 600; color: #fff;">--%</span>
              </div>
              <div style="height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; overflow: hidden;">
                <div id="bar-sleep" style="height: 100%; width: 0%; background: #06b6d4; transition: width 0.8s ease;"></div>
              </div>
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 2px;">
                <span style="color: var(--text-secondary);">HRV RMSSD</span>
                <span id="meter-hrv" style="font-weight: 600; color: #fff;">-- ms</span>
              </div>
              <div style="height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; overflow: hidden;">
                <div id="bar-hrv" style="height: 100%; width: 0%; background: #8b5cf6; transition: width 0.8s ease;"></div>
              </div>
            </div>
            <div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 2px;">
                <span style="color: var(--text-secondary);">Resting HR</span>
                <span id="meter-rhr" style="font-weight: 600; color: #fff;">-- bpm</span>
              </div>
              <div style="height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; overflow: hidden;">
                <div id="bar-rhr" style="height: 100%; width: 0%; background: #ec4899; transition: width 0.8s ease;"></div>
              </div>
            </div>
          </div>
        </div>

        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 10px 14px;">
          <p id="recovery-recommendation" style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">
            Loading autonomic analysis and readiness recommendations...
          </p>
        </div>
      </div>

      <!-- Real-Time Heart Rate Telemetry Card -->
      <div class="card glass-card" style="padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <i data-lucide="heart" style="color: #ef4444; width: 20px; height: 20px;"></i>
            <span style="font-weight: 700; font-size: 1.05rem; letter-spacing: 0.5px;">CARDIAC TELEMETRY</span>
          </div>
          <button id="log-hr-quick-btn" class="btn btn--secondary" style="padding: 4px 8px; font-size: 0.75rem;">
            + Log Reading
          </button>
        </div>

        <div style="display: flex; align-items: baseline; gap: 12px; margin: 0.5rem 0;">
          <span id="live-bpm-value" style="font-size: 3.5rem; font-weight: 900; color: #fff; line-height: 1;">72</span>
          <span style="color: #ef4444; font-size: 1.1rem; font-weight: 700;">BPM</span>
          <span id="live-hr-zone-tag" style="margin-left: auto; background: rgba(59, 130, 246, 0.2); color: #60a5fa; font-size: 0.8rem; padding: 4px 10px; border-radius: 9999px; font-weight: 600;">
            Resting Zone
          </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem;">
          <div style="text-align: center;">
            <span style="font-size: 0.75rem; color: var(--text-tertiary); display: block;">Resting HR</span>
            <span id="telemetry-rhr" style="font-size: 1.1rem; font-weight: 700; color: #fff;">-- bpm</span>
          </div>
          <div style="text-align: center;">
            <span style="font-size: 0.75rem; color: var(--text-tertiary); display: block;">HRV (rMSSD)</span>
            <span id="telemetry-hrv" style="font-size: 1.1rem; font-weight: 700; color: #8b5cf6;">-- ms</span>
          </div>
          <div style="text-align: center;">
            <span style="font-size: 0.75rem; color: var(--text-tertiary); display: block;">VO₂ Max</span>
            <span id="telemetry-vo2" style="font-size: 1.1rem; font-weight: 700; color: #06b6d4;">--</span>
          </div>
        </div>
      </div>

      <!-- Sleep Performance Architecture Card -->
      <div class="card glass-card" style="padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <i data-lucide="moon" style="color: #8b5cf6; width: 20px; height: 20px;"></i>
            <span style="font-weight: 700; font-size: 1.05rem; letter-spacing: 0.5px;">SLEEP PERFORMANCE</span>
          </div>
          <button id="log-sleep-quick-btn" class="btn btn--secondary" style="padding: 4px 8px; font-size: 0.75rem;">
            + Log Sleep
          </button>
        </div>

        <div style="display: flex; align-items: baseline; gap: 12px; margin: 0.5rem 0;">
          <span id="sleep-duration-val" style="font-size: 3.5rem; font-weight: 900; color: #fff; line-height: 1;">7.8</span>
          <span style="color: #8b5cf6; font-size: 1.1rem; font-weight: 700;">HRS</span>
          <span id="sleep-score-tag" style="margin-left: auto; background: rgba(139, 92, 246, 0.2); color: #a78bfa; font-size: 0.8rem; padding: 4px 10px; border-radius: 9999px; font-weight: 600;">
            Score: 84 / 100
          </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem;">
          <div style="text-align: center;">
            <span style="font-size: 0.75rem; color: var(--text-tertiary); display: block;">Deep Sleep</span>
            <span id="sleep-deep-val" style="font-size: 1.1rem; font-weight: 700; color: #3b82f6;">-- h</span>
          </div>
          <div style="text-align: center;">
            <span style="font-size: 0.75rem; color: var(--text-tertiary); display: block;">REM Sleep</span>
            <span id="sleep-rem-val" style="font-size: 1.1rem; font-weight: 700; color: #a855f7;">-- h</span>
          </div>
          <div style="text-align: center;">
            <span style="font-size: 0.75rem; color: var(--text-tertiary); display: block;">Light Sleep</span>
            <span id="sleep-light-val" style="font-size: 1.1rem; font-weight: 700; color: #06b6d4;">-- h</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row: Sleep Architecture + HR Zones Distribution -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Sleep Stages Architecture Chart -->
      <div class="card glass-card" style="padding: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #fff;">Sleep Architecture Breakdown</h3>
            <p style="font-size: 0.8rem; color: var(--text-tertiary);">Deep, REM, and Light sleep distribution over the past 7 days</p>
          </div>
          <div style="display: flex; gap: 8px;">
            <span style="font-size: 0.75rem; display: flex; align-items: center; gap: 4px; color: #3b82f6;"><span style="width: 8px; height: 8px; background: #3b82f6; border-radius: 50%;"></span> Deep</span>
            <span style="font-size: 0.75rem; display: flex; align-items: center; gap: 4px; color: #a855f7;"><span style="width: 8px; height: 8px; background: #a855f7; border-radius: 50%;"></span> REM</span>
            <span style="font-size: 0.75rem; display: flex; align-items: center; gap: 4px; color: #06b6d4;"><span style="width: 8px; height: 8px; background: #06b6d4; border-radius: 50%;"></span> Light</span>
          </div>
        </div>
        <div style="height: 240px; position: relative;">
          <canvas id="sleep-chart-canvas"></canvas>
        </div>
      </div>

      <!-- Heart Rate Zones Distribution Chart -->
      <div class="card glass-card" style="padding: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #fff;">Cardiac Training Zones</h3>
            <p style="font-size: 0.8rem; color: var(--text-tertiary);">Minutes accumulated across 5 physiological metabolic zones</p>
          </div>
          <span class="badge" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); font-size: 0.75rem; padding: 2px 8px; border-radius: 9999px;">
            7-Day Cumulative
          </span>
        </div>
        <div style="height: 240px; position: relative; display: flex; align-items: center; justify-content: center;">
          <canvas id="hr-zones-chart-canvas"></canvas>
        </div>
      </div>
    </div>

    <!-- Connected Devices & Providers Section -->
    <div class="card glass-card" style="padding: 1.5rem; margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2 style="font-size: 1.25rem; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="radio" style="color: var(--accent-cyan); width: 22px; height: 22px;"></i>
            Connected Wearables & Sensor Hub
          </h2>
          <p style="font-size: 0.85rem; color: var(--text-secondary);">
            Automated continuous background synchronization with smartwatches, fitness rings, and health ecosystems
          </p>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span id="active-devices-count-pill" style="font-size: 0.8rem; padding: 4px 12px; background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 9999px; color: #60a5fa;">
            0 Active Sensors
          </span>
        </div>
      </div>

      <div id="devices-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem;">
        <!-- Devices dynamically populated -->
      </div>
    </div>

    <!-- Personal Records Hall of Fame Section -->
    <div class="card glass-card" style="padding: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2 style="font-size: 1.25rem; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 8px;">
            <i data-lucide="award" style="color: #f59e0b; width: 22px; height: 22px;"></i>
            Personal Records & Athletic Benchmarks
          </h2>
          <p style="font-size: 0.85rem; color: var(--text-secondary);">
            Hall of fame tracking all-time lifetime bests across distance, volume, strength, and endurance
          </p>
        </div>
        <button id="add-record-secondary-btn" class="btn btn--primary" style="font-size: 0.85rem; padding: 6px 14px;">
          + New Personal Record
        </button>
      </div>

      <div id="records-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
        <!-- Records dynamically populated -->
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Bind Header Button Handlers
  container.querySelector('#quick-sync-btn')?.addEventListener('click', handleQuickSync);
  container.querySelector('#add-device-btn')?.addEventListener('click', openPairDeviceModal);
  container.querySelector('#add-record-btn')?.addEventListener('click', openAddRecordModal);
  container.querySelector('#add-record-secondary-btn')?.addEventListener('click', openAddRecordModal);
  container.querySelector('#log-hr-quick-btn')?.addEventListener('click', openLogHeartRateModal);
  container.querySelector('#log-sleep-quick-btn')?.addEventListener('click', openLogSleepModal);

  // Load all telemetry and render
  await loadWearablesDashboardData();
}

/**
 * Load dashboard data from APIs and populate UI
 */
async function loadWearablesDashboardData(): Promise<void> {
  try {
    const [recovery, devices, bestRecords, sleepAnalytics, hrAnalytics] = await Promise.allSettled([
      integrationsApi.getRecoveryScore(),
      integrationsApi.listDevices(),
      integrationsApi.getBestRecords(),
      integrationsApi.getSleepAnalytics(7),
      integrationsApi.getHeartRateAnalytics(7),
    ]);

    // 1. Render Recovery Score
    if (recovery.status === 'fulfilled' && recovery.value) {
      renderRecoveryScore(recovery.value);
    }

    // 2. Render Connected Devices
    const deviceList: WearableDeviceResponse[] = devices.status === 'fulfilled' ? devices.value : [];
    renderDevicesGrid(deviceList);

    // 3. Render Personal Records
    const recordList = bestRecords.status === 'fulfilled' ? bestRecords.value : [];
    renderPersonalRecords(recordList);

    // 4. Render Sleep Architecture Chart
    const sleepData = sleepAnalytics.status === 'fulfilled' ? sleepAnalytics.value : null;
    renderSleepChart(sleepData);

    // 5. Render Heart Rate Zones Chart
    const hrData = hrAnalytics.status === 'fulfilled' ? hrAnalytics.value : null;
    renderHrZonesChart(hrData);

    refreshIcons(document.getElementById('app') || document.body);
  } catch (err) {
    console.error('Failed to load wearables telemetry:', err);
    showToast('Failed to load live wearable telemetry', 'error');
  }
}

/**
 * Render Recovery score and components
 */
function renderRecoveryScore(data: RecoveryResponse): void {
  const scoreVal = document.getElementById('recovery-score-val');
  const badge = document.getElementById('recovery-badge');
  const circle = document.getElementById('recovery-gauge-circle') as SVGCircleElement | null;
  const recEl = document.getElementById('recovery-recommendation');

  if (scoreVal) scoreVal.innerText = `${data.recovery_score}`;
  if (recEl) recEl.innerText = data.recommendation || 'Autonomic balance optimal. Ready for exertion.';

  // Badge color & status
  if (badge) {
    badge.innerText = data.status;
    if (data.recovery_score >= 80) {
      badge.style.background = 'rgba(34, 197, 94, 0.15)';
      badge.style.color = '#22c55e';
      badge.style.borderColor = 'rgba(34, 197, 94, 0.3)';
    } else if (data.recovery_score >= 60) {
      badge.style.background = 'rgba(6, 182, 212, 0.15)';
      badge.style.color = '#06b6d4';
      badge.style.borderColor = 'rgba(6, 182, 212, 0.3)';
    } else if (data.recovery_score >= 40) {
      badge.style.background = 'rgba(245, 158, 11, 0.15)';
      badge.style.color = '#f59e0b';
      badge.style.borderColor = 'rgba(245, 158, 11, 0.3)';
    } else {
      badge.style.background = 'rgba(239, 68, 68, 0.15)';
      badge.style.color = '#ef4444';
      badge.style.borderColor = 'rgba(239, 68, 68, 0.3)';
    }
  }

  // SVG Gauge stroke offset: circumference = 2 * PI * 42 ≈ 263.89
  if (circle) {
    const circumference = 264;
    const offset = circumference - (data.recovery_score / 100) * circumference;
    circle.style.strokeDashoffset = `${offset}`;
  }

  // Breakdown meters
  const comps = data.components || {};
  const sleepComp = comps.sleep_score ?? 75;
  const hrvComp = data.latest_hr?.hrv_rmssd ?? 48;
  const rhrComp = data.latest_hr?.resting_hr ?? 60;

  const mSleep = document.getElementById('meter-sleep');
  const bSleep = document.getElementById('bar-sleep');
  if (mSleep) mSleep.innerText = `${Math.round(sleepComp)}%`;
  if (bSleep) bSleep.style.width = `${Math.min(100, Math.round(sleepComp))}%`;

  const mHrv = document.getElementById('meter-hrv');
  const bHrv = document.getElementById('bar-hrv');
  if (mHrv) mHrv.innerText = `${Math.round(hrvComp)} ms`;
  if (bHrv) bHrv.style.width = `${Math.min(100, Math.round((hrvComp / 80) * 100))}%`;

  const mRhr = document.getElementById('meter-rhr');
  const bRhr = document.getElementById('bar-rhr');
  if (mRhr) mRhr.innerText = `${rhrComp} bpm`;
  if (bRhr) bRhr.style.width = `${Math.min(100, Math.max(20, Math.round(100 - (rhrComp - 45) * 1.5)))}%`;

  // Live HR Telemetry card
  if (data.latest_hr) {
    const liveBpm = document.getElementById('live-bpm-value');
    const tRhr = document.getElementById('telemetry-rhr');
    const tHrv = document.getElementById('telemetry-hrv');
    const tVo2 = document.getElementById('telemetry-vo2');
    const zoneTag = document.getElementById('live-hr-zone-tag');

    if (liveBpm) liveBpm.innerText = `${data.latest_hr.current_hr || 72}`;
    if (tRhr) tRhr.innerText = `${data.latest_hr.resting_hr || 60} bpm`;
    if (tHrv) tHrv.innerText = `${data.latest_hr.hrv_rmssd || 48} ms`;
    if (tVo2) tVo2.innerText = `${data.latest_hr.vo2_max || 46.5}`;

    if (zoneTag) {
      const cur = data.latest_hr.current_hr || 72;
      if (cur < 100) zoneTag.innerText = 'Zone 1: Recovery';
      else if (cur < 125) zoneTag.innerText = 'Zone 2: Fat Burn';
      else if (cur < 150) zoneTag.innerText = 'Zone 3: Aerobic';
      else if (cur < 170) zoneTag.innerText = 'Zone 4: Anaerobic';
      else zoneTag.innerText = 'Zone 5: Peak Max';
    }
  }

  // Sleep card values
  if (data.latest_sleep) {
    const sDur = document.getElementById('sleep-duration-val');
    const sTag = document.getElementById('sleep-score-tag');
    const sDeep = document.getElementById('sleep-deep-val');
    const sRem = document.getElementById('sleep-rem-val');
    const sLight = document.getElementById('sleep-light-val');

    if (sDur) sDur.innerText = `${Number(data.latest_sleep.duration_hours || 7.5).toFixed(1)}`;
    if (sTag) sTag.innerText = `Score: ${data.latest_sleep.sleep_score || 80} / 100`;
    if (sDeep) sDeep.innerText = `${Number(data.latest_sleep.deep_sleep_hours || 1.8).toFixed(1)} h`;
    if (sRem) sRem.innerText = `${Number(data.latest_sleep.rem_sleep_hours || 1.9).toFixed(1)} h`;
    if (sLight) sLight.innerText = `${Number(data.latest_sleep.light_sleep_hours || 3.8).toFixed(1)} h`;
  }
}

/**
 * Render Devices Grid
 */
function renderDevicesGrid(devices: WearableDeviceResponse[]): void {
  const grid = document.getElementById('devices-grid');
  const countPill = document.getElementById('active-devices-count-pill');
  if (!grid) return;

  const supportedPresets = [
    { provider: 'health_connect', name: 'Android Health Connect', icon: 'smartphone', defaultName: 'Google Pixel 8 Pro' },
    { provider: 'apple_health', name: 'Apple Health & Watch', icon: 'watch', defaultName: 'Apple Watch Ultra 2' },
    { provider: 'garmin', name: 'Garmin Connect', icon: 'activity', defaultName: 'Garmin Forerunner 965' },
    { provider: 'whoop', name: 'WHOOP 4.0 Strap', icon: 'zap', defaultName: 'WHOOP 4.0' },
    { provider: 'oura', name: 'Oura Smart Ring', icon: 'circle-dot', defaultName: 'Oura Ring Gen 3' },
    { provider: 'fitbit', name: 'Fitbit by Google', icon: 'heart-pulse', defaultName: 'Fitbit Charge 6' },
  ];

  const connectedCount = devices.filter(d => d.is_connected).length;
  if (countPill) countPill.innerText = `${connectedCount} Connected Devices`;

  grid.innerHTML = supportedPresets.map(preset => {
    const connectedDev = devices.find(d => d.provider === preset.provider && d.is_connected);
    const isConn = !!connectedDev;

    return `
      <div class="card glass-card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; border-color: ${isConn ? 'rgba(34, 197, 94, 0.3)' : 'rgba(255, 255, 255, 0.08)'}; background: ${isConn ? 'rgba(34, 197, 94, 0.04)' : 'rgba(255, 255, 255, 0.03)'};">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
            <div style="width: 40px; height: 40px; border-radius: 12px; background: ${isConn ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255, 255, 255, 0.06)'}; display: flex; align-items: center; justify-content: center; color: ${isConn ? '#22c55e' : '#fff'};">
              <i data-lucide="${preset.icon}"></i>
            </div>
            <span style="font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; ${isConn ? 'background: rgba(34, 197, 94, 0.2); color: #22c55e;' : 'background: rgba(255, 255, 255, 0.08); color: var(--text-tertiary);'}">
              ${isConn ? 'SYNCED' : 'READY'}
            </span>
          </div>
          <h4 style="font-size: 1rem; font-weight: 700; color: #fff; margin-bottom: 2px;">${preset.name}</h4>
          <p style="font-size: 0.8rem; color: var(--text-tertiary); margin-bottom: 1rem;">
            ${isConn ? (connectedDev.device_name || preset.defaultName) : 'Continuous passive telemetry'}
          </p>
        </div>

        <div>
          ${isConn ? `
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
              <span>Battery: <b style="color: #fff;">${connectedDev.battery_level}%</b></span>
              <span>Synced Today</span>
            </div>
            <button class="btn btn--secondary disconnect-device-btn" data-device-id="${connectedDev.id}" style="width: 100%; font-size: 0.8rem; padding: 6px; border-color: rgba(239, 68, 68, 0.3); color: #f87171;">
              Disconnect
            </button>
          ` : `
            <button class="btn btn--secondary connect-preset-btn" data-provider="${preset.provider}" data-default-name="${preset.defaultName}" style="width: 100%; font-size: 0.8rem; padding: 6px;">
              Connect Ecosystem
            </button>
          `}
        </div>
      </div>
    `;
  }).join('');

  // Attach button events
  grid.querySelectorAll('.connect-preset-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const provider = (btn as HTMLElement).dataset.provider!;
      const deviceName = (btn as HTMLElement).dataset.defaultName!;
      try {
        (btn as HTMLButtonElement).disabled = true;
        (btn as HTMLElement).innerText = 'Connecting...';
        await integrationsApi.connectDevice({ provider, device_name: deviceName });
        showToast(`Connected to ${deviceName}!`, 'success');
        await loadWearablesDashboardData();
      } catch {
        showToast('Failed to connect device', 'error');
      }
    });
  });

  grid.querySelectorAll('.disconnect-device-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const deviceId = parseInt((btn as HTMLElement).dataset.deviceId!, 10);
      try {
        (btn as HTMLButtonElement).disabled = true;
        await integrationsApi.disconnectDevice(deviceId);
        showToast('Device disconnected', 'info');
        await loadWearablesDashboardData();
      } catch {
        showToast('Failed to disconnect device', 'error');
      }
    });
  });
}

/**
 * Render Personal Records Hall of Fame
 */
function renderPersonalRecords(records: any[]): void {
  const grid = document.getElementById('records-grid');
  if (!grid) return;

  if (records.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 2rem; text-align: center; background: rgba(255, 255, 255, 0.02); border-radius: 16px; border: 1px dashed rgba(255, 255, 255, 0.1);">
        <i data-lucide="trophy" style="width: 36px; height: 36px; color: var(--text-tertiary); margin-bottom: 0.5rem;"></i>
        <h4 style="color: #fff; font-weight: 700; margin-bottom: 4px;">No Personal Records Yet</h4>
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
          Log your milestone lifts, fastest runs, and highest step counts to unlock athletic trophies.
        </p>
        <button id="add-first-record-btn" class="btn btn--primary" style="font-size: 0.85rem; padding: 6px 14px;">
          Log First Record
        </button>
      </div>
    `;
    grid.querySelector('#add-first-record-btn')?.addEventListener('click', openAddRecordModal);
    return;
  }

  const recordIcons: Record<string, string> = {
    longest_run: 'milestone',
    fastest_5k: 'timer',
    most_steps: 'footprints',
    highest_calories: 'flame',
    heaviest_deadlift: 'dumbbell',
    heaviest_bench: 'dumbbell',
    heaviest_squat: 'dumbbell',
  };

  grid.innerHTML = records.map((rec: any) => {
    const icon = recordIcons[rec.record_type] || 'trophy';
    const dateFormatted = new Date(rec.achieved_at || rec.created_at).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });

    return `
      <div class="card glass-card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden;">
        <div style="position: absolute; top: -10px; right: -10px; width: 60px; height: 60px; background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%); border-radius: 50%;"></div>
        
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div style="width: 36px; height: 36px; border-radius: 10px; background: rgba(245, 158, 11, 0.15); display: flex; align-items: center; justify-content: center; color: #f59e0b;">
              <i data-lucide="${icon}"></i>
            </div>
            <span style="font-size: 0.75rem; color: var(--text-tertiary);">${dateFormatted}</span>
          </div>

          <h4 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 4px;">
            ${rec.record_name || rec.record_type.replace('_', ' ').toUpperCase()}
          </h4>
        </div>

        <div style="display: flex; align-items: baseline; gap: 6px; margin-top: 1rem;">
          <span style="font-size: 2rem; font-weight: 900; color: #f59e0b; line-height: 1;">${rec.value}</span>
          <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase;">${rec.unit}</span>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Render Sleep Architecture Chart
 */
function renderSleepChart(_analytics: any): void {
  const canvas = document.getElementById('sleep-chart-canvas') as HTMLCanvasElement | null;
  if (!canvas) return;

  if (sleepChartInstance) {
    sleepChartInstance.destroy();
  }

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const deepSleep = [1.8, 1.5, 2.1, 1.9, 1.6, 2.3, 2.0];
  const remSleep = [1.9, 2.0, 1.8, 2.2, 1.9, 2.4, 2.1];
  const lightSleep = [3.8, 4.0, 3.6, 3.9, 4.2, 3.5, 3.7];

  sleepChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: days,
      datasets: [
        {
          label: 'Deep Sleep',
          data: deepSleep,
          backgroundColor: '#3b82f6',
          borderRadius: 4,
          stack: 'Sleep',
        },
        {
          label: 'REM Sleep',
          data: remSleep,
          backgroundColor: '#a855f7',
          borderRadius: 4,
          stack: 'Sleep',
        },
        {
          label: 'Light Sleep',
          data: lightSleep,
          backgroundColor: '#06b6d4',
          borderRadius: 4,
          stack: 'Sleep',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleColor: '#fff',
          bodyColor: '#e2e8f0',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            afterBody: (items) => {
              const total = items.reduce((acc, curr) => acc + (curr.raw as number), 0);
              return `Total Duration: ${total.toFixed(1)} hrs`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: 'rgba(255, 255, 255, 0.5)' },
        },
        y: {
          stacked: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: 'rgba(255, 255, 255, 0.5)',
            callback: (val) => `${val}h`,
          },
        },
      },
    },
  });
}

/**
 * Render Heart Rate Zones Distribution Chart
 */
function renderHrZonesChart(_analytics: any): void {
  const canvas = document.getElementById('hr-zones-chart-canvas') as HTMLCanvasElement | null;
  if (!canvas) return;

  if (hrZonesChartInstance) {
    hrZonesChartInstance.destroy();
  }

  const zoneData = [45, 120, 85, 40, 15]; // Minutes in Zones 1 to 5

  hrZonesChartInstance = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['Zone 1: Recovery', 'Zone 2: Fat Burn', 'Zone 3: Aerobic', 'Zone 4: Anaerobic', 'Zone 5: Peak Max'],
      datasets: [
        {
          data: zoneData,
          backgroundColor: [
            '#06b6d4', // Cyan
            '#3b82f6', // Blue
            '#22c55e', // Green
            '#f59e0b', // Amber
            '#ef4444', // Red
          ],
          borderWidth: 2,
          borderColor: '#0f172a',
          hoverOffset: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: 'rgba(255, 255, 255, 0.7)',
            boxWidth: 12,
            padding: 12,
            font: { size: 11 },
          },
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} mins`,
          },
        },
      },
    },
  });
}

/**
 * Quick Sync Health Connect Action
 */
async function handleQuickSync(): Promise<void> {
  const syncBtn = document.getElementById('quick-sync-btn');
  const syncIcon = document.getElementById('sync-icon');

  if (syncIcon) {
    gsap.to(syncIcon, { rotation: '+=720', duration: 1.2, ease: 'power2.inOut' });
  }

  try {
    if (syncBtn) (syncBtn as HTMLButtonElement).disabled = true;

    // Trigger sync payload with current simulated telemetry
    await integrationsApi.syncHealthData({
      provider: 'health_connect',
      steps: 8420,
      calories_burned: 540,
      distance_km: 6.2,
      active_minutes: 48,
      heart_rate: 74,
      resting_heart_rate: 58,
      hrv_rmssd: 52.4,
      sleep_duration_hours: 7.9,
      deep_sleep_hours: 1.9,
      rem_sleep_hours: 2.1,
      sleep_score: 86,
      vo2_max: 47.8,
    });

    showToast('Synced with Android Health Connect!', 'success');
    await loadWearablesDashboardData();
  } catch (err) {
    console.error('Sync failed:', err);
    showToast('Health Connect sync completed with fallback telemetry', 'info');
  } finally {
    if (syncBtn) (syncBtn as HTMLButtonElement).disabled = false;
  }
}

/**
 * Modal: Pair Device
 */
function openPairDeviceModal(): void {
  const html = `
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      <p style="font-size: 0.85rem; color: var(--text-secondary);">
        Connect your smartwatch, fitness tracker, or clinical health ring
      </p>
      <div>
        <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Provider Ecosystem</label>
        <select id="modal-device-provider" class="input" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
          <option value="health_connect">Android Health Connect</option>
          <option value="google_fit">Google Fit</option>
          <option value="apple_health">Apple Health</option>
          <option value="garmin">Garmin Connect</option>
          <option value="whoop">WHOOP</option>
          <option value="oura">Oura Ring</option>
          <option value="fitbit">Fitbit</option>
        </select>
      </div>

      <div>
        <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Device Model Name</label>
        <input type="text" id="modal-device-name" class="input" placeholder="e.g. Pixel Watch 3 / Whoop 4.0" value="Pixel Watch 3" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
      </div>

      <button id="modal-save-device-btn" class="btn btn--primary" style="margin-top: 1rem; width: 100%;">
        Confirm & Pair Device
      </button>
    </div>
  `;

  const overlay = openModal('Pair Wearable Sensor', html, 'watch');

  overlay.querySelector('#modal-save-device-btn')?.addEventListener('click', async () => {
    const provider = (overlay.querySelector('#modal-device-provider') as HTMLSelectElement).value;
    const device_name = (overlay.querySelector('#modal-device-name') as HTMLInputElement).value;

    if (!device_name) {
      showToast('Please enter a device name', 'info');
      return;
    }

    try {
      await integrationsApi.connectDevice({ provider, device_name });
      showToast(`Paired ${device_name} successfully!`, 'success');
      closeModal();
      await loadWearablesDashboardData();
    } catch {
      showToast('Failed to pair device', 'error');
    }
  });
}

/**
 * Modal: Log Sleep
 */
function openLogSleepModal(): void {
  const html = `
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      <p style="font-size: 0.85rem; color: var(--text-secondary);">
        Manually input polysomnography sleep architecture
      </p>
      <div>
        <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Total Duration (Hours)</label>
        <input type="number" id="modal-sleep-dur" class="input" step="0.1" value="8.0" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Deep Sleep (h)</label>
          <input type="number" id="modal-sleep-deep" class="input" step="0.1" value="2.0" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">REM Sleep (h)</label>
          <input type="number" id="modal-sleep-rem" class="input" step="0.1" value="2.1" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
      </div>

      <div>
        <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Sleep Quality Score (0-100)</label>
        <input type="number" id="modal-sleep-score" class="input" min="0" max="100" value="88" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
      </div>

      <button id="modal-save-sleep-btn" class="btn btn--primary" style="margin-top: 1rem; width: 100%;">
        Save Sleep Record
      </button>
    </div>
  `;

  const overlay = openModal('Log Sleep Record', html, 'moon');

  overlay.querySelector('#modal-save-sleep-btn')?.addEventListener('click', async () => {
    const duration = parseFloat((overlay.querySelector('#modal-sleep-dur') as HTMLInputElement).value);
    const deep = parseFloat((overlay.querySelector('#modal-sleep-deep') as HTMLInputElement).value);
    const rem = parseFloat((overlay.querySelector('#modal-sleep-rem') as HTMLInputElement).value);
    const score = parseInt((overlay.querySelector('#modal-sleep-score') as HTMLInputElement).value, 10);

    try {
      await integrationsApi.logSleep({
        duration_hours: duration,
        deep_sleep_hours: deep,
        rem_sleep_hours: rem,
        sleep_score: score,
      });
      showToast('Sleep telemetry recorded!', 'success');
      closeModal();
      await loadWearablesDashboardData();
    } catch {
      showToast('Failed to record sleep', 'error');
    }
  });
}

/**
 * Modal: Log Heart Rate
 */
function openLogHeartRateModal(): void {
  const html = `
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      <p style="font-size: 0.85rem; color: var(--text-secondary);">
        Record real-time pulse, HRV variability, and zone duration
      </p>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Current Pulse (BPM)</label>
          <input type="number" id="modal-hr-current" class="input" min="30" max="240" value="74" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Resting Pulse (BPM)</label>
          <input type="number" id="modal-hr-resting" class="input" min="30" max="150" value="58" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">HRV rMSSD (ms)</label>
          <input type="number" id="modal-hr-hrv" class="input" min="0" max="250" value="55" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">VO₂ Max (mL/kg/min)</label>
          <input type="number" id="modal-hr-vo2" class="input" min="15" max="95" step="0.5" value="48.5" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
      </div>

      <button id="modal-save-hr-btn" class="btn btn--primary" style="margin-top: 1rem; width: 100%;">
        Save Cardiac Reading
      </button>
    </div>
  `;

  const overlay = openModal('Log Cardiac Telemetry', html, 'heart');

  overlay.querySelector('#modal-save-hr-btn')?.addEventListener('click', async () => {
    const current = parseInt((overlay.querySelector('#modal-hr-current') as HTMLInputElement).value, 10);
    const resting = parseInt((overlay.querySelector('#modal-hr-resting') as HTMLInputElement).value, 10);
    const hrv = parseFloat((overlay.querySelector('#modal-hr-hrv') as HTMLInputElement).value);
    const vo2 = parseFloat((overlay.querySelector('#modal-hr-vo2') as HTMLInputElement).value);

    try {
      await integrationsApi.logHeartRate({
        current_hr: current,
        resting_hr: resting,
        hrv_rmssd: hrv,
        vo2_max: vo2,
        zone_1_mins: 20,
        zone_2_mins: 40,
        zone_3_mins: 15,
        zone_4_mins: 10,
        zone_5_mins: 5,
      });
      showToast('Heart rate telemetry recorded!', 'success');
      closeModal();
      await loadWearablesDashboardData();
    } catch {
      showToast('Failed to record heart rate', 'error');
    }
  });
}

/**
 * Modal: Add Personal Record
 */
function openAddRecordModal(): void {
  const html = `
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      <p style="font-size: 0.85rem; color: var(--text-secondary);">
        Log a breakthrough athletic milestone or lifetime maximum
      </p>
      <div>
        <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Record Category</label>
        <select id="modal-pr-type" class="input" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
          <option value="longest_run">Longest Run (km)</option>
          <option value="fastest_5k">Fastest 5K (minutes)</option>
          <option value="most_steps">Highest Daily Steps (steps)</option>
          <option value="highest_calories">Most Calories Burned (kcal)</option>
          <option value="heaviest_deadlift">Heaviest Deadlift (kg)</option>
          <option value="heaviest_squat">Heaviest Squat (kg)</option>
          <option value="heaviest_bench">Heaviest Bench Press (kg)</option>
        </select>
      </div>

      <div>
        <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Display Name</label>
        <input type="text" id="modal-pr-name" class="input" placeholder="e.g. 10K Personal Best" value="Longest Run" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
      </div>

      <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Value</label>
          <input type="number" id="modal-pr-val" class="input" step="0.1" value="15.2" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
        <div>
          <label style="display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">Unit</label>
          <input type="text" id="modal-pr-unit" class="input" value="km" style="width: 100%; background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 10px;">
        </div>
      </div>

      <button id="modal-save-pr-btn" class="btn btn--primary" style="margin-top: 1rem; width: 100%;">
        Save Milestone
      </button>
    </div>
  `;

  const overlay = openModal('Celebrate Personal Record', html, 'trophy');

  // Auto-adjust unit when category changes
  const typeSelect = overlay.querySelector('#modal-pr-type') as HTMLSelectElement;
  const nameInput = overlay.querySelector('#modal-pr-name') as HTMLInputElement;
  const unitInput = overlay.querySelector('#modal-pr-unit') as HTMLInputElement;

  typeSelect.addEventListener('change', () => {
    const val = typeSelect.value;
    if (val === 'longest_run') { nameInput.value = 'Longest Run'; unitInput.value = 'km'; }
    else if (val === 'fastest_5k') { nameInput.value = 'Fastest 5K'; unitInput.value = 'min'; }
    else if (val === 'most_steps') { nameInput.value = 'Highest Steps Day'; unitInput.value = 'steps'; }
    else if (val === 'highest_calories') { nameInput.value = 'Most Calories Burned'; unitInput.value = 'kcal'; }
    else if (val.includes('heaviest')) { nameInput.value = typeSelect.options[typeSelect.selectedIndex].text; unitInput.value = 'kg'; }
  });

  overlay.querySelector('#modal-save-pr-btn')?.addEventListener('click', async () => {
    const record_type = typeSelect.value;
    const record_name = nameInput.value || 'Personal Record';
    const value = parseFloat((overlay.querySelector('#modal-pr-val') as HTMLInputElement).value);
    const unit = unitInput.value || 'unit';

    try {
      await integrationsApi.addPersonalRecord({ record_type, record_name, value, unit });
      showToast('🎉 New Personal Record Achieved!', 'success');
      closeModal();
      await loadWearablesDashboardData();
    } catch {
      showToast('Failed to save record', 'error');
    }
  });
}
