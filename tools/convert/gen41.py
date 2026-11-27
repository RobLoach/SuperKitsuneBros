from paths import NES
from gen import ENEMY, overworld, extend_down, flag, underground
W = 240
L = overworld('4-1', 0, W, legend=('4-1', 'B41'), tileset=None, qref=('4-1', 0, 25, 5), fresh=True)
flag(L, 224, day=True)
extend_down(L)
lakitus = sorted((o for o in L.objects if o['gid'] == ENEMY['lakitu'][0]), key=lambda o: o['x'])
L.objects[:] = [o for o in L.objects if o not in lakitus[1:]]  # one Lakitu that follows you, as in SMB (the NES map shows it 3 times)
height = lakitus[0]['y']
for x in (52, 78, 156, 182):  # more Spinies dropping from the sky
    L.add(48, x * 16 + 16, height + 32, 16, 32, respawn=True)
L.add(131, 132 * 16, (9 + 1) * 16, 32, 16, disableInventory=True, zoneTo='level-4-1-underground')
L.add(153, 163 * 16, (11 + 1) * 16, 32, 16)
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
