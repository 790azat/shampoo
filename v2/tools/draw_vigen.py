#!/usr/bin/env python3
"""Vigen, the third hero: an auto mechanic in a black zip bomber jacket over a grey-teal tee, blue jeans,
khaki-grey sneakers, short dark beard and side-swept dark hair (after the photo Azat sent).
His special is a wrench thrown like a boomerang (wrench_spin).

Uses the posed-limb renderer of draw_heroes.py for the full hero animation set.

    python3 tools/draw_vigen.py      -> assets/hero_vigen_*.png, assets/wrench_spin.png, assets/vigen.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_heroes as dh  # noqa: E402

dh.HERO['vigen'] = {
    'pal': {**dh.COMMON,
            'H': '#2a1c16', 'h': '#4a3426', 'I': '#160e0a',             # dark side-swept hair
            'B': '#2a1c14', 'b': '#4a3224',                             # short beard
            'C': '#24242c', 'c': '#17171d', 'D': '#0e0e12', 'U': '#3a3a46',  # black bomber jacket
            'z': '#c8ccd6',                                             # silver zip
            'T': '#7f9a98', 't': '#5f7876',                             # grey-teal tee
            'P': '#4a6a9e', 'p': '#6a8cc0', 'O': '#33507c',             # blue jeans
            'F': '#8a8672', 'f': '#b8b4a0', 'G': '#3a3830', 'Z': '#6e6a58'},  # khaki-grey sneakers
    'sleeve': ('U', 'C', 'c'), 'sleeve_far': ('c', 'c', 'D'),
    'pants': ('p', 'P', 'O'), 'pants_far': ('P', 'O', 'O'),
    'watch': False, 'pocket': False,
}
dh.HEADS['vigen'] = dict(art="""
......hhhhhh....
....hhHHHHHHhh..
...hHHHHHHHHHHh.
..hHHHHHHHHHhHh.
..IHHHHHHHhhSS..
.IIIHHHHHSSSSS..
.IIISSSSSSSSSS..
.IIsSSIIISSIIS..
.IsLsSSeSSSSeS..
.IssSSSSSSSsSSS.
.IsSsSSSSSSsSS..
..sBBSSSSSSBBS..
..sBBBBBmmBBB...
...sBBBBBBBBs...
....sBBBBBBs....
......BBBB......
""", neck=(7, 15), mouth=(10, 12), ear=(3, 8), top=(7, 0))
dh.TORSOS['vigen'] = dict(art="""
.......cCCCCCc......
.....cCcTTTTTcCc....
...cCUUCTTTTTCzCc...
..cCUUUCcTTTcCzCCc..
.cCUUUUUCCCCCCzCCCc.
cCUUUUUUCCCCCCzCCCc.
cCUUUUUCCCCCCCzCCCc.
cCUUUUCCCCCCCCzCDCc.
cCUUUUCCCCCCCCzCDCc.
cCUUUCCCCCCCCCzCDCc.
cCUUUCCCCCCCCCzCCCc.
cCUUCCCCCCCCCCzCCcc.
cCUUCCCCCCCCCCzCCcc.
cCUCCCCCCCCCCCzCCcc.
cCUCCCCCCCCCCCzCCcc.
cCCCCCCCCCCCCCzCCcc.
.cDDDDDDDDDDDDDDDDc.
.cDcDcDcDcDcDcDcDc..
.......OOOOOO.......
""", hip=(9, 19), sh=(5, 5), sh_far=(15, 5), neck=(9, 2))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets')


def to_rgba(g, pal):
    out = np.zeros(g.shape + (4,), np.uint8)
    for ch in np.unique(g):
        if ch == '.':
            continue
        hx = pal.get(ch, dh.OL).lstrip('#')
        out[g == ch] = (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255)
    return out


def wrench():
    """14x14 chrome wrench (ring end + open jaw), 8 rotation frames drawn at 4x and reduced."""
    import math
    from PIL import ImageDraw
    frames = []
    for i in range(8):
        a = math.radians(45 * i)
        big = Image.new('L', (56, 56), 0)
        d = ImageDraw.Draw(big)
        c, s_ = math.cos(a), math.sin(a)
        p1 = (28 - 15 * c, 28 - 15 * s_)
        p2 = (28 + 15 * c, 28 + 15 * s_)
        d.line([p1, p2], fill=255, width=7)
        d.ellipse([p1[0] - 8, p1[1] - 8, p1[0] + 8, p1[1] + 8], fill=255)
        d.ellipse([p1[0] - 3, p1[1] - 3, p1[0] + 3, p1[1] + 3], fill=0)
        d.ellipse([p2[0] - 9, p2[1] - 9, p2[0] + 9, p2[1] + 9], fill=255)
        q = (p2[0] + 6 * c, p2[1] + 6 * s_)
        d.polygon([(q[0] - 5 * s_, q[1] + 5 * c), (q[0] + 5 * s_, q[1] - 5 * c), (p2[0] + 4 * s_ * 0, p2[1])], fill=0)
        d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=0)
        m = np.array(big.resize((14, 14), Image.BOX)) > 110
        img = np.zeros((14, 14, 4), np.uint8)
        yy, xx = np.mgrid[0:14, 0:14]
        light = (xx + yy) < 13
        img[m & light] = (232, 236, 244, 255)
        img[m & ~light] = (150, 158, 176, 255)
        up = np.zeros_like(m); up[1:] = m[:-1]
        edge = m & ~up
        img[edge] = (250, 252, 255, 255)
        fill = m.copy()
        out = np.zeros_like(m)
        out[1:] |= fill[:-1]; out[:-1] |= fill[1:]; out[:, 1:] |= fill[:, :-1]; out[:, :-1] |= fill[:, 1:]
        img[out & ~fill] = (26, 16, 36, 255)
        frames.append(img)
    return frames


def main(dest=OUT):
    pal = dh.HERO['vigen']['pal']
    man = {}
    for name, (poses, fps) in dh.build('vigen').items():
        frames, metas = [], []
        for P in poses:
            g, m = dh.render('vigen', P)
            frames.append(to_rgba(g, pal)); metas.append(m)
        key = f'hero_vigen_{name}'
        Image.fromarray(np.concatenate(frames, 1), 'RGBA').save(os.path.join(dest, key + '.png'))
        man[key] = {'file': key + '.png', 'w': dh.W, 'h': dh.H, 'frames': len(frames), 'fps': fps,
                    'anchor': [dh.AX, dh.GROUND], 'meta': metas}
    wf = wrench()
    Image.fromarray(np.concatenate(wf, 1), 'RGBA').save(os.path.join(dest, 'wrench_spin.png'))
    man['wrench_spin'] = {'file': 'wrench_spin.png', 'w': 14, 'h': 14, 'frames': 8, 'fps': 20, 'anchor': [7, 7]}
    if dest == OUT:
        json.dump(man, open(os.path.join(OUT, 'vigen.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else OUT)
