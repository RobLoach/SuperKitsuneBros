"""the Bowser bridge collapses when the player reaches the axe: the bridge cells move into their own block layer
with a layer script, dropped by a layerscript trigger over the axe platform (like the Crusher 1 trigger in the
game's g-4.json). Edits the finished castle maps in place, keeping the rest of each file as it is."""
import json, re
from paths import ROOT
from textedit import set_cells

BRIDGE = (4923, 4924)  # bridge tiles, drawn in the background over a 5901 in Blocks
ROW = 10
LAYER = 'Bridge'
FUNC = 'collapse'
# wait until triggered, then drop out of the map; moveAnchored off so Bowser falls into the lava instead of riding it
MOVEMENT = f'end\n\nfunc {FUNC}\ndown 8 1 quad in\nend\n'


def block(s, a):
    """end (exclusive) of the {...} starting at s[a]"""
    depth, i, instr = 0, a, False
    while True:
        c = s[i]
        if instr:
            if c == '\\':
                i += 1
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if not depth:
                return i + 1
        i += 1


def indent(s, a):
    return s[s.rindex('\n', 0, a) + 1:a]


def find(s, key, value):
    """start of the {...} that holds "key": value"""
    m = re.search(r'"%s"\s*:\s*%s\s*,' % (key, re.escape(json.dumps(value))), s)
    return s.rindex('{', 0, m.start())


def setkey(t, key, value):
    return re.sub(r'("%s"\s*:\s*)("(?:[^"\\]|\\.)*"|[-\d.]+|true|false)' % key, lambda g: g.group(1) + json.dumps(value), t, count=1)


def props(t, items, sep):
    """replace the properties of the object or layer text t with items [(name, type, value)], in t's style"""
    a = t.index('{', re.search(r'"properties"\s*:\s*\[', t).end())
    b = block(t, a)
    one = t[a:b]
    end = t.rindex('}', 0, t.index(']', b)) + 1  # after the last entry
    entries = [setkey(setkey(setkey(one, 'name', n), 'type', ty), 'value', v) for n, ty, v in items]
    return t[:a] + (sep + '\n' + indent(t, a)).join(entries) + t[end:]


def main():
    for world in range(1, 9):
        path = f'{ROOT}/level-{world}-4-game.json'
        s = open(path).read()
        m = json.loads(s)
        if any(l['name'] == LAYER for l in m['layers']):
            print(f'{world}-4 already split')
            continue
        W = m['width']
        L = {l['name']: l for l in m['layers']}
        bg, bl = L['Background No Parallax']['data'], L['Blocks']['data']
        cols = [c for c in range(W) if bg[ROW * W + c] in BRIDGE]
        x0, x1 = cols[0], cols[-1]
        assert cols == list(range(x0, x1 + 1)) and all(bl[ROW * W + c] for c in cols), world
        assert all(bl[r * W + c] for r in (ROW - 1, ROW) for c in (x1 + 1, x1 + 2, x1 + 3)), world  # the axe platform
        cells = {ROW * W + c: bg[ROW * W + c] for c in cols}
        set_cells(path, 'Background No Parallax', {i: 0 for i in cells})
        set_cells(path, 'Blocks', {i: 0 for i in cells})

        s = open(path).read()
        tiled = re.search(r'"height":\d', s) is not None  # Tiled's own format, else json.dumps(indent=1)
        sep = ', ' if tiled else ','
        lid, oid = m['nextlayerid'], m['nextobjectid']

        # the new layer: a copy of Blocks right after it, so it is a block layer before Coins and Objects
        a = find(s, 'name', 'Blocks')
        b = block(s, a)
        t = s[a:b]
        d = re.search(r'"data"\s*:\s*\[', t).end()
        e = t.index(']', d)
        nums = iter(range(W * m['height']))
        t = t[:d] + re.sub(r'\d+', lambda g: str(cells.get(next(nums), 0)), t[d:e]) + t[e:]
        t = setkey(setkey(setkey(t, 'id', lid), 'name', LAYER), 'opacity', 1)
        t = props(t, [('blocks', 'bool', True), ('moveAnchored', 'bool', False), ('movement', 'string', MOVEMENT)], sep)
        s = s[:b] + sep + '\n' + indent(s, a) + t + s[b:]

        # the trigger: a rectangle over the right of the axe platform, from the top of the map down to its floor,
        # so the player is standing on solid ground past the bridge when it falls
        a = find(s, 'name', 'zoneTo')
        a = s.rindex('{', 0, s.rindex('"properties"', 0, a))  # the door holding that property
        b = block(s, a)
        t = re.sub(r'"gid"\s*:\s*\d+,\s*', '', s[a:b], count=1)
        for k, v in (('height', (ROW - 1) * 16), ('id', oid), ('width', 32), ('x', (x1 + 2) * 16), ('y', 0)):
            t = setkey(t, k, v)
        t = props(t, [('scriptFunc', 'string', FUNC), ('targetLayer', 'string', LAYER), ('trigger', 'string', 'layerscript')], sep)
        # appended after the last object, so bowsers.py still finds Bowser before this gid-less one
        e = re.search(r'"objects"\s*:\s*\[', s).end()
        while s[e:].lstrip()[0] in '{,':
            e = block(s, s.index('{', e))
        s = s[:e] + sep + '\n' + indent(s, a) + t + s[e:]

        s = re.sub(r'("nextlayerid"\s*:\s*)\d+', lambda g: g.group(1) + str(lid + 1), s)
        s = re.sub(r'("nextobjectid"\s*:\s*)\d+', lambda g: g.group(1) + str(oid + 1), s)
        open(path, 'w').write(s)
        print(f'{world}-4 bridge {x0}-{x1}, layer {lid}, trigger {oid}')


if __name__ == '__main__':
    main()
