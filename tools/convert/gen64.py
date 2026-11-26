import json
from gen import dumps, ROOT

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
open(f'{ROOT}/level-6-4-game.json', 'w').write(dumps(m))
