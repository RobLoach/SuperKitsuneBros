from paths import NES
import sys,json
import numpy as np
from PIL import Image
def tight(im,x0,y0,x1,y1):
    r=im[y0:y1,x0:x1].copy(); r[(r==(92,148,252)).all(2)]=0; m=(r!=0).any(2)
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
    return r[ys[0]:ys[-1]+1, xs[0]:xs[-1]+1]
def templates(lv,boxes):
    """sprites cut from a map's legend; a box can name another map's image first, for sprites missing from the legend"""
    ims={}
    image=lambda l: ims.setdefault(l, np.array(Image.open(f'{NES}/{l}.png').convert('RGB')))
    T={}
    for name,b in boxes.items():
        src,b=(b[0],b[1:]) if isinstance(b[0],str) else (lv,b)
        t=tight(image(src),*b); T[name]=t; T[name+'_flip']=t[:,::-1]
    return T
def find(img,T,minfrac=0.97):
    H,W,_=img.shape; out=[]
    for name,t in T.items():
        th,tw,_=t.shape; m=(t!=0).any(2); ys,xs=np.where(m); n=len(ys)
        score=np.zeros((H-th+1,W-tw+1),np.int32)
        for y,x in zip(ys,xs):
            score+=(img[y:y+H-th+1,x:x+W-tw+1]==t[y,x]).all(2)
        for y,x in zip(*np.where(score>=n*minfrac)):
            out.append((name,int(x),int(y),tw,th,int(score[y,x])/n))
    # non-max suppression
    out.sort(key=lambda o:-o[5]); keep=[]
    for o in out:
        if all(abs(o[1]-k[1])>=8 or abs(o[2]-k[2])>=8 for k in keep): keep.append(o)
    return sorted(keep,key=lambda o:(o[1],o[2]))
B31={'coin':(476,556,492,576),'mushroom':(474,580,494,600),'star':(474,606,494,628),'oneup':(474,630,494,650),
     'goomba':(604,553,624,574),'koopa':(604,572,624,598),'paratroopa':(604,600,624,626),'hammer':(604,627,624,653),'piranha':(546,652,568,678)}
B33={'mushroom':(3362,78,3382,98),'goomba':(3362,105,3382,125),'koopa':(3362,124,3382,150),'paratroopa':(3362,150,3382,177)}
B41={'coin':(511,293,525,311),'mushroom':(508,319,528,339),'oneup':(508,346,528,366),'lakitu':(508,366,528,392),'spiny':(508,391,528,409),'egg':(509,410,527,430),'piranha':(508,431,528,458)}
B42={'coin':(511,533,525,551),'mushroom':(508,559,528,579),'star':(509,586,527,606),'buzzy':(508,609,528,628),'goomba':(508,629,528,648),'koopa':(508,648,528,673),'piranha':(508,672,528,699),'piranha2':(488,672,508,699)}
B43={'coin':(320,64,336,80),'mushroom':(3108,102,3127,122),'koopa':(3108,131,3127,158),'paratroopa':(3108,164,3127,191)}
B44={'podoboo':(3620,108,3635,128)}
B51={'coin':(511,277,525,295),'star':(509,297,527,317),'oneup':(508,319,528,339),'bullet':(1733,177,1745,191),'goomba':(508,360,528,378),'koopa':(508,378,528,404),'paratroopa':(508,406,528,433),'piranha':(508,434,528,461)}
B52={'coin':(476,556,490,574),'mushroom':(473,582,493,602),'star':(474,609,492,629),'bullet':(473,632,494,649),'buzzy':(473,655,493,671),'blooper':(473,671,493,699),
     'cheep':(604,555,623,575),'cheep2':(624,555,641,575),'goomba':(623,576,641,595),'koopa':(603,593,623,620),'koopa2':(623,593,641,620),'paratroopa':(623,620,641,647),'hammer':(623,646,641,674),'piranha':(623,673,641,700)}
B53={'mushroom':(3364,79,3383,99),'goomba':(3364,107,3383,125),'koopa':(3364,125,3383,151),'paratroopa':(3364,150,3383,177),'bullet':(3364,182,3384,199)}
B54={'podoboo':(3108,123,3126,143)}
B61={'coin':(3879,53,3893,71),'mushroom':(3876,79,3896,99),'oneup':(3876,106,3896,126),'lakitu':(3876,126,3896,152),'spiny':(3876,150,3896,169),'egg':(3877,170,3895,190),'piranha':(3876,191,3896,218)}
B62={'coin':(476,76,490,94),'mushroom':(473,102,493,122),'star':(474,129,492,149),'buzzy':(473,153,493,169),'blooper':(473,169,493,197),
     'cheep':(604,75,623,95),'cheep2':(624,75,641,95),'goomba':(623,96,641,115),'koopa':(623,113,641,140),'paratroopa':(623,140,641,167),'piranha':(623,170,641,197)}
B63={'mushroom':(3620,120,3640,140),'bullet':(3620,170,3640,188)}
B64={'podoboo':(3108,123,3126,143)}
B71={'coin':(511,277,525,295),'oneup':(508,297,528,317),'bullet':(508,320,529,337),'buzzy':(508,341,528,357),'koopa':(508,356,528,383),'paratroopa':(508,385,528,412),'piranha':(508,413,528,440),'hammer':(508,441,528,469)}
B72={'blooper':(1149,98,1167,126),'cheep':(1149,135,1167,155)}
B73={'mushroom':(4388,79,4408,99),'cheep':(4388,106,4408,126),'koopa':(4368,124,4388,151),'koopa2':(4388,124,4408,151),'paratroopa':(4388,150,4408,177)}
B81={'coin':(508,277,528,295),'oneup':(508,297,528,317),'star':(508,318,528,338),'buzzy':(508,341,528,357),'goomba':(508,360,528,379),'koopa':(508,379,528,406),'paratroopa':(508,408,528,435),'piranha':(508,436,528,461)}
B82={'coin':(473,316,493,334),'mushroom':(473,342,493,362),'bullet':(473,372,493,387),'buzzy':(473,393,493,409),'lakitu':(473,410,493,436),
     'goomba':(623,315,643,334),'paratroopa':(623,336,643,363),'piranha':(623,366,643,393),'spiny':(623,392,643,411),'egg':(623,414,643,434)}
B83={'koopa':('8-1',508,379,528,406),'mushroom':(4388,79,4408,99),'bullet':(4388,109,4408,124),'paratroopa':(4388,132,4408,159),'piranha':(4388,163,4408,190),'hammer':(4388,193,4408,220)}
B84={'blooper':(510,343,530,371),'buzzy':(510,378,530,397),'cheep':(511,407,530,427),'hammer':(510,434,530,461),
     'paratroopa':(690,284,710,311),'goomba':(690,317,710,337),'piranha':(690,344,710,371),'podoboo':(691,376,709,396)}
B11={'coin':(511,293,525,311),'mushroom':(508,319,528,339),'star':(509,346,527,366),'oneup':(508,368,528,388),'goomba':(508,389,528,408),'koopa':(508,406,528,433)}
B21={'coin':(511,513,525,531),'mushroom':(508,539,528,559),'star':(509,566,527,586),'oneup':(508,588,528,608),'goomba':(508,609,528,628),'koopa':(508,626,528,653),'paratroopa':(508,655,528,682),'piranha':(508,683,528,710)}
if __name__=='__main__':
    lv,band,W=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
    T=templates('3-1',B31)
    for k,t in T.items():
        if not k.endswith('flip'): print(k,t.shape)
    img=np.array(Image.open(f'{NES}/{lv}.png').convert('RGB'))[band:band+240,:W*16]
    for o in find(img,T): print(o[0],'x=%d y=%d w=%d h=%d col=%.2f row=%.2f %.2f'%(o[1],o[2],o[3],o[4],o[1]/16,(o[2]+o[4])/16,o[5]))


def lifts(img, color=(216, 40, 0)):
    """orange NES lifts as (x, y, w) pixel boxes"""
    from scipy import ndimage
    m = (img == np.array(color)).all(2)
    lab, n = ndimage.label(ndimage.binary_closing(m, iterations=2))
    out = []
    for sl in ndimage.find_objects(lab):
        ys, xs = sl
        if xs.stop - xs.start >= 32 and ys.stop - ys.start <= 10:
            out.append((xs.start, ys.start, xs.stop - xs.start))
    return sorted(out)
