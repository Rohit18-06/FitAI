import { createIcons, icons } from 'lucide';

export function refreshIcons(root?: HTMLElement | Document): void {
  try {
    createIcons({
      icons,
      root: root || document,
      attrs: {
        'stroke-width': '2',
      },
    });
  } catch (err) {
    console.warn('Failed to initialize Lucide icons:', err);
  }
}
