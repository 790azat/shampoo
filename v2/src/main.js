import { loadManifest, loadWorld, SPR, draw } from './assets.js';
import { input, pollInput, bindTouch } from './input.js';
import { audioInit, playMusic, setMute, isMuted, sfx } from './audio.js';
import { G, P, update, newRun, startLevel, events, setView, score, getLives, ents } from './game.js';
import { render, setHudInset } from './render.js';
import { LEVELS } from './levels.js';

const $ = id => document.getElementById(id);
const cv = $('c'), mctx = cv.getContext('2d');
const buf = document.createElement('canvas'), ctx = buf.getContext('2d');
let S = 3;

function resize() {
  const dpr = window.devicePixelRatio || 1;
  cv.width = Math.round(innerWidth * dpr); cv.height = Math.round(innerHeight * dpr);
  S = Math.max(1, Math.floor(cv.height / 270));
  // at least 270 game pixels tall (more when the integer scale leaves room, shown as extra sky); width follows the screen
  const vh = Math.ceil(cv.height / S), vw = Math.ceil(cv.width / S);
  buf.width = vw; buf.height = vh; setView(vw, vh);
  setHudInset(Math.ceil(112 * dpr / S));
}
addEventListener('resize', resize); resize();

// ---------------- screens ----------------
const HEROES = ['azat', 'arsen', 'vigen'], NAMES = { azat: 'АЗАТ', arsen: 'АРСЕН', vigen: 'ВИГЕН' };
let heroIdx = 0;
try { heroIdx = Math.max(0, HEROES.indexOf(localStorage.getItem('shampoo2_hero'))); } catch (e) {}
const screens = ['menu', 'levelsScr', 'helpScr', 'pauseScr', 'endScr'];
function show(id) {
  for (const s of screens) $(s).classList.toggle('show', s === id);
  document.body.classList.toggle('playing', !id);
  const b = id && $(id).querySelector('.b.main, .b'); if (b) setTimeout(() => b.focus({ preventScroll: true }), 30);
}
const unlocked = () => { try { return +localStorage.getItem('shampoo2_unlocked') || 0; } catch (e) { return 0; } };
const best = () => { try { return +localStorage.getItem('shampoo2_best') || 0; } catch (e) { return 0; } };
function setHero(i) {
  heroIdx = (i + HEROES.length) % HEROES.length; $('heroName').textContent = NAMES[HEROES[heroIdx]];
  try { localStorage.setItem('shampoo2_hero', HEROES[heroIdx]); } catch (e) {}
}
function refreshMenu() {
  setHero(heroIdx);
  $('best').textContent = best() ? `РЕКОРД: ${String(best()).padStart(6, '0')}` : '';
  const L = $('levelList'); L.innerHTML = '';
  LEVELS.forEach((lv, i) => {
    const b = document.createElement('button'); b.className = 'b'; b.disabled = i > unlocked();
    b.innerHTML = `<span>${i + 1}</span><span>${lv.name}</span>`;
    b.onclick = () => { if (!b.disabled) go(i); }; L.appendChild(b);
  });
}
async function go(level) {
  audioInit(); playMusic(); sfx('click');
  await loadWorld(LEVELS[level].id);
  newRun(HEROES[heroIdx], level); show(null); paused = false;
}
async function goLevel(level) { await loadWorld(LEVELS[level].id); startLevel(level); show(null); paused = false; }

let paused = false;
function pause() { if (G.state !== 'play' && G.state !== 'dying') return; paused = true; show('pauseScr'); }
document.addEventListener('click', e => {
  const b = e.target.closest('[data-act]'); if (!b) return;
  audioInit();
  const a = b.dataset.act;
  if (a === 'play') go(0);
  else if (a === 'prev' || a === 'next') { setHero(heroIdx + (a === 'next' ? 1 : -1)); sfx('click'); }
  else if (a === 'levels') { refreshMenu(); show('levelsScr'); }
  else if (a === 'help') show('helpScr');
  else if (a === 'back') { refreshMenu(); show('menu'); }
  else if (a === 'resume') { paused = false; show(null); }
  else if (a === 'restart') { if (G.state === 'over') go(G.levelIndex); else goLevel(G.levelIndex); }
  else if (a === 'menu') { G.state = 'menu'; paused = false; refreshMenu(); show('menu'); }
  else if (a === 'next2') { if (G.levelIndex + 1 < LEVELS.length) goLevel(G.levelIndex + 1); else { G.state = 'menu'; refreshMenu(); show('menu'); } }
});
$('pauseBtn').onclick = () => pause();
$('muteBtn').onclick = e => { audioInit(); setMute(!isMuted()); e.currentTarget.textContent = isMuted() ? '×' : '♪'; e.currentTarget.blur(); };
$('muteBtn').textContent = isMuted() ? '×' : '♪';
addEventListener('blur', () => pause());
if ('ontouchstart' in window || navigator.maxTouchPoints > 0) document.body.classList.add('touch');
bindTouch($('touch'));

function handleEvents() {
  while (events.length) {
    const e = events.shift();
    if (e.type === 'clear') {
      const last = e.level + 1 >= LEVELS.length;
      $('endTitle').textContent = last ? 'ЕРЕВАН ПРОЙДЕН!' : 'ФИНИШ!';
      const m = Math.floor(e.time / 60), s = Math.floor(e.time % 60);
      $('endStats').innerHTML = `${LEVELS[e.level].name}<br>ВРЕМЯ: ${m}:${String(s).padStart(2, '0')}<br>ВРАГОВ: ${score.foes}<br>ОЧКИ: ${String(score.pts).padStart(6, '0')}`;
      $('nextBtn').style.display = last ? 'none' : '';
      saveBest(); show('endScr');
    } else if (e.type === 'over') {
      $('endTitle').textContent = 'GAME OVER';
      $('endStats').innerHTML = `ОЧКИ: ${String(score.pts).padStart(6, '0')}<br>ВРАГОВ: ${score.foes}`;
      $('nextBtn').style.display = 'none'; saveBest(); show('endScr');
    }
  }
}
function saveBest() { try { if (score.pts > best()) localStorage.setItem('shampoo2_best', score.pts); } catch (e) {} }

// ---------------- menu preview: the chosen hero runs on the spot ----------------
const pv = $('preview').getContext('2d');
function drawPreview(t) {
  if (!$('menu').classList.contains('show')) return;
  pv.clearRect(0, 0, 100, 110); pv.imageSmoothingEnabled = false;
  const h = HEROES[heroIdx], cyc = t % 6, a = cyc < 3 ? 'run' : cyc < 4.5 ? 'idle' : 'smoke';
  const s = SPR[`hero_${h}_${a}`];
  if (s) draw(pv, `hero_${h}_${a}`, a === 'run' ? Math.floor(t * 12) : a === 'idle' ? Math.floor(t * 3) : Math.floor((cyc - 4.5) / 1.5 * s.frames), 50, 104);
}

// ---------------- loop ----------------
const STEP = 1 / 120;
let last = performance.now(), acc = 0;
function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  pollInput();
  if (input.pressed.pause) { if (paused) { paused = false; show(null); } else pause(); }
  if (!paused && G.state !== 'menu') {
    acc += dt;
    while (acc >= STEP) {
      if (G.hitstop > 0) G.hitstop -= STEP; else update(STEP);
      acc -= STEP; pollInputEdgesClear();
    }
    handleEvents();
  }
  if (G.world) { render(ctx); mctx.imageSmoothingEnabled = false; mctx.drawImage(buf, 0, 0, buf.width * S, buf.height * S); }
  else { mctx.fillStyle = '#5ab0f0'; mctx.fillRect(0, 0, cv.width, cv.height); }
  drawPreview(now / 1000);
}
// "pressed" edges are consumed by the first fixed step of a frame
function pollInputEdgesClear() { for (const k in input.pressed) input.pressed[k] = false; }

// ---------------- boot ----------------
(async () => {
  await Promise.all(['heroes', 'vigen', 'actors', 'objects', 'boss'].map(loadManifest));
  // a backdrop for the menu: the first district
  await loadWorld(LEVELS[0].id);
  refreshMenu();
  requestAnimationFrame(frame);
  if (document.fonts) document.fonts.load("8px 'Press Start 2P'");
})();
window.__g = { G, get P() { return P; }, get ents() { return ents; }, input, score, startLevel, newRun, goLevel, get lives() { return getLives(); } };
