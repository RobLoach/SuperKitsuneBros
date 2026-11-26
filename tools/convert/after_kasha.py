"""Lakitus become kashas (they float and throw skulls, as Lakitu throws Spinies), in place of the kite ninjas.
Edits only those objects in the finished maps, so every file keeps its formatting; gen.py's ENEMY 'lakitu' and
gen41/gen61 make kashas from a rebuild, so this then finds nothing to do."""
import json, re
from paths import ROOT

KASHA, W, H = 123, 32, 32  # kasha-left
KITE = (156, 157)  # kite ninja, the old stand-in
MAPS = ('level-4-1-game', 'level-6-1-game', 'level-8-2-game')


def span(s, oid):
    """start and end of the object with id oid (skipping layers with the same id)"""
    for m in re.finditer(r'"id"\s*:\s*%d\s*,' % oid, s):
        a = s.rindex('{', 0, m.start())
        b = s.index('}', m.end())
        if s.find('{', m.end(), b) != -1:  # the object has properties: its closing brace is after them
            b = s.index('}', s.index(']', m.end()))
        if re.search(r'"gid"\s*:', s[a:b]):
            return a, b


def main():
    for name in MAPS:
        path = f'{ROOT}/{name}.json'
        objs = [o for l in json.load(open(path))['layers'] if l['type'] == 'objectgroup' for o in l['objects']]
        n = 0
        for o in objs:
            if o.get('gid') in KITE:
                x = o['x'] + (o['width'] - W) / 2  # same middle, same bottom
                s = open(path).read()
                a, b = span(s, o['id'])
                obj = s[a:b]
                for k, v in dict(gid=KASHA, width=W, height=H, x=int(x) if x == int(x) else x).items():
                    obj = re.sub(r'("%s"\s*:\s*)[-\d.]+' % k, lambda g: g.group(1) + str(v), obj)
                open(path, 'w').write(s[:a] + obj + s[b:])
                n += 1
        print(name[6:9], n, 'kashas')


if __name__ == '__main__':
    main()
