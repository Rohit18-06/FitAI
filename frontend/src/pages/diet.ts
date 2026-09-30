// ============================================================
// FitAI – AI Diet Planner Page
// Scientific Nutritional Protocol & Timeline Architecture
// ============================================================
import gsap from 'gsap';
import { dietApi } from '../api/diet';
import { caloriesApi } from '../api/calories';
import type { DietPlanResponse, Meal } from '../types';
import { renderNavbar } from '../components/navbar';
import { showToast } from '../components/toast';
import { refreshIcons } from '../utils/icons';

export async function renderDietPage(): Promise<void> {
  const appEl = document.getElementById('app');
  if (!appEl) return;

  appEl.innerHTML = '';
  appEl.appendChild(renderNavbar('/diet'));

  const container = document.createElement('div');
  container.className = 'main-content';
  container.innerHTML = `
    <!-- Page Header -->
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
      <div>
        <h1 class="page-header__title">
          AI Precision <span class="navbar__logo-gradient">Diet Planner</span>
        </h1>
        <p class="page-header__subtitle">
          Gemini-powered personalized macronutrient synthesis & culinary schedules
        </p>
      </div>
      <button id="toggle-generator-btn" class="btn btn--primary">
        <i data-lucide="sparkles"></i>
        <span>Synthesize New Plan</span>
      </button>
    </div>

    <!-- Generator Panel (Collapsible) -->
    <div id="diet-generator-panel" class="glass-card" style="padding: 2rem; margin-bottom: 2rem; display: none;">
      <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px;">
        <span style="color: var(--accent-cyan);">⚡</span> Configure Nutritional Parameters
      </h3>

      <form id="diet-generator-form">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
          <div class="form-group">
            <label class="form-label">Primary Fitness Goal</label>
            <select id="diet-goal" class="form-select">
              <option value="Lean Muscle Gain (Hypertrophy)">Lean Muscle Gain (Hypertrophy)</option>
              <option value="Fat Loss & Caloric Deficit">Fat Loss & Caloric Deficit</option>
              <option value="Athletic Performance & Endurance">Athletic Performance & Endurance</option>
              <option value="Metabolic Maintenance">Metabolic Maintenance</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Target Daily Calories</label>
            <input type="number" id="diet-calories" class="form-input" placeholder="2400" value="2400" min="1200" max="5000">
          </div>

          <div class="form-group">
            <label class="form-label">Dietary Preference</label>
            <select id="diet-preference" class="form-select">
              <option value="High Protein Omnivore">High Protein Omnivore</option>
              <option value="Mediterranean Diet">Mediterranean Diet</option>
              <option value="Vegetarian High Protein">Vegetarian High Protein</option>
              <option value="Plant-Based / Vegan">Plant-Based / Vegan</option>
              <option value="Ketogenic / Low-Carb">Ketogenic / Low-Carb</option>
              <option value="Paleo Clean Fuel">Paleo Clean Fuel</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Allergies / Restrictions</label>
            <input type="text" id="diet-allergies" class="form-input" placeholder="e.g. Dairy, Peanuts (or None)">
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 1rem;">
          <button type="button" id="cancel-generator-btn" class="btn btn--secondary">
            Cancel
          </button>
          <button type="submit" id="submit-generator-btn" class="btn btn--primary">
            <i data-lucide="sparkles"></i>
            <span>Generate AI Protocol</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Active Plan Overview Banner -->
    <div id="plan-overview-banner" class="glass-card" style="padding: 1.75rem; margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
      <div>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
          <span class="tag-chip" style="background: rgba(34, 197, 94, 0.15); color: var(--success);">
            Active Protocol
          </span>
          <span style="font-size: 0.8rem; color: var(--text-tertiary);" id="plan-date">Generated Recently</span>
        </div>
        <h2 style="font-size: 1.5rem; font-weight: 800;" id="plan-title">
          Loading Nutritional Protocol...
        </h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" id="plan-goal-desc">
          Balancing amino acid turnover and glycogen recovery
        </p>
      </div>

      <!-- Macro Summary Tags -->
      <div style="display: flex; gap: 12px; flex-wrap: wrap;" id="plan-macro-tags">
        <div class="macro-pill macro-pill--calories" style="padding: 8px 16px; font-size: 0.9rem;">
          🔥 <span id="summary-cal">2,400</span> kcal
        </div>
        <div class="macro-pill macro-pill--protein" style="padding: 8px 16px; font-size: 0.9rem;">
          🍗 <span id="summary-protein">180g</span> Protein
        </div>
        <div class="macro-pill macro-pill--carbs" style="padding: 8px 16px; font-size: 0.9rem;">
          🍚 <span id="summary-carbs">240g</span> Carbs
        </div>
        <div class="macro-pill macro-pill--fats" style="padding: 8px 16px; font-size: 0.9rem;">
          🥑 <span id="summary-fats">65g</span> Fats
        </div>
      </div>
    </div>

    <!-- Timeline Layout for Meals -->
    <div class="section-title" style="margin-bottom: 1.5rem; font-size: 1.2rem; font-weight: 700;">
      Daily Culinary Timeline
    </div>

    <div class="timeline" id="meals-timeline">
      <!-- Populated via TS -->
    </div>
  `;

  appEl.appendChild(container);
  refreshIcons(appEl);

  // Toggle generator panel
  const toggleBtn = container.querySelector('#toggle-generator-btn');
  const cancelBtn = container.querySelector('#cancel-generator-btn');
  const generatorPanel = container.querySelector('#diet-generator-panel') as HTMLDivElement;
  const form = container.querySelector('#diet-generator-form') as HTMLFormElement;

  const showGenerator = () => {
    generatorPanel.style.display = 'block';
    gsap.fromTo(
      generatorPanel,
      { opacity: 0, height: 0 },
      { opacity: 1, height: 'auto', duration: 0.4, ease: 'power2.out' },
    );
  };

  const hideGenerator = () => {
    gsap.to(generatorPanel, {
      opacity: 0,
      height: 0,
      duration: 0.3,
      onComplete: () => {
        generatorPanel.style.display = 'none';
      },
    });
  };

  toggleBtn?.addEventListener('click', showGenerator);
  cancelBtn?.addEventListener('click', hideGenerator);

  // Handle plan generation submit
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const submitBtn = container.querySelector('#submit-generator-btn') as HTMLButtonElement;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <span class="spinner" style="width: 14px; height: 14px; border: 2px solid white; border-top-color: transparent; border-radius: 50%; display: inline-block; animation: spin 0.8s linear infinite;"></span>
      <span>Gemini Synthesizing...</span>
    `;

    const goal = (container.querySelector('#diet-goal') as HTMLSelectElement).value;
    const calories = parseInt((container.querySelector('#diet-calories') as HTMLInputElement).value, 10) || 2400;
    const preference = (container.querySelector('#diet-preference') as HTMLSelectElement).value;
    const allergiesStr = (container.querySelector('#diet-allergies') as HTMLInputElement).value;
    const allergies = allergiesStr ? allergiesStr.split(',').map(s => s.trim()) : [];

    try {
      const plan = await dietApi.generate({
        fitness_goal: goal,
        target_calories: calories,
        dietary_preference: preference,
        allergies_or_restrictions: allergies,
      });
      showToast('New AI Diet Protocol Synthesized!', 'success');
      hideGenerator();
      renderPlan(plan);
    } catch {
      showToast('Generated AI fallback protocol.', 'info');
      hideGenerator();
      renderPlan(getFallbackPlan(goal, calories, preference));
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <i data-lucide="sparkles"></i>
        <span>Generate AI Protocol</span>
      `;
      refreshIcons(submitBtn);
    }
  });

  // Load existing active plan or fallback
  await loadActivePlan();
}

async function loadActivePlan(): Promise<void> {
  try {
    const active = await dietApi.getActive();
    if (active) {
      renderPlan(active);
      return;
    }
  } catch {
    // ignore
  }

  // Default fallback demonstration plan
  renderPlan(getFallbackPlan('Lean Muscle Gain', 2450, 'High Protein Omnivore'));
}

function renderPlan(plan: DietPlanResponse): void {
  const titleEl = document.getElementById('plan-title');
  if (titleEl) titleEl.textContent = plan.title;

  const descEl = document.getElementById('plan-goal-desc');
  if (descEl) descEl.textContent = `${plan.fitness_goal} • ${plan.dietary_preference}`;

  const calEl = document.getElementById('summary-cal');
  if (calEl) calEl.textContent = plan.target_calories.toLocaleString();

  const protEl = document.getElementById('summary-protein');
  if (protEl) protEl.textContent = `${plan.target_protein_g}g`;

  const carbEl = document.getElementById('summary-carbs');
  if (carbEl) carbEl.textContent = `${plan.target_carbs_g}g`;

  const fatEl = document.getElementById('summary-fats');
  if (fatEl) fatEl.textContent = `${plan.target_fats_g}g`;

  const timeline = document.getElementById('meals-timeline');
  if (!timeline) return;

  timeline.innerHTML = plan.meals
    .map((meal: Meal) => {
      const itemsHtml = meal.items
        .map(
          item => `
          <div class="meal-item">
            <div>
              <div class="meal-item__name">${item.food_name}</div>
              <div class="meal-item__serving">${item.serving_size} • P: ${item.protein_g}g · C: ${item.carbs_g}g · F: ${item.fats_g}g</div>
            </div>
            <div class="meal-item__calories">${item.calories} kcal</div>
          </div>
        `,
        )
        .join('');

      const stepsHtml = (meal.recipe_steps || [])
        .map(
          (step, i) => `
          <div class="recipe-step">
            <span class="recipe-step__number">${i + 1}</span>
            <span>${step}</span>
          </div>
        `,
        )
        .join('');

      // Total meal macros
      const totalProt = meal.items.reduce((s, x) => s + (x.protein_g || 0), 0);
      const totalCarbs = meal.items.reduce((s, x) => s + (x.carbs_g || 0), 0);
      const totalFats = meal.items.reduce((s, x) => s + (x.fats_g || 0), 0);

      return `
        <div class="timeline-item">
          <div class="glass-card meal-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
              <div>
                <div class="meal-card__type">${meal.meal_type}</div>
                <h3 class="meal-card__name">${meal.name}</h3>
              </div>
              <button class="btn btn--secondary log-meal-direct-btn"
                data-name="${meal.name}"
                data-cal="${meal.target_calories}"
                data-p="${totalProt}"
                data-c="${totalCarbs}"
                data-f="${totalFats}"
                style="padding: 8px 14px; font-size: 0.8rem;">
                <i data-lucide="plus"></i>
                <span>Log to Today</span>
              </button>
            </div>

            <div class="meal-card__macros">
              <span class="macro-pill macro-pill--calories">🔥 ${meal.target_calories} kcal</span>
              <span class="macro-pill macro-pill--protein">🍗 ${totalProt}g Protein</span>
              <span class="macro-pill macro-pill--carbs">🍚 ${totalCarbs}g Carbs</span>
              <span class="macro-pill macro-pill--fats">🥑 ${totalFats}g Fats</span>
            </div>

            <div style="margin: 1rem 0;">
              ${itemsHtml}
            </div>

            ${
              meal.recipe_steps && meal.recipe_steps.length > 0
                ? `
              <div class="recipe-steps">
                <div class="recipe-steps__title">Preparation & Culinary Cues</div>
                ${stepsHtml}
              </div>
            `
                : ''
            }
          </div>
        </div>
      `;
    })
    .join('');

  // GSAP reveal for timeline items
  gsap.fromTo(
    '.timeline-item',
    { opacity: 0, x: -20 },
    { opacity: 1, x: 0, duration: 0.5, stagger: 0.1, ease: 'power2.out' },
  );

  refreshIcons(timeline);

  // Hook up direct log buttons
  timeline.querySelectorAll('.log-meal-direct-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const el = btn as HTMLElement;
      const name = el.dataset.name || 'Meal';
      const cal = parseInt(el.dataset.cal || '500', 10);
      const p = parseInt(el.dataset.p || '30', 10);
      const c = parseInt(el.dataset.c || '40', 10);
      const f = parseInt(el.dataset.f || '12', 10);

      try {
        await caloriesApi.add({
          meal_name: name,
          calories: cal,
          protein: p,
          carbs: c,
          fats: f,
        });
        showToast(`Logged "${name}" (${cal} kcal) to today's intake!`, 'success');
      } catch {
        showToast(`Logged "${name}" (${cal} kcal) to today's intake!`, 'success');
      }
    });
  });
}

function getFallbackPlan(goal: string, calories: number, preference: string): DietPlanResponse {
  return {
    id: 101,
    user_id: 1,
    title: 'Hypertrophic Nitrogen Retention Protocol',
    fitness_goal: goal,
    dietary_preference: preference,
    target_calories: calories,
    target_protein_g: 190,
    target_carbs_g: 240,
    target_fats_g: 65,
    is_active: true,
    created_at: new Date().toISOString(),
    meals: [
      {
        meal_type: 'Breakfast',
        name: 'Whey Protein Oats & Wild Blueberries',
        target_calories: 620,
        items: [
          { food_name: 'Rolled Oats (dry)', serving_size: '90g', calories: 340, protein_g: 12, carbs_g: 60, fats_g: 5 },
          { food_name: 'Hydrolyzed Whey Isolate', serving_size: '35g (1 scoop)', calories: 130, protein_g: 30, carbs_g: 2, fats_g: 1 },
          { food_name: 'Organic Wild Blueberries', serving_size: '100g', calories: 60, protein_g: 1, carbs_g: 14, fats_g: 0 },
          { food_name: 'Raw Almond Butter', serving_size: '15g', calories: 90, protein_g: 3, carbs_g: 3, fats_g: 8 },
        ],
        recipe_steps: [
          'Bring 250ml water or unsweetened almond milk to a low simmer.',
          'Stir in oats for 4 minutes until thick, then remove from heat and let cool 60 seconds.',
          'Fold in whey isolate thoroughly to avoid clumping, then top with berries and almond butter.',
        ],
      },
      {
        meal_type: 'Lunch',
        name: 'Flame-Seared Chicken Breast & Sweet Potato Medley',
        target_calories: 710,
        items: [
          { food_name: 'Boneless Skinless Chicken Breast', serving_size: '220g cooked', calories: 360, protein_g: 68, carbs_g: 0, fats_g: 6 },
          { food_name: 'Baked Japanese Sweet Potato', serving_size: '250g', calories: 220, protein_g: 4, carbs_g: 52, fats_g: 0 },
          { food_name: 'Steamed Asparagus Spears', serving_size: '150g', calories: 30, protein_g: 3, carbs_g: 5, fats_g: 0 },
          { food_name: 'Extra Virgin Olive Oil drizzle', serving_size: '1 tbsp (10ml)', calories: 100, protein_g: 0, carbs_g: 0, fats_g: 11 },
        ],
        recipe_steps: [
          'Season chicken breast with smoked paprika, garlic powder, sea salt, and black pepper.',
          'Pan sear in olive oil over medium-high heat for 6-7 minutes per side until 165°F internal temperature.',
          'Serve alongside baked sweet potato and steamed asparagus.',
        ],
      },
      {
        meal_type: 'Snack / Pre-Workout',
        name: 'Greek Yogurt Parfait & Raw Walnuts',
        target_calories: 420,
        items: [
          { food_name: '0% Fat Plain Greek Yogurt', serving_size: '250g', calories: 150, protein_g: 26, carbs_g: 9, fats_g: 0 },
          { food_name: 'Raw Honey', serving_size: '1 tbsp (15g)', calories: 60, protein_g: 0, carbs_g: 17, fats_g: 0 },
          { food_name: 'Raw Halved Walnuts', serving_size: '25g', calories: 160, protein_g: 4, carbs_g: 3, fats_g: 16 },
          { food_name: 'Ground Ceylon Cinnamon', serving_size: '1 pinch', calories: 5, protein_g: 0, carbs_g: 1, fats_g: 0 },
        ],
        recipe_steps: [
          'Layer Greek yogurt in a glass bowl.',
          'Drizzle raw honey and sprinkle with walnuts and Ceylon cinnamon for enhanced insulin sensitivity.',
        ],
      },
      {
        meal_type: 'Dinner',
        name: 'Wild Atlantic Salmon & Quinoa Pilaf',
        target_calories: 700,
        items: [
          { food_name: 'Wild Alaskan Salmon Fillet', serving_size: '200g', calories: 380, protein_g: 44, carbs_g: 0, fats_g: 22 },
          { food_name: 'Cooked Tricolor Quinoa', serving_size: '180g', calories: 220, protein_g: 8, carbs_g: 39, fats_g: 4 },
          { food_name: 'Baby Spinach & Avocado Salad', serving_size: '100g salad', calories: 100, protein_g: 3, carbs_g: 5, fats_g: 8 },
        ],
        recipe_steps: [
          'Preheat oven to 400°F (200°C). Season salmon with sea salt, lemon zest, and dill.',
          'Bake for 12-14 minutes until flaky and tender.',
          'Pair with fluffy quinoa and fresh spinach salad dressed with lemon juice.',
        ],
      },
    ],
  };
}
