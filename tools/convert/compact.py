"""drop copied tiles (tileset rows 23 and up) that no map uses, merge near-identical ones, and pack the rest"""
import glob, json, os
import numpy as np
from PIL import Image
from paths import ROOT, HERE
from textedit import set_cells
import newtiles

FIRST = 23 * 32
SAME = 6  # tiles differing in this many pixels or fewer are merged


def main():
    maps = {}
    for f in sorted(glob.glob(f'{ROOT}/level-*.json')):
        m = json.load(open(f))
        fg = [t['firstgid'] for t in m['tilesets'] if t.get('image', '').startswith('tileset')]
        if fg:
            maps[f] = (m, fg[0])
    used = {}
    for f, (m, fg) in maps.items():
        for l in m['layers']:
            if l['type'] == 'tilelayer':
                for g in l['data']:
                    i = (g & 0x0FFFFFFF) - fg
                    if FIRST <= i < 1024:
                        used[i] = used.get(i, 0) + 1
    sheets = {n: np.array(Image.open(f'{ROOT}/{n}').convert('RGBA')) for n in ('tileset.png', 'tileset-night.png', 'tileset-night-white.png')}
    tile = lambda i: sheets['tileset.png'][i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16]
    # the most used tile of each group of near-identical ones stays
    rep = {}
    for i in sorted(used, key=lambda i: -used[i]):
        rep[i] = next((r for r in rep.values() if r == rep.get(r) and (tile(i) != tile(r)).any(2).sum() <= SAME), i)
    keep = sorted(set(rep.values()))
    new = {i: FIRST + keep.index(rep[i]) for i in used}
    for n, a in sheets.items():
        old = a.copy()
        a[FIRST // 32 * 16:] = 0
        for i in keep:
            j = new[i]
            a[j // 32 * 16:j // 32 * 16 + 16, j % 32 * 16:j % 32 * 16 + 16] = old[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16]
        Image.fromarray(a).save(f'{ROOT}/{n}', optimize=True)
    reg = newtiles._load()
    out = {}
    for key, (col, row) in reg.items():
        i = row * 32 + col
        if i in new:
            out[key] = [new[i] % 32, new[i] // 32]
    json.dump(out, open(newtiles.REG, 'w'))
    for f, (m, fg) in maps.items():
        for l in m['layers']:
            if l['type'] != 'tilelayer':
                continue
            cells = {}
            for k, g in enumerate(l['data']):
                i = (g & 0x0FFFFFFF) - fg
                if FIRST <= i < 1024 and new[i] != i:
                    cells[k] = (g & ~0x0FFFFFFF) + fg + new[i]
            if cells:
                set_cells(f, l['name'], cells)
    print(len(used), 'used tiles,', len(keep), 'after merging,', 9 * 32 - len(keep), 'free slots')


if __name__ == '__main__':
    main()
