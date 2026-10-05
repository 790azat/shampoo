import { SPR, WORLD, draw, frameAt, metaPoint } from './assets.js';
import { G, P, ents, cam, score, VIEW, playerAnim, heroFeet, getLives } from './game.js';
import { T, GROUND, BLOCK, LEDGE, CRATE } from './world.js';
import { LEVELS } from './levels.js';

export const FONT = "'Press Start 2P', monospace";
const OL = '#1a1024';

// ---------- crisp pixel text: rendered once with the web font, alpha thresholded, cached ----------
const TXT = new Map();
export function textImg(s, col, size = 8) {
  const key = s + '|' + col + '|' + size;
  let c = TXT.get(key);
  if (c) return c;
  const m = document.createElement('canvas').getContext('2d'); m.font = `${size}px ${FONT}`;
  const w = Math.ceil(m.measureText(s).width) + 4, h = size + 6;
  c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); g.font = `${size}px ${FONT}`; g.textBaseline = 'top';
  // dark outline first, then the colour
  g.fillStyle = OL; for (const [dx, dy] of [[0, 1], [2, 1], [1, 0], [1, 2], [2, 2]]) g.fillText(s, 1 + dx - 1, 1 + dy - 1 + 1);
  g.fillStyle = col; g.fillText(s, 1, 1);
  const d = g.getImageData(0, 0, w, h);
  for (let i = 3; i < d.data.length; i += 4) d.data[i] = d.data[i] > 110 ? 255 : 0;
  g.putImageData(d, 0, 0);
  if (document.fonts && document.fonts.status === 'loaded') TXT.set(key, c);
  return c;
}
export function txt(ctx, s, x, y, col = '#fff', align = 'left', size = 8) {
  const im = textImg(s, col, size);
  const ox = align === 'center' ? im.width / 2 : align === 'right' ? im.width : 0;
  ctx.drawImage(im, Math.round(x - ox), Math.round(y));
}

// ---------- tiles ----------
function tileName(W, tx, ty) {
  const t = W.at(tx, ty);
  const up = W.at(tx, ty - 1), L = W.at(tx - 1, ty), R = W.at(tx + 1, ty), dn = W.at(tx, ty + 1);
  const h = (tx * 7 + ty * 13) % 5;
  if (t === GROUND) {
    const oL = L !== GROUND && tx > 0, oR = R !== GROUND, oU = up !== GROUND;
    if (oU) {
      if (oL && oR) return ['single_top', 'top'];
      if (oL) return ['top_l', 'top'];
      if (oR) return ['top_r', 'top'];
      return h === 1 ? ['top2', 'top'] : h === 3 ? ['top3', 'top'] : ['top'];
    }
    if (oL && oR) return ['single', 'fill'];
    if (oL) return ['side_l', 'fill'];
    if (oR) return ['side_r', 'fill'];
    if (W.at(tx - 1, ty - 1) !== GROUND && tx > 0) return ['inner_l', 'fill'];
    if (W.at(tx + 1, ty - 1) !== GROUND) return ['inner_r', 'fill'];
    return h === 1 ? ['fill2', 'fill'] : h === 4 ? ['fill3', 'fill'] : ['fill'];
  }
  if (t === BLOCK) return [(h % 2) ? 'block2' : 'block', 'block'];
  if (t === CRATE) return [h === 2 ? 'barrel' : 'crate', 'crate'];
  if (t === LEDGE) return L !== LEDGE ? ['plat_l', 'plat'] : R !== LEDGE ? ['plat_r', 'plat'] : ['plat'];
  return null;
}
const FALLBACK = { [GROUND]: '#b5653f', [BLOCK]: '#7a6a80', [LEDGE]: '#8a5a3a', [CRATE]: '#c08a40' };

function drawTiles(ctx, W, world) {
  const ts = world && world.tiles, names = ts && ts.names;
  const c0 = Math.max(0, Math.floor(cam.x / T) - 1), c1 = Math.min(W.cols, c0 + Math.ceil(VIEW.w / T) + 3);
  for (let ty = 0; ty < W.rows; ty++) for (let tx = c0; tx < c1; tx++) {
    const t = W.at(tx, ty);
    if (!t) continue;
    const x = tx * T, y = ty * T;
    let done = false;
    if (ts && ts.img) {
      for (const n of tileName(W, tx, ty) || []) {
        const at = names[n];
        if (at) { ctx.drawImage(ts.img, at[0] * T, at[1] * T, T, T, x, y, T, T); done = true; break; }
      }
    }
    if (!done) {
      ctx.fillStyle = FALLBACK[t]; ctx.fillRect(x, y, T, t === LEDGE ? 5 : T);
      if (t === GROUND && W.at(tx, ty - 1) !== GROUND) { ctx.fillStyle = '#6dbb4a'; ctx.fillRect(x, y, T, 3); }
      ctx.fillStyle = OL; ctx.fillRect(x, y, T, 1);
    }
    // decoration on top of open ground
    if (t === GROUND && !W.at(tx, ty - 1) && names) {
      const h = (tx * 31 + ty * 17) % 7;
      const deco = h === 0 ? names.deco_grass : h === 3 ? names.deco_flowers : h === 5 ? names.deco_rocks : (tx * 13 + ty) % 23 === 0 ? names.deco_special : null;
      if (deco) ctx.drawImage(ts.img, deco[0] * T, deco[1] * T, T, T, x, y - T, T, T);
    }
  }
}

// ---------- parallax ----------
function drawBackground(ctx, world) {
  ctx.fillStyle = '#5ab0f0'; ctx.fillRect(0, 0, VIEW.w, VIEW.h);
  if (!world) return;
  const yShift = VIEW.h - 270;            // layers are authored for a 270 view; taller views extend the sky
  for (const L of world.layers) {
    const img = L.img, w = img.width, par = L.parallax || 0;
    if (L.file === 'bg_sky.png') { ctx.drawImage(img, 0, 0, w, img.height, 0, 0, VIEW.w, VIEW.h); continue; }
    const drift = L.drift ? G.t * L.drift : (L.file.includes('cloud') ? G.t * 6 : 0);
    const off = -Math.round((((cam.x * par + drift) % w) + w) % w);
    const y = Math.round((L.y || 0) + yShift);
    for (let x = off; x < VIEW.w; x += w) ctx.drawImage(img, x, y);
  }
}

// ---------- entities ----------
const ITEM_SPR = { boom: 'item_boom', rush: 'item_rush', vip: 'item_vip', terea: 'item_terea', shampoo: 'item_shampoo' };
const DECOR = { l: 'prop_lamp', n: 'prop_bench', u: 'prop_bin', q: 'prop_kiosk', T: 'prop_tree', f: 'prop_fountain', h: 'prop_hydrant' };
const FOE_SPR = {
  dog: e => (Math.abs(e.vx) > 1 ? ['dog_run', frameAt('dog_run', e.t * (Math.abs(e.vx) > 60 ? 1.6 : 1))] : ['dog_idle', frameAt('dog_idle', e.t)]),
  pigeon: e => ['pigeon_fly', frameAt('pigeon_fly', e.t)],
  granny: e => (e.throwT > 0 ? ['granny_throw', Math.min(2, Math.floor((0.45 - e.throwT) / 0.15))] : ['granny_walk', frameAt('granny_walk', e.t)]),
  courier: e => ['courier_ride', frameAt('courier_ride', e.t)]
};

function drawEntities(ctx) {
  const vx0 = cam.x - 80, vx1 = cam.x + VIEW.w + 80, vis = x => x > vx0 && x < vx1;
  for (const d of ents.decor) if (vis(d.x)) draw(ctx, DECOR[d.ch], d.ch === 'f' ? frameAt('prop_fountain', G.t) : 0, d.x, d.y);
  if (vis(G.car.x)) {
    const car = G.hero === 'azat' ? 'car_teana' : 'car_focus';
    const s = SPR[car]; if (s) draw(ctx, car, 0, G.car.x + s.anchor[0] - 6, G.car.y);
  }
  for (const f of ents.flags) if (vis(f.x)) {
    if (!draw(ctx, 'flag_wave', f.on ? frameAt('flag_wave', f.t) : 0, f.x, f.y)) { ctx.fillStyle = OL; ctx.fillRect(f.x - 1, f.y - 56, 3, 56); ctx.fillStyle = f.on ? '#d90012' : '#888'; ctx.fillRect(f.x + 2, f.y - 56, 20, 12); }
  }
  if (vis(G.finishX)) draw(ctx, 'finish_arch', 0, G.finishX, G.world.groundY(G.finishX, 100) > 0 ? G.world.groundY(G.finishX, 100) : 14 * T);
  for (const it of ents.items) if (vis(it.x)) {
    const bob = Math.round(Math.sin(it.t * 2.6) * 2), sh = 'item_' + it.kind + '_shine', s = SPR[sh];
    const shine = s && (it.t % 2.4) < s.frames / s.fps;
    if (!draw(ctx, shine ? sh : ITEM_SPR[it.kind], shine ? frameAt(sh, it.t % 2.4) : 0, it.x, it.y + 11 + bob)) { ctx.fillStyle = '#ffd23a'; ctx.fillRect(it.x - 5, it.y - 8 + bob, 10, 16); }
  }
  for (const e of ents.foes) if (vis(e.x)) {
    const fx = e.x + e.w / 2, fy = e.y + e.h;
    if (!e.alive) { if (!draw(ctx, e.kind + '_dead', 0, fx, e.kind === 'pigeon' ? e.y + e.h / 2 : fy, e.dir)) { ctx.fillStyle = '#a77'; ctx.fillRect(e.x, e.y, e.w, e.h); } continue; }
    const [n, i] = FOE_SPR[e.kind](e);
    if (!draw(ctx, n, i, fx, e.kind === 'pigeon' ? e.y + e.h / 2 : fy + 1, e.dir)) { ctx.fillStyle = '#c33'; ctx.fillRect(e.x, e.y, e.w, e.h); }
  }
}

function drawPlayer(ctx) {
  const p = P;
  if (!p) return;
  if (p.inv > 0 && G.state === 'play' && Math.floor(p.inv * 14) % 2) return;
  const [a, i] = playerAnim(), name = `hero_${G.hero}_${a}`, [fx, fy] = heroFeet();
  if (G.state === 'dying' && !p.pit) {
    // lies on his back, then a ghost floats up
    const s = SPR[name];
    if (s) { ctx.save(); ctx.translate(Math.round(fx), Math.round(fy)); ctx.scale(p.dir, 1); ctx.rotate(-Math.PI / 2 * Math.min(1, p.dead * 4)); ctx.drawImage(s.img, 0, 0, s.w, s.h, -s.anchor[0], -s.anchor[1], s.w, s.h); ctx.restore(); }
    if (p.dead > 0.5) { ctx.globalAlpha = Math.max(0, 1 - (p.dead - 0.5)); ctx.drawImage(ghost(), Math.round(fx - 7 + Math.sin(p.dead * 6) * 3), Math.round(fy - 50 - (p.dead - 0.5) * 50)); ctx.globalAlpha = 1; }
    return;
  }
  if (p.boost > 0) for (let k = 1; k <= 2; k++) { ctx.globalAlpha = 0.25 / k; draw(ctx, name, i, fx - p.vx * 0.025 * k, fy, p.dir); }
  ctx.globalAlpha = 1;
  if (!draw(ctx, name, i, fx, fy, p.dir)) { ctx.fillStyle = '#fff'; ctx.fillRect(p.x, p.y, p.w, p.h); }
  // the can in the raised hand
  if (p.act && p.act.type === 'drink') {
    const s = SPR[name], m = s && s.meta && s.meta[((i % s.frames) + s.frames) % s.frames];
    const hand = metaPoint(name, i, 6, fx, fy, p.dir), item = SPR[ITEM_SPR[p.act.item]];
    if (hand && item) { ctx.save(); ctx.translate(Math.round(hand[0]), Math.round(hand[1])); ctx.scale(p.dir, 1); ctx.rotate(-(m ? m[8] : 0)); ctx.drawImage(item.img, 0, 0, item.w, item.h, -Math.round(item.w / 2), -Math.round(item.h * 0.65), item.w, item.h); ctx.restore(); }
  }
  // DJ headphones on the ear
  if (p.djMode > 0) {
    const ear = metaPoint(name, i, 4, fx, fy, p.dir), top = metaPoint(name, i, 2, fx, fy, p.dir);
    if (ear && top) {
      const ex = Math.round(ear[0]), ey = Math.round(ear[1]), ty = Math.round(top[1]);
      ctx.fillStyle = OL; ctx.fillRect(ex - 3, ty - 2, 6, 2); ctx.fillRect(ex - 1, ty, 2, ey - ty - 2); ctx.fillRect(ex - 3, ey - 3, 5, 7);
      ctx.fillStyle = '#3a7bff'; ctx.fillRect(ex - 2, ey - 2, 3, 5); ctx.fillStyle = '#43e0ff'; ctx.fillRect(ex - 2, ey - 2, 1, 1);
    }
  }
}

let GHOST = null;
function ghost() {
  if (GHOST) return GHOST;
  const rows = ['....#####.....', '..##wwwww##...', '.#wwwwwwwww#..', '#wwnnwwwnnww#.', '#wwnnwwwnnww#.', '#wwwwwwwwwww#.', '#wwwwnnnwwww#.', '#wwwwwwwwwww#.', '#wwwwwwwwwww#.', '#ww#ww#ww#ww#.', '.##.##.##.##..'];
  GHOST = document.createElement('canvas'); GHOST.width = 14; GHOST.height = rows.length;
  const g = GHOST.getContext('2d');
  rows.forEach((r, y) => { for (let x = 0; x < r.length; x++) { const c = { '#': OL, w: '#f4f4ff', n: OL }[r[x]]; if (c) { g.fillStyle = c; g.fillRect(x, y, 1, 1); } } });
  return GHOST;
}
function drawShots(ctx) {
  for (const s of ents.shots) {
    if (s.kind === 'disc') { if (!draw(ctx, 'disc_spin', frameAt('disc_spin', s.t * 2), s.x, s.y + 6)) { ctx.fillStyle = '#222'; ctx.fillRect(s.x - 5, s.y - 5, 10, 10); } }
    else if (!draw(ctx, 'note', frameAt('note', s.t), s.x, s.y + 6, Math.sign(s.vx))) { ctx.fillStyle = '#43e0ff'; ctx.fillRect(s.x - 3, s.y - 5, 6, 10); }
  }
  for (const b of ents.bad) {
    if (b.kind === 'slipper') { if (!draw(ctx, 'slipper_spin', frameAt('slipper_spin', b.t * 2), b.x, b.y + 3)) { ctx.fillStyle = '#2a8a4a'; ctx.fillRect(b.x - 4, b.y - 2, 8, 4); } }
    else if (!draw(ctx, 'poop', 0, b.x, b.y + 3)) { ctx.fillStyle = OL; ctx.fillRect(b.x - 2, b.y - 2, 5, 5); ctx.fillStyle = '#f4f4ec'; ctx.fillRect(b.x - 1, b.y - 1, 3, 3); }
  }
}

function drawFx(ctx) {
  for (const f of ents.fx) {
    if (f.name === 'wave') {
      const n = 48;
      for (let k = 0; k < n; k++) { const a = k / n * Math.PI * 2; ctx.fillStyle = k % 3 ? '#3a7bff' : '#43e0ff'; ctx.fillRect(Math.round(f.x + Math.cos(a) * f.r), Math.round(f.y + Math.sin(a) * f.r * 0.6), 3, 3); }
      continue;
    }
    draw(ctx, f.name, Math.floor(f.t * (SPR[f.name] ? SPR[f.name].fps : 10)), f.x, f.y + (SPR[f.name] ? SPR[f.name].h - SPR[f.name].anchor[1] : 0), f.dir);
  }
  for (const q of ents.parts) {
    if (q.smoke && q.life / q.max < 0.3 && Math.floor(q.life * 30) % 2) continue;
    const s = q.smoke ? Math.max(2, Math.round(q.sz * (0.7 + (1 - q.life / q.max)))) : q.sz;
    ctx.fillStyle = q.c; ctx.fillRect(Math.round(q.x - s / 2), Math.round(q.y - s / 2), s, s);
  }
  for (const t of ents.texts) { if (t.life < 0.2 && Math.floor(t.life * 20) % 2) continue; txt(ctx, t.s, t.x, t.y, t.c, 'center'); }
}

// ---------- HUD ----------
function heart(ctx, x, y, full) {
  const rows = ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...'];
  rows.forEach((r, j) => { for (let k = 0; k < r.length; k++) if (r[k] === '#') { ctx.fillStyle = full ? (j === 1 && k === 1 ? '#ffb0b8' : '#e8283c') : '#3a2a44'; ctx.fillRect(x + k, y + j, 1, 1); } });
  ctx.fillStyle = OL;
}
// room the DOM pause/mute buttons take on the right, in game pixels
let hudInset = 8;
export function setHudInset(n) { hudInset = n; }
function drawHUD(ctx) {
  const p = P;
  // panel
  ctx.fillStyle = 'rgba(26,16,36,0.55)'; ctx.fillRect(4, 4, 136, 30);
  for (let k = 0; k < 3; k++) heart(ctx, 9 + k * 10, 9, k < p.hearts);
  txt(ctx, 'x' + getLives(), 41, 7, '#fff');
  // DJ meter
  const full = p.dj >= 1, w = 80;
  ctx.fillStyle = OL; ctx.fillRect(8, 21, w + 2, 8);
  ctx.fillStyle = '#2a2040'; ctx.fillRect(9, 22, w, 6);
  const v = p.djMode > 0 ? p.djMode / 10 : p.dj;
  ctx.fillStyle = p.djMode > 0 ? '#43e0ff' : full && Math.floor(G.t * 6) % 2 ? '#ffffff' : '#ffd23a'; ctx.fillRect(9, 22, Math.round(w * v), 6);
  txt(ctx, p.djMode > 0 ? 'DJ!' : full ? 'C=DJ' : 'DJ', 94, 21, p.djMode > 0 ? '#43e0ff' : full ? '#ffffff' : '#8fd0ff');
  // score + counters
  txt(ctx, String(score.pts).padStart(6, '0'), VIEW.w / 2, 7, '#ffffff', 'center');
  let x = VIEW.w - hudInset;
  for (const k of ['shampoo', 'terea', 'vip', 'rush', 'boom']) {
    const s = SPR[ITEM_SPR[k]], n = String(score.items[k]);
    const im = textImg(n, '#fff'); x -= im.width; ctx.drawImage(im, x, 9); x -= 2;
    if (s) { const sc = 0.5; x -= Math.ceil(s.w * sc); ctx.drawImage(s.img, 0, 0, s.w, s.h, x, 5, Math.ceil(s.w * sc), Math.ceil(s.h * sc)); }
    x -= 8;
  }
  if (G.intro > 0) {
    const L = LEVELS[G.levelIndex], a = Math.min(1, G.intro * 2);
    ctx.globalAlpha = a;
    ctx.fillStyle = 'rgba(26,16,36,0.75)'; ctx.fillRect(0, 96, VIEW.w, 40);
    txt(ctx, `УРОВЕНЬ ${G.levelIndex + 1}`, VIEW.w / 2, 102, '#ffd23a', 'center');
    txt(ctx, L.name, VIEW.w / 2, 116, '#ffffff', 'center', 16);
    ctx.globalAlpha = 1;
  }
}

export function render(ctx) {
  const W = G.world, world = WORLD[LEVELS[G.levelIndex].id];
  ctx.imageSmoothingEnabled = false;
  drawBackground(ctx, world);
  if (!W || !P) return;
  ctx.save();
  const sx = cam.shake > 0 ? Math.round((Math.random() - 0.5) * 6 * cam.shake / 0.2) : 0;
  ctx.translate(-Math.round(cam.x) + sx, -Math.round(cam.y));
  drawTiles(ctx, W, world);
  drawEntities(ctx);
  drawPlayer(ctx);
  drawShots(ctx);
  drawFx(ctx);
  ctx.restore();
  drawHUD(ctx);
}
