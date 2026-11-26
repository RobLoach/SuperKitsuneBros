from paths import NES
from gen import overworld, extend_down, flag, underground
W = 240
L = overworld('4-1', 0, W, legend=('4-1', 'B41'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True)
L.set(92, 5, (0, 0, 0, 0))  # hidden 1-up
L.add(60, 92 * 16, 6 * 16, 16, 40)
flag(L, 224, day=True)
extend_down(L)
L.add(131, 132 * 16, 9 * 16, 32, 16, disableInventory=True, zoneTo='level-4-1-underground')
L.add(153, 163 * 16, 11 * 16, 32, 16)
L.add(30, 231 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-4-2-begin')
L.save('level-4-1-game.json')

# bonus room, NES columns 148 to 164 at map columns 6 to 22
underground('level-4-1-underground.json', 'level-2-1-underground.json', [
    '#######..............PP#######',
    '#######..............PP#######',
    '#######..############PP#######',
    '#######..............PP#######',
    '#######..............PP#######',
    '#######..............PP#######',
    '#######..............PP#######',
    '#######..............PP#######',
    '#######..oooooooo....PP#######',
    '#######..########..M.LL#######',
    '#######..#......#........#####',
    '#######..#......#........#####',
    '#######..oooooooooo......#####',
    '==============================',
    '==============================',
    '==============================',
    '==============================',
], {'customIndicator': '4-1'}, (8, 1), (21, 10, 'level-4-1-game', 163.5, 9))
