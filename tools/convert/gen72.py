from paths import NES
import json
import numpy as np
from PIL import Image
from gen import dumps, redraw_water, ROOT
import sprites

# 7-2 has the same layout as 2-2, with more Bloopers and Cheep-cheeps
SUBS = [('level-2-2-', 'level-7-2-'), ('level-2-3-begin', 'level-7-3-begin'), ('"2-2"', '"7-2"')]
for part in ('game', 'game2'):
    s = open(f'{ROOT}/level-2-2-{part}.json').read()
    for a, b in SUBS:
        s = s.replace(a, b)
    open(f'{ROOT}/level-7-2-{part}.json', 'w').write(s)

m = json.loads(open(f'{ROOT}/level-2-2-underwater.json').read().replace('level-2-2-game2', 'level-7-2-game2').replace('"2-2"', '"7-2"'))
img = np.array(Image.open(f'{NES}/7-2.png').convert('RGB'))[240:480, :m['width'] * 16]
objects = next(l for l in m['layers'] if l['type'] == 'objectgroup')['objects']
objects[:] = [o for o in objects if o['gid'] not in (103, 77, 75)]
nid = m['nextobjectid']
for n, x, y, w, h, s in sprites.find(img, sprites.templates('7-2', sprites.B72)):
    g = 103 if n.startswith('blooper') else 77
    objects.append({'gid': g, 'height': 32, 'id': nid, 'name': '', 'rotation': 0, 'type': '', 'visible': True, 'width': 48,
                    'x': x + w // 2 - 24, 'y': round((y + h) / 16) * 16})
    nid += 1
m['nextobjectid'] = nid
redraw_water(m, img, [o for o in sprites.find(img, sprites.templates('7-2', sprites.B72))])  # the NES coral and seaweed
open(f'{ROOT}/level-7-2-underwater.json', 'w').write(dumps(m))
print(sum(1 for o in objects if o['gid'] in (103, 77)), 'fish')
