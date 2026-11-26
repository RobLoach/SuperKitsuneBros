from paths import NES
import numpy as np
import newtiles
from PIL import Image
from gen import ENEMY, Level, from_image, night, copy_cells, underground, water, flag, deco, fill_hidden, TILE
import sprites

W = 224
grid, unknown, img = from_image('3-1', 240, W)
print('unknown', unknown)
found = [(n.replace('_flip', ''), x, y, w, h, s) for n, x, y, w, h, s in sprites.find(img, sprites.templates('3-1', sprites.B31))]

L = Level('level-2-1-game.json', W)
night(L)
L.prop('customIndicator', '3-1')
EMPTY = (0, 0, 0, 0)
for (x, y), v in grid.items():
    L.set(x, y, v)
water(L)

# ? blocks and the items shown over blocks
q = img[9 * 16:10 * 16, 16 * 16:17 * 16]
qcells = [(x, y) for x in range(W) for y in range(15) if (img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == q).all()]
items = {((x + 8) // 16, (y + 8) // 16): n for n, x, y, w, h, s in found if n in ('mushroom', 'star', 'oneup')}
ITEM = {'mushroom': 113, 'star': 100}
for c, n in items.items():
    L.set(*c, (0, ITEM[n], 0, 0))
for x, y in qcells:
    if (x, y) not in items:
        L.set(x, y, EMPTY)
        L.add(139, x * 16, (y + 1) * 16, 16, 32, **{'spawn-type': 'coin'})

L.add(60, 82 * 16, 6 * 16, 16, 40)  # hidden 1-up
L.set(126, 12, EMPTY)  # springboard, replaced with a lift below
L.set(131, 5, (0, 208, 0, 0))  # vine block
L.set(152, 5, (0, 208, 0, 0))  # brick under a Koopa
flag(L, 199)
deco(L, '3-1', 240)
fill_hidden(L, img, found)

for x in range(W):
    for y in (15, 16):
        L.set(x, y, L.get(x, 14))

L.add(90, 32, 208, 48, 48, actor='Mario')
for n, x, y, w, h, s in found:
    bottom = round((y + h) / 16) * 16
    if n in ENEMY:
        g, ow, oh, props = ENEMY[n]
        L.add(g, x + 8 - ow // 2, bottom, ow, oh)  # centred on the NES sprite
    elif n == 'piranha':
        L.add(132, (x // 16) * 16, bottom, 32, 32)

L.add(131, 38 * 16, 9 * 16, 32, 16, disableInventory=True, zoneTo='level-3-1-underground')
L.add(153, 67 * 16, 11 * 16, 32, 16)
top = L.add(91, 126.5 * 16, 2.5 * 16, 16, 16)
bottom = L.add(91, 126.5 * 16, 13 * 16, 16, 16, path=top)
L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': bottom}]
L.add(136, 126 * 16, 13 * 16, 32, 16, path=top)
L.add(30, 206 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-3-2-begin')

# coin heaven sits above the level, NES rows -11 to -1
UP = 11
L.grow_top(UP)
heaven = img0 = np.array(Image.open(f'{NES}/3-1.png').convert('RGB'))[0:240, :W * 16]
cloud = heaven[13 * 16:14 * 16, 127 * 16:128 * 16]
for x in range(W):
    for y in range(15 - UP, 15):
        c = heaven[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        if (c == cloud).all():
            L.set(x, y - 15 + UP, (TILE(6, 22), 5901, 0, 0))
        elif 60 <= (c == (252, 152, 56)).all(2).sum() <= 90:
            L.set(x, y - 15 + UP, (0, 0, 66, 0))
row = lambda r: r + UP  # NES row of the main level to map row
# the vine grows from its block up through coin heaven: press up on it to climb into the clouds
for r in range(-6, 5):
    c = heaven[(r + 15) * 16:(r + 16) * 16, 131 * 16:132 * 16] if r < 0 else img[r * 16:(r + 1) * 16, 131 * 16:132 * 16]
    L.set(131, row(r), (newtiles.gid(c, (0, 0, 0)), 0, 0, 0))
L.add(30, 131 * 16, row(5) * 16, 16, 32, visible=False, zoneTo='level-3-1-game', zoneX=132.5, zoneY=row(-3))
# the cloud lift
a = L.add(91, 143.5 * 16, row(-4) * 16, 16, 16)
b = L.add(91, 158.5 * 16, row(-4) * 16, 16, 16, path=a)
L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]
L.add(136, 143 * 16, row(-4) * 16, 32, 16, path=a)
# falling off the end of coin heaven drops back into the level at column 163, like the NES
for x in range(210, 215):
    L.add(30, x * 16, row(0) * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-3-1-game', zoneX=163.5, zoneY=row(11))
L.save('level-3-1-game.json')

# underground bonus room, NES columns 52 to 68 at map columns 6 to 22
underground('level-3-1-underground.json', 'level-2-1-underground.json', [
    '######...............PP#######',
    '######...............PP#######',
    '#######..............PP#######',
    '#######......oo......PP#######',
    '#######.....oooo.....PP#######',
    '#######..##M.##.###..PP#######',
    '#######..##.o##o.##..PP#######',
    '#######..#.o#..#o.#..PP#######',
    '#######..#o#....#o#..PP#######',
    '#######...#......#...LL#######',
    '#######..................#####',
    '#######..................#####',
    '#######..................#####',
    '==============================',
    '==============================',
    '==============================',
    '==============================',
], {'customIndicator': '3-1'}, (8, 1), (21, 10, 'level-3-1-game', 67.5, 9 + UP))
