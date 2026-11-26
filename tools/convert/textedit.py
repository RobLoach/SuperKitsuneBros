"""edit tiles in maps that weren't generated here (Worlds 1 and 2), keeping the rest of the file as it is"""
import json, re


def set_cells(path, layer, cells):
    """cells: {index: gid} in the named tile layer"""
    s = open(path).read()
    m = json.loads(s)
    layers = [l for l in m['layers'] if l['type'] == 'tilelayer']
    k = next(i for i, l in enumerate(layers) if l['name'] == layer)
    a = [m_.end() for m_ in re.finditer(r'"data"\s*:\s*\[', s)][k]
    b = s.index(']', a)
    out, last = s[:a], 0
    for i, n in enumerate(re.finditer(r'\d+', s[a:b])):
        if i in cells:
            out += s[a + last:a + n.start()] + str(cells[i])
            last = n.end()
    open(path, 'w').write(out + s[a + last:])


def set_object(path, oid, **fields):
    """change number fields (gid, x, width...) of the object with id oid"""
    s = open(path).read()
    m = re.search(r'"id"\s*:\s*%d\s*,' % oid, s)
    a = s.rindex('{', 0, m.start())
    b = s.index('}', m.end())
    if s.find('{', m.end(), b) != -1:  # the object has properties: its closing brace is after them
        b = s.index('}', s.index(']', m.end()))
    obj = s[a:b]
    for k, v in fields.items():
        obj = re.sub(r'("%s"\s*:\s*)[-\d.]+' % k, lambda g: g.group(1) + str(v), obj)
    open(path, 'w').write(s[:a] + obj + s[b:])
