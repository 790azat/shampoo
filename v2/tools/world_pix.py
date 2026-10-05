"""Tiny pixel-art drawing helpers for SHAMPOO v2 world art.

Every Layer wraps horizontally: all x coordinates are taken modulo the layer
width, so anything drawn across the right edge continues on the left edge and
the PNG tiles seamlessly. Alpha is always 0 or 255.
"""
import numpy as np
from PIL import Image, ImageDraw

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade(c, f):
    """f<1 darker, f>1 lighter (towards white)."""
    if f <= 1:
        return tuple(int(round(v * f)) for v in c)
    return mix(c, (255, 255, 255), f - 1)


class Layer:
    def __init__(self, w, h, wrap=True):
        self.w, self.h, self.wrap = w, h, wrap
        self.a = np.zeros((h, w, 4), np.uint8)

    # ---- low level -------------------------------------------------------
    def _xs(self, x0, x1):
        xs = np.arange(int(x0), int(x1))
        if self.wrap:
            return xs % self.w
        return xs[(xs >= 0) & (xs < self.w)]

    def px(self, x, y, c):
        x, y = int(x), int(y)
        if not (0 <= y < self.h):
            return
        if self.wrap:
            x %= self.w
        elif not (0 <= x < self.w):
            return
        self.a[y, x, :3] = c[:3]
        self.a[y, x, 3] = 255

    def get(self, x, y):
        x, y = int(x) % self.w, int(y)
        if not (0 <= y < self.h):
            return None
        if self.a[y, x, 3] == 0:
            return None
        return tuple(int(v) for v in self.a[y, x, :3])

    def rect(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        y0, y1 = max(0, int(y)), min(self.h, int(y + h))
        if y0 >= y1:
            return
        xs = self._xs(x, x + w)
        if len(xs) == 0:
            return
        self.a[y0:y1, xs, :3] = c[:3]
        self.a[y0:y1, xs, 3] = 255

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def clear(self, x, y, w, h):
        y0, y1 = max(0, int(y)), min(self.h, int(y + h))
        xs = self._xs(x, x + w)
        self.a[y0:y1, xs, 3] = 0

    # ---- masks -----------------------------------------------------------
    def mask(self, fn):
        """fn(draw, ox) draws in '1' mode with x offset ox; result folded."""
        W = self.w
        if self.wrap:
            m = Image.new('1', (W * 3, self.h), 0)
            fn(ImageDraw.Draw(m), W)
            arr = np.array(m)
            return arr[:, :W] | arr[:, W:2 * W] | arr[:, 2 * W:]
        m = Image.new('1', (W, self.h), 0)
        fn(ImageDraw.Draw(m), 0)
        return np.array(m)

    def fill(self, m, c):
        self.a[m, :3] = c[:3]
        self.a[m, 3] = 255

    def poly(self, pts, c):
        m = self.mask(lambda d, ox: d.polygon([(x + ox, y) for x, y in pts], fill=1, outline=1))
        self.fill(m, c)
        return m

    def ellipse(self, x0, y0, x1, y1, c):
        m = self.mask(lambda d, ox: d.ellipse([x0 + ox, y0, x1 + ox, y1], fill=1, outline=1))
        self.fill(m, c)
        return m

    def line(self, pts, c, width=1):
        m = self.mask(lambda d, ox: d.line([(x + ox, y) for x, y in pts], fill=1, width=width))
        self.fill(m, c)
        return m

    def dither_rect(self, x, y, w, h, c1, c2, level):
        """level 0..16: fraction of c2 pixels (ordered Bayer)."""
        for yy in range(int(y), int(y + h)):
            if not 0 <= yy < self.h:
                continue
            for xx in range(int(x), int(x + w)):
                if BAYER4[yy % 4][xx % 4] < level:
                    self.px(xx, yy, c2)
                else:
                    self.px(xx, yy, c1)

    def dither_mask(self, m, c, level, ox=0, oy=0):
        H, W = m.shape
        yy, xx = np.mgrid[0:H, 0:W]
        sel = m & (BAYER4[(yy + oy) % 4, (xx + ox) % 4] < level)
        self.fill(sel, c)

    def solid(self):
        return self.a[:, :, 3] > 0

    def save(self, path):
        a = self.a.copy()
        a[a[:, :, 3] == 0] = 0
        Image.fromarray(a, 'RGBA').save(path)

    def blit(self, other, x, y):
        """Paste another (non-wrapping) layer; transparent pixels skipped."""
        for yy in range(other.h):
            ty = y + yy
            if not 0 <= ty < self.h:
                continue
            row = other.a[yy]
            on = np.nonzero(row[:, 3])[0]
            if len(on) == 0:
                continue
            xs = on + x
            if self.wrap:
                xs %= self.w
            else:
                k = (xs >= 0) & (xs < self.w)
                xs, on = xs[k], on[k]
            self.a[ty, xs] = row[on]


def edges(m):
    """Return (top, left, bottom, right) boundary masks of a boolean mask (wrapping in x)."""
    up = np.zeros_like(m)
    up[1:] = m[:-1]
    dn = np.zeros_like(m)
    dn[:-1] = m[1:]
    lf = np.roll(m, 1, axis=1)
    rt = np.roll(m, -1, axis=1)
    return m & ~up, m & ~lf, m & ~dn, m & ~rt


def periodic_noise(W, rng, octaves=((2, 1.0), (5, 0.5), (11, 0.25), (23, 0.12))):
    """Smooth 1D noise periodic over W samples. Returns array len W in ~[-1,1]."""
    x = np.arange(W) / W * 2 * np.pi
    out = np.zeros(W)
    tot = 0
    for f, a in octaves:
        ph = rng.uniform(0, 2 * np.pi)
        out += a * np.sin(f * x + ph)
        tot += a
    return out / tot


def save_preview(arr_or_layer, path, scale=3, bg=None):
    a = arr_or_layer.a if isinstance(arr_or_layer, Layer) else arr_or_layer
    im = Image.fromarray(a, 'RGBA')
    if bg is not None:
        base = Image.new('RGBA', im.size, bg + (255,))
        base.alpha_composite(im)
        im = base
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(path)
