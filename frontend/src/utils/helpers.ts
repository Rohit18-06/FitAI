// ============================================================
// FitAI – Utility Helpers
// ============================================================

/** Format ISO date string to readable format */
export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/** Format ISO date to time */
export function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Animate a number counter from 0 to target */
export function animateCounter(
  el: HTMLElement,
  target: number,
  duration = 1200,
  decimals = 0,
): void {
  let start = 0;
  const startTime = performance.now();
  const step = (now: number) => {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    start = target * eased;
    el.textContent = start.toFixed(decimals);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/** Escape HTML to prevent XSS */
export function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/** Simple debounce */
export function debounce<T extends (...args: unknown[]) => void>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** Check if user is authenticated */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('fitai_token');
}

/** Get stored user */
export function getStoredUser(): { id: number; email: string; username: string } | null {
  const raw = localStorage.getItem('fitai_user');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

/** Store auth data */
export function storeAuth(token: string, user: { id: number; email: string; username: string }): void {
  localStorage.setItem('fitai_token', token);
  localStorage.setItem('fitai_user', JSON.stringify(user));
}

/** Clear auth data */
export function clearAuth(): void {
  localStorage.removeItem('fitai_token');
  localStorage.removeItem('fitai_user');
}

/** Get a color for a priority level */
export function getPriorityColor(priority: string): string {
  switch (priority.toLowerCase()) {
    case 'high':
      return 'var(--danger)';
    case 'medium':
      return 'var(--warning)';
    case 'low':
      return 'var(--success)';
    default:
      return 'var(--accent-blue)';
  }
}

/** Get injury risk badge color */
export function getRiskColor(risk: string): string {
  switch (risk.toLowerCase()) {
    case 'high':
      return 'var(--danger)';
    case 'medium':
      return 'var(--warning)';
    case 'low':
      return 'var(--success)';
    default:
      return 'var(--accent-cyan)';
  }
}
