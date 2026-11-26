from paths import NES, ROOT
import numpy as np
from PIL import Image
from gen import overworld, extend_down, flag, ropes
import sprites

W = 160
L = overworld('4-3', 0, W, template='level-1-3-game.json', legend=('4-3', 'B43'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True)
img = np.array(Image.open(f'{NES}/4-3.png').convert('RGB'))[:240, :W * 16]

# mushroom caps are solid, their stems are background
ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
def is_cap(g):
    i = g - 4813
    t = ts[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16]
    red, orange = (t[..., :3] == (216, 40, 0)).all(2).sum(), (t[..., :3] == (252, 152, 56)).all(2).sum()
    return i >= 23 * 32 and red >= 10 and red + orange >= 60
def is_coin(g):
    i = g - 4813
    t = ts[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16]
    return i >= 23 * 32 and not (t[..., :3] == (216, 40, 0)).all(2).any() and 60 <= (t[..., :3] == (252, 152, 56)).all(2).sum() <= 90
for x in range(W):
    for y in range(15):
        v = L.get(x, y)
        if v[0] and v[1] == 0 and is_cap(v[0]):
            L.set(x, y, (v[0], 5901, 0, 0))
        elif v[0] and is_coin(v[0]):
            L.set(x, y, (0, 0, 66, 0))
# lifts are objects, not tiles
for lx, ly, lw in sprites.lifts(img):
    for x in range(lx // 16, (lx + lw + 15) // 16):
        for y in range(ly // 16, (ly + 7) // 16 + 1):
            L.set(x, y, (0, 0, 0, 0))

# lift ropes look like the flagpole
for x in range(W):
    for y in range(15):
        if L.get(x, y)[0] == 4879:
            L.set(x, y, (0, 0, 0, 0))
ropes(L, img, (92, 148, 252))  # pulley ropes and wheels that the lifts covered
flag(L, 146, red=True)
extend_down(L)


def lift(x, y, path):
    px, py = x, (round(y / 16) + 1) * 16
    if path[0] == 'v':
        a = L.add(91, px + 16, path[1] * 16, 16, 16)
        b = L.add(91, px + 16, path[2] * 16, 16, 16, path=a)
    else:
        a = L.add(91, px + 16 + path[1] * 16, py, 16, 16)
        b = L.add(91, px + 16 + path[2] * 16, py, 16, 16, path=a)
    L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]
    L.add(137, px, py, 48, 16, path=a)  # 3 wide, like the NES lifts


# the pulley (balance) lifts are pairs moving in opposite directions, like 3-3
MOVE = {48: ('v', 9, 3), 55: ('v', 3, 9), 58: ('v', 6, 13), 62: ('h', 3, -3), 80: ('v', 10, 3), 88: ('v', 3, 10),
        91: ('v', 10, 3), 96: ('v', 3, 10), 102: ('v', 10, 3), 108: ('v', 3, 10), 136: ('h', 3, -3)}
for x, y, w in sprites.lifts(img):
    lift(x, y, MOVE[x // 16])

for d in (152, 154, 156):
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-4-4-begin')
L.save('level-4-3-game.json')
