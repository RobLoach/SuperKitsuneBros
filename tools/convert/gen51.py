from paths import NES
import numpy as np
from PIL import Image
from gen import GREY_PIPES, cannons, overworld, extend_down, flag, underground

W = 224
L = overworld('5-1', 0, W, legend=('5-1', 'B51'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True, recolor=GREY_PIPES)
img = np.array(Image.open(f'{NES}/5-1.png').convert('RGB'))[:240, :W * 16]

print('cannons', cannons(L, img, img[11 * 16:12 * 16, 111 * 16:112 * 16]))
L.set(148, 9, (0, 0, 0, 0))  # hidden 1-up, the earth power-up like 1-1
L.add(60, 148 * 16, 10 * 16, 16, 40)
extend_down(L)
L.add(131, 156 * 16, 7 * 16, 32, 16, disableInventory=True, zoneTo='level-5-1-underground')
L.add(153, 163 * 16, 11 * 16, 32, 16)
L.add(30, 205 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-5-2-begin')
L.save('level-5-1-game.json')

# coin room, the same as the one in 4-2: NES columns 148 to 164 at map columns 6 to 22
underground('level-5-1-underground.json', 'level-2-1-underground.json', [
    '#######..............PP#######',
    '#######..............PP#######',
    '#######...#######....PP#######',
    '#######.........#....PP#######',
    '#######.........#....PP#######',
    '#######....ooooo#....PP#######',
    '#######...#ooooo###..PP#######',
    '#######...#######..o.PP#######',
    '#######..............PP#######',
    '#######..............LL#######',
    '#######..................#####',
    '#######..................#####',
    '#######..................#####',
    '==============================',
    '==============================',
    '==============================',
    '==============================',
], {'customIndicator': '5-1', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-5-1-game', 163.5, 9))
