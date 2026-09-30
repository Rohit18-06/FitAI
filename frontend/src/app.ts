// ============================================================
// FitAI – Main Application Coordinator & Route Registry
// ============================================================
import { router } from './router';
import { initBackground } from './components/background';
import { renderLoginPage } from './pages/login';
import { renderRegisterPage } from './pages/register';
import { renderDashboardPage } from './pages/dashboard';
import { renderDietPage } from './pages/diet';
import { renderWorkoutsPage } from './pages/workouts';
import { renderVideoPage } from './pages/video';
import { renderAnalyticsPage } from './pages/analytics';
import { renderInsightsPage } from './pages/insights';
import { renderProfilePage } from './pages/profile';
import { renderCoachPage } from './pages/coach';
import { renderBMIPage } from './pages/bmi';
import { renderCaloriesPage } from './pages/calories';
import { renderWaterPage } from './pages/water';
import { renderStepsPage } from './pages/steps';
import { renderWearablesPage } from './pages/wearables';

export function initApp(): void {
  // 1. Initialize animated ambient glassmorphism background
  initBackground();

  // 2. Register all SPA routes
  router
    // Public routes
    .addRoute('/login', () => renderLoginPage(), false)
    .addRoute('/register', () => renderRegisterPage(), false)

    // Protected core routes
    .addRoute('/dashboard', () => renderDashboardPage(), true)
    .addRoute('/wearables', () => renderWearablesPage(), true)
    .addRoute('/coach', () => renderCoachPage(), true)
    .addRoute('/bmi', () => renderBMIPage(), true)
    .addRoute('/calories', () => renderCaloriesPage(), true)
    .addRoute('/water', () => renderWaterPage(), true)
    .addRoute('/steps', () => renderStepsPage(), true)
    .addRoute('/diet', () => renderDietPage(), true)
    .addRoute('/workouts', () => renderWorkoutsPage(), true)
    .addRoute('/video', () => renderVideoPage(), true)
    .addRoute('/analytics', () => renderAnalyticsPage(), true)
    .addRoute('/insights', () => renderInsightsPage(), true)
    .addRoute('/profile', () => renderProfilePage(), true);

  // 3. Resolve initial route
  router.resolve();
}
