from paths import NES
import json
import numpy as np
from PIL import Image
from gen import GREY_PIPES, cannons, Level, overworld, extend_down, flag, from_image, fresh_tiles, ROOT, ENEMY, TILE
import sprites

W = 224
L = overworld('5-2', 240, W, legend=('5-2', 'B52'), tileset=None, qref=('5-2', 240, 78, 9), fresh=True, recolor=GREY_PIPES)
img = np.array(Image.open(f'{NES}/5-2.png').convert('RGB'))[240:480, :W * 16]
head = np.array(Image.open(f'{NES}/5-1.png').convert('RGB'))[11 * 16:12 * 16, 111 * 16:112 * 16]
print('cannons', cannons(L, img, head))
E = (0, 0, 0, 0)
for x in (81, 84):  # a ? block under a Koopa and a hidden coin block
    L.set(x, 9, E)
    L.add(139, x * 16, 10 * 16, 16, 32, **{'spawn-type': 'coin'})
L.set(85, 5, (0, 208, 0, 0))  # vine block
for y in (11, 12):  # springboard, a lift instead like 2-1 and 3-1
    L.set(25, y, E)
extend_down(L)


def link(a, b):
    o = next(o for o in L.objects if o['id'] == a)
    o['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]


def lift(x, top, bottom, start=None):
    a = L.add(91, (x + 0.5) * 16, top * 16, 16, 16)
    b = L.add(91, (x + 0.5) * 16, bottom * 16, 16, 16)
    link(a, b)
    link(b, a)
    L.add(136, x * 16, (start or bottom) * 16, 32, 16, path=a)


lift(25, 2.5, 13)
lift(85, 2, 5)  # the vine, then a higher lift to the right up to coin heaven, like 3-1
L.add(131, 55 * 16, 10 * 16, 32, 16, disableInventory=True, zoneTo='level-5-2-underwater')
L.add(153, 115 * 16, 11 * 16, 32, 16)
L.add(30, 206 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-5-3-begin')

# coin heaven sits above the level, NES rows -11 to -1
UP = 11
L.grow_top(UP)
row = lambda r: r + UP
heaven = np.array(Image.open(f'{NES}/5-2.png').convert('RGB'))[0:240, :W * 16]
cloud = np.array(Image.open(f'{NES}/3-1.png').convert('RGB'))[13 * 16:14 * 16, 127 * 16:128 * 16]
lit = cloud.any(2)
for x in range(W):
    for y in range(15 - UP, 15):
        c = heaven[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        if (c[lit] == cloud[lit]).all():
            L.set(x, y - 15 + UP, (TILE(6, 22), 5901, 0, 0))
        elif 60 <= (c == (252, 152, 56)).all(2).sum() <= 90:
            L.set(x, y - 15 + UP, (0, 0, 66, 0))
for x in (87, 88):  # shaft for the second lift
    L.set(x, row(-2), E)
lift(87, row(-2), row(1))
a = L.add(91, 97.5 * 16, row(-4) * 16, 16, 16)  # the cloud lift
b = L.add(91, 112.5 * 16, row(-4) * 16, 16, 16)
link(a, b)
link(b, a)
L.add(136, 97 * 16, row(-4) * 16, 32, 16, path=a)
for x in range(W):  # the nesmaps arrow between coin heaven and the level
    v = L.get(x, row(0))
    if v[0] >= TILE(0, 23):
        L.set(x, row(0), E)
for x in range(144, 149):  # falling off the end of coin heaven drops back into the level at column 131
    L.add(30, x * 16, row(0) * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-5-2-game', zoneX=130.5, zoneY=row(11))
L.save('level-5-2-game.json')

# underwater, NES columns 54 to 119 of the bottom band
X0, WW = 54, 66
grid, unknown, wimg = from_image('5-2', 480, WW, x0=X0, db='water', night=False)
print('water unknown', unknown)
U = Level('level-2-2-underwater.json', WW)
U.prop('customIndicator', '5-2')
for (x, y), v in grid.items():
    U.set(x, y, v)
water = next(l for l in U.m['layers'] if l['name'] == 'Water Background')
src = next(l for l in json.load(open(f'{ROOT}/level-2-2-underwater.json'))['layers'] if l['name'] == 'Water Background')
water['data'] = [src['data'][(i // WW) * src['width']] for i in range(WW * 17)]
found = [(n.replace('_flip', '').rstrip('2'), x, y, w, h, s) for n, x, y, w, h, s in sprites.find(wimg, sprites.templates('5-2', sprites.B52))]
fresh_tiles(U, wimg, found, unknown, (32, 56, 236))
for x in range(WW):  # nesmaps arrows and the black border are not part of the level
    for y in range(3):
        if U.get(x, y)[0] >= TILE(0, 23):
            U.set(x, y, E)
for y in range(15):
    U.set(WW - 1, y, U.get(WW - 2, y))
for xs, y in ((range(22, 26), 6), (range(28, 32), 10)):  # lifts
    for x in xs:
        U.set(x, y, E)
    a = U.add(91, (xs[0] + 1.5) * 16, (y - 1) * 16, 16, 16)
    b = U.add(91, (xs[0] + 1.5) * 16, (y + 3) * 16, 16, 16)
    for o, t in ((U.objects[-2], b), (U.objects[-1], a)):
        o['properties'] = [{'name': 'path', 'type': 'object', 'value': t}]
    U.add(92, xs[0] * 16, (y + 1) * 16, 64, 16, path=a)
extend_down(U)
U.add(90, 2 * 16, 6 * 16, 48, 48, actor='Mario')
for n, x, y, w, h, s in found:
    if n in ENEMY:
        g, ow, oh, props = ENEMY[n]
        U.add(g, x + w // 2 - ow // 2, round((y + h) / 16) * 16, ow, oh, **props)
for g, extra in ((153, {}), (30, {'alwaysActive': True, 'hidePrompt': True, 'visible': False})):  # out through the side pipe, like 2-2
    U.add(g, 62 * 16, 9 * 16, 32 if g == 153 else 16, 16 if g == 153 else 32, zoneTo='level-5-2-game', zoneX=115.5, zoneY=9 + UP, **extra)
U.save('level-5-2-underwater.json')
