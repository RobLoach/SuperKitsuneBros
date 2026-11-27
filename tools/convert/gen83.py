from paths import NES
import numpy as np
from PIL import Image
from gen import cannons, overworld, extend_down, flag_image

W = 240
L = overworld('8-3', 0, W, legend=('8-3', 'B83'), tileset=None, qref=('8-2', 0, 29, 9), fresh=True)
img = np.array(Image.open(f'{NES}/8-3.png').convert('RGB'))[:240, :W * 16]
head = np.array(Image.open(f'{NES}/5-1.png').convert('RGB'))[11 * 16:12 * 16, 111 * 16:112 * 16]
print('cannons', cannons(L, img, head))
flag_image(L, '8-3', 0, 213, (92, 148, 252))  # the NES flagpole
for o in L.objects:  # the five Koopas walking in front of the last walls, not Hammer Bros
    if o['gid'] == 79 and 140 * 16 <= o['x'] <= 190 * 16 and o['y'] == 13 * 16:
        o['gid'] = 24
for x in range(1, W - 1):  # the castle walls behind the Hammer Bros, Paratroopas and a Bullet Bill, left as sky
    for y in range(7, 13):
        c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        if L.get(x, y) != (0, 0, 0, 0) or (c == (92, 148, 252)).all(2).mean() > 0.5:
            continue
        for a, b in (((x - 1, y), (x + 1, y)), ((x, y - 1), (x, y + 1))):
            if L.get(*a) == L.get(*b) and L.get(*a)[0] and not L.get(*a)[1]:
                L.set(x, y, L.get(*a))
                break
extend_down(L)
for d in (222, 224, 226):  # the big castle, like 1-3
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-8-4-begin')
L.save('level-8-3-game.json')
