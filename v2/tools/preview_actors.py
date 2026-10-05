#!/usr/bin/env python3
"""Contact sheet of every strip in assets/actors.json + assets/objects.json,
3x scale, labelled.  Writes tools/preview_actors.png."""
import json
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')
SCALE = 3
MAXW = 1500

entries = []
for grp in ('actors', 'objects'):
    with open(os.path.join(ASSETS, grp + '.json')) as f:
        for k, v in json.load(f).items():
            entries.append((grp, k, v))

tiles = []
for grp, k, v in entries:
    im = Image.open(os.path.join(ASSETS, v['file'])).convert('RGBA')
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    label = '%s  %dx%d x%d @%dfps' % (k, v['w'], v['h'], v['frames'], v['fps'])
    w = max(im.width, len(label) * 6 + 4)
    tiles.append((label, im, w, im.height + 14, v))

# shelf packing
rows, cur, cw = [], [], 0
for t in tiles:
    if cur and cw + t[2] + 12 > MAXW:
        rows.append(cur)
        cur, cw = [], 0
    cur.append(t)
    cw += t[2] + 12
rows.append(cur)
H = sum(max(t[3] for t in r) + 12 for r in rows) + 12
sheet = Image.new('RGBA', (MAXW + 12, H), (88, 130, 170, 255))
d = ImageDraw.Draw(sheet)
y = 12
for r in rows:
    x = 12
    rh = max(t[3] for t in r)
    for label, im, w, h, v in r:
        d.text((x, y), label, fill=(255, 255, 255, 255))
        top = y + 12
        bg = Image.new('RGBA', im.size, (132, 182, 220, 255))
        sheet.paste(bg, (x, top))
        sheet.alpha_composite(im, (x, top))
        fw = v['w'] * SCALE
        for i in range(1, v['frames']):
            d.line([x + i * fw, top, x + i * fw, top + im.height - 1], fill=(255, 0, 255, 255))
        ax, ay = v['anchor']
        d.rectangle([x + ax * SCALE, top + ay * SCALE, x + ax * SCALE + 2, top + ay * SCALE + 2],
                    outline=(255, 40, 40, 255))
        x += w + 12
    y += rh + 12
sheet.save(os.path.join(HERE, 'preview_actors.png'))
print('wrote', os.path.join(HERE, 'preview_actors.png'), sheet.size)
