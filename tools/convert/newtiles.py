"""tiles copied from the nesmaps images into tileset row 23 and up, remembered by their pixels"""
from paths import HERE, ROOT
import json, os, hashlib
import numpy as np
from PIL import Image
REG = f'{HERE}/newtiles.json'
FIRST_ROW = 23
SKY = [(92, 148, 252), (0, 0, 0)]  # day and night sky are transparent


def _load():
    return json.load(open(REG)) if os.path.exists(REG) else {}


def gid(cell, sky=None, firstgid=4813):
    """gid in the Mario tileset (firstgid 4813) for a 16x16 RGB cell, adding it to the tilesets when new"""
    c = np.dstack([cell, np.full(cell.shape[:2], 255, np.uint8)])
    if sky is not None:
        c[(cell == sky).all(2)] = 0
    key = hashlib.sha1(c.tobytes()).hexdigest()
    reg = _load()
    if key not in reg:
        taken = {tuple(v) for v in reg.values()}
        i = next(i for i in range(9 * 32) if (i % 32, FIRST_ROW + i // 32) not in taken)
        col, row = i % 32, FIRST_ROW + i // 32
        assert row < 32, 'tileset is full'
        for name in ('tileset.png', 'tileset-night.png', 'tileset-night-white.png'):
            ts = np.array(Image.open(f'{ROOT}/{name}').convert('RGBA'))
            assert not ts[row * 16:row * 16 + 16, col * 16:col * 16 + 16, 3].any(), (name, col, row)
            ts[row * 16:row * 16 + 16, col * 16:col * 16 + 16] = c
            Image.fromarray(ts).save(f'{ROOT}/{name}', optimize=True)
        reg[key] = [col, row]
        json.dump(reg, open(REG, 'w'))
    col, row = reg[key]
    return firstgid + row * 32 + col


def recolor(g, mapping, firstgid=4813):
    """a copy of Mario tileset tile g with some colours swapped, e.g. grey pipes"""
    ts = np.array(Image.open(f'{ROOT}/tileset.png').convert('RGBA'))
    i = g - firstgid
    t = ts[i // 32 * 16:i // 32 * 16 + 16, i % 32 * 16:i % 32 * 16 + 16].copy()
    rgb = t[..., :3].copy()
    hit = False
    for a, b in mapping.items():
        m = (rgb == a).all(2) & (t[..., 3] > 0)
        hit |= m.any() and a != (0, 0, 0)
        t[m, :3] = b
    if not hit:
        return g
    return gid(t[..., :3], None, firstgid) if (t[..., 3] == 255).all() else _put(t, firstgid)


def _put(c, firstgid):
    key = hashlib.sha1(c.tobytes()).hexdigest()
    reg = _load()
    if key not in reg:
        taken = {tuple(v) for v in reg.values()}
        i = next(i for i in range(9 * 32) if (i % 32, FIRST_ROW + i // 32) not in taken)
        col, row = i % 32, FIRST_ROW + i // 32
        assert row < 32, 'tileset is full'
        for name in ('tileset.png', 'tileset-night.png', 'tileset-night-white.png'):
            ts = np.array(Image.open(f'{ROOT}/{name}').convert('RGBA'))
            assert not ts[row * 16:row * 16 + 16, col * 16:col * 16 + 16, 3].any(), (name, col, row)
            ts[row * 16:row * 16 + 16, col * 16:col * 16 + 16] = c
            Image.fromarray(ts).save(f'{ROOT}/{name}', optimize=True)
        reg[key] = [col, row]
        json.dump(reg, open(REG, 'w'))
    col, row = reg[key]
    return firstgid + row * 32 + col
