"""lifts that wait for the player (pathWait), like the NES: SMB's seven Flimsy Lifts (3-3, 6-3, 7-4) sink once stood on
and fall away below the level, the Coin Heaven cloud lifts only set off when landed on, and the lifts standing in for
springboards only rise once stepped on. Edits the finished maps in place, keeping
their formatting, and can be run again. Lifts are found by map, gid and position, not by object id."""
import json, re
from paths import ROOT
from textedit import set_object

# map: [(gid, column, bottom row)] of the platforms, as the generators place them
FALL = {'level-3-3-game': [(137, 60, 7)],  # the one in the middle, where the NES has it
        'level-6-3-game': [(136, 141, 8), (136, 145, 7), (136, 149, 9), (136, 153, 8)],  # the four before the flag
        'level-7-4-game': [(136, 18, 8), (136, 22, 9)]}  # over the lava, with a Podoboo between them
WAIT = [('level-3-1-game', 136, 143, 7), ('level-5-2-game', 136, 97, 7), ('level-6-2-game', 136, 93, 7),  # the cloud lifts: still go back and forth once started
        # springboards: the lift rises when stepped on, then keeps going up and down
        ('level-2-1-game', 136, 186, 13), ('level-3-1-game', 136, 126, 24), ('level-5-2-game', 136, 25, 24),
        ('level-6-3-game', 136, 38, 13), ('level-6-3-game', 136, 116, 13), ('level-7-1-game', 136, 151, 13),
        ('level-8-2-game', 136, 44, 13)]


def span(s, oid):
    """start and end of the object with id oid in the map text"""
    m = re.search(r'"id"\s*:\s*%d\s*,' % oid, s)
    a, depth = m.start(), 0
    while True:  # back to the object's opening brace
        a -= 1
        depth += {'}': 1, '{': -1}.get(s[a], 0)
        if depth < 0:
            break
    b, depth = a, 0
    while True:
        depth += {'{': 1, '}': -1}.get(s[b], 0)
        b += 1
        if depth == 0:
            return a, b


def set_properties(path, oid, props):
    """replace the properties of the object with id oid (props: {name: (type, value)}, None to remove one),
    written in the file's own style"""
    s = open(path).read()
    a, b = span(s, oid)
    obj = s[a:b]
    m = re.search(r'"properties"\s*:\s*\[', obj)
    if not m:  # only removing from an object without properties (a second run)
        assert all(v is None for v in props.values())
        return
    e = m.end() + obj[m.end():].index(']')  # property values here are never lists
    cur = {p['name']: (p['type'], p['value']) for p in json.loads(obj[m.end() - 1:e + 1])}
    for k, v in props.items():
        if v is None:
            cur.pop(k, None)
        else:
            cur[k] = v
    if not cur:  # drop the key and one of the commas around it
        g = re.search(r',\s*$', obj[:m.start()])
        if g:
            obj = obj[:g.start()] + obj[e + 1:]
        else:
            obj = obj[:m.start()] + re.sub(r'^\s*,', '', obj[e + 1:], count=1)
    else:
        line = obj[:m.start()].rsplit('\n', 1)[-1]  # indent of "properties"
        step = re.search(r'\n(\s+)"', obj).group(1)[len(re.search(r'^\s*', s[s.rindex('\n', 0, a) + 1:]).group(0)):]
        i1, i2 = line + step, line + step * 2
        items = []
        for k in sorted(cur):
            t, v = cur[k]
            items.append(i1 + '{\n' + ',\n'.join(i2 + json.dumps(n) + ': ' + json.dumps(x)
                                                 for n, x in (('name', k), ('type', t), ('value', v))) + '\n' + i1 + '}')
        obj = obj[:m.end()] + '\n' + ',\n'.join(items) + '\n' + line + obj[e:]
    open(path, 'w').write(s[:a] + obj + s[b:])


def lift(m, gid, col, bottom):
    objs = {o['id']: o for l in m['layers'] if l['type'] == 'objectgroup' for o in l['objects']}
    o = next(o for o in objs.values() if o.get('gid') == gid and o['x'] == col * 16 and o['y'] == bottom * 16)
    a = next(p['value'] for p in o['properties'] if p['name'] == 'path')
    b = next(p['value'] for p in objs[a]['properties'] if p['name'] == 'path')
    return o, a, b


def main():
    for name, lifts in FALL.items():
        path = f'{ROOT}/{name}.json'
        for gid, col, bottom in lifts:
            o, a, b = lift(json.load(open(path)), gid, col, bottom)
            x = o['x'] + o['width'] // 2 - 8
            # sink a tile slowly, then fall out of the map and stay there, like the game's own falling platforms
            set_object(path, a, x=x, y=o['y'] + 16)
            set_object(path, b, x=x, y=(json.load(open(path))['height'] + 3) * 16)
            set_properties(path, o['id'], {'pathWait': ('bool', True), 'pathSpeed': ('float', 0.5)})
            set_properties(path, a, {'path': ('object', b), 'pathSpeed': ('float', 1)})
            set_properties(path, b, {'path': None})
            print(name, col, 'falls')
    for name, gid, col, bottom in WAIT:
        path = f'{ROOT}/{name}.json'
        o, a, b = lift(json.load(open(path)), gid, col, bottom)
        set_properties(path, o['id'], {'pathWait': ('bool', True)})
        print(name, col, 'waits')


if __name__ == '__main__':
    main()
