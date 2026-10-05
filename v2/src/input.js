// Keyboard, touch buttons and gamepad merged into one set of held keys plus "pressed this frame" edges.
const held = { left: false, right: false, up: false, down: false, jump: false, fire: false, dj: false, pause: false };
const touch = { left: false, right: false, down: false, jump: false, fire: false, dj: false };
let prev = {};
export const input = { held: {}, pressed: {}, usingTouch: false };

const KEYS = {
  ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'up', KeyW: 'up', ArrowDown: 'down', KeyS: 'down',
  Space: 'jump', KeyZ: 'jump', KeyX: 'fire', KeyJ: 'fire', KeyC: 'dj', KeyK: 'dj', Escape: 'pause', KeyP: 'pause'
};
addEventListener('keydown', e => {
  const k = KEYS[e.code];
  if (!k) return;
  held[k] = true;
  if (k === 'up') held.jump = true;
  e.preventDefault();
});
addEventListener('keyup', e => {
  const k = KEYS[e.code];
  if (!k) return;
  held[k] = false;
  if (k === 'up') held.jump = false;
});
addEventListener('blur', () => { for (const k in held) held[k] = false; for (const k in touch) touch[k] = false; });

// on-screen buttons: any element with data-key; several fingers at once
export function bindTouch(root) {
  const update = e => {
    for (const k in touch) touch[k] = false;
    for (const t of e.touches) {
      const el = document.elementFromPoint(t.clientX, t.clientY);
      const b = el && el.closest('[data-key]');
      if (b) touch[b.dataset.key] = true;
    }
    for (const b of root.querySelectorAll('[data-key]')) b.classList.toggle('on', !!touch[b.dataset.key]);
    input.usingTouch = true;
    e.preventDefault();
  };
  for (const ev of ['touchstart', 'touchmove', 'touchend', 'touchcancel']) root.addEventListener(ev, update, { passive: false });
}

export function pollInput() {
  const pad = navigator.getGamepads ? [...navigator.getGamepads()].find(p => p) : null;
  const g = {};
  if (pad) {
    const ax = pad.axes[0] || 0, b = i => pad.buttons[i] && pad.buttons[i].pressed;
    g.left = ax < -0.4 || b(14); g.right = ax > 0.4 || b(15); g.down = (pad.axes[1] || 0) > 0.5 || b(13);
    g.jump = b(0); g.fire = b(2) || b(7); g.dj = b(3) || b(1); g.pause = b(9);
  }
  const now = {};
  for (const k in held) now[k] = held[k] || !!touch[k] || !!g[k];
  for (const k in now) input.pressed[k] = now[k] && !prev[k];
  input.held = now; prev = now;
}
