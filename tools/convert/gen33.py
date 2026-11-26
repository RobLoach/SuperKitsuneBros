from paths import NES
import numpy as np
from PIL import Image
from gen import overworld, extend_down, copy_cells, flag
import sprites

W = 176
L = overworld('3-3', 0, W, template='level-1-3-game.json', legend=('3-3', 'B33'), tileset='tileset-night.png')
img = np.array(Image.open(f'{NES}/3-3.png').convert('RGB'))[:240, :W * 16]

# coins left unknown by the classifier (night coins are orange on black)
ORANGE = np.array((252, 152, 56))
for x in range(W):
    for y in range(15):
        c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        n = (c == ORANGE).all(2).sum()
        if 60 <= n <= 90 and L.get(x, y) == (0, 0, 0, 0) and not (c == (216, 40, 0)).all(2).any():
            L.set(x, y, (0, 0, 66, 0))

# pulley ropes look like the flagpole
for x in range(W):
    for y in range(15):
        if L.get(x, y)[0] == 4879:
            L.set(x, y, (0, 0, 0, 0))
flag(L, 150, green=True)
extend_down(L)


def lift(x, y, path):
    """moving platform centred on a 3 wide NES lift, moving between rows path[0] and path[1] (or columns)"""
    px, py = x - 8, (round(y / 16) + 1) * 16
    if path[0] == 'v':
        a = L.add(91, px + 24, path[1] * 16, 16, 16)
        b = L.add(91, px + 24, path[2] * 16, 16, 16, path=a)
    else:
        a = L.add(91, px + 24 + path[1] * 16, py, 16, 16)
        b = L.add(91, px + 24 + path[2] * 16, py, 16, 16, path=a)
    L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]
    L.add(92, px, py, 64, 16, path=a)


# vertical lifts come in pairs, the pulley (balance) lifts move in opposite directions
MOVE = {30: ('v', 3, 14), 33: ('v', 14, 3), 60: ('h', 3, -3), 81: ('v', 10, 4), 88: ('v', 4, 10), 94: ('v', 14, 3),
        96: ('v', 3, 14), 103: ('h', 3, -3), 132: ('h', 3, -3), 136: ('v', 9, 3), 140: ('v', 3, 9)}
for x, y, w in sprites.lifts(img):
    lift(x, y, MOVE[x // 16])

for d in (156, 158, 160):
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-3-4-begin')
L.save('level-3-3-game.json')
