#!/usr/bin/env python3
"""Hero sprites for SHAMPOO v2, drawn natively in pixels (no downscaled puppet).

Each frame is built from hand-drawn pixel parts (head, torso, shoes) and limbs rendered as shaded pixel
capsules from a pose: hip/knee/shoulder/elbow angles. Every part carries its own 1px outline and parts are
stacked back-to-front (far arm, far leg, torso, near leg, head, near arm), so limbs stay readable over the body.
Grounded poses put the lowest foot on the baseline automatically, so feet never float or sink.

Run:  python3 tools/draw_heroes.py [preview_dir]
Writes assets/hero_<hero>_<anim>.png and assets/heroes.json (meta per frame:
[mouthX, mouthY, headTopX, headTopY, earX, earY, handX, handY, canTip]).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets')
OL = '#1a1024'
W, H = 56, 66              # one canvas for every frame
GROUND = H - 2             # feet rest on this row
AX = 26                    # anchor x (hip centre when standing)

# ------------------------------------------------------------------ palettes (sampled from Azat's character sheets)
SKIN = {'L': '#f4c8a4', 'S': '#e2a580', 's': '#bf7a58', 'q': '#8a4c34'}
COMMON = {'k': OL, 'e': '#1a1024', 'w': '#ffffff', 'm': '#5a1a1a', 'r': '#c03a3a', 'X': '#141218', **SKIN}
HERO = {
    'azat': {
        'pal': {**COMMON,
                'H': '#3c2416', 'h': '#6a4228', 'I': '#1e120c',           # dark brown quiff
                'B': '#2c1a12', 'b': '#4a2e20',                           # full dark beard
                'C': '#ece4d8', 'c': '#cfc3b2', 'D': '#a3947f', 'U': '#fbf7f0',  # oversized cream hoodie
                'P': '#2a2422', 'p': '#3d3431', 'O': '#17131a',           # black baggy cargo
                'F': '#f6f6f8', 'f': '#cfd0da', 'G': '#9d9eac', 'Z': '#d9dae2'},  # chunky white sneakers
        'sleeve': ('U', 'C', 'c'), 'sleeve_far': ('c', 'c', 'D'),
        'pants': ('p', 'P', 'O'), 'pants_far': ('P', 'O', 'O'),
        'watch': True,
    },
    'arsen': {
        'pal': {**COMMON,
                'H': '#24222a', 'h': '#3a3742', 'I': '#0f0d12', 'y': '#e0b44a',  # black bucket hat, gold logo
                'B': '#24170f', 'b': '#3e2a1e', 'Y': '#2e1e14',           # beard, side hair
                'C': '#2a2730', 'c': '#1c1a21', 'D': '#121015', 'U': '#3e3a46',  # black overshirt
                'T': '#141216', 't': '#ff8a2a', 'o': '#d8482a', 'g': '#ffd05a',  # black tee, sunset print
                'P': '#28252b', 'p': '#3a363e', 'O': '#141217',           # black cargo
                'F': '#2a2830', 'f': '#ececf0', 'G': '#f0ece2', 'Z': '#1c1a20'},  # black/white sneakers
        'sleeve': ('U', 'C', 'c'), 'sleeve_far': ('c', 'c', 'D'),
        'pants': ('p', 'P', 'O'), 'pants_far': ('P', 'O', 'O'),
        'watch': True,
    },
}

# ------------------------------------------------------------------ hand-drawn parts, 3/4 view facing right
HEADS = {
    'azat': dict(art="""
.......hhhhh....
.....hhHHHHHh...
...hhHHHHHHHHh..
..hHHHHHHHHHHH..
.IHHHHHHHHHHHH..
.IIHHHHHHHHHH...
.IIIISSSSSSSS...
.IIsSSIIISSIIS..
.IsLsSSeSSSeSS..
.IssSSSSSSSsSSS.
.IBsSSSSSSSsSS..
.IBBsBBBBBBBBB..
..BBBBBBmmmBBB..
..BBBBBBBBBBBB..
...BBBBBBBBBB...
....BBBBBBB.....
""", neck=(7, 15), mouth=(10, 12), ear=(3, 8), top=(7, 0)),
    'arsen': dict(art="""
....hhhhhhh.....
...hHHHHHHHh....
..hHHHHHHHHHh...
..HHHHHHHHyHH...
.hHHHHHHHHHHHh..
IIIIIIIIIIIIIIII
IIYYSSSSSSSSSII.
.YYsSSSIISSIIS..
.YsLwSSeSSSeSS..
.YsSsSSSSSSSsSS.
.YBsSSSSSSSsSS..
.BBBsBBBBBBBBB..
..BBBBBBmmBBBB..
..BBBBBBBBBBBB..
...BBBBBBBBBB...
....BBBBBBB.....
""", neck=(7, 15), mouth=(10, 12), ear=(3, 8), top=(7, 0)),
}
# torsos: hip anchor (x, y) and near/far shoulder points in torso coords
TORSOS = {
    'azat': dict(art="""
......cCCCCCc.......
....cCUUUUUUCCc.....
..cCUUUCDDDDCUCCc...
.cCUUUUCDDDDCCCCCc..
cCUUUUUUCCCCCCCCCCc.
cCUUUUUCCCCDCDCCCCc.
cCUUUUCCCCCDCDCCCCc.
cCUUUUCCCCCDCDCCCCc.
cCUUUCCCCCCDCDCCCcc.
cCUUUCCCCCCXCXCCCcc.
cCUUCCCCCCCCCCCCCcc.
cCUUCCCCCCCCCCCCCcc.
cCUCCCCCCCCCCCCCCcc.
cCUCCCCCCCCCCCCCCcc.
cCUCCCCDDDDDDDDCCcc.
cCCCCCCDCCCCCCDCCcc.
cCCCCCCDCCCCCCDCCcc.
cCCCCCCDDCCCCDDCCcc.
cCCCCCCCCCCCCCCCCcc.
.cDDDDDDDDDDDDDDDDc.
.cDcDcDcDcDcDcDcDcc.
""", hip=(9, 20), sh=(5, 5), sh_far=(15, 5), neck=(9, 2)),
    'arsen': dict(art="""
.......UCTTTTCU.......
.....cUUCTTTTTCUUc....
...cCUUUCTTTTTCCUCCc..
..cCUUUUCTttttTCCCCCc.
.cCUUUUUCTggggTCCCCCCc
.cCUUUUUCToooTTCCCCCCc
cCUDDDDUCTgttgTCDDDDCc
cCUDCCDUCTttttTCDCCDCc
cCUCCCCCCTTggTTCCCCCCc
cCUCCCCCCTTTTTTCCCCCCc
cCUCCCCCCTTTTTTCCCCCCc
cCUCCCCCCTTTTTTCCCCCCc
cCCCCCCCCTTTTTTCCCCCcc
cCCCCCCCCTTTTTTCCCCCcc
cCCCCCCCCTTTTTTCCCCCcc
cCCCCCCCCTTTTTTCCCCCcc
cCCCCCCCCTTTTTTCCCCCcc
cCCCCCCCCTTTTTTCCCCCcc
cCCCCCCCcTTTTTTcCCCCcc
.ccccccccTTTTTTccccccc
.........PPPPPP.......
""", hip=(11, 21), sh=(5, 5), sh_far=(17, 5), neck=(11, 2)),
}
# chunky sneakers, ankle at the given point: flat, toe-down (heel raised), heel-strike (toe up), in the air
SHOES = {
    'flat': ("""
...FFFFF....
..FFFFFFFF..
.FFFFFFFFFF.
FFFFfFFFfFFf
GGGGGGGGGGGG
""", (4, 0)),
    'toe': ("""
..FFFF......
..FFFFFF....
...FFFFFFF..
....FFFfFFFf
.....GGGGGGG
""", (3, 0)),
    'heel': ("""
..FFFFF..ff.
.FFFFFFFFff.
FFFFFFFFFf..
FFFFfFFFf...
GGGGGGGG....
""", (4, 0)),
    'air': ("""
..FFFF......
..FFFFFFFF..
...FFFFFFFFf
....FfFFFFf.
.....GGGGGG.
""", (3, 0)),
}


def art(s):
    rows = s.strip('\n').split('\n')
    w = max(len(r) for r in rows)
    return np.array([list(r.ljust(w, '.')) for r in rows])


class Canvas:
    def __init__(self):
        self.g = np.full((H, W), '.', dtype='<U1')

    def layer(self, part, x0, y0):
        """Composite a part grid (already outlined) at (x0, y0)."""
        h, w = part.shape
        for y in range(h):
            for x in range(w):
                c = part[y, x]
                if c != '.' and 0 <= y0 + y < H and 0 <= x0 + x < W:
                    self.g[y0 + y, x0 + x] = c


def outline(g):
    filled = g != '.'
    out = np.zeros_like(filled)
    out[1:] |= filled[:-1]; out[:-1] |= filled[1:]; out[:, 1:] |= filled[:, :-1]; out[:, :-1] |= filled[:, 1:]
    g = g.copy()
    g[out & ~filled] = 'k'
    return g


def pad(g, n=1):
    return np.pad(g, n, constant_values='.')


def capsules(segs, cols):
    """Rasterise a chain of capsules [(x0,y0,x1,y1,r), ...] into a grid with rim shading.
    cols = (light, base, shade). Light comes from the top-left."""
    lt, base, sh = cols
    g = np.full((H, W), '.', dtype='<U1')
    inside = np.zeros((H, W), bool)
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = xx + 0.5, yy + 0.5
    for x0, y0, x1, y1, r in segs:
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-6
        t = np.clip(((cx - x0) * dx + (cy - y0) * dy) / L2, 0, 1)
        px, py = x0 + t * dx, y0 + t * dy
        inside |= (cx - px) ** 2 + (cy - py) ** 2 <= r * r
    g[inside] = base
    # rim light on pixels whose up or left neighbour is empty, shade on down/right
    up = np.zeros_like(inside); up[1:] = inside[:-1]
    lf = np.zeros_like(inside); lf[:, 1:] = inside[:, :-1]
    dn = np.zeros_like(inside); dn[:-1] = inside[1:]
    rt = np.zeros_like(inside); rt[:, :-1] = inside[:, 1:]
    g[inside & (~dn | ~rt)] = sh
    g[inside & (~up | ~lf) & dn & rt] = lt
    return g


def rot(a):
    return math.sin(math.radians(a)), math.cos(math.radians(a))


# ------------------------------------------------------------------ pose -> frame
LEG = (10.0, 10.0)      # thigh, shin (hip -> knee -> ankle)
ARM = (8.5, 8.0)      # upper arm, forearm (shoulder -> elbow -> wrist)


def leg_points(hip, thigh, knee):
    s, c = rot(thigh)
    K = (hip[0] + LEG[0] * s, hip[1] + LEG[0] * c)
    s2, c2 = rot(thigh - knee)
    A = (K[0] + LEG[1] * s2, K[1] + LEG[1] * c2)
    return K, A


def arm_points(S, up, elbow):
    s, c = rot(up)
    E = (S[0] + ARM[0] * s, S[1] + ARM[0] * c)
    s2, c2 = rot(up + elbow)
    Wr = (E[0] + ARM[1] * s2, E[1] + ARM[1] * c2)
    return E, Wr


def ik(S, T):
    """Two-bone arm from shoulder S reaching for T, elbow hanging down. Returns (elbow, wrist)."""
    L1, L2 = ARM
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = max(1e-3, min(math.hypot(dx, dy), L1 + L2 - 0.05))
    a = math.atan2(dy, dx)
    b = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    c1 = (S[0] + L1 * math.cos(a + b), S[1] + L1 * math.sin(a + b))
    c2 = (S[0] + L1 * math.cos(a - b), S[1] + L1 * math.sin(a - b))
    E = c1 if c1[1] > c2[1] else c2
    e = math.atan2(T[1] - E[1], T[0] - E[0])
    return E, (E[0] + L2 * math.cos(e), E[1] + L2 * math.sin(e))


def render(hero, P):
    """P: pose dict. Angles in degrees; thigh/arm angles measured from straight down, positive = forward.
    knee = how far the shin folds back, elbow = how far the forearm folds forward/up."""
    D = HERO[hero]
    lean = P.get('lean', 0)                 # torso lean forward in px over its height
    legN, legF = P['legN'], P['legF']        # (thigh, knee, shoe)
    # place hips so the lowest foot touches the ground
    hip0 = (0.0, 0.0)
    lows = []
    for th, kn, shoe in (legN, legF):
        K, A = leg_points(hip0, th, kn)
        lows.append(A[1] + art(SHOES[shoe][0]).shape[0] - 1)
    if P.get('air') is None:
        hipY = GROUND - max(lows) + P.get('bob', 0)
    else:
        hipY = GROUND - 24 - P['air']
    hip = (AX + P.get('dx', 0), hipY)
    cv = Canvas()
    T = TORSOS[hero]
    tor = art(T['art'])
    # lean: shear torso rows forward towards the top
    th_, tw_ = tor.shape
    sheared = np.full((th_, tw_ + 4), '.', dtype='<U1')
    for y in range(th_):
        off = int(round(lean)) if y < T['hip'][1] * 0.5 else int(round(lean * 0.5))
        for x in range(tw_):
            if 0 <= x + off + 2 < tw_ + 4:
                sheared[y, x + off + 2] = tor[y, x]
    tor = sheared
    tx0 = int(round(hip[0] - T['hip'][0] - 2))
    ty0 = int(round(hip[1] - T['hip'][1] + P.get('breath', 0) * 0))
    br = P.get('breath', 0)
    shoff = int(round(lean))
    SN = (tx0 + 2 + T['sh'][0] + shoff + 0.5, ty0 + T['sh'][1] - br + 0.5)
    SF = (tx0 + 2 + T['sh_far'][0] + shoff + 0.5, ty0 + T['sh_far'][1] - br + 0.5)

    def draw_leg(spec, cols, far):
        th, kn, shoe = spec
        hp = (hip[0] + (3.2 if far else -3.2), hip[1])
        K, A = leg_points(hp, th, kn)
        g = capsules([(hp[0], hp[1], K[0], K[1], 4.7), (K[0], K[1], A[0], A[1], 4.1)], cols)
        # cargo pocket on the near thigh
        if not far:
            mx, my = int(round(hp[0] + (K[0] - hp[0]) * 0.55)) - 1, int(round(hp[1] + (K[1] - hp[1]) * 0.45))
            for yy in range(my, my + 5):
                for xx in range(mx - 2, mx + 2):
                    if 0 <= yy < H and 0 <= xx < W and g[yy, xx] != '.':
                        edge = yy in (my, my + 4) or xx in (mx - 2, mx + 1)
                        g[yy, xx] = cols[2] if edge else cols[0] if yy == my + 1 else cols[1]
        sa, (ax, ay) = art(SHOES[shoe][0]), SHOES[shoe][1]
        if far:
            sa = np.where(sa == 'F', 'Z', sa)
        sx, sy = int(round(A[0])) - ax, int(round(A[1])) - ay
        for y in range(sa.shape[0]):
            for x in range(sa.shape[1]):
                if sa[y, x] != '.' and 0 <= sy + y < H and 0 <= sx + x < W:
                    g[sy + y, sx + x] = sa[y, x]
        cv.layer(outline(g), 0, 0)

    def draw_arm(S, spec, cols, far):
        if isinstance(spec, dict):                     # reach for a point near the mouth
            mx, my = mouth
            tx, ty = (mx + spec.get('dx', 0), my + spec.get('dy', 0))
            E, Wr = ik(S, (tx, ty))
            ang = math.atan2(Wr[1] - E[1], Wr[0] - E[0])
            s, c = math.cos(ang), math.sin(ang)
        else:
            up, el = spec[:2]
            E, Wr = arm_points(S, up, el)
            s, c = rot(up + el)
        g = capsules([(S[0], S[1], E[0], E[1], 3.2), (E[0], E[1], Wr[0], Wr[1], 2.8)], cols)
        if not isinstance(spec, dict) and len(spec) > 2 and spec[2] == 'pocket':      # hand tucked in the trouser pocket
            cv.layer(outline(g), 0, 0)
            return (-1, -1)
        # hand
        Hc = (Wr[0] + 2.0 * s, Wr[1] + 2.0 * c)
        hg = capsules([(Wr[0], Wr[1], Hc[0], Hc[1], 2.1)], ('S', 'S', 's') if not far else ('s', 's', 'q'))
        g[hg != '.'] = hg[hg != '.']
        if D['watch'] and not far:
            wx, wy = int(round(Wr[0] - 0.8 * s)), int(round(Wr[1] - 0.8 * c))
            if 0 <= wy < H and 0 <= wx < W:
                g[wy, wx] = 'X'
        cv.layer(outline(g), 0, 0)
        return Hc

    armN, armF = P['armN'], P['armF']
    if armF:
        draw_arm(SF, armF, [HERO[hero]['sleeve_far'][i] for i in range(3)], True)
    draw_leg(legF, D['pants_far'], True)
    cv.layer(outline(pad(tor)), tx0 - 1, ty0 - 1 - br)
    draw_leg(legN, D['pants'], False)
    # head on the neck point at the torso top
    hd = HEADS[hero]
    ha = art(hd['art'])
    if P.get('head') == 'back':     # tipped back (drinking): shift top rows back
        hb = np.full((ha.shape[0], ha.shape[1] + 2), '.', dtype='<U1')
        for y in range(ha.shape[0]):
            off = 2 - int(round(2 * (ha.shape[0] - y) / ha.shape[0]))
            hb[y, off:off + ha.shape[1]] = ha[y]
        ha = hb
    if P.get('mouth'):
        mx_, my_ = hd['mouth']
        ha = ha.copy(); ha[my_, mx_ - 1] = 'm'; ha[my_ + 1, mx_ - 1] = 'm'; ha[my_ + 1, mx_] = 'm'
    nx = tx0 + 2 + T['neck'][0] + int(round(lean * 1.2)) + P.get('hdx', 0)
    ny = ty0 + T['neck'][1] - br + P.get('hdy', 0)
    hx0, hy0 = nx - hd['neck'][0], ny - hd['neck'][1]
    cv.layer(outline(pad(ha)), hx0 - 1, hy0 - 1)
    mouth = (hx0 + hd['mouth'][0], hy0 + hd['mouth'][1])
    hand = (-1, -1)
    if armN:
        hand = draw_arm(SN, armN, [HERO[hero]['sleeve'][i] for i in range(3)], False)
    # props drawn in-sprite: cigarette / IQOS stick / lighter
    prop = P.get('prop')
    if prop:
        hx, hy = int(round(hand[0])), int(round(hand[1]))
        def put(x, y, c):
            if 0 <= y < H and 0 <= x < W:
                cv.g[y, x] = c
        if prop in ('cig', 'cigHand'):
            for i in range(1, 5): put(hx + i, hy - 1, 'w')
            put(hx + 5, hy - 1, 'r')
        elif prop == 'stick':
            for i in range(1, 4): put(hx + i, hy - 1, 'w')
            put(hx + 4, hy - 1, 'f')
        elif prop == 'lighter':
            for d in (1, 2): put(hx, hy - d, 'r')
            if P.get('flame'):
                put(hx, hy - 3, 'y' if 'y' in D['pal'] else 'h'); put(hx, hy - 4, 'w')
    if P.get('cig'):
        mx, my = mouth
        for i in range(1, 5):
            if 0 <= mx + i < W: cv.g[my, mx + i] = 'w'
        cv.g[my, mx + 5] = 'r' if P['cig'] == 1 else 'y' if 'y' in D['pal'] else 'r'
    meta = [mouth[0], mouth[1], hx0 + hd['top'][0], hy0 + hd['top'][1], hx0 + hd['ear'][0], hy0 + hd['ear'][1],
            int(round(hand[0])), int(round(hand[1])), P.get('tip', 0)]
    return cv.g, meta


# ------------------------------------------------------------------ animation tables
def cyc(n, i):
    return i % n


def walk():
    # thigh, knee for one leg over 8 frames starting at its front contact
    T = [(24, 4, 'heel'), (16, 18, 'flat'), (4, 6, 'flat'), (-10, 4, 'flat'), (-22, 14, 'toe'), (-14, 46, 'air'), (6, 52, 'air'), (22, 22, 'air')]
    A = [-28, -18, -4, 12, 28, 18, 4, -12]       # near arm swing (opposite to near leg)
    out = []
    for i in range(8):
        n, f = T[i], T[(i + 4) % 8]
        out.append(dict(legN=n, legF=f, armN=(A[i], 18 + max(0, A[i]) * 0.6), armF=(-A[i], 18 + max(0, -A[i]) * 0.6),
                        lean=1, bob=[0, 1, 0, -1, 0, 1, 0, -1][i]))
    return out


def run():
    T = [(38, 10, 'heel'), (16, 42, 'flat'), (-14, 22, 'flat'), (-42, 30, 'toe'), (-38, 96, 'air'), (2, 118, 'air'), (44, 92, 'air'), (54, 40, 'air')]
    A = [-55, -30, 10, 50, 62, 40, 0, -40]
    out = []
    for i in range(8):
        n, f = T[i], T[(i + 4) % 8]
        out.append(dict(legN=n, legF=f, armN=(A[i], 80 + max(0, A[i]) * 0.4), armF=(-A[i], 80 + max(0, -A[i]) * 0.4),
                        lean=3, bob=[1, 2, 0, -2, 1, 2, 0, -2][i]))
    return out


POCKET_N, POCKET_F = (-6, 34), (6, 20, 'pocket')   # near hand resting at the hip, as on the sheets


def idle():
    return [dict(legN=(4, 3, 'flat'), legF=(-4, 3, 'flat'), armN=POCKET_N, armF=None, breath=b) for b in (0, 0, 1, 1)]


STAND = dict(legN=(4, 3, 'flat'), legF=(-4, 3, 'flat'), armF=None)
CHEST = {'dx': -1, 'dy': 10}
MOUTH = {'dx': 2, 'dy': 1}
CAN = {'dx': 4, 'dy': 0}


def st(**k):
    d = dict(STAND); d['armN'] = POCKET_N; d.update(k); return d


def jump():
    return [dict(legN=(-8, 14, 'toe'), legF=(-26, 22, 'toe'), armN=(62, 40), armF=(160, 10), lean=1, air=2),
            dict(legN=(62, 96, 'air'), legF=(26, 104, 'air'), armN=(88, 60), armF=(120, 40), lean=1, air=4)]


def fall():
    return [dict(legN=(30, 44, 'air'), legF=(-4, 52, 'air'), armN=(100, 30), armF=(140, 20), air=2),
            dict(legN=(14, 16, 'air'), legF=(-16, 30, 'air'), armN=(92, 34), armF=(165, 20), air=0, mouth=True)]


def build(hero):
    anims = {
        'idle': (idle(), 3),
        'walk': (walk(), 10),
        'run': (run(), 14),
        'jump': (jump(), 1),
        'fall': (fall(), 1),
        'land': ([dict(legN=(52, 84, 'flat'), legF=(18, 76, 'flat'), armN=(34, 40), armF=(-22, 30), lean=3)], 1),
        'crouch': ([dict(legN=(84, 132, 'flat'), legF=(50, 138, 'toe'), armN=(46, 30), armF=(20, 30), lean=3)], 1),
        'shoot': ([dict(legN=(22, 10, 'flat'), legF=(-16, 10, 'flat'), armN=(-62, 70), armF=(40, 40), lean=-1),
                   dict(legN=(26, 14, 'flat'), legF=(-20, 12, 'toe'), armN=(96, 4), armF=(-40, 30), lean=3, mouth=True),
                   dict(legN=(24, 14, 'flat'), legF=(-18, 12, 'toe'), armN=(68, 10), armF=(-30, 30), lean=2)], 14),
        'drop': ([dict(legN=(14, 8, 'flat'), legF=(-12, 8, 'flat'), armN=(120, 50), armF=(-18, 24), mouth=True, lean=-1),
                  dict(legN=(14, 8, 'flat'), legF=(-12, 8, 'flat'), armN=(128, 44), armF=(-24, 28), mouth=True, bob=1, lean=-1)], 6),
        'hurt': ([dict(legN=(24, 34, 'flat'), legF=(-12, 22, 'toe'), armN=(84, 50), armF=(160, 20), lean=-3, mouth=True, hdx=-1)], 1),
        'dead': ([dict(legN=(4, 4, 'flat'), legF=(-6, 6, 'flat'), armN=(100, 0), armF=(80, 10), mouth=True)], 1),
        'talk': ([st(armN=(40, 60)), st(armN=(46, 70), mouth=True)], 11),
        'smoke': ([st(armN=dict(CHEST), prop='cig'),
                   st(armN=dict(MOUTH), prop='lighter', cig=1),
                   st(armN=dict(MOUTH), prop='lighter', flame=1, cig=1),
                   st(armN=dict(MOUTH), prop='lighter', flame=2, cig=2, breath=1),
                   st(armN=POCKET_N, cig=2, breath=1),
                   st(armN=dict(MOUTH), prop='cigHand', breath=1),
                   st(armN=dict(CHEST), prop='cigHand', mouth=True)], 4),
        'vape': ([st(armN=dict(CHEST), prop='stick'),
                  st(armN=dict(MOUTH), prop='stick'),
                  st(armN=dict(MOUTH), prop='stick', breath=1),
                  st(armN=dict(CHEST), prop='stick', mouth=True)], 3),
        'drink': ([st(armN=dict(CHEST), tip=0),
                   st(armN=dict(CAN), tip=0.6, head='back'),
                   st(armN=dict(CAN, dy=-1), tip=1.1, head='back', lean=-1),
                   st(armN=dict(CAN, dy=-1), tip=1.2, head='back', lean=-1, breath=1),
                   st(armN=dict(CHEST), tip=0, mouth=True)], 4),
        'chill': ([st(cig=1, breath=b) for b in (0, 0, 1, 1)], 3),
    }
    return anims


def main(prev=None):
    manifest = {}
    for hero in HERO:
        pal = HERO[hero]['pal']
        for name, (poses, fps) in build(hero).items():
            frames, metas = [], []
            for P in poses:
                g, m = render(hero, P)
                frames.append(g); metas.append(m)
            strip = np.zeros((H, W * len(frames), 4), np.uint8)
            for i, g in enumerate(frames):
                for ch in np.unique(g):
                    if ch == '.':
                        continue
                    hx = pal.get(ch, OL).lstrip('#')
                    strip[:, i * W:(i + 1) * W][g == ch] = (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255)
            key = f'hero_{hero}_{name}'
            im = Image.fromarray(strip, 'RGBA')
            im.save(os.path.join(OUT if prev is None else prev, key + '.png'))
            manifest[key] = {'file': key + '.png', 'w': W, 'h': H, 'frames': len(frames), 'fps': fps,
                             'anchor': [AX, GROUND], 'meta': metas}
    if prev is None:
        json.dump(manifest, open(os.path.join(OUT, 'heroes.json'), 'w'), separators=(',', ':'))
    return manifest


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
