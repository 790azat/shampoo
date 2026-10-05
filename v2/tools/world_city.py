"""Generic Yerevan city pieces: tuff buildings, soviet blocks, trees, far
silhouettes, street props and Armenian-looking sign lettering."""
import numpy as np
from world_pix import Layer, BAYER4, mix, shade, edges

HAZE_MID = (168, 190, 230)
HAZE_FAR = (150, 166, 214)


def tuff(base, haze=0.0, hz=HAZE_MID):
    """Palette dict for a stone colour. Light from top-left."""
    b = mix(base, hz, haze)
    return {
        'hi': mix(shade(b, 1.18), hz, haze * 0.3),
        'base': b,
        'joint': shade(b, 0.93),
        'sh': shade(b, 0.8),
        'dk': shade(b, 0.62),
    }


GLASS = (58, 64, 98)
GLASS_HI = (118, 140, 182)
GLASS_MID = (80, 90, 128)

TUFF_COLOURS = {
    'pink': (214, 146, 132),
    'rose': (198, 122, 112),
    'orange': (222, 156, 104),
    'apricot': (232, 176, 128),
    'cream': (228, 200, 152),
    'yellow': (222, 186, 120),
    'grey': (164, 154, 162),
    'basalt': (128, 118, 128),
    'white': (230, 226, 216),
}

LAUNDRY = [(232, 64, 72), (250, 250, 250), (72, 132, 220), (250, 210, 70), (120, 200, 120), (240, 140, 190)]
BALC_FRAMES = [(222, 222, 214), (150, 176, 196), (176, 140, 104), (200, 196, 170), (120, 150, 120)]


def tex_courses(L, x, y, w, h, pal, rng, every=4, step=7):
    """Stone courses: horizontal joints + staggered vertical joints."""
    for r, yy in enumerate(range(y + every - 1, y + h, every)):
        L.hline(x + 1, yy, w - 2, pal['joint'])
        off = (r * 3 + int(rng.integers(0, 2))) % step
        for xx in range(x + 1 + off, x + w - 1, step):
            L.vline(xx, yy - every + 1, every - 1, pal['joint'])


def window(L, x, y, w, h, pal, arched=False, rng=None, lit=False):
    L.rect(x - 1, y - 1, w + 2, h + 2, pal['sh'])  # reveal / frame shade
    L.rect(x, y, w, h, GLASS)
    L.vline(x, y, h, GLASS_MID)
    L.px(x, y, GLASS_HI)
    if h > 4:
        L.px(x + 1, y + 1, GLASS_HI)
    if w >= 4:  # mullion
        L.vline(x + w // 2, y, h, pal['dk'])
    L.hline(x - 1, y + h + 1, w + 2, pal['hi'])  # sill catches the light
    L.hline(x - 1, y + h + 2, w + 2, pal['sh'])
    if arched:
        L.px(x - 1, y - 1, pal['base'])
        L.px(x + w, y - 1, pal['base'])
        L.px(x, y - 1, pal['sh'])
        L.px(x + w - 1, y - 1, pal['sh'])
        L.rect(x, y - 2, w, 1, pal['sh'])
        L.px(x - 1 , y - 1, pal['base'])
        L.px(x, y, pal['sh'])
        L.px(x + w - 1, y, pal['sh'])
        L.hline(x, y - 3, w, pal['hi'])  # keystone arch highlight


def balcony_open(L, x, y, w, pal, rng):
    """Open balcony with iron railing below a window starting at y (window bottom)."""
    L.hline(x - 2, y, w + 4, pal['hi'])
    L.hline(x - 2, y + 1, w + 4, pal['dk'])
    iron = (60, 52, 64)
    L.hline(x - 2, y - 4, w + 4, iron)
    for xx in range(x - 2, x + w + 2, 2):
        L.vline(xx, y - 3, 3, iron)
    if rng.random() < 0.6:  # laundry
        L.hline(x - 2, y - 7, w + 4, (90, 84, 90))
        for xx in range(x - 1, x + w + 1, 2):
            if rng.random() < 0.75:
                c = LAUNDRY[int(rng.integers(len(LAUNDRY)))]
                L.rect(xx, y - 6, 1 + int(rng.random() < .5), 2 + int(rng.integers(0, 2)), c)


def balcony_closed(L, x, y, w, h, pal, rng):
    """Glazed-in soviet balcony box sticking out around a window."""
    fr = BALC_FRAMES[int(rng.integers(len(BALC_FRAMES)))]
    fr_sh = shade(fr, 0.75)
    bx, by, bw, bh = x - 2, y - 1, w + 4, h + 4
    L.rect(bx, by, bw, bh, fr)
    L.rect(bx + 1, by + 1, bw - 2, h - 2, GLASS_MID)
    for xx in range(bx + 1, bx + bw - 1, 3):
        L.vline(xx, by + 1, h - 2, fr)
    L.px(bx + 1, by + 1, GLASS_HI)
    L.rect(bx, by + h - 1, bw, bh - h + 1, fr)
    L.hline(bx, by + h, bw, fr_sh)
    L.vline(bx + bw - 1, by, bh, fr_sh)
    L.hline(bx, by + bh, bw, pal['dk'])


def ac_unit(L, x, y):
    L.rect(x, y, 4, 3, (214, 216, 220))
    L.hline(x, y + 2, 4, (160, 164, 172))
    L.px(x + 1, y + 1, (120, 124, 136))
    L.px(x + 2, y + 1, (120, 124, 136))


def dish(L, x, y):
    L.rect(x, y, 3, 3, (226, 226, 230))
    L.px(x + 2, y + 2, (170, 170, 180))
    L.px(x, y, (250, 250, 250))
    L.px(x + 3, y + 3, (90, 90, 100))


ROOF_TIN = (150, 112, 104)


def rooftop(L, x, top, w, pal, rng):
    k = rng.random()
    if k < 0.3:  # tv antennas
        for _ in range(int(rng.integers(1, 3))):
            ax = x + int(rng.integers(3, max(4, w - 3)))
            L.vline(ax, top - 8, 8, (96, 92, 104))
            L.hline(ax - 2, top - 7, 5, (96, 92, 104))
            L.hline(ax - 1, top - 5, 3, (96, 92, 104))
    elif k < 0.55:  # small pitched tin roof shed
        sx = x + int(rng.integers(2, max(3, w - 14)))
        L.rect(sx, top - 4, 12, 4, pal['sh'])
        L.poly([(sx - 1, top - 4), (sx + 6, top - 8), (sx + 12, top - 4)], ROOF_TIN)
        L.hline(sx, top - 4, 12, shade(ROOF_TIN, .7))
    elif k < 0.75:  # water tank
        sx = x + int(rng.integers(2, max(3, w - 8)))
        L.rect(sx, top - 6, 6, 5, (176, 180, 190))
        L.vline(sx + 5, top - 6, 5, (130, 134, 146))
        L.hline(sx, top - 6, 6, (210, 214, 222))
        L.vline(sx + 1, top - 1, 1, (100, 100, 110))
        L.vline(sx + 4, top - 1, 1, (100, 100, 110))
    if rng.random() < 0.5:
        dish(L, x + int(rng.integers(1, max(2, w - 4))), top - 3)


def tuff_building(L, x, ground, w, floors, colour, rng, haze=0.12, arcade=False,
                  shops=True, arched_top=True, balconies=0.35, fh=11, cornice=True):
    pal = tuff(TUFF_COLOURS[colour] if isinstance(colour, str) else colour, haze)
    gf = 14  # ground floor height
    h = gf + floors * fh + 4
    top = ground - h
    L.rect(x, top, w, h, pal['base'])
    tex_courses(L, x, top + 4, w, h - 4 - gf, pal, rng)
    # ground floor rustication
    L.rect(x, ground - gf, w, gf, pal['sh'] if arcade else pal['base'])
    for yy in range(ground - gf + 3, ground, 4):
        L.hline(x, yy, w, pal['joint'] if not arcade else pal['dk'])
    # cornice + belt course
    if cornice:
        L.hline(x - 1, top, w + 2, pal['hi'])
        L.hline(x - 1, top + 1, w + 2, pal['base'])
        L.hline(x - 1, top + 2, w + 2, pal['sh'])
        for xx in range(x, x + w, 3):
            L.px(xx, top + 2, pal['dk'])
    L.hline(x, ground - gf - 1, w, pal['hi'])
    L.hline(x, ground - gf, w, pal['sh'])
    # light from top-left
    L.vline(x, top + 1, h - 1, pal['hi'])
    L.vline(x + w - 1, top + 3, h - 3, pal['sh'])
    # windows
    step = 9
    n = max(1, (w - 6) // step)
    x0 = x + (w - (n * step - step + 4)) // 2
    for f in range(floors):
        wy = top + 5 + f * fh + 1
        for i in range(n):
            wx = x0 + i * step
            ar = arched_top and f == 0
            window(L, wx, wy, 4, fh - 5, pal, arched=ar)
            r = rng.random()
            if f > 0 and r < balconies:
                if rng.random() < 0.5:
                    balcony_closed(L, wx, wy, 4, fh - 5, pal, rng)
                else:
                    balcony_open(L, wx, wy + fh - 4, 4, pal, rng)
            elif r < balconies + 0.12:
                ac_unit(L, wx + 5, wy + fh - 7)
            elif r < balconies + 0.17:
                dish(L, wx + 5, wy)
    # ground floor
    if arcade:
        aw = 8
        na = max(1, (w - 4) // (aw + 3))
        ax0 = x + (w - (na * (aw + 3) - 3)) // 2
        for i in range(na):
            ax = ax0 + i * (aw + 3)
            L.rect(ax, ground - gf + 4, aw, gf - 4, pal['dk'])
            L.hline(ax + 1, ground - gf + 3, aw - 2, pal['dk'])
            L.hline(ax + 2, ground - gf + 2, aw - 4, pal['dk'])
            L.vline(ax, ground - gf + 4, gf - 4, shade(pal['dk'], 0.85))
            L.hline(ax + 2, ground - gf + 1, aw - 4, pal['hi'])
            L.px(ax, ground - gf + 3, pal['hi'])
            L.px(ax + aw - 1, ground - gf + 3, pal['hi'])
    elif shops:
        sx = x + 3
        while sx + 12 < x + w - 2:
            sw = int(rng.integers(10, 18))
            sw = min(sw, x + w - 3 - sx)
            if sw < 8:
                break
            L.rect(sx, ground - gf + 5, sw, gf - 5, GLASS)
            L.px(sx, ground - gf + 5, GLASS_HI)
            L.vline(sx + 1, ground - gf + 6, 2, GLASS_HI)
            awn = LAUNDRY[int(rng.integers(len(LAUNDRY)))] if rng.random() < 0.6 else None
            if awn:
                for xx in range(sx - 1, sx + sw + 1):
                    c = awn if (xx // 2) % 2 == 0 else (245, 240, 230)
                    L.vline(xx, ground - gf + 2, 3, c)
                L.hline(sx - 1, ground - gf + 5, sw + 2, shade(awn, .7))
            else:
                sign(L, sx, ground - gf + 1, sw, rng)
            sx += sw + int(rng.integers(3, 7))
    rooftop(L, x, top, w, pal, rng)
    return top


# ------------------------------------------------- Armenian-looking letters
# 3x5 glyphs, loosely modelled on Armenian capitals (Ա Ս Ր Ն Մ Ե Հ Ց Ք Թ Կ Տ Ո Ւ Խ)
GLYPHS = {
    'Ա': ["#.#", "#.#", "#.#", "#.#", ".##"],
    'Ս': ["#.#", "#.#", "#.#", "#.#", "###"],
    'Ր': ["##.", "#.#", "#.#", "#..", "#.."],
    'Ն': ["#..", "#.#", "#.#", "#.#", "###"],
    'Մ': ["#.#", "#.#", "#.#", "#.#", "##."],
    'Ե': ["#..", "###", "#..", "#..", "###"],
    'Հ': ["#..", "##.", "#.#", "#.#", "#.#"],
    'Ց': ["#.#", "###", "..#", "..#", "..#"],
    'Ք': ["#.#", "#.#", "###", "#..", "#.."],
    'Թ': ["#..", "###", "#.#", "#.#", "#.#"],
    'Կ': ["#..", "#..", "#..", "###", "..#"],
    'Տ': ["#.#", "#.#", "###", "..#", "..#"],
    'Ո': ["###", "#.#", "#.#", "#.#", "#.#"],
    'Ւ': ["#..", "#..", "#..", "#..", "##."],
    'Խ': ["#..", "#.#", "###", "#.#", "#.#"],
    'Պ': ["###", "#.#", "#.#", "#.#", "#.#"],
    'Գ': ["##.", "#.#", "#.#", "#.#", "#.#"],
    'Դ': ["##.", "#.#", "#.#", "#.#", "#.."],
    'Ի': ["#..", "#..", "###", "#.#", "#.#"],
    'Յ': ["##.", "..#", ".#.", "..#", "##."],
    'Ղ': ["#..", "#..", "##.", "#.#", "#.#"],
    'Ճ': ["#..", "##.", "#.#", "#.#", "###"],
    'Ժ': ["#..", "#..", "###", "#.#", "#.#"],
}
WORDS = ["ՍՐՃԱՐԱՆ", "ՀԱՑ", "ՄԹԵՐՔ", "ԽԱՆՈՒԹ", "ԴԵՂԱՏՈՒՆ", "ԳԻՐՔ", "ՀՅՈՒՍ", "ՄՍ", "ՔԱՂԱՔ", "ԿՈՆՅԱԿ"]
SIGN_BG = [(40, 70, 140), (180, 40, 50), (30, 110, 80), (240, 200, 70), (240, 240, 232), (80, 40, 90)]


def text(L, x, y, word, c):
    cx = x
    for ch in word:
        g = GLYPHS.get(ch)
        if g is None:
            g = GLYPHS['Ո']
        for r, row in enumerate(g):
            for k, v in enumerate(row):
                if v == '#':
                    L.px(cx + k, y + r, c)
        cx += 4
    return cx - x - 1


def text_width(word):
    return len(word) * 4 - 1


def sign(L, x, y, w, rng, bg=None, word=None):
    bg = bg or SIGN_BG[int(rng.integers(len(SIGN_BG)))]
    fg = (250, 246, 236) if sum(bg) < 500 else (150, 30, 40)
    words = [wd for wd in WORDS if text_width(wd) <= w - 2]
    if not words:
        L.rect(x, y, w, 3, bg)
        return
    word = word or words[int(rng.integers(len(words)))]
    tw = text_width(word)
    L.rect(x, y, w, 7, bg)
    L.hline(x, y + 6, w, shade(bg, .7))
    text(L, x + (w - tw) // 2, y + 1, word, fg)


# ------------------------------------------------------------------ trees
TREE_G = [(44, 96, 58), (62, 128, 64), (92, 158, 72), (140, 190, 86)]
TRUNK = [(92, 66, 58), (66, 48, 46)]


def tree_round(L, cx, ground, r, rng, pal=None, trunk_h=None, haze=0.0, hz=HAZE_MID):
    pal = [mix(c, hz, haze) for c in (pal or TREE_G)]
    tk = [mix(c, hz, haze) for c in TRUNK]
    th = trunk_h if trunk_h is not None else int(r * 0.9)
    cy = ground - th - r
    L.rect(cx - 1, cy + r // 2, 3, ground - cy - r // 2, tk[0])
    L.vline(cx + 1, cy + r // 2, ground - cy - r // 2, tk[1])
    L.line([(cx, cy + r), (cx - r // 2, cy + r // 3)], tk[0])
    blobs = [(cx + rng.uniform(-r * .55, r * .55), cy + rng.uniform(-r * .3, r * .4), r * rng.uniform(.5, .75))
             for _ in range(5)] + [(cx, cy, r * 0.8)]

    def fn(d, ox, sx=0, sy=0, k=1.0):
        for bx, by, br in blobs:
            br2 = br * k
            d.ellipse([bx - br2 + ox + sx, by - br2 + sy, bx + br2 + ox + sx, by + br2 + sy], fill=1)
    m = L.mask(fn)
    L.fill(m, pal[0])
    mid = L.mask(lambda d, ox: fn(d, ox, -r * .18, -r * .2, 0.85)) & m
    L.fill(mid, pal[1])
    hi = L.mask(lambda d, ox: fn(d, ox, -r * .35, -r * .38, 0.55)) & m
    L.fill(hi, pal[2])
    # leaf clusters: little dither specks
    H, W = m.shape
    yy, xx = np.mgrid[0:H, 0:W]
    spk = rng.random((H, W)) < 0.10
    L.fill(spk & hi, pal[3])
    L.fill(spk & mid & ~hi, pal[2])
    L.fill((rng.random((H, W)) < 0.12) & m & ~mid, shade(pal[0], .8))
    return m


def tree_poplar(L, cx, ground, h, rng, haze=0.0, hz=HAZE_MID):
    pal = [mix(c, hz, haze) for c in TREE_G]
    tk = mix(TRUNK[0], hz, haze)
    w = max(4, h // 6)
    L.rect(cx, ground - 6, 2, 6, tk)
    pts = []
    top = ground - h
    for i in range(0, 13):
        t = i / 12
        y = top + t * (h - 5)
        ww = w * np.sin(np.pi * min(1, t * 1.25 + 0.05)) ** 0.7
        pts.append((cx + 1 - ww, y))
    rpts = [(2 * cx + 2 - px, py) for px, py in pts[::-1]]
    m = L.poly(pts + rpts, pal[0])
    H, W = m.shape
    yy, xx = np.mgrid[0:H, 0:W]
    left = ((xx - cx) % W > W // 2) | ((xx - cx) % W == 0)
    L.fill(m & left, pal[1])
    L.fill(m & left & (((yy // 3 + xx) % 4) == 0), pal[2])
    L.fill(m & ~left & (((yy // 3 + xx) % 4) == 0), pal[1])
    return m


def bush(L, cx, ground, w, h, rng, haze=0.0, pal=None):
    pal = [mix(c, HAZE_MID, haze) for c in (pal or TREE_G)]
    def fn(d, ox, sx=0, sy=0):
        n = max(2, w // 6)
        for i in range(n):
            bx = cx - w / 2 + (i + .5) * w / n
            d.ellipse([bx - w / n * .8 + ox + sx, ground - h + sy + (i % 2), bx + w / n * .8 + ox + sx, ground + h * .4 + sy], fill=1)
    m = L.mask(fn)
    m[ground:, :] = False
    L.fill(m, pal[0])
    hi = L.mask(lambda d, ox: fn(d, ox, -2, -2)) & m
    L.fill(hi, pal[1])
    hi2 = L.mask(lambda d, ox: fn(d, ox, -3, -4)) & hi
    L.fill(hi2, pal[2])
    H, W = m.shape
    spk = (rng.random((H, W)) < 0.12)
    L.fill(spk & hi2, pal[3])


# --------------------------------------------------------- far silhouettes
def far_city(L, ground, rng, tones, density=1.0, hmin=14, hmax=46, start=0, end=None):
    """Distant skyline of block shapes; tones = [back, front, window, light]."""
    W = L.w
    end = end or W
    back, front, win, lit = tones
    x = start
    while x < end:  # back row
        w = int(rng.integers(14, 40))
        h = int(rng.integers(hmin + 8, hmax + 10))
        L.rect(x, ground - h, w, h, back)
        if rng.random() < 0.25:
            L.rect(x + w // 3, ground - h - 6, max(3, w // 4), 6, back)
        x += w + int(rng.integers(-4, 3))
    x = start + 6
    while x < end:  # front row with windows
        w = int(rng.integers(12, 34))
        h = int(rng.integers(hmin, hmax))
        L.rect(x, ground - h, w, h, front)
        L.vline(x, ground - h, h, lit)
        for yy in range(ground - h + 3, ground - 3, 4):
            for xx in range(x + 2, x + w - 2, 3):
                if rng.random() < 0.55 * density:
                    L.px(xx, yy, win)
        k = rng.random()
        if k < 0.15:
            L.vline(x + w // 2, ground - h - 6, 6, front)
        elif k < 0.25:
            L.poly([(x, ground - h), (x + w // 2, ground - h - 6), (x + w - 1, ground - h)], front)
        x += w + int(rng.integers(0, 10))


def far_hill(L, base_y, amp, rng, c, freq=((2, 1), (5, .5), (13, .2))):
    from world_pix import periodic_noise
    n = periodic_noise(L.w, rng, freq)
    for x in range(L.w):
        t = int(base_y - amp * (n[x] * 0.5 + 0.5))
        L.vline(x, t, L.h - t, c)


def tv_tower_far(L, x, ground, h, c, c2):
    """Little distant lattice tower silhouette (seen from everywhere)."""
    for i in range(h):
        y = ground - i
        t = i / h
        hw = int(round(5 * (1 - t) ** 1.6)) if t < 0.75 else 0
        L.hline(x - hw, y, 2 * hw + 1, c)
        if (i // 4) % 2 == 0 and t > 0.3:
            L.hline(x - hw, y, 2 * hw + 1, c2)
    L.rect(x - 2, ground - int(h * .62), 5, 3, c)
    L.rect(x - 1, ground - int(h * .82), 3, 2, c)


# --------------------------------------------------------- street props
CARS = [(200, 60, 56), (232, 232, 226), (70, 110, 170), (64, 64, 72), (220, 180, 70), (110, 150, 110), (150, 150, 160)]


def car(L, x, ground, rng, kind=None, colour=None):
    """Side-view parked car (near layer, no outline). ~40px long."""
    c = colour or CARS[int(rng.integers(len(CARS)))]
    hi, sh = shade(c, 1.2), shade(c, 0.72)
    kind = kind or ['lada', 'sedan', 'van'][int(rng.integers(3))]
    tyre, rim = (36, 32, 40), (170, 170, 180)
    if kind == 'lada':  # boxy zhiguli
        L.rect(x, ground - 11, 40, 7, c)
        L.rect(x + 9, ground - 17, 20, 6, c)
        L.rect(x + 11, ground - 16, 7, 4, GLASS_MID)
        L.rect(x + 20, ground - 16, 7, 4, GLASS_MID)
        L.px(x + 11, ground - 16, GLASS_HI)
        L.px(x + 20, ground - 16, GLASS_HI)
        L.hline(x + 9, ground - 17, 20, hi)
        L.hline(x, ground - 11, 9, hi)
        L.hline(x + 29, ground - 11, 11, hi)
        L.hline(x, ground - 5, 40, sh)
        L.hline(x - 1, ground - 7, 2, (220, 220, 225))
        L.hline(x + 39, ground - 7, 2, (220, 220, 225))
        L.px(x + 39, ground - 9, (250, 230, 150))
        L.vline(x + 19, ground - 10, 5, sh)
        wheels = (x + 8, x + 31)
    elif kind == 'sedan':
        L.rect(x, ground - 11, 42, 7, c)
        L.poly([(x + 9, ground - 11), (x + 14, ground - 17), (x + 29, ground - 17), (x + 34, ground - 11)], c)
        L.poly([(x + 12, ground - 11), (x + 15, ground - 15), (x + 21, ground - 15), (x + 21, ground - 11)], GLASS_MID)
        L.poly([(x + 23, ground - 11), (x + 23, ground - 15), (x + 28, ground - 15), (x + 31, ground - 11)], GLASS_MID)
        L.hline(x + 14, ground - 17, 15, hi)
        L.hline(x, ground - 11, 10, hi)
        L.hline(x, ground - 5, 42, sh)
        L.px(x + 41, ground - 9, (250, 230, 150))
        wheels = (x + 9, x + 33)
    else:  # van / gazelle
        L.rect(x, ground - 20, 44, 15, c)
        L.rect(x + 36, ground - 18, 7, 6, GLASS_MID)
        L.px(x + 36, ground - 18, GLASS_HI)
        L.hline(x, ground - 20, 44, hi)
        L.hline(x, ground - 5, 44, sh)
        L.rect(x + 4, ground - 16, 26, 6, shade(c, .9))
        sign(L, x + 6, ground - 17, 22, rng, bg=(245, 240, 230))
        wheels = (x + 9, x + 35)
    for wx in wheels:
        L.rect(wx - 3, ground - 6, 7, 6, tyre)
        L.rect(wx - 2, ground - 7, 5, 1, tyre)
        L.rect(wx - 1, ground - 4, 3, 2, rim)
        L.px(wx - 1, ground - 4, (220, 220, 230))


def lamp(L, x, ground, h=40):
    dk, md, hi = (44, 52, 62), (70, 80, 92), (110, 122, 136)
    L.rect(x - 1, ground - 4, 4, 4, dk)
    L.vline(x, ground - h, h, md)
    L.vline(x + 1, ground - h, h, dk)
    L.px(x, ground - h, hi)
    L.hline(x - 4, ground - h, 10, md)
    for lx in (x - 5, x + 5):
        L.rect(lx - 1, ground - h + 1, 3, 4, (250, 242, 210))
        L.px(lx + 1, ground - h + 3, (220, 200, 150))
        L.hline(lx - 1, ground - h, 3, dk)


def fence(L, x, ground, w, h=12, c=(52, 52, 64), hi=(96, 98, 112)):
    L.hline(x, ground - h + 2, w, c)
    L.hline(x, ground - 3, w, c)
    for xx in range(x, x + w, 3):
        L.vline(xx, ground - h + 1, h - 1, c)
        L.px(xx, ground - h, hi)
    for xx in range(x, x + w, 12):
        L.rect(xx, ground - h - 1, 2, h + 1, c)
        L.px(xx, ground - h - 2, hi)


def low_wall(L, x, ground, w, h, colour='pink', haze=0.0):
    pal = tuff(TUFF_COLOURS[colour], haze)
    L.rect(x, ground - h, w, h, pal['base'])
    L.hline(x - 1, ground - h - 2, w + 2, pal['hi'])
    L.hline(x - 1, ground - h - 1, w + 2, pal['sh'])
    for r, yy in enumerate(range(ground - h + 3, ground, 4)):
        L.hline(x, yy, w, pal['joint'])
        for xx in range(x + (r % 2) * 5, x + w, 10):
            L.vline(xx, yy - 3, 3, pal['joint'])
    L.vline(x + w - 1, ground - h, h, pal['sh'])
    return pal


def bench(L, x, ground):
    wood, wsh, iron = (170, 112, 70), (124, 80, 54), (50, 48, 58)
    L.rect(x, ground - 7, 18, 2, wood)
    L.hline(x, ground - 6, 18, wsh)
    L.rect(x, ground - 12, 18, 2, wood)
    L.hline(x, ground - 11, 18, wsh)
    for lx in (x + 2, x + 15):
        L.vline(lx, ground - 12, 12, iron)


def kiosk(L, x, ground, w, rng, colour=None, word=None):
    c = colour or [(236, 228, 210), (210, 226, 236), (240, 220, 190)][int(rng.integers(3))]
    sh = shade(c, .78)
    h = 26
    L.rect(x, ground - h, w, h, c)
    L.vline(x + w - 1, ground - h, h, sh)
    L.rect(x + 3, ground - h + 11, w - 6, 9, GLASS)
    L.px(x + 3, ground - h + 11, GLASS_HI)
    L.vline(x + 4, ground - h + 12, 3, GLASS_HI)
    # bottles / goods on shelf
    for xx in range(x + 5, x + w - 4, 2):
        L.px(xx, ground - h + 17, LAUNDRY[(xx // 2) % len(LAUNDRY)])
    awn = LAUNDRY[int(rng.integers(len(LAUNDRY)))] if colour is None else (200, 50, 60)
    for xx in range(x - 2, x + w + 2):
        cc = awn if (xx // 3) % 2 == 0 else (248, 244, 236)
        L.vline(xx, ground - h + 8, 3, cc)
        if (xx % 3) == 1:
            L.px(xx, ground - h + 11, cc)
    L.hline(x - 2, ground - h + 7, w + 4, shade(awn, .8))
    sign(L, x, ground - h, w, rng, word=word)
