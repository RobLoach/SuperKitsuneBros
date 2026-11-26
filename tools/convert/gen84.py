from paths import NES
import json
import numpy as np
from PIL import Image
from scipy import ndimage
from gen import redraw_water, Level, from_image, extend_down, fresh_tiles, copy_cells, night, ROOT, ENEMY, TILE, LAYERS
import sprites
import newtiles

W = 320
grid, unknown, img = from_image('8-4', 0, W)
found = [(n.replace('_flip', ''), x, y, w, h, s) for n, x, y, w, h, s in sprites.find(img, sprites.templates('8-4', sprites.B84))]
L = Level('level-2-4-game.json', W)
L.prop('customIndicator', '8-4')
night(L)  # grey pipes
E = (0, 0, 0, 0)
for (x, y), v in grid.items():
    L.set(x, y, v)
fresh_tiles(L, img, found, unknown, (0, 0, 0))
for x in range(304, W):  # the ending text and the princess are drawn from the image, Mario is left out
    for y in range(3, 13):
        c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        L.set(x, y, E if not c.any() or x in (311, 312) and y >= 11 else (newtiles.gid(c, (0, 0, 0)), 0, 0, 0))
for x in range(286, 301):  # Bowser's hammers and fire are sprites, not tiles
    for y in range(3, 10):
        if L.get(x, y)[0] >= TILE(0, 23):
            L.set(x, y, E)
for x in range(W):  # nesmaps marks the loop points under the floor
    if L.get(x, 14)[0] >= TILE(0, 23):
        L.set(x, 14, L.get(31, 14))
extend_down(L)
copy_cells(L, 'level-2-4-game.json', range(134, 142), range(2, 17), dx=160)
L.set(150, 9, E)  # the hidden coin block you stand on to reach the floating pipe
L.add(139, 150 * 16, 10 * 16, 16, 32, **{'spawn-type': 'coin'})  # the end of the Bowser bridge matches 2-4

L.add(90, 0, 7 * 16, 48, 48, actor='Mario')
for n, x, y, w, h, s in found:
    bottom = round((y + h) / 16) * 16
    if n == 'podoboo':
        L.add(38, x + w // 2 - 24, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)
    elif n == 'piranha':
        L.add(132, (x // 16) * 16, bottom, 32, 32)
    elif n in ENEMY:
        g, ow, oh, props = ENEMY[n]
        L.add(g, x + w // 2 - ow // 2, bottom, ow, oh, **props)
src = [o for l in json.load(open(f'{ROOT}/level-2-4-game.json'))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
for o in src:
    if o['gid'] == 196:  # Bowser
        L.add(196, o['x'] + 160 * 16, o['y'], o['width'], o['height'], **{p['name']: p['value'] for p in o.get('properties', [])})
L.add(42, 289 * 16, 10 * 16, 48, 32, respawn=True)  # Bowser's fire
for x in range(314, W):  # past the princess, on to the world select
    L.add(30, x * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-world-select')
# the lift over the first lava pit, up to the top of the walls either side and back down
a = L.add(91, 70.5 * 16, 10 * 16, 16, 16)
b = L.add(91, 70.5 * 16, 13 * 16, 16, 16, path=a)
L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]
L.add(136, 70 * 16, 13 * 16, 32, 16, path=a)

# pipes: the right ones carry you on, the others go back to pipe 1
SELF = 'level-8-4-game'
L.add(153, 19 * 16, (11 + 1) * 16, 32, 16)  # pipe 1
L.add(153, 259 * 16, (11 + 1) * 16, 32, 16)  # pipe 2
for x, top in ((51, 11), (132, 11), (212, 7), (266, 11)):
    L.add(131, x * 16, (top + 1) * 16, 32, 16, zoneTo=SELF, zoneX=19.5, zoneY=9)
L.add(131, 81 * 16, (8 + 1) * 16, 32, 16, zoneTo=SELF, zoneX=115.5, zoneY=9)
L.add(131, 152 * 16, (6 + 1) * 16, 32, 16, zoneTo=SELF, zoneX=195.5, zoneY=9)
L.add(131, 228 * 16, (8 + 1) * 16, 32, 16, zoneTo='level-8-4-underwater')
# walking on past the right pipe in the last room loops back, like the NES (the loops at 96 and 160 were removed in a18cd53)
for x, zx, zy in ((255, 195.5, 9),):
    for y in (5, 7, 9, 11, 13):
        L.add(30, x * 16, y * 16, 16, 32, alwaysActive=True, visible=False, zoneTo=SELF, zoneX=zx, zoneY=zy)
L.save('level-8-4-game.json')

# underwater, NES columns 225 to 297 of the bottom band, out to pipe 2
X0, WW = 225, 73
grid, unknown, wimg = from_image('8-4', 240, WW, x0=X0, db='water', night=False)
U = Level('level-2-2-underwater.json', WW)
U.prop('customIndicator', '8-4')
U.prop('music', 'music-underwater')
for (x, y), v in grid.items():
    U.set(x, y, v)
water = next(l for l in U.m['layers'] if l['name'] == 'Water Background')
srcw = next(l for l in json.load(open(f'{ROOT}/level-2-2-underwater.json'))['layers'] if l['name'] == 'Water Background')
water['data'] = [srcw['data'][(i // WW) * srcw['width']] for i in range(WW * 17)]
wfound = [(n.replace('_flip', ''), x, y, w, h, s) for n, x, y, w, h, s in sprites.find(wimg, sprites.templates('8-4', sprites.B84))]
# firebars under the water: flames circling the middle of each bar
m = np.zeros(wimg.shape[:2], bool)
for c in ((216, 40, 0), (252, 152, 56)):
    m |= (wimg == c).all(2)
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=3))
bars = []
for sl in ndimage.find_objects(lab):
    ys, xs = sl
    if xs.stop - xs.start > 30:
        bars.append(((xs.start + xs.stop) // 32, (ys.start + ys.stop) // 32))
        for y in range(ys.start // 16, (ys.stop + 15) // 16):
            for x in range(xs.start // 16, (xs.stop + 15) // 16):
                if (wimg[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == (216, 40, 0)).all(2).any():
                    wfound.append(('flame', x * 16, y * 16, 16, 16, 1))
fresh_tiles(U, wimg, wfound, unknown, (32, 56, 236))
for x in range(WW):  # nesmaps labels above the water are not part of the level
    for y in range(3):
        if U.get(x, y)[0] >= TILE(0, 23):
            U.set(x, y, E)
for x in range(WW):  # 8-4's green blocks and the pink entry pipe aren't in the 2-2 database, so they came out as pictures only
    for y in range(2, 15):
        c = wimg[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        if (c == (0, 168, 0)).all(2).sum() >= 60 or (c == (228, 0, 88)).all(2).sum() >= 20:
            U.layers['Blocks'][y * WW + x] = 5901
for y in range(15):  # the last column is a nesmaps arrow
    U.set(WW - 1, y, U.get(WW - 2, y))
extend_down(U)
redraw_water(U.m, wimg, wfound)  # the NES coral and seaweed
for y in range(17):  # the redraw brings back the nesmaps border in the last column
    U.set(WW - 1, y, U.get(WW - 2, y))
U.add(90, 3 * 16, 6 * 16, 48, 48, actor='Mario')
RING = [(1, 3), (2, 2), (2, 0), (1, -1), (-1, -1), (-2, 0), (-2, 2), (-1, 3)]
for px, py in bars:
    ids = [U.add(91, (px + dx) * 16, (py + dy) * 16, 16, 16) for dx, dy in RING]
    for i, oid in enumerate(ids):
        U.objects[-8 + i]['properties'] = [{'name': 'path', 'type': 'object', 'value': ids[(i + 1) % 8]}]
    U.add(188, (px - 1) * 16, (py + 3) * 16, 48, 32, path=ids[0])
for n, x, y, w, h, s in wfound:
    if n == 'blooper':
        U.add(103, x + w // 2 - 24, round((y + h) / 16) * 16, 48, 32)
side = [(i % WW, i // WW) for i, g in enumerate(U.layers['Foreground']) if g == 5206]
print('bars', bars, 'side pipe', side)
sx, sy = side[0]
for x in (sx - 2, sx - 1):  # out through the side pipe to pipe 2: invisible doors in the water just in front of it
    U.add(30, x * 16, (sy + 2) * 16, 16, 32, alwaysActive=True, hidePrompt=True, visible=False, zoneTo=SELF, zoneX=259.5, zoneY=9)
U.save('level-8-4-underwater.json')

# "push button B to select a world": a room with a pipe into each world, and the end of the game past them
W = 48
L = Level('level-2-1-game.json', W)
L.prop('customIndicator', '8-4')
L.prop('music', 'music-princess')  # Saved the Princess
copy_cells(L, 'level-1-1-game.json', range(W), range(13))  # 1-1's hills, bushes and clouds...
for x in range(W):
    for y in range(13):
        if L.get(x, y)[1:] != (0, 0, 0):  # ...but not its blocks and pipes
            L.set(x, y, E)
    for y in range(13, 17):
        L.set(x, y, (0, 206 if y == 13 else 238, 0, 5044))
text = lambda x, y, s: [L.set(x + i, y, (TILE(ord(c) - 65, 18) if c.isalpha() else TILE(int(c), 19), 0, 0, 0)) for i, c in enumerate(s) if c != ' ']
text(10, 4, 'SELECT A WORLD')
for i in range(8):
    x = 7 + 4 * i
    text(x, 8, str(i + 1))
    L.set(x, 10, (0, 5901, 0, 5144))
    L.set(x + 1, 10, (0, 5901, 0, 5145))
    for y in (11, 12):
        L.set(x, y, (0, 5901, 0, 5176))
        L.set(x + 1, y, (0, 5901, 0, 5177))
    L.add(131, x * 16, 11 * 16, 32, 16, zoneTo=f'level-{i + 1}-1-begin')
text(41, 3, 'THE END')  # over the torii
copy_cells(L, 'level-8-4-game.json', [313], (11, 12), dx=45 - 313)  # and the princess under it, inside the torii
L.add(90, 2 * 16, 13 * 16, 48, 48, actor='Mario')
L.add(96, 43 * 16, 13 * 16, 80, 112, endLevel=True, visible=False)  # the end of Super Mario Bros.
L.save('level-world-select.json')
