#!/usr/bin/env python3
"""SHAMPOO v2 world art generator.

Writes to ../assets/:
  bg_sky.png, bg_clouds.png, bg_ararat.png            (shared)
  bg_<district>_far.png / _mid.png / _near.png         (per district)
  tiles_<district>.png, world_<district>.json          (per district)
and 2x mock scenes to tools/preview_world_<district>.png.

Usage: python3 draw_world.py [district ...]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from world_pix import Layer, BAYER4, mix, shade, periodic_noise  # noqa: E402
from world_sky import draw_sky, draw_clouds, draw_ararat  # noqa: E402
from world_city import (tuff_building, tree_round, tree_poplar, bush, far_city, far_hill,  # noqa: E402
                        tv_tower_far, car, lamp, fence, low_wall, bench, kiosk, sign, text,
                        TUFF_COLOURS, tuff, GLASS, GLASS_HI, GLASS_MID, LAUNDRY, TREE_G)
from world_landmarks import (government_house, history_museum, opera_house, swan_lake, cascade,  # noqa: E402
                             botero_cat, st_gregory, mother_armenia, ferris_wheel, swing_ride,
                             tv_tower, panel_block, arch, flag)
from world_tiles import build_tileset, NAMES  # noqa: E402

ASSETS = os.path.normpath(os.path.join(HERE, '..', 'assets'))
DISTRICTS = ['square', 'opera', 'cascade', 'cathedral', 'victory', 'tower']
GROUND_Y = 224

# vertical placement in the 270 view
Y_CLOUDS, Y_ARARAT = 8, 62
FAR_W, FAR_H, FAR_Y = 960, 110, 118      # far ground row ~ 104 -> y 222
MID_W, MID_H, MID_Y = 960, 140, 88       # mid ground row 132 -> y 220
NEAR_W, NEAR_H, NEAR_Y = 960, 110, 160   # near ground row 64 -> y 224; below = under-street (shows in pits)


# ======================================================================= FAR
FAR_TONES = {
    'square': [(160, 156, 208), (136, 132, 190), (176, 174, 218), (150, 148, 202)],
    'opera': [(156, 162, 210), (132, 140, 192), (172, 180, 220), (148, 156, 204)],
    'cascade': [(162, 158, 210), (138, 134, 192), (178, 176, 220), (152, 150, 204)],
    'cathedral': [(164, 156, 206), (140, 130, 186), (180, 174, 216), (154, 146, 200)],
    'victory': [(156, 164, 208), (132, 142, 190), (172, 182, 218), (148, 158, 202)],
    'tower': [(160, 160, 210), (136, 136, 192), (176, 178, 220), (150, 150, 204)],
}


def draw_far(d):
    rng = np.random.default_rng(100 + DISTRICTS.index(d))
    L = Layer(FAR_W, FAR_H)
    g = 104
    back, front, win, lit = FAR_TONES[d]
    hill_c = mix(back, (180, 196, 232), 0.35)
    if d in ('cascade', 'victory', 'tower'):
        far_hill(L, g - 30, 34, rng, hill_c)
        # tiny houses dotted on the hill
        for x in range(0, FAR_W, 7):
            col = L.a[:, x, 3]
            top = int(np.argmax(col > 0))
            if rng.random() < 0.35 and top < g - 14:
                yo = top + int(rng.integers(3, 12))
                L.rect(x, yo, 4, 3, back)
                L.px(x + 1, yo + 1, win)
    else:
        far_hill(L, g - 18, 14, rng, hill_c, ((1, 1), (3, .5), (9, .2)))
    far_city(L, g, rng, FAR_TONES[d], hmin=12 if d != 'tower' else 18, hmax=40 if d != 'tower' else 54)
    # the TV tower and the Cascade obelisk are visible from most of the city
    if d != 'tower':
        tv_tower_far(L, 700 if d != 'victory' else 180, g - 10, 86, back, mix(back, (220, 120, 140), 0.35))
    if d in ('square', 'opera'):
        ox = 250
        L.poly([(ox - 30, g - 20), (ox - 30, g - 28), (ox + 30, g - 52), (ox + 30, g - 20)], back)
        L.poly([(ox + 26, g - 52), (ox + 28, g - 80), (ox + 30, g - 80), (ox + 32, g - 52)], back)
    if d == 'tower':
        # distant Mother Armenia on her hill
        L.rect(380, g - 56, 8, 30, back)
        L.rect(383, g - 66, 2, 10, back)
        L.hline(377, g - 63, 12, back)
    L.rect(0, g, FAR_W, FAR_H - g, front)
    # bottom haze lines
    for y in range(g - 4, FAR_H):
        sel = BAYER4[y % 4, np.arange(FAR_W) % 4] < 3
        row = (L.a[y, :, 3] > 0) & sel
        L.a[y, row, :3] = lit
    return L


# ======================================================================= MID
def fill_buildings(L, x0, x1, ground, rng, colours, fl=(3, 6), trees=0.3, arcade=0.15, wmin=40, wmax=78):
    x = x0
    while x < x1 - 30:
        w = int(rng.integers(wmin, wmax))
        w = min(w, x1 - x)
        if w < 30:
            break
        col = colours[int(rng.integers(len(colours)))]
        tuff_building(L, x, ground, w, int(rng.integers(fl[0], fl[1] + 1)), col, rng,
                      arcade=rng.random() < arcade)
        x += w + int(rng.integers(0, 4))
        if rng.random() < trees and x < x1 - 20:
            gap = int(rng.integers(10, 20))
            if rng.random() < 0.5:
                tree_poplar(L, x + gap // 2, ground, int(rng.integers(40, 70)), rng, haze=0.12)
            else:
                tree_round(L, x + gap // 2, ground, int(rng.integers(9, 14)), rng, haze=0.12)
            x += gap


def mid_ground(L, ground, c_top, c):
    L.rect(0, ground, L.w, L.h - ground, c)
    L.hline(0, ground, L.w, c_top)


def tree_row(L, xs, ground, rng, rmin=10, rmax=16, haze=0.1):
    for x in xs:
        if rng.random() < 0.3:
            tree_poplar(L, x, ground, int(rng.integers(50, 80)), rng, haze=haze)
        else:
            tree_round(L, x, ground, int(rng.integers(rmin, rmax)), rng, haze=haze)


def draw_mid(d):
    rng = np.random.default_rng(200 + DISTRICTS.index(d))
    H = {'cascade': 170, 'victory': 186, 'tower': 236}.get(d, MID_H)
    L = Layer(MID_W, H)
    g = H - 8
    pave_top, pave = (196, 170, 160), (170, 146, 140)
    if d == 'square':
        fill_buildings(L, 300, 590, g, rng, ['pink', 'orange', 'apricot', 'rose'], fl=(3, 5), trees=0.2, arcade=0.3)
        fill_buildings(L, 770, 960, g, rng, ['cream', 'pink', 'orange'], fl=(3, 5), trees=0.2)
        government_house(L, 30, g, rng)
        history_museum(L, 600, g, rng)
        # singing fountain basin (mid distance) in front of the museum
        tree_row(L, [292, 760, 950], g, rng)
    elif d == 'opera':
        fill_buildings(L, 400, 960, g, rng, ['pink', 'cream', 'orange', 'rose', 'apricot', 'yellow'], fl=(3, 5), trees=0.5)
        fill_buildings(L, 0, 90, g, rng, ['cream', 'apricot'], fl=(3, 5), trees=0.5)
        opera_house(L, 115, g, rng)
        # opera park: lots of trees in front of the wings
        tree_row(L, [100, 124, 150, 176, 346, 372, 396, 420, 480, 600, 720, 840, 930], g, rng, 11, 17)
    elif d == 'cascade':
        # green hillside behind (Kanaker plateau)
        hill = np.clip(40 + 90 * (np.arange(MID_W) - 60) / 420, 18, 128)
        for x in range(MID_W):
            h = hill[x] + 4 * np.sin(x * 0.05)
            if x > 560:
                h = 128 - (x - 560) * 0.45
            h = max(18, h)
            L.vline(x, int(g - h), int(h), (104, 140, 92))
            L.vline(x, int(g - h), 2, (130, 166, 104))
        for x in range(110, 760, 13):
            col = L.a[:, x, 3]
            top = int(np.argmax(col > 0))
            tree_round(L, x + int(rng.integers(-3, 3)), top + 12, int(rng.integers(6, 10)), rng, haze=0.18)
        fill_buildings(L, 500, 960, g, rng, ['pink', 'cream', 'apricot', 'rose', 'yellow'], fl=(3, 6), trees=0.3)
        fill_buildings(L, 0, 120, g, rng, ['cream', 'pink'], fl=(3, 5), trees=0.6)
        cascade(L, 140, g, rng, H=118)
        tree_row(L, [126, 486], g, rng, 9, 12)
    elif d == 'cathedral':
        fill_buildings(L, 410, 960, g, rng, ['orange', 'cream', 'grey', 'pink', 'apricot', 'yellow'], fl=(4, 7), trees=0.3)
        fill_buildings(L, 0, 100, g, rng, ['pink', 'apricot'], fl=(4, 7), trees=0.3)
        st_gregory(L, 140, g, rng)
        tree_row(L, [112, 128, 392, 404], g, rng, 9, 13)
    elif d == 'victory':
        # park hill (Victory park sits above the city)
        n = periodic_noise(MID_W, rng, ((1, 1), (3, .4), (7, .15)))
        for x in range(MID_W):
            h = int(36 + 10 * n[x])
            L.vline(x, g - h, h, (92, 140, 80))
            L.vline(x, g - h, 2, (124, 170, 96))
            for y in range(g - h + 3, g, 1):  # mown stripes / paths
                if (x + y * 2) % 23 == 0 or (BAYER4[y % 4, x % 4] < 2 and (x // 40) % 2):
                    L.px(x, y, (104, 152, 86))
        # stepped stone paths up the hill
        for px0 in (40, 430, 700):
            for k in range(12):
                L.rect(px0 + k * 3, g - 2 - k * 3, 10, 2, (196, 186, 170))
                L.hline(px0 + k * 3, g - 2 - k * 3, 10, (226, 218, 204))
        mother_armenia(L, 300, g - 36, rng)
        ferris_wheel(L, 120, g - 30, 38, rng)
        swing_ride(L, 230, g - 34, rng)
        xs = list(range(0, 960, 22))
        for x in xs:
            if not (270 < x < 400 or 70 < x < 170 or 205 < x < 260):
                col = L.a[:, x % MID_W, 3]
                top = int(np.argmax(col > 0)) if col.any() else g - 50
                if rng.random() < 0.35:
                    tree_poplar(L, x, top + 8, int(rng.integers(40, 64)), rng, haze=0.1)
                else:
                    tree_round(L, x, top + 8, int(rng.integers(9, 14)), rng, haze=0.1)
        # soviet blocks at the foot of the hill
        for x in (500, 600, 760, 860):
            panel_block(L, x, g, 60, int(rng.integers(5, 9)), rng, colour=(210, 190, 170))
        tree_row(L, [20, 60, 200, 260, 420, 470, 680, 740, 940], g, rng, 10, 14)
    elif d == 'tower':
        # dry golden hillside of Nork with the TV tower on its crest
        n = periodic_noise(MID_W, rng, ((1, 1), (2, .5), (5, .2)))
        for x in range(MID_W):
            dx = min(abs(x - 300), MID_W - abs(x - 300))
            h = int(40 + 26 * np.exp(-(dx / 220) ** 2) + 6 * n[x])
            L.vline(x, g - h, h, (200, 172, 112))
            L.vline(x, g - h, 2, (226, 200, 136))
            for y in range(g - h + 3, g):
                b = BAYER4[y % 4, x % 4]
                if ((x + (y // 5) * 3) % 13 == 0) or (y > g - h + 8 and (y // 6) % 3 == 0 and b < 3):
                    L.px(x, y, (178, 150, 98))
                elif y < g - h + 6 and b < 4:
                    L.px(x, y, (214, 188, 126))
        for x in range(0, MID_W, 9):  # shrubs on the slope
            top = int(np.argmax(L.a[:, x, 3] > 0))
            if rng.random() < 0.6:
                y = top + int(rng.integers(4, 40))
                bush(L, x, y, 8, 4, rng, haze=0.1, pal=[(110, 130, 70), (140, 160, 80), (170, 186, 96), (196, 206, 120)])
        tv_tower(L, 300, g - 64, 152, rng)
        # soviet panel blocks climbing the hill
        for x, w, f, yo in ((-20, 56, 12, 24), (60, 64, 9, 30), (140, 50, 14, 40), (390, 60, 9, 52),
                            (470, 56, 12, 40), (550, 64, 9, 30), (850, 56, 14, 26)):
            panel_block(L, x, g - yo + 20, w, f, rng,
                        colour=[(198, 188, 178), (214, 196, 170), (186, 186, 190), (220, 176, 150)][int(rng.integers(4))])
        fill_buildings(L, 630, 840, g, rng, ['pink', 'grey', 'cream'], fl=(2, 4), trees=0.4, wmax=60)
        tree_row(L, [210, 236, 350, 376, 620], g, rng, 9, 13)
    mid_ground(L, g, pave_top, pave)
    return L, g


# ====================================================================== NEAR
def fountain(L, x, ground, w, rng):
    """Republic Square singing fountains: basalt rim, water jets of varied height."""
    rim, rim_hi, rim_sh = (120, 112, 124), (160, 152, 164), (86, 80, 92)
    water, wl = (96, 160, 220), (180, 220, 250)
    L.rect(x, ground - 6, w, 6, rim)
    L.hline(x, ground - 6, w, rim_hi)
    L.hline(x, ground - 1, w, rim_sh)
    for i, jx in enumerate(range(x + 4, x + w - 3, 6)):
        h = [24, 34, 40, 30, 20][i % 5] + int(rng.integers(-3, 4))
        L.rect(jx, ground - 6 - h, 2, h, wl)
        L.vline(jx + 1, ground - 6 - h + 3, h - 3, water)
        L.px(jx - 1, ground - 6 - h + 1, (240, 250, 255))
        L.px(jx + 2, ground - 6 - h + 2, (240, 250, 255))
        L.px(jx - 1, ground - 6 - h + 6, wl)
        L.px(jx + 3, ground - 6 - h + 7, wl)
        L.px(jx - 2, ground - 6 - h + 10, wl)
    for xx in range(x + 2, x + w - 2, 4):
        L.px(xx, ground - 5, (240, 250, 255))


def cafe(L, x, ground, rng, colour):
    """Café terrace: umbrella, table, two chairs."""
    c, sh = colour, shade(colour, 0.75)
    L.vline(x + 10, ground - 26, 26, (80, 74, 84))
    L.poly([(x - 2, ground - 22), (x + 4, ground - 30), (x + 17, ground - 30), (x + 23, ground - 22)], c)
    L.hline(x - 2, ground - 22, 26, sh)
    for xx in range(x, x + 22, 4):
        L.vline(xx, ground - 21, 2, sh if (xx // 4) % 2 else (248, 244, 236))
    L.hline(x + 5, ground - 29, 11, shade(c, 1.25))
    L.rect(x + 5, ground - 10, 11, 2, (236, 232, 224))
    L.vline(x + 10, ground - 8, 8, (80, 74, 84))
    for cx in (x + 1, x + 18):
        L.vline(cx, ground - 12, 12, (96, 70, 56))
        L.hline(cx - (0 if cx < x + 10 else 3), ground - 7, 4, (130, 92, 66))
        L.vline(cx + (3 if cx < x + 10 else -3), ground - 7, 7, (96, 70, 56))
    L.px(x + 8, ground - 11, (250, 250, 250))
    L.px(x + 12, ground - 11, (180, 60, 60))


def garage(L, x, ground, rng):
    """Soviet corrugated metal garage, painted and rusty."""
    c = [(80, 120, 150), (110, 140, 96), (150, 150, 156), (176, 120, 80)][int(rng.integers(4))]
    hi, sh = shade(c, 1.2), shade(c, 0.72)
    w, h = 34, 22
    L.rect(x, ground - h, w, h, c)
    for xx in range(x + 1, x + w, 2):
        L.vline(xx, ground - h + 2, h - 2, sh)
    L.hline(x - 1, ground - h, w + 2, hi)
    L.hline(x - 1, ground - h + 1, w + 2, sh)
    L.rect(x + 4, ground - h + 4, w - 8, h - 4, shade(c, 0.9))
    L.vline(x + w // 2, ground - h + 4, h - 4, sh)
    for k in range(4):
        L.px(x + int(rng.integers(3, w - 3)), ground - h + int(rng.integers(3, h - 2)), (150, 82, 50))
        L.vline(x + int(rng.integers(3, w - 3)), ground - h + 2, int(rng.integers(2, 6)), (150, 82, 50))
    L.px(x + w // 2 - 2, ground - 10, (60, 60, 70))
    text(L, x + 6, ground - h + 6, "ԳԱՐԱԺ", (250, 250, 240))


def power_pole(L, x, ground):
    L.rect(x, ground - 52, 3, 52, (170, 168, 160))
    L.vline(x + 2, ground - 52, 52, (130, 128, 124))
    L.hline(x - 6, ground - 48, 15, (110, 106, 104))
    for ix in (x - 6, x + 8, x + 1):
        L.px(ix, ground - 49, (230, 230, 240))


def draw_near(d):
    rng = np.random.default_rng(300 + DISTRICTS.index(d))
    L = Layer(NEAR_W, NEAR_H)
    g = 64
    side_top, side = (178, 166, 162), (150, 138, 136)
    if d == 'square':
        for x in (0, 320, 640):
            low_wall(L, x + 10, g, 110, 9, 'pink')
            fence(L, x + 10, g - 11, 110, 9)
        fountain(L, 140, g, 96, rng)
        fountain(L, 560, g, 70, rng)
        for x in (128, 250, 460, 700, 900):
            lamp(L, x, g, 46)
        kiosk(L, 270, g, 34, rng, word='ՀԱՑ')
        kiosk(L, 870, g, 30, rng, word='ՄԹԵՐՔ')
        car(L, 330, g, rng, 'lada', (232, 232, 226))
        car(L, 380, g, rng, 'sedan', (64, 64, 72))
        car(L, 740, g, rng, 'van', (250, 210, 60))
        car(L, 800, g, rng, 'lada', (200, 60, 56))
        for x in (20, 60, 480, 520, 660):
            bush(L, x, g, 26, 10, rng)
        tree_round(L, 440, g, 17, rng)
        tree_round(L, 680, g, 15, rng)
    elif d == 'opera':
        for x in range(0, 960, 40):
            if not 370 < x < 540:
                bush(L, x + 20, g, 44, 7, rng)
        swan_lake(L, 380, g, 150)
        for x, c in ((40, (210, 50, 60)), (80, (240, 240, 232)), (120, (210, 50, 60)), (620, (40, 110, 80)),
                     (660, (250, 250, 240)), (700, (40, 110, 80))):
            cafe(L, x, g, rng, c)
        kiosk(L, 170, g, 32, rng, word='ՍՐՃԱՐԱՆ')
        for x in (10, 230, 300, 560, 760, 840, 920):
            tree_round(L, x, g, int(rng.integers(14, 19)), rng)
        for x in (360, 548, 740):
            lamp(L, x, g, 44)
        for x in (270, 520, 800, 880):
            bench(L, x, g)
        for x in (340, 600, 780):
            bush(L, x, g, 24, 9, rng)
    elif d == 'cascade':
        for x in range(0, 960, 40):
            if (x // 40) % 3 != 1:
                bush(L, x + 20, g, 40, 6, rng)
        botero_cat(L, 250, g)
        for x in (60, 420, 740):
            low_wall(L, x, g, 120, 7, 'white')
        for x in range(64, 180, 8):
            L.rect(x, g - 11, 6, 3, LAUNDRY[(x // 8) % len(LAUNDRY)])   # flower bed
            L.px(x + 2, g - 12, (250, 250, 250))
        for x in range(424, 540, 8):
            L.rect(x, g - 11, 6, 3, LAUNDRY[(x // 8 + 2) % len(LAUNDRY)])
        for x in (30, 200, 330, 600, 680, 880):
            tree_round(L, x, g, int(rng.integers(13, 18)), rng)
        for x in (190, 400, 560, 860):
            lamp(L, x, g, 44)
        kiosk(L, 590, g, 32, rng, word='ՍՐՃԱՐԱՆ')
        car(L, 760, g, rng, 'sedan')
        car(L, 806, g, rng, 'lada')
        fountain(L, 470, g, 40, rng)
    elif d == 'cathedral':
        for x in (0, 480):
            low_wall(L, x, g, 200, 8, 'orange')
            fence(L, x, g - 10, 200, 10)
        for x in (40, 110, 230, 330, 520, 640, 760, 880):
            tree_round(L, x, g, int(rng.integers(14, 19)), rng)
        for x in (90, 300, 600, 840):
            bench(L, x, g)
        for x in (210, 450, 700, 930):
            lamp(L, x, g, 46)
        # small khachkar (cross-stone)
        for kx in (400, 800):
            L.rect(kx, g - 26, 12, 26, (206, 150, 108))
            L.vline(kx, g - 26, 26, (232, 186, 140))
            L.vline(kx + 11, g - 26, 26, (160, 104, 80))
            L.vline(kx + 6, g - 22, 14, (160, 104, 80))
            L.hline(kx + 3, g - 17, 7, (160, 104, 80))
            L.rect(kx - 2, g - 3, 16, 3, (150, 146, 152))
        car(L, 250, g, rng, 'sedan', (232, 232, 226))
        car(L, 700, g, rng, 'lada', (70, 110, 170))
        for x in (150, 420, 560, 980):
            bush(L, x, g, 22, 9, rng)
    elif d == 'victory':
        for x in range(0, 960, 160):
            fence(L, x, g, 150, 14, (60, 90, 70), (110, 150, 120))
        for x in (20, 140, 260, 380, 470, 590, 710, 830):
            if rng.random() < 0.3:
                tree_poplar(L, x, g, int(rng.integers(50, 64)), rng)
            else:
                tree_round(L, x, g, int(rng.integers(14, 19)), rng)
        for x in (60, 200, 320, 520, 650, 780, 900):
            bush(L, x, g, 30, 11, rng)
        kiosk(L, 420, g, 30, rng, word='ՄԹԵՐՔ')
        for x in (100, 560, 870):
            bench(L, x, g)
        for x in (180, 620):
            lamp(L, x, g, 44)
    elif d == 'tower':
        for i, x in enumerate((40, 76, 112, 520, 556)):
            garage(L, x, g, rng)
        for x in (170, 400, 700, 900):
            power_pole(L, x, g)
        # sagging wires (wrap)
        for k in range(2):
            pts = []
            poles = [170, 400, 700, 900, 1130]
            for a, b in zip(poles[:-1], poles[1:]):
                for t in np.linspace(0, 1, 40):
                    pts.append((a + 1 + (b - a) * t, g - 48 + k * 3 + 10 * 4 * t * (1 - t)))
            for p0, p1 in zip(pts[:-1], pts[1:]):
                L.line([p0, p1], (60, 58, 70))
        car(L, 200, g, rng, 'lada', (110, 150, 110))
        car(L, 610, g, rng, 'van', (236, 236, 230))
        car(L, 760, g, rng, 'lada', (200, 60, 56))
        for x in (300, 350, 460, 820, 940):
            bush(L, x, g, 26, 10, rng, pal=[(84, 110, 58), (116, 142, 70), (150, 170, 86), (186, 196, 110)])
        for x in (260, 490, 660, 860):
            tree_round(L, x, g, int(rng.integers(12, 16)), rng)
        kiosk(L, 420, g, 30, rng, word='ՀԱՑ')
    L.rect(0, g, NEAR_W, 7, side)
    L.hline(0, g, NEAR_W, side_top)
    L.hline(0, g + 6, NEAR_W, shade(side, .7))
    # below street level: dark retaining wall / earth, darker with depth (seen in pits)
    wall = UNDER[d]
    L.rect(0, g + 7, NEAR_W, NEAR_H - g - 7, wall)
    for r, y in enumerate(range(g + 7, NEAR_H, 6)):
        L.hline(0, y + 5, NEAR_W, shade(wall, .8))
        for x in range((r % 2) * 9, NEAR_W, 18):
            L.vline(x, y, 5, shade(wall, .8))
    yy, xx = np.mgrid[0:NEAR_H, 0:NEAR_W]
    for k, y0 in enumerate((g + 20, g + 32)):
        sel = (yy >= y0) & (BAYER4[yy % 4, xx % 4] < (8 if k == 0 else 16))
        L.a[sel, :3] = shade(wall, 0.72 - 0.12 * k)
    return L


UNDER = {'square': (112, 72, 70), 'opera': (82, 58, 46), 'cascade': (150, 144, 134),
         'cathedral': (84, 80, 90), 'victory': (70, 52, 42), 'tower': (76, 54, 56)}


# ===================================================================== OUTPUT
def save_png(L, name):
    L.save(os.path.join(ASSETS, name))


def composite(d, layers, tiles_img, scroll=0):
    """Mock 480x270 scene: all layers + ground strip + floating platform."""
    view = Image.new('RGBA', (480, 270))
    for lay in layers:
        im = Image.open(os.path.join(ASSETS, lay['file'])).convert('RGBA')
        off = int(scroll * lay['parallax']) % im.width
        x = -off
        while x < 480:
            if x >= 0:
                view.alpha_composite(im, (x, lay['y']))
            else:
                view.alpha_composite(im.crop((-x, 0, im.width, im.height)), (0, lay['y']))
            x += im.width
    def tile(n):
        c, r = NAMES[n]
        return tiles_img.crop((c * 16, r * 16, c * 16 + 16, r * 16 + 16))
    # ground: main strip with a gap, a step up block and stairs
    for col in range(30):
        if col in (12, 13):
            continue
        top = 'top_r' if col == 11 else ('top_l' if col == 14 else ('top2' if col % 7 == 3 else 'top'))
        fill = 'side_r' if col == 11 else ('side_l' if col == 14 else ['fill', 'fill2', 'fill3'][col % 3])
        if col in (22, 23, 24, 25, 26, 27, 28, 29):
            continue
        view.alpha_composite(tile(top), (col * 16, 224))
        view.alpha_composite(tile(fill), (col * 16, 240))
        view.alpha_composite(tile(fill), (col * 16, 256))
    # raised section with stairs
    view.alpha_composite(tile('stairs_r'), (22 * 16, 208))
    view.alpha_composite(tile('inner_r'), (22 * 16, 224))
    for col in range(23, 30):
        view.alpha_composite(tile('top' if col != 26 else 'top3'), (col * 16, 208))
        view.alpha_composite(tile('fill'), (col * 16, 224))
        view.alpha_composite(tile('fill2'), (col * 16, 240))
        view.alpha_composite(tile('fill'), (col * 16, 256))
    for col in (22,):
        view.alpha_composite(tile('fill'), (col * 16, 240))
        view.alpha_composite(tile('fill3'), (col * 16, 256))
    # floating one-way platform + floating ground chunk + props
    for i, n in enumerate(['plat_l', 'plat', 'plat', 'plat_r']):
        view.alpha_composite(tile(n), ((6 + i) * 16, 160))
    for i, (a, b) in enumerate((('top_l', 'bot_l'), ('top', 'bot'), ('top_r', 'bot_r'))):
        view.alpha_composite(tile(a), ((15 + i) * 16, 144))
        view.alpha_composite(tile(b), ((15 + i) * 16, 160))
    view.alpha_composite(tile('deco_flowers'), (16 * 16, 128))
    view.alpha_composite(tile('crate'), (3 * 16, 208))
    view.alpha_composite(tile('crate'), (4 * 16, 208))
    view.alpha_composite(tile('crate'), (3 * 16, 192))
    view.alpha_composite(tile('block'), (19 * 16, 208))
    view.alpha_composite(tile('block2'), (20 * 16, 208))
    view.alpha_composite(tile('block'), (20 * 16, 192))
    view.alpha_composite(tile('deco_grass'), (1 * 16, 208))
    view.alpha_composite(tile('deco_special'), (8 * 16, 208))
    view.alpha_composite(tile('deco_rocks'), (10 * 16, 208))
    view.alpha_composite(tile('deco_crack'), (5 * 16, 240))
    view.alpha_composite(tile('deco_grass'), (27 * 16, 192))
    view.alpha_composite(tile('deco_flowers'), (28 * 16, 192))
    view.alpha_composite(tile('barrel'), (25 * 16, 192))
    # hero-sized marker (56px) to judge scale
    # heroes for scale, if the actors worker has drawn them (read only)
    for name, x, y in (('hero_azat_idle', 150, 224), ('hero_arsen_idle', 120, 160)):
        p = os.path.join(ASSETS, name + '.png')
        meta = os.path.join(ASSETS, 'heroes.json')
        if os.path.exists(p) and os.path.exists(meta):
            try:
                m = json.load(open(meta))[name]
                fr = Image.open(p).convert('RGBA').crop((0, 0, m['w'], m['h']))
                view.alpha_composite(fr, (x - m['anchor'][0], y - m['anchor'][1]))
            except Exception:
                pass
    return view


def build_district(d, shared):
    mid, mg = draw_mid(d)
    far = draw_far(d)
    near = draw_near(d)
    save_png(far, f'bg_{d}_far.png')
    save_png(mid, f'bg_{d}_mid.png')
    save_png(near, f'bg_{d}_near.png')
    sheet = build_tileset(d, DISTRICTS.index(d))
    save_png(sheet, f'tiles_{d}.png')
    mid_y = 220 - mg
    layers = [
        {'file': 'bg_sky.png', 'parallax': 0.0, 'y': 0, 'w': 480, 'h': 270},
        {'file': 'bg_clouds.png', 'parallax': 0.05, 'y': Y_CLOUDS, 'w': 960, 'h': 60},
        {'file': 'bg_ararat.png', 'parallax': 0.08, 'y': Y_ARARAT, 'w': 960, 'h': 120},
        {'file': f'bg_{d}_far.png', 'parallax': 0.2, 'y': FAR_Y, 'w': FAR_W, 'h': FAR_H},
        {'file': f'bg_{d}_mid.png', 'parallax': 0.45, 'y': mid_y, 'w': MID_W, 'h': mid.h},
        {'file': f'bg_{d}_near.png', 'parallax': 0.75, 'y': NEAR_Y, 'w': NEAR_W, 'h': NEAR_H},
    ]
    manifest = {
        'district': d,
        'ground_y': GROUND_Y,
        'layers': layers,
        'tiles': {'file': f'tiles_{d}.png', 'size': 16, 'cols': 8, 'rows': 4, 'names': NAMES,
                  'one_way': ['plat_l', 'plat', 'plat_r'],
                  'breakable': ['crate', 'barrel'],
                  'decor': ['deco_grass', 'deco_flowers', 'deco_crack', 'deco_rocks', 'deco_special'],
                  'slopes': {'stairs_r': 'up_right', 'stairs_l': 'up_left'}},
        'notes': 'Layers tile horizontally (repeat every w px). Draw back to front in list order; '
                 'x offset = -camera_x * parallax. Tiles: one-way platforms are solid only on their top 6 px; '
                 'deco_* are non-solid overlays placed on the tile above the ground (deco_crack overlays a fill tile).',
    }
    with open(os.path.join(ASSETS, f'world_{d}.json'), 'w') as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    tiles_img = Image.open(os.path.join(ASSETS, f'tiles_{d}.png')).convert('RGBA')
    return layers, tiles_img


def main(args):
    os.makedirs(ASSETS, exist_ok=True)
    save_png(draw_sky(), 'bg_sky.png')
    save_png(draw_clouds(), 'bg_clouds.png')
    save_png(draw_ararat(), 'bg_ararat.png')
    for d in (args or DISTRICTS):
        layers, tiles_img = build_district(d, None)
        v = composite(d, layers, tiles_img, scroll=0)
        v.resize((960, 540), Image.NEAREST).save(os.path.join(HERE, f'preview_world_{d}.png'))
        print('ok', d)


if __name__ == '__main__':
    main(sys.argv[1:])
