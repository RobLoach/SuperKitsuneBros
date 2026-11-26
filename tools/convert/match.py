from paths import HERE
import pickle
from db import cell,norm
BLUE=(92,148,252); BLACK=(0,0,0)
def px(b): return [tuple(b[i:i+3]) for i in range(0,len(b),3)]
_dbs={}
def get(name):
    if name not in _dbs:
        db,ndb=pickle.load(open(f'{HERE}/db-{name}.pkl','rb'))
        _dbs[name]=(db,ndb,[(c,px(c),v.most_common(1)[0][0]) for c,v in db.items()])
    return _dbs[name]
def fuzzy(c,name='over'):
    """night cells: black may stand for the day's blue sky, other colours map one to one"""
    n=px(c); best=None
    for dc,d,v in get(name)[2]:
        f={};ok=True
        for a,b in zip(n,d):
            if a==BLACK:
                if b not in (BLUE,BLACK): ok=False;break
                continue
            if b==BLUE or f.setdefault(a,b)!=b: ok=False;break
        if ok and len(set(f.values()))==len(f):
            score=sum(1 for a,b in zip(n,d) if a==BLACK and b==BLACK)+(100000 if v!=(0,0,0,0) else 0)
            if best is None or score>best[0]: best=(score,v)
    return best[1] if best else None
def classify(c,name='over',night=True):
    db,ndb,_=get(name)
    if c in db: return db[c].most_common(1)[0][0],'e'
    v=fuzzy(c,name) if night else None
    if v is not None: return v,'f'
    if norm(c) in ndb: return ndb[norm(c)].most_common(1)[0][0],'n'
    return None,'?'
