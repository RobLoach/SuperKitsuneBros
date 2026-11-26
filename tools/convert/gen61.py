from gen import overworld, extend_down, flag

W = 208
L = overworld('6-1', 0, W, legend=('6-1', 'B61'), tileset='tileset-night.png', qref=('6-1', 0, 17, 9), fresh=True)
L.set(90, 8, (0, 0, 0, 0))  # hidden 1-up, the earth power-up like 1-1
L.add(60, 90 * 16, 9 * 16, 16, 40)
flag(L, 185, green=True)
extend_down(L)
L.add(30, 194 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-6-2-begin')
L.save('level-6-1-game.json')
