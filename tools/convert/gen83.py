from paths import NES
import numpy as np
from PIL import Image
from gen import cannons, overworld, extend_down, flag_image, ENEMY

W = 240
L = overworld('8-3', 0, W, legend=('8-3', 'B83'), tileset=None, qref=('8-2', 0, 29, 9), fresh=True)
img = np.array(Image.open(f'{NES}/8-3.png').convert('RGB'))[:240, :W * 16]
head = np.array(Image.open(f'{NES}/5-1.png').convert('RGB'))[11 * 16:12 * 16, 111 * 16:112 * 16]
print('cannons', cannons(L, img, head))
flag_image(L, '8-3', 0, 213, (92, 148, 252))  # the NES flagpole
for o in L.objects:  # the five Koopas walking in front of the last walls, not Hammer Bros
    if o['gid'] == ENEMY['hammer'][0] and 140 * 16 <= o['x'] <= 190 * 16 and o['y'] == 13 * 16:
        g, w, h, _ = ENEMY['koopa']
        o.update(gid=g, x=o['x'] + (o['width'] - w) // 2, width=w, height=h)
extend_down(L)
for d in (222, 224, 226):  # the big castle, like 1-3
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-8-4-begin')
L.save('level-8-3-game.json')
