from paths import NES
import json
import numpy as np
from PIL import Image
from gen import Level, overworld, extend_down, flag, underground, dumps, ROOT, TILE

W = 240
L = overworld('6-2', 240, W, legend=('6-2', 'B62'), tileset='tileset-night.png', qref=('6-1', 0, 17, 9), fresh=True)
E = (0, 0, 0, 0)
L.set(81, 5, (0, 208, 0, 0))  # vine block
flag(L, 215, green=True)
extend_down(L)


def link(a, b):
    o = next(o for o in L.objects if o['id'] == a)
    o['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]


def lift(x, top, bottom):
    a = L.add(91, (x + 0.5) * 16, top * 16, 16, 16)
    b = L.add(91, (x + 0.5) * 16, bottom * 16, 16, 16)
    link(a, b)
    link(b, a)
    L.add(136, x * 16, bottom * 16, 32, 16, path=a)


lift(81, 2, 5)  # the vine, then a higher lift to the right up to coin heaven, like 3-1
L.add(131, 19 * 16, 9 * 16, 32, 16, disableInventory=True, zoneTo='level-6-2-underground')
L.add(153, 35 * 16, 11 * 16, 32, 16)
L.add(131, 56 * 16, 8 * 16, 32, 16, disableInventory=True, zoneTo='level-6-2-underwater')
L.add(153, 115 * 16, 11 * 16, 32, 16)
L.add(131, 153 * 16, 10 * 16, 32, 16, disableInventory=True, zoneTo='level-6-2-underground2')
L.add(153, 179 * 16, 11 * 16, 32, 16)
L.add(30, 222 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-6-3-begin')

# coin heaven sits above the level, NES rows -11 to -1
UP = 11
L.grow_top(UP)
row = lambda r: r + UP
heaven = np.array(Image.open(f'{NES}/6-2.png').convert('RGB'))[0:240, :W * 16]
cloud = np.array(Image.open(f'{NES}/3-1.png').convert('RGB'))[13 * 16:14 * 16, 127 * 16:128 * 16]
for x in range(60, W):  # the legend is on the left
    for y in range(15 - UP, 15):
        c = heaven[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        if (c == cloud).all():
            L.set(x, y - 15 + UP, (TILE(6, 22), 5901, 0, 0))
        elif 60 <= (c == (252, 152, 56)).all(2).sum() <= 90:
            L.set(x, y - 15 + UP, (0, 0, 66, 0))
for x in range(W):  # the nesmaps arrow from coin heaven
    for y in (row(0), row(1)):
        if L.get(x, y)[0] >= TILE(0, 23):
            L.set(x, y, E)
for x in (83, 84):  # shaft for the second lift
    L.set(x, row(-2), E)
lift(83, row(-2), row(1))
a = L.add(91, 93.5 * 16, row(-4) * 16, 16, 16)  # the cloud lift
b = L.add(91, 108.5 * 16, row(-4) * 16, 16, 16)
link(a, b)
link(b, a)
L.add(136, 93 * 16, row(-4) * 16, 32, 16, path=a)
for x in range(160, 166):  # falling off the end of coin heaven drops back into the level at column 163
    L.add(30, x * 16, row(0) * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-6-2-game', zoneX=163.5, zoneY=row(11))
L.save('level-6-2-game.json')

# underwater: the same as 5-2's, two columns further on
m = json.load(open(f'{ROOT}/level-5-2-underwater.json'))
for p in m['properties']:
    if p['name'] == 'customIndicator':
        p['value'] = '6-2'
for l in m['layers']:
    for o in l.get('objects', []):
        for p in o.get('properties', []):
            if p['name'] == 'zoneTo':
                p['value'] = 'level-6-2-game'
            if p['name'] == 'zoneX':
                p['value'] = 115.5
open(f'{ROOT}/level-6-2-underwater.json', 'w').write(dumps(m))

# coin rooms, the same as 4-2's and 4-1's
ROOM_A = ['#######..............PP#######', '#######..............PP#######', '#######...#######....PP#######', '#######.........#....PP#######',
          '#######.........#....PP#######', '#######....ooooo#....PP#######', '#######...#ooooo###..PP#######', '#######...#######..o.PP#######',
          '#######..............PP#######', '#######..............LL#######'] + ['#######..................#####'] * 3 + ['=' * 30] * 4
ROOM_B = ['#######..............PP#######', '#######..............PP#######', '#######..############PP#######'] + ['#######..............PP#######'] * 5 + [
          '#######..oooooooo....PP#######', '#######..########..M.LL#######', '#######..#......#........#####', '#######..#......#........#####',
          '#######..oooooooooo......#####'] + ['=' * 30] * 4
underground('level-6-2-underground.json', 'level-2-1-underground.json', ROOM_A, {'customIndicator': '6-2', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-6-2-game', 35.5, 9 + UP))
underground('level-6-2-underground2.json', 'level-2-1-underground.json', ROOM_B, {'customIndicator': '6-2', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-6-2-game', 179.5, 9 + UP))
