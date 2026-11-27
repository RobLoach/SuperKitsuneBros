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
- `gen.py`'s `tiles()` reads a map's tile layers with the castle's `Bridge` layer folded back into the background and blocks, and `Level()` drops `Bridge` from its template, so generators copying a castle still work.
- Last steps, run after the generators: `bowsers.py`, then every `after_*.py` in name order. Each edits the finished maps in place, keeping their formatting:
  - `bowsers.py` puts a different enemy on each castle bridge as Bowser.
  - `after_bridges.py` moves each Bowser bridge into its own `Bridge` block layer with a Layer Script `movement`, dropped by a `trigger: layerscript` rectangle over the axe platform. `moveAnchored: false` lets Bowser fall into the lava.
  - `after_checkpoints.py` adds the game's `checkpoint` (gid 105) at SMB's halfway points, from `HalfwayPageNybbles` in the SMB disassembly. Castles and World 8 have none, as on the NES.
  - `after_liftwait.py` makes lifts wait for the player (`pathWait`): the Flimsy Lifts in 3-3, 6-3 and 7-4 sink, then fall out of the level; the coin heaven cloud lifts and springboard lifts wait until stepped on. The speeds are the constants at its top.
  - `after_kasha.py` makes the Lakitus in 4-1, 6-1 and 8-2 kashas (gid 123), one per level.
- `fixflags.py` and `world12.py` give the hand-made World 1 and 2 maps (and the copies of them) the NES flag and the trees, fences and bushes, editing only those tiles with `textedit.py`.
- `compact.py` drops copied tiles no map uses, merges near-identical ones and packs the rest; run it now and then, it isn't part of `run.py`.
- `render.py map.json out.png [night]` and `zoom.py` draw maps and NES images for checking the results.
- `ascii.py map.json 150-175 ...` prints the solid tiles, doors and pipes as text, to trace routes through mazes.

## Adding a last step

Add an `after_<name>.py` that runs under `if __name__ == '__main__'`; `run.py` picks it up automatically, in name order after the generators. It must edit the finished maps in place, keeping their formatting (`textedit.py` helps), and be idempotent: running it twice changes nothing. Objects can have no gid (trigger rectangles), so use `o.get('gid')`.
