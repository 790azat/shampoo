import { buildMap, ROWS } from './levels.js';

export const T = 16;
export const EMPTY = 0, GROUND = 1, BLOCK = 2, LEDGE = 3, CRATE = 4;
const TILE = { '#': GROUND, B: BLOCK, '=': LEDGE, C: CRATE };

// The level grid plus everything placed on it.
export class World {
  constructor(level) {
    this.level = level;
    const rows = buildMap(level);
    this.cols = rows[0].length; this.rows = ROWS;
    this.w = this.cols * T; this.h = this.rows * T;
    this.tiles = new Uint8Array(this.cols * this.rows);
    this.spawns = [];
    for (let y = 0; y < this.rows; y++) for (let x = 0; x < this.cols; x++) {
      const ch = rows[y][x];
      if (TILE[ch]) this.tiles[y * this.cols + x] = TILE[ch];
      else if (ch !== '.') this.spawns.push({ ch, x: x * T + T / 2, y: (y + 1) * T });
    }
  }
  at(tx, ty) {
    if (tx < 0) return BLOCK;                  // the left edge of the level is a wall
    if (tx >= this.cols || ty < 0 || ty >= this.rows) return EMPTY;
    return this.tiles[ty * this.cols + tx];
  }
  solid(tx, ty) { const t = this.at(tx, ty); return t === GROUND || t === BLOCK || t === CRATE; }
  // ground row under a world x (for placing things), or -1 over a pit
  groundY(x, fromY = 0) {
    const tx = Math.floor(x / T);
    for (let ty = Math.max(0, Math.floor(fromY / T)); ty < this.rows; ty++) if (this.at(tx, ty) !== EMPTY) return ty * T;
    return -1;
  }
}

// Move a box {x, y, w, h, vx, vy} through the tiles. Sets onGround / hitWall. One-way ledges only stop a falling box
// whose feet were above the ledge top, unless dropThrough is set.
export function moveBox(world, b, dt) {
  b.hitWall = 0;
  let nx = b.x + b.vx * dt;
  if (b.vx !== 0) {
    const edge = b.vx > 0 ? nx + b.w : nx, tx = Math.floor(edge / T);
    for (let ty = Math.floor(b.y / T); ty <= Math.floor((b.y + b.h - 1) / T); ty++) {
      if (world.solid(tx, ty)) { nx = b.vx > 0 ? tx * T - b.w : (tx + 1) * T; b.hitWall = Math.sign(b.vx); b.vx = 0; break; }
    }
  }
  b.x = nx;
  let ny = b.y + b.vy * dt;
  b.onGround = false;
  if (b.vy > 0) {
    const feet0 = b.y + b.h, feet1 = ny + b.h;
    for (let ty = Math.floor(feet0 / T); ty <= Math.floor((feet1 - 0.01) / T); ty++) {
      let hit = false;
      for (let tx = Math.floor((b.x + 1) / T); tx <= Math.floor((b.x + b.w - 2) / T); tx++) {
        const t = world.at(tx, ty);
        if (t === GROUND || t === BLOCK || t === CRATE || (t === LEDGE && !b.dropThrough && feet0 <= ty * T + 0.5)) { hit = true; break; }
      }
      if (hit) { ny = ty * T - b.h; b.vy = 0; b.onGround = true; break; }
    }
  } else if (b.vy < 0) {
    const ty = Math.floor(ny / T);
    for (let tx = Math.floor((b.x + 1) / T); tx <= Math.floor((b.x + b.w - 2) / T); tx++) {
      if (world.solid(tx, ty)) { ny = (ty + 1) * T; b.vy = 0; b.bonk = true; break; }
    }
  }
  b.y = ny;
}

// is there floor right under this box (used to keep "grounded" stable when standing still)
export function standing(world, b) {
  const ty = Math.floor((b.y + b.h + 1) / T);
  if (Math.abs(b.y + b.h - ty * T) > 1) return false;
  for (let tx = Math.floor((b.x + 1) / T); tx <= Math.floor((b.x + b.w - 2) / T); tx++) if (world.at(tx, ty) !== EMPTY && !(world.at(tx, ty) === LEDGE && b.dropThrough)) return true;
  return false;
}
