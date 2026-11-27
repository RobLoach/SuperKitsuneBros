from paths import NES
import numpy as np
from PIL import Image
from gen import overworld, extend_down, copy_cells, flag, ropes
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
ropes(L, img, (0, 0, 0))  # the pulley ropes and wheels
flag(L, 150, green=True)
extend_down(L)


def lift(x, y, path):
    """moving platform on a 3 wide NES lift, moving between rows path[0] and path[1] (or columns)"""
    px, py = x, (round(y / 16) + 1) * 16
    if path[0] == 'v':
        a = L.add(91, px + 16, path[1] * 16, 16, 16)
        b = L.add(91, px + 16, path[2] * 16, 16, 16, path=a)
    else:
        a = L.add(91, px + 16 + path[1] * 16, py, 16, 16)
        b = L.add(91, px + 16 + path[2] * 16, py, 16, 16, path=a)
    L.objects[-2]['properties'] = [{'name': 'path', 'type': 'object', 'value': b}]
    L.add(137, px, py, 48, 16, path=a)  # 3 wide, like the NES lifts


# the pulley (balance) lifts move in opposite directions; the others are SMB's horizontal lifts (enemy $28 in its
# 3-3 data), which set off to the left and swing back about 3 tiles (the Flimsy Lift at 60 is made by after_liftwait.py)
H = ('h', 0, -3)
MOVE = {30: H, 33: H, 60: ('h', 3, -3), 81: ('v', 10, 4), 88: ('v', 4, 10), 94: H, 96: H, 103: H, 132: H,
        136: ('v', 9, 3), 140: ('v', 3, 9)}
for x, y, w in sprites.lifts(img):
    lift(x, y, MOVE[x // 16])

for d in (156, 158, 160):
    L.add(30, d * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-3-4-begin')
L.set(26, 6, (0, 0, 0, 0))  # a Goomba the sprite search missed, copied as scenery: 3-3 has its enemy there already
L.save('level-3-3-game.json')
