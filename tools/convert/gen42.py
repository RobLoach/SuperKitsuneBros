from paths import NES
import json, re
import numpy as np
from PIL import Image
from gen import Level, from_image, extend_down, fresh_tiles, underground, ROOT, ENEMY, ITEM
import sprites
import newtiles

# start and exit areas are the same as 1-2
for src, dst, subs in (('level-1-2-game.json', 'level-4-2-game.json', [('level-1-2-underground', 'level-4-2-underground'), ('music-pipe', 'music-pipe')]),
                       ('level-1-2-game2.json', 'level-4-2-game2.json', [('level-1-3-begin', 'level-4-3-begin')])):
    s = open(f'{ROOT}/{src}').read()
    for a, b in subs + [('"1-2"', '"4-2"')]:
        assert s.count(a) == 1, (src, a)
        s = s.replace(a, b)
    open(f'{ROOT}/{dst}', 'w').write(s)

W = 224
grid, unknown, img = from_image('4-2', 240, W, db='ug')
print('unknown', unknown)
found = [(n.replace('_flip', '').rstrip('2'), x, y, w, h, s) for n, x, y, w, h, s in sprites.find(img, sprites.templates('4-2', sprites.B42))]
L = Level('level-1-2-underground.json', W)
L.prop('customIndicator', '4-2')
for (x, y), v in grid.items():
    L.set(x, y, v)
L.save('level-4-2-underground.json')

# --- underground objects ---
L.add(90, 3 * 16, 0, 48, 48, actor='Mario')
E = (0, 0, 0, 0)
q = img[9 * 16:10 * 16, 54 * 16:55 * 16]  # a plain ? block
items = {((x + 8) // 16, (y + 8) // 16): n for n, x, y, w, h, s in found if n in ITEM}
for x in range(W):
    for y in range(15):
        if (x, y) in items:
            L.set(x, y, (0, ITEM[items[x, y]], 0, 0))
        elif (img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == q).all():
            L.set(x, y, E)
            L.add(139, x * 16, (y + 1) * 16, 16, 32, **{'spawn-type': 'coin'})
for x, y in ((64, 7), (63, 8), (65, 8), (66, 9)):  # hidden coin blocks: the steps up to the vine block
    L.set(x, y, E)
    L.add(139, x * 16, (y + 1) * 16, 16, 32, **{'spawn-type': 'coin'})
for i, v in enumerate(L.layers['Blocks']):  # the teal bricks, which 1-2 leaves as plain cave tiles
    if v == 1234 and not L.layers['Foreground'][i] and not L.layers['Background No Parallax'][i]:
        L.layers['Foreground'][i] = 5711
for n, x, y, w, h, s in found:
    bottom = round((y + h) / 16) * 16
    if n in ENEMY:
        g, ow, oh, props = ENEMY[n]
        L.add(g, x + w // 2 - ow // 2, bottom, ow, oh, **props)
    elif n == 'piranha':
        L.add(132, (x // 16) * 16, bottom, 32, 32)
L.set(64, 5, L.get(65, 5))  # vine block
# the exit pipe ends above the floor so you can jump up into it, like 1-2 (the side pipe is skipped)
L.set(189, 7, (0, 4877, 0, 5816))
L.set(190, 7, (0, 4877, 0, 5817))
for x in range(187, 191):
    for y in (8, 9):
        L.set(x, y, E)
extend_down(L)
L.layers['Background No Parallax'][8 * W + 214] = 5325 + 19 * 32 + 5  # "5" over the warp pipe


def link(a, b, **extra):
    """point path node a at b"""
    o = next(o for o in L.objects if o['id'] == a)
    o['properties'] = [{'name': 'path', 'type': 'object', 'value': b}] + [
        {'name': k, 'type': 'float', 'value': v} for k, v in extra.items()]


# the beanstalk: press up on it to climb into the warp zone above
for y in range(5):
    L.set(64, y, (newtiles.gid(img[y * 16:y * 16 + 16, 64 * 16:65 * 16], (0, 0, 0), 5325), 0, 0, 0))
L.add(30, 64 * 16, 5 * 16, 16, 32, visible=False, zoneTo='level-4-2-warp', zoneX=10.5, zoneY=11)

# a lift going up and down, then columns of lifts that loop up or down like 1-2
a = L.add(91, 60 * 16, 5 * 16, 16, 16)
b = L.add(91, 60 * 16, 12 * 16, 16, 16)
link(a, b)
link(b, a)
L.add(137, 59 * 16, 8 * 16, 48, 16, path=a)  # 3 wide, like the NES lifts
for col, ys, down in ((114, (3, 10), True), (123, (5, 12), False), (155, (5, 12), True)):
    hi = L.add(91, (col + 1) * 16, -3 * 16, 16, 16)
    lo = L.add(91, (col + 1) * 16, 21 * 16, 16, 16)
    if down:  # ride down to lo, jump back up to hi
        link(hi, lo, pathSpeed=1)
        link(lo, hi, pathSpeed=9999)
    else:
        link(lo, hi, pathSpeed=1)
        link(hi, lo, pathSpeed=9999)
    for y in ys:
        L.add(137, col * 16, y * 16, 48, 16, path=lo if down else hi)

# pipes
L.add(131, 84 * 16, (10 + 1) * 16, 32, 16, disableInventory=True, zoneTo='level-4-2-underground2')
L.add(153, 189 * 16, 8 * 16, 32, 16, zoneTo='level-4-2-game2', zoneX=3.5, zoneY=10)
L.add(131, 214 * 16, (10 + 1) * 16, 32, 16, zoneTo='level-5-1-begin')  # the warp zone to World 5
L.save('level-4-2-underground.json')

# coin room, NES columns 116 to 132 at map columns 6 to 22
underground('level-4-2-underground2.json', 'level-2-1-underground.json', [
    '#######..............PP#######',
    '#######..............PP#######',
    '#######...#######....PP#######',
    '#######.........#....PP#######',
    '#######.........#....PP#######',
    '#######....ooooo#....PP#######',
    '#######...#ooooo###..PP#######',
    '#######...#######..o.PP#######',
    '#######..............PP#######',
    '#######..............LL#######',
    '#######..................#####',
    '#######..................#####',
    '#######..................#####',
    '==============================',
    '==============================',
    '==============================',
    '==============================',
], {'customIndicator': '4-2', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-4-2-underground', 131.5, 9))

# the warp zone above the vine, NES columns 56 to 124 of the sky, with pipes to the 4-2 exit (Worlds 6 to 8 are out of scope)
X0, WW = 56, 69
grid, unknown, img = from_image('4-2', 0, WW, x0=X0, night=False)
L = Level('level-2-1-game.json', WW)
L.prop('customIndicator', '4-2')
for (x, y), v in grid.items():
    L.set(x, y, v)
fresh_tiles(L, img, [], unknown, (92, 148, 252))
ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
for x in range(WW):
    for y in range(15):
        v = L.get(x, y)
        i = v[0] - 4813
        if i >= 23 * 32 and v[1] == 0:  # new tiles: mushroom caps and the orange pipes are solid
            t = ts[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16, :3]
            red, orange = (t == (216, 40, 0)).all(2).sum(), (t == (252, 152, 56)).all(2).sum()
            if red >= 10 and red + orange >= 60:
                L.set(x, y, (v[0], 5901, 0, 0))
for y in (13, 14):  # no pit under the vine
    L.set(64 - X0, y, L.get(65 - X0, y))
extend_down(L)
L.add(90, (66 - X0) * 16, 13 * 16, 48, 48, actor='Mario')
L.add(131, (110 - X0) * 16, (10 + 1) * 16, 32, 16, zoneTo='level-8-1-begin')  # the 8 pipe
L.add(131, (114 - X0) * 16, (10 + 1) * 16, 32, 16, zoneTo='level-7-1-begin')  # the 7 pipe
L.add(131, (118 - X0) * 16, (10 + 1) * 16, 32, 16, zoneTo='level-6-1-begin')  # the 6 pipe
L.save('level-4-2-warp.json')
