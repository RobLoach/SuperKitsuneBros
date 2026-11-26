import json
from gen import dumps, obj, ROOT

# 6-4 has the same layout as 1-4, only the sprites are in different poses
m = json.load(open(f'{ROOT}/level-1-4-game.json'))
for p in m['properties']:
    if p['name'] == 'customIndicator':
        p['value'] = '6-4'
for l in m['layers']:
    if l['type'] == 'objectgroup':
        l['objects'] = [o for o in l['objects'] if o['gid'] != 30]
        for x in range(144, 160):  # into World 7: doors all along the floor of the end room
            l['objects'].append({'gid': 30, 'height': 32, 'id': m['nextobjectid'], 'name': '', 'rotation': 0, 'type': '', 'visible': True,
                                 'properties': [{'name': 'alwaysActive', 'type': 'bool', 'value': True}, {'name': 'visible', 'type': 'bool', 'value': False},
                                                {'name': 'zoneTo', 'type': 'string', 'value': 'level-7-1-begin'}],
                                 'width': 16, 'x': x * 16, 'y': 13 * 16})
            m['nextobjectid'] += 1

# 6-4 adds firebars on four of 1-4's plain blocks, and Podoboos over the lava and the bridge. The firebars are built like
# 1-4's: a flying beetle circling 8 path nodes around the block
objects = next(l for l in m['layers'] if l['type'] == 'objectgroup')['objects']


def add(gid, x, y, w, h, **props):
    objects.append(obj(m['nextobjectid'], gid, x, y, w, h, **props))
    m['nextobjectid'] += 1
    return m['nextobjectid'] - 1


RING = [(2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1)]
for bx, by in ((23, 6), (37, 6), (80, 4), (92, 9)):
    first = m['nextobjectid']
    for i, (dx, dy) in enumerate(RING):
        nxt = first + (i + 1) % len(RING)
        add(91, (bx + dx) * 16, (by + 1 + dy) * 16, 16, 16, path=nxt, pathType='circley' if abs(dx) == 2 else 'circlex')
    add(188, (bx + 1) * 16, by * 16, 48, 32, path=first)
for x in (27.6, 33.2, 131.6):  # Podoboo centres
    add(38, round(x * 16) - 24, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)
open(f'{ROOT}/level-6-4-game.json', 'w').write(dumps(m))
