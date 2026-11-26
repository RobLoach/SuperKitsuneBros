import json
from gen import dumps, ROOT

# 6-4 has the same layout as 1-4, only the sprites are in different poses
m = json.load(open(f'{ROOT}/level-1-4-game.json'))
for p in m['properties']:
    if p['name'] == 'customIndicator':
        p['value'] = '6-4'
for l in m['layers']:
    if l['type'] == 'objectgroup':
        for o in l['objects']:  # the 1-4 doors lead into World 7 instead
            for p in o.get('properties', []):
                if p['name'] == 'zoneTo':
                    p['value'] = 'level-7-1-begin'
open(f'{ROOT}/level-6-4-game.json', 'w').write(dumps(m))
