# Map converter

Builds the World 3 to 8 maps from the full-size [nesmaps.com](https://nesmaps.com/maps/SuperMarioBrothers/SuperMarioBrothers.html) images, tile for tile.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python download.py   # the nesmaps images, into nesmaps/
.venv/bin/python run.py        # rebuilds every World 3 to 8 map in the repository root
```

Run `npm t` first so `deps/Content` has the game's tilesets, then `npm run lint` afterwards.

## How it works

- `db.py` learns which tiles were used for each 16x16 cell of the NES image in maps that were built 1:1 from it (2-1, 2-3, 2-4 and 1-3 for overworlds and castles, 1-2 for underground, 2-2 for underwater).
- `match.py` looks a cell up in those, also matching cells that only differ in colour (night palettes).
- `sprites.py` finds enemies, items and lifts by matching the sprites from each map's legend.
- `newtiles.py` copies cells the earlier maps never used (snowy trees, mushrooms, grey pipes...) into the free rows of `tileset.png` and both night tilesets. `newtiles.json` remembers where each one went, so keep it with the tilesets.
- `addtiles.py` adds the hand-picked tiles in tileset rows 20 to 22: water, the NES flags, trees, fences and the coin heaven cloud.
- `gen.py` has the shared helpers, and `genWL.py` builds world W level L, with the level's own fixes: Kitsune stand-ins, links between maps, lifts, maze doors and so on.
- `render.py map.json out.png [night]` and `zoom.py` draw maps and NES images for checking the results.
