"""Hero sprites for SHAMPOO v2: puppet frames (exported by hero_export.html) -> pixel-art strips.

Usage: python3 hero_pixelize.py frames_hi.json   (writes ../assets/hero_<name>_<anim>.png and ../assets/heroes.json)
Each frame shares one canvas per hero; the feet sit on the anchor row. meta per frame: mouth, head top, ear, hand, can tip.
"""
import base64, io, json, os, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'assets')
TARGET = {'azat': 56, 'arsen': 58}
HEAD_LIFT = {'azat': 1.08, 'arsen': 1.3}
NCOL = 40
OL = (26, 16, 36)
W0, H0 = 140, 205
FPS = {'IDLE': 3, 'WALK': 10, 'RUN': 14, 'JUMP': 1, 'FALL': 1, 'LAND': 1, 'CROUCH': 1, 'SHOOT': 14, 'DROP': 6, 'HURT': 1, 'DEAD': 1,
       'TALK': 11, 'SMOKE': 4, 'VAPE': 3, 'DRINK': 4, 'CHILL': 3}

def decode(png): return Image.open(io.BytesIO(base64.b64decode(png.split(',')[1]))).convert('RGBA')

def prep(f, hero):
    im = Image.new('RGBA', (W0, H0)); im.paste(decode(f['png']), (0, 0))
    a = np.array(im).astype(float)
    x0, x1 = int(f['hx'] - f['hw'] * 0.6), int(f['hx'] + f['hw'] * 0.6)
    y0, y1 = max(0, int(f['hy'])), int(f['hy'] + f['hh'])
    a[y0:y1, x0:x1, :3] = 255 * (a[y0:y1, x0:x1, :3] / 255) ** (1 / HEAD_LIFT[hero])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

def head_mask(f, w, h, sx, sy):
    yy, xx = np.mgrid[0:h, 0:w]
    return (xx >= (f['hx'] - f['hw'] * 0.55) * sx) & (xx <= (f['hx'] + f['hw'] * 0.55) * sx) & (yy >= f['hy'] * sy - 1) & (yy <= (f['hy'] + f['hh']) * sy)

def enhance(rgb): return ImageEnhance.Contrast(ImageEnhance.Color(rgb).enhance(1.2)).enhance(1.12)

def put(out, x, y, c):
    if 0 <= y < out.shape[0] and 0 <= x < out.shape[1]: out[y, x] = (*c, 255)

def run(src):
    data = json.load(open(src)); manifest = {}
    for hero, anims in data.items():
        idle = anims['IDLE'][0]
        top = np.argmax(np.array(decode(idle['png']))[..., 3].max(1) > 0)
        s = TARGET[hero] / (idle['h'] - top)
        W1, H1 = round(W0 * s), round(H0 * s); sx, sy = W1 / W0, H1 / H0
        base = np.array(prep(idle, hero)); m = base[..., 3] > 128
        hm = head_mask(idle, W0, H0, 1, 1) & m
        mkpal = lambda sel, n: enhance(Image.fromarray(base[sel][:, :3].reshape(-1, 1, 3), 'RGB')).quantize(colors=n, method=Image.Quantize.MEDIANCUT)
        # body palette also sees a raised-arm frame, so the sleeve keeps its own colours
        armf = np.array(prep(anims['SHOOT'][1], hero)); am = (armf[..., 3] > 128) & ~head_mask(anims['SHOOT'][1], W0, H0, 1, 1)
        both = np.concatenate([base[m & ~hm][:, :3], armf[am][:, :3]])
        pal = enhance(Image.fromarray(both.reshape(-1, 1, 3), 'RGB')).quantize(colors=NCOL, method=Image.Quantize.MEDIANCUT)
        hpal = mkpal(hm, 24)
        frames = {}; baseline = None
        for name, fl in anims.items():
            frames[name] = []
            for f in fl:
                im = prep(f, hero).resize((W1, H1), Image.BOX)
                mask = np.array(im)[..., 3] > 120
                rgb = enhance(im.convert('RGB').filter(ImageFilter.UnsharpMask(1, 60, 0)))
                q = np.array(rgb.quantize(palette=pal, dither=Image.Dither.NONE).convert('RGB'))
                qh = np.array(rgb.quantize(palette=hpal, dither=Image.Dither.NONE).convert('RGB'))
                hm1 = head_mask(f, W1, H1, sx, sy); q[hm1] = qh[hm1]
                out = np.zeros((H1, W1, 4), np.uint8); out[..., :3] = q; out[..., 3] = mask * 255
                o = f['o'] or {}; arm = o.get('arm') or {}
                mx, my = round(f['mx'] * sx), round(f['my'] * sy)
                if o.get('mouth'): out[my, mx - 1:mx + 1] = (58, 14, 14, 255)
                if o.get('cig'):
                    for i in range(4): put(out, mx + i, my, (244, 244, 244))
                    put(out, mx + 4, my, (255, 210, 58) if o['cig'] == 2 else (255, 90, 36))
                hx2 = hy2 = -1
                if f.get('hand'):
                    hx2, hy2 = round(f['hand'][0] * sx), round(f['hand'][1] * sy); ob = arm.get('obj')
                    if ob in ('cig', 'cigHand'):
                        for i in range(1, 5): put(out, hx2 + i, hy2 - 1, (244, 244, 244))
                        put(out, hx2 + 5, hy2 - 1, (255, 90, 36))
                    elif ob == 'stick':
                        for i in range(1, 4): put(out, hx2 + i, hy2 - 1, (240, 226, 190))
                        put(out, hx2 + 4, hy2 - 1, (196, 154, 116))
                    elif ob == 'lighter':
                        for d in (1, 2, 3): put(out, hx2, hy2 - d, (200, 30, 40))
                        if arm.get('flame'):
                            put(out, hx2, hy2 - 4, (255, 210, 58)); put(out, hx2, hy2 - 5, (255, 140, 30) if arm['flame'] == 2 else (255, 240, 160))
                            put(out, hx2 + (1 if arm['flame'] == 2 else 0), hy2 - 6, (255, 240, 160))
                full = out[..., 3] > 0
                ol = np.zeros_like(full)
                ol[1:] |= full[:-1]; ol[:-1] |= full[1:]; ol[:, 1:] |= full[:, :-1]; ol[:, :-1] |= full[:, 1:]
                ol &= ~full; out[ol] = (*OL, 255)
                low = int(np.nonzero(full.any(1))[0].max())
                if baseline is None: baseline = low     # first frame is the standing IDLE pose
                dy = baseline - low if o.get('grounded', True) is not False else 0
                if dy: out = np.roll(out, dy, axis=0); out[:dy] = 0 if dy > 0 else out[:dy]
                meta = [mx, my + dy, round(f['hx'] * sx), round(f['hy'] * sy) + dy, round(f['ex'] * sx), round(f['ey'] * sy) + dy,
                        hx2, hy2 + dy if hy2 >= 0 else -1, arm.get('tip', 0)]
                frames[name].append((out, meta))
        # one tight canvas for every frame of this hero
        allm = np.zeros((H1, W1), bool)
        for fl in frames.values():
            for out, _ in fl: allm |= out[..., 3] > 0
        ys, xs = np.nonzero(allm); x0, x1, y0 = int(xs.min()), int(xs.max()) + 1, int(ys.min()); y1 = int(baseline) + 2
        ax = round(idle['ax'] * sx) - x0
        for name, fl in frames.items():
            key = f'hero_{hero}_{name.lower()}'
            strip = Image.new('RGBA', ((x1 - x0) * len(fl), y1 - y0))
            metas = []
            for i, (out, meta) in enumerate(fl):
                strip.paste(Image.fromarray(out[y0:y1, x0:x1]), (i * (x1 - x0), 0))
                metas.append([meta[0] - x0, meta[1] - y0, meta[2] - x0, meta[3] - y0, meta[4] - x0, meta[5] - y0,
                              meta[6] - x0 if meta[6] >= 0 else -1, meta[7] - y0 if meta[7] >= 0 else -1, meta[8]])
            strip.save(os.path.join(OUT, key + '.png'), optimize=True)
            manifest[key] = {'file': key + '.png', 'w': int(x1 - x0), 'h': int(y1 - y0), 'frames': len(fl), 'fps': FPS.get(name, 8),
                             'anchor': [int(ax), int(baseline + 1 - y0)], 'meta': [[float(v) if isinstance(v, float) else int(v) for v in m] for m in metas]}
        print(hero, 'frame', x1 - x0, 'x', y1 - y0, 'anims', len(frames))
    json.dump(manifest, open(os.path.join(OUT, 'heroes.json'), 'w'), separators=(',', ':'))

if __name__ == '__main__':
    run(sys.argv[1])
