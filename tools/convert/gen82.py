from paths import NES
import numpy as np
from PIL import Image
from gen import cannons, overworld, extend_down, underground, flag_image

W = 240
L = overworld('8-2', 0, W, legend=('8-2', 'B82'), tileset=None, qref=('8-2', 0, 29, 9), fresh=True)
img = np.array(Image.open(f'{NES}/8-2.png').convert('RGB'))[:240, :W * 16]
head = np.array(Image.open(f'{NES}/5-1.png').convert('RGB'))[11 * 16:12 * 16, 111 * 16:112 * 16]
print('cannons', cannons(L, img, head))
L.set(44, 5, (0, 0, 0, 0))  # the 1-up in the long brick row: the earth power-up, like 1-1
L.add(60, 44 * 16, 6 * 16, 16, 40)
for y in (11, 12):  # springboard, a lift instead like 2-1 and 3-1
    L.set(44, y, (0, 0, 0, 0))
flag_image(L, '8-2', 0, 215, (92, 148, 252))  # the NES flagpole
extend_down(L)
a = L.add(91, 44.5 * 16, 2.5 * 16, 16, 16)
b = L.add(91, 44.5 * 16, 13 * 16, 16, 16)
for o, t in ((L.objects[-2], b), (L.objects[-1], a)):
    o['properties'] = [{'name': 'path', 'type': 'object', 'value': t}]
L.add(136, 44 * 16, 13 * 16, 32, 16, path=a)
L.add(131, 156 * 16, (9 + 1) * 16, 32, 16, disableInventory=True, zoneTo='level-8-2-underground')
L.add(153, 163 * 16, (11 + 1) * 16, 32, 16)
L.add(30, 222 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-8-3-begin')
L.save('level-8-2-game.json')

# coin room, the same as 4-2's
underground('level-8-2-underground.json', 'level-2-1-underground.json', [
    '#######..............PP#######', '#######..............PP#######', '#######...#######....PP#######', '#######.........#....PP#######',
    '#######.........#....PP#######', '#######....ooooo#....PP#######', '#######...#ooooo###..PP#######', '#######...#######..o.PP#######',
    '#######..............PP#######', '#######..............LL#######'] + ['#######..................#####'] * 3 + ['=' * 30] * 4,
    {'customIndicator': '8-2', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-8-2-game', 163.5, 9))
