// Sprite strips described by assets/*.json manifests: { name: { file, w, h, frames, fps, anchor:[x,y], meta? } }
export const SPR = {};
export const IMG = {};
export const WORLD = {};

const loadImage = src => new Promise(res => { const im = new Image(); im.onload = () => res(im); im.onerror = () => res(null); im.src = src; });
const loadJSON = src => fetch(src).then(r => (r.ok ? r.json() : null)).catch(() => null);

export async function loadManifest(group) {
  const m = await loadJSON(`assets/${group}.json`);
  if (!m) return;
  await Promise.all(Object.entries(m).map(async ([name, d]) => {
    const im = await loadImage(`assets/${d.file}`);
    if (im) SPR[name] = Object.assign({ fps: 8, frames: 1, anchor: [d.w >> 1, d.h] }, d, { img: im, flip: null });
  }));
}

// a district: parallax layers and the tileset
export async function loadWorld(name) {
  if (WORLD[name]) return WORLD[name];
  const m = await loadJSON(`assets/world_${name}.json`);
  if (!m) return (WORLD[name] = null);
  const layers = await Promise.all((m.layers || []).map(async L => Object.assign({}, L, { img: await loadImage(`assets/${L.file}`) })));
  const tiles = m.tiles ? Object.assign({}, m.tiles, { img: await loadImage(`assets/${m.tiles.file}`) }) : null;
  return (WORLD[name] = { layers: layers.filter(l => l.img), tiles });
}

// mirrored copy of a strip, built once, so drawing left-facing sprites stays a plain drawImage
function flipped(s) {
  if (s.flip) return s.flip;
  const c = document.createElement('canvas'); c.width = s.img.width; c.height = s.img.height;
  const g = c.getContext('2d');
  for (let i = 0; i < s.frames; i++) { g.save(); g.translate((i + 1) * s.w, 0); g.scale(-1, 1); g.drawImage(s.img, i * s.w, 0, s.w, s.h, 0, 0, s.w, s.h); g.restore(); }
  return (s.flip = c);
}

export function frameAt(name, t) { const s = SPR[name]; return s ? Math.floor(t * s.fps) % s.frames : 0; }

// draw frame i of a strip with its anchor at (x, y); dir -1 mirrors around the anchor
export function draw(ctx, name, i, x, y, dir = 1) {
  const s = SPR[name];
  if (!s) return false;
  i = ((i % s.frames) + s.frames) % s.frames;
  const ax = dir < 0 ? s.w - s.anchor[0] : s.anchor[0];
  ctx.drawImage(dir < 0 ? flipped(s) : s.img, i * s.w, 0, s.w, s.h, Math.round(x - ax), Math.round(y - s.anchor[1]), s.w, s.h);
  return true;
}

// a point from a frame's meta (e.g. mouth, hand) converted to world space for an anchor at (x, y)
export function metaPoint(name, i, k, x, y, dir = 1) {
  const s = SPR[name];
  if (!s || !s.meta) return null;
  const m = s.meta[((i % s.frames) + s.frames) % s.frames];
  if (m[k] < 0) return null;
  return [x + dir * (m[k] - s.anchor[0]), y + (m[k + 1] - s.anchor[1])];
}
