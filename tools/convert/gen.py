"""Generate Super Kitsune Bros maps from nesmaps.com images.

Tiles are classified by match.classify (learned from World 2), sprites by
sprites.find (legend templates). Per-level tweaks live in levels.py.
"""
from paths import NES, ROOT
import json, re, copy
import numpy as np
from PIL import Image
from match import classify, cell
import sprites

LAYERS = ('Background No Parallax', 'Blocks', 'Coins', 'Foreground')
H = 17


def dumps(m):
    s = json.dumps(m, indent=1, ensure_ascii=False)
    W = None

    def rows(match):
        nums = [x.strip() for x in match.group(1).split(',')]
        w = rows.width
        lines = [', '.join(nums[i:i + w]) for i in range(0, len(nums), w)]
        return '"data": [' + ',\n            '.join(lines) + ']'
    out = []
    # widths differ per layer only by map width, all tile layers are map-wide
    rows.width = m['width']
    s = re.sub(r'"data": \[([\d,\s]*?)\]', rows, s)
    return s + '\n'


def obj(oid, gid, x, y, w, h, **props):
    o = {'gid': gid, 'height': h, 'id': oid, 'name': '', 'rotation': 0, 'type': '', 'visible': True, 'width': w, 'x': x, 'y': y}
    if props:
        ty = {bool: 'bool', int: 'int', float: 'float', str: 'string'}
        o['properties'] = [{'name': k, 'type': 'object' if k == 'path' else ty[type(v)], 'value': v} for k, v in sorted(props.items())]
    o = dict(sorted(o.items()))
    return o


class Level:
    def __init__(self, template, width):
        self.m = copy.deepcopy(json.load(open(f'{ROOT}/{template}')))
        self.W = width
        self.m['width'] = width
        self.layers = {}
        for l in self.m['layers']:
            if l['type'] == 'tilelayer':
                l['width'] = width
                l['data'] = [0] * (width * H)
                self.layers[l['name']] = l['data']
            elif l['type'] == 'objectgroup':
                l['objects'] = []
                self.objects = l['objects']
        self.nextid = 1

    def set(self, x, y, tup):
        for name, g in zip(LAYERS, tup):
            if name in self.layers:
                self.layers[name][y * self.W + x] = g

    def get(self, x, y):
        return tuple(self.layers[n][y * self.W + x] if n in self.layers else 0 for n in LAYERS)

    def add(self, gid, x, y, w, h, **props):
        o = obj(self.nextid, gid, x, y, w, h, **props)
        self.nextid += 1
        self.objects.append(o)
        return o['id']

    def prop(self, name, value=None, delete=False):
        ps = self.m['properties']
        ps[:] = [p for p in ps if p['name'] != name]
        if not delete:
            ty = {bool: 'bool', int: 'int', str: 'string'}[type(value)]
            ps.append({'name': name, 'type': ty, 'value': value})
            ps.sort(key=lambda p: p['name'])

    def grow_top(self, n):
        """add n empty rows above the map, moving everything down"""
        for l in self.m['layers']:
            if l['type'] == 'tilelayer':
                l['data'][:0] = [0] * (n * self.W)
                l['height'] += n
                self.layers[l['name']] = l['data']
        for o in self.objects:
            o['y'] += n * 16
        self.m['height'] += n
        self.H = self.m['height']

    def save(self, path):
        self.m['nextobjectid'] = self.nextid
        open(f'{ROOT}/{path}', 'w').write(dumps(self.m))


def from_image(lv, band, width, x0=0, db='over', night=True):
    """classify every cell of the nesmaps band into layer tuples"""
    im = Image.open(f'{NES}/{lv}.png').convert('RGB').crop((x0 * 16, band, (x0 + width) * 16, band + 240))
    grid = {}
    unknown = []
    kinds = {}
    for y in range(15):
        for x in range(width):
            v, k = classify(cell(im, x, y), db, night)
            kinds[x, y] = k
            if v is None:
                unknown.append((x, y))
                v = (0, 0, 0, 0)
            grid[x, y] = v
    # cells partly covered by a sprite: copy a neighbour whose lower part looks the same
    a = np.array(im)
    px = lambda x, y: a[y * 16 + 4:y * 16 + 16, x * 16:x * 16 + 16]
    for x, y in list(unknown):
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y + 1)):
            if (nx, ny) in grid and (nx, ny) not in unknown and grid[nx, ny] != (0, 0, 0, 0) and (px(x, y) == px(nx, ny)).all():
                grid[x, y] = grid[nx, ny]
                unknown.remove((x, y))
                break
    # mostly covered by a sprite: copy the most similar known neighbour
    full = lambda x, y: a[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
    for x, y in list(unknown):
        best = None
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in grid and (nx, ny) not in unknown:
                same = (full(x, y) == full(nx, ny)).all(2).mean()
                if same >= 0.6 and (best is None or same > best[0]):
                    best = (same, grid[nx, ny])
        if best:
            grid[x, y] = best[1]
            unknown.remove((x, y))
    from_image.kinds = kinds
    return grid, unknown, a


def night(L, image='tileset-night-white.png'):
    """black sky: no background and a night copy of the Mario tileset"""
    L.prop('background', delete=True)
    for t in L.m['tilesets']:
        if t.get('image') == 'tileset.png':
            t['image'] = image


def copy_cells(L, src, xs, ys, dx=0):
    m = json.load(open(f'{ROOT}/{src}'))
    W = m['width']
    S = {l['name']: l['data'] for l in m['layers'] if l['type'] == 'tilelayer'}
    for x in xs:
        for y in ys:
            L.set(x + dx, y, tuple(S[n][y * W + x] if n in S else 0 for n in LAYERS))


def underground(path, template, rows, props, spawn, exit_):
    """rows: 17 strings of 30 chars. # brick, = floor, o coin, M mushroom brick, P pipe body, L pipe lip"""
    L = Level(template, 30)
    T = {'#': (0, 1234, 0, 5711), '=': (0, 1262, 0, 5712), 'o': (0, 0, 66, 0), 'M': (0, 113, 0, 0),
         'P': (0, 4877, 0, 5784), 'L': (0, 4877, 0, 5816), '.': (0, 0, 0, 0)}
    for y, r in enumerate(rows):
        assert len(r) == 30, (y, len(r))
        for x, ch in enumerate(r):
            v = T[ch]
            if ch == '=' and (y == 0 or rows[y - 1][x] != '='):
                v = (0, 1230, 0, 5712)
            if ch in 'PL' and x > 0 and r[x - 1] == ch:
                v = (v[0], v[1], v[2], v[3] + 1)
            L.set(x, y, v)
    L.add(90, spawn[0] * 16, spawn[1] * 16, 48, 48)
    x, y, zone, zx, zy = exit_
    L.add(153, x * 16, y * 16, 32, 16, zoneTo=zone, zoneX=zx, zoneY=zy)
    for k, v in props.items():
        L.prop(k, v)
    L.save(path)


ENEMY = {'goomba': (36, 48, 32, {'walkOffLedges': True}),  # Goombas walk off ledges like the NES ones
         'koopa': (24, 48, 32, {}), 'paratroopa': (38, 48, 96, {}), 'hammer': (79, 48, 32, {}),
         'lakitu': (156, 48, 48, {}), 'spiny': (48, 16, 32, {'respawn': True}), 'egg': (48, 16, 32, {'respawn': True}),
         'buzzy': (73, 48, 40, {}), 'blooper': (103, 48, 32, {}), 'cheep': (77, 48, 32, {})}
ITEM = {'mushroom': 113, 'star': 100}


def fresh_tiles(L, img, found, unknown, sky, x0=0):
    """cells the World 1 to 3 maps never used (bushes, hills, mushrooms...) become new background tiles"""
    import newtiles
    kinds = from_image.kinds
    boxes = [(x, y, w, h) for n, x, y, w, h, s in found]
    covered = {}
    ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGB'))
    def colors(g):  # colours of a Mario tileset tile
        i = g - 4813
        return {tuple(p) for p in ts[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16].reshape(-1, 3)}
    for (x, y), k in kinds.items():
        v = L.get(x + x0, y)
        if k == 'f' and v != (0, 0, 0, 0) and not v[2]:  # matched in other colours, e.g. bushes as clouds: keep the collision, redraw it
            c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            vis = [g for g in (v[0], v[3]) if g >= 4813]
            if vis and not {tuple(p) for p in c.reshape(-1, 3)} - {tuple(sky)} <= set().union(*map(colors, vis)):
                g = newtiles.gid(c, sky)
                L.set(x + x0, y, (0, v[1], 0, g) if v[3] else (g, v[1], 0, 0))  # same layer, so it still covers the block tile
            continue
        if k != 'n' and (x, y) not in unknown and v != (0, 0, 0, 0):
            continue
        c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
        free = np.ones((16, 16), bool)  # pixels not under a sprite
        for bx, by, bw, bh in boxes:
            free[max(0, by - y * 16):max(0, by + bh - y * 16), max(0, bx - x * 16):max(0, bx + bw - x * 16)] = False
        if not free.all():
            covered[x, y] = free
            continue
        if (c == sky).all():
            continue
        solid = L.get(x + x0, y)[1] if k == 'n' else 0  # same shape as a solid tile, e.g. grey pipes: keep it solid
        L.set(x + x0, y, (newtiles.gid(c, sky), solid, 0, 0))
    # behind a sprite: copy a neighbour that matches the visible part of the cell
    for _ in range(2):
        for (x, y), free in list(covered.items()):
            c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            if free.sum() < 24:
                continue
            for nx, ny in ((x, y + 1), (x - 1, y), (x + 1, y), (x, y - 1)):
                if (nx, ny) in covered or not (0 <= ny < 15 and 0 <= nx < img.shape[1] // 16):
                    continue
                n = img[ny * 16:ny * 16 + 16, nx * 16:nx * 16 + 16]
                if (c[free] == n[free]).all() and (L.get(nx + x0, ny)[0] or L.get(nx + x0, ny)[1]):
                    L.set(x + x0, y, L.get(nx + x0, ny))
                    del covered[x, y]
                    break


GREY_PIPES = {(128, 208, 16): (252, 252, 252), (0, 168, 0): (116, 116, 116), (0, 0, 0): (188, 188, 188)}


def recolor_shapes(L, mapping, x0=0):
    """cells that only matched by shape (e.g. grey pipes) use recoloured copies of the tiles they matched"""
    import newtiles
    for (x, y), k in from_image.kinds.items():
        if k != 'n':
            continue
        v = L.get(x + x0, y)
        new = tuple(newtiles.recolor(g, mapping) if g and i in (0, 3) else g for i, g in enumerate(v))
        if new != v:
            L.set(x + x0, y, new)
            from_image.kinds[x, y] = 'e'


def overworld(lv, band, W, template='level-2-1-game.json', legend=('3-1', 'B31'), tileset='tileset-night-white.png', qref=('3-1', 240, 16, 9), fresh=False, recolor=None):
    """overworld from the nesmaps image: tiles, ? blocks, items and enemies. tileset None keeps the day sky"""
    import sprites
    grid, unknown, img = from_image(lv, band, W, night=bool(tileset))
    found = [(n.replace('_flip', '').rstrip('2'), x, y, w, h, s) for n, x, y, w, h, s in sprites.find(img, sprites.templates(legend[0], getattr(sprites, legend[1])))]
    L = Level(template, W)
    if tileset:
        night(L, tileset)
    L.prop('customIndicator', lv)
    E = (0, 0, 0, 0)
    for (x, y), v in grid.items():
        L.set(x, y, v)
    water(L)
    if recolor:
        recolor_shapes(L, recolor)
    if fresh:
        fresh_tiles(L, img, found, unknown, (0, 0, 0) if tileset else (92, 148, 252))
    for x in range(W):  # hidden blocks, drawn faded on nesmaps (night, day)
        for y in range(15):
            c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            if (c == (100, 38, 6)).all(2).sum() >= 40 or (c == (46, 74, 126)).all(2).sum() >= 30:
                L.set(x, y, (0, 0, 0, 0))
                if (c == (46, 158, 126)).all(2).sum() >= 20:  # a 1-up: the earth power-up, like 1-1
                    L.add(60, x * 16, (y + 1) * 16, 16, 40)
                else:
                    L.add(139, x * 16, (y + 1) * 16, 16, 32, **{'spawn-type': 'coin'})
    qlv, qband, qx, qy = qref  # a plain ? block
    q = np.array(Image.open(f'{NES}/{qlv}.png').convert('RGB'))[qband + qy * 16:qband + qy * 16 + 16, qx * 16:qx * 16 + 16]
    qcells = [(x, y) for x in range(W) for y in range(15) if (img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == q).all()]
    items = {((x + 8) // 16, (y + 8) // 16): n for n, x, y, w, h, s in found if n in ITEM}
    for c, n in items.items():
        L.set(*c, (0, ITEM[n], 0, 0))
    for n, x, y, w, h, s in found:
        if n == 'coin' and fresh:
            L.set((x + w // 2) // 16, (y + h // 2) // 16, (0, 0, 66, 0))
        if n == 'oneup':  # Kitsune has no lives: the earth power-up block, like 1-1 and 2-1
            L.set((x + 8) // 16, (y + 8) // 16, E)
            L.add(60, (x + 8) // 16 * 16, ((y + 8) // 16 + 1) * 16, 16, 40)
    for x, y in qcells:
        if (x, y) not in items:
            L.set(x, y, E)
            L.add(139, x * 16, (y + 1) * 16, 16, 32, **{'spawn-type': 'coin'})
    L.add(90, 32, 208, 48, 48, actor='Mario')
    for n, x, y, w, h, s in found:
        bottom = round((y + h) / 16) * 16
        if n in ENEMY:
            g, ow, oh, props = ENEMY[n]
            L.add(g, x + w // 2 - ow // 2, bottom, ow, oh, **props)  # centred on the NES sprite
        elif n == 'piranha':
            L.add(132, (x // 16) * 16, bottom, 32, 32)
    if fresh:
        fill_hidden(L, img, found)
    L.found, L.img = found, img
    print(lv, 'unknown', unknown)
    print(lv, '? blocks', qcells, 'items', items)
    return L


WATER_TOP, WATER = 5453, 5454


def water(L):
    """the water surface matches 2-4's lava: fake water tiles over a pit, like the water in 2-3"""
    for x in range(L.W):
        for y in range(15):
            if L.get(x, y)[0] in (4925, 4957):
                L.set(x, y, (WATER_TOP, 0, 0, 0))
                for y2 in range(y + 1, 15):
                    if L.get(x, y2) == (0, 0, 0, 0) or L.get(x, y2)[0] in (4925, 4957):
                        L.set(x, y2, (WATER, 0, 0, 0))
                break


def extend_down(L):
    """NES has 15 rows, the map 17: repeat the bottom row"""
    for x in range(L.W):
        for y in (15, 16):
            L.set(x, y, L.get(x, 14))


TILE = lambda col, row: 4813 + row * 32 + col  # Mario tileset gid
DECO = [(11, 11), (11, 12), (13, 10), (13, 11), (14, 12), (77, 8)]  # 3-1 cells, see addtiles.py
FLAG_CELLS = [(0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4), (1, 5)]  # see addtiles.py


def flag(L, x0, green=False, day=False, red=False):
    """NES flagpole: x0 is the column left of the pole, tiles in tileset row 21"""
    ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
    for x in (x0, x0 + 1):
        for y in range(12):
            if L.get(x, y)[0] in (4814, 4815, 4846, 4847, 4879) or TILE(0, 21) <= L.get(x, y)[0] < TILE(0, 22):
                L.set(x, y, (0, 0, 0, 0))
    for i, (dx, dy) in enumerate(FLAG_CELLS + [(1, y) for y in range(6, 12)]):
        col = (24 if red else 16 if day else 8 if green else 0) + min(i, 6)
        if ts[21 * 16:22 * 16, col * 16:col * 16 + 16, 3].any():
            v = L.get(x0 + dx, dy)
            L.set(x0 + dx, dy, (TILE(col, 21),) + v[1:])


def deco(L, lv, band):
    """snowy trees and fences, tiles in tileset row 22, also behind sprites when the rest of the cell matches"""
    import sprites
    img = np.array(Image.open(f'{NES}/{lv}.png').convert('RGB'))[band:band + 240, :L.W * 16]
    ref = np.array(Image.open(f'{NES}/3-1.png').convert('RGB'))[240:480]
    tiles = [ref[y * 16:y * 16 + 16, x * 16:x * 16 + 16] for x, y in DECO]
    boxes = [(x, y, w, h) for n, x, y, w, h, s in sprites.find(img, sprites.templates('3-1', sprites.B31))]
    for y in range(13):
        for x in range(L.W):
            if L.get(x, y) != (0, 0, 0, 0):
                continue
            c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            if not c.any():
                continue
            free = np.ones((16, 16), bool)  # pixels not covered by a sprite
            for bx, by, bw, bh in boxes:
                free[max(0, by - y * 16):max(0, by + bh - y * 16), max(0, bx - x * 16):max(0, bx + bw - x * 16)] = False
            best = None
            for i, t in enumerate(tiles):
                lit = t.any(2) & free
                if lit.sum() < 12:
                    continue
                if (c[free] == t[free]).all(1).mean() >= 0.95 and (c[lit] == t[lit]).all(1).mean() >= 0.95:
                    best = i
                    break
            if best is not None:
                L.set(x, y, (TILE(best, 22), 0, 0, 0))


def cannons(L, img, head):
    """Bullet Bill cannons: solid down to the ground, with a hornet nest firing hornets"""
    out = []
    for x in range(L.W):
        for y in range(15):
            if (img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] == head).all():
                out.append((x, y))
                yy = y
                while yy < 15 and L.get(x, yy)[1] == 0:
                    v = L.get(x, yy)
                    L.set(x, yy, (v[0], 5901, 0, 0))
                    yy += 1
                if not any(ox == x and oy < y for ox, oy in out[:-1]):  # one nest on top of a stacked cannon
                    L.add(43, x * 16 - 16, (y + 1) * 16, 48, 32)
    return out


def flag_image(L, lv, band, x0, sky, x_img=None):
    """the NES flagpole copied cell for cell from the level's image: x0 is the column left of the pole"""
    import newtiles
    xi = x0 if x_img is None else x_img
    img = np.array(Image.open(f'{NES}/{lv}.png').convert('RGB'))[band:band + 240]
    for dx in (0, 1):
        for y in range(12):
            c = img[y * 16:y * 16 + 16, (xi + dx) * 16:(xi + dx) * 16 + 16]
            v = L.get(x0 + dx, y)
            g = 0 if (c == sky).all() else newtiles.gid(c, sky)
            L.set(x0 + dx, y, (g, v[1], v[2], 0))


def fill_hidden(L, img, found, x0=0, rows=range(13)):
    """scenery hidden behind sprites (trees and fences behind Goombas...): learnt from the rest of the level,
    a cell between two fences is a fence, a cell under a tree top is the trunk, and so on"""
    import collections
    ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
    first = TILE(0, 22)  # decorations and copied tiles
    bg = lambda x, y: L.get(x, y)[0] if 0 <= x < L.W and 0 <= y < 17 else 0
    deco = lambda g: g >= first
    boxes = [(x - 6, y - 4, w + 12, h + 8) for n, x, y, w, h, s in found]  # some sprite templates are only part of the sprite
    covered = {}
    for y in rows:
        for x in range(img.shape[1] // 16):
            free = np.ones((16, 16), bool)
            for bx, by, bw, bh in boxes:
                free[max(0, by - y * 16):max(0, by + bh - y * 16), max(0, bx - x * 16):max(0, bx + bw - x * 16)] = False
            if not free.all() and L.get(x + x0, y) == (0, 0, 0, 0):
                covered[x + x0, y] = free
    below, between = collections.Counter(), collections.Counter()
    for y in rows:
        for x in range(L.W):
            if (x, y) in covered or not deco(bg(x, y)):
                continue
            if deco(bg(x, y - 1)) and (x, y - 1) not in covered:
                below[bg(x, y - 1), bg(x, y)] += 1
            if (x - 1, y) not in covered and (x + 1, y) not in covered and deco(bg(x - 1, y)) and deco(bg(x + 1, y)):
                between[bg(x - 1, y), bg(x + 1, y), bg(x, y)] += 1

    def fits(g, x, y):  # the visible part of the cell agrees with the tile
        i = g - 4813
        t = ts[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16]
        c = img[y * 16:y * 16 + 16, (x - x0) * 16:(x - x0) * 16 + 16]
        free = covered[x, y]
        lit = t[..., 3] > 0
        return (c[free & lit] == t[free & lit][:, :3]).all(1).mean() >= 0.8 if (free & lit).any() else True

    for _ in range(3):
        for (x, y) in sorted(covered, key=lambda c: c[1]):
            if bg(x, y):
                continue
            options = [(n, g) for (l, r, g), n in between.items() if l == bg(x - 1, y) and r == bg(x + 1, y)]
            options += [(n, g) for (a, g), n in below.items() if a == bg(x, y - 1) and deco(a)]
            for n, g in sorted(options, reverse=True):
                if n >= 2 and fits(g, x, y):
                    v = L.get(x, y)
                    L.set(x, y, (g,) + v[1:])
                    break


def ropes(L, img, sky, x0=0):
    """pulley ropes and wheels, copied from the image where the map is empty (the lifts themselves are objects)"""
    import newtiles
    import sprites
    lifts = sprites.lifts(img)
    for y in range(15):
        for x in range(img.shape[1] // 16):
            c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            if L.get(x + x0, y) != (0, 0, 0, 0) or (c == (252, 188, 176)).all(2).sum() < 2:
                continue
            if any(lx < x * 16 + 16 and x * 16 < lx + lw and ly < y * 16 + 16 and y * 16 < ly + 8 for lx, ly, lw in lifts):
                continue
            L.set(x + x0, y, (newtiles.gid(c, sky), 0, 0, 0))


def vine(L, col, block, up, heaven, main, sky, zone):
    """the vine from its block up through coin heaven (map grown by `up` rows): press up on it to climb into the clouds"""
    import newtiles
    for r in range(-6, block):
        c = heaven[(r + 15) * 16:(r + 16) * 16, col * 16:(col + 1) * 16] if r < 0 else main[r * 16:(r + 1) * 16, col * 16:(col + 1) * 16]
        if not (c == sky).all():
            L.set(col, r + up, (newtiles.gid(c, sky), 0, 0, 0))
    L.add(30, col * 16, (block + up) * 16, 16, 32, visible=False, zoneTo=zone, zoneX=col + 1.5, zoneY=up - 3)


def redraw_water(m, img, found, water=(32, 56, 236)):
    """underwater maps built from 2-2 use Kitsune's coral and seaweed: redraw every block and plant from the NES image"""
    import newtiles
    W = m['width']
    L = {l['name']: l['data'] for l in m['layers'] if l['type'] == 'tilelayer'}
    bg, blocks, coins = L['Background No Parallax'], L['Blocks'], L['Coins']
    boxes = [(x - 2, y - 2, w + 4, h + 4) for n, x, y, w, h, s in found if n != 'flame']
    flames = [(x, y, w, h) for n, x, y, w, h, s in found if n == 'flame']
    for y in range(2, 15):
        for x in range(min(W, img.shape[1] // 16)):
            i = y * W + x
            c = img[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
            if y == 2 and not blocks[i]:
                continue  # the water surface is its own layer
            if coins[i] or (c == water).all():
                if not blocks[i] and not coins[i]:
                    bg[i] = 0
                continue
            if not blocks[i] and any(bx < x * 16 + 16 and x * 16 < bx + bw and by < y * 16 + 16 and y * 16 < by + bh for bx, by, bw, bh in flames):
                bg[i] = 0  # firebar flames are objects, there is only water behind them
                continue
            if not blocks[i] and any(bx < x * 16 + 16 and x * 16 < bx + bw and by < y * 16 + 16 and y * 16 < by + bh for bx, by, bw, bh in boxes):
                continue  # a fish in front: keep what is there
            bg[i] = newtiles.gid(c, water)
    for y in (15, 16):  # the 2 rows below the NES screen repeat the bottom row
        for x in range(W):
            bg[y * W + x] = bg[14 * W + x]
