import json
import numpy as np
from gen import Level, from_image, extend_down, copy_cells, night, ROOT

W = 224
grid, unknown, img = from_image('7-4', 0, W)
L = Level('level-2-4-game.json', W)
L.prop('customIndicator', '7-4')
night(L)  # grey castle palette
for (x, y), v in grid.items():
    L.set(x, y, v)
extend_down(L)
copy_cells(L, 'level-3-4-game.json', range(134, 160), range(2, 17), dx=64)  # the Bowser bridge and ending match 3-4

L.add(90, 0, 7 * 16, 48, 48, actor='Mario')
RING = [(1, 3), (2, 2), (2, 0), (1, -1), (-1, -1), (-2, 0), (-2, 2), (-1, 3)]
px, py = 103, 7  # the firebar, like 2-4
ids = [L.add(91, (px + dx) * 16, (py + dy) * 16, 16, 16) for dx, dy in RING]
for i, oid in enumerate(ids):
    L.objects[-8 + i]['properties'] = [{'name': 'path', 'type': 'object', 'value': ids[(i + 1) % 8]}]
L.add(188, (px - 1) * 16, (py + 3) * 16, 48, 32, path=ids[0])
for x in (20.1, 196.1):  # podoboos
    L.add(38, round(x * 16) + 8 - 24, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)
L.add(42, round(180.2 * 16), 10 * 16, 48, 32, respawn=True)  # Bowser's fire
for x, y in ((18, 8), (22, 9)):  # the flimsy lifts over the lava bob up and down
    a = L.add(91, (x + 0.5) * 16, y * 16, 16, 16)
    b = L.add(91, (x + 0.5) * 16, (y + 1) * 16, 16, 16)
    for o, t in ((L.objects[-2], b), (L.objects[-1], a)):
        o['properties'] = [{'name': 'path', 'type': 'object', 'value': t}]
    L.add(136, x * 16, y * 16, 32, 16, path=a)
src = [o for l in json.load(open(f'{ROOT}/level-3-4-game.json'))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
for o in src:
    if o['gid'] == 196 and o['x'] >= 134 * 16:
        L.add(196, o['x'] + 64 * 16, o['y'], o['width'], o['height'], **{p['name']: p['value'] for p in o.get('properties', [])})
for x in range(208, 224):  # into World 8: doors all along the floor of the end room
    L.add(30, x * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-8-1-begin')

# the maze: each wrong path ends at a door back to the start of its puzzle, walled off where it would rejoin the right path
BRICK = L.get(0, 2)
for x, ys in ((51, (3, 4, 5)), (67, (3, 4, 5)), (67, (11, 12)), (119, (11, 12)), (134, (3, 4, 5)), (159, (11, 12))):
    for y in ys:
        L.set(x, y, BRICK)
P1, P2 = (33.5, 11), (96.5, 8)
DOORS = [(50, 4, P1), (50, 6, P1),  # puzzle 1: take the bottom...
         (66, 4, P1), (66, 6, P1), (66, 13, P1),  # ...then the middle...
         (92, 11, P1), (92, 13, P1),  # ...then the top
         (109, 8, P2), (109, 10, P2), (118, 12, P2), (118, 13, P2),  # puzzle 2: take the top with the firebar...
         (133, 4, P2), (133, 6, P2),  # ...then stay in the middle...
         (158, 13, P2)]  # ...then the top again
for x, y, (zx, zy) in DOORS:
    L.add(30, x * 16, y * 16, 16, 32, alwaysActive=True, zoneTo='level-7-4-game', zoneX=zx, zoneY=zy)
L.save('level-7-4-game.json')
