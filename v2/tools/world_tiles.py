"""16x16 tilesets, one per district. Light from top-left, 1px dark rim on
exposed edges so the play field reads clearly against the parallax."""
import numpy as np
from world_pix import Layer, mix, shade

T = 16
COLS, ROWS = 8, 4
NAMES = {
    'top_l': [0, 0], 'top': [1, 0], 'top_r': [2, 0], 'top2': [3, 0],
    'plat_l': [4, 0], 'plat': [5, 0], 'plat_r': [6, 0], 'crate': [7, 0],
    'side_l': [0, 1], 'fill': [1, 1], 'side_r': [2, 1], 'fill2': [3, 1],
    'block': [4, 1], 'block2': [5, 1], 'stairs_r': [6, 1], 'stairs_l': [7, 1],
    'bot_l': [0, 2], 'bot': [1, 2], 'bot_r': [2, 2], 'fill3': [3, 2],
    'deco_grass': [4, 2], 'deco_flowers': [5, 2], 'deco_crack': [6, 2], 'deco_rocks': [7, 2],
    'single_top': [0, 3], 'single': [1, 3], 'single_bot': [2, 3], 'inner_l': [3, 3],
    'inner_r': [4, 3], 'deco_special': [5, 3], 'top3': [6, 3], 'barrel': [7, 3],
}

OUT = (26, 16, 36)  # #1a1024 like the sprite outline


def P(base, rim=None):
    return {'base': base, 'hi': shade(base, 1.2), 'hi2': shade(base, 1.35), 'sh': shade(base, 0.8),
            'dk': shade(base, 0.6), 'rim': rim or mix(shade(base, 0.35), OUT, 0.5)}


def tile():
    return Layer(T, T, wrap=True)


# ---------------------------------------------------------------- textures
def block_pattern(t, courses, pal, mortar, rng, speck=0.08, rough=False):
    """courses: [(y, h, [x0, x1, ...])] block starts; wraps horizontally."""
    t.rect(0, 0, T, T, mortar)
    for y, h, xs in courses:
        xs2 = list(xs) + [xs[0] + T]
        for a, b in zip(xs2[:-1], xs2[1:]):
            w = b - a - 1
            hh = h - 1
            base = pal['base'] if rng.random() > 0.25 else mix(pal['base'], pal['sh'], 0.35)
            t.rect(a, y, w, hh, base)
            t.hline(a, y, w, pal['hi'])
            t.vline(a, y, hh, pal['hi'])
            t.hline(a + 1, y + hh - 1, w - 1, pal['sh'])
            t.vline(a + w - 1, y + 1, hh - 1, pal['sh'])
            if rough:
                t.px(a, y, mortar)
                t.px(a + w - 1, y + hh - 1, mortar)
            for _ in range(int(w * hh * speck)):
                sx = a + 1 + int(rng.integers(0, max(1, w - 2)))
                sy = y + 1 + int(rng.integers(0, max(1, hh - 2)))
                t.px(sx, sy, pal['sh'] if rng.random() < .6 else pal['hi'])


def soil(t, pal, rng, stones=3, stone_pal=None, roots=False):
    t.rect(0, 0, T, T, pal['base'])
    for _ in range(14):
        x, y = rng.integers(0, T, 2)
        t.px(x, y, pal['sh'])
    for _ in range(6):
        x, y = rng.integers(0, T, 2)
        t.px(x, y, pal['hi'])
    sp = stone_pal or P((150, 140, 132))
    for _ in range(stones):
        x, y = int(rng.integers(0, T)), int(rng.integers(1, T - 3))
        w = int(rng.integers(2, 5))
        t.rect(x, y, w, 2, sp['base'])
        t.hline(x, y, w - 1, sp['hi'])
        t.hline(x + 1, y + 2, w, pal['dk'])
    if roots:
        x = int(rng.integers(0, T))
        for y in range(0, int(rng.integers(4, 9))):
            t.px(x + (y // 3) % 2, y, (120, 84, 60))


# ---------------------------------------------------------------- materials
class Ground:
    """Holds callables for one district's ground."""
    def __init__(self, fill_fns, cap_fn, cap_h, rim, cap_rim=None, bottom_pal=None):
        self.fill_fns, self.cap_fn, self.cap_h, self.rim = fill_fns, cap_fn, cap_h, rim
        self.cap_rim = cap_rim or rim

    def fill(self, t, v=0):
        self.fill_fns[v % len(self.fill_fns)](t)


def edge_left(t, rim, hi, y0=0):
    for y in range(y0, T):
        if t.get(0, y) is not None:
            t.px(0, y, rim)
            c = t.get(1, y)
            if c is not None:
                t.px(1, y, mix(c, hi, 0.5))


def edge_right(t, rim, sh, y0=0):
    for y in range(y0, T):
        if t.get(T - 1, y) is not None:
            t.px(T - 1, y, rim)
            c = t.get(T - 2, y)
            if c is not None:
                t.px(T - 2, y, mix(c, sh, 0.6))


def edge_bottom(t, rim, sh):
    for x in range(T):
        if t.get(x, T - 1) is not None:
            t.px(x, T - 1, rim)
            c = t.get(x, T - 2)
            if c is not None:
                t.px(x, T - 2, mix(c, sh, 0.6))


def round_corner(t, corner):
    if corner == 'tl':
        for x, y in ((0, 0), (1, 0), (0, 1)):
            t.clear(x, y, 1, 1)
    elif corner == 'tr':
        for x, y in ((15, 0), (14, 0), (15, 1)):
            t.clear(x, y, 1, 1)
    elif corner == 'bl':
        for x, y in ((0, 15), (1, 15), (0, 14)):
            t.clear(x, y, 1, 1)
    elif corner == 'br':
        for x, y in ((15, 15), (14, 15), (15, 14)):
            t.clear(x, y, 1, 1)


def fix_corner_rim(t, rim, corner):
    if corner == 'tl':
        t.px(1, 1, rim)
    if corner == 'tr':
        t.px(14, 1, rim)
    if corner == 'bl':
        t.px(1, 14, rim)
    if corner == 'br':
        t.px(14, 14, rim)


# ---------------------------------------------------------------- platforms
def platform(kind, part, rng):
    t = tile()
    if kind == 'iron':        # square: painted steel ledge with rivets
        c, hi, sh, dk = (70, 86, 112), (120, 140, 168), (48, 58, 80), OUT
        t.rect(0, 0, T, 6, c)
        t.hline(0, 0, T, dk)
        t.hline(0, 1, T, hi)
        t.hline(0, 4, T, sh)
        t.hline(0, 5, T, dk)
        for x in (3, 11):
            t.px(x, 3, hi)
            t.px(x + 1, 3, sh)
    elif kind == 'wood':      # opera / victory: wooden planks
        c, hi, sh = (178, 118, 70), (212, 156, 98), (128, 80, 52)
        t.rect(0, 0, T, 6, c)
        t.hline(0, 0, T, OUT)
        t.hline(0, 1, T, hi)
        t.hline(0, 3, T, sh)
        t.hline(0, 4, T, sh)
        t.hline(0, 5, T, OUT)
        t.vline(7, 1, 4, sh)
        t.px(2, 2, sh)
        t.px(12, 2, (232, 180, 120))
    elif kind == 'green':     # victory park: green painted plank
        c, hi, sh = (70, 140, 84), (118, 188, 110), (44, 96, 64)
        t.rect(0, 0, T, 6, c)
        t.hline(0, 0, T, OUT)
        t.hline(0, 1, T, hi)
        t.hline(0, 4, T, sh)
        t.hline(0, 5, T, OUT)
        t.vline(8, 1, 4, sh)
        t.px(4, 3, (200, 200, 190))
        t.px(12, 3, (200, 200, 190))
    elif kind == 'stone':     # cascade / cathedral: stone slab
        c, hi, sh = (220, 216, 204), (246, 244, 236), (176, 170, 160)
        t.rect(0, 0, T, 6, c)
        t.hline(0, 0, T, OUT)
        t.hline(0, 1, T, hi)
        t.hline(0, 4, T, sh)
        t.hline(0, 5, T, OUT)
        t.px(5, 3, sh)
        t.px(11, 2, sh)
    elif kind == 'basalt':
        c, hi, sh = (112, 104, 112), (150, 140, 148), (80, 74, 84)
        t.rect(0, 0, T, 6, c)
        t.hline(0, 0, T, OUT)
        t.hline(0, 1, T, hi)
        t.hline(0, 4, T, sh)
        t.hline(0, 5, T, OUT)
        t.px(6, 3, sh)
        t.px(12, 2, hi)
    elif kind == 'girder':    # tower: red/white steel girder
        t.rect(0, 0, T, 6, (210, 56, 52))
        t.hline(0, 0, T, OUT)
        t.hline(0, 1, T, (240, 110, 100))
        t.hline(0, 5, T, OUT)
        t.hline(0, 4, T, (150, 36, 40))
        for x in range(0, T, 4):
            t.px(x, 2, (150, 36, 40))
            t.px(x + 1, 3, (150, 36, 40))
        t.rect(8, 1, 8, 3, (240, 236, 230))
        t.hline(8, 1, 8, (255, 255, 255))
        t.hline(8, 3, 8, (196, 196, 204))
    if part == 'l':
        t.clear(0, 0, 1, 1)
        t.clear(0, 5, 1, 1)
        t.vline(0, 1, 4, OUT)
        bracket(t, 3, kind)
    elif part == 'r':
        t.clear(15, 0, 1, 1)
        t.clear(15, 5, 1, 1)
        t.vline(15, 1, 4, OUT)
        bracket(t, 11, kind)
    return t


def bracket(t, x, kind):
    c = {'iron': (48, 58, 80), 'wood': (128, 80, 52), 'green': (44, 96, 64), 'stone': (176, 170, 160),
         'basalt': (80, 74, 84), 'girder': (150, 36, 40)}[kind]
    for i in range(4):
        t.hline(x + (i if x < 8 else 0), 6 + i, 3 - i if x < 8 else 3 - i, c)
    t.vline(x + (0 if x < 8 else 2), 6, 4, c)


# ---------------------------------------------------------------- props
def crate(rng):
    t = tile()
    c, hi, sh, dk = (190, 128, 72), (226, 168, 104), (140, 90, 54), (104, 64, 42)
    t.rect(0, 0, T, T, OUT)
    t.rect(1, 1, 14, 14, c)
    t.rect(1, 1, 14, 2, hi)
    t.rect(1, 13, 14, 2, sh)
    t.rect(1, 1, 2, 14, hi)
    t.rect(13, 1, 2, 14, sh)
    for i in range(3, 13):
        t.px(i, i, dk)
        t.px(i + 1, i, hi if i < 12 else dk)
        t.px(15 - i, i, dk)
    t.hline(3, 6, 10, sh)
    t.hline(3, 9, 10, sh)
    for x, y in ((2, 2), (13, 2), (2, 13), (13, 13)):
        t.px(x, y, (90, 90, 100))
    t.rect(5, 3, 6, 2, (230, 220, 190))   # shipping stencil
    t.px(6, 3, (180, 60, 60))
    t.px(8, 3, (180, 60, 60))
    return t


def barrel(rng):
    t = tile()
    c, hi, sh = (60, 112, 168), (110, 160, 210), (40, 74, 120)
    t.rect(2, 0, 12, 16, OUT)
    t.rect(1, 1, 14, 14, OUT)
    t.rect(2, 1, 12, 14, c)
    t.rect(3, 1, 3, 14, hi)
    t.rect(11, 1, 3, 14, sh)
    for y in (3, 8, 12):
        t.hline(2, y, 12, (40, 44, 60))
    t.px(4, 2, (200, 220, 240))
    t.rect(6, 5, 4, 2, (240, 210, 70))
    return t


def stairs(fill_fn, cap_pal, rim, direction):
    t = tile()
    fill_fn(t)
    for i in range(4):
        # steps rising to the right for 'r'
        sx = i * 4 if direction == 'r' else 12 - i * 4
        top = 12 - i * 4
        t.clear(sx, 0, 4, top)
        t.hline(sx, top, 4, rim)
        t.hline(sx, top + 1, 4, cap_pal['hi2'])
        t.hline(sx, top + 2, 4, cap_pal['hi'])
        if direction == 'r':
            t.vline(sx, top, 4 if i else 4, rim) if i == 0 else None
            if i > 0:
                t.vline(sx, top, 4, rim)
                t.vline(sx + 1, top + 1, 3, cap_pal['hi'])
        else:
            if i > 0:
                t.vline(sx + 3, top, 4, rim)
                t.vline(sx + 2, top + 1, 3, cap_pal['sh'])
    if direction == 'r':
        t.vline(0, 12, 4, rim)
    else:
        t.vline(15, 12, 4, rim)
    return t


def deco_grass(rng, g):
    t = tile()
    for x in range(1, 15):
        if rng.random() < 0.7:
            h = int(rng.integers(2, 7))
            for y in range(16 - h, 16):
                t.px(x, y, g[1] if y > 16 - h else g[2])
            if rng.random() < 0.3:
                t.px(x + 1, 16 - h - 1 + 2, g[2])
    for x in range(0, 16, 3):
        t.px(x, 15, g[0])
    return t


def deco_flowers(rng, g, petals):
    t = tile()
    for x in range(1, 15, 2):
        h = int(rng.integers(2, 5))
        t.vline(x, 16 - h, h, g[1])
    for i, x in enumerate((2, 6, 10, 13)):
        y = 16 - int(rng.integers(5, 9))
        c = petals[i % len(petals)]
        t.vline(x, y + 2, 16 - y - 2, g[0])
        t.px(x, y, c)
        t.px(x - 1, y + 1, c)
        t.px(x + 1, y + 1, c)
        t.px(x, y + 2, c)
        t.px(x, y + 1, (250, 230, 90))
        t.px(x + 1, y + 3, g[2])
    return t


def deco_crack(rim):
    t = tile()
    pts = [(3, 0), (4, 1), (4, 2), (5, 3), (5, 4), (7, 5), (8, 6), (8, 7), (9, 8), (11, 9), (12, 10), (12, 11),
           (6, 6), (5, 7), (4, 8), (10, 9), (10, 10), (9, 12)]
    for x, y in pts:
        t.px(x, y + 2, rim)
    return t


def deco_rocks(rng, pal):
    t = tile()
    for x, w, h in ((1, 5, 3), (7, 3, 2), (11, 4, 4)):
        t.rect(x, 16 - h, w, h, OUT)
        t.rect(x + 1, 16 - h + 1, w - 2, h - 1, pal['base'])
        t.px(x + 1, 16 - h + 1, pal['hi2'])
        if w > 3:
            t.hline(x + 1, 15, w - 2, pal['sh'])
    return t


# ---------------------------------------------------------------- district data
def build_tileset(district, seed=0):
    rng = np.random.default_rng(seed + 11)
    D = DISTRICTS[district]
    g = D['ground']
    sheet = Layer(COLS * T, ROWS * T, wrap=False)

    def put(name, t):
        c, r = NAMES[name]
        sheet.blit(t, c * T, r * T)

    def make(fill_v=0, cap=False, l=False, r=False, b=False, cap_v=0):
        t = tile()
        g.fill(t, fill_v)
        if cap:
            g.cap_fn(t, cap_v)
        rim, hi, sh = g.rim, D['edge_hi'], D['edge_sh']
        if l:
            edge_left(t, rim, hi, 0)
        if r:
            edge_right(t, rim, sh, 0)
        if b:
            edge_bottom(t, rim, sh)
        if cap and l:
            round_corner(t, 'tl')
            fix_corner_rim(t, g.cap_rim, 'tl')
        if cap and r:
            round_corner(t, 'tr')
            fix_corner_rim(t, g.cap_rim, 'tr')
        if b and l:
            round_corner(t, 'bl')
            fix_corner_rim(t, rim, 'bl')
        if b and r:
            round_corner(t, 'br')
            fix_corner_rim(t, rim, 'br')
        return t

    put('top_l', make(0, cap=True, l=True))
    put('top', make(0, cap=True))
    put('top_r', make(0, cap=True, r=True))
    put('top2', make(1, cap=True, cap_v=1))
    put('top3', make(2, cap=True, cap_v=2))
    put('side_l', make(0, l=True))
    put('fill', make(0))
    put('side_r', make(0, r=True))
    put('fill2', make(1))
    put('fill3', make(2))
    put('bot_l', make(0, l=True, b=True))
    put('bot', make(0, b=True))
    put('bot_r', make(0, r=True, b=True))
    put('single_top', make(0, cap=True, l=True, r=True))
    put('single', make(0, l=True, r=True))
    put('single_bot', make(0, l=True, r=True, b=True))
    # inner corners: fill with a sliver of cap at one top corner (ground stepping up)
    for name, side in (('inner_l', 'l'), ('inner_r', 'r')):
        t = make(0)
        c = tile()
        g.fill(c, 0)
        g.cap_fn(c, 0)
        xs = range(0, 3) if side == 'l' else range(13, 16)
        for x in xs:
            for y in range(0, g.cap_h):
                col = c.get(x, y)
                if col is not None:
                    t.px(x, y, col)
        put(name, t)
    for part, nm in (('l', 'plat_l'), ('m', 'plat'), ('r', 'plat_r')):
        put(nm, platform(D['platform'], part, rng))
    put('crate', crate(rng))
    put('barrel', barrel(rng))
    put('block', D['block'](0))
    put('block2', D['block'](1))
    put('stairs_r', stairs(lambda t: g.fill(t, 0), D['step_pal'], g.rim, 'r'))
    put('stairs_l', stairs(lambda t: g.fill(t, 0), D['step_pal'], g.rim, 'l'))
    put('deco_grass', deco_grass(rng, D['grass']))
    put('deco_flowers', deco_flowers(rng, D['grass'], D['petals']))
    put('deco_crack', deco_crack(g.rim))
    put('deco_rocks', deco_rocks(rng, D['rock_pal']))
    put('deco_special', D['special'](rng))
    return sheet


def outlined_block(pal, mortar, courses, rng, rough=False, speck=0.08):
    t = tile()
    block_pattern(t, courses, pal, mortar, rng, speck=speck, rough=rough)
    t.hline(0, 0, T, OUT)
    t.hline(0, 15, T, OUT)
    t.vline(0, 0, T, OUT)
    t.vline(15, 0, T, OUT)
    t.hline(1, 1, 14, pal['hi2'])
    t.vline(1, 1, 14, pal['hi'])
    t.hline(1, 14, 14, pal['dk'])
    t.vline(14, 1, 14, pal['dk'])
    return t


def _mk_districts():
    D = {}
    GRASS = [(52, 112, 56), (84, 156, 66), (150, 206, 92)]
    rngs = lambda s: np.random.default_rng(s)

    # ---- square: tuff ashlar walls, basalt curb, pink paving
    tuffp = P((208, 132, 108))
    tuffp2 = P((214, 142, 112))
    mortar = (150, 92, 84)
    ash = [(0, 8, [0, 10]), (8, 8, [5, 13])]
    ash2 = [(0, 8, [3, 12]), (8, 8, [0, 7])]
    ash3 = [(0, 4, [0, 6, 11]), (4, 4, [3, 9]), (8, 8, [0, 10])]
    curb = P((118, 112, 124))
    pave = P((214, 170, 150))

    def sq_cap(t, v):
        # paving surface seen slightly from above + basalt curb
        t.rect(0, 0, T, 3, pave['base'])
        t.hline(0, 0, T, pave['hi2'])
        for x in (0, 8) if v != 1 else (4, 12):
            t.vline(x, 0, 3, pave['sh'])
        t.hline(0, 3, T, curb['hi'])
        t.rect(0, 4, T, 3, curb['base'])
        t.hline(0, 6, T, curb['sh'])
        t.vline(5, 4, 3, curb['dk'])
        t.vline(13, 4, 3, curb['dk'])
        t.hline(0, 7, T, curb['dk'])
        if v == 2:  # drain grate
            t.rect(5, 0, 6, 3, (64, 60, 72))
            for x in range(6, 11, 2):
                t.vline(x, 0, 3, (110, 104, 116))
    D['square'] = dict(
        ground=Ground([lambda t: block_pattern(t, ash, tuffp, mortar, rngs(1)),
                       lambda t: block_pattern(t, ash2, tuffp2, mortar, rngs(2)),
                       lambda t: block_pattern(t, ash3, tuffp, mortar, rngs(3))],
                      sq_cap, 8, rim=mix(tuffp['dk'], OUT, .6), cap_rim=curb['dk']),
        edge_hi=tuffp['hi'], edge_sh=tuffp['sh'], platform='iron',
        block=lambda v: outlined_block(P((196, 112, 98)) if v else P((226, 170, 120)), mortar,
                                       [(0, 8, [0, 8]), (8, 8, [4, 12])], rngs(5 + v)),
        step_pal=pave, grass=GRASS, petals=[(240, 70, 80), (250, 240, 240), (250, 200, 60)],
        rock_pal=curb, special=lambda rng: bollard())

    # ---- opera: lawn and brown soil, gravel path variant
    soilp = P((132, 92, 64))
    gravel = P((206, 186, 150))

    def grass_cap(t, v, G=GRASS, depth=5):
        if v == 1:  # gravel path
            t.rect(0, 1, T, 4, gravel['base'])
            t.hline(0, 1, T, gravel['hi2'])
            for x in range(0, T, 3):
                t.px(x + (x % 2), 3, gravel['sh'])
                t.px(x + 1, 2, gravel['hi'])
            t.hline(0, 5, T, gravel['dk'])
            t.clear(0, 0, T, 1)
            return
        t.clear(0, 0, T, 2)
        t.rect(0, 2, T, depth, G[1])
        t.hline(0, 2, T, G[2])
        for x in range(T):
            hh = [1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 1, 2, 0, 1, 1, 2][x]
            for k in range(hh):
                t.px(x, 1 - k, G[1] if k == 0 else G[2])
            d = [1, 2, 1, 0, 2, 3, 1, 1, 0, 2, 1, 3, 2, 0, 1, 2][x]
            t.vline(x, 2 + depth, d, G[0])
            t.px(x, 2 + depth + d, shade(G[0], .7))
        for x in range(1, T, 4):
            t.px(x, 4, G[2])
            t.px(x + 2, 5, G[0])
        if v == 2:  # tulips poking
            for x in (3, 9, 13):
                t.px(x, 0, (230, 60, 70))
    D['opera'] = dict(
        ground=Ground([lambda t: soil(t, soilp, rngs(11), 3),
                       lambda t: soil(t, soilp, rngs(12), 4, roots=True),
                       lambda t: soil(t, soilp, rngs(13), 2, roots=True)],
                      grass_cap, 9, rim=mix(soilp['dk'], OUT, .6), cap_rim=shade(GRASS[0], .55)),
        edge_hi=soilp['hi'], edge_sh=soilp['sh'], platform='wood',
        block=lambda v: outlined_block(P((214, 196, 166)) if v == 0 else P((196, 140, 110)), (150, 128, 108),
                                       [(0, 8, [0, 8]), (8, 8, [4, 12])], rngs(15 + v)),
        step_pal=gravel, grass=GRASS, petals=[(240, 70, 90), (250, 250, 250), (180, 120, 230), (250, 200, 60)],
        rock_pal=P((170, 160, 150)), special=lambda rng: tulips())

    # ---- cascade: white travertine
    lime = P((232, 228, 214))
    lime2 = P((220, 214, 196))
    lmort = (176, 168, 152)

    def lime_cap(t, v):
        t.rect(0, 0, T, 4, (248, 246, 238))
        t.hline(0, 0, T, (255, 255, 252))
        t.hline(0, 3, T, lime['sh'])
        t.hline(0, 4, T, lime['dk'])
        if v == 1:
            for x in range(1, T, 5):
                t.px(x, 1, (120, 180, 230))   # water rivulet
            t.rect(0, 1, T, 2, (150, 200, 240))
            t.hline(0, 1, T, (220, 240, 255))
        if v == 2:
            t.hline(0, 0, T, (120, 170, 80))
            t.px(4, 0, (250, 210, 70))
    def lime_fill(seed, courses):
        def f(t):
            rr = rngs(seed)
            block_pattern(t, courses, lime if seed % 2 else lime2, lmort, rr, speck=0.0)
            for _ in range(6):  # travertine pores
                x, y = rr.integers(0, T, 2)
                t.px(x, y, lime['sh'])
                t.px(x + 1, y, lime['hi2'])
        return f
    D['cascade'] = dict(
        ground=Ground([lime_fill(21, [(0, 8, [0]), (8, 8, [8])]),
                       lime_fill(22, [(0, 16, [0, 8])]),
                       lime_fill(23, [(0, 4, [0, 8]), (4, 4, [4, 12]), (8, 8, [0])])],
                      lime_cap, 5, rim=(140, 132, 124), cap_rim=(150, 146, 140)),
        edge_hi=(255, 255, 250), edge_sh=lime['sh'], platform='stone',
        block=lambda v: outlined_block(P((236, 232, 220)) if v == 0 else P((206, 200, 186)), lmort,
                                       [(0, 16, [0])] if v == 0 else [(0, 8, [0, 8]), (8, 8, [4, 12])],
                                       rngs(25 + v), speck=0.03),
        step_pal=lime, grass=GRASS, petals=[(250, 120, 60), (250, 220, 70), (250, 250, 250)],
        rock_pal=lime2, special=lambda rng: cube_sculpture())

    # ---- cathedral: grey granite + orange tuff accents
    gran = P((150, 146, 152))
    gran2 = P((132, 128, 136))
    gmort = (88, 84, 94)

    def gran_cap(t, v):
        t.rect(0, 0, T, 5, (178, 174, 178))
        t.hline(0, 0, T, (214, 210, 212))
        t.hline(0, 4, T, gran['sh'])
        t.hline(0, 5, T, gran['dk'])
        t.vline(7, 1, 4, gran['sh'])
        t.vline(15, 1, 4, gran['sh'])
        for x in (2, 10, 12):
            t.px(x, 2, (196, 192, 196))
        if v == 1:  # orange tuff inlay band
            t.rect(0, 1, T, 3, (214, 150, 100))
            t.hline(0, 1, T, (236, 182, 130))
            t.vline(7, 1, 3, (170, 110, 80))
            t.vline(15, 1, 3, (170, 110, 80))
        if v == 2:
            t.hline(0, 0, T, (90, 150, 70))
            for x in range(0, T, 2):
                t.px(x, 0, (130, 190, 90))
    def gfill(seed, courses, pal):
        def f(t):
            block_pattern(t, courses, pal, gmort, rngs(seed), speck=0.22)
        return f
    D['cathedral'] = dict(
        ground=Ground([gfill(31, [(0, 8, [0, 9]), (8, 8, [4, 13])], gran),
                       gfill(32, [(0, 8, [2, 11]), (8, 8, [6])], gran2),
                       gfill(33, [(0, 6, [0, 8]), (6, 5, [3, 11]), (11, 5, [0, 6, 12])], gran)],
                      gran_cap, 6, rim=mix(gran['dk'], OUT, .6)),
        edge_hi=gran['hi'], edge_sh=gran['sh'], platform='basalt',
        block=lambda v: outlined_block(P((218, 156, 104)) if v == 0 else P((150, 146, 152)),
                                       (150, 100, 80) if v == 0 else gmort,
                                       [(0, 8, [0, 8]), (8, 8, [4, 12])], rngs(35 + v), speck=0.12),
        step_pal=P((178, 174, 178)), grass=GRASS, petals=[(250, 250, 250), (240, 90, 90), (250, 210, 70)],
        rock_pal=gran, special=lambda rng: khachkar())

    # ---- victory: lush park grass over dark earth, dirt path variant
    VG = [(40, 98, 52), (70, 140, 60), (126, 190, 80)]
    dsoil = P((104, 74, 58))
    D['victory'] = dict(
        ground=Ground([lambda t: soil(t, dsoil, rngs(41), 3, roots=True),
                       lambda t: soil(t, dsoil, rngs(42), 5),
                       lambda t: soil(t, dsoil, rngs(43), 2, roots=True)],
                      lambda t, v: grass_cap(t, v if v != 1 else 1, VG, 6), 10,
                      rim=mix(dsoil['dk'], OUT, .6), cap_rim=shade(VG[0], .55)),
        edge_hi=dsoil['hi'], edge_sh=dsoil['sh'], platform='green',
        block=lambda v: outlined_block(P((150, 140, 150)) if v == 0 else P((196, 120, 100)), (90, 84, 94),
                                       [(0, 8, [0, 8]), (8, 8, [4, 12])], rngs(45 + v), speck=0.12),
        step_pal=gravel, grass=VG, petals=[(250, 250, 250), (250, 220, 60), (240, 70, 80)],
        rock_pal=P((150, 140, 150)), special=lambda rng: daisies())

    # ---- tower: asphalt over volcanic rubble
    rock = P((128, 84, 76))
    rock2 = P((96, 84, 92))
    rmort = (66, 48, 52)
    asph = P((86, 86, 96))

    def asph_cap(t, v):
        t.rect(0, 0, T, 5, asph['base'])
        t.hline(0, 0, T, asph['hi'])
        for x, y in ((2, 2), (7, 3), (11, 1), (14, 3), (5, 1)):
            t.px(x, y, asph['sh'] if (x + y) % 2 else asph['hi'])
        t.hline(0, 5, T, asph['dk'])
        t.hline(0, 6, T, rmort)
        if v == 1:  # painted lane mark
            t.rect(4, 2, 8, 1, (240, 210, 80))
        if v == 2:  # pothole patch
            t.rect(3, 1, 9, 3, shade(asph['base'], .8))
            t.hline(3, 1, 9, asph['sh'])
            t.px(5, 2, (110, 150, 200))
    def rfill(seed, pal):
        def f(t):
            block_pattern(t, [(0, 6, [0, 7]), (6, 5, [3, 11]), (11, 5, [0, 6, 13])], pal, rmort, rngs(seed),
                          rough=True, speck=0.15)
        return f
    D['tower'] = dict(
        ground=Ground([rfill(51, rock), rfill(52, rock2), rfill(53, rock)],
                      asph_cap, 7, rim=mix(rmort, OUT, .5), cap_rim=asph['dk']),
        edge_hi=rock['hi'], edge_sh=rock['sh'], platform='girder',
        block=lambda v: concrete_block(v),
        step_pal=asph, grass=[(80, 110, 56), (120, 150, 70), (170, 190, 96)],
        petals=[(250, 220, 60), (250, 250, 250), (200, 120, 230)],
        rock_pal=rock, special=lambda rng: tyre())
    return D


def bollard():
    t = tile()
    c, hi, sh = (60, 60, 72), (110, 110, 126), (36, 36, 46)
    t.rect(5, 6, 6, 10, OUT)
    t.rect(6, 4, 4, 2, OUT)
    t.rect(6, 7, 4, 9, c)
    t.vline(6, 7, 9, hi)
    t.vline(9, 7, 9, sh)
    t.rect(7, 5, 2, 2, c)
    t.px(7, 5, hi)
    t.hline(6, 10, 4, (200, 170, 60))
    return t


def tulips():
    t = tile()
    for i, (x, c) in enumerate(((2, (230, 50, 60)), (6, (250, 200, 50)), (10, (230, 50, 60)), (13, (240, 120, 180)))):
        t.vline(x, 9, 7, (60, 130, 60))
        t.px(x - 1, 12, (84, 156, 66))
        t.rect(x - 1, 6 + (i % 2), 3, 3, c)
        t.px(x, 6 + (i % 2), shade(c, 1.3))
        t.px(x - 1, 5 + (i % 2), c)
        t.px(x + 1, 5 + (i % 2), c)
    return t


def cube_sculpture():
    t = tile()
    # small red modern sculpture on a plinth (Cascade garden vibe)
    t.rect(3, 12, 10, 4, OUT)
    t.rect(4, 12, 8, 3, (220, 216, 204))
    t.hline(4, 12, 8, (246, 244, 236))
    t.rect(5, 3, 6, 9, OUT)
    t.rect(6, 4, 4, 7, (210, 50, 60))
    t.vline(6, 4, 7, (240, 100, 100))
    t.rect(8, 1, 4, 4, OUT)
    t.rect(9, 2, 2, 2, (60, 120, 210))
    return t


def khachkar():
    t = tile()
    st, hi, sh = (206, 150, 108), (232, 186, 140), (160, 104, 80)
    t.rect(3, 0, 10, 16, OUT)
    t.rect(4, 1, 8, 15, st)
    t.vline(4, 1, 15, hi)
    t.vline(11, 1, 15, sh)
    t.vline(8, 3, 9, sh)
    t.hline(6, 6, 5, sh)
    t.px(7, 3, sh)
    t.px(9, 3, sh)
    t.px(6, 12, sh)
    t.px(10, 12, sh)
    for x in range(5, 11, 2):
        t.px(x, 14, sh)
    return t


def daisies():
    t = tile()
    for x, y in ((2, 11), (6, 9), (10, 12), (13, 10)):
        t.vline(x, y + 1, 16 - y - 1, (60, 130, 60))
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            t.px(x + dx, y + dy, (252, 252, 252))
        t.px(x, y, (250, 200, 40))
    return t


def tyre():
    t = tile()
    t.ellipse(1, 6, 14, 16, OUT)
    t.ellipse(2, 7, 13, 15, (52, 50, 58))
    t.ellipse(5, 9, 10, 13, OUT)
    t.hline(4, 8, 6, (90, 88, 100))
    for x in range(1, 4):
        t.px(x + 10, 6 - x, (120, 150, 70))
    t.vline(13, 2, 5, (120, 150, 70))
    return t


def concrete_block(v):
    t = tile()
    c = (170, 168, 164) if v == 0 else (150, 120, 110)
    pal = P(c)
    t.rect(0, 0, T, T, OUT)
    t.rect(1, 1, 14, 14, pal['base'])
    t.hline(1, 1, 14, pal['hi2'])
    t.vline(1, 1, 14, pal['hi'])
    t.hline(1, 14, 14, pal['dk'])
    t.vline(14, 1, 14, pal['dk'])
    for x, y in ((4, 4), (10, 6), (6, 11), (12, 11)):
        t.px(x, y, pal['sh'])
    if v == 0:  # rusty rebar stubs + hazard stripe
        t.rect(1, 12, 14, 2, (240, 200, 60))
        for x in range(1, 15, 4):
            t.rect(x, 12, 2, 2, (40, 36, 44))
        t.px(5, 0, (170, 80, 50))
        t.px(10, 0, (170, 80, 50))
    else:
        t.vline(7, 2, 6, pal['sh'])
        t.px(8, 8, pal['sh'])
        t.px(9, 9, pal['sh'])
    return t


DISTRICTS = _mk_districts()
