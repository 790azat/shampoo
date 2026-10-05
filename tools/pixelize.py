"""Turns the puppet frames exported by tools/export.html into the game's pixel-art hero sprites.

Usage: python3 pixelize.py frames_hi.json out_dir
Writes out_dir/hero_atlas.js (const HERO_ATLAS = ...) and a preview PNG per hero.
"""
import base64, io, json, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

TARGET = {'azat': 40, 'arsen': 42}          # standing height in game pixels
HEAD_LIFT = {'azat': 1.08, 'arsen': 1.3}   # brighten faces so they survive the downscale (Arsen's portrait is dark)
NCOL = 32
OL = (26, 16, 36)                           # the game's outline colour
W0, H0 = 140, 205                           # puppet frame canvas

def decode(png):
    return Image.open(io.BytesIO(base64.b64decode(png.split(',')[1]))).convert('RGBA')

def prep(f, hero):
    im = Image.new('RGBA', (W0, H0)); im.paste(decode(f['png']), (0, 0))
    a = np.array(im).astype(float)
    x0, x1 = int(f['hx'] - f['hw'] * 0.6), int(f['hx'] + f['hw'] * 0.6)
    y0, y1 = max(0, int(f['hy'])), int(f['hy'] + f['hh'])
    reg = a[y0:y1, x0:x1, :3]
    a[y0:y1, x0:x1, :3] = 255 * (reg / 255) ** (1 / HEAD_LIFT[hero])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')

def head_mask(f, w, h, sx, sy):
    yy, xx = np.mgrid[0:h, 0:w]
    return (xx >= (f['hx'] - f['hw'] * 0.55) * sx) & (xx <= (f['hx'] + f['hw'] * 0.55) * sx) & (yy >= f['hy'] * sy - 1) & (yy <= (f['hy'] + f['hh']) * sy)

def enhance(rgb):
    return ImageEnhance.Contrast(ImageEnhance.Color(rgb).enhance(1.2)).enhance(1.12)

def run(src, out_dir):
    data = json.load(open(src))
    atlas = {}
    for hero, anims in data.items():
        idle = anims['IDLE'][0]
        top = np.argmax(np.array(decode(idle['png']))[..., 3].max(1) > 0)
        s = TARGET[hero] / (idle['h'] - top)
        W1, H1 = round(W0 * s), round(H0 * s); sx, sy = W1 / W0, H1 / H0
        # one palette per hero, from the standing frame at full detail
        # separate palettes for head and body, so skin, beard and eyes keep their own shades next to the dark clothes
        base = np.array(prep(idle, hero)); m = base[..., 3] > 128
        hm = head_mask(idle, base.shape[1], base.shape[0], 1, 1) & m
        mkpal = lambda sel, n: enhance(Image.fromarray(base[sel][:, :3].reshape(-1, 1, 3), 'RGB')).quantize(colors=n, method=Image.Quantize.MEDIANCUT)
        pal, hpal = mkpal(m & ~hm, NCOL), mkpal(hm, 20)
        tiles, meta = [], {}
        for name, frames in anims.items():
            meta[name] = []
            for f in frames:
                im = prep(f, hero).resize((W1, H1), Image.BOX)
                mask = np.array(im)[..., 3] > 120
                rgb = enhance(im.convert('RGB').filter(ImageFilter.UnsharpMask(1, 60, 0)))
                q = np.array(rgb.quantize(palette=pal, dither=Image.Dither.NONE).convert('RGB'))
                qh = np.array(rgb.quantize(palette=hpal, dither=Image.Dither.NONE).convert('RGB'))
                hm1 = head_mask(f, W1, H1, sx, sy)
                q[hm1] = qh[hm1]
                out = np.zeros((H1, W1, 4), np.uint8); out[..., :3] = q; out[..., 3] = mask * 255
                o = f['o'] or {}
                mx, my = round(f['mx'] * sx), round(f['my'] * sy)
                if o.get('mouth'): out[my, mx - 1:mx + 1] = (58, 14, 14, 255)
                if o.get('cig'):
                    out[my, mx:mx + 3] = (244, 244, 244, 255)
                    out[my, mx + 3] = (255, 210, 58, 255) if o['cig'] == 2 else (255, 90, 36, 255)
                arm = o.get('arm') or {}
                hx2 = hy2 = -1
                if f.get('hand'):
                    hx2, hy2 = round(f['hand'][0] * sx), round(f['hand'][1] * sy)
                    ob = arm.get('obj')
                    def put(x, y, c):
                        if 0 <= y < H1 and 0 <= x < W1: out[y, x] = (*c, 255)
                    if ob == 'cig' or ob == 'cigHand':
                        for i in range(1, 4): put(hx2 + i, hy2 - 1, (244, 244, 244))
                        put(hx2 + 4, hy2 - 1, (255, 90, 36))
                    elif ob == 'stick':
                        for i in range(1, 3): put(hx2 + i, hy2 - 1, (240, 226, 190))
                        put(hx2 + 3, hy2 - 1, (196, 154, 116))
                    elif ob == 'lighter':
                        put(hx2, hy2 - 1, (200, 30, 40)); put(hx2, hy2 - 2, (200, 30, 40))
                        if arm.get('flame'):
                            put(hx2, hy2 - 3, (255, 210, 58)); put(hx2, hy2 - 4, (255, 140, 30) if arm['flame'] == 2 else (255, 240, 160))
                            if arm['flame'] == 2: put(hx2 + 1, hy2 - 3, (255, 240, 160))
                full = out[..., 3] > 0
                ol = np.zeros_like(full)
                ol[1:] |= full[:-1]; ol[:-1] |= full[1:]; ol[:, 1:] |= full[:, :-1]; ol[:, :-1] |= full[:, 1:]
                ol &= ~full; out[ol] = (*OL, 255)
                if o.get('grounded', True) is not False:
                    bottom = int(np.nonzero(full.any(1))[0].max()) + 1
                else:
                    bottom = round(f['h'] * sy)
                tiles.append(Image.fromarray(out[:bottom]))
                meta[name].append([round(f['ax'] * sx, 1), bottom, round(f['hx'] * sx, 1), round(f['hy'] * sy, 1), round(f['hw'] * sx, 1),
                                   round(f['hh'] * sy, 1), round(f['mx'] * sx, 1), round(f['my'] * sy, 1), round(f['ex'] * sx, 1), round(f['ey'] * sy, 1), hx2, hy2, arm.get('tip', 0)])
        sheet = Image.new('RGBA', (W1 * len(tiles), max(t.height for t in tiles)))
        for i, t in enumerate(tiles): sheet.paste(t, (i * W1, 0))
        buf = io.BytesIO(); sheet.save(buf, 'PNG', optimize=True)
        atlas[hero] = {'w': W1, 'src': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), 'anims': meta}
        prev = Image.new('RGBA', sheet.size, (138, 180, 232, 255)); prev.alpha_composite(sheet)
        prev.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(f'{out_dir}/preview_{hero}.png')
        print(hero, 'frame', W1, 'x', sheet.height, 'tiles', len(tiles), 'png', len(buf.getvalue()))
    open(f'{out_dir}/hero_atlas.js', 'w').write('const HERO_ATLAS = ' + json.dumps(atlas, separators=(',', ':')) + ';\n')

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
