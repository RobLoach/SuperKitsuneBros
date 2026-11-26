from paths import NES
import json, math
import numpy as np
from PIL import Image
from gen import Level, from_image, ROOT, LAYERS

# 5-4 is 2-4 with more firebars: start from the 2-4 map and add the differences
W = 160
src = json.load(open(f'{ROOT}/level-2-4-game.json'))
L = Level('level-2-4-game.json', W)
S = {l['name']: l['data'] for l in src['layers'] if l['type'] == 'tilelayer'}
for name, data in L.layers.items():
    data[:] = S[name]
L.prop('customIndicator', '5-4')

grid, unknown, img = from_image('5-4', 0, W)
old = np.array(Image.open(f'{NES}/2-4.png').convert('RGB'))[:240, :W * 16]
for (x, y), v in grid.items():
    if (x, y) not in unknown and not (img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == old[y * 16:y * 16 + 16, x * 16:x * 16 + 16]).all():
        L.set(x, y, v)
for x in range(W):  # 2-4's map has a few blocks the NES doesn't (a ledge under the firebar at 55 left only a 2-tall gap)
    for y in range(2, 15):
        if L.get(x, y)[1] and not img[y * 16:y * 16 + 16, x * 16:x * 16 + 16].any():
            L.set(x, y, (0, 0, 0, 0))

keep = [o for l in src['layers'] if l['type'] == 'objectgroup' for o in l['objects'] if o['gid'] in (90, 136, 196)]
ids = {p['value'] for o in keep for p in o.get('properties', []) if p['name'] == 'path'}
nodes = [o for l in src['layers'] if l['type'] == 'objectgroup' for o in l['objects'] if o['id'] in ids]
ids |= {p['value'] for o in nodes for p in o.get('properties', []) if p['name'] == 'path'}
for o in keep + [o for l in src['layers'] if l['type'] == 'objectgroup' for o in l['objects'] if o['id'] in ids and o not in keep]:
    L.objects.append(o)
L.nextid = max(o['id'] for o in L.objects) + 1


def firebar(px, py, r):
    """a flying beetle circling the firebar's block, like 2-4"""
    cx, cy = px + 0.5, py + 0.5
    pts = [(cx + r * math.cos(math.pi / 4 * k) - 0.5, cy + r * math.sin(math.pi / 4 * k) + 0.5) for k in range(8)]
    ids = [L.add(91, round(x * 16), round(y * 16), 16, 16) for x, y in pts]
    for i, oid in enumerate(ids):
        L.objects[-8 + i]['properties'] = [{'name': 'path', 'type': 'object', 'value': ids[(i + 1) % 8]}]
    x, y = pts[0]
    L.add(188, round(x * 16) - 16, round(y * 16), 48, 32, path=ids[0])


for px, py in ((55, 5), (82, 6), (49, 9), (61, 9), (73, 9), (92, 10), (103, 11), (43, 13), (55, 13), (67, 13)):
    firebar(px, py, 2)
firebar(23, 7, 4.5)  # the long one
for x, y in ((20.1, 5), (16.1, 6), (30.1, 6), (109.1, 6), (113.1, 6), (131.1, 7)):  # podoboos
    L.add(38, round(x * 16) + 8 - 24, 14 * 16, 48, 96, flyDistance=7, flyVertical=True, respawn=True)
for x, y in ((96.2, 8), (110.4, 10), (124.4, 8)):  # Bowser's fire
    L.add(42, round(x * 16), y * 16, 48, 32, respawn=True)
for x in range(144, 160):  # into World 6: doors all along the floor of the end room
    L.add(30, x * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-6-1-begin')
L.save('level-5-4-game.json')
