# SHAMPOO v2 — art & asset spec

Game: side-scrolling pixel platformer through Yerevan. Heroes Azat (white hoodie, black cargo, white sneakers, quiff, beard) and Arsen (black bucket hat, black overshirt over printed tee, black cargo). Humorous tone, Broforce-like chunky readable pixel art, sunny daytime Yerevan.

## Canvas and scale
- Internal resolution 480x270, upscaled by an integer factor with nearest-neighbour. Everything is drawn 1:1 in this pixel grid; never scale sprites at runtime.
- Tile size 16x16. Visible area = 30 x ~17 tiles. Ground level is usually row 14 of 17.
- Heroes are ~56 px tall. Use this to size everything (a dog ~ knee/hip height of a hero, a granny ~ 0.75 of a hero, a car ~ 2.2 heroes long).

## Pixel style rules
- Hard pixels only: no anti-aliasing, no semi-transparent pixels (alpha 0 or 255), no smooth gradients (use 2-3 colour bands or ordered dithering).
- Light comes from the top-left: highlight on top/left edges, shade on bottom/right.
- Sprites (characters, enemies, items, props, cars, FX): 1 px outline in #1a1024 around the silhouette; inner lines use a darker shade of the local colour, not black.
- Background parallax layers: no outline; far layers are desaturated and bluish, near layers get more contrast.
- Each sprite uses a small palette (8-16 colours). Prefer warm, saturated colours for the city (Yerevan pink/orange tuff stone), clear blue sky.
- Sprites face RIGHT. The game mirrors them for left.

## Files and formats (all under /mnt/project-files/game/shampoo2/assets/)
- One PNG per animation strip: frames laid out left to right, all frames the same size, transparent background.
- Name: `<thing>_<anim>.png`, e.g. `dog_run.png`, `granny_throw.png`, `item_boom.png`.
- Every PNG is listed in `assets/<group>.json` (group = `actors`, `objects`, `world_<district>` …) as:
  `"dog_run": { "file": "dog_run.png", "w": 34, "h": 24, "frames": 6, "fps": 12, "anchor": [17, 24] }`
  anchor = the point placed on the entity position: for anything standing on the ground, x centre and y = bottom row (feet).
- Generator scripts go in `/mnt/project-files/game/shampoo2/tools/` (Python 3 + Pillow + numpy), so art can be regenerated and tweaked. Draw from ASCII pixel maps or careful primitive code; check every sprite by rendering an enlarged preview (8x) and looking at it before calling it done.

## Districts (one level each, in this order)
1. `square`  — Republic Square: pink/orange tuff buildings with arcades, the clock tower of the Government House, singing fountains.
2. `opera`   — Opera & Ballet Theatre (round classical building, columns), Swan Lake, café terraces, lots of trees.
3. `cascade` — The Cascade: giant white limestone stairway with terraces, modern sculptures (Botero cat), fountains.
4. `cathedral` — St. Gregory the Illuminator Cathedral: modern stone church with cones/domes, park.
5. `victory` — Victory Park: Mother Armenia statue on a pedestal, old amusement-park rides, Ferris wheel.
6. `tower`   — Yerevan TV Tower (red/white lattice tower), hillside, soviet apartment blocks.
Ararat (big snowy Masis + smaller sharp Sis to its left) is visible in the sky of every district.
