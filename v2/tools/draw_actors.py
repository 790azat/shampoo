#!/usr/bin/env python3
"""Enemy sprites for SHAMPOO v2: dog, pigeon, granny, courier (+ their projectiles
poop / slipper are written to objects.json by draw_objects.py).

Every enemy is a small puppet rig (body masses + IK limbs) posed per key frame,
so the cycles are built from real poses (contact / passing / extremes) instead of
1px nudges of one drawing.

Run:  python3 tools/draw_actors.py   (writes assets/*.png + assets/actors.json)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixkit import Spr, Book, OUTLINE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
PREV = os.environ.get('PREVIEW_DIR')


# ============================================================== rig helpers
def ik2(root, target, l1, l2, bend):
    """2-bone IK. Returns the middle joint. bend=+1 puts the joint on the
    right-hand side of root->target (screen coords, y down), -1 on the left."""
    rx, ry = root
    tx, ty = target
    dx, dy = tx - rx, ty - ry
    d = math.hypot(dx, dy)
    d = max(1e-3, min(d, l1 + l2 - 1e-3))
    a = math.atan2(dy, dx)
    cosb = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1.0, min(1.0, cosb)))
    aa = a - bend * b
    return rx + math.cos(aa) * l1, ry + math.sin(aa) * l1


def polar(p, ang, ln):
    """point at distance ln from p; ang in degrees, 0 = right, 90 = up."""
    a = math.radians(ang)
    return p[0] + math.cos(a) * ln, p[1] - math.sin(a) * ln


def shear_rows(s, amt, y_top, y_piv):
    """Lean: shift rows above y_piv horizontally, linearly up to `amt` px at y_top."""
    if not amt:
        return
    g = s.g.copy()
    for y in range(0, y_piv):
        k = (y_piv - y) / float(y_piv - y_top)
        sh = int(round(amt * min(1.0, k)))
        if sh == 0:
            continue
        row = g[y].copy()
        new = row.copy()
        new[:] = '.'
        for x in range(s.w):
            nx = x + sh
            if 0 <= nx < s.w:
                new[nx] = row[x]
        s.g[y] = new


def puff(s, x, y, r, c='w', c2=None):
    s.ellipse(x, y, r, r * 0.8, c)
    if c2 and r >= 1.5:
        s.ellipse(x + r * 0.35, y + r * 0.35, r * 0.55, r * 0.45, c2)


# ============================================================== DOG
DOG_PAL = {
    'k': OUTLINE,
    'T': '#ecc58a',  # highlight
    't': '#cf9a5c',  # tan
    'b': '#a06c3c',  # tan shade
    'd': '#6e4528',  # dark brown (patch, ears, far legs)
    'D': '#4e3020',  # darker brown
    'c': '#f3dfb4',  # cream muzzle/belly
    'C': '#d9bd8c',  # cream shade
    'w': '#ffffff',
    'p': '#ef6f86',  # tongue
    'P': '#b8405c',
    'n': '#2a1a22',  # nose
    'r': '#c2363c',  # collar (red string)
    'Y': '#ffd23a',
    'u': '#e8e2d2',  # dust
}

# head facing right (mouth open, panting); the ear is drawn separately
DOG_HEAD_OPEN = """
...ttt.......
.ttttttt.....
ttTTTtttt....
tTTtkwttttt..
tTttkkttcccn.
ttttttcccccnn
.btttttbkkkk.
..bbbbbbk....
"""
DOG_ALL = 'tTbcCdDkwpPnrY'
DG = 25          # dog ground row (outline row = anchor)


# leg poses: joint angles in degrees from straight down, + = rotated forward (toward +x).
#   hind : (thigh, shank, cannon)      front : (upper, forearm, paw)
HIND = {
    'stand': (22, -22, 2),
    'plant': (25, -15, 8),       # just landed, under the belly
    'push':  (-20, -45, -60),    # driving back, paw behind the hip
    'trail': (-45, -80, -100),   # stretched out behind (extended flight)
    'swing': (20, -95, -20),     # folded, hock high, coming forward
    'reach': (55, -5, 40),       # swung far forward under the belly (gathered)
}
FRONT = {
    'stand': (2, 0, 0),
    'reach': (55, 80, 100),      # stretched forward (extended flight)
    'land':  (30, 18, 10),       # reaching down for the ground
    'plant': (0, -2, 0),
    'push':  (-30, -32, -20),    # behind the shoulder, pushing off
    'tuck':  (5, -120, -150),    # folded back under the chest (gathered)
    'swing': (40, -40, -60),     # coming forward, wrist still bent
}
HL = (4.2, 4.6, 3.0)
FL = (4.6, 4.6, 1.5)


def leg_points(root, angs, lens):
    pts = [root]
    for a, l in zip(angs, lens):
        r = math.radians(a)
        p = pts[-1]
        pts.append((p[0] + math.sin(r) * l, p[1] + math.cos(r) * l))
    return pts


def draw_leg(s, pts, kind, col, padc):
    if kind == 'hind':
        (h, k, a, p) = pts
        s.ellipse((h[0] + k[0]) / 2.0 - 0.3, (h[1] + k[1]) / 2.0, 1.6, 1.6, col)   # thigh muscle
        s.line(k[0], k[1], a[0], a[1], col, 1)
        s.line(k[0] - 1, k[1], a[0] - 1, a[1], col, 1)
        s.line(a[0], a[1], p[0], p[1], col, 1)
    else:
        (h, k, a, p) = pts
        s.line(h[0], h[1], k[0], k[1], col, 2)
        s.line(k[0], k[1], a[0], a[1], col, 1)
        s.line(a[0], a[1], p[0], p[1], col, 1)
    x, y = p
    s.px(x, y, padc)
    s.px(x + 1, y, padc)


def _ang(v, table):
    return table[v] if isinstance(v, str) else v


def dog_frame(H, C, arch=0, legs=None, plant=(), tail=0, ear='down', head=None, hdx=0, hdy=0,
              tongue=0, chest=0.0):
    """H/C = haunch/chest centres. legs: B1,B2 (hind near/far), F1,F2 (front) as joint angles
    (name from HIND/FRONT or a tuple). Legs listed in `plant` are pinned to the ground by IK."""
    head = head or DOG_HEAD_OPEN
    hip0 = (H[0], H[1] + 1)
    sho0 = (C[0] - 1, C[1] + 2)
    P = {}
    for key in ('B1', 'B2', 'F1', 'F2'):
        far = key.endswith('2')
        if key[0] == 'B':
            root = (hip0[0] + (1 if far else 0), hip0[1])
            P[key] = leg_points(root, _ang(legs[key], HIND), HL)
        else:
            root = (sho0[0] + (1 if far else 0), sho0[1])
            P[key] = leg_points(root, _ang(legs[key], FRONT), FL)
    # planted paws: keep the pose's paw x, pin it to the ground and IK the upper joints
    for k in plant:
        pts = P[k]
        lens = HL if k[0] == 'B' else FL
        last = (pts[3][0] - pts[2][0], pts[3][1] - pts[2][1])
        paw = (pts[3][0], DG - 1)
        ank = (paw[0] - last[0], paw[1] - last[1])
        knee = ik2(pts[0], ank, lens[0], lens[1], 1 if k[0] == 'B' else -1)
        P[k] = [pts[0], knee, ank, paw]

    s = Spr(40, 26)
    far = Spr(40, 26)
    draw_leg(far, P['B2'], 'hind', 'b', 'd')
    draw_leg(far, P['F2'], 'front', 'b', 'd')
    s.blit(far, 0, 0)

    # body: spine is a quadratic curve haunch -> chest, arched by `arch` (up)
    mx, my = (H[0] + C[0]) / 2.0, (H[1] + C[1]) / 2.0 - arch * 2

    def spine(u):
        return ((1 - u) ** 2 * H[0] + 2 * (1 - u) * u * mx + u * u * C[0],
                (1 - u) ** 2 * H[1] + 2 * (1 - u) * u * my + u * u * C[1])
    for i in range(13):
        u = i / 12.0
        x, y = spine(u)
        r = 3.1 - 0.9 * math.sin(u * math.pi) + 0.6 * u      # waist tuck, deep chest
        s.ellipse(x, y + (0.6 * u), r + 0.2, r + (0.4 + chest) * u, 't')
    # neck up to the head
    s.line(C[0] + 1, C[1] - 1, C[0] + 3 + hdx, C[1] - 4 + hdy, 't', 3)
    # cream belly under the chest
    s.ellipse(C[0] - 1, C[1] + 3.2 + chest, 3.2, 1.3, 'c', only='t')
    # saddle patch along the top of the back
    for i in range(3, 9):
        x, y = spine(i / 12.0)
        s.px(x, y - 2, 'd')
        if 4 <= i <= 7:
            s.px(x, y - 1, 'd')
    s.px(H[0] - 2, H[1] - 4, 't')            # rump tuft

    # tail: thick base, curving tip; tail = angle in deg (0 = straight back, + = up)
    tb = (H[0] - 3, H[1] - 2)
    pts = [tb]
    a = 180 - tail
    for i in range(1, 7):
        a2 = a - (tail * 0.12 + 6) * (i / 2.0)
        pts.append(polar(pts[-1], a2, 1.15))
    s.poly(pts[:4], 't', 2)
    s.poly(pts[3:], 't', 1)
    s.px(pts[-1][0], pts[-1][1], 'c')

    # head
    hx, hy = C[0] - 2 + hdx, C[1] - 8 + hdy
    s.ascii(hx, hy, head)
    s.px(hx + 3, hy + 6, 'r')                 # collar
    s.px(hx + 4, hy + 7, 'r')
    s.px(hx + 3, hy + 7, 'r')
    if tongue:                                 # panting tongue, flaps with the bounce
        tx, ty = hx + 9, hy + 7
        s.px(tx, ty, 'p')
        s.px(tx + 1, ty, 'p')
        s.px(tx, ty + 1, 'p')
        if tongue > 1:
            s.px(tx, ty + 2, 'P')
            s.px(tx - 1, ty + 2, 'P')
        elif tongue < 0:
            s.px(tx - 1, ty + 1, 'P')
        else:
            s.px(tx + 1, ty + 1, 'P')
    er = (hx + 3, hy + 1)                       # floppy ear, root on top of the skull
    if ear == 'up':
        s.poly([er, (er[0] - 1, er[1] - 2), (er[0] - 3, er[1] - 3)], 'd', 2)
    elif ear == 'back':
        s.poly([er, (er[0] - 3, er[1] - 1), (er[0] - 5, er[1])], 'd', 2)
    elif ear == 'mid':
        s.poly([er, (er[0] - 2, er[1] - 1), (er[0] - 4, er[1] + 1)], 'd', 2)
    else:
        s.poly([er, (er[0] - 2, er[1] + 1), (er[0] - 2, er[1] + 3)], 'd', 2)
    s.px(er[0], er[1], 'D')

    s.shade('t', 'T', 'b', group=DOG_ALL)
    s.shade('c', None, 'C', group=DOG_ALL)
    s.outline('k')
    # near legs on their own layer so they read against the body
    n = Spr(40, 26)
    draw_leg(n, P['B1'], 'hind', 't', 'b')
    draw_leg(n, P['F1'], 'front', 't', 'b')
    n.outline('k')
    hip_y = H[1] + 2
    for y in range(n.h):                      # no outline where the leg grows out of the body
        for x in range(n.w):
            if n.g[y, x] == 'k' and y <= hip_y and s.get(x, y) in 'tTbcCd':
                n.g[y, x] = '.'
    s.blit(n, 0, 0)
    s.body = (H, C)
    return s


# Rotary gallop, 8 frames (body moving right)
#   0 extended flight  1 trailing front lands  2 front support (lowest)  3 lead front push-off
#   4 gathered flight (back arched)  5 hind lands  6 hind support  7 hind push-off
def _gallop():
    K = [
        dict(H=(11, 10), C=(26, 9), tail=12, ear='back', hdx=1, hdy=-1, tongue=-1,
             legs=dict(B1='trail', B2=(-40, -70, -90), F1='reach', F2=(50, 70, 85))),
        dict(H=(12, 10), C=(26, 11), plant=('F2',), tail=4, ear='back', hdx=1, hdy=0, tongue=1,
             legs=dict(B1=(-5, -95, -60), B2=(0, -90, -50), F1=(50, 55, 60), F2='land')),
        dict(H=(13, 11), C=(26, 13), plant=('F1', 'F2'), tail=-6, ear='mid', hdx=0, hdy=1, tongue=2,
             legs=dict(B1='swing', B2=(25, -85, -10), F1='land', F2=(-15, -18, -10))),
        dict(H=(14, 12), C=(25, 12), arch=2, plant=('F1',), tail=-2, ear='mid', hdx=-1, hdy=1, tongue=2,
             legs=dict(B1=(45, -40, 20), B2=(40, -60, 10), F1='push', F2='tuck')),
        dict(H=(15, 10), C=(25, 10), arch=3, tail=14, ear='up', hdx=-1, hdy=1, tongue=-1,
             legs=dict(B1='reach', B2=(50, -15, 30), F1='tuck', F2=(0, -100, -130))),
        dict(H=(15, 11), C=(26, 9), arch=2, plant=('B2',), tail=24, ear='up', hdx=0, hdy=-1, tongue=1,
             legs=dict(B1=(50, 0, 40), B2='plant', F1='swing', F2=(30, -60, -80))),
        dict(H=(14, 13), C=(26, 10), arch=1, plant=('B1', 'B2'), tail=20, ear='mid', hdx=1, hdy=-1, tongue=1,
             legs=dict(B1='plant', B2=(-5, -30, -30), F1=(55, 50, 40), F2=(45, 30, 20))),
        dict(H=(12, 12), C=(26, 9), plant=('B1',), tail=16, ear='back', hdx=1, hdy=-1, tongue=-1,
             legs=dict(B1='push', B2=(-35, -65, -85), F1='reach', F2=(55, 70, 80))),
    ]
    return [dog_frame(**k) for k in K]


def _idle():
    legs = dict(B1='stand', B2=(18, -18, 2), F1='stand', F2=(-2, 0, 0))
    out = []
    # 4 frames: tongue-out pant with chest heave (head dips on the exhale) + quick tail wag
    for tail, chest, dy, tg in ((45, 0.0, 0, 2), (20, 0.7, 1, 1), (58, 0.0, 0, 2), (25, 0.7, 1, 1)):
        out.append(dog_frame((14, 12), (25, 11 + dy), arch=1, plant=('B1', 'F1'), legs=legs, tail=tail,
                             ear='down', hdy=dy, tongue=tg, chest=chest))
    return out


def dog_dead():
    s = Spr(40, 26)
    # lying on its back, belly up, paws in the air, tongue out, X eyes
    s.ellipse(17, 20, 9, 3.5, 't')
    s.ellipse(17, 18, 6, 1.2, 'c', only='t')
    for x, top, lean in ((10, 12, -1), (14, 11, 0), (20, 11, 0), (24, 12, 1)):
        s.line(x, 17, x + lean, top + 2, 't', 2)
        s.line(x + lean, top + 2, x + lean - 1, top, 't', 2)   # bent wrist
        s.px(x + lean - 1, top - 1, 'b')
        s.px(x + lean, top - 1, 'b')
    s.poly([(8, 21), (6, 22), (4, 22)], 't', 2)          # limp tail
    s.px(3, 22, 'c')
    head = Spr(13, 9)
    head.ascii(0, 0, DOG_HEAD_OPEN)
    head = head.flipy()
    for (x, y) in ((4, 4), (5, 4), (4, 5), (5, 5), (4, 3), (5, 3)):
        head.px(x, y, 't')
    head.px(3, 3, 'k'); head.px(5, 3, 'k'); head.px(4, 4, 'k'); head.px(3, 5, 'k'); head.px(5, 5, 'k')
    s.blit(head, 23, 14)
    s.poly([(26, 21), (24, 23), (22, 23)], 'd', 2)        # ear flopped on the ground
    s.px(32, 22, 'p'); s.px(33, 22, 'p'); s.px(33, 23, 'P')   # tongue lolling
    s.shade('t', 'T', 'b', group=DOG_ALL)
    s.outline('k')
    for (x, y) in ((27, 6), (33, 9), (21, 5)):
        s.px(x, y, 'w')
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            s.px(x + dx, y + dy, 'Y')
    return s


def pad(frames, l, t, r=0, b=0):
    out = []
    for f in frames:
        p = Spr(f.w + l + r, f.h + t + b)
        p.blit(f, l, t)
        out.append(p)
    return out


def build_dog(book):
    # rig works in a 40x26 space; pad 1px left/right and 2px on top for ear/tail headroom
    book.add('dog_run', pad(_gallop(), 1, 2, 1), DOG_PAL, fps=16, anchor=[21, 27])
    book.add('dog_idle', pad(_idle(), 1, 2, 1), DOG_PAL, fps=6, anchor=[21, 27])
    book.add('dog_dead', pad([dog_dead()], 1, 2, 1), DOG_PAL, fps=1, anchor=[21, 27])


# ============================================================== PIGEON
PIG_PAL = {
    'k': OUTLINE,
    'G': '#c3cadb', 'g': '#949fba', 's': '#69718f', 'x': '#454a66',
    'v': '#4cc28e', 'V': '#2f8a6a', 'u': '#9a63bd', 'U': '#6e3f8e',
    'o': '#f39a2b', 'w': '#f4f2ee', 'q': '#3b3346', 'f': '#e0707a',
    'Y': '#ffd23a',
}
PIG_BODY = """
....................
....................
....................
.............GGg....
............GGGgg...
............Gggowqq.
............gggggq..
............uvvVg...
...........uuvvVg...
.x....ggggggguuuUg..
xsx.gGGGgggggggggs..
.xssggggggggggggss..
..xs.ssgggggggsss...
.......sssssss......
....................
"""

def _wing_pts(S, phi, spread):
    sp = math.sin(math.radians(phi))
    sg = 1 if sp >= 0 else -1
    dx, dy = -(0.2 + 0.7 * (1 - abs(sp))), -sp
    n = math.hypot(dx, dy)
    d = (dx / n, dy / n)
    Wp = (S[0] + d[0] * 5.5 * spread, S[1] + d[1] * 5.5 * spread)          # wrist
    hx, hy = d[0] - 0.35 * (2 - spread), d[1]
    n = math.hypot(hx, hy)
    T = (Wp[0] + hx / n * 6.5 * spread, Wp[1] + hy / n * 6.5 * spread)      # wing tip
    P1 = (T[0] - 2, T[1] + 1.5 * sg)                                        # primary ends
    P2 = (Wp[0] - 4.5, Wp[1] + 1.0 * sg)                                    # secondary ends
    P3 = (S[0] - 7, S[1] + 0.5 * sg)                                        # trailing root
    return sg, Wp, T, P1, P2, P3


def pig_wing(s, S, phi, spread=1.0, under=False, far=False):
    """side-view wing hinged at shoulder S. phi = beat angle (deg): +90 straight up, -90 down.
    spread < 1 folds it (upstroke). Shape: shoulder->wrist->tip leading edge, tapered trailing
    edge of feathers. Near wing: light top / grey underside, dark bar + dark primaries."""
    sg, Wp, T, P1, P2, P3 = _wing_pts(S, phi, spread)
    body = 's' if (under or far) else 'g'
    s.polyfill([(S[0] + 1, S[1]), Wp, T, P1, P2, P3], body)
    for a_, b_ in ((S, Wp), (Wp, T), (T, P1), (P1, P2), (P2, P3)):
        s.line(a_[0], a_[1], b_[0], b_[1], body)
    if far:
        return
    s.line(S[0], S[1], Wp[0], Wp[1], 'g' if under else 'G')      # leading edge
    s.line(Wp[0], Wp[1], T[0], T[1], 'g' if under else 'G')
    s.line(T[0], T[1], P1[0], P1[1], 'x')                        # dark primaries
    s.line(P1[0], P1[1], (P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2, 'x')
    m1 = ((S[0] + Wp[0]) / 2, (S[1] + Wp[1]) / 2)                  # wing bar
    m2 = ((P2[0] + P3[0]) / 2 + 1, (P2[1] + P3[1]) / 2)
    s.line(m1[0], m1[1], m2[0], m2[1], 'x')


def pig_smear(s, S, phis, spread=1.0):
    """light arc along the path the wing tip just swept."""
    for i, ph in enumerate(phis):
        T = _wing_pts(S, ph, spread)[2]
        s.px(T[0], T[1], 'w' if i % 2 else 'G')
        s.px(T[0] - 1, T[1], 'G')


def pigeon_frame(phi, spread=1.0, bob=0, tail=0, smear=False):
    W, H = 22, 26
    ox, oy = 1, 6
    s = Spr(W, H)
    S = (12 + ox, 9 + oy + bob)
    fw = Spr(W, H)                                   # far wing, behind the body
    pig_wing(fw, (S[0] + 2, S[1] - 1), phi * 0.92, spread * 0.85, far=True)
    fw.outline('k')
    b = Spr(W, H)
    b.ascii(ox, oy + bob, PIG_BODY)
    if tail:                                         # tail fan flicks with the beat
        b.px(ox, oy + bob + 10 + tail, 'x')
        b.px(ox + 1, oy + bob + 10 + tail, 's')
    b.outline('k')
    n = Spr(W, H)
    pig_wing(n, S, phi, spread, under=phi < -10)
    n.outline('k')
    s.blit(fw, 0, 0)
    s.blit(b, 0, 0)
    s.blit(n, 0, 0)
    if smear:                                        # smear arc behind the fast downstroke
        sm = Spr(W, H)
        pig_smear(sm, S, smear)
        sm.blit(s, 0, 0)
        s = sm
    return s


# 6-frame wing beat: snappy downstroke (0->3, 3 frames), slower folded recovery (4,5)
PIG_BEAT = [
    dict(phi=80, spread=1.0, bob=1, tail=0),
    dict(phi=30, spread=1.0, bob=0, tail=0, smear=(70, 62, 54, 46, 38)),
    dict(phi=-40, spread=1.0, bob=-1, tail=1, smear=(22, 12, 2, -8, -18, -28)),
    dict(phi=-80, spread=0.95, bob=-2, tail=1),
    dict(phi=-25, spread=0.7, bob=-1, tail=0),
    dict(phi=40, spread=0.75, bob=0, tail=0),
]


PIG_DEAD = """
...................
...................
...................
......f...f........
.....fff.fff.......
......f...f........
......f...f........
....GGGGGGGGG......
..GGgggggggggg.....
.xsgggggggggggvuGG.
xxsggggggggggguvGgg
xsxsgggggggggguvggg
.x.ssgggggggggsuggq
....sssssssssss.sqq
...................
"""


def pigeon_dead():
    s = Spr(20, 15)
    # tail fan
    s.ascii(0, 9, """
xs..
xxsg
xsgg
.x..
""")
    s.ellipse(9, 10, 5.5, 3.5, 'g')
    s.ellipse(9, 8, 3.5, 1, 'G', only='g')
    s.shade('g', 'G', 's', group='gGsx')
    for x in (7, 11):           # feet up
        s.vline(x, 3, 6, 'f')
        s.px(x - 1, 3, 'f'); s.px(x + 1, 3, 'f'); s.px(x, 2, 'f')
    s.outline('k')
    h = Spr(20, 15)
    h.ellipse(16, 10.5, 2.5, 2.5, 'g')
    h.shade('g', 'G', 's')
    h.px(14, 10, 'v'); h.px(14, 11, 'u'); h.px(14, 9, 'V'); h.px(15, 12, 'u')
    h.px(19, 11, 'q'); h.px(19, 12, 'q'); h.px(18, 12, 'w')
    h.outline('k')
    s.blit(h, 0, 0)
    # X eye
    for (x, y) in ((15, 8), (17, 8), (16, 9), (15, 10), (17, 10)):
        s.px(x, y, 'x')
    s.px(4, 3, 'G'); s.px(5, 2, 'g'); s.px(14, 2, 'G'); s.px(15, 3, 'g')  # loose feathers
    return s


def build_pigeon(book):
    book.add('pigeon_fly', pad([pigeon_frame(**f) for f in PIG_BEAT], 1, 0), PIG_PAL, fps=14, anchor=[12, 13])
    book.add('pigeon_dead', [pigeon_dead()], PIG_PAL, fps=1, anchor=[10, 14])


# ============================================================== GRANNY
GRAN_PAL = {
    'k': OUTLINE,
    'R': '#d9303a', 'Q': '#f0564e', 'r': '#98182c', 'W': '#fff3e6',
    'S': '#f2b88e', 'P': '#fbd6b4', 's': '#c98060', 'm': '#9a3c40',
    'H': '#cfcad6', 'h': '#9a94a6',
    'q': '#3a2636', 'c': '#bfe6f2', 'w': '#ffffff',
    'D': '#3e3a5c', 'E': '#565280', 'd': '#29243e',
    'L': '#8c4a62', 'M': '#b0647e', 'l': '#5e2c44',
    'A': '#eee2c4', 'a': '#c2ad86', 'f': '#e0566e', 'e': '#5aa84e',
    'G': '#4fc25a', 'g': '#2c8a3e', 'J': '#9ef08e', 'j': '#1d5a2c',
    'N': '#8a6a62', 'B': '#6e4a3a', 'b': '#4e3430',
    'Y': '#ffd23a', 'y': '#fff7b0',
}
GRAN_HEAD = """
....RRRRR....
..RQQWRRRRR..
.RQWQRRRRWRR.
.RQQRRRRRRRRR
RRWRRHHHHHHRR
RRRRHHSSSSSHR
RRRRHqqqSqqqS
RWRRqwcqqwcqS
rRRRqckqqckqS
rRRRSqqSSqqSSS
.rRRSSSSSSSsSS
.rrRsSSSsmmSs.
..rRRssSSSSs..
...rRWRrsss...
....rRr.......
"""
GRAN_HEAD_DAZED = """
....RRRRR....
..RQQWRRRRR..
.RQWQRRRRWRR.
.RQQRRRRRRRRR
RRWRRHHHHHHRR
RRRRHHSSSSSHR
RRRRHqqqSqqqS
RWRRqkckqkckS
rRRRqckqqckqS
rRRRSqqSSqqSSS
.rRRSSSSSSSsSS
.rrRsSSSmmmSs.
..rRRssSmmSs..
...rRWRrsss...
....rRr.......
"""
GRAN_HEAD_SHOUT = GRAN_HEAD.replace(".rrRsSSSsmmSs.", ".rrRsSSmmmmSs.").replace("..rRRssSSSSs..", "..rRRssmmmSs..")


def star(s, x, y, big=False):
    s.px(x, y, 'y')
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        s.px(x + dx, y + dy, 'Y')
    if big:
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            s.px(x + dx, y + dy, 'Y')


def slipper(s, x, y, ang):
    """green slipper: heel at (x,y), pointing along ang (deg, 0=right, 90=up)."""
    a = math.radians(ang)
    dx, dy = math.cos(a), -math.sin(a)
    nx, ny = -dy, dx  # normal (sole side)
    for i in range(7):
        px, py = x + dx * i, y + dy * i
        s.px(px, py, 'G')
        s.px(px + nx, py + ny, 'j')          # sole
        if 1 <= i <= 4:
            s.px(px - nx, py - ny, 'G')      # upper
    s.px(x + dx * 2 - nx, y + dy * 2 - ny, 'J')
    s.px(x + dx * 3 - nx, y + dy * 3 - ny, 'J')
    s.px(x + dx * 6, y + dy * 6, 'g')



def shoe(s, x, y, tilt, col):
    """old-lady shoe, toe to the right. (x, y) = heel bottom. tilt: 0 flat, 1 toe up (heel strike),
    -1 heel up (toe-off)."""
    if tilt == 1:
        s.hline(x - 1, x + 1, y, col)
        s.hline(x - 1, x + 2, y - 1, col)
        s.hline(x + 1, x + 3, y - 2, col)
    elif tilt == -1:
        s.hline(x + 1, x + 3, y, col)
        s.hline(x, x + 3, y - 1, col)
        s.hline(x - 1, x + 1, y - 2, col)
    else:
        s.hline(x - 1, x + 3, y, col)
        s.hline(x - 1, x + 2, y - 1, col)


def granny_frame(bob=0, lean=0, hem=0, feet=((9, 0, 0), (15, 0, 0)), arm=None, slip=None,
                 head=None, hdx=0, hdy=0, W=32, H=42, oy=0, smear=None, dust=None, fwd_hem=0,
                 arm_behind=False, arm_len=5, sh_dx=0):
    """Walk/throw rig. Coordinates are in the 32x42 walk space, shifted down by `oy` on bigger
    canvases. feet = (far, near) as (heel_x, lift, tilt). lean = px the head top shifts (shear
    around the hips). arm = (upper_deg, forearm_deg) from straight down, + = forward."""
    head = head or GRAN_HEAD
    o = bob
    GY = 40 + oy                     # shoe bottom row (outline lands on the anchor row)
    PIV = 31 + oy                    # lean pivot (hips)

    def shx(y):                      # shear offset at row y
        if y >= PIV:
            return 0
        return int(round(lean * min(1.0, (PIV - y) / float(PIV - oy))))

    s = Spr(W, H)
    if smear:
        s.blit(smear, 0, 0)
    # legs + shoes (not leaned)
    for (x, lift, tilt), col in zip(feet, ('b', 'B')):
        y = GY - lift
        top = 34 + oy
        s.rect(x, top, x + 1, y - 2, 'N')
        shoe(s, x, y, tilt, col)
    # body (drawn upright, then sheared)
    b = Spr(W, H)
    Y = lambda v: v + oy + o
    hb, hf = hem, hem + fwd_hem
    b.polyfill([(7, Y(14)), (17, Y(14)), (19, Y(22)), (21 + hf, 36 + oy), (5 + hb, 36 + oy), (4, Y(27)), (5, Y(20))], 'D')
    # hem flick: one ruffled pixel trailing the swing
    b.px(4 + hb - (1 if hem > 0 else 0), 35 + oy, 'D')
    b.polyfill([(14, Y(22)), (19, Y(22)), (21 + hf, 34 + oy), (12 + hb + (hf - hb) // 2, 34 + oy)], 'A')
    b.hline(12 + hb + (hf - hb) // 2, 20 + hf, 34 + oy, 'a')
    for (x, y) in ((15, 26), (18, 29), (15, 32), (18, 33), (17, 24)):
        dx = (hf if y > 30 else 0)
        yy = Y(y) if y < 31 else y + oy
        b.px(x + dx, yy, 'f')
        b.px(x + 1 + dx, yy, 'e')
    b.hline(13, 19, Y(22), 'a')
    b.polyfill([(8, Y(12)), (16, Y(12)), (19, Y(17)), (17, Y(22)), (11, Y(24)), (5, Y(22)), (3, Y(18)), (4, Y(14))], 'L')
    for x in range(4, 18, 2):        # shawl fringe
        yy = Y(23) + (1 if 7 <= x <= 13 else 0)
        b.px(x, yy, 'L')
        b.px(x, yy + 1, 'l')
    for (x, y) in ((6, 16), (9, 18), (12, 16), (7, 20), (14, 19), (10, 21)):
        b.px(x, Y(y), 'l')
    b.ascii(10 + hdx, Y(0) + hdy, head)
    shear_rows(b, lean, oy, PIV)
    s.blit(b, 0, 0)
    s.shade('D', 'E', 'd', group='DEdAaefLlMN')
    s.shade('A', None, 'a', group='DEdAaefLlMN')
    s.shade('L', 'M', 'l', group='LMl')
    s.outline('k')
    if dust:
        d = Spr(W, H)
        for (x, y, r) in dust:
            puff(d, x, y + oy, r, 'W')
        d.outline('k')
        d.blit(s, 0, 0)
        s = d
    hand = None
    if arm:
        a = Spr(W, H)
        sy = Y(16)
        sh = (14 + sh_dx + shx(sy), sy)
        el = (sh[0] + math.sin(math.radians(arm[0])) * arm_len, sh[1] + math.cos(math.radians(arm[0])) * arm_len)
        hd = (el[0] + math.sin(math.radians(arm[1])) * arm_len, el[1] + math.cos(math.radians(arm[1])) * arm_len)
        a.line(sh[0], sh[1], el[0], el[1], 'D', 2)
        a.line(el[0], el[1], hd[0], hd[1], 'D', 2)
        hx, hy = int(round(hd[0])), int(round(hd[1]))
        a.rect(hx, hy, hx + 1, hy + 1, 'S')
        if slip is not None:
            slipper(a, hx + 1, hy + 1, slip)
        a.shade('D', 'E', 'd')
        a.outline('k')
        if arm_behind:              # wound up behind the head: body overlaps the arm
            a.blit(s, 0, 0)
            s = a
        else:
            s.blit(a, 0, 0)
        hand = (hx + 1, hy + 1)
    s.hand = hand
    return s


# 6-frame shuffle (moving right): contact / down / passing, twice.
#   feet: (far, near) = (heel_x, lift, tilt)
def _granny_walk():
    bob = [0, 1, -1, 0, 1, -1]
    feet = [
        ((6, 0, -1), (17, 0, 1)),     # near heel strikes, far toe-off
        ((9, 3, -1), (14, 0, 0)),     # down: far foot picks up
        ((13, 2, 0), (10, 0, 0)),     # passing (high)
        ((17, 0, 1), (6, 0, -1)),     # far heel strikes
        ((14, 0, 0), (9, 3, -1)),
        ((10, 0, 0), (13, 2, 0)),
    ]
    hem = [2, 0, -2, 2, 0, -2]
    fwd = [1, 1, 0, 1, 1, 0]
    arm_u = [-30, -12, 18, 38, 22, -8]         # near arm swings against the near leg
    arm_f = [-10, 8, 45, 70, 50, 15]
    out = []
    for i in range(6):
        vel = arm_u[(i + 1) % 6] - arm_u[i - 1]
        slip = -90 + arm_f[i] - vel * 0.9           # slipper dangles and drags behind the swing
        out.append(granny_frame(bob=bob[i], lean=[0, 2, 1, 0, 2, 1][i], hem=hem[i], fwd_hem=fwd[i],
                                feet=feet[i], arm=(arm_u[i], arm_f[i]), slip=slip,
                                hdx=[0, 1, 0, 0, 1, 0][i], hdy=bob[i - 1] - bob[i], H=44, oy=2))
    return out


def _smear(W, H, pts, oy):
    """crescent motion smear following the slipper's path (list of points, oldest first)."""
    s = Spr(W, H)
    n = len(pts)
    for i in range(n - 1):
        t = 2 if i > n // 3 else 1
        c = 'J' if i < n - 2 else 'G'
        s.line(pts[i][0], pts[i][1] + oy, pts[i + 1][0], pts[i + 1][1] + oy, c, t)
    s.outline('k')
    for i in range(0, n - 1, 2):
        s.px(pts[i][0], pts[i][1] + oy, 'y')
    return s


def _granny_throw():
    W, H, oy, PADL = 36, 46, 4, 4
    out = []
    # 0 anticipation: rock back onto the heel, slipper cocked high behind the head
    out.append(granny_frame(bob=1, lean=-3, hem=-2, fwd_hem=3, feet=((7, 0, 0), (15, 0, 1)),
                            arm=(-135, -150), slip=100, arm_behind=True, arm_len=6, sh_dx=-4, head=GRAN_HEAD_SHOUT, hdx=-1, hdy=0,
                            W=W, H=H, oy=oy))
    # 1 release: lunge forward, arm whips out straight; smear arc from behind the head to the hand
    arc = []
    for k in range(12):
        t = k / 11.0
        ang = math.radians(130 - 130 * t)
        arc.append((14 + math.cos(ang) * 12, 20 - math.sin(ang) * 17 - oy))
    rel = granny_frame(bob=1, lean=3, hem=2, fwd_hem=0, feet=((9, 0, -1), (16, 0, 0)),
                       arm=(82, 92), slip=None, head=GRAN_HEAD_SHOUT, hdx=1, hdy=1,
                       W=W, H=H, oy=oy, smear=_smear(W, H, arc, oy))
    out.append(rel)
    # 2 follow-through: arm sweeps down across, weight over the front foot, back foot drags
    out.append(granny_frame(bob=2, lean=5, hem=1, fwd_hem=1, feet=((11, 1, -1), (16, 0, 0)),
                            arm=(45, 20), slip=None, head=GRAN_HEAD, hdx=2, hdy=1,
                            W=W, H=H, oy=oy))
    # pad on the left so the cocked arm has room behind her
    padded = []
    for f in out:
        p = Spr(W + PADL, H)
        p.blit(f, PADL, 0)
        padded.append(p)
    return padded, (rel.hand[0] + PADL, rel.hand[1])


def granny_dead():
    s = Spr(38, 38)
    # legs stretched forward, shoes toes-up
    for x, y, col in ((28, 34, 'b'), (31, 35, 'B')):
        s.rect(20, y - 1, x - 1, y, 'N')
        s.rect(x, y - 4, x + 1, y, col)
        s.px(x - 1, y, col)
    # sitting dress mound
    s.polyfill([(7, 20), (17, 20), (20, 27), (23, 30), (23, 36), (4, 36), (3, 28)], 'D')
    s.polyfill([(15, 26), (19, 27), (22, 31), (22, 35), (14, 35)], 'A')
    for (x, y) in ((17, 29), (20, 31), (17, 33)):
        s.px(x, y, 'f'); s.px(x + 1, y, 'e')
    s.polyfill([(8, 18), (16, 18), (19, 23), (17, 27), (11, 29), (5, 27), (3, 23), (4, 20)], 'L')
    for x in range(5, 18, 2):
        s.px(x, 28 + (1 if 8 <= x <= 13 else 0), 'L'); s.px(x, 29 + (1 if 8 <= x <= 13 else 0), 'l')
    s.ascii(9, 5, GRAN_HEAD_DAZED)
    # arm propped on the ground behind
    s.line(7, 23, 5, 31, 'D', 2)
    s.rect(4, 32, 5, 33, 'S')
    s.shade('D', 'E', 'd', group='DEdAaefLlMN')
    s.shade('A', None, 'a', group='DEdAaefLlMN')
    s.shade('L', 'M', 'l', group='LMl')
    s.outline('k')
    # dropped slipper on the ground in front
    sl = Spr(34, 38)
    slipper(sl, 0, 35, 0)
    sl.outline('k')
    s.blit(sl, 0, 0)
    # stars orbit
    star(s, 8, 3, True)
    star(s, 17, 1)
    star(s, 25, 4, True)
    return s


def build_granny(book):
    book.add('granny_walk', _granny_walk(), GRAN_PAL, fps=8, anchor=[12, 43])
    frames, hand = _granny_throw()
    book.add('granny_throw', frames, GRAN_PAL, fps=8, anchor=[16, 45],
             extra={'release_frame': 1, 'hand': list(hand)})
    book.add('granny_dead', [granny_dead()], GRAN_PAL, fps=1, anchor=[14, 37])


# ============================================================== COURIER
COUR_PAL = {
    'k': OUTLINE,
    'Y': '#ffcf2e', 'y': '#e0951c', 'Z': '#fff3a0', 'o': '#b86a10',
    'J': '#30507a', 'j': '#1f3352', 'I': '#4c7cb0',
    'P': '#45455e', 'p': '#30304a',
    'S': '#eaa97c', 's': '#bb7856',
    'H': '#f6f6fa', 'h': '#b9bdd0', 'V': '#28385a', 'v': '#6a9ad0',
    'M': '#a3adbf', 'm': '#5f6880', 'N': '#e0e6ef',
    'T': '#3c3548', 't': '#5a5266',
    'W': '#f2f2f2', 'X': '#c8c8d0', 'r': '#e5484d', 'w': '#ffffff',
}



def wheel(s, cx, cy, ang, r=5):
    """wheel with 3 dark spokes at angle `ang` (deg, clockwise = rolling right), a light
    hub disc and a bright scuff on the tyre that rotates with them."""
    s.ellipse(cx, cy, r, r, 'T')
    s.ellipse(cx, cy, r - 1.7, r - 1.7, 'M')
    for k in range(3):
        a = math.radians(ang + k * 120)
        for rr in (1, 2, 3):
            s.px(cx + round(math.cos(a) * rr), cy + round(math.sin(a) * rr), 'm')
    a = math.radians(ang + 60)
    for da in (-0.25, 0.0, 0.25):
        s.px(cx + round(math.cos(a + da) * r), cy + round(math.sin(a + da) * r), 't')
    s.px(cx, cy, 'N')


def scooter(ang=0, dy=0):
    s = Spr(42, 44)
    o = dy
    s.rect(6, 33 + o, 31, 35 + o, 'm')         # deck
    s.hline(7, 30, 33 + o, 'M')
    s.hline(9, 28, 34 + o, 'P')                # grip tape
    s.rect(2, 33 + o, 8, 35 + o, 'm')          # rear fender
    s.hline(2, 7, 33 + o, 'M')
    s.px(2, 34 + o, 'r')                       # tail light
    s.line(31, 30 + o, 34, 38, 'm', 2)         # fork
    s.line(31, 35 + o, 27, 18 + o, 'M', 2)     # stem
    s.rect(25, 17 + o, 30, 17 + o, 'm')        # handlebar
    s.rect(29, 16 + o, 31, 18 + o, 'T')        # grip
    s.px(30, 21 + o, 'w'); s.px(31, 21 + o, 'Y'); s.px(30, 22 + o, 'Y')  # headlight
    wheel(s, 7, 37, ang)
    wheel(s, 34, 37, ang)
    s.shade('m', 'M', None, group='mMNTtPrwY')
    s.outline('k')
    return s


JACKET_FLAP = [
    [(14, 21), (6, 23), (8, 24), (10, 26), (14, 26)],
    [(14, 21), (7, 25), (9, 25), (11, 27), (14, 26)],
    [(14, 21), (5, 22), (7, 24), (10, 25), (14, 26)],
]


def rider(flap=0, bob=0, head=0, deck=0):
    s = Spr(40, 44)
    o = bob
    # legs: hips ride with the torso, sneakers stay on the deck -> knees flex on the bounce
    for hip, foot, col, th in (((15, 24 + o), (12, 31 + deck), 'p', 3), ((18, 24 + o), (20, 31 + deck), 'P', 3)):
        knee = ik2(hip, foot, 4.6, 3.8, 1 if col == 'P' else 1)
        s.line(hip[0], hip[1], knee[0], knee[1], col, th)
        s.line(knee[0], knee[1], foot[0], foot[1] - 1, col, 2)
    s.rect(10, 31 + deck, 15, 32 + deck, 'W'); s.hline(10, 15, 32 + deck, 'X')
    s.rect(18, 31 + deck, 23, 32 + deck, 'W'); s.hline(18, 23, 32 + deck, 'X')
    # jacket tail flutter (behind)
    s.polyfill([(x, y + o) for x, y in JACKET_FLAP[flap]], 'J')
    # torso leaning forward
    s.polyfill([(13, 25 + o), (20, 26 + o), (25, 18 + o), (24, 13 + o), (18, 13 + o), (13, 19 + o)], 'J')
    s.hline(14, 20, 25 + o, 'j')
    s.line(15, 20 + o, 22, 17 + o, 'Y')  # reflective stripe
    s.shade('J', 'I', 'j', group='JIjYPp')
    h = head
    # head: face profile under helmet
    s.ellipse(26, 9 + h, 3.5, 3.5, 'S')
    s.px(30, 9 + h, 'S'); s.px(30, 10 + h, 'S')    # nose
    s.px(28, 8 + h, 'k')                           # eye
    s.px(27, 7 + h, 's')                           # brow
    s.hline(26, 29, 12 + h, 's'); s.px(29, 11 + h, 'm')  # stubble + mouth
    s.px(23, 9 + h, 's'); s.px(23, 10 + h, 's')    # ear
    # helmet
    s.ellipse(25, 4.5 + h, 5, 3, 'H')
    s.hline(20, 30, 6 + h, 'H')
    s.hline(26, 31, 6 + h, 'V'); s.px(30, 5 + h, 'v')   # visor peak
    s.hline(21, 27, 2 + h, 'Y'); s.hline(20, 26, 3 + h, 'Y')  # stripe
    s.line(22, 7 + h, 24, 12 + h, 'h')             # strap
    s.shade('H', None, 'h', group='HhVvYSskm')
    s.outline('k')
    return s


def backpack(bob=0, tilt=0):
    s = Spr(40, 44)
    o = bob
    x0, y0, x1, y1 = 5, 9 + o, 17, 21 + o
    s.rect(x0, y0, x1, y1, 'Y')
    s.hline(x0, x1, y0 + 3, 'y')                   # lid seam
    s.hline(x0, x1, y0, 'Z')
    s.vline(x0, y0, y1, 'Z')
    s.vline(x1, y0 + 1, y1, 'y')
    s.hline(x0 + 1, x1, y1, 'y')
    s.px(x1, y0, 'Y')
    if tilt:                                       # lid lifts off the box at the top of the jiggle
        s.hline(x0, x1 - 1, y0 - 1, 'Y')
        s.hline(x0, x1 - 1, y0, 'y')
    s.rect(9, 15 + o, 13, 18 + o, 'o')
    s.px(10, 14 + o, 'o'); s.px(12, 14 + o, 'o'); s.px(11, 13 + o, 'o')
    s.px(10, 16 + o, 'Y'); s.px(12, 16 + o, 'Y'); s.px(11, 17 + o, 'Y')
    s.outline('k')
    return s


def arm(bob=0, deck=0):
    s = Spr(40, 44)
    sh = (21, 15 + bob)
    hand = (27, 16 + deck)                          # hands stay on the grips
    el = ik2(sh, hand, 4.5, 4.5, 1)
    s.line(sh[0], sh[1], el[0], el[1], 'J', 2)
    s.line(el[0], el[1], hand[0], hand[1], 'J', 2)
    s.rect(27, 16 + deck, 28, 17 + deck, 'S')
    s.shade('J', 'I', 'j')
    s.outline('k')
    return s


CPAD = 8          # extra room behind the scooter for dust and speed lines
# 6-frame ride (12 fps): road bump at frame 2 -> deck kicks, rider absorbs with the knees,
# head and the heavy box follow a frame late and overshoot.
COUR_DECK = [0, 0, -1, 0, 0, 0]
COUR_BODY = [0, 0, -1, 1, 2, 1]
COUR_HEAD = [1, 0, -1, 0, 1, 2]
COUR_BOX = [0, 0, 0, -2, 0, 2]


def courier_frame(i):
    W = 42 + CPAD
    deck = COUR_DECK[i]
    bob = COUR_BODY[i]
    head = COUR_HEAD[i]
    box = COUR_BOX[i]
    base = scooter(ang=i * 40, dy=deck)
    base.blit(rider(flap=i % 3, bob=bob, head=head, deck=deck), 0, 0)
    base.blit(backpack(bob=box, tilt=(i == 3)), 0, 0)
    base.blit(arm(bob=bob, deck=deck), 0, 0)
    base.px(19, 14 + bob, 'j'); base.px(20, 15 + bob, 'j')   # strap over shoulder
    s = Spr(W, 44)
    # speed lines: streaks peel off the rider's back and slide away, getting shorter
    fx = Spr(W, 44)
    for k, (y, ph) in enumerate(((12, 0), (19, 2), (27, 1))):
        t = (i + ph * 2) % 6
        x1 = CPAD + 5 - t * 2
        L = max(2, 9 - t * 1.5)
        fx.hline(int(x1 - L), x1, y, 'N')
    # dust kicked off the rear wheel: puffs grow and drift back, then fade
    d = Spr(W, 44)
    for k in range(2):
        t = (i + k * 3) % 6
        if t < 4:
            puff(d, CPAD + 2 - t * 2, 40 - t * 0.8, 0.9 + t * 0.35, 'W', 'X')
    d.outline('k')
    s.blit(d, 0, 0)
    s.blit(fx, 0, 0)
    s.blit(base, CPAD, 0)
    return s


def courier_dead():
    s = Spr(54, 24)
    # scooter fallen on its side: deck edge-on, wheels seen flat, stem lying forward
    sc = Spr(54, 24)
    sc.rect(36, 20, 49, 21, 'm'); sc.hline(36, 49, 20, 'M')
    sc.ellipse(36, 21, 3, 1.5, 'T'); sc.ellipse(49, 21, 3, 1.5, 'T')
    sc.px(36, 21, 'M'); sc.px(49, 21, 'M')
    sc.line(49, 20, 52, 13, 'M', 2)     # stem sticking up at an angle
    sc.rect(50, 11, 53, 12, 'T')
    sc.outline('k')
    s.blit(sc, 0, 0)
    # courier face down
    p = Spr(54, 24)
    p.line(15, 20, 4, 21, 'P', 3)       # straight leg
    p.line(14, 18, 9, 13, 'p', 3)       # bent leg in the air
    p.line(9, 13, 5, 14, 'p', 2)
    p.rect(1, 20, 4, 22, 'W'); p.rect(3, 12, 5, 15, 'W')   # sneakers
    p.rect(14, 16, 27, 22, 'J')         # torso
    p.ellipse(31, 19.5, 3.5, 3, 'H')    # helmeted head, face down
    p.hline(31, 34, 22, 'V'); p.hline(28, 32, 16, 'Y')
    p.line(27, 22, 35, 22, 'J', 1)      # arm reaching for the scooter
    p.rect(35, 21, 36, 22, 'S')
    p.shade('J', 'I', 'j', group='JIjPp')
    p.shade('H', None, 'h', group='HhVY')
    p.outline('k')
    s.blit(p, 0, 0)
    b = Spr(54, 24)                     # delivery box still on the back, lid flipped open
    b.rect(15, 7, 26, 16, 'Y')
    b.hline(15, 26, 7, 'Z'); b.vline(15, 7, 16, 'Z'); b.vline(26, 8, 16, 'y'); b.hline(16, 26, 16, 'y')
    b.rect(19, 10, 22, 13, 'o'); b.px(20, 11, 'Y'); b.px(21, 12, 'Y')
    b.line(15, 6, 22, 1, 'y')
    b.line(16, 6, 23, 1, 'Y')
    b.outline('k')
    s.blit(b, 0, 0)
    f = Spr(54, 24)                     # spilled lavash wrap + soda cup
    f.rect(7, 4, 11, 6, 'Z'); f.hline(8, 10, 4, 'S'); f.px(11, 5, 'r')
    f.rect(29, 4, 31, 8, 'W'); f.hline(29, 31, 4, 'r'); f.px(30, 3, 'X'); f.px(30, 2, 'X')
    f.outline('k')
    s.blit(f, 0, 0)
    for (x, y) in ((36, 12), (41, 8), (33, 6)):
        star(s, x, y)
    return s


def build_courier(book):
    frames = pad([courier_frame(i) for i in range(6)], 0, 1)
    book.add('courier_ride', frames, COUR_PAL, fps=12, anchor=[20 + CPAD, 44])
    book.add('courier_dead', [courier_dead()], COUR_PAL, fps=1, anchor=[27, 23])


def main(only=None):
    book = Book(ASSETS, 'actors.json', PREV)
    builders = [('dog', build_dog), ('pigeon', build_pigeon), ('granny', build_granny), ('courier', build_courier)]
    for name, fn in builders:
        if only and name not in only:
            continue
        fn(book)
    book.save()


if __name__ == '__main__':
    main(sys.argv[1:] or None)
