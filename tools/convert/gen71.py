from paths import NES
import numpy as np
from PIL import Image
from gen import GREY_PIPES, cannons, overworld, extend_down, underground

W = 208
L = overworld('7-1', 0, W, legend=('7-1', 'B71'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True, recolor=GREY_PIPES)
img = np.array(Image.open(f'{NES}/7-1.png').convert('RGB'))[:240, :W * 16]
head = np.array(Image.open(f'{NES}/5-1.png').convert('RGB'))[11 * 16:12 * 16, 111 * 16:112 * 16]
print('cannons', cannons(L, img, head))
L.set(93, 5, (0, 0, 0, 0))  # hidden 1-up, the earth power-up like 1-1
L.add(60, 93 * 16, 6 * 16, 16, 40)
for y in (11, 12):  # springboard, a lift instead like 2-1 and 3-1
    L.set(151, y, (0, 0, 0, 0))
extend_down(L)
a = L.add(91, 151.5 * 16, 2.5 * 16, 16, 16)
b = L.add(91, 151.5 * 16, 13 * 16, 16, 16)
for o, t in ((L.objects[-2], b), (L.objects[-1], a)):
    o['properties'] = [{'name': 'path', 'type': 'object', 'value': t}]
L.add(136, 151 * 16, 13 * 16, 32, 16, path=a)
L.add(30, 185 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-7-2-begin')
L.add(131, 93 * 16, 10 * 16, 32, 16, disableInventory=True, zoneTo='level-7-1-underground')
L.add(153, 115 * 16, 11 * 16, 32, 16)
L.save('level-7-1-game.json')

# coin room, NES columns 100 to 116 at map columns 6 to 22
underground('level-7-1-underground.json', 'level-2-1-underground.json', [
    '#######..............PP#######',
    '#######..............PP#######',
    '#######...#######....PP#######',
    '#######..............PP#######',
    '#######..............PP#######',
    '#######....ooooo.....PP#######',
    '#######..............PP#######',
    '#######...ooooooo....PP#######',
    '#######..............PP#######',
    '#######...ooooooo....LL#######',
    '#######...#######........#####',
    '#######...#######........#####',
    '#######...#######........#####',
    '==============================',
    '==============================',
    '==============================',
    '==============================',
], {'customIndicator': '7-1', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-7-1-game', 115.5, 9))
