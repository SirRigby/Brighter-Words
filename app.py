import cv2    
import os
import numpy as np

def Trans(s, t=" "):
    s=' '.join(s.split('\n'))
    return s.replace(" ",t)

fontFace = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX

def mosaic(im, corlist, n, m):
    h, w = im.shape[:2]
    block_height = h // n
    block_width = w // m
    
    for i in range(n):
        for j in range(m):
            srow = i * block_height
            scol = j * block_width
            erow = srow + block_height + (1 if i < h % n else 0) - 1
            ecol = scol + block_width + (1 if j < w % m else 0) - 1
            
            erow = min(erow, h - 1)
            ecol = min(ecol, w - 1)
            
            corlist.append([srow, scol, erow, ecol])

def fillCol(op, corlist, collist):
    for srow, scol, erow, ecol in corlist:
        region = op[srow:erow+1, scol:ecol+1]
        avg_color = np.mean(region, axis=(0, 1)).astype(int)
        collist.append(avg_color)

def changeB(op):
    op[:] = (op * 0.1).clip(0, 255).astype(np.uint8)

def getScale(cor, c):
    h, w = cor[2] - cor[0] + 1, cor[3] - cor[1] + 1
    y, x = (cor[0] + cor[2]) // 2, (cor[1] + cor[3]) // 2

    for scale in range(1000, 0, -1):
        sz = cv2.getTextSize(c, fontFace, fontScale=scale / 100, thickness=1)
        if h >= sz[0][1] and w >= sz[0][0]:
            return scale*(0.75)
    return 1

def getOrg(cor,c,scale):
    y, x = (cor[0] + cor[2]) // 2, (cor[1] + cor[3]) // 2
    sz = cv2.getTextSize(c, fontFace, fontScale=scale / 100, thickness=1)
    return (int(x - 0.65 * (sz[0][0] / 2)), int(y + 0.5 * (sz[0][1] / 2)))


def wrtText(im, corlist, collist, s):
    scale=getScale(corlist[0],s[0])
    for i in range(len(corlist)):
        c=s[i%len(s)]
        org = getOrg(corlist[i],c, scale)
        color = tuple(min(255, int(20 + int(ch))) for ch in collist[i])
        cv2.putText(im, c, org, fontFace, scale / 100, color, 1, cv2.LINE_AA)

dir_path = os.path.dirname(os.path.realpath(__file__))

#text processing
tfile=os.path.join(dir_path,"input.txt")
textFile= open(tfile,"r")
textlist=textFile.readlines()
text=(' '.join(textlist)).replace('\n','')+' '

# image processing
file = os.path.join(dir_path, "input.jpg")
im = cv2.imread(file)
op = im.copy()

corlist = []
collist = []
mosaic(op, corlist, 50, 150)
fillCol(op, corlist, collist)
changeB(op)
wrtText(op, corlist, collist, text )

cv2.imwrite(os.path.join(dir_path, "output.jpg"), op)
