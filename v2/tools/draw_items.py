#!/usr/bin/env python3
"""Collectibles for SHAMPOO v2, drawn after the real products (Azat's photos):
BOOM Best (blue can, white vertical BOOM, orange BEST), Adrenaline Rush (black can, gold A),
VIP Blue (white pack, blue band, SMOKING KILLS box), TEREA Beige (two-tone box, white ring logo)
and Head & Shoulders Classic Clean (white bottle, navy cap, blue splash).

Used by draw_objects.build_items; run draw_objects.py to rebuild.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixkit import Spr, OUTLINE  # noqa: E402

FONT3 = {
    'A': ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'],
    'B': ['XX.', 'X.X', 'XX.', 'X.X', 'XX.'],
    'E': ['XXX', 'X..', 'XX.', 'X..', 'XXX'],
    'H': ['X.X', 'X.X', 'XXX', 'X.X', 'X.X'],
    'I': ['XXX', '.X.', '.X.', '.X.', 'XXX'],
    'P': ['XX.', 'X.X', 'XX.', 'X..', 'X..'],
    'R': ['XX.', 'X.X', 'XX.', 'X.X', 'X.X'],
    'S': ['.XX', 'X..', '.X.', '..X', 'XX.'],
    'T': ['XXX', '.X.', '.X.', '.X.', '.X.'],
    'V': ['X.X', 'X.X', 'X.X', 'X.X', '.X.'],
    '&': ['.X.', 'X.X', '.X.', 'X.X', '.XX'],
}
FONT_BOLD = {
    'B': ['XXX.', 'X..X', 'XXX.', 'X..X', 'XXX.'],
    'O': ['.XX.', 'X..X', 'X..X', 'X..X', '.XX.'],
    'M': ['X...X', 'XX.XX', 'X.X.X', 'X...X', 'X...X'],
}

PAL = {
    'k': OUTLINE, 'w': '#ffffff',
    # aluminium
    'L': '#f4f6fa', 'l': '#c9cfdb', 'm': '#8e97aa', 'n': '#5d6578',
    # BOOM: deep blue can, orange BEST
    'B': '#1f4fc4', 'U': '#4f86ec', 'b': '#132f80', 'O': '#ff8a1e', 'o': '#d8501a', 'Y': '#ffd23a',
    # Rush: black can, gold A
    'K': '#2c2934', 'J': '#4a4658', 'j': '#16141b', 'G': '#f2c14a', 'g': '#a8781e',
    # VIP: white pack, blue band, red crest
    'W': '#f6f4ef', 'X': '#cfc9bc', 'V': '#2350c8', 'v': '#15338a', 'R': '#d8283a', 'z': '#7a7a80',
    # TEREA beige
    'F': '#d9d1bf', 'f': '#aaa18c', 'E': '#bb8a5e', 'Q': '#d6a87c', 'e': '#8c6040',
    # Head & Shoulders
    'H': '#f3f6fb', 'h': '#c6d2e6', 'Z': '#16337c', 'C': '#2a6ad8', 'D': '#8cc4ff', 'd': '#4f96ee',
}


def text(s, x, y, msg, c, font=FONT3, gap=1):
    for ch in msg:
        g = font[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == 'X':
                    s.px(x + i, y + j, c)
        x += len(g[0]) + gap
    return x


def vtext(s, x, ybot, msg, c, font=FONT3, gap=1):
    """Text turned 90° counter-clockwise, read bottom to top (like on the BOOM can)."""
    off = 0
    for ch in msg:
        g = font[ch]
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == 'X':
                    s.px(x + j, ybot - off - i, c)
        off += len(g[0]) + gap
    return ybot - off


def can(body, hi, sh):
    """16x32 tall 450ml can, front facing."""
    s = Spr(16, 32)
    s.hline(4, 11, 1, 'm')
    s.hline(3, 12, 2, 'l'); s.px(6, 2, 'n'); s.px(7, 2, 'n')
    s.hline(3, 12, 3, 'm')
    s.hline(2, 13, 4, 'l'); s.px(3, 4, 'L')
    s.rect(2, 5, 13, 26, body)
    s.vline(3, 5, 26, hi)
    s.vline(12, 5, 26, sh); s.vline(13, 5, 26, sh)
    s.hline(2, 13, 27, 'l'); s.px(3, 27, 'L')
    s.hline(3, 12, 28, 'm')
    return s


def item_boom():
    s = can('B', 'U', 'b')
    vtext(s, 3, 25, 'BOOM', 'w', font=FONT_BOLD)       # big white BOOM up the can
    vtext(s, 9, 20, 'BEST', 'O')                         # orange BEST beside it
    # the orange "100% energy" badge at the bottom right
    s.rect(9, 23, 12, 25, 'O'); s.hline(10, 11, 22, 'O'); s.hline(10, 11, 26, 'o')
    s.px(10, 24, 'Y'); s.px(11, 24, 'Y')
    s.outline('k')
    return s


def item_rush():
    s = can('K', 'J', 'j')
    # "Adrenaline" in white script, "RUSH" in gold under it
    s.ascii(3, 7, """
.w..w.....
ww.www.ww.
""")
    s.hline(5, 10, 9, 'G')
    # the big gold A with its sharp left leg
    s.ascii(3, 11, """
.....GG...
....GGG...
....GgG...
...GG.G...
...G..GG..
..GG..GG..
..GGGGGG..
.GG....Gg.
.G.....GG.
GG.....GG.
G.......G.
""")
    s.hline(5, 10, 24, 'w')                    # 449 мл
    s.outline('k')
    return s


def item_vip():
    s = Spr(20, 30)
    s.rect(2, 2, 17, 27, 'W')
    s.vline(17, 2, 27, 'X')
    s.hline(2, 17, 8, 'X')                     # flip-top lid seam
    # blue band with VIP running up it
    s.rect(4, 2, 10, 19, 'V')
    s.vline(10, 2, 19, 'v')
    vtext(s, 5, 17, 'VIP', 'w')
    # red crest and the blue "V3 BLUE" line
    s.rect(13, 3, 14, 4, 'R'); s.px(13, 5, 'R'); s.px(14, 5, 'R')
    s.vline(14, 10, 16, 'V'); s.vline(13, 12, 16, 'R')
    # SMOKING KILLS box
    s.rect(3, 20, 16, 26, 'k')
    s.rect(4, 21, 15, 25, 'W')
    s.hline(5, 14, 22, 'z')
    s.hline(6, 13, 24, 'z')
    s.outline('k')
    return s


def item_terea():
    s = Spr(32, 20)
    # upper grey-beige half with the brain sketch and warning lines
    s.rect(1, 2, 30, 8, 'F')
    s.ascii(3, 3, """
.fff.
f.f.f
ff.ff
.fff.
""")
    for y in (3, 5, 7):
        s.hline(11, 28, y, 'f')
    # lower tan half: white ring logo + TEREA
    s.rect(1, 9, 30, 17, 'E')
    s.hline(1, 30, 9, 'Q')
    s.vline(30, 9, 17, 'e'); s.hline(1, 30, 17, 'e')
    s.ascii(3, 11, """
.www.
w...w
w....
w...w
.www.
""")
    text(s, 11, 11, 'TEREA', 'w')
    s.vline(30, 2, 8, 'f')
    s.outline('k')
    return s


def item_shampoo():
    s = Spr(18, 34)
    # navy flip cap
    s.rect(6, 1, 11, 5, 'Z'); s.vline(7, 2, 4, 'C')
    # shoulders and white body
    s.polyfill([(5, 6), (12, 6), (14, 9), (14, 31), (3, 31), (3, 9)], 'H')
    s.vline(13, 9, 31, 'h'); s.vline(14, 9, 31, 'h'); s.hline(4, 13, 31, 'h')
    # blue logo ring + H&S
    s.hline(5, 12, 10, 'C')
    text(s, 4, 12, 'H', 'Z', gap=0)
    text(s, 7, 12, '&', 'C', gap=0)
    text(s, 10, 12, 'S', 'Z', gap=0)
    # CLASSIC CLEAN lines
    s.hline(5, 11, 19, 'C'); s.hline(5, 10, 21, 'C')
    # the water splash
    s.ascii(6, 22, """
....dD..
..dDDDd.
.dDwDDDd
dDDDDwDd
.dDDDDd.
..ddCd..
""")
    s.hline(4, 7, 29, 'Z')
    s.outline('k')
    return s


ITEMS = (('boom', item_boom), ('rush', item_rush), ('vip', item_vip),
         ('terea', item_terea), ('shampoo', item_shampoo))
