// ============================================================
// FitAI – Main Entry Point
// ============================================================
import './styles/main.css';
import { initApp } from './app';

// Boot the application
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

// Also trigger immediately in case DOM is already ready
if (document.readyState === 'interactive' || document.readyState === 'complete') {
  initApp();
}
