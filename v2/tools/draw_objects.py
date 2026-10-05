#!/usr/bin/env python3
"""Objects for SHAMPOO v2: collectibles, cars, DJ projectiles, enemy projectiles,
checkpoint flag / finish arch, FX and street props.

Run:  python3 tools/draw_objects.py   (writes assets/*.png + assets/objects.json)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixkit import Spr, Book, OUTLINE  # noqa: E402
import draw_actors as A  # noqa: E402  (slipper drawing + granny palette)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
PREV = os.environ.get('PREVIEW_DIR')

# ------------------------------------------------------------------ fonts
FONT3 = {  # 3x5
    'A': ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'],
    'B': ['XX.', 'X.X', 'XX.', 'X.X', 'XX.'],
    'E': ['XXX', 'X..', 'XX.', 'X..', 'XXX'],
    'H': ['X.X', 'X.X', 'XXX', 'X.X', 'X.X'],
    'I': ['XXX', '.X.', '.X.', '.X.', 'XXX'],
    'M': ['X.X', 'XXX', 'XXX', 'X.X', 'X.X'],
    'O': ['XXX', 'X.X', 'X.X', 'X.X', 'XXX'],
    'P': ['XX.', 'X.X', 'XX.', 'X..', 'X..'],
    'R': ['XX.', 'X.X', 'XX.', 'X.X', 'X.X'],
    'S': ['.XX', 'X..', '.X.', '..X', 'XX.'],
    'T': ['XXX', '.X.', '.X.', '.X.', '.X.'],
    'V': ['X.X', 'X.X', 'X.X', 'X.X', '.X.'],
    '&': ['.X.', 'X.X', '.X.', 'X.X', '.XX'],
}
FONT_BOLD = {  # 4x5 chunky
    'B': ['XXX.', 'X..X', 'XXX.', 'X..X', 'XXX.'],
    'O': ['.XX.', 'X..X', 'X..X', 'X..X', '.XX.'],
    'M': ['X...X', 'XX.XX', 'X.X.X', 'X...X', 'X...X'],
}
FONT_SMALL = {  # 3x5 with a narrow 2px E
    'T': FONT3['T'], 'R': FONT3['R'], 'A': FONT3['A'],
    'E': ['XX', 'X.', 'XX', 'X.', 'XX'],
}
FONT7 = {  # 5x7 cyrillic for the finish banner
    'Ф': ['..X..', '.XXX.', 'X.X.X', 'X.X.X', '.XXX.', '..X..', '..X..'],
    'И': ['X...X', 'X...X', 'X..XX', 'X.X.X', 'XX..X', 'X...X', 'X...X'],
    'Н': ['X...X', 'X...X', 'X...X', 'XXXXX', 'X...X', 'X...X', 'X...X'],
    'Ш': ['X...X', 'X...X', 'X.X.X', 'X.X.X', 'X.X.X', 'X.X.X', 'XXXXX'],
}


def text(s, x, y, msg, c, font=FONT3, gap=1, shadow=None):
    for ch in msg:
        g = font[ch]
        if shadow:
            for j, row in enumerate(g):
                for i, v in enumerate(row):
                    if v == 'X':
                        s.px(x + i + 1, y + j + 1, shadow)
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == 'X':
                    s.px(x + i, y + j, c)
        x += len(g[0]) + gap
    return x


def text_w(msg, font=FONT3, gap=1):
    return sum(len(font[c][0]) for c in msg) + gap * (len(msg) - 1)


def shine_frames(base, light='w', step=None, width=2, skip=('k', '.')):
    """4 frames: a diagonal white glint sweeping left->right across the sprite."""
    out = []
    W, H = base.w, base.h
    pos = [-H * 0.25 - 3 + (W + H * 0.5 + 6) * k / 3.0 for k in range(4)] if step is None else step
    for p in pos:
        f = base.copy()
        for y in range(H):
            for x in range(W):
                d = (x + y * 0.5) - (p + H * 0.25)
                if 0 <= d < width and f.g[y, x] not in skip:
                    f.g[y, x] = light
        out.append(f)
    return out


# ================================================================== ITEMS
ITEM_PAL = {
    'k': OUTLINE, 'w': '#ffffff',
    # silver / aluminium
    'L': '#f4f6fa', 'l': '#c9cfdb', 'm': '#8e97aa', 'n': '#5d6578',
    # boom
    'O': '#ff8a1e', 'o': '#c85a10', 'B': '#2a7fe0', 'b': '#1a4e9a',
    # rush
    'K': '#2a2632', 'j': '#3e3a48', 'J': '#57536a', 'G': '#f5c542', 'g': '#b8862a', 'R': '#e0303c',
    # vip
    'V': '#1f5fd0', 'v': '#143e8e', 'U': '#5c9af0', 'W': '#f2efe8', 'X': '#c9c3b6',
    # terea
    'E': '#8f8a4a', 'e': '#666233', 'F': '#e6dcb8', 'f': '#bfb38a', 'Q': '#b5ad6a',
    # shampoo
    'C': '#2f6fd6', 'c': '#1d469a', 'D': '#7fb2ff', 'Z': '#0f2a66', 'Y': '#f2f6ff', 'y': '#c8d6ee', 'r': '#e04050',
}


def can_base(body, bodyhi, bodysh):
    """16x24 drink can, front facing. body colours given as palette chars."""
    s = Spr(16, 24)
    # body cylinder 12 wide
    s.rect(2, 4, 13, 20, body)
    # lid + rim
    s.rect(3, 2, 12, 3, 'l')
    s.hline(4, 11, 1, 'm')
    s.hline(3, 12, 3, 'm')
    s.px(6, 2, 'n'); s.px(7, 2, 'n')          # tab
    s.hline(2, 13, 4, 'l')                      # neck shoulder
    # bottom
    s.rect(3, 21, 12, 21, 'l')
    s.hline(4, 11, 22, 'm')
    # cylinder shading bands
    s.vline(3, 5, 20, bodyhi)
    s.vline(4, 5, 20, bodyhi)
    s.vline(12, 5, 20, bodysh)
    s.vline(13, 5, 20, bodysh)
    s.vline(2, 5, 20, body)
    return s


def item_boom():
    s = can_base('L', 'w', 'l')
    s.vline(13, 5, 20, 'm')
    # blue swoosh band top and bottom
    s.hline(2, 13, 6, 'B'); s.hline(2, 13, 19, 'B')
    s.hline(12, 13, 6, 'b'); s.hline(12, 13, 19, 'b')
    # BO / OM stacked in orange with blue shadow
    text(s, 4, 8, 'BO', 'O', font=FONT_BOLD)
    text(s, 3, 13, 'OM', 'O', font=FONT_BOLD)
    for x in range(3, 13):            # darker bottom edge on letters
        for y in (12, 17):
            if s.get(x, y) == 'O':
                s.px(x, y, 'o')
    s.outline('k')
    return s


def item_rush():
    s = can_base('K', 'J', 'j')
    # silver ribbons
    s.hline(2, 13, 6, 'l'); s.hline(2, 13, 19, 'l')
    s.hline(12, 13, 6, 'm'); s.hline(12, 13, 19, 'm')
    # big stylised gold A (lightning legs)
    s.ascii(4, 8, """
...GG...
..GgGG..
..G..G..
.GGGGGG.
.G....Gg
GG....GG
""")
    s.hline(4, 11, 15, 'R')
    s.hline(5, 10, 17, 'm')     # small silver text line
    s.outline('k')
    return s


def item_vip():
    s = Spr(16, 24)
    s.rect(2, 2, 13, 21, 'W')
    s.hline(2, 13, 2, 'w')
    s.hline(2, 13, 6, 'X')       # flip-top lid line
    s.px(2, 6, 'X'); s.px(13, 6, 'X')
    s.vline(13, 3, 21, 'X')
    s.vline(2, 3, 21, 'w')
    # blue band with VIP
    s.rect(2, 9, 13, 16, 'V')
    s.hline(2, 13, 9, 'U')
    s.hline(2, 13, 16, 'v')
    text(s, 2, 10, 'VIP', 'w', gap=1)
    s.vline(13, 10, 15, 'v')
    # small crest + text lines
    s.hline(6, 9, 4, 'V')
    s.px(7, 3, 'V'); s.px(8, 3, 'V')
    s.hline(5, 10, 18, 'X')
    s.hline(6, 9, 20, 'X')
    s.outline('k')
    return s


def item_terea():
    s = Spr(21, 24)
    s.rect(1, 2, 19, 21, 'E')
    s.hline(1, 19, 2, 'Q')
    s.vline(1, 2, 21, 'Q')
    s.vline(19, 3, 21, 'e')
    s.hline(2, 19, 21, 'e')
    s.hline(1, 19, 6, 'e')       # lid
    # beige label panel with TEREA
    s.rect(1, 9, 19, 15, 'F')
    s.hline(1, 19, 15, 'f')
    s.vline(19, 9, 15, 'f')
    text(s, 2, 10, 'TEREA', 'e', font=FONT_SMALL, gap=1)
    # little wave mark
    s.px(8, 18, 'F'); s.px(9, 17, 'F'); s.px(10, 18, 'F'); s.px(11, 17, 'F'); s.px(12, 18, 'F')
    s.hline(7, 13, 4, 'Q')
    s.outline('k')
    return s


def item_shampoo():
    s = Spr(16, 26)
    # cap (navy, flip-top)
    s.rect(5, 1, 10, 4, 'Z')
    s.hline(5, 10, 1, 'c')
    s.px(6, 2, 'c')
    # shoulders + body (bottle with slight waist)
    s.polyfill([(4, 5), (12, 5), (14, 8), (13, 15), (14, 22), (13, 24), (3, 24), (2, 22), (3, 15), (2, 8)], 'C')
    # white front label wave
    s.polyfill([(3, 10), (13, 9), (13, 20), (3, 21)], 'Y', only='C')
    s.polyfill([(3, 10), (13, 9), (13, 11), (3, 12)], 'D', only='Y')
    # H&S
    x = text(s, 3, 13, 'H', 'c', gap=0)
    x = text(s, x + 0, 13, '&', 'r', gap=0)
    text(s, x, 13, 'S', 'c', gap=0)
    s.hline(4, 12, 19, 'y')
    s.shade('C', 'D', 'c', group='CDcYyZr')
    s.shade('Y', None, 'y', group='CDcYyZr')
    s.outline('k')
    return s


# ================================================================== PROJECTILES
PROJ_PAL = dict(A.GRAN_PAL)
PROJ_PAL.update({
    'k': OUTLINE, 'w': '#ffffff', 'a': '#dedad2', 'z': '#a8a29a', 'x': '#6e6a66', 'n': '#7a6a3a',
    'V': '#1c1a22', 'v': '#34303e', 'u': '#55506a', 'R': '#e0303c', 'O': '#ffb030', 'o': '#ffe680',
    'p': '#ff5fa8', 'P': '#c43a80', 'q': '#ffd0e8', 'c': '#5fe0ff', 'C': '#2a9ad0',
})


def poop():
    s = Spr(6, 7)
    s.ascii(1, 1, """
.ww.
wwaw
waaz
.az.
.z..
""")
    s.px(2, 3, 'x')
    s.outline('k')
    return s


def poop_splat():
    frames = []
    shapes = [
        """
....ww....
...waaw...
..waazaw..
""",
        """
.w..ww..w.
.wwwaawww.
wwaaazaaaw
""",
        """
w.......w.
.w.wwww.w.
wwaazaaazw
""",
    ]
    for sh in shapes:
        s = Spr(12, 6)
        s.ascii(1, 2, sh)
        s.px(5, 4, 'x')
        s.outline('k')
        frames.append(s)
    return frames


SLIPPER = """
......GGG.
.....GJJGg
GGGGGGGGGg
jjjjjjjjjj
"""


def slipper_spin():
    import numpy as np
    base = Spr(10, 10)
    base.ascii(0, 3, SLIPPER)
    frames = []
    for i in range(4):
        r = base.copy()
        r.g = np.rot90(base.g, k=i).copy()   # counter-clockwise quarter turns
        s = Spr(12, 12)
        s.blit(r, 1, 1)
        s.outline('k')
        frames.append(s)
    return frames[::-1]                       # thrown to the right -> spin clockwise


def disc_spin():
    frames = []
    for i in range(4):
        s = Spr(12, 12)
        s.ellipse(5.5, 5.5, 5, 5, 'V')
        s.ring(5.5, 5.5, 3.6, 'v')
        s.ring(5.5, 5.5, 4.6, 'v')
        s.ellipse(5.5, 5.5, 1.6, 1.6, 'R')
        s.px(5, 5, 'o'); s.px(6, 6, 'k'); s.px(5, 6, 'R'); s.px(6, 5, 'R')
        # rotating light reflections (two opposite glints)
        a = i * math.pi / 4 + math.pi / 4
        for r in (3, 4):
            for sgn in (1, -1):
                s.px(5.5 + sgn * math.cos(a) * r, 5.5 + sgn * math.sin(a) * r, 'u')
        s.px(5.5 + math.cos(a) * 2.6, 5.5 + math.sin(a) * 2.6, 'w')
        s.outline('k')
        frames.append(s)
    return frames


def note():
    frames = []
    for i, (c, hi) in enumerate((('p', 'q'), ('c', 'w'))):
        s = Spr(10, 12)
        s.ellipse(3, 8.5, 2, 1.5, c)
        s.vline(5, 1, 8, c)
        s.vline(4 if False else 5, 1, 8, c)
        # flag
        if i == 0:
            s.ascii(6, 1, "XX.\n.XX\n..X\n.X.".replace('X', c))
        else:
            s.ascii(6, 2, "X..\nXX.\n.XX\n..X".replace('X', c))
        s.px(2, 8, hi)
        s.outline('k')
        frames.append(s)
    return frames


# ================================================================== CARS
CAR_PAL = {
    'k': OUTLINE,
    'H': '#ffffff', 'W': '#eef1f5', 'w': '#c6cdd8', 'v': '#949eb0',
    'T': '#253048', 't': '#34425e', 'r': '#6f86ab', 'R': '#9fb4d4',
    'C': '#eef3f8', 'c': '#8b95a8', 'K': '#2b2733', 'J': '#45404f',
    'M': '#c4ccd8', 'm': '#7c8698', 'n': '#565f72',
    'Y': '#b9d0e4', 'y': '#8aa2ba', 'L': '#fff3a8', 'l': '#ffe066',
    'E': '#e2343e', 'e': '#9a1e2a', 'O': '#ff9a2a', 'B': '#1c1824',
}


def car_wheel(s, cx, cy, r=8):
    s.ellipse(cx, cy, r, r, 'K')
    s.ring(cx, cy, r, 'J', 1)
    s.ellipse(cx, cy, r - 3, r - 3, 'M')
    s.ring(cx, cy, r - 3, 'm', 1)
    for k in range(5):                      # 5 spokes
        a = k * 2 * math.pi / 5 - math.pi / 2
        s.line(cx + math.cos(a) * 1.5, cy + math.sin(a) * 1.5,
               cx + math.cos(a) * (r - 3.5), cy + math.sin(a) * (r - 3.5), 'n')
    s.ellipse(cx, cy, 1, 1, 'c')
    s.px(cx, cy, 'C')
    s.px(cx - 2, cy - 3, 'C'); s.px(cx - 3, cy - 2, 'C')   # rim glint


def well(s, cx, cy, r=10.6):
    for y in range(int(cy - r), int(cy) + 4):
        for x in range(int(cx - r), int(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= (r + 0.2) ** 2 and s.get(x, y) == '.':
                s.px(x, y, 'B')


def arch(s, cx, cy, r):
    for y in range(int(cy - r) - 1, s.h):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= (r + 0.3) ** 2 or (y >= cy and abs(x - cx) <= r):
                s.px(x, y, '.')


def car_teana(lights=False):
    s = Spr(120, 40)
    wr, wf, wy = 24, 96, 31
    body = [(3, 35), (2, 27), (3, 21), (7, 17), (32, 15), (43, 6), (49, 4), (70, 4), (76, 6),
            (88, 15), (108, 18), (115, 21), (118, 26), (118, 31), (116, 35)]
    s.polyfill(body, 'W')
    arch(s, wr, wy, 10)
    arch(s, wf, wy, 10)
    # lower body shading band + sill
    for x in range(2, 119):
        for y in range(27, 36):
            if s.get(x, y) == 'W':
                s.px(x, y, 'w')
    s.hline(36, 84, 33, 'v')
    # shoulder crease highlight
    s.line(5, 20, 112, 21, 'H')
    s.line(5, 21, 112, 22, 'W')
    # greenhouse (tinted)
    glass = [(35, 15), (45, 7), (50, 5.5), (69, 5.5), (75, 7.5), (85, 15)]
    s.polyfill(glass, 'T')
    s.poly([(35, 15), (45, 7), (50, 5), (69, 5), (75, 7), (85, 15)], 'C')   # chrome trim
    s.hline(35, 85, 15, 'C')
    s.rect(58, 6, 60, 15, 'B')                 # B-pillar
    s.line(44, 15, 49, 7, 'B')                 # C quarter glass divider
    s.line(45, 15, 50, 7, 'B')
    # reflections on glass
    for (x0, x1, y) in ((63, 67, 7), (61, 64, 9), (52, 55, 7)):
        s.line(x0, y + 5, x1, y, 'r')
    s.line(66, 13, 71, 8, 't'); s.line(76, 13, 79, 11, 't')
    # door seams + handles
    s.vline(59, 16, 33, 'v')
    s.line(85, 16, 87, 33, 'v')
    s.line(35, 16, 36, 30, 'v')
    s.hline(36, 36, 31, 'v')
    s.rect(48, 23, 52, 23, 'C'); s.hline(48, 52, 24, 'c')
    s.rect(72, 23, 76, 23, 'C'); s.hline(72, 76, 24, 'c')
    # mirror
    s.polyfill([(81, 12), (86, 11), (88, 15), (83, 16)], 'w'); s.hline(83, 87, 11, 'W'); s.px(84, 16, 'v')
    # roof highlight
    s.hline(50, 69, 5, 'H')
    # chrome side strip low
    s.hline(38, 83, 30, 'C')
    # front: big chrome grille + headlight
    s.rect(112, 23, 118, 29, 'c')
    for y in (23, 25, 27, 29):
        s.hline(112, 118, y, 'C')
    s.vline(112, 23, 29, 'C')
    s.line(95, 18, 112, 22, 'w')               # hood edge
    s.polyfill([(104, 19), (112, 19), (116, 22), (116, 23), (107, 23)], 'L' if lights else 'Y')
    s.hline(108, 115, 23, 'l' if lights else 'y')
    s.px(109, 20, 'H')
    s.rect(110, 31, 115, 32, 'O')               # side marker/fog
    s.hline(110, 115, 32, 'c')
    # rear: tail light + bumper
    s.polyfill([(3, 19), (9, 18), (9, 23), (3, 23)], 'E')
    s.hline(3, 9, 23, 'e')
    s.px(4, 20, 'H')
    s.hline(2, 12, 30, 'v')
    s.rect(3, 33, 8, 34, 'v')                   # exhaust area
    s.rect(9, 34, 12, 34, 'c')
    # fuel cap
    s.rect(18, 19, 20, 20, 'w')
    s.outline('k')
    well(s, wr, wy)
    well(s, wf, wy)
    car_wheel(s, wr, wy)
    car_wheel(s, wf, wy)
    # shadow-ish dark inside arches above wheels
    for cx in (wr, wf):
        for x in range(cx - 8, cx + 9):
            if s.get(x, wy - 9) == 'k':
                pass
    if lights:
        for (x, y) in ((119, 20), (119, 22), (118, 18)):
            s.px(x, y, 'L')
    return s


def car_focus(lights=False):
    s = Spr(108, 40)
    wr, wf, wy = 22, 86, 31
    body = [(3, 35), (2, 26), (3, 19), (6, 12), (12, 7), (20, 5), (44, 3.5), (56, 4), (62, 6), (78, 14),
            (96, 17), (103, 20), (106, 25), (106, 31), (104, 35)]
    s.polyfill(body, 'W')
    arch(s, wr, wy, 10)
    arch(s, wf, wy, 10)
    for x in range(2, 107):
        for y in range(27, 36):
            if s.get(x, y) == 'W':
                s.px(x, y, 'w')
    # strong rising shoulder line
    s.line(5, 21, 100, 19, 'H')
    s.line(5, 22, 100, 20, 'W')
    s.hline(28, 76, 33, 'v')
    s.hline(22, 54, 4, 'H')
    # glass
    glass = [(11, 14), (14, 9), (20, 7), (44, 5.5), (56, 5.5), (62, 7.5), (76, 14)]
    s.polyfill(glass, 'T')
    s.poly([(10, 14), (14, 8), (20, 6), (44, 5), (56, 5), (62, 6.5), (77, 14)], 'B')
    s.hline(10, 77, 14, 'B')
    s.rect(46, 5, 48, 14, 'B')                  # B-pillar
    s.line(26, 14, 24, 7, 'B'); s.line(27, 14, 25, 7, 'B')   # C-pillar
    for (x0, y0, x1, y1) in ((52, 12, 56, 7), (50, 12, 52, 9), (34, 12, 38, 7), (63, 12, 66, 9), (15, 12, 18, 9)):
        s.line(x0, y0, x1, y1, 'r')
    # black roof spoiler over the hatch
    s.polyfill([(5, 9), (11, 5), (22, 3), (23, 5), (12, 8)], 'B')
    s.line(9, 6, 20, 4, 'J')
    # doors / handles
    s.vline(47, 15, 33, 'v'); s.line(77, 15, 78, 33, 'v'); s.line(25, 15, 26, 31, 'v')
    s.hline(36, 40, 22, 'C'); s.hline(36, 40, 23, 'c')
    s.hline(62, 66, 22, 'C'); s.hline(62, 66, 23, 'c')
    # mirror
    s.polyfill([(73, 12), (78, 11), (80, 15), (75, 16)], 'w'); s.hline(75, 79, 11, 'W'); s.px(76, 16, 'v')
    # front: swept headlight + big black trapezoid lower grille
    s.polyfill([(92, 17), (100, 18), (104, 21), (98, 21)], 'L' if lights else 'Y')
    s.hline(98, 104, 21, 'l' if lights else 'y')
    s.px(97, 18, 'H')
    s.polyfill([(100, 25), (107, 24), (107, 31), (101, 31)], 'B')
    s.hline(101, 106, 27, 'J')
    s.rect(101, 32, 103, 32, 'c')               # fog light
    s.hline(104, 106, 23, 'c')                   # upper grille slit
    # rear: tall tail light in hatch corner
    s.polyfill([(3, 16), (9, 15), (13, 19), (3, 21)], 'E')
    s.line(4, 21, 12, 20, 'e')
    s.px(4, 17, 'H'); s.px(5, 17, 'H')
    s.hline(2, 10, 29, 'v')
    s.rect(6, 34, 9, 34, 'c')
    s.outline('k')
    well(s, wr, wy)
    well(s, wf, wy)
    car_wheel(s, wr, wy)
    car_wheel(s, wf, wy)
    if lights:
        for (x, y) in ((107, 18), (107, 20)):
            s.px(x, y, 'L')
    return s


def build_cars(book):
    for name, fn in (('teana', car_teana), ('focus', car_focus)):
        off = fn(False)
        on = fn(True)
        anc = [off.w // 2, off.h - 1]
        book.add('car_' + name, [off], CAR_PAL, fps=1, anchor=anc)
        book.add('car_%s_lights' % name, [off, on], CAR_PAL, fps=3, anchor=anc)


# ================================================================== FLAG + FINISH
FLAG_PAL = {
    'k': OUTLINE, 'w': '#ffffff',
    'R': '#e0182a', 'r': '#a50e20', 'S': '#ff5a5a',
    'B': '#1f4fc0', 'b': '#13307e', 'U': '#4f86f0',
    'O': '#f5a800', 'o': '#c07a00', 'P': '#ffd25a',
    'G': '#f2c94c', 'g': '#b8862a', 'M': '#9aa3b5', 'm': '#5d6578', 'N': '#d4dae4',
    'T': '#d98a6a', 't': '#a85e48', 'Q': '#f0b292',
    'K': '#26222e', 'W': '#f4f4f4', 'X': '#c9ccd6',
    'Y': '#ffe14a', 'L': '#e8442e', 'l': '#2a7fe0',
}


def flag_frame(ph):
    s = Spr(28, 56)
    # flag cloth
    fx0, fy0, fl, fh = 4, 4, 22, 15
    for i in range(fl):
        x = fx0 + i
        amp = 0.6 + 1.6 * i / fl
        off = amp * math.sin(ph + i * 0.42)
        d = math.cos(ph + i * 0.42)
        for j in range(fh):
            band = j // 5
            base, hi, sh = (('R', 'S', 'r'), ('B', 'U', 'b'), ('O', 'P', 'o'))[band]
            c = base
            if d > 0.55:
                c = hi
            elif d < -0.55:
                c = sh
            s.px(x, fy0 + j + round(off), c)
    s.outline('k')
    # pole
    p = Spr(28, 56)
    p.rect(2, 3, 3, 52, 'M')
    p.vline(2, 3, 52, 'N')
    p.ellipse(2.5, 1.5, 1.5, 1.5, 'G')
    p.px(2, 1, 'Y')
    # stone base (tuff)
    p.rect(0, 52, 6, 55, 'T')
    p.hline(0, 6, 52, 'Q')
    p.hline(0, 6, 55, 't')
    p.outline('k')
    s.blit(p, 0, 0)
    return s


def finish_arch():
    s = Spr(96, 80)
    # truss pillars
    for x0 in (2, 82):
        s.rect(x0, 22, x0 + 11, 76, 'm')
        s.rect(x0 + 1, 22, x0 + 10, 76, 'K')
        s.vline(x0, 22, 76, 'M'); s.vline(x0 + 1, 22, 76, 'N')
        s.vline(x0 + 10, 22, 76, 'M'); s.vline(x0 + 11, 22, 76, 'm')
        for y in range(22, 76, 8):
            s.line(x0 + 2, y, x0 + 9, y + 7, 'M')
            s.line(x0 + 9, y, x0 + 2, y + 7, 'm')
            s.hline(x0 + 1, x0 + 10, y, 'N')
            s.hline(x0 + 1, x0 + 10, y + 1, 'm')
        # weighted foot
        s.rect(x0 - 2, 76, x0 + 13, 79, 'K')
        s.hline(x0 - 2, x0 + 13, 76, 'm')
        s.px(x0 + 1, 78, 'Y'); s.px(x0 + 10, 78, 'Y')
    # banner
    s.rect(0, 2, 95, 23, 'R')
    s.hline(0, 95, 2, 'S')
    s.hline(0, 95, 23, 'r')
    # checker strips
    for y0 in (3, 19):
        for x in range(0, 96):
            for y in range(y0, y0 + 3):
                if ((x // 3) + (y0 // 3)) % 2 == 0:
                    s.px(x, y, 'W')
                else:
                    s.px(x, y, 'K')
    # big white ФИНИШ (5x7 font at 2x)
    msg = 'ФИНИШ'
    tw = 5 * 10 + 4 * 3
    x = (96 - tw) // 2
    for ch in msg:
        g = FONT7[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == 'X':
                    s.rect(x + i * 2 + 1, 6 + j * 2 + 1 - 1, x + i * 2 + 2, 6 + j * 2 + 1, 'r')
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == 'X':
                    s.rect(x + i * 2, 5 + j * 2 - 1 + 1, x + i * 2 + 1, 5 + j * 2 + 1, 'w')
        x += 13
    s.outline('k')
    # balloons on top corners
    bl = Spr(96, 80)
    for (cx, cy, c, hc) in ((5, 7, 'R', 'S'), (10, 4, 'B', 'U'), (15, 7, 'O', 'P'),
                            (80, 7, 'O', 'P'), (85, 4, 'R', 'S'), (90, 7, 'B', 'U')):
        pass
    s.blit(bl, 0, 0)
    return s


# ================================================================== FX
FX_PAL = {
    'k': OUTLINE, 'w': '#ffffff',
    'D': '#eadcc0', 'd': '#bfa98a', 'e': '#8f7a62',
    'Y': '#fff27a', 'y': '#ffd23a', 'O': '#ff9a1e', 'o': '#e8551a', 'R': '#b8261c',
    'G': '#9a94a6', 'g': '#6a6476', 'h': '#4a4456', 'H': '#c9c4d2',
    'C': '#bff4ff',
}


def blob(s, pts, c):
    for (x, y, r) in pts:
        s.ellipse(x, y, r, r, c)


def fx_dust():
    frames = []
    for i in range(5):
        s = Spr(16, 10)
        t = i / 4
        r = [2.2, 3, 3, 2.4, 1.4][i]
        spread = 2 + 2.8 * t
        cy = 6.5 - 2 * t
        pts = [(8 - spread, cy, r), (8 + spread, cy, r), (8, cy - 1 - t, r * 1.05)]
        if i >= 3:
            pts = pts[:2]
        blob(s, pts, 'D')
        s.shade('D', None, 'd')
        s.outline('k')
        frames.append(s)
    return frames


def fx_boom():
    import random
    rnd = random.Random(7)
    frames = []
    for i in range(6):
        s = Spr(32, 32)
        if i == 0:
            s.ellipse(15.5, 17, 5, 5, 'Y')
            s.ellipse(15.5, 17, 3, 3, 'w')
            for a in range(8):
                aa = a * math.pi / 4
                s.line(15.5 + math.cos(aa) * 5, 17 + math.sin(aa) * 5,
                       15.5 + math.cos(aa) * 8, 17 + math.sin(aa) * 8, 'Y')
        elif i in (1, 2):
            R = 11 if i == 1 else 13
            pts = [(15.5, 16, R - 3)]
            for k in range(9):
                a = k * 2 * math.pi / 9 + rnd.random() * 0.4
                pts.append((15.5 + math.cos(a) * (R - 5), 16 + math.sin(a) * (R - 5) * 0.9, 4 + rnd.random() * 2))
            blob(s, pts, 'o')
            blob(s, [(x - 0.5, y - 0.8, r * 0.75) for x, y, r in pts], 'O')
            blob(s, [(x - 1, y - 1.5, r * 0.45) for x, y, r in pts], 'y')
            s.ellipse(14.5, 14.5, 4 if i == 1 else 3, 4 if i == 1 else 3, 'Y')
            if i == 1:
                s.ellipse(14, 14, 2, 2, 'w')
            if i == 2:
                for (x, y) in ((6, 24), (25, 23), (10, 26)):
                    s.ellipse(x, y, 2.5, 2, 'g')
        elif i == 3:
            pts = []
            for k in range(7):
                a = k * 2 * math.pi / 7 + 0.3
                pts.append((15.5 + math.cos(a) * 8, 15 + math.sin(a) * 7, 4 + rnd.random() * 1.5))
            pts.append((15.5, 14, 5))
            blob(s, pts, 'g')
            blob(s, [(x - 0.7, y - 0.8, r * 0.7) for x, y, r in pts], 'G')
            blob(s, [(x + 0.5, y + 1, r * 0.55) for x, y, r in pts[:5]], 'o')
            blob(s, [(x + 0.5, y + 1, r * 0.3) for x, y, r in pts[:5]], 'O')
            s.ellipse(15.5, 15, 2.5, 2.5, 'o'); s.ellipse(15.5, 15, 1.2, 1.2, 'y')
        elif i == 4:
            pts = [(9, 12, 4.5), (20, 10, 5), (15, 18, 4), (24, 19, 3.5), (7, 20, 3)]
            blob(s, pts, 'h')
            blob(s, [(x - 0.7, y - 1, r * 0.75) for x, y, r in pts], 'g')
            blob(s, [(x - 1.2, y - 1.6, r * 0.35) for x, y, r in pts], 'G')
            s.px(15, 19, 'O'); s.px(22, 12, 'o'); s.px(9, 14, 'O')
        else:
            pts = [(10, 9, 3), (21, 7, 3.5), (16, 14, 2.5)]
            blob(s, pts, 'g')
            blob(s, [(x - 0.6, y - 0.8, r * 0.6) for x, y, r in pts], 'G')
        s.outline('k')
        # flying debris chunks
        if i in (1, 2, 3):
            d = [(4, 5), (27, 4), (2, 15), (29, 14), (6, 28), (26, 29)]
            for (x, y) in d[: 2 + i]:
                sp = (i - 1) * 2
                xx = x + (-sp if x < 16 else sp) // 2
                yy = y + (-sp if y < 16 else sp) // 2
                s.px(xx, yy, 'O' if i < 3 else 'h')
                s.px(xx + 1, yy, 'o' if i < 3 else 'g')
        frames.append(s)
    return frames


def fx_smoke():
    frames = []
    for i, r in enumerate((1.5, 2.5, 3, 2.2)):
        s = Spr(8, 8)
        s.ellipse(3.5, 4 - i * 0.3, r, r, 'G')
        if i >= 2:
            s.ellipse(2.5, 3, r * 0.5, r * 0.5, 'H')
        s.shade('G', 'H', 'g')
        if i == 3:
            s.px(3, 4, '.'); s.px(4, 3, '.')
        s.outline('k')
        frames.append(s)
    return frames


def fx_sparkle():
    frames = []
    shapes = [
        ['...', '.w.', '...'],
        ['.Y.', 'YwY', '.Y.'],
        ['..Y..', '..Y..', 'YYwYY', '..Y..', '..Y..'],
        ['Y...Y', '.y.y.', '..w..', '.y.y.', 'Y...Y'],
    ]
    for sh in shapes:
        s = Spr(7, 7)
        n = len(sh)
        o = (7 - n) // 2
        s.ascii(o, o, '\n'.join(sh))
        s.outline('k')
        frames.append(s)
    return frames


def fx_hit():
    frames = []
    for i in range(3):
        s = Spr(12, 12)
        c = 5.5
        if i == 0:
            s.ellipse(c, c, 2.5, 2.5, 'Y'); s.ellipse(c, c, 1.2, 1.2, 'w')
        elif i == 1:
            for a in range(8):
                aa = a * math.pi / 4 + math.pi / 8
                L = 5 if a % 2 == 0 else 3.5
                s.line(c, c, c + math.cos(aa) * L, c + math.sin(aa) * L, 'y')
            s.ellipse(c, c, 2.2, 2.2, 'Y')
            s.ellipse(c, c, 1, 1, 'w')
        else:
            for a in range(8):
                aa = a * math.pi / 4 + math.pi / 8
                s.line(c + math.cos(aa) * 3.5, c + math.sin(aa) * 3.5, c + math.cos(aa) * 5.2, c + math.sin(aa) * 5.2, 'O' if a % 2 else 'y')
        s.outline('k')
        frames.append(s)
    return frames


# ================================================================== PROPS
PROP_PAL = {
    'k': OUTLINE, 'w': '#ffffff',
    'I': '#3a4a48', 'i': '#26302f', 'J': '#5a6e6a',          # cast iron (dark green-grey)
    'L': '#fff1a0', 'l': '#ffd860', 'C': '#e8eef4',
    'W': '#b8743e', 'v': '#8a5228', 'V': '#d89a5e',          # wood
    'G': '#4caf50', 'g': '#2f7d3a', 'H': '#86d65a', 'h': '#1f5a2c',  # foliage
    'T': '#7a4e30', 't': '#55341f', 'U': '#9a6a44',          # trunk
    'S': '#d98a6a', 's': '#a85e48', 'Q': '#f0b292', 'q': '#7e4436',  # tuff stone
    'A': '#7fd0ff', 'a': '#3a9ad8', 'Z': '#e8f8ff',          # water
    'R': '#d8303a', 'r': '#98182c', 'P': '#ff6a5a',
    'M': '#9aa3b5', 'm': '#5d6578', 'N': '#d4dae4',
    'B': '#2c6aa0', 'b': '#1d4a74', 'E': '#f0e6d0', 'e': '#c9bfa6',
    'Y': '#ffd23a', 'y': '#e0951c', 'F': '#ff7aa8', 'f': '#c43a80', 'O': '#ff9a2a',
}


def prop_lamp():
    s = Spr(12, 50)
    # base
    s.rect(3, 44, 8, 49, 'I')
    s.rect(2, 47, 9, 49, 'I')
    s.hline(4, 7, 43, 'I')
    # fluted post
    s.rect(5, 14, 6, 43, 'I')
    s.vline(5, 14, 43, 'J')
    for y in (20, 32, 40):
        s.hline(4, 7, y, 'I')
    # lantern bracket + head
    s.rect(4, 12, 7, 13, 'I')
    s.polyfill([(2, 5), (10, 5), (9, 11), (3, 11)], 'L')
    s.vline(5, 5, 11, 'I'); s.vline(6, 5, 11, 'l')
    s.hline(2, 9, 11, 'I')
    s.polyfill([(1, 4), (11, 4), (8, 1), (4, 1)], 'I')   # cap
    s.px(6, 0, 'I')
    s.px(3, 6, 'w')
    s.shade('I', 'J', 'i', group='IJiLlw')
    s.outline('k')
    return s


def prop_bench():
    s = Spr(34, 16)
    for y in (2, 4):                   # backrest slats
        s.rect(2, y, 31, y + 1, 'W')
        s.hline(2, 31, y, 'V')
    s.rect(2, 9, 31, 10, 'W')          # seat
    s.hline(2, 31, 9, 'V')
    s.hline(2, 31, 11, 'v')
    for x in (4, 28):                  # cast iron frame
        s.vline(x, 1, 15, 'I')
        s.vline(x + 1, 1, 15, 'i')
        s.line(x, 12, x - 2, 15, 'I')
        s.line(x + 1, 12, x + 3, 15, 'I')
    s.vline(16, 6, 9, 'I')
    s.outline('k')
    return s


def prop_bin():
    s = Spr(14, 18)
    s.polyfill([(2, 4), (12, 4), (11, 17), (3, 17)], 'J')
    for x in (4, 7, 10):
        s.vline(x, 6, 15, 'I')
    s.rect(1, 2, 12, 4, 'I')            # rim
    s.hline(1, 12, 2, 'J')
    s.rect(4, 0, 9, 1, 'I')
    s.px(3, 5, 'C')
    # a bit of litter peeking out
    s.px(8, 1, 'E'); s.px(9, 0, 'R')
    s.shade('J', None, 'I', group='JIiCER')
    s.outline('k')
    return s


def prop_kiosk():
    s = Spr(42, 42)
    # body (painted blue-green metal)
    s.rect(3, 12, 38, 38, 'B')
    s.hline(3, 38, 12, 'b')
    # window with magazines
    s.rect(6, 15, 35, 27, 'Z')
    s.rect(7, 16, 34, 26, 'a')
    mags = 'RYFOEPGR'
    for i, c in enumerate(mags):
        x = 8 + i * 3 + (i // 4)
        s.rect(x, 18 + (i % 2), x + 2, 25, c)
        s.hline(x, x + 2, 18 + (i % 2), 'w')
    s.line(10, 16, 16, 26, 'Z')         # glass glint
    s.hline(5, 36, 28, 'E')             # counter
    s.hline(5, 36, 29, 'e')
    # roof + striped awning
    s.rect(1, 6, 40, 8, 'b')
    for x in range(1, 41):
        for y in range(9, 13):
            s.px(x, y, 'R' if (x // 4) % 2 == 0 else 'E')
    for x in range(1, 41, 4):           # scalloped edge
        s.px(x + 1, 13, 'R'); s.px(x + 2, 13, 'R')
    s.hline(1, 40, 6, 'B')
    # sign
    s.rect(10, 1, 31, 5, 'E')
    s.hline(10, 31, 5, 'e')
    text(s, 12, 1, 'PRESS', 'r')
    # flower buckets in front
    for i, (fc, hx) in enumerate((('F', 4), ('Y', 10), ('R', 30), ('O', 36))):
        s.rect(hx, 34, hx + 4, 39, 'M')
        s.hline(hx, hx + 4, 34, 'N')
        s.ellipse(hx + 2, 31, 2.6, 2.2, 'g')
        for (dx, dy) in ((0, 30), (2, 29), (4, 30), (1, 32), (3, 31)):
            s.px(hx + dx, dy, fc)
    s.shade('B', None, 'b', group='BbZaRYFOEPGwEe')
    s.outline('k')
    return s


def prop_tree():
    s = Spr(42, 58)
    # trunk + roots
    s.rect(18, 34, 22, 55, 'T')
    s.vline(18, 34, 55, 'U')
    s.vline(22, 34, 55, 't')
    s.line(17, 55, 14, 57, 'T', 2)
    s.line(23, 55, 26, 57, 'T', 2)
    s.line(20, 40, 14, 32, 'T', 2)       # branches
    s.line(21, 38, 27, 31, 'T', 2)
    # crown: cluster of blobs
    blobs = [(20, 18, 13), (10, 24, 8), (31, 23, 8.5), (14, 11, 8), (27, 10, 8), (20, 28, 8), (21, 6, 6)]
    for (x, y, r) in blobs:
        s.ellipse(x, y, r, r * 0.92, 'G')
    for y in range(s.h):                 # under-side of the crown in shadow
        for x in range(s.w):
            if s.g[y, x] == 'G' and (s.get(x, y + 3) not in 'GHgh' or y > 27):
                s.g[y, x] = 'g'
    s.shade('G', 'H', 'g', group='GHgh', depth=1)
    # leaf clumps texture + inner shadows
    for (x, y) in ((12, 16), (24, 14), (17, 24), (29, 20), (9, 27), (22, 30), (20, 9), (33, 26), (14, 30)):
        s.px(x, y, 'g'); s.px(x + 1, y, 'g'); s.px(x, y + 1, 'h')
    for (x, y) in ((11, 8), (15, 6), (8, 18), (19, 3), (24, 6)):
        s.px(x, y, 'H'); s.px(x + 1, y + 1, 'H')
    s.outline('k')
    return s


def prop_fountain(fr):
    s = Spr(16, 24)
    # tuff stone pulpulak column with small basin
    s.rect(3, 6, 10, 21, 'S')
    s.rect(2, 4, 11, 6, 'S')            # top cap
    s.hline(2, 11, 4, 'Q')
    s.rect(1, 19, 12, 23, 'S')          # basin
    s.hline(1, 12, 19, 'Q')
    s.rect(2, 20, 11, 20, 'a')          # water in basin
    s.vline(3, 7, 18, 'Q')
    s.vline(10, 7, 18, 's')
    # carved ornament (Armenian cross-stone motif)
    s.vline(6, 9, 14, 'q'); s.hline(5, 7, 11, 'q')
    s.px(5, 9, 'q'); s.px(7, 9, 'q'); s.px(5, 14, 'q'); s.px(7, 14, 'q')
    s.px(8, 12, 's')
    # spout
    s.rect(10, 9, 11, 9, 'M')
    s.shade('S', 'Q', 's', group='SQsqMaA')
    s.outline('k')
    # water arc (no outline: thin stream)
    w = Spr(16, 24)
    w.px(12, 8, 'A'); w.px(13, 8, 'A'); w.px(14, 9, 'A')
    for y in range(9, 19):
        w.px(13, y, 'a'); w.px(14, y, 'A')
    for y in range(9 + fr * 2, 19, 4):    # moving highlights in the stream
        w.px(14, y, 'Z')
    w.outline('b')
    w.px(12, 19, 'Z' if fr else 'A'); w.px(11, 18 - fr, 'Z')
    w.px(4 + fr * 3, 20, 'Z')
    s.blit(w, 0, 0)
    return s


def prop_hydrant():
    s = Spr(12, 16)
    s.rect(3, 5, 8, 13, 'R')
    s.rect(2, 13, 9, 15, 'R')
    s.ellipse(5.5, 4, 3, 2, 'R')
    s.rect(5, 0, 6, 1, 'R')
    s.rect(1, 7, 10, 8, 'M')            # side caps
    s.px(0, 7, 'M'); s.px(11, 7, 'M')
    s.rect(4, 9, 7, 10, 'M')            # front cap
    s.vline(4, 4, 12, 'P')
    s.px(5, 3, 'P')
    s.shade('R', None, 'r', group='RrPM')
    s.shade('M', 'N', 'm', group='RrPMNm')
    s.outline('k')
    return s


def build_flag(book):
    frames = [flag_frame(k * math.pi / 2) for k in range(4)]
    book.add('flag_wave', frames, FLAG_PAL, fps=8, anchor=[3, 55])
    book.add('finish_arch', [finish_arch()], FLAG_PAL, fps=1, anchor=[48, 79])


def build_fx(book):
    book.add('fx_dust', fx_dust(), FX_PAL, fps=14, anchor=[8, 9])
    book.add('fx_boom', fx_boom(), FX_PAL, fps=14, anchor=[16, 16])
    book.add('fx_smoke', fx_smoke(), FX_PAL, fps=8, anchor=[4, 4])
    book.add('fx_sparkle', fx_sparkle(), FX_PAL, fps=12, anchor=[3, 3])
    book.add('fx_hit', fx_hit(), FX_PAL, fps=18, anchor=[6, 6])


def build_props(book):
    for name, fn in (('lamp', prop_lamp), ('bench', prop_bench), ('bin', prop_bin),
                     ('kiosk', prop_kiosk), ('tree', prop_tree), ('hydrant', prop_hydrant)):
        im = fn()
        book.add('prop_' + name, [im], PROP_PAL, fps=1, anchor=[im.w // 2, im.h - 1])
    fr = [prop_fountain(0), prop_fountain(1)]
    book.add('prop_fountain', fr, PROP_PAL, fps=5, anchor=[7, 23])


# ================================================================== BUILD
def build_items(book):
    for name, fn in (('boom', item_boom), ('rush', item_rush), ('vip', item_vip),
                     ('terea', item_terea), ('shampoo', item_shampoo)):
        base = fn()
        anc = [base.w // 2, base.h - 1]
        book.add('item_' + name, [base], ITEM_PAL, fps=1, anchor=anc)
        book.add('item_%s_shine' % name, shine_frames(base), ITEM_PAL, fps=10, anchor=anc)


def build_proj(book):
    book.add('poop', [poop()], PROJ_PAL, fps=1, anchor=[3, 3])
    book.add('poop_splat', poop_splat(), PROJ_PAL, fps=10, anchor=[6, 5])
    book.add('slipper_spin', slipper_spin(), PROJ_PAL, fps=16, anchor=[6, 6])
    book.add('disc_spin', disc_spin(), PROJ_PAL, fps=16, anchor=[6, 6])
    book.add('note', note(), PROJ_PAL, fps=6, anchor=[5, 6])


BUILDERS = [('items', build_items), ('proj', build_proj), ('cars', build_cars),
            ('flag', build_flag), ('fx', build_fx), ('props', build_props)]


def main(only=None):
    book = Book(ASSETS, 'objects.json', PREV)
    for name, fn in BUILDERS:
        if only and name not in only:
            continue
        fn(book)
    if not only:
        book.save()


if __name__ == '__main__':
    main(sys.argv[1:] or None)
