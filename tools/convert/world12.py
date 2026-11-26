"""trees, fences and bushes for the hand-made 1-1 and 2-1, copied from the nesmaps images into empty cells, and 2-3's clouds"""
import json
import numpy as np
from PIL import Image
from paths import NES, ROOT
from gen import Level, LAYERS, fill_hidden
import newtiles
import sprites
from textedit import set_cells

SKY = (92, 148, 252)
MAPS = [('1-1', 0, 'level-1-1-game.json', 'B11'), ('2-1', 240, 'level-2-1-game.json', 'B21')]


def main():
    ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))[:20 * 16].reshape(-1, 4)  # the original NES colours
    palette = {tuple(p[:3]) for p in ts[ts[:, 3] == 255]} | {SKY}
    for lv, band, f, legend in MAPS:
        m = json.load(open(f'{ROOT}/{f}'))
        W = m['width']
        L = Level(f, W)
        for l in m['layers']:
            if l['type'] == 'tilelayer':
                L.layers[l['name']][:] = l['data']
        before = list(L.layers['Background No Parallax'])
        img = np.array(Image.open(f'{NES}/{lv}.png').convert('RGB'))[band:band + 240, :W * 16]
        found = list(sprites.find(img, sprites.templates(lv, getattr(sprites, legend))))
        # the map's own enemies and items too, wherever they sit
        found += [('obj', int(o['x']), int(o['y'] - o['height']), int(o['width']), int(o['height']), 1)
                  for l in m['layers'] if l['type'] == 'objectgroup' for o in l['objects'] if o.get('gid')]
        boxes = [(x - 2, y - 2, w + 4, h + 4) for n, x, y, w, h, s in found]
        for y in range(5, 13):  # trees, fences and bushes stand on the ground, nesmaps arrows and the 2-1 vine are higher
            for x in range(W):
                c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
                if L.get(x, y) != (0, 0, 0, 0) or (c == SKY).all() or not {tuple(p) for p in c.reshape(-1, 3)} <= palette:  # faded hidden blocks
                    continue
                if any(bx < x * 16 + 16 and x * 16 < bx + bw and by < y * 16 + 16 and y * 16 < by + bh for bx, by, bw, bh in boxes):
                    continue
                L.set(x, y, (newtiles.gid(c, SKY), 0, 0, 0))
        fill_hidden(L, img, found, rows=range(9, 13))
        after = L.layers['Background No Parallax']
        cells = {i: g for i, (a, g) in enumerate(zip(before, after)) if a != g}
        set_cells(f'{ROOT}/{f}', 'Background No Parallax', cells)
        print(f, len(cells), 'scenery tiles')


CLOUDS = set(range(5019, 5023)) | set(range(5051, 5055)) | set(range(5080, 5083)) | set(range(5112, 5115))


def clouds(lv, band, f):
    """put the clouds where the image has them (2-3's were a tile off)"""
    from match import classify
    from db import cell
    m = json.load(open(f'{ROOT}/{f}'))
    W = m['width']
    bg = next(l for l in m['layers'] if l['name'] == 'Background No Parallax')['data']
    im = Image.open(f'{NES}/{lv}.png').convert('RGB').crop((0, band, W * 16, band + 240))
    a = np.array(im)
    cells = {}
    for y in range(10):
        for x in range(W):
            i = y * W + x
            v, k = classify(cell(im, x, y), 'over', False)
            want = v[0] if k == 'e' and v[0] in CLOUDS else 0
            fish = (a[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == (216, 40, 0)).all(2).any()  # a flying Cheep-cheep, which 2-3 drew as bits of cloud
            if fish:
                want = 0
            if (want or bg[i] in CLOUDS or fish and bg[i] in (4814, 4815, 4846, 4847)) and bg[i] != want:
                cells[i] = want
    set_cells(f'{ROOT}/{f}', 'Background No Parallax', cells)
    print(f, len(cells), 'cloud tiles')


if __name__ == '__main__':
    main()
    clouds('2-3', 0, 'level-2-3-game.json')
