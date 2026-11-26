from paths import NES
import json
import numpy as np
from PIL import Image
from gen import dumps, ENEMY, ROOT
import sprites

# 7-3 has the same layout as 2-3, with Koopas and Paratroopas on the bridges as well as the flying Cheep-cheeps
m = json.loads(open(f'{ROOT}/level-2-3-game.json').read().replace('level-2-4-begin', 'level-7-4-begin').replace('"2-3"', '"7-3"'))
img = np.array(Image.open(f'{NES}/7-3.png').convert('RGB'))[:240, :m['width'] * 16]
objects = next(l for l in m['layers'] if l['type'] == 'objectgroup')['objects']
nid = m['nextobjectid']
for n, x, y, w, h, s in sprites.find(img, sprites.templates('7-3', sprites.B73)):
    n = n.replace('_flip', '').rstrip('2')
    if n in ('koopa', 'paratroopa'):
        g, ow, oh, props = ENEMY[n]
        o = {'gid': g, 'height': oh, 'id': nid, 'name': '', 'rotation': 0, 'type': '', 'visible': True, 'width': ow,
             'x': x + w // 2 - ow // 2, 'y': round((y + h) / 16) * 16}
        objects.append(o)
        nid += 1
m['nextobjectid'] = nid
open(f'{ROOT}/level-7-3-game.json', 'w').write(dumps(m))
print(nid - json.load(open(f'{ROOT}/level-2-3-game.json'))['nextobjectid'], 'Koopas')

from world12 import clouds
clouds('7-3', 0, 'level-7-3-game.json')  # 7-3's own clouds, not 2-3's
