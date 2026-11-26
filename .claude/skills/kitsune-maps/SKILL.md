---
name: kitsune-maps
description: Reference for editing this mod's Tiled maps for Kitsune Tails - object ids and what they do, the properties that matter, how pipes, doors, lifts and level ends are wired, and the tileset layout. Use before adding or moving objects, links between maps, pipes, doors, lifts or text in any level-*.json, or when a warp, door or arrival spot misbehaves.
---

# Kitsune Tails maps

Each level is a Tiled JSON map (`level-W-L-*.json`), 16px tiles, usually 17 rows (the NES has 15; rows 15 and 16 repeat row 14). The modding guide is `deps/Kitsune Tails Map Editing Guide.pdf` and the game's object list is `deps/Content/objects.json` (run `npm t` to get `deps/`).

## Layers

- `Background No Parallax`: what you see. Mario tiles are gids from `tileset.png`, firstgid 4813 (5325 in the maps copied from the underground templates).
- `Blocks`: collision. Any non-zero gid is solid; 5901 is the plain invisible solid block, under Mario tiles drawn in the background layer. Kitsune's own blocks in this layer are drawn and solid.
- `Coins`: gid 66 is a coin.
- `Foreground`: drawn over the player (pipes).
- Underwater maps also have `Water Background`.
- One object layer. Tiled object `y` is the object's **bottom** edge.

## Objects (gid: Kitsune object, what this mod uses it for)

| gid | object | use |
| --- | --- | --- |
| 90 | yuzu, `actor` | player start |
| 30 | door | links between maps; see below |
| 131 | wellwarp | pipe you go down into |
| 153 | wellwarp-up | pipe you come out of |
| 96 | tori, `endLevel` | ends the run; lint needs a route to one |
| 91 | pathnode, `path` | points lifts and flyers follow; each points at the next |
| 136 / 137 / 92 | moving-platform 2x1 / 3x1 / 4x1, `path` | lifts |
| 188 | flying-beetle-path | firebars: one circling a ring of 8 path nodes |
| 139 | bang (custom), `spawn-type` | ? block (`spawn-type: coin`), hidden blocks |
| 60 / 113 / 100 | bang earth / fire / invincibility | 1-up / mushroom and flower / star |
| 36, 24, 73 | beetle, pango, crab | Goomba, Koopa, Buzzy Beetle |
| 38 | flying-beetle, `flyDistance`, `flyVertical` | Paratroopa, Podoboo |
| 132 | rokurokubi | Piranha Plant, at `y = pipe top row * 16` |
| 156, 48 | kiteninja, porcupine (`respawn`) | Lakitu, Spiny |
| 43, 42 | hornet-nest, hornet | Bullet Bill cannon, Bullet Bill and Bowser's fire |
| 79 | archer | Hammer Bro |
| 103, 77 | pufferfish, carp | Blooper, Cheep-cheep |
| 196 | spearman (captain) | Bowser |

`tools/convert/gen.py` has `ENEMY` with the sizes; centre an enemy on the NES sprite (`x + w/2 - width/2`), not by its left edge.

## Wiring

- **Pipes:** the 131/153 object sits *inside* the pipe's top tile: `y = (top row + 1) * 16`, `x` = the pipe's left column * 16, 32x16. One tile higher and you can't go down it.
- **Links:** `zoneTo` is the map name without `.json`. `zoneX`/`zoneY` are in tiles: `zoneX` is usually a column + 0.5, `zoneY` is the **top** row of the 2-tile-tall player, so standing on a floor at row 13 is `zoneY: 11`. The arrival tile must not be solid (`npm run lint` checks).
- **Doors (30), 16x32:**
  - `alwaysActive: true` goes through on touch: hidden exits, loops, maze doors. Add `visible: false` to hide it.
  - Without it the player presses up: vines, beanstalks, visible doors.
  - A door can zone to another spot in its own map (mazes, coin heaven exits).
  - A wrong-path door must have a wall right behind it and a ceiling or wall above, or the player jumps over it. Check with `tools/convert/ascii.py`.
- **End of a castle:** doors all along the floor of the end room to the next `level-W-1-begin`. 8-4 goes to `level-world-select`, which holds the game's only `endLevel`.
- **Lifts:** two path nodes pointing at each other plus a platform with `path` set to the first:
  ```python
  a = L.add(91, (x + 0.5) * 16, top * 16, 16, 16)
  b = L.add(91, (x + 0.5) * 16, bottom * 16, 16, 16, path=a)
  L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]
  L.add(136, x * 16, bottom * 16, 32, 16, path=a)
  ```
- **Map properties:** `music` (`music-*.ogg` without the extension), `customIndicator` (the "W-L" shown), `background` (`bg-bluesky` for day maps).

## Tileset (`tileset.png`, 32 tiles wide)

- Rows 0 to 19: the hand-made World 1 and 2 tiles. Row 18 is the font A to Z, row 19 is 0 to 9 and punctuation: `TILE(col, row) = 4813 + row * 32 + col`.
- Rows 20 to 22: hand-picked extras (`tools/convert/addtiles.py`): water, flags, trees, fences.
- Rows 23 to 31: tiles copied from the NES images by `newtiles.py`, remembered by a hash of their pixels in `newtiles.json`. Keep `tileset.png`, `tileset-night.png`, `tileset-night-white.png` and `newtiles.json` in step.

## Pitfalls seen in this repo

- Enemies or NES markers in front of a cell get classified as tiles: Cheep-cheeps became solid blocks in 2-3/7-3, nesmaps loop markers became floor tiles in 8-4. Compare renders with the NES image.
- `compact.py` must only merge tiles with the same shape; merging by pixel count turned O into 8 and N into W.
- Hand-made maps (Worlds 1 and 2) are edited cell by cell with `tools/convert/textedit.set_cells` to keep their formatting; the rest are regenerated, so fix the generator (`tools/convert/genWL.py`), not the JSON.
