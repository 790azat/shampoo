"""Recognisable Yerevan landmarks for the mid parallax layers."""
import numpy as np
from world_pix import Layer, BAYER4, mix, shade, edges
from world_city import (tuff, TUFF_COLOURS, GLASS, GLASS_HI, GLASS_MID, window, tex_courses,
                        text, sign)

FLAG = [(217, 0, 18), (0, 51, 160), (242, 168, 0)]  # Armenian tricolour


def flag(L, x, y, w=7):
    L.vline(x, y, 12, (90, 86, 96))
    for i, c in enumerate(FLAG):
        L.rect(x + 1, y + 1 + i * 2, w, 2, c)
        L.px(x + w, y + 2 + i * 2, c)


def arch(L, x, y, w, h, fill, rim_hi=None, rim_sh=None):
    """Round-topped opening, top at y."""
    eh = min(w, h)
    r = eh / 2
    m = L.mask(lambda d, ox: (d.ellipse([x + ox, y, x + w - 1 + ox, y + eh - 1], fill=1),
                              d.rectangle([x + ox, y + r, x + w - 1 + ox, y + h - 1], fill=1)))
    L.fill(m, fill)
    if rim_hi is not None:
        t, l, b, rr = edges(m)
        up = np.zeros_like(m)
        up[:-1] = m[1:]
        rim = up & ~m
        lf = np.roll(m, -1, 1) & ~m
        L.fill(rim | lf, rim_hi)
        L.fill(l, shade(fill, 0.8))
    return m


def column(L, x, top, h, pal, w=3):
    L.rect(x, top, w, h, pal['base'])
    L.vline(x, top, h, pal['hi'])
    L.vline(x + w - 1, top, h, pal['sh'])
    L.hline(x - 1, top, w + 2, pal['hi'])
    L.hline(x - 1, top + 1, w + 2, pal['sh'])
    L.hline(x - 1, top + h - 1, w + 2, pal['base'])


# ------------------------------------------------------------ Republic Sq.
def government_house(L, x, ground, rng):
    """Long arcaded tuff building with the famous clock tower (Republic Square)."""
    pal = tuff((230, 174, 128), 0.08)
    pal2 = tuff((216, 150, 116), 0.08)
    W = 250
    h = 60
    top = ground - h
    L.rect(x, top, W, h, pal['base'])
    tex_courses(L, x, top + 4, W, h - 4, pal, rng, every=4, step=9)
    # roof cornice and frieze
    L.hline(x - 2, top - 1, W + 4, pal['hi'])
    L.hline(x - 2, top, W + 4, pal['hi'])
    L.hline(x - 2, top + 1, W + 4, pal['sh'])
    for xx in range(x, x + W, 4):
        L.px(xx, top + 2, pal['dk'])
        L.px(xx + 1, top + 3, pal['sh'])
    L.vline(x, top, h, pal['hi'])
    L.vline(x + W - 1, top, h, pal['sh'])
    # upper storeys: paired windows with carved frames
    gfh = 24
    for f in range(2):
        wy = top + 7 + f * 14
        for i in range(0, W - 12, 12):
            wx = x + 6 + i
            L.rect(wx - 2, wy - 2, 10, 11, pal['sh'])
            L.rect(wx - 1, wy - 1, 8, 9, pal['hi'])
            window(L, wx, wy, 2, 7, pal)
            window(L, wx + 4, wy, 2, 7, pal)
            if f == 0:
                L.hline(wx - 2, wy - 3, 10, pal['dk'])
    # big two-storey arcade at ground floor
    L.hline(x, ground - gfh - 1, W, pal['hi'])
    L.hline(x, ground - gfh, W, pal['sh'])
    for i in range(0, W - 10, 12):
        ax = x + 4 + i
        arch(L, ax, ground - gfh + 2, 9, gfh - 2, pal['dk'], rim_hi=pal['hi'])
        L.rect(ax + 2, ground - 9, 5, 9, GLASS)
        L.px(ax + 2, ground - 9, GLASS_HI)
        L.hline(ax + 1, ground - gfh + 11, 7, pal['sh'])
    # clock tower, a bit left of centre
    tx, tw = x + 70, 30
    ttop = top - 64
    tp = tuff((236, 182, 136), 0.06)
    L.rect(tx, ttop + 24, tw, top - ttop - 24, tp['base'])
    tex_courses(L, tx, ttop + 26, tw, top - ttop - 26, tp, rng, every=4, step=6)
    L.vline(tx, ttop + 24, top - ttop - 24, tp['hi'])
    L.rect(tx + tw - 3, ttop + 24, 3, top - ttop - 24, tp['sh'])
    # tall slit windows on the shaft
    for wx in (tx + 7, tx + 13, tx + 19):
        window(L, wx, top - 34, 3, 26, tp, arched=True)
    # clock stage
    cy = ttop + 30
    L.rect(tx - 1, cy - 8, tw + 2, 18, tp['hi'])
    L.rect(tx, cy - 7, tw, 16, tp['base'])
    L.rect(tx + tw - 3, cy - 7, 3, 16, tp['sh'])
    L.ellipse(tx + 7, cy - 6, tx + 22, cy + 8, tp['dk'])
    L.ellipse(tx + 8, cy - 5, tx + 21, cy + 7, (250, 246, 232))
    L.ellipse(tx + 10, cy - 3, tx + 19, cy + 5, (238, 232, 214))
    for a in range(12):
        ang = a / 12 * 2 * np.pi
        L.px(tx + 14.5 + 5.6 * np.sin(ang), cy + 1 + 5.6 * np.cos(ang), (60, 50, 60))
    L.vline(tx + 14, cy - 3, 5, (40, 34, 44))
    L.hline(tx + 14, cy + 1, 4, (40, 34, 44))
    L.hline(tx - 2, cy + 10, tw + 4, tp['hi'])
    L.hline(tx - 2, cy + 11, tw + 4, tp['sh'])
    # open belvedere with three arches and balustrade
    by = ttop + 6
    L.hline(tx - 2, cy - 9, tw + 4, tp['hi'])
    L.rect(tx + 1, by, tw - 2, 13, tp['base'])
    for k in range(3):
        arch(L, tx + 4 + k * 8, by + 2, 6, 11, (120, 156, 214))
        L.hline(tx + 4 + k * 8, by + 10, 6, tp['sh'])
        for b in range(0, 6, 2):
            L.vline(tx + 4 + k * 8 + b, by + 10, 3, tp['hi'])
    L.vline(tx + 1, by, 13, tp['hi'])
    L.rect(tx + tw - 3, by, 2, 13, tp['sh'])
    # stepped cap and spire with flag
    L.rect(tx - 1, by - 2, tw + 2, 2, tp['hi'])
    L.hline(tx - 1, by - 1, tw + 2, tp['sh'])
    L.rect(tx + 4, by - 5, tw - 8, 3, tp['base'])
    L.hline(tx + 4, by - 5, tw - 8, tp['hi'])
    L.rect(tx + 9, by - 8, tw - 18, 3, tp['base'])
    L.hline(tx + 9, by - 8, tw - 18, tp['hi'])
    flag(L, tx + 15, by - 20)
    # side wings with small towers/pediment
    for wxx in (x + 160, x + 220):
        L.poly([(wxx - 14, top - 1), (wxx, top - 9), (wxx + 14, top - 1)], pal['hi'])
        L.poly([(wxx - 11, top - 2), (wxx, top - 7), (wxx + 11, top - 2)], pal['base'])
    return W


def history_museum(L, x, ground, rng):
    """Pinker arcaded building across the square (History Museum / Marriott style)."""
    pal = tuff((214, 134, 118), 0.08)
    W, h = 150, 68
    top = ground - h
    L.rect(x, top, W, h, pal['base'])
    tex_courses(L, x, top + 4, W, h - 4, pal, rng, every=4, step=8)
    L.hline(x - 2, top, W + 4, pal['hi'])
    L.hline(x - 2, top + 1, W + 4, pal['sh'])
    L.vline(x, top, h, pal['hi'])
    L.vline(x + W - 1, top, h, pal['sh'])
    # colonnade loggia on top floor
    L.rect(x + 6, top + 4, W - 12, 12, pal['dk'])
    for i in range(x + 6, x + W - 8, 7):
        L.rect(i, top + 4, 3, 12, pal['base'])
        L.vline(i, top + 4, 12, pal['hi'])
    L.hline(x + 4, top + 16, W - 8, pal['hi'])
    for f in range(2):
        for i in range(x + 8, x + W - 8, 9):
            window(L, i, top + 22 + f * 12, 4, 7, pal, arched=(f == 0))
    for i in range(x + 5, x + W - 12, 13):
        arch(L, i, ground - 20, 10, 20, pal['dk'], rim_hi=pal['hi'])
        L.rect(i + 2, ground - 8, 6, 8, GLASS)
    L.hline(x, ground - 22, W, pal['sh'])
    return W


# ------------------------------------------------------------------ Opera
def opera_house(L, x, ground, rng):
    """Alexander Tamanyan's Opera: round drum, ring of columns, wide wings."""
    pal = tuff((232, 206, 170), 0.06)
    pal2 = tuff((222, 184, 150), 0.06)
    W = 270
    cx = x + W // 2
    # side wings
    wing_h = 40
    L.rect(x, ground - wing_h, W, wing_h, pal2['base'])
    tex_courses(L, x, ground - wing_h + 4, W, wing_h - 4, pal2, rng, every=4, step=8)
    L.hline(x - 2, ground - wing_h - 1, W + 4, pal2['hi'])
    L.hline(x - 2, ground - wing_h, W + 4, pal2['sh'])
    L.vline(x, ground - wing_h, wing_h, pal2['hi'])
    L.vline(x + W - 1, ground - wing_h, wing_h, pal2['sh'])
    for i in range(x + 6, x + W - 6, 10):
        if abs(i - cx) > 62:
            window(L, i, ground - wing_h + 7, 4, 9, pal2, arched=True)
            window(L, i, ground - 17, 4, 9, pal2)
    # big drum (rotunda): tall arched bays between pilasters, foreshortened
    dw, dh = 112, 50
    dtop = ground - wing_h - dh + 8
    d0 = cx - dw // 2
    L.rect(d0, dtop, dw, dh, pal['base'])
    nb = 15
    for k in range(nb + 1):
        a0 = -np.pi / 2 + k * np.pi / nb
        a1 = -np.pi / 2 + (k + 1) * np.pi / nb
        xa = cx + int(np.sin(a0) * dw / 2)
        xb = cx + int(np.sin(a1) * dw / 2) if k < nb else d0 + dw
        bw = xb - xa
        lit = pal['hi'] if k < 4 else (pal['base'] if k < 10 else pal['sh'])
        L.rect(xa, dtop, max(1, bw), dh, lit)
        if bw >= 4 and k < nb:
            ww = max(2, bw - 3)
            arch(L, xa + 2, dtop + 10, ww, dh - 16, pal['dk'] if k > 8 else shade(pal['dk'], 1.1))
            if ww >= 3:
                L.rect(xa + 3, dtop + 18, ww - 2, dh - 26, GLASS_MID)
                L.px(xa + 3, dtop + 18, GLASS_HI)
            L.hline(xa + 2, dtop + dh - 14, ww, lit)  # transom between storeys
        L.vline(xa, dtop + 6, dh - 6, pal['hi'] if k < 9 else pal['sh'])
    L.rect(d0 + dw - 3, dtop, 3, dh, pal['dk'])
    # entablature, attic ring and flat roof with lantern
    L.rect(d0 - 2, dtop, dw + 4, 7, pal['base'])
    L.hline(d0 - 2, dtop, dw + 4, pal['hi'])
    L.hline(d0 - 2, dtop + 6, dw + 4, pal['sh'])
    for i in range(d0, d0 + dw, 3):
        L.px(i, dtop + 4, pal['joint'])
    L.rect(d0 + dw - 6, dtop, 8, 7, pal['sh'])
    L.rect(d0 + 4, dtop - 6, dw - 8, 6, pal2['base'])
    L.hline(d0 + 4, dtop - 6, dw - 8, pal2['hi'])
    L.rect(d0 + dw - 14, dtop - 6, 10, 6, pal2['sh'])
    L.poly([(d0 + 10, dtop - 6), (cx - 26, dtop - 10), (cx + 26, dtop - 10), (d0 + dw - 10, dtop - 6)], (150, 160, 172))
    L.hline(cx - 26, dtop - 10, 52, (196, 204, 214))
    # semicircular front portico with columns
    pw, ph = 76, 34
    p0 = cx - pw // 2
    L.rect(p0, ground - ph, pw, ph, pal['dk'])
    L.rect(p0 + 2, ground - ph + 8, pw - 4, ph - 8, GLASS)
    for i in range(p0 + 4, p0 + pw - 4, 9):
        L.rect(i + 3, ground - ph + 12, 4, 8, GLASS_MID)
        L.px(i + 3, ground - ph + 12, GLASS_HI)
    for k in range(9):
        t = (k + 0.5) / 9
        ang = (t - 0.5) * np.pi
        px_ = cx + int(np.sin(ang) * (pw / 2 - 3))
        cw = 3 if abs(ang) < 1.1 else 2
        column(L, px_ - 1, ground - ph + 6, ph - 6, pal if t < 0.7 else tuff((206, 180, 150), .06), w=cw)
    L.rect(p0 - 2, ground - ph, pw + 4, 6, pal['base'])
    L.hline(p0 - 2, ground - ph, pw + 4, pal['hi'])
    L.hline(p0 - 2, ground - ph + 5, pw + 4, pal['sh'])
    for i in range(p0 - 2, p0 + pw + 2, 2):  # balustrade
        L.vline(i, ground - ph - 3, 3, pal['hi'] if i < cx + 20 else pal['sh'])
    L.hline(p0 - 2, ground - ph - 4, pw + 4, pal['hi'])
    L.rect(p0 - 2, ground - 3, pw + 4, 3, pal['sh'])  # steps
    L.hline(p0 - 4, ground - 2, pw + 8, pal['hi'])
    return W


def swan_lake(L, x, ground, w):
    """Small pond with swans, drawn at the street level (near layer)."""
    water, wl, wd = (86, 150, 210), (150, 200, 240), (60, 112, 176)
    L.rect(x, ground - 3, w, 3, water)
    L.hline(x, ground - 4, w, (200, 200, 196))
    L.hline(x, ground - 5, w, (226, 224, 218))
    for i in range(x + 2, x + w - 3, 7):
        L.hline(i, ground - 2, 3, wl)
    L.hline(x, ground - 1, w, wd)
    for sx in (x + w // 4, x + w * 2 // 3):
        L.rect(sx, ground - 8, 6, 3, (252, 252, 252))
        L.vline(sx + 5, ground - 12, 4, (252, 252, 252))
        L.px(sx + 6, ground - 12, (250, 140, 30))
        L.px(sx + 4, ground - 11, (252, 252, 252))
        L.hline(sx, ground - 6, 6, (210, 214, 224))


# ---------------------------------------------------------------- Cascade
def cascade(L, x, ground, rng, W=330, H=128):
    """The Cascade: white limestone terraces climbing to the right, with the
    central stair, fountains, flower beds and the obelisk monument on top."""
    pal = tuff((236, 232, 220), 0.05)
    stone_hi, stone, stone_sh, stone_dk = pal['hi'], pal['base'], pal['sh'], pal['dk']
    green = [(70, 130, 70), (96, 160, 80), (140, 194, 96)]
    n = 6
    tw = W // n
    for k in range(n):
        tx = x + k * tw
        th = int(18 + k * (H - 40) / (n - 1))
        top = ground - th
        L.rect(tx, top, W - k * tw, th, stone)
        # terrace front: arched glass gallery (the art centre) and buttress
        L.hline(tx, top, W - k * tw, stone_hi)
        L.hline(tx, top + 1, W - k * tw, stone_hi)
        L.hline(tx, top + 2, W - k * tw, stone_sh)
        # flower beds / greenery on terrace
        for gx in range(tx + 2, tx + tw - 2):
            L.px(gx, top - 1, green[1] if (gx // 3) % 2 else green[0])
            if (gx * 7) % 5 == 0:
                L.px(gx, top - 2, green[2])
        # face of the terrace step: arcade of 3 openings
        fh = min(th - 4, 22)
        face_y = top + 3
        for a in range(3):
            ax = tx + 4 + a * (tw - 8) // 3
            aw = (tw - 8) // 3 - 3
            arch(L, ax, face_y + 3, aw, fh - 5, stone_dk)
            L.rect(ax + 1, face_y + 9, aw - 2, fh - 11, GLASS_MID)
            L.px(ax + 1, face_y + 9, GLASS_HI)
        # vertical stone texture below gallery
        for yy in range(face_y + fh, ground, 4):
            L.hline(tx, yy, tw, pal['joint'])
        L.vline(tx, top, th, stone_hi)
        L.vline(tx + 1, top, th, stone_hi)
        if k > 0:
            L.rect(tx - 2, top + 3, 2, th - 3, stone_sh)  # shadow of the higher step on the lower
    # the great outdoor stair: a stepped band climbing through every terrace
    rise = (H - 30) / (W - 16)
    for i in range(0, W - 16):
        sx = x + 8 + i
        sy = ground - 4 - int(i * rise)
        L.vline(sx, sy, 7, stone_sh)
        L.px(sx, sy + 7, stone_dk)
        if int(i * rise) != int((i + 1) * rise):     # step nose
            L.px(sx, sy, stone_hi)
            L.px(sx, sy + 1, stone_hi)
        else:
            L.px(sx, sy, mix(stone_hi, stone_sh, .5))
    for i in range(0, W - 16, 24):                  # little people-free landings / lamps
        sx = x + 8 + i
        sy = ground - 4 - int(i * rise)
        L.vline(sx, sy - 6, 6, (90, 90, 100))
        L.px(sx, sy - 7, (250, 240, 200))
    # fountain water channels down the centre (blue)
    for k in range(1, n):
        tx = x + k * tw
        th = int(18 + k * (H - 40) / (n - 1))
        L.rect(tx + tw // 2 - 2, ground - th + 3, 4, 4, (110, 176, 230))
        L.px(tx + tw // 2 - 1, ground - th + 3, (220, 240, 255))
        L.vline(tx + tw // 2, ground - th - 4, 4, (180, 220, 250))
        L.px(tx + tw // 2 - 1, ground - th - 3, (200, 230, 252))
        L.px(tx + tw // 2 + 1, ground - th - 2, (200, 230, 252))
    # obelisk monument at the top (50th anniversary of Soviet Armenia)
    ox = x + W - tw // 2
    otop = ground - H - 2 - 34
    base = ground - int(18 + (n - 1) * (H - 40) / (n - 1))
    L.rect(ox - 6, base - 6, 12, 6, stone)
    L.hline(ox - 6, base - 6, 12, stone_hi)
    L.poly([(ox - 4, base - 6), (ox - 2, otop), (ox + 2, otop), (ox + 4, base - 6)], stone)
    L.poly([(ox + 1, base - 6), (ox + 1, otop), (ox + 2, otop), (ox + 4, base - 6)], stone_sh)
    L.vline(ox - 3, otop + 6, base - otop - 12, stone_hi)
    L.poly([(ox - 2, otop), (ox, otop - 5), (ox + 2, otop)], stone_hi)
    return W


def botero_cat(L, x, ground):
    """Fernando Botero's fat bronze cat (Cascade garden) on a plinth."""
    dk, md, hi, hl = (34, 30, 36), (58, 52, 60), (92, 84, 92), (140, 130, 136)
    L.rect(x, ground - 6, 22, 6, (210, 206, 196))
    L.hline(x, ground - 6, 22, (236, 234, 226))
    L.vline(x + 21, ground - 6, 6, (170, 166, 160))
    L.ellipse(x + 2, ground - 22, x + 20, ground - 5, md)
    L.ellipse(x + 10, ground - 31, x + 22, ground - 19, md)  # head
    L.poly([(x + 11, ground - 27), (x + 12, ground - 34), (x + 15, ground - 30)], md)
    L.poly([(x + 17, ground - 30), (x + 20, ground - 34), (x + 21, ground - 27)], md)
    L.line([(x + 2, ground - 12), (x - 3, ground - 18), (x - 2, ground - 24)], md, 2)
    L.ellipse(x + 4, ground - 20, x + 10, ground - 13, hi)
    L.ellipse(x + 11, ground - 30, x + 15, ground - 26, hi)
    L.px(x + 5, ground - 19, hl)
    L.px(x + 12, ground - 29, hl)
    L.ellipse(x + 14, ground - 22, x + 20, ground - 8, dk)
    L.px(x + 14, ground - 26, (230, 200, 90))
    L.px(x + 19, ground - 26, (230, 200, 90))


# ------------------------------------------------------- St Gregory church
def st_gregory(L, x, ground, rng):
    """St. Gregory the Illuminator Cathedral: blocky tuff volumes, central
    drum with conical roof, smaller chapels and a separate bell gate."""
    pal = tuff((228, 176, 118), 0.06)   # yellow-orange tuff
    roof = tuff((196, 140, 100), 0.06)
    W = 250
    cx = x + 150

    def cone_drum(cx, base_y, dw, dh, ch, shaded_win=True):
        d0 = cx - dw // 2
        L.rect(d0, base_y - dh, dw, dh, pal['base'])
        L.vline(d0, base_y - dh, dh, pal['hi'])
        L.rect(d0 + dw - max(2, dw // 5), base_y - dh, max(2, dw // 5), dh, pal['sh'])
        for i in range(d0 + 3, d0 + dw - 3, 5):
            window(L, i, base_y - dh + 4, 2, max(3, dh - 9), pal, arched=True)
        L.hline(d0 - 1, base_y - dh - 1, dw + 2, pal['hi'])
        # cone (umbrella) roof
        L.poly([(d0 - 2, base_y - dh - 1), (cx, base_y - dh - ch), (d0 + dw + 1, base_y - dh - 1)], roof['base'])
        L.poly([(cx, base_y - dh - ch), (d0 + dw + 1, base_y - dh - 1), (cx + 1, base_y - dh - 1)], roof['sh'])
        L.line([(d0 - 2, base_y - dh - 1), (cx, base_y - dh - ch)], roof['hi'])
        for k in range(2, dw // 2, 3):
            L.px(cx - k, base_y - dh - 2, roof['dk'])
        # cross
        cy = base_y - dh - ch
        L.vline(cx, cy - 8, 8, (210, 180, 90))
        L.hline(cx - 2, cy - 6, 5, (210, 180, 90))
        L.px(cx, cy - 8, (250, 230, 150))

    # main body: rectangular hall with blind arcade
    bw, bh = 120, 46
    b0 = cx - bw // 2
    L.rect(b0, ground - bh, bw, bh, pal['base'])
    tex_courses(L, b0, ground - bh + 4, bw, bh - 4, pal, rng, every=5, step=10)
    L.hline(b0 - 1, ground - bh - 1, bw + 2, pal['hi'])
    L.vline(b0, ground - bh, bh, pal['hi'])
    L.rect(b0 + bw - 4, ground - bh, 4, bh, pal['sh'])
    for i in range(b0 + 6, b0 + bw - 8, 12):
        arch(L, i, ground - bh + 6, 8, 26, pal['sh'])
        window(L, i + 3, ground - bh + 11, 2, 10, pal, arched=True)
    # gabled pediments
    L.poly([(b0 - 1, ground - bh - 1), (b0 + 30, ground - bh - 14), (b0 + 61, ground - bh - 1)], roof['base'])
    L.poly([(b0 + 59, ground - bh - 1), (b0 + 90, ground - bh - 14), (b0 + bw, ground - bh - 1)], roof['sh'])
    L.rect(cx - 30, ground - bh - 14, 60, 13, pal['base'])
    L.vline(cx - 30, ground - bh - 14, 13, pal['hi'])
    L.rect(cx + 26, ground - bh - 14, 4, 13, pal['sh'])
    cone_drum(cx, ground - bh - 14, 34, 18, 22)
    # big portal arch with relief
    arch(L, cx - 10, ground - 34, 20, 34, pal['sh'])
    arch(L, cx - 7, ground - 30, 14, 30, (70, 52, 50))
    L.vline(cx, ground - 40, 4, pal['dk'])
    L.hline(cx - 1, ground - 39, 3, pal['dk'])
    # side chapels with small cones
    for sx in (b0 - 22, b0 + bw + 22):
        L.rect(sx - 14, ground - 30, 28, 30, pal['base'])
        L.vline(sx - 14, ground - 30, 30, pal['hi'])
        L.rect(sx + 10, ground - 30, 4, 30, pal['sh'])
        arch(L, sx - 3, ground - 22, 6, 22, (70, 52, 50))
        cone_drum(sx, ground - 30, 16, 10, 12)
    # bell gate/tower on the left: arched open stage and small cone
    gx = x + 30
    gh = 64
    L.rect(gx - 12, ground - gh, 24, gh, pal['base'])
    tex_courses(L, gx - 12, ground - gh + 4, 24, gh - 4, pal, rng, every=5, step=8)
    L.vline(gx - 12, ground - gh, gh, pal['hi'])
    L.rect(gx + 9, ground - gh, 3, gh, pal['sh'])
    arch(L, gx - 6, ground - 26, 12, 26, (70, 52, 50))
    for k in range(2):
        arch(L, gx - 8 + k * 9, ground - gh + 6, 7, 14, (110, 140, 200))
    L.px(gx - 5, ground - gh + 14, (150, 120, 60))
    L.px(gx + 4, ground - gh + 14, (150, 120, 60))
    L.hline(gx - 13, ground - gh - 1, 26, pal['hi'])
    L.poly([(gx - 13, ground - gh - 1), (gx, ground - gh - 16), (gx + 13, ground - gh - 1)], roof['base'])
    L.poly([(gx, ground - gh - 16), (gx + 13, ground - gh - 1), (gx + 1, ground - gh - 1)], roof['sh'])
    L.vline(gx, ground - gh - 23, 7, (210, 180, 90))
    L.hline(gx - 2, ground - gh - 21, 5, (210, 180, 90))
    return W


# --------------------------------------------------------- Mother Armenia
STATUE = [
    # Mother Armenia, ~22 x 40, sword held horizontally across the body.
    # S=shadow side, M=metal, H=highlight
    "..........HM..........",
    ".........HMMS.........",
    ".........HMMS.........",
    "..........MS..........",
    ".........HMMS.........",
    "........HMMMMS........",
    "...HHHHHHMMMMMSSSSSSSSS",
    "...MMMMMMMMMMMMMMMMMMMS",
    "........HMMMMS........",
    "........HMMMMS........",
    "........HMMMMSS.......",
    ".......HMMMMMSS.......",
    ".......HMMMMMMS.......",
    ".......HMMMMMMS.......",
    ".......HMMMMMMSS......",
    "......HMMMMMMMSS......",
    "......HMMMMMMMSS......",
    "......HMMMMMMMMS......",
    "......HMMMMMMMMSS.....",
    ".....HMMMMMMMMMSS.....",
    ".....HMMMMMMMMMSS.....",
    ".....HMMMMMMMMMMS.....",
    ".....HMMMMMMMMMMSS....",
    "....HMMMMMMMMMMMSS....",
    "....HMMMMMMMMMMMSS....",
    "....HMMMMMMMMMMMMS....",
    "...HMMMMMMMMMMMMMSS...",
    "...HMMMMMMMMMMMMMSS...",
    "..HMMMMMMMMMMMMMMMSS..",
    "..MMMMMMMMMMMMMMMMMSS.",
]


def mother_armenia(L, x, ground, rng):
    """Pedestal (stepped grey basalt museum) with the copper statue on top."""
    ped = tuff((150, 140, 150), 0.08)
    ped2 = tuff((176, 164, 168), 0.08)
    W = 64
    cx = x + W // 2
    # steps at base
    for k, (w, h) in enumerate([(64, 6), (52, 6), (44, 4)]):
        y = ground - 6 * k - h - (2 if k == 2 else 0)
        L.rect(cx - w // 2, ground - sum([6, 6, 4][:k + 1]), w, [6, 6, 4][k], ped2['base'])
        L.hline(cx - w // 2, ground - sum([6, 6, 4][:k + 1]), w, ped2['hi'])
        L.vline(cx + w // 2 - 1, ground - sum([6, 6, 4][:k + 1]), [6, 6, 4][k], ped2['sh'])
    base = ground - 16
    # tall pedestal with vertical fins
    pw, ph = 34, 66
    L.rect(cx - pw // 2, base - ph, pw, ph, ped['base'])
    L.vline(cx - pw // 2, base - ph, ph, ped['hi'])
    L.rect(cx + pw // 2 - 5, base - ph, 5, ph, ped['sh'])
    for i in range(cx - pw // 2 + 4, cx + pw // 2 - 6, 5):
        L.vline(i, base - ph + 8, ph - 18, ped['dk'])
        L.vline(i + 1, base - ph + 8, ph - 18, ped['hi'])
    for yy in range(base - ph + 4, base, 6):
        L.hline(cx - pw // 2 + 1, yy, pw - 6, ped['joint'])
    arch(L, cx - 5, base - 14, 10, 14, (60, 54, 64))
    L.rect(cx - pw // 2 - 2, base - ph - 3, pw + 4, 3, ped2['base'])
    L.hline(cx - pw // 2 - 2, base - ph - 3, pw + 4, ped2['hi'])
    L.hline(cx - pw // 2 - 2, base - ph - 1, pw + 4, ped['dk'])
    # statue: slender robed woman holding the long sword horizontally
    M, H, S, D = (98, 114, 110), (150, 166, 156), (68, 78, 82), (50, 56, 64)
    sh_ = 44
    sb = base - ph - 3          # feet level
    st = sb - sh_
    # robe: widens towards the feet, slight sway
    for r in range(12, sh_):
        t = (r - 12) / (sh_ - 12)
        hw = 3 + int(5 * t ** 1.3)
        y = st + r
        L.hline(cx - hw, y, 2 * hw + 1, M)
        L.px(cx - hw, y, H)
        L.rect(cx + hw - 1, y, 2, 1, S)
        if r > 16:
            F = (82, 96, 96)
            L.px(cx - 1 - (r > 30), y, F)   # fold lines
            if r > 22:
                L.px(cx + 2 + (r > 34), y, F)
    # torso/shoulders
    L.rect(cx - 3, st + 6, 7, 7, M)
    L.vline(cx - 3, st + 6, 7, H)
    L.vline(cx + 3, st + 6, 7, S)
    L.hline(cx - 4, st + 6, 9, M)
    L.px(cx - 4, st + 6, H)
    # head + hair
    L.rect(cx - 1, st, 3, 5, M)
    L.px(cx - 1, st + 1, H)
    L.px(cx + 1, st + 1, S)
    L.vline(cx + 2, st + 1, 4, S)
    L.vline(cx, st + 5, 1, M)
    # arms forward to the hilt
    L.rect(cx - 4, st + 9, 3, 3, M)
    L.rect(cx + 2, st + 9, 3, 3, S)
    # sword: long horizontal blade across the body, hilt on her right (viewer left)
    L.hline(cx - 18, st + 11, 32, H)
    L.hline(cx - 18, st + 12, 32, S)
    L.px(cx + 14, st + 11, M)
    L.vline(cx - 6, st + 9, 6, D)        # cross-guard
    L.hline(cx - 9, st + 11, 3, D)       # grip
    L.px(cx - 10, st + 11, M)            # pommel
    # shield leaning at her feet
    L.rect(cx + 7, sb - 8, 4, 8, S)
    L.vline(cx + 7, sb - 8, 8, M)
    L.px(cx + 8, sb - 5, H)
    return W


def ferris_wheel(L, cx, ground, r, rng):
    steel, steel_sh = (220, 226, 236), (160, 168, 186)
    cy = ground - r - 8
    m = L.mask(lambda d, ox: d.ellipse([cx - r + ox, cy - r, cx + r + ox, cy + r], outline=1))
    L.fill(m, steel)
    m2 = L.mask(lambda d, ox: d.ellipse([cx - r + 3 + ox, cy - r + 3, cx + r - 3 + ox, cy + r - 3], outline=1))
    L.fill(m2, steel_sh)
    for k in range(16):
        a = k / 16 * 2 * np.pi
        L.line([(cx, cy), (cx + r * np.cos(a), cy + r * np.sin(a))], steel_sh)
    gond = [(220, 60, 60), (250, 200, 60), (70, 140, 220), (90, 180, 100)]
    for k in range(8):
        a = k / 8 * 2 * np.pi + 0.2
        gx, gy = cx + r * np.cos(a), cy + r * np.sin(a)
        c = gond[k % 4]
        L.rect(gx - 2, gy + 1, 5, 4, c)
        L.hline(gx - 2, gy + 1, 5, shade(c, 1.25))
        L.vline(gx, gy, 1, steel_sh)
    # A-frame legs
    L.line([(cx, cy), (cx - r * 0.55, ground)], (150, 70, 70), 2)
    L.line([(cx, cy), (cx + r * 0.55, ground)], (120, 54, 58), 2)
    L.rect(cx - 1, cy - 1, 3, 3, (90, 90, 100))


def swing_ride(L, cx, ground, rng):
    """Old chain-swing carousel of Victory Park."""
    pole, pole_sh = (230, 210, 120), (190, 160, 90)
    h = 40
    L.rect(cx - 1, ground - h, 3, h, pole)
    L.vline(cx + 1, ground - h, h, pole_sh)
    L.poly([(cx - 16, ground - h + 4), (cx, ground - h - 6), (cx + 16, ground - h + 4)], (210, 60, 70))
    for i in range(cx - 16, cx + 17, 4):
        L.vline(i, ground - h + 2, 3, (248, 240, 230))
    L.hline(cx - 16, ground - h + 4, 33, (160, 40, 50))
    for k, sx in enumerate((-18, -11, -4, 4, 11, 18)):
        L.line([(cx + sx * 0.8, ground - h + 5), (cx + sx * 1.15, ground - h + 22)], (120, 120, 130))
        L.rect(cx + sx * 1.15 - 1, ground - h + 22, 3, 2, [(250, 200, 60), (70, 140, 220), (220, 60, 60)][k % 3])


# --------------------------------------------------------------- TV tower
def tv_tower(L, cx, ground, h, rng):
    """Yerevan TV tower: red/white banded steel lattice, wide splayed legs,
    service platforms, tapering mast."""
    RED, RED_SH, WHT, WHT_SH = (214, 52, 50), (160, 36, 42), (246, 244, 240), (196, 196, 204)
    top = ground - h
    for i in range(h):
        y = ground - i
        t = i / h
        if t < 0.55:
            hw = 3 + 22 * (1 - t / 0.55) ** 1.7
        elif t < 0.86:
            hw = 3 - 1.5 * (t - 0.55) / 0.31
        else:
            hw = 0.5
        band = int(i / (h / 18)) % 2
        c, cs = (RED, RED_SH) if band == 0 else (WHT, WHT_SH)
        hwi = int(round(hw))
        if t < 0.55:
            # lattice: two leg chords with cross bracing
            L.rect(cx - hwi, y, 2, 1, c)
            L.rect(cx + hwi - 1, y, 2, 1, cs)
            L.px(cx, y, cs)
            span = max(1, 2 * hwi - 2)
            k = (i % 10) / 10
            bx1 = cx - hwi + 1 + int(k * span)
            bx2 = cx + hwi - 2 - int(k * span)
            L.px(bx1, y, c)
            L.px(bx2, y, cs)
            if i % 10 == 0:
                L.hline(cx - hwi, y, 2 * hwi + 1, c)
        else:
            L.hline(cx - hwi, y, max(1, 2 * hwi + 1), c)
            L.px(cx + hwi, y, cs)
    # platforms
    for t, w in ((0.55, 14), (0.70, 10), (0.80, 8)):
        y = ground - int(t * h)
        L.rect(cx - w // 2, y - 3, w + 1, 3, (90, 92, 104))
        L.hline(cx - w // 2, y - 3, w + 1, (150, 154, 168))
        L.hline(cx - w // 2 - 1, y, w + 3, (60, 60, 72))
    L.px(cx, top - 1, (255, 60, 60))


def panel_block(L, x, ground, w, floors, rng, colour=(196, 186, 176), haze=0.1):
    """Soviet 9-14 storey panel block with grid windows and glazed balconies."""
    pal = tuff(colour, haze)
    fh = 7
    h = floors * fh + 4
    top = ground - h
    L.rect(x, top, w, h, pal['base'])
    L.vline(x, top, h, pal['hi'])
    L.rect(x + w - 2, top, 2, h, pal['sh'])
    L.hline(x, top, w, pal['hi'])
    for f in range(floors):
        y = top + 3 + f * fh
        L.hline(x + 1, y + fh - 1, w - 3, pal['joint'])
        for wx in range(x + 3, x + w - 5, 6):
            r = rng.random()
            if r < 0.3:
                fr = [(214, 214, 206), (150, 176, 196), (186, 150, 110), (200, 196, 170)][int(rng.integers(4))]
                L.rect(wx - 1, y, 5, 5, fr)
                L.rect(wx, y + 1, 3, 2, GLASS_MID)
                L.hline(wx - 1, y + 5, 5, pal['dk'])
            else:
                L.rect(wx, y + 1, 3, 3, GLASS)
                L.px(wx, y + 1, GLASS_HI)
                if r > 0.9:
                    L.rect(wx + 3, y + 3, 2, 2, (214, 216, 220))
    return top
