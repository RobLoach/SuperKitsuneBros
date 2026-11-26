import json
from bowsers import GIDS
import numpy as np
from gen import Level, from_image, extend_down, copy_cells, night, ROOT
import sprites

W = 192
grid, unknown, img = from_image('4-4', 0, W)
print('unknown', unknown)
L = Level('level-2-4-game.json', W)
L.prop('customIndicator', '4-4')
night(L)  # the grey pipe
for (x, y), v in grid.items():
    L.set(x, y, v)
extend_down(L)
copy_cells(L, 'level-3-4-game.json', range(134, 160), range(2, 17), dx=32)  # the Bowser bridge and ending match 3-4

L.add(90, 0, 7 * 16, 48, 48, actor='Mario')
L.add(132, 40 * 16, 10 * 16, 32, 32)  # piranha plant in the pipe

# firebars: a flying beetle circling its block, like 2-4
RING = [(1, 3), (2, 2), (2, 0), (1, -1), (-1, -1), (-2, 0), (-2, 2), (-1, 3)]
pivots = [(53, 6), (60, 9), (115, 6), (122, 10), (162, 10)]  # the firebars here turn inside the walls
for px, py in pivots:
    ids = [L.add(91, (px + dx) * 16, (py + dy) * 16, 16, 16) for dx, dy in RING]
    for i, oid in enumerate(ids):
        L.objects[-8 + i]['properties'] = [{'name': 'path', 'type': 'object', 'value': ids[(i + 1) % 8]}]
    L.add(188, (px - 1) * 16, (py + 3) * 16, 48, 32, path=ids[0])
print('firebars', pivots)

found = sprites.find(img, sprites.templates('4-4', sprites.B44))
for n, x, y, w, h, s in found:  # podoboos jump from the lava
    L.add(38, x + w // 2 - 24, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)
print('podoboos', [(x / 16, y / 16) for n, x, y, w, h, s in found])

# the fake Bowser's fire
for x, y in ((130.9, 10), (160.5, 8)):
    L.add(42, x * 16 - 12, y * 16, 48, 32, respawn=True)

src = [o for l in json.load(open(f'{ROOT}/level-3-4-game.json'))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
for x in range(176, 192):  # into World 5: doors all along the floor of the end room
    L.add(30, x * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-5-1-begin')
for o in src:
    if o['gid'] in GIDS and o['x'] >= 134 * 16:
        p = {q['name']: q['value'] for q in o.get('properties', [])}
        L.add(o['gid'], o['x'] + 32 * 16, o['y'], o['width'], o['height'], **p)


# the maze: wrong paths end at a door that takes you back to where the paths split
BRICK = L.get(0, 2)
for y in (10, 11, 12):  # the bottom path of the first split is walled off
    L.set(74, y, BRICK)
for x, y, zx, zy in ((73, 13, 14.5, 8),  # first split: the bottom path
                     (143, 5, 86.5, 11), (142, 10, 86.5, 11)):  # second split: the top and middle paths
    L.add(30, x * 16, y * 16, 16, 32, alwaysActive=True, wrongWarp=True, zoneTo='level-4-4-game', zoneX=zx, zoneY=zy)  # with a buzzer
L.save('level-4-4-game.json')
