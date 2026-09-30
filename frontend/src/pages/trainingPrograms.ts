// ============================================================
// FitAI – AI Training Programs Page
// Phase 8: Multi-week periodized programs, daily exercise routines,
// adaptive progression, and workout completion
// ============================================================
import { trainingApi } from '../api/training';
import type { TrainingProgramResponse, ProgramDayResponse } from '../types';
import { renderNavbar } from '../components/navbar';
import { refreshIcons } from '../utils/icons';

export async function renderTrainingProgramsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/training-programs'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          Adaptive <span class="navbar__logo-gradient">Training Programs</span>
        </h1>
        <p class="page-header__subtitle">
          AI-designed periodized training schedules tailored to your goals and recovery state
        </p>
      </div>
      <button id="btn-open-generator" class="btn btn-primary" style="display: flex; align-items: center; gap: 0.5rem;">
        <i data-lucide="sparkles" style="width: 18px; height: 18px;"></i>
        <span>Generate New Program</span>
      </button>
    </div>

    <!-- Generator Modal Container -->
    <div id="generator-modal" class="modal-backdrop" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(8px); z-index: 9999; align-items: center; justify-content: center; padding: 1rem;">
      <div class="card glass-card" style="max-width: 520px; width: 100%; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h3 style="font-size: 1.3rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <i data-lucide="cpu" style="width: 22px; height: 22px; color: var(--accent);"></i>
            <span>AI Program Architect</span>
          </h3>
          <button id="btn-close-modal" style="background: none; border: none; color: var(--text-secondary); cursor: pointer; padding: 0.25rem;">
            <i data-lucide="x" style="width: 20px; height: 20px;"></i>
          </button>
        </div>

        <form id="program-generator-form">
          <div style="margin-bottom: 1.25rem;">
            <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-secondary);">Fitness Goal</label>
            <select id="gen-goal" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);">
              <option value="muscle_building">Hypertrophy & Muscle Building</option>
              <option value="strength">Maximum Strength & Power</option>
              <option value="fat_loss">Fat Loss & Conditioning</option>
              <option value="general_fitness">General Health & Longevity</option>
              <option value="endurance">Cardiovascular Endurance</option>
            </select>
          </div>

          <div style="margin-bottom: 1.25rem;">
            <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-secondary);">Experience Level</label>
            <select id="gen-level" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);">
              <option value="beginner">Beginner (0-1 years)</option>
              <option value="intermediate" selected>Intermediate (1-3 years)</option>
              <option value="advanced">Advanced (3+ years)</option>
            </select>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-secondary);">Duration (Weeks)</label>
              <input type="number" id="gen-weeks" value="4" min="1" max="12" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
            <div>
              <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-secondary);">Days / Week</label>
              <input type="number" id="gen-days" value="4" min="2" max="6" class="input-field" style="width: 100%; padding: 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1);" />
            </div>
          </div>

          <button type="submit" id="btn-submit-generate" class="btn btn-primary" style="width: 100%; padding: 0.85rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            <i data-lucide="zap" style="width: 18px; height: 18px;"></i>
            <span>Synthesize AI Routine</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Active Program Display -->
    <div id="program-content">
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <div class="spinner" style="margin: 0 auto 1rem;"></div>
        <p style="color: var(--text-secondary);">Loading your AI training program...</p>
      </div>
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons();

  // Setup modal handlers
  const modal = container.querySelector('#generator-modal') as HTMLElement;
  const btnOpen = container.querySelector('#btn-open-generator') as HTMLButtonElement;
  const btnClose = container.querySelector('#btn-close-modal') as HTMLButtonElement;
  const genForm = container.querySelector('#program-generator-form') as HTMLFormElement;

  btnOpen.addEventListener('click', () => {
    modal.style.display = 'flex';
    refreshIcons();
  });

  btnClose.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
  });

  genForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = genForm.querySelector('#btn-submit-generate') as HTMLButtonElement;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner" style="width: 18px; height: 18px; border-width: 2px;"></div> Generating Periodization...';

    try {
      const fitness_goal = (genForm.querySelector('#gen-goal') as HTMLSelectElement).value;
      const fitness_level = (genForm.querySelector('#gen-level') as HTMLSelectElement).value;
      const duration_weeks = parseInt((genForm.querySelector('#gen-weeks') as HTMLInputElement).value, 10);
      const days_per_week = parseInt((genForm.querySelector('#gen-days') as HTMLInputElement).value, 10);

      await trainingApi.generateProgram({
        fitness_goal,
        fitness_level,
        duration_weeks,
        days_per_week,
      });

      modal.style.display = 'none';
      await loadProgram(container);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to generate program. Please try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i data-lucide="zap" style="width: 18px; height: 18px;"></i><span>Synthesize AI Routine</span>';
      refreshIcons();
    }
  });

  await loadProgram(container);
}

async function loadProgram(container: HTMLElement): Promise<void> {
  const content = container.querySelector('#program-content');
  if (!content) return;

  try {
    const activeProg = await trainingApi.getActiveProgram();
    if (!activeProg) {
      content.innerHTML = `
        <div class="card glass-card" style="padding: 4rem 2rem; text-align: center; max-width: 600px; margin: 2rem auto;">
          <div style="width: 70px; height: 70px; border-radius: 50%; background: rgba(59, 130, 246, 0.15); display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; color: var(--accent);">
            <i data-lucide="dumbbell" style="width: 36px; height: 36px;"></i>
          </div>
          <h2 style="font-size: 1.6rem; font-weight: 700; margin-bottom: 0.75rem;">No Active Training Program</h2>
          <p style="color: var(--text-secondary); margin-bottom: 2rem; line-height: 1.6;">
            Unlock progressive overload and sports science periodization. Generate your personalized AI training cycle today.
          </p>
          <button id="btn-create-first" class="btn btn-primary" style="padding: 0.85rem 2rem; font-size: 1rem;">
            Generate My First Program
          </button>
        </div>
      `;
      refreshIcons();
      content.querySelector('#btn-create-first')?.addEventListener('click', () => {
        const modal = container.querySelector('#generator-modal') as HTMLElement;
        if (modal) modal.style.display = 'flex';
        refreshIcons();
      });
      return;
    }

    renderActiveProgram(content, activeProg);
  } catch (err) {
    content.innerHTML = `
      <div class="card glass-card" style="padding: 3rem; text-align: center;">
        <p style="color: var(--danger);">Failed to load active program.</p>
      </div>
    `;
  }
}

function renderActiveProgram(container: Element, program: TrainingProgramResponse): void {
  let activeWeekIdx = 0;

  function renderView() {
    const totalDays = program.weeks.reduce((acc, w) => acc + w.days.length, 0);
    const completedDays = program.weeks.reduce(
      (acc, w) => acc + w.days.filter((d) => d.completed).length,
      0
    );
    const progressPct = totalDays > 0 ? Math.round((completedDays / totalDays) * 100) : 0;
    const currentWeek = program.weeks[activeWeekIdx] || program.weeks[0];

    container.innerHTML = `
      <!-- Program Overview Banner -->
      <div class="card glass-card" style="margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(255, 255, 255, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.5rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
              <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Active Cycle</span>
              <span style="font-size: 0.85rem; color: var(--text-secondary);">${program.fitness_goal.replace('_', ' ').toUpperCase()} • ${program.fitness_level.toUpperCase()}</span>
            </div>
            <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -0.02em;">${program.title}</h2>
            <p style="color: var(--text-secondary); max-width: 600px; font-size: 0.95rem; line-height: 1.5;">${program.description || 'Customized AI periodization plan with progressive overload tracking.'}</p>
          </div>

          <div style="min-width: 220px; background: rgba(255,255,255,0.03); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem;">
              <span style="color: var(--text-secondary);">Cycle Progress</span>
              <span style="font-weight: 700; color: var(--accent);">${progressPct}%</span>
            </div>
            <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 9999px; overflow: hidden; margin-bottom: 0.75rem;">
              <div style="height: 100%; width: ${progressPct}%; background: linear-gradient(90deg, var(--accent), #38BDF8); border-radius: 9999px; transition: width 0.6s ease;"></div>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); display: flex; justify-content: space-between;">
              <span>${completedDays} / ${totalDays} Sessions</span>
              <span>${program.duration_weeks} Weeks</span>
            </div>
          </div>
        </div>

        <!-- Periodization Weeks Navigator -->
        <div style="display: flex; gap: 0.75rem; overflow-x: auto; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 1.5rem;">
          ${program.weeks
            .map(
              (w, idx) => `
            <button class="week-tab-btn" data-week-idx="${idx}" style="flex: 1; min-width: 130px; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid ${
                idx === activeWeekIdx ? 'var(--accent)' : 'rgba(255,255,255,0.08)'
              }; background: ${
                idx === activeWeekIdx ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255,255,255,0.02)'
              }; color: ${
                idx === activeWeekIdx ? '#fff' : 'var(--text-secondary)'
              }; cursor: pointer; text-align: left; transition: all 0.2s;">
              <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Week ${w.week_number}</div>
              <div style="font-size: 0.95rem; font-weight: 700; margin: 0.2rem 0; color: #fff;">${w.theme || 'Progressive'}</div>
              <div style="font-size: 0.75rem; opacity: 0.8;">Intensity: ${w.intensity_pct}%</div>
            </button>
          `
            )
            .join('')}
        </div>
      </div>

      <!-- Current Week Sessions -->
      <div style="margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
        <h3 style="font-size: 1.3rem; font-weight: 700; margin: 0;">
          Week ${currentWeek.week_number} Routines <span style="font-size: 0.9rem; color: var(--text-secondary); font-weight: 400;">(${currentWeek.days.length} workouts scheduled)</span>
        </h3>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
        ${currentWeek.days.map((day) => renderDayCard(day)).join('')}
      </div>
    `;

    refreshIcons();

    // Attach week tabs
    container.querySelectorAll('.week-tab-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const target = (e.currentTarget as HTMLElement).getAttribute('data-week-idx');
        if (target !== null) {
          activeWeekIdx = parseInt(target, 10);
          renderView();
        }
      });
    });

    // Attach complete session buttons
    container.querySelectorAll('.btn-complete-day').forEach((btn) => {
      btn.addEventListener('click', async (e) => {
        const targetBtn = e.currentTarget as HTMLButtonElement;
        const dayId = parseInt(targetBtn.getAttribute('data-day-id') || '0', 10);
        if (!dayId) return;

        targetBtn.disabled = true;
        targetBtn.innerHTML = '<div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>';

        try {
          await trainingApi.completeDay(dayId);
          // Update in-memory state
          for (const w of program.weeks) {
            for (const d of w.days) {
              if (d.id === dayId) {
                d.completed = true;
                d.completed_at = new Date().toISOString();
              }
            }
          }
          renderView();
        } catch {
          alert('Could not mark session complete.');
          targetBtn.disabled = false;
          targetBtn.textContent = 'Mark Completed';
        }
      });
    });
  }

  renderView();
}

function renderDayCard(day: ProgramDayResponse): string {
  const isDone = day.completed;
  return `
    <div class="card glass-card" style="padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between; border-left: 4px solid ${
      isDone ? '#10B981' : 'var(--accent)'
    };">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <span style="font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase;">Day ${day.day_number}</span>
          ${
            isDone
              ? '<span class="badge" style="background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.3); font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 9999px;">✓ Completed</span>'
              : `<span style="font-size: 0.8rem; color: var(--text-secondary); display: flex; align-items: center; gap: 0.25rem;"><i data-lucide="clock" style="width: 14px; height: 14px;"></i> ~${day.estimated_duration_min}m</span>`
          }
        </div>

        <h4 style="font-size: 1.2rem; font-weight: 700; margin: 0 0 0.5rem 0;">${day.day_name}</h4>
        <div style="font-size: 0.85rem; color: var(--accent); font-weight: 600; margin-bottom: 1.25rem;">Focus: ${day.focus}</div>

        <!-- Exercises List -->
        <div style="margin-bottom: 1.25rem;">
          <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem;">Core Exercises (${day.exercises.length})</div>
          <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            ${day.exercises
              .map(
                (ex) => `
              <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px; font-size: 0.85rem;">
                <span style="font-weight: 600;">${ex.name}</span>
                <span style="color: var(--text-secondary); font-size: 0.8rem;">${ex.sets} × ${ex.reps} (${ex.rest_seconds}s)</span>
              </div>
            `
              )
              .join('')}
          </div>
        </div>
      </div>

      <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 1rem;">
        ${
          isDone
            ? `<div style="text-align: center; font-size: 0.85rem; color: #10B981; font-weight: 600;">Workout Finished</div>`
            : `<button class="btn btn-primary btn-complete-day" data-day-id="${day.id}" style="width: 100%; padding: 0.65rem; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                <i data-lucide="check" style="width: 16px; height: 16px;"></i>
                <span>Complete Workout Session</span>
              </button>`
        }
      </div>
    </div>
  `;
}
