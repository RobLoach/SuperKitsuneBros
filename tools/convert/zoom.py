from paths import NES
import sys
from PIL import Image, ImageDraw
lv,band,c0,c1=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]); out=sys.argv[5]
im=Image.open(f'{NES}/{lv}.png').convert('RGB')
c=im.crop((c0*16,band,c1*16,band+240)).resize(((c1-c0)*32,480),Image.NEAREST); d=ImageDraw.Draw(c)
for i in range(c1-c0+1): d.line([(i*32,0),(i*32,480)],fill=(120,0,0)); d.text((i*32+1,1),str(c0+i),fill=(255,255,0))
for j in range(16): d.line([(0,j*32),(c.width,j*32)],fill=(120,0,0)); d.text((1,j*32+12),str(j),fill=(0,255,255))
c.save(out)
