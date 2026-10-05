#!/usr/bin/env python3
"""The boss «ШЕФ»: a slick guy in a black three-piece suit (white shirt, pocket square, trimmed beard,
dark quiff, black dress shoes), drawn after the photo Azat sent. Uses the posed-limb renderer of
draw_heroes.py. Also draws his projectile, a spinning business card.

    python3 tools/draw_boss.py        -> assets/boss_*.png + assets/boss.json
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_heroes as dh  # noqa: E402

dh.HERO['boss'] = {
    'pal': {**dh.COMMON,
            'H': '#231a16', 'h': '#3e2e26', 'I': '#120c0a',             # dark swept-up quiff
            'B': '#1e1410', 'b': '#3a2a20',                             # short trimmed beard
            'J': '#1e1e29', 'j': '#43435a', 'K': '#0f0f15',             # black jacket
            'V': '#14141b', 'o': '#4a4a58',                             # vest, buttons
            'W': '#f6f6f8', 'Q': '#e8e8ee',                             # shirt, pocket square
            'P': '#1a1a22', 'p': '#2a2a36', 'O': '#0e0e14',             # suit trousers
            'F': '#17171d', 'f': '#6a6a7a', 'G': '#08080b', 'Z': '#101015',  # black dress shoes
            'X': '#f2f2f6'},                                            # white shirt cuff
    'sleeve': ('j', 'J', 'K'), 'sleeve_far': ('J', 'K', 'K'),
    'pants': ('p', 'P', 'O'), 'pants_far': ('P', 'O', 'O'),
    'watch': True, 'pocket': False,
}
dh.HEADS['boss'] = dict(art="""
........hhhh....
.....hhhHHHHh...
...hhHHHHHHHHh..
..hHHHHHHHHHHH..
..HHHHHHHHHHHh..
.IIHHHHHHHHHH...
.IISSIHHSSSSS...
.IsLsSIISSSIIS..
.IsLsSSeSSSSeS..
.IssSSSSSSSsSSS.
.IsSsSSSSSSsSS..
..sBBSSSSSBBSS..
..sBBBBBmmBBB...
...sBBBBBBBBs...
....sBBBBBBs....
......BBBB......
""", neck=(7, 15), mouth=(10, 12), ear=(3, 8), top=(8, 0))
dh.TORSOS['boss'] = dict(art="""
.........WWWWW......
......jJJWWWWWJj....
....jJJJjWWWWWWjJj..
...jJJJJjVWWWWVjJJj.
..jJJJJJJjVWWWVjJJj.
.jJJJJJJJjVWWWVjQJj.
.jJJJJJJJjVVWVVjJJj.
.jJJJJJJJJjVWVjJJJj.
.jJJJJJJJJjVVVjJJJj.
.jJJJJJJJJjVoVjJJJj.
.jJJJJJJJJJjVjJJJJj.
.jJJJJJJJJJJoJJJJJj.
.jJJJJJJJJJjJjJJJJj.
.jJJJJJJJJjJJJjJJJj.
.jJJJJJJJJjJJJjJJJj.
.jJJJJJJJjJJJJJjJJj.
.jJJJJJJJjJJJJJjJJj.
..KKKKKKKKKKKKKKKK..
""", hip=(9, 18), sh=(5, 4), sh_far=(15, 4), neck=(10, 1))
# he is taller and slimmer than the heroes
dh.LEG = (11.5, 11.5)
dh.ARM = (9.5, 9.0)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets')

CHEST = {'dx': -2, 'dy': 9}          # the photo pose: fixing his jacket button


def anims():
    stand = dict(legN=(4, 3, 'flat'), legF=(-5, 3, 'flat'))
    walk = dh.walk()
    for f in walk:
        f['lean'] = 0
        f['armN'] = (f['armN'][0] * 0.7, 12)
        f['armF'] = (f['armF'][0] * 0.7, 12)
    return {
        'walk': (walk, 8),
        'idle': ([dict(stand, armN=CHEST, armF=None, breath=b) for b in (0, 1)], 2),
        # wind-up behind the head, flick forward, follow through
        'throw': ([dict(stand, armN=(-150, 60), armF=(20, 20), lean=-1),
                   dict(legN=(16, 6, 'flat'), legF=(-12, 6, 'toe'), armN=(95, 6), armF=(-20, 20), lean=2, mouth=True),
                   dict(legN=(14, 6, 'flat'), legF=(-10, 6, 'toe'), armN=(70, 10), armF=(-14, 20), lean=1)], 8),
        'hurt': ([dict(legN=(18, 22, 'flat'), legF=(-14, 18, 'toe'), armN=(70, 50), armF=(150, 20), lean=-3, mouth=True, hdx=-1)], 1),
        'dead': ([dict(legN=(24, 30, 'air'), legF=(-18, 30, 'air'), armN=(110, 30), armF=(-70, 20), mouth=True, air=0, hdx=-1)], 1),
    }


def card():
    """6x4 white business card turning in the air: 4 frames."""
    frames = []
    shapes = [["kkkkkkkk", "kWWWWWWk", "kWooWWWk", "kWWWWWWk", "kkkkkkkk"],
              ["..kkkk..", ".kWWWWk.", ".kWooWk.", ".kWWWWk.", "..kkkk.."],
              ["...kk...", "...kk...", "...kk...", "...kk...", "...kk..."],
              ["..kkkk..", ".kWWWWk.", ".kWWooWk", ".kWWWWk.", "..kkkk.."]]
    pal = dh.HERO['boss']['pal']
    for sh in shapes:
        g = np.zeros((5, 8, 4), np.uint8)
        for y, r in enumerate(sh):
            for x, c in enumerate(r[:8]):
                if c != '.':
                    hx = pal[c].lstrip('#')
                    g[y, x] = (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255)
        frames.append(g)
    return frames


def to_rgba(g):
    pal = dh.HERO['boss']['pal']
    out = np.zeros(g.shape + (4,), np.uint8)
    for ch in np.unique(g):
        if ch == '.':
            continue
        hx = pal.get(ch, dh.OL).lstrip('#')
        out[g == ch] = (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255)
    return out


def main(dest=OUT):
    man = {}
    for name, (poses, fps) in anims().items():
        frames, metas = [], []
        for P in poses:
            g, m = dh.render('boss', P)
            frames.append(to_rgba(g)); metas.append(m)
        key = f'boss_{name}'
        Image.fromarray(np.concatenate(frames, 1), 'RGBA').save(os.path.join(dest, key + '.png'))
        man[key] = {'file': key + '.png', 'w': dh.W, 'h': dh.H, 'frames': len(frames), 'fps': fps,
                    'anchor': [dh.AX, dh.GROUND], 'meta': metas}
    cf = card()
    Image.fromarray(np.concatenate(cf, 1), 'RGBA').save(os.path.join(dest, 'card_spin.png'))
    man['card_spin'] = {'file': 'card_spin.png', 'w': 8, 'h': 5, 'frames': 4, 'fps': 12, 'anchor': [4, 5]}
    if dest == OUT:
        json.dump(man, open(os.path.join(OUT, 'boss.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else OUT)
