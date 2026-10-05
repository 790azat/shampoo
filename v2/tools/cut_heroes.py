#!/usr/bin/env python3
"""Heroes cut straight from Azat's own sprite sheets (uploads), so they look exactly like him and Arsen.

Each frame is taken from a panel of the sheet, masked with a cached matte (tools/mattes, made once
with rembg's birefnet-general-lite, see make_mattes), scaled down to game size, colour-quantised
to a small per-hero palette and aligned on a shared anchor (feet for grounded frames, head height
for airborne ones). Meta per frame: mouth, head top, ear, hand, can tilt (see render.js).

    python3 tools/cut_heroes.py            -> assets/hero_*.png + assets/heroes.json
    python3 tools/cut_heroes.py <dir>      -> previews only
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets')
MATTES = os.path.join(HERE, 'mattes')
UPLOADS = '/mnt/project-files/uploads/hearth/'
OL = (20, 16, 24)

SHEETS = {'azat': '0315cdac-852b-4c66-a2f7-8ff699f69605', 'arsen': '13800bf5-f165-4cba-95f3-111c3728c992'}
PANELS = {
    'azat': {'idle': (590, 50, 935, 205), 'walk': (965, 50, 1355, 205), 'run': (1355, 50, 1760, 205),
             'jump': (585, 245, 985, 400), 'fall': (1000, 245, 1375, 400), 'attack': (1375, 245, 1765, 400),
             'special': (585, 445, 1225, 615), 'hurt': (1245, 445, 1405, 615), 'dead': (1420, 445, 1760, 615),
             'extra': (580, 620, 1400, 850)},
    'arsen': {'idle': (505, 25, 1052, 197), 'walk': (1052, 25, 1748, 197), 'run': (505, 212, 1100, 388),
              'jump': (1100, 212, 1748, 388), 'fall': (505, 385, 1048, 542), 'attack': (1048, 385, 1748, 542),
              'hurt': (505, 542, 722, 698), 'dead': (722, 542, 1172, 698), 'special': (1172, 542, 1748, 698),
              'extra': (500, 700, 1180, 887)},
}
# standing height in the sheet (px) -> game height
STAND = {'azat': 141, 'arsen': 156}
GAME_H = 60
# some panels of the sheet are drawn bigger than the idle row
ZOOM = {'azat': {'extra': 183 / 141, 'special': 151 / 141}, 'arsen': {}}

# frame = (panel, box inside the panel); 'air' frames are aligned by the head instead of the feet
F = {
    'azat': {
        'idle': [('idle', (5, 6, 80, 147)), ('idle', (89, 6, 162, 147)), ('idle', (173, 5, 246, 147)), ('idle', (256, 6, 328, 147))],
        'walk': [('walk', (3, 5, 70, 148)), ('walk', (71, 5, 152, 148)), ('walk', (154, 4, 216, 148)), ('walk', (216, 4, 296, 148)), ('walk', (298, 5, 377, 148))],
        'run': [('run', (7, 5, 101, 148)), ('run', (101, 8, 197, 151)), ('run', (200, 6, 286, 151)), ('run', (286, 8, 390, 151))],
        'jump': [('jump', (83, 19, 172, 144)), ('jump', (190, 0, 269, 109))],
        'fall': [('jump', (293, 25, 387, 144)), ('fall', (16, 26, 111, 150))],
        'land': [('fall', (243, 48, 336, 150))],
        'crouch': [('jump', (6, 56, 81, 154))],
        'shoot': [('attack', (0, 25, 101, 153)), ('attack', (101, 19, 196, 153))],
        'drop': [('special', (10, 10, 100, 161)), ('special', (180, 8, 279, 160)), ('special', (319, 4, 415, 161))],
        'hurt': [('hurt', (19, 19, 137, 154))],
        'dead': [('dead', (11, 85, 159, 139))],
        'smoke': [('extra', (342, 49, 432, 207))],
        'phone': [('extra', (140, 47, 222, 230))],
    },
    'arsen': {
        'idle': [('idle', (16, 14, 101, 170)), ('idle', (118, 14, 199, 167)), ('idle', (223, 14, 306, 169)), ('idle', (331, 14, 412, 170)), ('idle', (435, 13, 519, 169))],
        'walk': [('walk', (10, 12, 98, 170)), ('walk', (98, 15, 184, 169)), ('walk', (184, 14, 276, 170)), ('walk', (278, 14, 367, 170)),
                 ('walk', (370, 14, 459, 170)), ('walk', (461, 14, 562, 168)), ('walk', (566, 14, 669, 170))],
        'run': [('run', (7, 21, 119, 159)), ('run', (123, 21, 234, 165)), ('run', (234, 21, 344, 162)), ('run', (344, 21, 453, 162)), ('run', (453, 21, 568, 165))],
        'jump': [('jump', (119, 32, 222, 163)), ('jump', (240, 3, 332, 133))],
        'fall': [('jump', (347, 8, 438, 136)), ('fall', (344, 20, 425, 134))],
        'land': [('jump', (438, 32, 546, 163))],
        'crouch': [('jump', (30, 55, 114, 163))],
        'shoot': [('attack', (114, 21, 217, 148)), ('attack', (217, 8, 306, 149)), ('attack', (490, 22, 602, 151))],
        'drop': [('special', (300, 0, 432, 148)), ('special', (432, 0, 566, 148))],
        'hurt': [('hurt', (10, 29, 97, 148))],
        'dead': [('dead', (256, 80, 429, 137))],
        # Azat asked not to have Arsen sit on a crate: he smokes standing, in his drinking pose
        'smoke': [('extra', (355, 16, 441, 176))],
        'drink': [('extra', (355, 16, 441, 176))],
        'phone': [('extra', (135, 16, 212, 177))],
    },
}
AIR = {'jump', 'fall'}
FPS = {'idle': 3, 'walk': 9, 'run': 12, 'jump': 1, 'fall': 1, 'land': 1, 'crouch': 1, 'shoot': 14, 'drop': 6,
       'hurt': 1, 'dead': 1, 'talk': 11, 'smoke': 4, 'vape': 3, 'drink': 4, 'chill': 3}


def make_mattes(hero):
    """One-off: python3 -c 'import cut_heroes as c; c.make_mattes("azat")' (needs rembg)."""
    from rembg import remove, new_session
    s = new_session('birefnet-general-lite')
    sheet = Image.open(UPLOADS + SHEETS[hero]).convert('RGB')
    for name, box in PANELS[hero].items():
        im = sheet.crop(box)
        big = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        remove(big, session=s, only_mask=True).resize(im.size, Image.BOX).save(os.path.join(MATTES, f'm_{hero}_{name}.png'))


def cut(hero, sheet, panel, box, k):
    px0, py0, _, _ = PANELS[hero][panel]
    x0, y0, x1, y1 = box
    rgb = np.array(sheet.crop((px0 + x0, py0 + y0, px0 + x1, py0 + y1))).astype(float)
    m = np.array(Image.open(os.path.join(MATTES, f'm_{hero}_{panel}.png')).crop((x0, y0, x1, y1))).astype(float) / 255
    w, h = round((x1 - x0) / k), round((y1 - y0) / k)
    # premultiplied box filter so the dark sheet background does not bleed into the edges
    pm = Image.fromarray(np.uint8(np.clip(rgb * m[..., None], 0, 255))).resize((w, h), Image.BOX)
    ma = np.array(Image.fromarray(np.uint8(m * 255)).resize((w, h), Image.BOX)).astype(float) / 255
    col = np.array(pm).astype(float) / np.maximum(ma, 1e-3)[..., None]
    a = ma > 0.5
    return np.clip(col, 0, 255), a


def quantise(frames, n):
    px = np.concatenate([c[a] for c, a in frames])
    q = Image.fromarray(np.uint8(px[None]), 'RGB').quantize(n, method=Image.Quantize.MEDIANCUT, kmeans=4)
    pal = np.array(q.getpalette()[:n * 3]).reshape(-1, 3)
    out = []
    for c, a in frames:
        d = ((c[..., None, :] - pal[None, None]) ** 2).sum(-1)
        out.append((pal[d.argmin(-1)], a))
    return out


def clean(c, a, rim=True):
    """Drop stray matte specks, keep the biggest blob(s), then give the silhouette a dark rim."""
    from scipy import ndimage
    lab, n = ndimage.label(a)
    if n > 1:
        sizes = ndimage.sum(a, lab, range(1, n + 1))
        a = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= max(12, sizes.max() * 0.04)])
    if not rim:
        return c, a
    edge = a & ~ndimage.binary_erosion(a)
    lum = c @ np.array([0.3, 0.55, 0.15])
    c = c.copy()
    c[edge & (lum > 70)] = c[edge & (lum > 70)] * 0.45      # bright edge pixels -> shaded rim
    c[edge & (lum <= 70)] = np.minimum(c[edge & (lum <= 70)], OL)
    return c, a


def head_meta(a, top_y):
    ys, xs = np.nonzero(a)
    ty = ys.min()
    tx = int(xs[ys == ty].mean())
    row = lambda y: np.nonzero(a[min(y, a.shape[0] - 1)])[0]
    hs = round(GAME_H / 4.2)                     # head size in game px
    my = ty + round(hs * 0.78)
    r = row(my)
    mx = int(r.max()) - 1 if len(r) else tx
    ey = ty + round(hs * 0.5)
    r = row(ey)
    ex = int((r.min() + r.max()) / 2) - 1 if len(r) else tx
    return [mx, my, tx, ty, ex, ey]


def build(hero):
    sheet = Image.open(UPLOADS + SHEETS[hero]).convert('RGB')
    k = STAND[hero] / GAME_H
    raw = {name: [clean(*cut(hero, sheet, p, b, k * ZOOM[hero].get(p, 1)), rim=False) for p, b in fr] for name, fr in F[hero].items()}
    names = list(raw)
    flat = quantise([f for n in names for f in raw[n]], 40)
    i = 0
    for n in names:
        raw[n] = [clean(*flat[i + j]) for j in range(len(raw[n]))]
        i += len(raw[n])
    return raw


def place(frames, air=False, stand_h=GAME_H):
    """Common canvas for an animation: x anchor = centre of head+torso, y anchor = feet."""
    info = []
    for c, a in frames:
        ys, xs = np.nonzero(a)
        top, bot = ys.min(), ys.max()
        band = a[top:top + int((bot - top) * 0.45) + 1]
        bx = np.nonzero(band)[1]
        ax = int(round(bx.mean()))
        ay = top + stand_h if air else bot + 1
        info.append((ax, ay))
    L = max(ax for ax, _ in info) + 2
    R = max(c.shape[1] - ax for (c, _), (ax, _) in zip(frames, info)) + 2
    T = max(ay for _, ay in info) + 1
    B = max(max(c.shape[0] - ay for (c, _), (_, ay) in zip(frames, info)), 0) + 2
    W, H = L + R, T + B
    out = []
    for (c, a), (ax, ay) in zip(frames, info):
        img = np.zeros((H, W, 4), np.uint8)
        ox, oy = L - ax, T - ay
        h, w = a.shape
        img[oy:oy + h, ox:ox + w, :3][a] = np.uint8(c[a])
        img[oy:oy + h, ox:ox + w, 3][a] = 255
        out.append((img, ox, oy))
    return out, (L, T)


def overlay(img, pts, col):
    for x, y in pts:
        if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
            img[y, x] = (*col, 255)


def main(prev=None):
    manifest = {}
    dest = OUT if prev is None else prev
    for hero in SHEETS:
        raw = build(hero)
        stand = int(np.mean([np.ptp(np.nonzero(a)[0]) + 1 for _, a in raw['idle']]))
        anims = {}
        for name, frames in raw.items():
            if name == 'phone':
                continue
            anims[name] = place(frames, name in AIR, stand)
        # action poses reuse the sheet's own extra frames
        hand = HAND[hero]
        anims['chill'] = anims['smoke']
        anims['vape'] = anims['smoke']
        if 'drink' not in anims:
            anims['drink'] = anims['smoke']
        idle0 = place([raw['idle'][0]], False, stand)
        anims['talk'] = (idle0[0] * 2, idle0[1])
        for name, (frames, (axx, ayy)) in anims.items():
            imgs = []
            metas = []
            for j, (img, ox, oy) in enumerate(frames):
                img = img.copy()
                a = img[..., 3] > 0
                m = head_meta(a, 0) + [-1, -1, 0]
                if name in ('smoke', 'vape', 'drink', 'chill'):
                    hx, hy = hand[name if name in hand else 'smoke']
                    m[6], m[7] = hx, hy
                    if name == 'drink':
                        m[8] = 0.9
                if hero == 'arsen' and name in ('smoke', 'chill', 'vape'):   # paint the can out of his hand
                    for y in range(13, 18):
                        for x in range(21, 25):
                            if img[y, x, 3] and img[y, x, :3].astype(int).sum() > 150:
                                img[y, x, :3] = (22, 18, 20)
                if name in ('smoke', 'chill'):          # the cigarette between the fingers
                    x, y = m[6], m[7]
                    overlay(img, [(x + 1, y - 1), (x + 2, y - 1), (x + 3, y - 1)], (240, 236, 228))
                    overlay(img, [(x + 4, y - 1)], (255, 120, 40))
                if name == 'vape':                      # the IQOS stick
                    x, y = m[6], m[7]
                    overlay(img, [(x + 1, y - 1), (x + 2, y - 1), (x + 3, y - 1), (x + 4, y - 1)], (226, 210, 180))
                    overlay(img, [(x + 4, y - 1)], (180, 140, 100))
                if name == 'talk' and j == 1:            # mouth open: SHAMPOO!
                    mx, my = m[0], m[1]
                    overlay(img, [(mx - 1, my), (mx - 2, my), (mx - 1, my + 1), (mx - 2, my + 1)], (60, 16, 20))
                imgs.append(img)
                metas.append(m)
            strip = np.concatenate(imgs, axis=1)
            key = f'hero_{hero}_{name}'
            Image.fromarray(strip, 'RGBA').save(os.path.join(dest, key + '.png'))
            h, w = imgs[0].shape[:2]
            manifest[key] = {'file': key + '.png', 'w': w, 'h': h, 'frames': len(imgs), 'fps': FPS[name],
                             'anchor': [int(axx), int(ayy)], 'meta': [[float(v) if isinstance(v, float) else int(v) for v in m] for m in metas]}
    if prev is None:
        json.dump(manifest, open(os.path.join(OUT, 'heroes.json'), 'w'), separators=(',', ':'))
    return manifest


# hand (holding the cigarette / can) in the finished frame's coords, set by eye from the previews
HAND = {'azat': {'smoke': (26, 17)}, 'arsen': {'smoke': (25, 15), 'drink': (29, 21)}}

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
