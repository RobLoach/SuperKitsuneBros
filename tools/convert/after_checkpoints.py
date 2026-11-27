"""SMB's halfway points: a Kitsune checkpoint (gid 105) at the halfway page of each x-1, x-2 and x-3 level, so dying
after passing it restarts there. Castles and World 8 have none, as on the NES. Edited into the finished maps as text,
so the hand-made World 1 and 2 maps keep their Tiled formatting. Running it again changes nothing."""
import json, re
from paths import ROOT

# level: (map holding the halfway point, NES column) - the column is the start of the halfway page (page * 16) from
# SMB's HalfwayPageNybbles, counted in the level's main area (underground for 1-2 and 4-2, underwater for 2-2 and 7-2)
HALFWAY = {'1-1': ('level-1-1-game', 5 * 16), '1-2': ('level-1-2-underground', 6 * 16), '1-3': ('level-1-3-game', 4 * 16),
           '2-1': ('level-2-1-game', 6 * 16), '2-2': ('level-2-2-underwater', 5 * 16), '2-3': ('level-2-3-game', 7 * 16),
           '3-1': ('level-3-1-game', 6 * 16), '3-2': ('level-3-2-game', 6 * 16), '3-3': ('level-3-3-game', 4 * 16),
           '4-1': ('level-4-1-game', 6 * 16), '4-2': ('level-4-2-underground', 6 * 16), '4-3': ('level-4-3-game', 4 * 16),
           '5-1': ('level-5-1-game', 6 * 16), '5-2': ('level-5-2-game', 6 * 16), '5-3': ('level-5-3-game', 4 * 16),
           '6-1': ('level-6-1-game', 6 * 16), '6-2': ('level-6-2-game', 6 * 16), '6-3': ('level-6-3-game', 6 * 16),
           '7-1': ('level-7-1-game', 6 * 16), '7-2': ('level-7-2-underwater', 5 * 16), '7-3': ('level-7-3-game', 7 * 16)}
CHECKPOINT = 105  # 32x64, standing on the floor


def floor(m, x):
    """the first column from x on with a floor and the lowest row that is solid under both of the checkpoint's columns with 4 open rows above it (maps that grew
    coin heaven rows on top keep the level at the bottom, so this needs no row shift)"""
    W, H = m['width'], m['height']
    solid = [0] * (W * H)
    for l in m['layers']:
        if l['type'] == 'tilelayer' and any(p['name'] == 'blocks' and p['value'] for p in l.get('properties', [])):
            solid = [a or b for a, b in zip(solid, l['data'])]
    for x in range(x, x + 16):  # over a gap: the next floor on the halfway page
        for r in range(H - 1, 3, -1):
            if all(solid[r * W + c] and not any(solid[y * W + c] for y in range(r - 4, r)) for c in (x, x + 1)):
                return x, r
    raise ValueError(f'no floor at column {x}')


def add_object(path, fields):
    """insert an object first in the object layer and bump nextobjectid, in the file's own style"""
    s = open(path).read()
    m = re.search(r'"objects"(\s*):(\s*)\[(\s*)\{', s)
    tiled = m.group(2) == ''  # Tiled writes "key":value, the generators "key": value
    ind = m.group(3).split('\n')[-1]
    sep = ':' if tiled else ': '
    body = ',\n'.join(f'{ind} "{k}"{sep}{json.dumps(v)}' for k, v in sorted(fields.items()))
    text = f'{ind}{{\n{body}\n{ind}}},' + (' ' if tiled else '') + '\n'
    a = m.end() - len(ind) - 1
    s = s[:a] + text + s[a:]
    s = re.sub(r'("nextobjectid"\s*:\s*)(\d+)', lambda g: g.group(1) + str(fields['id'] + 1), s)
    open(path, 'w').write(s)


def main():
    for lv, (name, x) in HALFWAY.items():
        path = f'{ROOT}/{name}.json'
        m = json.load(open(path))
        if any(o.get('gid') == CHECKPOINT for l in m['layers'] if l['type'] == 'objectgroup' for o in l['objects']):
            continue
        x, r = floor(m, x)
        oid = max([m['nextobjectid']] + [o['id'] + 1 for l in m['layers'] if l['type'] == 'objectgroup' for o in l['objects']])
        add_object(path, {'gid': CHECKPOINT, 'height': 64, 'id': oid, 'name': '', 'rotation': 0, 'type': '',
                          'visible': True, 'width': 32, 'x': x * 16, 'y': r * 16})
        print(lv, name, 'column', x, 'floor row', r)


if __name__ == '__main__':
    main()
