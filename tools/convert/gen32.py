from gen import overworld, extend_down, copy_cells, flag, deco, fill_hidden
L = overworld('3-2', 0, 224)
flag(L, 208)
deco(L, '3-2', 0)
fill_hidden(L, L.img, L.found)
extend_down(L)
L.add(30, 215 * 16, 13 * 16, 16, 32, alwaysActive=True, visible=False, zoneTo='level-3-3-begin')
L.save('level-3-2-game.json')
