"""copy World 3 tiles from the nesmaps images into the free rows of tileset.png, then rebuild the night tilesets"""
from paths import NES, ROOT
import numpy as np
from PIL import Image
FLAG = [(0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4), (1, 5)]  # relative to the cell left of the pole
DECO = [(11, 11), (11, 12), (13, 10), (13, 11), (14, 12), (77, 8)]  # small tree, trunk, tall tree top, tall tree middle, fence, bridge rail
n31 = np.array(Image.open(f'{NES}/3-1.png').convert('RGBA'))[240:480]
n33 = np.array(Image.open(f'{NES}/3-3.png').convert('RGBA'))[0:240]
n61 = np.array(Image.open(f'{NES}/6-1.png').convert('RGBA'))[0:240]
n41 = np.array(Image.open(f'{NES}/4-1.png').convert('RGBA'))[0:240]
n43 = np.array(Image.open(f'{NES}/4-3.png').convert('RGBA'))[0:240]

def cell(im, x, y):
    c = im[y * 16:y * 16 + 16, x * 16:x * 16 + 16].copy()
    c[(c[..., :3] == 0).all(2)] = 0  # black sky is transparent
    return c

ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
put = lambda col, row, c: ts.__setitem__((slice(row * 16, row * 16 + 16), slice(col * 16, col * 16 + 16)), c)
for i, (dx, dy) in enumerate(FLAG):
    put(i, 21, cell(n31, 199 + dx, dy))
    put(8 + i, 21, cell(n61, 185 + dx, dy))  # the green flag, from 6-1 (a cloud overlaps 3-3's)
    for col0, im, x0 in ((16, n41, 224), (24, n43, 146)):
        c = im[dy * 16:dy * 16 + 16, (x0 + dx) * 16:(x0 + dx) * 16 + 16].copy()
        c[(c[..., :3] == (92, 148, 252)).all(2)] = 0  # day sky is transparent
        put(col0 + i, 21, c)
for i, (x, y) in enumerate(DECO):
    put(i, 22, cell(n31, x, y))
put(6, 22, cell(np.array(Image.open(f'{NES}/3-1.png').convert('RGBA'))[0:240], 127, 13))  # coin heaven cloud block
Image.fromarray(ts).save(f'{ROOT}/tileset.png', optimize=True)

SKY = {(92, 148, 252, 255): (0, 0, 0, 0)}
PIPES = {(128, 208, 16, 255): (252, 252, 252, 255), (0, 168, 0, 255): (116, 116, 116, 255), (0, 68, 0, 255): (188, 188, 188, 255)}
for name, M in (('tileset-night.png', SKY), ('tileset-night-white.png', {**SKY, **PIPES})):
    im = Image.fromarray(ts.copy()).copy()
    px = im.load()
    for y in range(20 * 16):  # rows 20 and up are already in their final colours
        for x in range(im.width):
            if px[x, y] in M:
                px[x, y] = M[px[x, y]]
    im.save(f'{ROOT}/{name}', optimize=True)
