#!/usr/bin/env python3
"""Enemy sprites for SHAMPOO v2: dog, pigeon, granny, courier (+ their projectiles
poop / slipper are written to objects.json by draw_objects.py).

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
}

# head drawn facing right; origin = top-left of map
DOG_HEAD = """
...dd........
..dDDd.......
..dDtd.......
.ttttttt.....
ttTTTtttt....
tTTtkwttttt..
tTttkkttcccn.
ttttttcccccnn
.btttttbcccc.
..bbbbbbCC...
"""
DOG_HEAD_PANT = """
...dd........
..dDDd.......
..dDtd.......
.ttttttt.....
ttTTTtttt....
tTTtkwttttt..
tTttkkttcccn.
ttttttcccccnn
.btttttbkkkk.
..bbbbbCppP..
........pP...
"""


def dog_frame(bob=0, legs=None, tail=0.0, head='run', stretch=0, ear=0):
    s = Spr(34, 24)
    gy = 23
    hipx, shx = 10 - stretch // 2, 22 + (stretch + 1) // 2
    hy = 13 + bob

    def leg(hx, hyy, fx, fy, kind, col, paw):
        # hip/shoulder -> knee -> foot, 2px wide
        mx, my = (hx + fx) / 2, (hyy + fy) / 2
        lift = gy - fy
        if kind == 'back':
            kx, ky = mx - 2 + (1 if fx < hx - 3 else 0), my - 1
        else:
            kx, ky = mx + (1 if lift > 1 else 0), my
        s.line(hx, hyy, kx, ky, col, 2)
        s.line(kx, ky, fx, fy - 1, col, 1)
        s.line(kx + 1, ky, fx + (1 if kind == 'back' else 0), fy - 1 if kind == 'back' else ky + 1, col, 1)
        # paw
        if kind == 'front' and lift > 2:
            s.px(fx - 1, fy, paw)
            s.px(fx, fy, paw)
        else:
            s.px(fx, fy, paw)
            s.px(fx + 1, fy, paw)

    L = legs
    # far legs first (dark)
    leg(hipx + 1, hy, hipx + L['B2'][0], L['B2'][1], 'back', 'd', 'D')
    leg(shx, hy, shx + L['F2'][0], L['F2'][1], 'front', 'd', 'D')

    # body
    s.ellipse(16 + (stretch % 2) * 0.5, 11 + bob, 8 + stretch * 0.5, 3.5, 't')
    s.ellipse(21, 10.5 + bob, 3.5, 4, 't')          # deep chest
    s.ellipse(10, 10.5 + bob, 3.5, 3.5, 't')        # haunch
    s.ellipse(16, 13.5 + bob, 5, 1.2, 'c', only='t')  # belly
    # scruffy tufts: rump, neck ruff, belly fringe
    for x, y, c in ((9, 6, 't'), (8, 7, 't'), (21, 5, 't'), (14, 15, 'c'), (18, 15, 'c'), (11, 15, 't')):
        s.px(x, y + bob, c)
    # dark saddle patch
    s.ellipse(14, 8.5 + bob, 3, 1.2, 'd', only='t')
    s.px(17, 8 + bob, 'd')
    s.px(12, 7 + bob, 'd')

    # tail (from rump, angle in deg, 0 = straight back/up)
    tx, ty = 7 - stretch // 2, 9 + bob
    a = math.radians(140 + tail)
    pts = [(tx, ty)]
    for i in range(1, 7):
        aa = a + math.radians(tail * 0.15) * i
        pts.append((tx + math.cos(aa) * i * 1.0, ty - math.sin(aa) * i * 1.0 - (0.3 * i if i > 3 else 0)))
    s.poly(pts[:6], 't', 2)
    s.poly(pts, 't', 1)
    ex, ey = pts[-1]
    s.px(ex, ey, 'c')
    s.px(pts[-2][0], pts[-2][1], 'c')

    # near legs
    leg(hipx, hy, hipx + L['B1'][0], L['B1'][1], 'back', 't', 'b')
    leg(shx - 1, hy, shx - 1 + L['F1'][0], L['F1'][1], 'front', 't', 'b')
    # collar
    s.px(23, 9 + bob, 'r')
    s.px(23, 10 + bob, 'r')
    s.px(24, 11 + bob, 'r')

    # head
    hmap = DOG_HEAD_PANT if head == 'pant' else DOG_HEAD
    s.ascii(20, 0 + bob + (1 if head == 'low' else 0), hmap)
    if ear:  # ear flap (top of floppy ear raised/lowered)
        s.px(23, 0 + bob, '.')
        s.px(24, 0 + bob, '.')
        s.px(21, 1 + bob, 'd')

    # lighting
    s.shade('t', 'T', 'b', group='tTbcCdDkwpPnr')
    s.shade('c', None, 'C', group='tTbcCdDkwpPnr')
    s.outline('k')
    return s


DOG_RUN = [
    # B = back legs (dx from hip, foot y), F = front legs (dx from shoulder, foot y)
    dict(bob=-1, stretch=2, tail=-10, head='pant', legs=dict(B1=(-7, 20), B2=(-5, 21), F1=(6, 20), F2=(8, 21))),
    dict(bob=0, stretch=1, tail=0, head='pant', legs=dict(B1=(-6, 21), B2=(-4, 22), F1=(4, 23), F2=(6, 22))),
    dict(bob=1, stretch=0, tail=10, head='pant', legs=dict(B1=(-3, 21), B2=(-1, 22), F1=(0, 23), F2=(2, 23))),
    dict(bob=1, stretch=-1, tail=20, head='pant', legs=dict(B1=(2, 23), B2=(4, 22), F1=(-3, 21), F2=(-1, 22))),
    dict(bob=0, stretch=-1, tail=10, head='pant', legs=dict(B1=(1, 23), B2=(-1, 23), F1=(2, 19), F2=(0, 20))),
    dict(bob=-1, stretch=1, tail=-5, head='pant', legs=dict(B1=(-3, 22), B2=(-5, 23), F1=(5, 19), F2=(3, 20))),
]
DOG_STAND = dict(B1=(-1, 23), B2=(1, 23), F1=(0, 23), F2=(2, 23))


def dog_dead():
    s = Spr(34, 24)
    # lying on its back, belly up, paws in the air, tongue out, X eyes
    s.ellipse(14, 18, 9, 3.5, 't')
    s.ellipse(14, 16, 6, 1.2, 'c', only='t')
    for x, top, lean in ((7, 10, -1), (11, 9, 0), (17, 9, 0), (21, 10, 1)):
        s.line(x, 15, x + lean, top + 2, 't', 2)
        s.line(x + lean, top + 2, x + lean - 1, top, 't', 2)   # bent wrist
        s.px(x + lean - 1, top - 1, 'b')
        s.px(x + lean, top - 1, 'b')
    s.poly([(5, 19), (3, 20), (1, 20)], 't', 2)          # limp tail
    s.px(0, 20, 'c')
    head = Spr(13, 11)
    head.ascii(0, 0, DOG_HEAD_PANT)
    head = head.flipy()
    # X eye (was at 4..5, 5..6 -> flipped rows 4..5)
    for (x, y) in ((4, 4), (5, 4), (4, 5), (5, 5)):
        head.px(x, y, 't')
    head.px(3, 3, 'k'); head.px(5, 3, 'k'); head.px(4, 4, 'k'); head.px(3, 5, 'k'); head.px(5, 5, 'k')
    s.blit(head, 20, 11)
    s.shade('t', 'T', 'b', group='tTbcCdDkwpPnr')
    s.outline('k')
    for (x, y) in ((24, 5), (30, 7), (19, 4)):
        s.px(x, y, 'w')
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            s.px(x + dx, y + dy, 'Y')
    return s


def build_dog(book):
    frames = [dog_frame(**f) for f in DOG_RUN]
    book.add('dog_run', frames, DOG_PAL, fps=14, anchor=[17, 23])
    idle = [dog_frame(bob=0, legs=DOG_STAND, tail=-35, head='pant'),
            dog_frame(bob=0, legs=DOG_STAND, tail=-10, head='pant', ear=1)]
    # breathing: second frame chest 1px lower belly
    book.add('dog_idle', idle, DOG_PAL, fps=3, anchor=[17, 23])
    pal = dict(DOG_PAL, Y='#ffd23a')
    book.add('dog_dead', [dog_dead()], pal, fps=1, anchor=[17, 23])


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
PIG_WINGS = {
    'up': (3, 0, """
.x..........
.xsx........
..xsgx......
..xxsgg.....
...xsgGg....
....xsggGg..
....xxsggGg.
.....xxsgggg
......xsgggg
.......sggg.
"""),
    'mid': (2, 7, """
.....GGGGGG.....
xxxsgGgggggg....
.xxssgxgxgg.....
...xxss.........
"""),
    'down': (3, 10, """
....GGGGGGg
...sggxgxgg
..xsgxgxgs.
.xxsggss...
xxss.......
"""),
}


def pigeon_frame(wing, bob=0):
    s = Spr(20, 15)
    s.ascii(0, bob, PIG_BODY)
    if wing == 'down':  # legs tucked show under wing anyway
        pass
    s.outline('k')
    wx, wy, m = PIG_WINGS[wing]
    w = Spr(20, 15)
    w.ascii(wx, wy + bob, m)
    w.outline('k')
    s.blit(w, 0, 0)
    return s


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
    frames = [pigeon_frame('up', 1), pigeon_frame('mid', 0), pigeon_frame('down', -2), pigeon_frame('mid', 0)]
    book.add('pigeon_fly', frames, PIG_PAL, fps=12, anchor=[10, 7])
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


def granny_body(s, bob=0, hem=0, lean=0):
    o = bob
    # dress
    s.polyfill([(7, 14 + o), (17, 14 + o), (19, 22 + o), (20 + hem, 37), (5 + hem, 37), (4, 27 + o), (5, 20 + o)], 'D')
    # apron (front)
    s.polyfill([(14, 22 + o), (19, 22 + o), (20 + hem, 35), (12 + hem, 35)], 'A')
    s.hline(12 + hem, 19 + hem, 35, 'a')
    for (x, y) in ((15, 26), (18, 29), (15, 32), (18, 34), (17, 24)):
        s.px(x + (hem if y > 30 else 0), y + o, 'f')
        s.px(x + 1 + (hem if y > 30 else 0), y + o, 'e')
    s.hline(13, 19, 22 + o, 'a')  # apron tie
    # shawl over hunched shoulders
    s.polyfill([(8, 12 + o), (16, 12 + o), (19, 17 + o), (17, 22 + o), (11, 24 + o), (5, 22 + o), (3, 18 + o), (4, 14 + o)], 'L')
    for x in range(4, 18, 2):     # fringe
        yy = 23 + o + (1 if 7 <= x <= 13 else 0)
        s.px(x, yy, 'L')
        s.px(x, yy + 1, 'l')
    # knit pattern
    for (x, y) in ((6, 16), (9, 18), (12, 16), (7, 20), (14, 19), (10, 21)):
        s.px(x, y + o, 'l')


def granny_feet(s, fl, fr):
    """fl/fr = (x, lift) for back/front foot."""
    for (x, lift), col in ((fl, 'b'), (fr, 'B')):
        y = 40 - lift
        s.rect(x, 36, x + 1, y - 1, 'N')
        s.rect(x - 1, y - 1, x + 3, y, col)
        s.px(x + 3, y - 1, '.')


def granny_arm(s, sx, sy, ex, ey, hx, hy, slip=None):
    s.line(sx, sy, ex, ey, 'D', 2)
    s.line(ex, ey, hx, hy, 'D', 2)
    s.rect(hx, hy, hx + 1, hy + 1, 'S')
    if slip is not None:
        slipper(s, hx + 1, hy, slip)


def granny_frame(bob=0, hem=0, feet=((7, 0), (13, 0)), arm=None, head=GRAN_HEAD, hx=10, slip=None, stars=False):
    s = Spr(30, 42)
    granny_feet(s, *feet)
    granny_body(s, bob, hem)
    s.ascii(hx, bob - 0, head)
    s.shade('D', 'E', 'd', group='DEdAaefLlMN')
    s.shade('A', None, 'a', group='DEdAaefLlMN')
    s.shade('L', 'M', 'l', group='LMl')
    s.outline('k')
    if arm:
        a = Spr(30, 42)
        granny_arm(a, *arm, slip=slip)
        a.shade('D', 'E', 'd')
        a.outline('k')
        s.blit(a, 0, 0)
    return s


GRAN_WALK = [
    dict(bob=0, hem=1, feet=((5, 0), (15, 0)), arm=(14, 16, 17, 20, 20, 22), slip=-15),
    dict(bob=-1, hem=0, feet=((9, 1), (12, 0)), arm=(14, 15, 16, 20, 18, 23), slip=-35),
    dict(bob=0, hem=-1, feet=((14, 0), (7, 0)), arm=(14, 16, 15, 21, 16, 25), slip=-55),
    dict(bob=-1, hem=0, feet=((11, 0), (10, 1)), arm=(14, 15, 16, 20, 18, 23), slip=-35),
]


def granny_throw():
    out = []
    poses = [
        # (lean x, head, shoulder, elbow, hand, slipper angle or None, streak)
        (-1, GRAN_HEAD_SHOUT, (11, 19), (7, 13), (6, 7), 80, False),
        (1, GRAN_HEAD_SHOUT, (15, 20), (20, 20), (25, 19), None, True),
        (1, GRAN_HEAD, (15, 19), (19, 23), (21, 27), None, False),
    ]
    for lean, head, sh, el, ha, sl, streak in poses:
        base = granny_frame(head=head, hx=10 + lean)
        big = Spr(32, 46)
        big.blit(base, 0, 4)
        a = Spr(32, 46)
        granny_arm(a, sh[0], sh[1], el[0], el[1], ha[0], ha[1], slip=sl)
        a.shade('D', 'E', 'd')
        a.outline('k')
        big.blit(a, 0, 0)
        if streak:
            for (x0, y0, x1) in ((27, 15, 30), (28, 18, 31), (27, 22, 30)):
                big.hline(x0, x1, y0, 'y')
        out.append(big)
    return out


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
    frames = []
    for f in GRAN_WALK:
        frames.append(granny_frame(**f))
    book.add('granny_walk', frames, GRAN_PAL, fps=7, anchor=[12, 41])
    book.add('granny_throw', granny_throw(), GRAN_PAL, fps=8, anchor=[12, 45],
             extra={'release_frame': 1, 'hand': [26, 19]})
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


def wheel(s, cx, cy, ph, r=4):
    s.ellipse(cx, cy, r, r, 'T')
    s.ellipse(cx, cy, r - 1.6, r - 1.6, 'M')
    s.px(cx, cy, 'm')
    a = ph * math.pi / 4
    for k in range(2):
        aa = a + k * math.pi / 2
        s.px(cx + round(math.cos(aa) * 2), cy + round(math.sin(aa) * 2), 'm')
        s.px(cx - round(math.cos(aa) * 2), cy - round(math.sin(aa) * 2), 'N')
    s.px(cx + round(math.cos(a) * r), cy + round(math.sin(a) * r), 't')
    s.px(cx - round(math.cos(a) * r), cy - round(math.sin(a) * r), 't')


def scooter(ph=0):
    s = Spr(40, 44)
    s.rect(6, 33, 31, 35, 'm')         # deck
    s.hline(7, 30, 33, 'M')
    s.hline(9, 28, 34, 'P')            # grip tape
    s.rect(2, 33, 8, 35, 'm')          # rear fender
    s.hline(2, 7, 33, 'M')
    s.px(2, 34, 'r')                   # tail light
    s.line(31, 30, 34, 38, 'm', 2)     # fork
    s.line(31, 35, 27, 18, 'M', 2)     # stem
    s.rect(25, 17, 30, 17, 'm')        # handlebar
    s.rect(29, 16, 31, 18, 'T')        # grip
    s.px(30, 21, 'w'); s.px(31, 21, 'Y'); s.px(30, 22, 'Y')  # headlight
    wheel(s, 7, 38, ph)
    wheel(s, 34, 38, ph)
    s.shade('m', 'M', None, group='mMNTtPrwY')
    s.outline('k')
    return s


def rider(flap=0, bob=0):
    s = Spr(40, 44)
    o = bob
    # legs (back leg bent, front leg straight)
    s.line(15, 24 + o, 13, 29 + o, 'p', 3)
    s.line(13, 29 + o, 12, 31, 'p', 2)
    s.line(18, 24 + o, 21, 28 + o, 'P', 3)
    s.line(21, 28 + o, 20, 31, 'P', 2)
    s.rect(10, 31, 15, 32, 'W'); s.hline(10, 15, 32, 'X')
    s.rect(18, 31, 23, 32, 'W'); s.hline(18, 23, 32, 'X')
    # jacket tail flutter (behind)
    flaps = [[(14, 21), (8, 24), (10, 25), (14, 26)], [(14, 21), (7, 23), (10, 24), (14, 26)],
             [(14, 21), (8, 25), (11, 25), (14, 26)], [(14, 21), (7, 22), (9, 24), (14, 26)]]
    s.polyfill([(x, y + o) for x, y in flaps[flap]], 'J')
    # torso leaning forward
    s.polyfill([(13, 25 + o), (20, 26 + o), (25, 18 + o), (24, 13 + o), (18, 13 + o), (13, 19 + o)], 'J')
    s.hline(14, 20, 25 + o, 'j')
    s.line(15, 20 + o, 22, 17 + o, 'Y')  # reflective stripe
    s.shade('J', 'I', 'j', group='JIjYPp')
    # head: face profile under helmet
    s.ellipse(26, 9 + o, 3.5, 3.5, 'S')
    s.px(30, 9 + o, 'S'); s.px(30, 10 + o, 'S')    # nose
    s.px(28, 8 + o, 'k')                           # eye
    s.px(27, 7 + o, 's')                           # brow
    s.hline(26, 29, 12 + o, 's'); s.px(29, 11 + o, 'm')  # stubble + mouth
    s.px(23, 9 + o, 's'); s.px(23, 10 + o, 's')    # ear
    # helmet
    s.ellipse(25, 4.5 + o, 5, 3, 'H')
    s.hline(20, 30, 6 + o, 'H')
    s.hline(26, 31, 6 + o, 'V'); s.px(30, 5 + o, 'v')   # visor peak
    s.hline(21, 27, 2 + o, 'Y'); s.hline(20, 26, 3 + o, 'Y')  # stripe
    s.line(22, 7 + o, 24, 12 + o, 'h')             # strap
    s.shade('H', None, 'h', group='HhVvYSskm')
    s.outline('k')
    return s


def backpack(bob=0):
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
    # logo: little shopping bag
    s.rect(9, 15 + o, 13, 18 + o, 'o')
    s.px(10, 14 + o, 'o'); s.px(12, 14 + o, 'o'); s.px(11, 13 + o, 'o')
    s.px(10, 16 + o, 'Y'); s.px(12, 16 + o, 'Y'); s.px(11, 17 + o, 'Y')
    s.outline('k')
    return s


def arm(bob=0):
    s = Spr(40, 44)
    o = bob
    s.line(21, 15 + o, 23, 20 + o, 'J', 2)
    s.line(23, 20 + o, 27, 17 + o, 'J', 2)
    s.rect(27, 16 + o, 28, 17 + o, 'S')
    s.shade('J', 'I', 'j')
    s.outline('k')
    return s


def courier_frame(i):
    bob = (0, -1, 0, 0)[i]
    s = scooter(ph=i)
    s.blit(rider(flap=i, bob=bob), 0, 0)
    s.blit(backpack(bob=bob), 0, 0)
    s.blit(arm(bob=bob), 0, 0)
    s.px(19, 14 + bob, 'j'); s.px(20, 15 + bob, 'j')   # strap over shoulder
    if i % 2 == 0:                                      # speed lines
        s.hline(0, 3, 26, 'N'); s.hline(0, 2, 29, 'N')
    else:
        s.hline(0, 2, 27, 'N'); s.hline(0, 3, 30, 'N')
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
    frames = [courier_frame(i) for i in range(4)]
    book.add('courier_ride', frames, COUR_PAL, fps=12, anchor=[20, 43])
    book.add('courier_dead', [courier_dead()], COUR_PAL, fps=1, anchor=[27, 23])


def main(only=None):
    book = Book(ASSETS, 'actors.json', PREV)
    builders = [('dog', build_dog), ('pigeon', build_pigeon), ('granny', build_granny), ('courier', build_courier)]
    for name, fn in builders:
        if only and name not in only:
            continue
        fn(book)
    if not only:
        book.save()


if __name__ == '__main__':
    main(sys.argv[1:] or None)
