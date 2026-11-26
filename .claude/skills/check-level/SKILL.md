---
name: check-level
description: Regenerate, render and verify a converted Super Mario Bros. level against the NES map - side-by-side renders, a text map of solid tiles to trace routes and find leaks, lint, tileset compaction and the full rebuild. Use when fixing or reviewing any World 1 to 8 level, after changing a tools/convert generator, or when asked whether a level matches the original or can be completed.
---

# Check a level

Generators live in `tools/convert/` (see its README). Set up `tools/convert` as its README says: a `.venv` with numpy, scipy and pillow, and the NES images in `nesmaps/` from `download.py`. Run the scripts from `tools/convert` with `.venv/bin/python`; below, `python` means that. If `/tmp` has a stray `inspect.py` or similar, run Python from a clean directory.

## 1. Regenerate just the level

```sh
cd tools/convert && .venv/bin/python gen74.py   # world 7 level 4
```

World 1 and 2 fixes are in `world12.py` and `fixflags.py`. A level copied from another (7-3 from 2-3) inherits its bugs: fix the source.

## 2. Look at it next to the original

```sh
python render.py ../../level-7-4-game.json /tmp/g.png night   # night for castles and night levels
```

Crop the same columns from `nesmaps/W-L.png` (240px tall per band; extra bands are underwater or bonus areas) and the render (272px), stack them with a column ruler every 5 tiles, and read the image. Look for:

- blocks or tiles where the NES has a sprite (fish, enemies, nesmaps arrows and markers);
- missing lifts, hidden blocks, vines, objects one tile off;
- text glyphs that are wrong (compaction merges);
- enemies hovering or inside walls.

The Mario Wiki page for the level (`https://www.mariowiki.com/World_7-4_(Super_Mario_Bros.)`, Layout section) says which pipes, paths and hidden blocks matter.

## 3. Trace the routes

```sh
python ascii.py level-7-4-game.json 150-175 200-230
```

`#` solid, `D` door, `X` door buried in a wall, `v`/`^` pipe in/out. For every choice point, follow each path: the right one must continue, each wrong one must end at a door with a wall behind it and no way to jump over the door or climb out to the right path. Check every arrival spot (`zoneX`/`zoneY`) lets the player reach every choice, and that no jump is bigger than the NES one it replaces (roughly 4 tiles up); anything bigger needs playing to confirm.

## 4. Lint

```sh
npm run lint   # from the repo root
```

Broken links, arrival spots in walls, blank tiles, duplicate ids, and the `level.json` to `endLevel` chain.

## 5. Full rebuild, compact, lint again

```sh
python -u run.py > /tmp/run.log 2>&1   # about 25 minutes; run it in the background
python compact.py
npm run lint
git status --short                     # only the maps you meant to change, plus tilesets/newtiles.json
```

Render a few of the changed maps once more before committing. Say in the report what was only checked by rendering and lint, and what still needs playing in the game.
