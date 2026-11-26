# render a Kitsune Tails tiled map to PNG: render.py map.json out.png [scale]
import json,sys,os
from PIL import Image
GM=0x0FFFFFFF
root=os.path.dirname(os.path.abspath(sys.argv[1]))  # the tilesets next to the map
m=json.load(open(sys.argv[1]))
ts=[]
for t in sorted(m['tilesets'],key=lambda t:t['firstgid']):
    if 'source' in t:
        d=json.load(open(os.path.join(root,t['source']))); base=os.path.dirname(os.path.join(root,t['source']))
    else: d=t; base=root
    ent={'first':t['firstgid'],'d':d,'base':base,'img':None,'tiles':{}}
    if d.get('image'): ent['img']=Image.open(os.path.join(base,d['image'])).convert('RGBA')
    for x in d.get('tiles',[]):
        if x.get('image'): ent['tiles'][x['id']]=x['image']
    ts.append(ent)
cache={}
def tile(g):
    g&=GM
    if g in cache: return cache[g]
    e=[t for t in ts if t['first']<=g][-1]; i=g-e['first']; d=e['d']; im=None
    if e['img'] is not None:
        c=d['columns']; tw=d['tilewidth']; th=d['tileheight']
        im=e['img'].crop(((i%c)*tw,(i//c)*th,(i%c+1)*tw,(i//c+1)*th))
    elif i in e['tiles']:
        try: im=Image.open(os.path.join(e['base'],e['tiles'][i])).convert('RGBA')
        except Exception: im=None
    cache[g]=im; return im
W,H=m['width'],m['height']
bg=(0,0,0,255) if 'night' in sys.argv else (92,148,252,255)
out=Image.new('RGBA',(W*16,H*16),bg)
def layers(ls):
    for l in ls:
        if l['type']=='group': yield from layers(l['layers'])
        else: yield l
for l in layers(m['layers']):
    if not l.get('visible',True): continue
    if l['type']=='tilelayer':
        for k,g in enumerate(l['data']):
            if not g: continue
            im=tile(g)
            if im is None: continue
            if g&0x80000000: im=im.transpose(Image.FLIP_LEFT_RIGHT)
            x,y=(k%W)*16,(k//W)*16
            out.alpha_composite(im.crop((0,0,min(im.width,W*16-x),min(im.height,H*16-y))),(x,y+16-min(im.height,16)) if im.height<=16 else (x,y))
    elif l['type']=='objectgroup':
        for o in l['objects']:
            if not o.get('gid'): continue
            im=tile(o['gid'])
            if im is None: continue
            im=im.resize((int(o['width']),int(o['height'])))
            x,y=int(o['x']),int(o['y']-o['height'])
            if 0<=x<W*16 and 0<=y<H*16: out.alpha_composite(im.crop((0,0,min(im.width,W*16-x),min(im.height,H*16-y))),(x,y))
out.save(sys.argv[2])
