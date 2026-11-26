from paths import NES
import numpy as np
from PIL import Image
from gen import overworld, extend_down
import sprites

W = 192
L = overworld('6-3', 0, W, template='level-1-3-game.json', legend=('6-3', 'B63'), tileset='tileset-night.png', qref=('6-1', 0, 17, 9), fresh=True)
img = np.array(Image.open(f'{NES}/6-3.png').convert('RGB'))[:240, :W * 16]
E = (0, 0, 0, 0)
for x, y, w in sprites.lifts(img):  # lifts are objects, not tiles
    for xx in range(x // 16, (x + w + 15) // 16):
        for yy in range(y // 16, (y + 7) // 16 + 1):
            L.set(xx, yy, E)
for x in range(W):  # lift ropes look like the flagpole
    for y in range(15):
        if L.get(x, y)[0] == 4879 and x != 167:
            L.set(x, y, E)
for x in (38, 116):  # springboards, lifts instead
    for y in (11, 12):
        L.set(x, y, E)
for x in range(170, W):  # the castle matched 2-4's walls: it is scenery here, like 1-3
    for y in range(13):
        v = L.get(x, y)
        L.set(x, y, (v[0], 0, v[2], v[3]))
extend_down(L)

for n, x, y, w, h, s in sprites.find(img, sprites.templates('6-3', sprites.B63)):  # Bullet Bills: hornets that come back
    if n.startswith('bullet'):
        L.add(42, x + w // 2 - 24, round((y + h) / 16) * 16, 48, 32, respawn=True)


def lift(x, y, path):
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


# pulley (balance) lifts move in opposite directions, the falling lifts go back and forth
MOVE = {28: ('v', 13, 6), 60: ('v', 12, 5), 70: ('v', 9, 3), 74: ('v', 3, 9), 78: ('v', 9, 3), 81: ('v', 3, 9),
        126: ('v', 9, 3), 129: ('v', 3, 9)}
for x, y, w in sprites.lifts(img):
    lift(x, y, MOVE.get(x // 16, ('h', 2, -2)))
for x in (38, 116):
    lift(x * 16, 12 * 16, ('v', 12, 3))
for d in (172, 174, 176):
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-6-4-begin')
L.save('level-6-3-game.json')
