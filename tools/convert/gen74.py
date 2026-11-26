import json
import numpy as np
from gen import Level, from_image, extend_down, copy_cells, night, ROOT

grid, unknown, img = from_image('7-4', 0, 224)
# space the maze out: repeat a plain stretch of corridor before each door, so where a path ends can't be seen from
# where it splits. X() moves an NES column to its map column
STRETCH = 24
cuts = [next(x for x in range(want, 224) if all(grid.get((x, y)) == grid.get((x - 1, y)) for y in range(15)))
        for want in (43, 58, 82, 112, 125, 148)]
X = lambda x: x + STRETCH * sum(c <= x for c in cuts)
src = [c for x in range(224) for c in [x - 1] * STRETCH * (x in cuts) + [x]]
W = len(src)
print("maze cuts", cuts)
L = Level('level-2-4-game.json', W)
L.prop('customIndicator', '7-4')
night(L)  # grey castle palette
for x, sx in enumerate(src):
    for y in range(15):
        L.set(x, y, grid[sx, y])
extend_down(L)
copy_cells(L, 'level-3-4-game.json', range(134, 160), range(2, 17), dx=X(198) - 134)  # the Bowser bridge and ending match 3-4

L.add(90, 0, 7 * 16, 48, 48, actor='Mario')
RING = [(1, 3), (2, 2), (2, 0), (1, -1), (-1, -1), (-2, 0), (-2, 2), (-1, 3)]
px, py = X(103), 7  # the firebar, like 2-4
ids = [L.add(91, (px + dx) * 16, (py + dy) * 16, 16, 16) for dx, dy in RING]
for i, oid in enumerate(ids):
    L.objects[-8 + i]['properties'] = [{'name': 'path', 'type': 'object', 'value': ids[(i + 1) % 8]}]
L.add(188, (px - 1) * 16, (py + 3) * 16, 48, 32, path=ids[0])
for x in (20.1, 196.1):  # podoboos
    L.add(38, round(X(x) * 16) + 8 - 24, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)
L.add(42, round(X(180.2) * 16), 10 * 16, 48, 32, respawn=True)  # Bowser's fire
for x, y in ((18, 8), (22, 9)):  # the flimsy lifts over the lava bob up and down
    a = L.add(91, (x + 0.5) * 16, y * 16, 16, 16)
    b = L.add(91, (x + 0.5) * 16, (y + 1) * 16, 16, 16)
    for o, t in ((L.objects[-2], b), (L.objects[-1], a)):
        o['properties'] = [{'name': 'path', 'type': 'object', 'value': t}]
    L.add(136, x * 16, y * 16, 32, 16, path=a)
src34 = [o for l in json.load(open(f'{ROOT}/level-3-4-game.json'))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
for o in src34:
    if o['gid'] == 196 and o['x'] >= 134 * 16:
        L.add(196, o['x'] + (X(198) - 134) * 16, o['y'], o['width'], o['height'], **{p['name']: p['value'] for p in o.get('properties', [])})
for x in range(X(208), W):  # into World 8: doors all along the floor of the end room
    L.add(30, x * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-8-1-begin')

# the maze: each wrong path ends at a door standing at its far end, walled off where it would rejoin the right path,
# and the door takes you back to the start of the puzzle. The NES checks your height at set points instead, so a few
# places where paths meet are filled in (NES columns, rows)
BRICK = L.get(0, 2)
WALLS = [(50, (3, 4, 5)), (65, (3, 4, 5)), (66, (11, 12)), (119, (11, 12)), (134, (3, 4, 5)), (153, (7, 8, 9)),
         *((x, (6, 7, 8, 9)) for x in range(88, 96)),  # puzzle 1's last bottom path ends at its door, and the top path runs on into puzzle 2
         *((x, (6, 7, 8, 9)) for x in (116, 117)), (118, (7, 8, 9)),  # puzzle 2's first bottom path can't be jumped out of past its door
         (122, (10,)), (123, (10,)),  # dropping from the top path lands in the middle one
         (130, (6,)), (131, (6,)),  # the second top path can't drop back into the middle one past its door
         *((x, (10,)) for x in range(105, 110))]  # a floor under puzzle 2's short middle path, so its door isn't hanging over the bottom one
for x, ys in WALLS:
    for y in ys:
        L.set(X(x), y, BRICK)
P1, P2 = (30.5, 8), (X(95) + 0.5, 4)  # on the block before puzzle 1, and on the top path before the firebar
DOORS = [(49, 6, P1),  # puzzle 1: the bottom path first, not the top...
         (64, 6, P1), (65, 13, P1),  # ...then the middle, not the top or bottom...
         (92, 13, P1),  # ...then the top, not the bottom
         (109, 10, P2), (118, 13, P2),  # puzzle 2: the top with the firebar first, not the middle or bottom...
         (133, 6, P2),  # ...then stay in the middle, not up...
         (152, 10, P2)]  # ...then the top again, not the middle
for x, y, (zx, zy) in DOORS:
    L.add(30, X(x) * 16, y * 16, 16, 32, alwaysActive=True, wrongWarp=True, zoneTo='level-7-4-game', zoneX=zx, zoneY=zy)  # with a buzzer
L.save('level-7-4-game.json')
