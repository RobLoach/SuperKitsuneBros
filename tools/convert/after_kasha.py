"""Hammer Bros become kashas (they throw skulls), and each NES pair shares an activation group so both start together.
Edits only those objects in the finished maps, so every file keeps its formatting."""
import json, re
from paths import ROOT

KASHA, W, H = 123, 32, 32  # kasha-left; gen.py's ENEMY 'hammer' makes these from a rebuild
ARCHER = 79  # the old stand-in
# map: Hammer Bros by (middle x, bottom y), a list per NES pair
HAMMERS = {'level-3-1-game': [[(1816, 320), (1864, 384)]],
           'level-5-2-game': [[(744, 336)], [(1304, 320)], [(1928, 320), (1992, 256)]],
           'level-7-1-game': [[(1366, 144), (1396, 80)], [(2168, 208), (2200, 144)]],
           'level-8-3-game': [[(1016, 208), (1048, 144)], [(1880, 144), (1912, 208)]],
           'level-8-4-game': [[(4376, 208)]]}


def span(s, oid):
    """start and end of the object with id oid (skipping layers with the same id)"""
    for m in re.finditer(r'"id"\s*:\s*%d\s*,' % oid, s):
        a = s.rindex('{', 0, m.start())
        b = s.index('}', m.end())
        if s.find('{', m.end(), b) != -1:  # the object has properties: its closing brace is after them
            b = s.index('}', s.index(']', m.end()))
        if re.search(r'"gid"\s*:', s[a:b]):
            return a, b


def set_group(obj, value):
    """add a string group property to the object text, in the file's own style"""
    if re.search(r'"name"\s*:\s*"group"', obj):
        return re.sub(r'("name"\s*:\s*"group"\s*,\s*"type"\s*:\s*"string"\s*,\s*"value"\s*:\s*)"[^"]*"',
                      lambda g: g.group(1) + json.dumps(value), obj)
    sep = ': ' if '": ' in obj else ':'
    line = re.search(r'\n([ \t]*)"name"\s*:\s*"[^"]*",', obj)
    ind = line.group(1)
    entry = (f'{ind} {{\n{ind}  "name"{sep}"group",\n{ind}  "type"{sep}"string",\n'
             f'{ind}  "value"{sep}{json.dumps(value)}\n{ind} }}')
    if '"properties"' in obj:
        end = obj.index(']', obj.index('"properties"'))
        return obj[:end].rstrip() + ',\n' + entry + '\n' + ind + obj[end:].lstrip()
    return obj[:line.end()] + f'\n{ind}"properties"{sep}[\n{entry}\n{ind}],' + obj[line.end():]


def edit(path, oid, fields, group):
    s = open(path).read()
    a, b = span(s, oid)
    obj = s[a:b]
    for k, v in fields.items():
        obj = re.sub(r'("%s"\s*:\s*)[-\d.]+' % k, lambda g: g.group(1) + str(v), obj)
    if group:
        obj = set_group(obj, group)
    open(path, 'w').write(s[:a] + obj + s[b:])


def main():
    for name, pairs in HAMMERS.items():
        path = f'{ROOT}/{name}.json'
        objs = [o for l in json.load(open(path))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
        lv = name[6:9]
        n = 0
        for pair in pairs:
            n += len(pair) > 1
            group = f'hammer-{lv}-{n}' if len(pair) > 1 else None  # a lone Hammer Bro needs no group
            for mx, y in pair:
                o = next(o for o in objs if o.get('gid') in (ARCHER, KASHA) and o['y'] == y and abs(o['x'] + o['width'] / 2 - mx) < 1)
                x = mx - W / 2
                edit(path, o['id'], dict(gid=KASHA, width=W, height=H, x=int(x) if x == int(x) else x), group)
            print(lv, 'kasha', len(pair), group or '')


if __name__ == '__main__':
    main()
