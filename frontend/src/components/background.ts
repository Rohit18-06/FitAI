// ============================================================
// FitAI – Animated Glass Background System
// Apple Vision Pro · Cyberpunk · Ambient Mesh
// ============================================================
import gsap from 'gsap';

export function initBackground(): void {
  // Check if background canvas already exists
  if (document.getElementById('bg-canvas')) return;

  const canvas = document.createElement('div');
  canvas.id = 'bg-canvas';
  canvas.className = 'bg-canvas';

  // 3 ambient glowing orbs
  canvas.innerHTML = `
    <div class="bg-orb bg-orb--1" id="orb-1"></div>
    <div class="bg-orb bg-orb--2" id="orb-2"></div>
    <div class="bg-orb bg-orb--3" id="orb-3"></div>
    <div id="particles-container"></div>
  `;

  document.body.prepend(canvas);

  // GSAP ambient motion for glowing orbs
  gsap.to('#orb-1', {
    x: '+=60',
    y: '+=40',
    scale: 1.15,
    duration: 12,
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
  });

  gsap.to('#orb-2', {
    x: '-=70',
    y: '-=50',
    scale: 1.2,
    duration: 15,
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
    delay: 1,
  });

  gsap.to('#orb-3', {
    x: '+=50',
    y: '-=40',
    scale: 1.1,
    duration: 10,
    repeat: -1,
    yoyo: true,
    ease: 'sine.inOut',
    delay: 2,
  });

  // Spawn floating particle dust
  const particlesContainer = document.getElementById('particles-container');
  if (particlesContainer) {
    const particleCount = 28;
    for (let i = 0; i < particleCount; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      const size = Math.random() * 3 + 1;
      p.style.width = `${size}px`;
      p.style.height = `${size}px`;
      p.style.left = `${Math.random() * 100}vw`;
      p.style.top = `${Math.random() * 100}vh`;
      p.style.opacity = `${Math.random() * 0.45 + 0.1}`;

      // Subtle cyan/blue/white tint
      const tints = ['rgba(255,255,255,0.6)', 'rgba(6,182,212,0.6)', 'rgba(59,130,246,0.6)'];
      p.style.background = tints[Math.floor(Math.random() * tints.length)];
      p.style.boxShadow = `0 0 6px ${p.style.background}`;

      particlesContainer.appendChild(p);

      // Float animation
      gsap.to(p, {
        y: `-=${Math.random() * 80 + 30}`,
        x: `+=${(Math.random() - 0.5) * 60}`,
        opacity: Math.random() * 0.7 + 0.1,
        duration: Math.random() * 8 + 6,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        delay: Math.random() * 5,
      });
    }
  }
}
