from paths import NES
import numpy as np
from PIL import Image
from gen import overworld, extend_down
import sprites

W = 176
L = overworld('5-3', 0, W, template='level-1-3-game.json', legend=('5-3', 'B53'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True)
img = np.array(Image.open(f'{NES}/5-3.png').convert('RGB'))[:240, :W * 16]
for x, y, w in sprites.lifts(img):  # lifts are objects, not tiles
    for xx in range(x // 16, (x + w + 15) // 16):
        L.set(xx, y // 16, (0, 0, 0, 0))
        L.set(xx, y // 16 + 1, (0, 0, 0, 0)) if (y % 16) > 8 else None
extend_down(L)

# Bullet Bills fly in from the right: hornets that come back
for n, x, y, w, h, s in sprites.find(img, sprites.templates('5-3', sprites.B53)):
    if n.startswith('bullet'):
        L.add(42, x + w // 2 - 24, round((y + h) / 16) * 16, 48, 32, respawn=True)


def lift(x, y, path):
    """moving platform on a 2 wide NES lift, the same moves as 1-3"""
    px, py = x, (round(y / 16) + 1) * 16
    if path[0] == 'v':
        a = L.add(91, px + 8, path[1] * 16, 16, 16)
        b = L.add(91, px + 8, path[2] * 16, 16, 16)
    else:
        a = L.add(91, px + 8 + path[1] * 16, py, 16, 16)
        b = L.add(91, px + 8 + path[2] * 16, py, 16, 16)
    for o, t in ((L.objects[-2], b), (L.objects[-1], a)):
        o['properties'] = [{'name': 'path', 'type': 'object', 'value': t}]
    L.add(136, px, py, 32, 16, path=a)


MOVE = {55: ('v', 7, 15), 86: ('h', 1, -2), 94: ('h', 1, -3), 131: ('h', 1, -3)}
for x, y, w in sprites.lifts(img):
    lift(x, y, MOVE[x // 16])
for d in (157, 159, 161):
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-5-4-begin')
L.save('level-5-3-game.json')
