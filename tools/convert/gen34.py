from paths import NES
import json
import numpy as np
from gen import Level, from_image, extend_down, copy_cells, ROOT

W = 160
grid, unknown, img = from_image('3-4', 0, W)
print('unknown', unknown)
L = Level('level-2-4-game.json', W)
L.prop('customIndicator', '3-4')
for (x, y), v in grid.items():
    L.set(x, y, v)

# ? blocks with coins either side of a mushroom, and three coins
L.set(42, 9, (0, 0, 0, 0))
L.set(44, 9, (0, 0, 0, 0))
L.set(43, 9, (0, 113, 0, 0))
L.add(139, 42 * 16, 10 * 16, 16, 32, **{'spawn-type': 'coin'})
L.add(139, 44 * 16, 10 * 16, 16, 32, **{'spawn-type': 'coin'})
for x in (81, 82, 83):
    L.set(x, 6, (0, 0, 66, 0))
for x in (88, 97, 103, 109):  # lava under the podoboos
    L.set(x, 12, L.get(x + 1, 12))
extend_down(L)
copy_cells(L, 'level-2-4-game.json', range(134, 160), range(2, 17))  # the Bowser bridge and ending match 2-4

L.add(90, 0, 7 * 16, 48, 48, actor='Mario')

# podoboos
for x in (16, 26, 88, 97, 103, 109):
    L.add(38, x * 16 - 16, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)

# firebars: a flying beetle circling its block, like 2-4
RING = [(1, 3), (2, 2), (2, 0), (1, -1), (-1, -1), (-2, 0), (-2, 2), (-1, 3)]
for px in range(W):
    for py in range(15):
        c = img[py * 16:py * 16 + 16, px * 16:px * 16 + 16]
        if (c == (200, 76, 12)).all(2).sum() >= 100 and (c == (216, 40, 0)).all(2).any():
            ids = [L.add(91, (px + dx) * 16, (py + dy) * 16, 16, 16) for dx, dy in RING]
            for i, oid in enumerate(ids):
                L.objects[-8 + i]['properties'] = [{'name': 'path', 'type': 'object', 'value': ids[(i + 1) % 8]}]
            L.add(188, (px - 1) * 16, (py + 3) * 16, 48, 32, path=ids[0])

# Bowser's fire
for x, y in ((101, 10), (115, 8), (122.5, 9), (129, 10)):
    L.add(42, x * 16 - 12, y * 16, 48, 32, respawn=True)  # centred on the 24 wide NES fire

# the Bowser bridge is the same as 2-4: copy its lift, Bowser and the level end
src = [o for l in json.load(open(f'{ROOT}/level-2-4-game.json'))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
ids = {}
for o in src:
    if o['x'] >= 134 * 16 and o['gid'] not in (42, 30):
        ids[o['id']] = L.nextid
        L.nextid += 1
for o in src:
    if o['id'] in ids:
        o = json.loads(json.dumps(o))
        o['id'] = ids[o['id']]
        for p in o.get('properties', []):
            if p['name'] == 'path':
                p['value'] = ids[p['value']]
        L.objects.append(o)
for x in range(144, 160):  # into World 4: doors all along the floor of the end room
    L.add(30, x * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-4-1-begin')
L.save('level-3-4-game.json')
