import { World, moveBox, standing, T } from './world.js';
import { LEVELS } from './levels.js';
import { SPR, metaPoint } from './assets.js';
import { input } from './input.js';
import { sfx, voice, voiceLength } from './audio.js';

// ---------------- tuning ----------------
const RUN = 150, BOOST_RUN = 215, ACC = 1300, DEC = 1600, AIR_ACC = 900;
const JUMP_V = 375, JUMP_CUT = 130, GRAV = 1150, MAX_FALL = 470, COYOTE = 0.1, BUFFER = 0.13;
const DJ_TIME = 10, HEARTS = 3, LIVES = 3;
const ITEM = {
  b: { kind: 'boom', act: 'drink', pts: 10, label: 'BOOM!' },
  r: { kind: 'rush', act: 'drink', pts: 15, label: 'RUSH!' },
  v: { kind: 'vip', act: 'smoke', pts: 25, label: '+25' },
  t: { kind: 'terea', act: 'vape', pts: 25, label: '+25' },
  s: { kind: 'shampoo', act: 'talk', pts: 40, label: 'SHAMPOO!' }
};
const ACT_DUR = { drink: 1.05, smoke: 1.75, vape: 1.2 };
export const FOE = {
  d: { kind: 'dog', w: 26, h: 18, pts: 50, label: 'ГАВ!' },
  p: { kind: 'pigeon', w: 16, h: 12, pts: 40, label: 'КУРЛЫ!' },
  g: { kind: 'granny', w: 16, h: 36, pts: 75, label: 'ВАЙ!' },
  k: { kind: 'courier', w: 28, h: 34, pts: 100, label: 'ДОСТАВКА!' }
};

export const G = { state: 'menu', hero: 'azat', levelIndex: 0, world: null, t: 0 };
export let P = null;                      // the player
export let ents = { items: [], foes: [], shots: [], bad: [], fx: [], parts: [], texts: [], flags: [], decor: [] };
export const cam = { x: 0, y: 0, look: 0, shake: 0 };
export const score = { pts: 0, items: { boom: 0, rush: 0, vip: 0, terea: 0, shampoo: 0 }, foes: 0, time: 0 };
export let events = [];                    // ui notifications: {type, ...}
let lives = LIVES;
export const getLives = () => lives;

export function newRun(hero, levelIndex = 0) {
  G.hero = hero; lives = LIVES;
  score.pts = 0; score.foes = 0; score.time = 0; for (const k in score.items) score.items[k] = 0;
  startLevel(levelIndex);
}

export function startLevel(i) {
  G.levelIndex = i; G.world = new World(LEVELS[i]); G.t = 0; G.finishX = G.world.w; G.levelTime = 0;
  ents = { items: [], foes: [], shots: [], bad: [], fx: [], parts: [], texts: [], flags: [], decor: [] };
  let start = { x: 40, y: 13 * T };
  for (const s of G.world.spawns) {
    if (s.ch === 'P') start = s;
    else if (ITEM[s.ch]) ents.items.push(Object.assign({ x: s.x, y: s.y - 10, t: Math.random() * 3 }, ITEM[s.ch]));
    else if (FOE[s.ch]) ents.foes.push(makeFoe(s.ch, s.x, s.y));
    else if (s.ch === 'F') ents.flags.push({ x: s.x, y: s.y, on: false, t: 0 });
    else if (s.ch === 'E') G.finishX = s.x;
    else ents.decor.push({ ch: s.ch, x: s.x, y: s.y });
  }
  G.car = { x: start.x + 6, y: start.y };
  G.checkpoint = { x: start.x + 70, y: start.y };
  spawnPlayer(G.checkpoint.x, G.checkpoint.y, true);
  cam.x = Math.max(0, P.x - 140); cam.look = 0;
  G.state = 'play'; G.intro = 2.2;
  events.push({ type: 'level', name: LEVELS[i].name, n: i + 1 });
}

function spawnPlayer(x, y, fresh) {
  const keep = P ? { dj: P.dj } : { dj: 0 };
  P = { x: x - 7, y: y - 44, w: 14, h: 44, vx: 0, vy: 0, dir: 1, onGround: true, coyote: 0, buffer: 0, hearts: HEARTS,
    inv: fresh ? 0 : 1.5, dj: fresh ? 0 : keep.dj, djMode: 0, djIntro: 0, act: null, boost: 0, shoot: 0, shootCD: 0,
    land: 0, crouch: false, idle: 0, dist: 0, dead: 0, hurt: 0, stretch: 1 };
}

function makeFoe(ch, x, y) {
  const F = FOE[ch];
  const e = { ...F, ch, x: x - F.w / 2, y: y - F.h, vx: 0, vy: 0, dir: -1, t: Math.random() * 2, alive: true, dead: 0, cd: 1 + Math.random(), onGround: false };
  if (e.kind === 'dog') e.vx = -40;
  if (e.kind === 'granny') e.vx = -16;
  if (e.kind === 'pigeon') { e.x0 = e.x; e.y0 = e.y - 8; e.range = 40 + Math.random() * 30; }
  if (e.kind === 'courier') e.wait = true;
  return e;
}

// ---------------- helpers ----------------
const overlap = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
export function text(x, y, s, c = '#fff', life = 0.9) { ents.texts.push({ x, y, s, c, life, max: life }); }
export function fx(name, x, y, o = {}) { ents.fx.push(Object.assign({ name, x, y, t: 0, dir: 1 }, o)); }
function part(o) { ents.parts.push(Object.assign({ vx: 0, vy: 0, g: 0, life: 0.6, sz: 2, c: '#fff' }, o, { max: o.life || 0.6 })); }
function burst(x, y, n, cols, sp = 80) { for (let i = 0; i < n; i++) part({ x, y, vx: (Math.random() - 0.5) * sp * 2, vy: -Math.random() * sp - 20, g: 400, life: 0.4 + Math.random() * 0.4, c: cols[i % cols.length], sz: Math.random() < 0.4 ? 3 : 2 }); }
function addPts(n, x, y, label, c) { score.pts += n; text(x, y, label || '+' + n, c); }
const heroAnim = a => `hero_${G.hero}_${a}`;

// ---------------- update ----------------
export function update(dt) {
  if (G.state !== 'play' && G.state !== 'dying' && G.state !== 'clear') return;
  G.t += dt;
  if (G.intro > 0) G.intro -= dt;
  if (G.state === 'play') { G.levelTime += dt; score.time += dt; }
  updatePlayer(dt);
  updateFoes(dt);
  updateShots(dt);
  updateItems(dt);
  updateFx(dt);
  updateCamera(dt);
}

function updatePlayer(dt) {
  const p = P, I = input.held, W = G.world;
  if (G.state === 'dying') {
    p.dead += dt; p.vy += GRAV * dt; p.y += p.vy * dt * (p.pit ? 0 : 1);
    const gy = W.groundY(p.x + p.w / 2, p.y); if (!p.pit && gy > 0 && p.y + p.h > gy) { p.y = gy - p.h; p.vy = 0; }
    if (p.dead > 1.6) {
      if (lives <= 0) { G.state = 'over'; events.push({ type: 'over' }); }
      else { spawnPlayer(G.checkpoint.x, G.checkpoint.y, false); G.state = 'play'; }
    }
    return;
  }
  if (G.state === 'clear') { p.vx = Math.min(p.vx + ACC * dt, 90); p.dir = 1; p.vy += GRAV * dt; moveBox(W, p, dt); p.dist += Math.abs(p.vx) * dt; return; }

  const busy = p.act || p.djIntro > 0;
  // horizontal
  const want = (I.right ? 1 : 0) - (I.left ? 1 : 0);
  p.crouch = I.down && p.onGround && !p.act;
  const max = p.crouch ? 0 : p.boost > 0 ? BOOST_RUN : RUN;
  if (p.djIntro > 0) p.vx *= 0.8;
  else if (want) {
    const a = p.onGround ? (Math.sign(p.vx) === -want ? DEC + ACC : ACC) : AIR_ACC;
    p.vx += want * a * dt; if (Math.abs(p.vx) > max) p.vx = Math.sign(p.vx) * Math.max(max, Math.abs(p.vx) - DEC * dt);
    p.dir = want;
  } else {
    const d = (p.onGround ? DEC : AIR_ACC * 0.5) * dt; p.vx = Math.abs(p.vx) <= d ? 0 : p.vx - Math.sign(p.vx) * d;
  }
  if (p.crouch) p.vx *= 0.85;
  // jump: coyote time + input buffer, variable height; down+jump drops through a ledge
  p.coyote = p.onGround ? COYOTE : p.coyote - dt;
  p.buffer = input.pressed.jump ? BUFFER : p.buffer - dt;
  if (p.buffer > 0 && I.down && p.onGround && onLedge(p)) { p.dropThrough = 0.25; p.buffer = 0; }
  else if (p.buffer > 0 && p.coyote > 0 && p.djIntro <= 0) {
    p.vy = -JUMP_V * (p.boost > 0 ? 1.06 : 1); p.onGround = false; p.coyote = 0; p.buffer = 0; p.stretch = 1.25;
    sfx('jump'); dust(p.x + p.w / 2, p.y + p.h, 4);
  }
  if (!I.jump && p.vy < -JUMP_CUT) p.vy = -JUMP_CUT;
  p.vy = Math.min(MAX_FALL, p.vy + GRAV * dt);
  if (p.dropThrough > 0) p.dropThrough -= dt;
  const wasGround = p.onGround, vy0 = p.vy;
  p.dropThrough = p.dropThrough > 0 ? p.dropThrough : 0;
  moveBox(W, p, dt);
  if (!p.onGround && p.vy >= 0 && standing(W, p)) p.onGround = true;
  if (p.onGround && !wasGround && vy0 > 200) { p.land = 0.12; p.stretch = 0.8; sfx('land'); dust(p.x + p.w / 2, p.y + p.h, 6); }
  p.dist += Math.abs(p.vx) * dt;
  p.stretch += (1 - p.stretch) * Math.min(1, dt * 12);
  for (const k of ['land', 'inv', 'boost', 'shoot', 'shootCD', 'djIntro', 'hurt']) if (p[k] > 0) p[k] -= dt;
  p.idle = p.onGround && Math.abs(p.vx) < 5 && !p.act && !p.crouch ? p.idle + dt : 0;
  if (p.boost > 0 && Math.random() < dt * 30) part({ x: p.x + p.w / 2 - p.dir * 8, y: p.y + 10 + Math.random() * 30, vx: -p.dir * 40, life: 0.3, c: Math.random() < 0.5 ? '#ffd23a' : '#ff8a1e' });

  // pickup actions
  if (p.act) {
    const A = p.act; A.t += dt;
    const n = SPR[heroAnim(A.type)] ? SPR[heroAnim(A.type)].frames : 4, fi = Math.min(n - 1, Math.floor(A.t / A.dur * n));
    if (A.type === 'smoke' && fi === 2 && !A.lit) { A.lit = true; sfx('lighter'); }
    const mouth = mouthPoint();
    if ((A.type === 'smoke' && fi >= 3 || A.type === 'vape' && fi >= 1) && fi < n - 1 && mouth && Math.random() < dt * 12)
      part({ x: mouth[0] + p.dir * 6, y: mouth[1], vx: p.dir * 8, vy: -16, g: -20, life: 0.8, c: A.type === 'vape' ? '#ffffff' : '#c8c4d0', sz: 2, smoke: 1 });
    if ((A.type === 'smoke' || A.type === 'vape') && fi === n - 1 && !A.puffed && mouth) {
      A.puffed = true; sfx('puff');
      for (let i = 0; i < 10; i++) part({ x: mouth[0], y: mouth[1], vx: p.dir * (30 + Math.random() * 50), vy: -10 - Math.random() * 25, g: -25, life: 0.9 + Math.random() * 0.4, c: A.type === 'vape' ? '#ffffff' : '#d6d2de', sz: 3, smoke: 1 });
    }
    if (A.type === 'drink' && fi >= 2 && !A.gulped) { A.gulped = true; sfx('gulp'); }
    if (A.type === 'talk' && Math.random() < dt * 20) part({ x: p.x + p.w / 2 + (Math.random() - 0.5) * 30, y: p.y + Math.random() * 20, vy: -30, g: -20, life: 0.8, c: Math.random() < 0.5 ? '#ffffff' : '#8fd0ff', sz: 2 });
    if (A.t >= A.dur) { if (A.after) A.after(); p.act = null; }
  }

  // DJ mode
  if (p.djMode > 0) { p.djMode -= dt; if (p.djMode <= 0) text(p.x + p.w / 2, p.y - 8, 'DJ OFF', '#8fd0ff'); }
  if (input.pressed.dj && p.dj >= 1 && p.djMode <= 0) startDJ();
  if (input.pressed.fire) {
    if (p.djMode > 0 && p.shootCD <= 0 && p.djIntro <= 0) shoot();
    else if (p.djMode <= 0) events.push({ type: 'needdj' });
  }

  // pits
  if (p.y > W.h + 20) { p.pit = true; loseLife('fall'); }
  // checkpoints and finish
  for (const f of ents.flags) if (!f.on && p.x + p.w > f.x - 6) {
    f.on = true; G.checkpoint = { x: f.x, y: f.y }; sfx('flag'); text(f.x, f.y - 66, 'ЧЕКПОИНТ', '#ffd23a', 1.4);
    burst(f.x, f.y - 50, 14, ['#d90012', '#0033a0', '#f2a800']);
    if (p.hearts < HEARTS) p.hearts = HEARTS;
  }
  if (G.state === 'play' && p.x > G.finishX) levelClear();
}

const onLedge = p => { const ty = Math.floor((p.y + p.h + 1) / T); let any = false; for (let tx = Math.floor((p.x + 1) / T); tx <= Math.floor((p.x + p.w - 2) / T); tx++) { const t = G.world.at(tx, ty); if (t === 1 || t === 2 || t === 4) return false; if (t === 3) any = true; } return any; };

export function playerAnim() {
  const p = P, A = p.act;
  if (G.state === 'dying') return ['dead', 0];
  if (p.hurt > 0) return ['hurt', 0];
  if (!p.onGround) return p.vy < -120 ? ['jump', 0] : p.vy < 60 ? ['jump', 1] : p.vy < 240 ? ['fall', 0] : ['fall', 1];
  if (p.djIntro > 0) return ['drop', Math.floor(G.t * 6)];
  if (p.shoot > 0) { const n = SPR[heroAnim('shoot')] ? SPR[heroAnim('shoot')].frames : 3; return ['shoot', Math.min(n - 1, Math.floor((1 - p.shoot / 0.24) * n))]; }
  // pickups never slow him down: on the move he keeps running and the can goes to his mouth (see render)
  if (A && Math.abs(p.vx) < 40) { const s = SPR[heroAnim(A.type)], n = s ? s.frames : 2; return [A.type, A.type === 'talk' ? Math.floor(A.t * 11) : Math.min(n - 1, Math.floor(A.t / A.dur * n))]; }
  if (p.crouch) return ['crouch', 0];
  if (p.land > 0) return ['land', 0];
  if (Math.abs(p.vx) > 100) return ['run', Math.floor(p.dist / 11)];
  if (Math.abs(p.vx) > 8) return ['walk', Math.floor(p.dist / 8)];
  if (p.idle > 4) return ['chill', Math.floor(p.idle * 2.5)];
  return ['idle', Math.floor(G.t * 2.6)];
}
export function heroFeet() { return [P.x + P.w / 2, P.y + P.h]; }
export function mouthPoint() { const [a, i] = playerAnim(), [fx2, fy] = heroFeet(); return metaPoint(heroAnim(a), i, 0, fx2, fy, P.dir); }

function startDJ() {
  const p = P; p.dj = 0; p.djMode = DJ_TIME; p.djIntro = 0.7; p.act = null;
  sfx('dj'); cam.shake = 0.25; events.push({ type: 'dj' });
  text(p.x + p.w / 2, p.y - 12, 'DJ MODE!', '#43e0ff', 1.2);
  // the drop: a shock wave that knocks out everything close
  ents.fx.push({ name: 'wave', x: p.x + p.w / 2, y: p.y + p.h / 2, t: 0, r: 0 });
}
function shoot() {
  const p = P; p.shoot = 0.24; p.shootCD = 0.28; sfx('shoot');
  const x = p.x + p.w / 2 + p.dir * 18, y = p.y + 16;
  if (G.hero === 'azat') ents.shots.push({ kind: 'disc', x, y, vx: p.dir * 330 + p.vx * 0.3, vy: -20, t: 0 });
  else ents.shots.push({ kind: 'note', x, y, vx: p.dir * 280 + p.vx * 0.3, vy: 0, t: 0 });
}

function hurtPlayer(fromX, why) {
  const p = P;
  if (p.inv > 0 || G.state !== 'play') return;
  p.hearts--; p.inv = 1.5; p.hurt = 0.35; p.act = null; p.vy = -240; p.vx = (p.x + p.w / 2 < fromX ? -1 : 1) * 160;
  cam.shake = 0.2; sfx('hurt'); G.hurtBy = why;
  if (p.hearts <= 0) loseLife(why);
}
function loseLife(why) {
  if (G.state !== 'play') return;
  lives--; G.state = 'dying'; P.dead = 0; P.vx = 0; P.vy = P.pit ? 0 : -300; G.lastDeath = why;
  sfx(why === 'fall' ? 'fall' : 'over'); events.push({ type: 'died', why });
}
function levelClear() {
  G.state = 'clear'; sfx('win'); score.pts += P.hearts * 100;
  for (let i = 0; i < 5; i++) setTimeout(() => fx('fx_boom', G.finishX + 20 + i * 24, 120 + (i % 2) * 30), i * 150);
  try { const k = 'shampoo2_unlocked', u = +localStorage.getItem(k) || 0; if (G.levelIndex + 1 > u) localStorage.setItem(k, G.levelIndex + 1); } catch (e) {}
  setTimeout(() => events.push({ type: 'clear', level: G.levelIndex, time: G.levelTime }), 1400);
}

// ---------------- items ----------------
function updateItems(dt) {
  const p = P;
  for (const it of ents.items) {
    it.t += dt;
    if (it.got || G.state !== 'play') continue;
    if (Math.abs(it.x - (p.x + p.w / 2)) < 14 && it.y > p.y - 6 && it.y < p.y + p.h + 8) collect(it);
  }
  ents.items = ents.items.filter(i => !i.got);
}
function collect(it) {
  const p = P; it.got = true;
  score.items[it.kind]++; addPts(it.pts, it.x, it.y - 16, it.label, '#ffd23a');
  if (p.djMode <= 0) { p.dj = Math.min(1, p.dj + 0.2); if (p.dj >= 1) events.push({ type: 'djready' }); }
  burst(it.x, it.y, 10, ['#ffffff', '#ffd23a', '#8fd0ff']);
  events.push({ type: 'item', kind: it.kind });
  if (it.act === 'drink') { sfx('can'); p.act = { type: 'drink', t: 0, dur: ACT_DUR.drink, item: it.kind, after: () => { p.boost = it.kind === 'rush' ? 3.5 : 2.5; text(p.x + p.w / 2, p.y - 8, 'ТУРБО!', '#ff8a1e'); } }; }
  else if (it.act === 'talk') { p.act = { type: 'talk', t: 0, dur: Math.max(0.9, voiceLength('shampoo')) }; voice('shampoo'); }
  else { sfx('pack'); p.act = { type: it.act, t: 0, dur: ACT_DUR[it.act] }; }
}

// ---------------- enemies ----------------
function updateFoes(dt) {
  const p = P, W = G.world, px = p.x + p.w / 2;
  for (const e of ents.foes) {
    if (!e.alive) { e.dead += dt; e.vy += GRAV * dt; e.y += e.vy * dt; e.x += e.vx * dt; continue; }
    if (Math.abs(e.x - p.x) > 520) continue;
    e.t += dt; e.cd -= dt;
    const dx = px - (e.x + e.w / 2);
    if (e.kind === 'pigeon') {
      const nx = e.x0 + Math.sin(e.t * 0.9) * e.range; e.dir = nx > e.x ? 1 : -1; e.x = nx;
      e.y = e.y0 + Math.sin(e.t * 5) * 3 + Math.sin(e.t * 1.7) * 6;
      if (e.cd <= 0 && Math.abs(dx) < 24 && p.y > e.y) { e.cd = 1.6; ents.bad.push({ kind: 'poop', x: e.x + e.w / 2, y: e.y + e.h, vx: 0, vy: 30, t: 0 }); sfx('coo'); }
    } else {
      if (e.kind === 'dog') {
        const sees = Math.abs(dx) < 130 && Math.abs(p.y + p.h - (e.y + e.h)) < 30;
        const sp = sees ? 105 : 40;
        if (sees && Math.sign(dx) !== Math.sign(e.vx) && e.cd <= 0) { e.vx = Math.sign(dx) * sp; e.cd = 0.8; sfx('bark'); text(e.x + e.w / 2, e.y - 6, 'ГАВ!', '#fff', 0.5); }
        e.vx = Math.sign(e.vx || -1) * sp;
      } else if (e.kind === 'granny') {
        e.vx = Math.sign(e.vx || -1) * 16;
        if (e.throwT > 0) {
          e.throwT -= dt; e.vx = 0;
          // the slipper leaves the hand on the release frame of the throw strip
          if (!e.thrown && e.throwT <= 0.3) {
            e.thrown = true;
            const s = SPR.granny_throw, an = s ? s.anchor : [12, 45], hd = (s && s.hand) || [26, 19];
            const sx = e.x + e.w / 2 + (hd[0] - an[0]) * e.dir, sy = e.y + e.h + 1 + hd[1] - an[1], tt = 0.85;
            ents.bad.push({ kind: 'slipper', x: sx, y: sy, vx: (e.tx - sx) / tt, vy: (e.ty - sy) / tt - 0.5 * GRAV * 0.5 * tt, g: GRAV * 0.5, t: 0 }); sfx('throw');
          }
        }
        if (Math.abs(dx) < 190 && Math.abs(dx) > 24 && e.cd <= 0) {
          e.cd = 2.6; e.throwT = 0.45; e.vx = Math.sign(dx) * 0.01; e.dir = Math.sign(dx);
          e.thrown = false; e.tx = px; e.ty = p.y + 10;
          text(e.x + e.w / 2, e.y - 8, 'ЭЙ!', '#ff8a8a', 0.6);
        }
      } else if (e.kind === 'courier') {
        if (e.wait) { if (dx > -300 && dx < 0) { e.wait = false; e.vx = -150; text(e.x, e.y - 8, 'БИП-БИП!', '#ffd23a', 0.8); } else continue; }
        e.vx = Math.sign(e.vx) * 150;
      }
      e.vy = Math.min(MAX_FALL, e.vy + GRAV * dt);
      // turn at walls and ledge ends (the courier just rides on)
      const ahead = e.vx > 0 ? e.x + e.w + 2 : e.x - 2, footY = e.y + e.h + 2;
      if (e.onGround && e.kind !== 'courier' && Math.abs(e.vx) > 1 && !W.at(Math.floor(ahead / T), Math.floor(footY / T))) e.vx = -e.vx;
      moveBox(W, e, dt);
      if (e.hitWall) e.vx = -e.hitWall * (e.kind === 'courier' ? 150 : 40);
      if (Math.abs(e.vx) > 1) e.dir = Math.sign(e.vx);
      if (e.y > W.h + 40) { e.alive = false; e.dead = 9; }
    }
    // contact with the player: a stomp from above kills, anything else hurts (pigeons only hurt with what they drop)
    if (G.state === 'play' && overlap(p, e)) {
      if (p.vy > 30 && p.y + p.h - p.vy * dt <= e.y + 8) {
        killFoe(e, true); p.vy = input.held.jump ? -440 : -300; p.stretch = 1.3;
      } else if (e.kind !== 'pigeon') hurtPlayer(e.x + e.w / 2, e.kind);
    }
  }
  ents.foes = ents.foes.filter(e => e.dead < 2.5);
}
export function killFoe(e, stomp) {
  e.alive = false; e.vy = -220; e.vx = (e.x > P.x ? 1 : -1) * 60; e.dead = 0; score.foes++;
  addPts(e.pts, e.x + e.w / 2, e.y - 8, `${e.label} +${e.pts}`, '#ffffff');
  sfx('stomp'); cam.shake = Math.max(cam.shake, 0.08);
  fx('fx_hit', e.x + e.w / 2, e.y + e.h / 2);
  if (e.kind === 'pigeon') burst(e.x + 8, e.y + 6, 10, ['#c8ccd8', '#8f96ae', '#ffffff']);
  if (P.djMode <= 0) { P.dj = Math.min(1, P.dj + 0.1); if (P.dj >= 1) events.push({ type: 'djready' }); }
  G.hitstop = stomp ? 0.05 : 0.03;
}

// ---------------- projectiles ----------------
function updateShots(dt) {
  const W = G.world, p = P;
  for (const s of ents.shots) {
    s.t += dt; s.x += s.vx * dt; s.y += s.vy * dt;
    if (s.kind === 'note') s.y += Math.sin(s.t * 18) * 1.2;
    if (W.solid(Math.floor(s.x / T), Math.floor(s.y / T))) { s.t = 9; fx('fx_hit', s.x, s.y); }
    for (const e of ents.foes) if (e.alive && s.x > e.x - 4 && s.x < e.x + e.w + 4 && s.y > e.y - 4 && s.y < e.y + e.h + 4) { killFoe(e, false); s.t = 9; break; }
  }
  ents.shots = ents.shots.filter(s => s.t < 1.4);
  for (const b of ents.bad) {
    b.t += dt; b.vy += (b.g || 300) * dt; b.x += b.vx * dt; b.y += b.vy * dt;
    if (G.state === 'play' && b.x > p.x - 3 && b.x < p.x + p.w + 3 && b.y > p.y && b.y < p.y + p.h) {
      if (b.kind === 'poop') text(p.x + p.w / 2, p.y - 8, 'ФУУ!', '#f4f4ec', 0.8);
      hurtPlayer(b.x - b.vx, b.kind); b.t = 9;
    }
    if (W.solid(Math.floor(b.x / T), Math.floor(b.y / T))) { b.t = 9; if (b.kind === 'poop') { fx('poop_splat', b.x, Math.floor(b.y / T) * T); sfx('splat'); } else dust(b.x, b.y, 3); }
  }
  ents.bad = ents.bad.filter(b => b.t < 3);
}

// ---------------- fx ----------------
export function dust(x, y, n) { fx('fx_dust', x, y); for (let i = 0; i < n; i++) part({ x: x + (Math.random() - 0.5) * 10, y: y - 1, vx: (Math.random() - 0.5) * 60, vy: -Math.random() * 30, g: 80, life: 0.35, c: '#e8dcc8', sz: 2 }); }
function updateFx(dt) {
  for (const f of ents.fx) {
    f.t += dt;
    if (f.name === 'wave') {
      f.r += 360 * dt;
      for (const e of ents.foes) if (e.alive && Math.hypot(e.x + e.w / 2 - f.x, e.y + e.h / 2 - f.y) < f.r) killFoe(e, false);
    }
  }
  ents.fx = ents.fx.filter(f => (f.name === 'wave' ? f.r < 220 : !SPR[f.name] || f.t < SPR[f.name].frames / SPR[f.name].fps));
  for (const q of ents.parts) { q.life -= dt; q.vy += q.g * dt; q.x += q.vx * dt; q.y += q.vy * dt; }
  ents.parts = ents.parts.filter(q => q.life > 0);
  for (const t of ents.texts) { t.life -= dt; t.y -= 22 * dt; }
  ents.texts = ents.texts.filter(t => t.life > 0);
  if (cam.shake > 0) cam.shake -= dt;
  for (const f of ents.flags) f.t += dt;
}

// ---------------- camera ----------------
export let VIEW = { w: 480, h: 270 };
export function setView(w, h) { VIEW = { w, h }; }
function updateCamera(dt) {
  const p = P, W = G.world;
  cam.look += ((p.dir * 60 + p.vx * 0.25) - cam.look) * Math.min(1, dt * 2.5);
  const target = p.x + p.w / 2 + cam.look - VIEW.w * 0.42;
  cam.x += (target - cam.x) * Math.min(1, dt * 6);
  cam.x = Math.max(0, Math.min(W.w - VIEW.w, cam.x));
  cam.y = W.h - VIEW.h;
}
