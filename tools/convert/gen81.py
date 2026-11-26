from paths import NES
from gen import overworld, extend_down, flag, underground

W = 400
L = overworld('8-1', 0, W, legend=('8-1', 'B81'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True)
extend_down(L)
L.add(131, 104 * 16, 9 * 16, 32, 16, disableInventory=True, zoneTo='level-8-1-underground')
L.add(153, 115 * 16, 11 * 16, 32, 16)
L.add(30, 382 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-8-2-begin')
L.save('level-8-1-game.json')

# coin room, NES columns 100 to 116 at map columns 6 to 22
underground('level-8-1-underground.json', 'level-2-1-underground.json', [
    '#######..............PP#######',
    '#######..............PP#######',
    '#######..############PP#######',
    '#######..############PP#######',
    '#######..############PP#######',
    '#######..############PP#######',
    '#######............##PP#######',
    '#######............##PP#######',
    '#######...oooooooo.##PP#######',
    '#######..#########o##LL#######',
    '#######............##....#####',
    '#######..................#####',
    '#######..ooooooooo.......#####',
    '==============================',
    '==============================',
    '==============================',
    '==============================',
], {'customIndicator': '8-1', 'music': 'music-underground'}, (8, 1), (21, 10, 'level-8-1-game', 115.5, 9))
