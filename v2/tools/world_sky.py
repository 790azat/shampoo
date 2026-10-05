"""Shared sky, clouds and Mount Ararat layers."""
import numpy as np
from world_pix import Layer, BAYER4, mix, periodic_noise

SKY_BANDS = [  # (y_start, colour) top -> bottom
    (0, (56, 124, 212)),
    (40, (70, 142, 224)),
    (84, (90, 160, 234)),
    (124, (114, 180, 240)),
    (160, (142, 198, 244)),
    (192, (172, 214, 247)),
    (220, (200, 228, 250)),
]


def draw_sky():
    W, H = 480, 270
    L = Layer(W, H)
    yy, xx = np.mgrid[0:H, 0:W]
    for i, (y0, c) in enumerate(SKY_BANDS):
        y1 = SKY_BANDS[i + 1][0] if i + 1 < len(SKY_BANDS) else H
        L.rect(0, y0, W, y1 - y0, c)
        # ordered-dither transition from previous band (6 px)
        if i > 0:
            pc = SKY_BANDS[i - 1][1]
            for k in range(6):
                lvl = 13 - k * 2
                y = y0 + k
                row = BAYER4[y % 4, xx[0] % 4] < lvl
                L.a[y, row, :3] = pc
    # sun, top-left (light comes from top-left)
    cx, cy = 62, 38
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    halo2 = (d < 30) & (BAYER4[yy % 4, xx % 4] < 4)
    halo1 = (d < 23) & (BAYER4[yy % 4, xx % 4] < 9)
    L.a[halo2, :3] = mix(SKY_BANDS[0][1], (255, 250, 220), 0.35)
    L.a[halo1, :3] = mix(SKY_BANDS[1][1], (255, 248, 210), 0.55)
    L.a[d < 16.5, :3] = (255, 236, 170)
    L.a[d < 14.5, :3] = (255, 246, 200)
    L.a[d < 11, :3] = (255, 253, 236)
    return L


CLOUD_W = (255, 255, 255)
CLOUD_L = (236, 244, 253)
CLOUD_M = (212, 226, 246)
CLOUD_S = (186, 206, 238)


def cloud(L, x, y, w, h, rng):
    """Flat-bottomed cumulus whose bottom is at y, spanning x..x+w."""
    puffs = []
    n = max(3, w // 14)
    for i in range(n):
        t = (i + 0.5) / n
        px = x + t * w
        bump = np.sin(t * np.pi)
        r = (h * 0.35 + h * 0.65 * bump) * rng.uniform(0.75, 1.0)
        puffs.append((px + rng.uniform(-3, 3), y - r * 0.55, r))
    def fn(d, ox):
        for px, py, r in puffs:
            d.ellipse([px - r * 1.15 + ox, py - r * 0.8, px + r * 1.15 + ox, py + r * 0.8], fill=1)
    m = L.mask(fn)
    m[int(y):, :] = False
    # light: highlight on upper-left part of each puff
    def fn_hi(d, ox):
        for px, py, r in puffs:
            d.ellipse([px - r * 1.15 + ox, py - r * 0.8, px + r * 0.55 + ox, py + r * 0.1], fill=1)
    def fn_sh(d, ox):
        for px, py, r in puffs:
            d.ellipse([px - r * 0.4 + ox, py - r * 0.1, px + r * 1.15 + ox, py + r * 0.8], fill=1)
    hi = L.mask(fn_hi) & m
    sh = L.mask(fn_sh) & m
    L.fill(m, CLOUD_L)
    L.fill(sh & ~hi, CLOUD_M)
    L.fill(hi, CLOUD_W)
    # flat shaded bottom bands
    yb = int(y)
    rowm = m[yb - 1]
    for k, c in ((1, CLOUD_S), (2, CLOUD_S), (3, CLOUD_M)):
        sel = m[yb - k] & ~hi[yb - k] if k > 2 else m[yb - k]
        L.a[yb - k, sel, :3] = c
    # dithered transition between L and M
    yy, xx = np.mgrid[0:L.h, 0:L.w]
    edge = sh & ~hi
    grow = np.roll(edge, -1, 0) | np.roll(edge, 1, 1)
    sel = grow & ~edge & m & ~hi & (BAYER4[yy % 4, xx % 4] < 8)
    L.fill(sel, CLOUD_M)


def draw_clouds():
    W, H = 960, 60
    L = Layer(W, H)
    rng = np.random.default_rng(7)
    specs = [(20, 30, 70, 22), (150, 52, 120, 34), (330, 22, 54, 16), (430, 46, 96, 28),
             (600, 34, 64, 20), (730, 56, 150, 40), (900, 18, 44, 13)]
    for x, y, w, h in specs:
        cloud(L, x, y, w, h, rng)
    return L


# ---------------------------------------------------------------- Ararat
ROCK_HI = (180, 190, 226)
ROCK = (158, 170, 214)
ROCK_SH = (140, 150, 200)
ROCK_DK = (124, 132, 186)
SNOW = (252, 253, 255)
SNOW_M = (230, 237, 251)
SNOW_S = (204, 214, 242)
SNOW_DK = (184, 194, 232)
HAZE = (184, 206, 240)


ARARAT_SHIFT = 110


def ararat_profile(W, H):
    # control points (x, y) of the skyline. Sis (left, sharp cone) + Masis (broad, right)
    pts = [(-40, 108), (60, 107), (110, 101), (150, 86), (190, 62), (222, 42), (234, 36),
           (246, 42), (272, 58), (292, 66), (312, 68), (334, 64), (360, 54), (384, 44),
           (398, 41), (416, 34), (438, 22), (458, 13), (478, 9), (496, 8), (512, 9),
           (528, 12), (548, 19), (572, 30), (610, 44), (660, 58), (720, 72), (790, 86),
           (860, 98), (930, 106), (1000, 108)]
    xs = np.array([p[0] for p in pts], float)
    ys = np.array([p[1] for p in pts], float)
    prof = np.interp((np.arange(W) + ARARAT_SHIFT) % W, xs, ys)
    # light smoothing (keep Sis sharp)
    sm = prof.copy()
    for i in range(W):
        if abs(i - (234 - ARARAT_SHIFT)) > 6:
            sm[i] = prof[max(0, i - 2):i + 3].mean()
    return sm


def _angle_noise(rng, n=720, k=3):
    v = rng.uniform(-1, 1, n)
    ker = np.ones(k) / k
    v = np.convolve(np.concatenate([v[-k:], v, v[:k]]), ker, 'same')[k:-k]
    v = v / np.abs(v).max()
    def f(ang):
        t = (ang + np.pi / 2) / np.pi * (n - 1)
        return np.interp(t, np.arange(n), v)
    return f


def draw_ararat():
    W, H = 960, 120
    L = Layer(W, H)
    rng = np.random.default_rng(3)
    prof = ararat_profile(W, H)
    hills = 104 + 4 * periodic_noise(W, rng, ((3, 1), (7, .6), (17, .3)))
    top = np.minimum(prof, hills).astype(int)
    yy, xx = np.mgrid[0:H, 0:W]
    body = yy >= top[None, :]
    dith = BAYER4[yy % 4, xx % 4] / 16.0 - 0.47
    # lighting: each summit casts radiating ridges; left faces lit
    light = np.zeros((H, W)) + 0.1
    ridges = {}
    for name, px_, py_, span in (("sis", 234 - ARARAT_SHIFT, 36, 150), ("masis", 496 - ARARAT_SHIFT, 8, 330)):
        f = _angle_noise(rng, 260 if name == "masis" else 130, 3)
        g = _angle_noise(rng, 70, 3)
        dx = xx - px_
        dy = np.maximum(yy - py_, 1)
        ang = np.arctan2(dx, dy * 1.4)
        r = 0.65 * f(ang) + 0.35 * g(ang)
        # ridges wobble a little with depth
        r = r + 0.12 * np.sin(yy * 0.21 + xx * 0.03)
        w = np.clip(1 - np.abs(dx) / span, 0, 1)
        side = -np.tanh(dx / 18.0)
        val = 0.55 * side + 0.75 * r
        light = np.where(w > 0.0, light * (1 - w) + val * w, light)
        ridges[name] = (r, ang, dx)
    light = light + dith * 0.08
    col = np.select([light > 0.45, light > -0.05, light > -0.5], [0, 1, 2], 3)
    col[(yy > 92) & (col == 0)] = 1
    pal = [ROCK_HI, ROCK, ROCK_SH, ROCK_DK]
    for i, c in enumerate(pal):
        L.fill(body & (col == i), c)
    # snow caps: Masis big cap with fingers down the gullies, Sis small tip
    for name, px_, py_, depth, fing, span in (("masis", 496 - ARARAT_SHIFT, 8, 34, 16, 125), ("sis", 234 - ARARAT_SHIFT, 36, 8, 7, 40)):
        r, ang, dx = ridges[name]
        fingers = np.clip(r + 0.1, 0, 1) ** 1.3 * fing
        line = py_ + depth * np.clip(1 - (dx / span) ** 2, 0, 1) ** 0.6 + fingers
        snow = body & (yy < line) & (np.abs(dx) < span)
        lv = light - 0.15 * (yy - py_) / max(depth, 1)
        L.fill(snow, SNOW_S)
        L.fill(snow & (lv > -0.35), SNOW_M)
        L.fill(snow & (lv > 0.2), SNOW)
        L.fill(snow & (lv < -0.75), SNOW_DK)
        # dark rock outcrops poking through the cap
        out = snow & (r < -0.55) & (yy > py_ + depth * 0.45) & (dx > -40)
        L.fill(out, ROCK_SH)
        # loose snow speckle just below the line
        near_line = body & ~snow & (yy < line + 4) & (np.abs(dx) < span * 0.9) & (BAYER4[yy % 4, xx % 4] < 1)
        L.fill(near_line, SNOW_S)
    # sunlit skyline rim
    for x in range(W):
        t = top[x]
        if t < 95:
            c = L.get(x, t)
            if c in (SNOW_M, SNOW_S):
                L.px(x, t, SNOW)
            elif c in (ROCK, ROCK_SH):
                L.px(x, t, ROCK_HI if (x < 496 - ARARAT_SHIFT) else ROCK)
    # haze towards the base
    for y in range(84, H):
        lvl = int(np.clip((y - 84) / 26 * 16, 0, 16))
        row = body[y] & (BAYER4[y % 4, np.arange(W) % 4] < lvl)
        L.a[y, row, :3] = HAZE
    return L
