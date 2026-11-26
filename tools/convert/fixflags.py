"""the NES flag on maps that weren't generated here (Worlds 1 and 2, and the copies of them), editing only the flag tiles"""
import json, re
import numpy as np
from PIL import Image
from paths import ROOT
from gen import TILE, FLAG_CELLS

MAPS = ['level-1-1-game', 'level-1-2-game2', 'level-1-3-game', 'level-2-1-game', 'level-2-2-game2', 'level-2-3-game',
        'level-4-2-game2', 'level-7-2-game2', 'level-7-3-game']
OLD = {4814, 4815, 4846, 4847, 4879} | set(range(TILE(0, 21), TILE(0, 22)))


def main():
    for name in MAPS:
        path = f'{ROOT}/{name}.json'
        s = open(path).read()
        m = json.loads(s)
        W = m['width']
        layers = [l for l in m['layers'] if l['type'] == 'tilelayer']
        k = next(i for i, l in enumerate(layers) if l['name'] == 'Background No Parallax')
        bg = layers[k]['data']
        poles = [i % W for i, g in enumerate(bg) if g in (4879, TILE(22, 21))]
        pole = max(set(poles), key=poles.count)
        new = {}
        for x in (pole - 1, pole):
            for y in range(12):
                if bg[y * W + x] in OLD:
                    new[y * W + x] = 0
        ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
        for i, (dx, dy) in enumerate(FLAG_CELLS + [(1, y) for y in range(6, 12)]):
            col = 16 + min(i, 6)  # the day flag, see addtiles.py
            if ts[21 * 16:22 * 16, col * 16:col * 16 + 16, 3].any():
                new[dy * W + pole - 1 + dx] = TILE(col, 21)
        new = {i: g for i, g in new.items() if g != bg[i] and not (g and bg[i] not in OLD | {0})}
        starts = [m_.end() for m_ in re.finditer(r'"data"\s*:\s*\[', s)]
        a = starts[k]
        b = s.index(']', a)
        nums = list(re.finditer(r'\d+', s[a:b]))
        out = s[:a]
        last = 0
        for i, n in enumerate(nums):
            if i in new:
                out += s[a + last:a + n.start()] + str(new[i])
                last = n.end()
        out += s[a + last:]
        open(path, 'w').write(out)
        print(name, 'pole', pole, len(new), 'tiles')


if __name__ == '__main__':
    main()
