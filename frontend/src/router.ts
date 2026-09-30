// ============================================================
// FitAI – Hash-based SPA Router (no framework dependencies)
// ============================================================
import gsap from 'gsap';
import { isAuthenticated } from './utils/helpers';

export type RouteHandler = (params?: Record<string, string>) => void;

interface Route {
  path: string;
  handler: RouteHandler;
  requiresAuth: boolean;
}

class Router {
  private routes: Route[] = [];
  private currentPath = '';

  constructor() {
    window.addEventListener('hashchange', () => this.resolve());
    window.addEventListener('load', () => this.resolve());
  }

  addRoute(path: string, handler: RouteHandler, requiresAuth = true): Router {
    this.routes.push({ path, handler, requiresAuth });
    return this;
  }

  navigate(path: string): void {
    window.location.hash = `#${path}`;
  }

  resolve(): void {
    const hash = window.location.hash.slice(1) || '/login';

    // Prevent re-rendering same route
    if (hash === this.currentPath) return;
    this.currentPath = hash;

    const matched = this.routes.find(r => {
      if (r.path === hash) return true;
      // Simple param matching: /route/:id
      const routeParts = r.path.split('/');
      const hashParts = hash.split('/');
      if (routeParts.length !== hashParts.length) return false;
      return routeParts.every((part, i) =>
        part.startsWith(':') || part === hashParts[i],
      );
    });

    if (!matched) {
      this.navigate('/login');
      return;
    }

    if (matched.requiresAuth && !isAuthenticated()) {
      this.navigate('/login');
      return;
    }

    if (!matched.requiresAuth && isAuthenticated() && (hash === '/login' || hash === '/register')) {
      this.navigate('/dashboard');
      return;
    }

    // Page transition
    const appEl = document.getElementById('app');
    if (appEl) {
      gsap.to(appEl, {
        opacity: 0,
        duration: 0.15,
        onComplete: () => {
          // Extract params
          const params: Record<string, string> = {};
          const routeParts = matched.path.split('/');
          const hashParts = hash.split('/');
          routeParts.forEach((part, i) => {
            if (part.startsWith(':')) {
              params[part.slice(1)] = hashParts[i];
            }
          });

          matched.handler(params);

          gsap.to(appEl, { opacity: 1, duration: 0.25 });
        },
      });
    }
  }
}

export const router = new Router();
