"""print a map's solid tiles as text, to trace routes through mazes and find leaks between paths

    python ascii.py level-7-4-game.json 150-175 200-230

# solid, . open, D door that zones somewhere, X such a door inside a wall (unreachable),
v pipe you go down into, ^ pipe you come out of
"""
import json
import sys
from paths import ROOT


def main(path, *windows):
    m = json.load(open(f'{ROOT}/{path}' if not path.startswith('/') else path))
    W, H = m['width'], m['height']
    solid = [0] * (W * H)
    for l in m['layers']:
        if l['type'] == 'tilelayer' and any(p['name'] == 'blocks' and p['value'] for p in l.get('properties', [])):
            solid = [a or b for a, b in zip(solid, l['data'])]
    marks = {}
    for l in m['layers']:
        for o in l.get('objects', []) if l['type'] == 'objectgroup' else []:
            x, y = int(o['x'] // 16), int(o['y'] // 16)
            if o['gid'] == 30 and any(p['name'] == 'zoneTo' for p in o.get('properties', [])):
                for yy in (y - 2, y - 1):
                    if 0 <= yy < H:
                        marks[x, yy] = 'X' if solid[yy * W + x] else 'D'
            elif o['gid'] in (131, 153):
                for xx in (x, x + 1):
                    marks[xx, y - 1] = 'v' if o['gid'] == 131 else '^'
    for w in windows or [f'0-{W}']:
        x0, x1 = map(int, w.split('-'))
        x1 = min(x1, W)
        print('    ' + ' '.join(f'{x:3}' for x in range(x0, x1)))
        for y in range(H):
            print(f'{y:3} ' + ' '.join('  ' + (marks.get((x, y)) or ('#' if solid[y * W + x] else '.')) for x in range(x0, x1)))


if __name__ == '__main__':
    main(*sys.argv[1:])
