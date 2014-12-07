import cv2
import numpy as np
import random
import itertools
import math

im = cv2.imread("amundi2.jpg")
gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(1,1),1000)
flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)
cv2.imwrite("05-thresh.jpg", thresh)

canny = cv2.Canny(gray, 10, 100, 3)
cv2.imwrite("06-canny.jpg", canny)

contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea,reverse=True)[:1]

card = contours[0]
color = tuple([random.randint(0,255) for i in range(0,3)])
peri = cv2.arcLength(card,True)
approx = cv2.approxPolyDP(card,0.02*peri,True)
#rect = cv2.minAreaRect(contours[2])
#r = cv2.cv.BoxPoints(rect)

order = approx.argsort(0)
def get_corner(a,b):
    for i in range(0,4):
        if 2 * a <= order[i][0][0] < (a+1)*2 and  2 * b <= order[i][0][1] < (b+1)*2:
            return approx[i]

box = np.array([get_corner(0,0),
                get_corner(0,1),
                get_corner(1,1),
                get_corner(1,0)], np.float32)

print(box)

get_size = lambda a,b: math.sqrt(math.pow(box[a][0][0]-box[b][0][0], 2) + math.pow(box[a][0][1]-box[b][0][1],2))
top = get_size(0,3)
left = get_size(0,1)
right = get_size(2,3)
bottom = get_size(1,2)

width = min(top, bottom)
height = min(left, right)

print(width, height)

portrait = True
if width > height:
    width, height = height, width
    portrait = False

ideal_width = height * 210 / 297
ideal_height = width * 297 / 210

width = int(math.ceil(min(ideal_width, width)))
height = int(math.ceil(min(ideal_height, height)))

if not portrait:
    width, height = height, width

print(width, height)

h = np.array([ [0,0],[0,height],[width, height],[width,0] ],np.float32)
transform = cv2.getPerspectiveTransform(approx.astype(np.float32),h)
warp = cv2.warpPerspective(im,transform, (width, height))
cv2.imwrite("20-res.jpg", warp)

try: 
    points = [tuple(approx[i][0]) for i in range(0,4)]
    lines = itertools.combinations(points, 2)
    for line in lines:
        cv2.line(im, line[0], line[1], color, 3)
except:
    pass

cv2.drawContours(im, card, -1, color, 3)

cv2.imwrite("10-box.jpg", im)

