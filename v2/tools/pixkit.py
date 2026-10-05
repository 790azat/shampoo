"""pixkit - tiny pixel-art helper used by draw_actors.py / draw_objects.py.

A sprite is a grid of palette characters ('.' = transparent).  We draw with
primitives / ASCII maps, run rim-light shading (light from top-left), then add
an automatic 1px #1a1024 outline and export hard-edged RGBA PNG strips.
"""
import json
import os
import numpy as np
from PIL import Image, ImageDraw

OUTLINE = '#1a1024'
T = '.'


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Spr:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = np.full((h, w), T, dtype='<U1')

    def copy(self):
        s = Spr(self.w, self.h)
        s.g = self.g.copy()
        return s

    # ---------------------------------------------------------- primitives
    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y, x] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.g[y, x]
        return T

    def rect(self, x0, y0, x1, y1, c):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.px(x, y, c)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            if t == 1:
                self.px(x0, y0, c)
            else:
                self.rect(x0, y0, x0 + t - 1, y0 + t - 1, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts, c, t=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], c, t)

    def polyfill(self, pts, c, only=None):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(int(min(ys)), int(max(ys)) + 1):
            yc = y + 0.5
            xs = []
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= yc < y1) or (y1 <= yc < y0):
                    xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(round(a)), int(round(b))):
                    if only is None or self.get(x, y) in only:
                        self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, only=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if rx <= 0 or ry <= 0:
                    continue
                if ((x - cx) / (rx + 0.35)) ** 2 + ((y - cy) / (ry + 0.35)) ** 2 <= 1.0:
                    if only is None or self.get(x, y) in only:
                        self.px(x, y, c)

    def ring(self, cx, cy, r, c, w=1):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if r - w + 0.5 <= d + 0.0 < r + 0.5:
                    self.px(x, y, c)

    def ascii(self, x0, y0, text, skip=' .'):
        rows = [r for r in text.strip('\n').split('\n')]
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch not in skip:
                    self.px(x0 + i, y0 + j, ch)

    def fill(self, x, y, c):
        old = self.get(x, y)
        if old == c:
            return
        st = [(x, y)]
        while st:
            a, b = st.pop()
            if 0 <= a < self.w and 0 <= b < self.h and self.g[b, a] == old:
                self.g[b, a] = c
                st += [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)]

    def replace(self, a, b):
        self.g[self.g == a] = b

    def blit(self, o, x0, y0):
        for y in range(o.h):
            for x in range(o.w):
                if o.g[y, x] != T:
                    self.px(x0 + x, y0 + y, o.g[y, x])

    def flipx(self):
        s = self.copy()
        s.g = s.g[:, ::-1].copy()
        return s

    def flipy(self):
        s = self.copy()
        s.g = s.g[::-1, :].copy()
        return s

    # ---------------------------------------------------------- shading
    def shade(self, base, hi=None, sh=None, group=None, hi_d=((0, -1), (-1, 0)),
              sh_d=((0, 1), (1, 0)), depth=1):
        """Rim shading: pixels of `base` whose up/left neighbour is outside
        `group` become `hi`, down/right neighbours outside become `sh`."""
        group = set(group or base)
        src = self.g.copy()

        def outside(x, y):
            if not (0 <= x < self.w and 0 <= y < self.h):
                return True
            return src[y, x] not in group

        for y in range(self.h):
            for x in range(self.w):
                if src[y, x] != base:
                    continue
                if sh and any(outside(x + dx * k, y + dy * k) for dx, dy in sh_d for k in range(1, depth + 1)):
                    self.g[y, x] = sh
                elif hi and any(outside(x + dx, y + dy) for dx, dy in hi_d):
                    self.g[y, x] = hi

    def outline(self, c='k', diag=False):
        src = self.g.copy()
        filled = src != T
        out = np.zeros_like(filled)
        nb = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if diag:
            nb += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        H, W = filled.shape
        for dy, dx in nb:
            sh = np.zeros_like(filled)
            ys = slice(max(dy, 0), H + min(dy, 0))
            yd = slice(max(-dy, 0), H + min(-dy, 0))
            xs = slice(max(dx, 0), W + min(dx, 0))
            xd = slice(max(-dx, 0), W + min(-dx, 0))
            sh[yd, xd] = filled[ys, xs]
            out |= sh
        out &= ~filled
        self.g[out] = c
        return self

    # ---------------------------------------------------------- export
    def image(self, pal):
        img = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        for ch in np.unique(self.g):
            if ch == T:
                continue
            if ch not in pal:
                raise KeyError('palette missing %r' % ch)
            r, g, b = hexrgb(pal[ch])
            img[self.g == ch] = (r, g, b, 255)
        return Image.fromarray(img, 'RGBA')


def strip(frames, pal):
    w, h = frames[0].w, frames[0].h
    im = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        assert f.w == w and f.h == h
        im.paste(f.image(pal), (i * w, 0))
    return im


class Book:
    """Collects strips, writes PNGs + manifest, and makes previews."""

    def __init__(self, asset_dir, manifest_name, preview_dir=None):
        self.dir = asset_dir
        self.name = manifest_name
        self.preview_dir = preview_dir
        self.entries = {}
        self.images = {}

    def add(self, key, frames, pal, fps=8, anchor=None, extra=None):
        im = strip(frames, pal)
        w, h = frames[0].w, frames[0].h
        if anchor is None:
            anchor = [w // 2, h - 1]
        fn = key + '.png'
        im.save(os.path.join(self.dir, fn))
        e = {'file': fn, 'w': w, 'h': h, 'frames': len(frames), 'fps': fps,
             'anchor': list(anchor)}
        if extra:
            e.update(extra)
        self.entries[key] = e
        self.images[key] = im
        if self.preview_dir:
            preview(im, os.path.join(self.preview_dir, key + '.png'), 8, len(frames))
        return im

    def save(self):
        with open(os.path.join(self.dir, self.name), 'w') as f:
            json.dump(self.entries, f, indent=1)


def preview(im, path, scale, nframes=1):
    w, h = im.size
    bg = Image.new('RGBA', (w * scale + (nframes - 1) * 4 * 0, h * scale), (120, 170, 210, 255))
    # checker so transparency is visible
    d = ImageDraw.Draw(bg)
    for y in range(0, h):
        for x in range(0, w):
            if (x + y) % 2:
                d.rectangle([x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1],
                            fill=(132, 182, 220, 255))
    big = im.resize((w * scale, h * scale), Image.NEAREST)
    bg.alpha_composite(big)
    fw = w // max(nframes, 1)
    for i in range(1, nframes):
        d.line([i * fw * scale, 0, i * fw * scale, h * scale], fill=(255, 0, 255, 255))
    bg.save(path)
