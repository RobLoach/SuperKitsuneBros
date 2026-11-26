from paths import HERE, NES, ROOT
import json,collections,pickle
from PIL import Image
GM=0x0FFFFFFF
# (nesmaps image, band y, columns, map file): maps built 1:1 from the image, grouped by tileset layout
SRC={'over':[('2-1',240,224,'level-2-1-game.json'),('2-3',0,240,'level-2-3-game.json'),('2-4',0,160,'level-2-4-game.json'),('1-3',0,176,'level-1-3-game.json')],
     'ug':[('1-2',240,192,'level-1-2-underground.json')],
     'water':[('2-2',240,192,'level-2-2-underwater.json')]}
def cell(im,x,y): return im.crop((x*16,y*16,x*16+16,y*16+16)).tobytes()
def norm(b):
    lab={};o=bytearray()
    for i in range(0,len(b),3):
        p=b[i:i+3]
        if p not in lab: lab[p]=len(lab)
        o.append(lab[p])
    return bytes(o)
def load(src):
    db=collections.defaultdict(collections.Counter); ndb=collections.defaultdict(collections.Counter)
    for lv,band,W,f in src:
        im=Image.open(f'{NES}/{lv}.png').convert('RGB')
        im=im.crop((0,band,W*16,band+240))
        m=json.load(open(f'{ROOT}/{f}'))
        L={l['name']:l['data'] for l in m['layers'] if l['type']=='tilelayer'}
        MW=m['width']
        for x in range(W):
            for y in range(15):
                k=y*MW+x
                v=tuple(L[n][k]&GM if n in L else 0 for n in ('Background No Parallax','Blocks','Coins','Foreground'))
                c=cell(im,x,y)
                db[c][v]+=1; ndb[norm(c)][v]+=1
    return db,ndb
if __name__=='__main__':
    for name,src in SRC.items():
        db,ndb=load(src)
        pickle.dump((db,ndb),open(f'{HERE}/db-{name}.pkl','wb'))
        print(name,len(db),'cells',sum(1 for c in db.values() if len(c)>1),'ambiguous')
