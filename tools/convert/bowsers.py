"""a different enemy as Bowser in each castle (the NES fake Bowsers are other enemies in disguise), edited into the
finished maps so the hand-made 1-4 and 2-4 keep their formatting"""
import json
from paths import ROOT
from textedit import set_object

# world: (gid, width, height), all facing left
BOWSER = {1: (46, 16, 32),    # skeleton
          2: (56, 32, 32),    # tanuki ninja
          3: (160, 48, 48),   # brown monkey
          4: (101, 48, 48),   # tengu
          5: (194, 80, 32),   # spear soldier
          6: (123, 32, 32),   # kasha: Bowser throws hammers from 6-4 on, and the kasha throws skulls
          7: (196, 80, 32),   # spear captain
          8: (125, 64, 32)}   # big pango: the real Bowser, king of the Koopas (pangos)
GIDS = {g for g, w, h in BOWSER.values()}  # the generators copy Bowser from other castles by these


def main():
    for world, (gid, w, h) in BOWSER.items():
        path = f'{ROOT}/level-{world}-4-game.json'
        m = json.load(open(path))
        o = next(o for l in m['layers'] if l['type'] == 'objectgroup' for o in l['objects'] if o['gid'] in GIDS and o['y'] == 160)
        x = o['x'] + (o['width'] - w) / 2  # same middle, standing on the bridge
        set_object(path, o['id'], gid=gid, width=w, height=h, x=int(x) if x == int(x) else x)
        print(f'{world}-4', gid)


if __name__ == '__main__':
    main()
