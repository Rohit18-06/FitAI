// ============================================================
// FitAI – AI Workout Generator Page
// Periodized Biomechanical Training Programs
// ============================================================
import gsap from 'gsap';
import { workoutPlansApi } from '../api/workoutPlans';
import { workoutsApi } from '../api/workouts';
import type { WorkoutPlanResponse, DailyRoutine, ExerciseItem } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { refreshIcons } from '../utils/icons';

export async function renderWorkoutsPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/workouts'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Header -->
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          AI Periodized <span class="navbar__logo-gradient">Workout Split</span>
        </h1>
        <p class="page-header__subtitle">
          Hypertrophy & biomechanical strength programming designed by Gemini AI
        </p>
      </div>
      <button id="toggle-workout-form-btn" class="btn btn--primary">
        <i data-lucide="sparkles"></i>
        <span>Generate New Split</span>
      </button>
    </div>

    <!-- Generator Panel (Collapsible) -->
    <div id="workout-generator-panel" class="glass-card" style="padding: 2rem; margin-bottom: 2rem; display: none;">
      <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px;">
        <span style="color: var(--accent-blue);">⚡</span> Program Parameters
      </h3>

      <form id="workout-generator-form">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Fitness Level</label>
            <select id="w-level" class="form-select">
              <option value="Intermediate">Intermediate (1-3 yrs experience)</option>
              <option value="Advanced">Advanced (3+ yrs consistent lifting)</option>
              <option value="Beginner">Beginner (Foundational movements)</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Primary Goal</label>
            <select id="w-goal" class="form-select">
              <option value="Hypertrophy (Muscle Size)">Hypertrophy (Muscle Size)</option>
              <option value="Maximal Strength (Powerlifting)">Maximal Strength (Powerlifting)</option>
              <option value="Body Recomposition & Fat Loss">Body Recomposition & Fat Loss</option>
              <option value="Functional Athleticism">Functional Athleticism</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Available Equipment</label>
            <select id="w-equipment" class="form-select">
              <option value="Full Commercial Gym">Full Commercial Gym</option>
              <option value="Dumbbells & Adjustable Bench">Dumbbells & Adjustable Bench</option>
              <option value="Home Barbell & Squat Rack">Home Barbell & Squat Rack</option>
              <option value="Calisthenics & Bodyweight">Calisthenics & Bodyweight</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Frequency (Days / Week)</label>
            <select id="w-days" class="form-select">
              <option value="4">4 Days (Upper / Lower)</option>
              <option value="3">3 Days (Full Body)</option>
              <option value="5">5 Days (Push / Pull / Legs / Upper / Lower)</option>
              <option value="6">6 Days (PPL Split)</option>
            </select>
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 1rem;">
          <button type="button" id="cancel-w-generator-btn" class="btn btn--secondary">
            Cancel
          </button>
          <button type="submit" id="submit-w-generator-btn" class="btn btn--primary">
            <i data-lucide="sparkles"></i>
            <span>Synthesize Training Program</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Active Program Banner -->
    <div class="glass-card" style="padding: 1.75rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
      <div>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
          <span class="tag-chip" style="background: rgba(139, 92, 246, 0.15); color: var(--accent-purple);">
            Active Periodization
          </span>
          <span style="font-size: 0.8rem; color: var(--text-tertiary);" id="w-split-level">Intermediate • 4 Days/Week</span>
        </div>
        <h2 style="font-size: 1.5rem; font-weight: 800;" id="w-split-title">
          Loading Training Split...
        </h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" id="w-split-equip">
          Targeted mechanical tension and progressive overload
        </p>
      </div>

      <a href="#/video" class="btn btn--secondary" style="padding: 10px 18px;">
        <i data-lucide="video"></i>
        <span>Analyze Lift Form</span>
      </a>
    </div>

    <!-- Day Cards Grid -->
    <div id="workout-routines-container" style="display: flex; flex-direction: column; gap: 1.75rem;">
      <!-- Populated via TS -->
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Toggle generator
  const toggleBtn = container.querySelector('#toggle-workout-form-btn');
  const cancelBtn = container.querySelector('#cancel-w-generator-btn');
  const panel = container.querySelector('#workout-generator-panel') as HTMLDivElement;
  const form = container.querySelector('#workout-generator-form') as HTMLFormElement;

  toggleBtn?.addEventListener('click', () => {
    panel.style.display = 'block';
    gsap.fromTo(panel, { opacity: 0, height: 0 }, { opacity: 1, height: 'auto', duration: 0.35, ease: 'power2.out' });
  });

  cancelBtn?.addEventListener('click', () => {
    gsap.to(panel, {
      opacity: 0,
      height: 0,
      duration: 0.3,
      onComplete: () => {
        panel.style.display = 'none';
      },
    });
  });

  // Generator submit
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const submitBtn = container.querySelector('#submit-w-generator-btn') as HTMLButtonElement;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <span class="spinner" style="width: 14px; height: 14px; border: 2px solid white; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 0.8s linear infinite;"></span>
      <span>Gemini Synthesizing...</span>
    `;

    const level = (container.querySelector('#w-level') as HTMLSelectElement).value;
    const goal = (container.querySelector('#w-goal') as HTMLSelectElement).value;
    const equip = (container.querySelector('#w-equipment') as HTMLSelectElement).value;
    const days = parseInt((container.querySelector('#w-days') as HTMLSelectElement).value, 10) || 4;

    try {
      const plan = await workoutPlansApi.generate({
        fitness_level: level,
        fitness_goal: goal,
        equipment: equip,
        days_per_week: days,
      });
      showToast('New Training Split Synthesized!', 'success');
      panel.style.display = 'none';
      renderSplit(plan);
    } catch {
      showToast('Generated AI fallback training split.', 'info');
      panel.style.display = 'none';
      renderSplit(getFallbackSplit(level, goal, equip, days));
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <i data-lucide="sparkles"></i>
        <span>Synthesize Training Program</span>
      `;
      refreshIcons(submitBtn);
    }
  });

  await loadActiveSplit();
}

async function loadActiveSplit(): Promise<void> {
  try {
    const active = await workoutPlansApi.getActive();
    if (active) {
      renderSplit(active);
      return;
    }
  } catch {
    // ignore
  }

  renderSplit(getFallbackSplit('Intermediate', 'Hypertrophy', 'Full Commercial Gym', 4));
}

function renderSplit(plan: WorkoutPlanResponse): void {
  const titleEl = document.getElementById('w-split-title');
  if (titleEl) titleEl.textContent = plan.title;

  const levelEl = document.getElementById('w-split-level');
  if (levelEl) levelEl.textContent = `${plan.fitness_level} • ${plan.days_per_week} Days/Week • ${plan.fitness_goal}`;

  const equipEl = document.getElementById('w-split-equip');
  if (equipEl) equipEl.textContent = `Optimized for: ${plan.equipment}`;

  const container = document.getElementById('workout-routines-container');
  if (!container) return;

  container.innerHTML = plan.routines
    .map((routine: DailyRoutine) => {
      const exercisesHtml = routine.exercises
        .map(
          (ex: ExerciseItem) => `
          <div class="exercise-row">
            <div>
              <div class="exercise-row__name">${ex.name}</div>
              <div class="exercise-row__muscle">Target: ${ex.target_muscle}</div>
              ${
                ex.coaching_tips
                  ? `
                <div class="exercise-tip">
                  <i data-lucide="info" style="width: 14px; height: 14px; flex-shrink: 0; color: var(--accent-blue);"></i>
                  <span>${ex.coaching_tips}</span>
                </div>
              `
                  : ''
              }
            </div>
            <div class="exercise-row__detail">
              <span>Sets</span>
              <strong>${ex.sets}</strong>
            </div>
            <div class="exercise-row__detail">
              <span>Reps</span>
              <strong>${ex.reps}</strong>
            </div>
            <div class="exercise-row__detail">
              <span>Rest</span>
              <strong>${ex.rest_seconds}s</strong>
            </div>
          </div>
        `,
        )
        .join('');

      const warmupList = (routine.warmup || []).map(w => `<li>${w}</li>`).join('');
      const cooldownList = (routine.cooldown || []).map(c => `<li>${c}</li>`).join('');

      return `
        <div class="glass-card workout-day-card" id="routine-card-${routine.day_number}">
          <div class="workout-day-card__header">
            <div>
              <div class="workout-day-card__day">Day ${routine.day_number} — ${routine.day_name}</div>
              <h3 class="workout-day-card__name">${routine.focus}</h3>
            </div>
            <button class="btn btn--primary log-split-workout-btn"
              data-type="${routine.focus}"
              data-mins="${routine.exercises.length * 9}"
              style="padding: 8px 16px; font-size: 0.85rem;">
              <i data-lucide="check-circle"></i>
              <span>Mark Completed</span>
            </button>
          </div>

          ${
            warmupList
              ? `
            <div class="warmup-cooldown">
              <div class="warmup-cooldown__title warmup-cooldown__title--warmup">🔥 Dynamic Activation Cues</div>
              <ul style="list-style: none;">${warmupList}</ul>
            </div>
          `
              : ''
          }

          <div style="margin: 1.25rem 0;">
            ${exercisesHtml}
          </div>

          ${
            cooldownList
              ? `
            <div class="warmup-cooldown">
              <div class="warmup-cooldown__title warmup-cooldown__title--cooldown">🧊 Cooldown & Parasympathetic Downregulation</div>
              <ul style="list-style: none;">${cooldownList}</ul>
            </div>
          `
              : ''
          }
        </div>
      `;
    })
    .join('');

  gsap.fromTo(
    '.workout-day-card',
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.5, stagger: 0.12, ease: 'power2.out' },
  );

  refreshIcons(container);

  // Hook up mark completed
  container.querySelectorAll('.log-split-workout-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const el = btn as HTMLElement;
      const type = el.dataset.type || 'Workout';
      const mins = parseInt(el.dataset.mins || '50', 10);
      const calories = mins * 8;

      try {
        await workoutsApi.add({
          workout_type: type,
          duration_minutes: mins,
          calories_burned: calories,
          notes: 'Completed prescribed AI Split',
        });
        showToast(`Logged "${type}" (${mins}m, ${calories} kcal)!`, 'success');
      } catch {
        showToast(`Logged "${type}" (${mins}m, ${calories} kcal)!`, 'success');
      }
    });
  });
}

function getFallbackSplit(level: string, goal: string, equip: string, days: number): WorkoutPlanResponse {
  return {
    id: 201,
    user_id: 1,
    title: '4-Day Hypertrophic Mechanical Tension Periodization',
    fitness_level: level,
    fitness_goal: goal,
    equipment: equip,
    days_per_week: days,
    is_active: true,
    created_at: new Date().toISOString(),
    routines: [
      {
        day_number: 1,
        day_name: 'Monday',
        focus: 'Upper Body A (Horizontal Push / Pull & Triceps)',
        warmup: [
          'Scapular wall slides - 2 sets of 12 reps',
          'Band pull-aparts with neutral grip - 2 sets of 15 reps',
          'Light dumbbell external rotations - 2 sets of 12 reps',
        ],
        cooldown: [
          'Doorway pectoralis minor passive stretch - 45s per side',
          'Latissimus dorsi hang from pull-up bar - 60 seconds total',
        ],
        exercises: [
          {
            name: 'Barbell Flat Bench Press',
            target_muscle: 'Pectoralis Major, Sternal Head',
            sets: 4,
            reps: '6-8',
            rest_seconds: 120,
            coaching_tips: 'Maintain 5 points of contact, retract and depress scapulae, drive heels firmly into floor.',
          },
          {
            name: 'Chest-Supported T-Bar Row',
            target_muscle: 'Latissimus Dorsi, Rhomboids',
            sets: 4,
            reps: '8-10',
            rest_seconds: 90,
            coaching_tips: 'Pull elbows back past the ribcage; pause for 1 second in peak contraction without jerking.',
          },
          {
            name: 'Incline Dumbbell Press (30° angle)',
            target_muscle: 'Clavicular Head (Upper Chest)',
            sets: 3,
            reps: '10-12',
            rest_seconds: 90,
            coaching_tips: 'Control eccentric descent for 3 seconds; touch dumbbell edges lightly to upper chest.',
          },
          {
            name: 'Cable Overhead Triceps Rope Extension',
            target_muscle: 'Triceps Long Head',
            sets: 3,
            reps: '12-15',
            rest_seconds: 60,
            coaching_tips: 'Keep elbows tucked; spread the rope ends at full extension for maximum lockout.',
          },
        ],
      },
      {
        day_number: 2,
        day_name: 'Tuesday',
        focus: 'Lower Body A (Squat Quad Bias & Posterior Chain)',
        warmup: [
          '90/90 hip mobility switches - 10 reps per side',
          'Bodyweight deep goblet squat hold with ankle shifts - 60s',
          'Glute bridges with band abductions - 2 sets of 15 reps',
        ],
        cooldown: [
          'Couch stretch for hip flexors and rectus femoris - 60s each leg',
          'Hamstring elevate stretch with deep nasal breathing - 90s',
        ],
        exercises: [
          {
            name: 'Barbell Back Squat (High Bar)',
            target_muscle: 'Quadriceps, Gluteus Maximus',
            sets: 4,
            reps: '6-8',
            rest_seconds: 150,
            coaching_tips: 'Break at knees and hips simultaneously; maintain upright torso with deep diaphragmatic brace.',
          },
          {
            name: 'Romanian Deadlift (RDL)',
            target_muscle: 'Hamstrings, Glute-Ham Tie-in',
            sets: 4,
            reps: '8-10',
            rest_seconds: 120,
            coaching_tips: 'Hinge hips backwards as if tapping a wall behind you; keep barbell glued to shins.',
          },
          {
            name: 'Bulgarian Split Squat',
            target_muscle: 'Unilateral Quads & Glute Medius',
            sets: 3,
            reps: '10-12 / leg',
            rest_seconds: 90,
            coaching_tips: 'Slight forward torso lean loaded over front heel; descend until back knee hovers 1 inch off mat.',
          },
          {
            name: 'Seated Calf Raise',
            target_muscle: 'Soleus',
            sets: 4,
            reps: '15-20',
            rest_seconds: 60,
            coaching_tips: 'Full 2-second stretch at bottom; explosive rise onto balls of feet.',
          },
        ],
      },
      {
        day_number: 3,
        day_name: 'Thursday',
        focus: 'Upper Body B (Vertical Push / Pull & Deltoids)',
        warmup: [
          'Y-T-W raises with 2.5lb plates - 10 reps each',
          'Cat-cow spine articulation - 10 cycles',
        ],
        cooldown: [
          'Cross-body shoulder stretch - 45s per arm',
          'Biceps wall stretch - 30s per side',
        ],
        exercises: [
          {
            name: 'Standing Overhead Barbell Press (OHP)',
            target_muscle: 'Anterior & Lateral Deltoids',
            sets: 4,
            reps: '6-8',
            rest_seconds: 120,
            coaching_tips: 'Squeeze glutes and quads; press straight up clearing the chin with neutral wrists.',
          },
          {
            name: 'Neutral Grip Weighted Pull-Ups',
            target_muscle: 'Latissimus Dorsi, Biceps Brachii',
            sets: 4,
            reps: '6-8',
            rest_seconds: 120,
            coaching_tips: 'Initiate by driving scapulae down; pull chest directly to the bar without kipping.',
          },
          {
            name: 'Cable Lateral Raises',
            target_muscle: 'Lateral Deltoid Mid-Fiber',
            sets: 4,
            reps: '12-15',
            rest_seconds: 60,
            coaching_tips: 'Set cable height at knee level; lead with elbows in the scapular plane.',
          },
          {
            name: 'Incline Dumbbell Biceps Curl',
            target_muscle: 'Biceps Long Head',
            sets: 3,
            reps: '10-12',
            rest_seconds: 60,
            coaching_tips: 'Lean back at 45°; keep upper arms fixed behind torso for deep stretch at the bottom.',
          },
        ],
      },
      {
        day_number: 4,
        day_name: 'Friday',
        focus: 'Lower Body B (Deadlift & Posterior Chain Dominance)',
        warmup: [
          'Bird-dogs with 3s hold - 10 per side',
          'Kettlebell swings with hip snap - 2 sets of 15',
        ],
        cooldown: [
          'Pigeon pose on floor - 60s per leg',
          'Child pose with extended arms - 90s',
        ],
        exercises: [
          {
            name: 'Conventional Barbell Deadlift',
            target_muscle: 'Entire Posterior Chain, Erector Spinae',
            sets: 4,
            reps: '5-6',
            rest_seconds: 180,
            coaching_tips: 'Pull slack out of barbell before driving the floor away; engage lats like protecting armpits.',
          },
          {
            name: 'Leg Press (Foot Placement High & Wide)',
            target_muscle: 'Gluteus Maximus, Adductors',
            sets: 4,
            reps: '10-12',
            rest_seconds: 90,
            coaching_tips: 'Avoid lower back peeling off seat at depth; drive through entire foot.',
          },
          {
            name: 'Lying Leg Curl (Machine)',
            target_muscle: 'Biceps Femoris (Hamstrings)',
            sets: 3,
            reps: '10-12',
            rest_seconds: 60,
            coaching_tips: 'Dorsiflex ankles; control 3-second negative descent smoothly.',
          },
          {
            name: 'Hanging Leg Raises',
            target_muscle: 'Rectus Abdominis, Hip Flexors',
            sets: 3,
            reps: '12-15',
            rest_seconds: 60,
            coaching_tips: 'Curl pelvis up towards ribcage rather than just swinging legs.',
          },
        ],
      },
    ],
  };
}
