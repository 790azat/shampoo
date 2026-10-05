// WebAudio: the 8-bit SpongeBob theme from assets/theme.mp3, the "Shampoo" voice clip and synthesized chip sound effects.
const A = { ctx: null, master: null, music: null, sfx: null, buf: {}, src: null, muted: false };
try { A.muted = localStorage.getItem('shampoo2_mute') === '1'; } catch (e) {}

export function audioInit() {
  if (A.ctx) { if (A.ctx.state === 'suspended') A.ctx.resume(); return; }
  const C = window.AudioContext || window.webkitAudioContext;
  if (!C) return;
  A.ctx = new C();
  A.master = A.ctx.createGain(); A.master.gain.value = A.muted ? 0 : 0.8; A.master.connect(A.ctx.destination);
  A.music = A.ctx.createGain(); A.music.gain.value = 0.55; A.music.connect(A.master);
  A.sfx = A.ctx.createGain(); A.sfx.gain.value = 0.9; A.sfx.connect(A.master);
  for (const n of ['theme', 'shampoo'])
    fetch(`assets/${n}.mp3`).then(r => r.arrayBuffer()).then(b => A.ctx.decodeAudioData(b)).then(d => { A.buf[n] = d; if (n === 'theme' && A.wantMusic) playMusic(); }).catch(() => {});
}

export function playMusic() {
  A.wantMusic = true;
  if (!A.ctx || !A.buf.theme || A.src) return;
  const s = A.ctx.createBufferSource(); s.buffer = A.buf.theme; s.loop = true;
  s.loopStart = 0.5; s.loopEnd = Math.max(1, A.buf.theme.duration - 1.5);
  s.connect(A.music); s.start(); A.src = s;
}
export function setMute(m) {
  A.muted = m;
  try { localStorage.setItem('shampoo2_mute', m ? '1' : '0'); } catch (e) {}
  if (A.master) A.master.gain.setTargetAtTime(m ? 0 : 0.8, A.ctx.currentTime, 0.02);
}
export const isMuted = () => A.muted;
export function duckMusic(on) { if (A.music) A.music.gain.setTargetAtTime(on ? 0.15 : 0.55, A.ctx.currentTime, 0.05); }

export function voice(name) {
  if (!A.ctx || !A.buf[name]) return 0;
  const s = A.ctx.createBufferSource(); s.buffer = A.buf[name]; s.connect(A.sfx); s.start();
  duckMusic(true); setTimeout(() => duckMusic(false), A.buf[name].duration * 1000);
  return A.buf[name].duration;
}
export const voiceLength = name => (A.buf[name] ? A.buf[name].duration : 1.1);

const mf = m => 440 * Math.pow(2, (m - 69) / 12);
function tone(type, f0, f1, t, dur, vol) {
  const o = A.ctx.createOscillator(), g = A.ctx.createGain();
  o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  o.connect(g); g.connect(A.sfx); o.start(t); o.stop(t + dur + 0.02);
}
let noiseBuf = null;
function noise(t, dur, vol, freq) {
  if (!noiseBuf) { noiseBuf = A.ctx.createBuffer(1, A.ctx.sampleRate * 0.5, A.ctx.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }
  const s = A.ctx.createBufferSource(), f = A.ctx.createBiquadFilter(), g = A.ctx.createGain();
  s.buffer = noiseBuf; f.type = 'lowpass'; f.frequency.value = freq;
  g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  s.connect(f); f.connect(g); g.connect(A.sfx); s.start(t); s.stop(t + dur + 0.02);
}

export function sfx(name) {
  if (!A.ctx || A.muted) return;
  const t = A.ctx.currentTime;
  switch (name) {
    case 'jump': tone('square', 260, 620, t, 0.12, 0.16); break;
    case 'land': noise(t, 0.05, 0.15, 600); break;
    case 'can': [0, 4, 7, 12].forEach((n, i) => tone('square', mf(76 + n), mf(76 + n), t + i * 0.045, 0.07, 0.14)); noise(t, 0.3, 0.35, 320); break;
    case 'gulp': for (let i = 0; i < 3; i++) tone('square', 220, 130, t + i * 0.16, 0.08, 0.14); break;
    case 'pack': tone('triangle', mf(81), mf(81), t, 0.06, 0.25); tone('triangle', mf(88), mf(88), t + 0.06, 0.1, 0.25); break;
    case 'lighter': noise(t, 0.04, 0.4, 5000); tone('sawtooth', 1200, 900, t + 0.03, 0.08, 0.05); break;
    case 'puff': noise(t, 0.4, 0.22, 900); break;
    case 'stomp': tone('square', 420, 110, t, 0.12, 0.2); noise(t, 0.08, 0.35, 1500); break;
    case 'hurt': tone('sawtooth', 340, 70, t, 0.3, 0.2); break;
    case 'fall': tone('triangle', 700, 90, t, 0.6, 0.25); break;
    case 'throw': noise(t, 0.08, 0.25, 3000); tone('square', 600, 900, t, 0.06, 0.08); break;
    case 'shoot': tone('square', 900, 300, t, 0.09, 0.12); noise(t, 0.05, 0.2, 4000); break;
    case 'dj': [60, 64, 67, 72, 76, 79].forEach((m, i) => tone('square', mf(m), mf(m), t + i * 0.04, 0.06, 0.14)); tone('sawtooth', 80, 40, t, 0.5, 0.25); noise(t + 0.05, 0.3, 0.25, 4000); break;
    case 'boom': noise(t, 0.5, 0.5, 400); tone('triangle', 120, 30, t, 0.5, 0.4); break;
    case 'flag': [72, 76, 79].forEach((m, i) => tone('square', mf(m), mf(m), t + i * 0.08, 0.1, 0.14)); break;
    case 'click': tone('square', 880, 880, t, 0.04, 0.1); break;
    case 'win': [72, 76, 79, 84, 79, 84].forEach((m, i) => tone('square', mf(m), mf(m), t + i * 0.11, i === 5 ? 0.5 : 0.1, 0.16)); break;
    case 'over': [67, 63, 60, 55].forEach((m, i) => tone('square', mf(m), mf(m), t + i * 0.18, 0.2, 0.16)); break;
    case 'bark': tone('sawtooth', 520, 260, t, 0.08, 0.12); tone('sawtooth', 480, 240, t + 0.12, 0.08, 0.1); break;
    case 'coo': tone('sine', 420, 360, t, 0.18, 0.08); break;
    case 'splat': noise(t, 0.12, 0.3, 700); break;
  }
}
