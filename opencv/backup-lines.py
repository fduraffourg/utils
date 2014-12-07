import cv2
import math
import random
import numpy as np
import itertools


def get_random_color():
    return tuple([random.randint(0,255) for i in range(0,3)])

orig = cv2.imread("amundi2.jpg")

gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
#gray = cv2.blur(gray, (5,5))
cv2.imwrite("05-gray.jpg", gray)

element = cv2.getStructuringElement(cv2.MORPH_RECT,(30,30))
dilate = cv2.dilate(gray, element)
cv2.imwrite("06-dilate.jpg", dilate)

erode = cv2.erode(dilate, element)
cv2.imwrite("07-erode.jpg", erode)

blur = cv2.blur(erode, (5, 5))
cv2.imwrite("08-blur.jpg", blur)

flag, thresh = cv2.threshold(blur, 140, 255, cv2.THRESH_BINARY)
cv2.imwrite("09-thresh.jpg", thresh)


#gray = cv2.equalizeHist(gray)
edges = cv2.Canny(thresh, 80, 120)
cv2.imwrite("10-canny.jpg", edges)

img = orig.copy()
lines = cv2.HoughLinesP(edges, 1, math.pi/880, 100, None, 30, 20)
for line in lines[0]:
    pt1 = (line[0],line[1])
    pt2 = (line[2],line[3])
    size = math.sqrt(math.pow(pt1[0] - pt2[0], 2) +
            math.pow(pt1[1] - pt2[1], 2))
    color = tuple([random.randint(0,255) for i in range(0,3)])
    cv2.line(img, pt1, pt2, color, 3)
cv2.imwrite("20-lines.jpg", img)


def get_orientation(a, b):
    x = 1.0 * b[0] - a[0]
    y = 1.0 * b[1] - a[1]
    if x == 0:
        return math.pi/2
    return math.atan(y / x)
        
def is_aligned(a, b, threshold = math.pi/180):
    oa = get_orientation((a[0], a[1]), (a[2], a[3]))
    ob1 = get_orientation((a[0], a[1]), (b[0], b[1]))
    ob2 = get_orientation((a[0], a[1]), (b[2], b[3]))
    if abs(ob1 - oa) < threshold and abs(ob2 - oa) < threshold:
        return True
    return False

def is_parallel(a, b, threshold = math.pi/180):
    oa = get_orientation((a[0], a[1]), (a[2], a[3]))
    ob = get_orientation((b[0], b[1]), (b[2], b[3]))
    if abs(ob - oa) < threshold or abs((ob - oa + math.pi) % math.pi ) < threshold:
        return True
    return False

# Group lines
groups = []
for line in lines[0]:
    is_alone = True
    for group in groups:
        for subline in group:
            if is_aligned(subline, line):
                group.append(line)
                is_alone = False
                break
    if is_alone:
        groups.append([line])


img = orig.copy()
for group in groups:
    color = tuple([random.randint(0,255) for i in range(0,3)])
    for line in group:
        pt1 = (line[0],line[1])
        pt2 = (line[2],line[3])
        cv2.line(img, pt1, pt2, color, 3)
cv2.imwrite("25-groups.jpg", img)



# Get line from group
def get_length(line):
    return math.sqrt(math.pow(line[0]-line[2], 2) + math.pow(line[1]-line[3],2))

flines = []
for group in groups:
    total = 0
    v = [0,0,0,0]
    for l in group:
        length = get_length(l)
        total += length
        for i in range(0,4):
            v[i] += l[i] * length
    v = map(lambda x:int(x/total), v)
    flines.append((v, length))

img = orig.copy()
for line, l in flines:
    pt1 = (line[0],line[1])
    pt2 = (line[2],line[3])
    size = math.sqrt(math.pow(pt1[0] - pt2[0], 2) +
            math.pow(pt1[1] - pt2[1], 2))
    color = tuple([random.randint(0,255) for i in range(0,3)])
    cv2.line(img, pt1, pt2, color, 3)
cv2.imwrite("30-flines.jpg", img)


# Get corners
def get_intersection(l1, l2):
   pass

def intersect(a1, a2, b1, b2):
    x_1 = a1[0]
    y_1 = a1[1]
    x_2 = a2[0]
    y_2 = a2[1]

    x_3 = b1[0]
    y_3 = b1[1]
    x_4 = b2[0]
    y_4 = b2[1]

    denom = float((x_1 - x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 -
x_4))
    if denom == 0:
        return
    
    x = ((x_1 * y_2 - y_1 * x_2) * (x_3 - x_4) - (x_1 - x_2) *
(x_3 * y_4 - y_3 * x_4)) / denom
    y = ((x_1 * y_2 - y_1 * x_2) * (y_3 - y_4) - (y_1 - y_2) *
(x_3 * y_4 - y_3 * x_4)) / denom
    try:
        x = int(x)
        y = int(y)
    except OverflowError:
        return
    return (x, y)


def get_points_from_line(l):
    a = np.array([l[0], l[1]])
    b = np.array([l[2], l[3]])
    return a,b


flines_by_len = flines.sort(key=lambda x: x[1], reverse=True)


groups = []
for fline in flines:
    line, length = fline[0], fline[1]
    is_alone = True
    for group in groups:
        for subline, sublen in group:
            if is_parallel(subline, line, threshold=math.pi/6):
                group.append(fline)
                is_alone = False
                break
    if is_alone:
        groups.append([fline])


img = orig.copy()
for group in groups:
    color = get_random_color()
    for l, length in group:
        cv2.line(img, (l[0], l[1]), (l[2], l[3]), color, 3)
cv2.imwrite("35-parallel_lines.jpg", img)


# We assume the noise will produce small groups, so we take the 2 groups with
# the maximum length
first = (0,0)
second = (0,0)
for i, group in enumerate(groups):
    total = 0
    for line, length in group:
        total += length
    if total > first[1]:
        second = first
        first = (i, total)
        continue
    if total > second[1]:
        second = (i, total)

for i in [first[0], second[0]]:
    l = groups[i][0][0]
    orientation = get_orientation((l[0],l[1]), (l[2], l[3]))
    if 0 <= abs(orientation) <= math.pi/4:
        horizontal = groups[i]
    else:
        vertical = groups[i]

if horizontal[0][0][1] > horizontal[1][0][1]:
    top, bottom = horizontal[1][0], horizontal[0][0]
else:
    top, bottom = horizontal[0][0], horizontal[1][0]



if vertical[0][0][1] < vertical[1][0][1]:
    left, right = vertical[1][0], vertical[0][0]
else:
    left, right = vertical[0][0], vertical[1][0]

duos = [(top,left), (left, bottom), (bottom, right), (right, top)]
corners = []
for duo in duos:
    a1, a2 = get_points_from_line(duo[0])
    b1, b2 = get_points_from_line(duo[1])
    inter = intersect(a1, a2, b1, b2)
    corners.append(inter)  


img = orig.copy()
for point in corners:
    cv2.circle(img, tuple(point), 8, (255,0,0), -1)
cv2.imwrite("40-corners.jpg", img) 




get_size = lambda a,b: math.sqrt(math.pow(corners[a][0]-corners[b][0], 2) + 
                       math.pow(corners[a][1]-corners[b][1],2))
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

box = np.array(corners, np.float32)
dst = np.array([ [0,0],[0,height],[width, height],[width,0] ],np.float32)
print(box, dst)
transform = cv2.getPerspectiveTransform(box, dst)
warp = cv2.warpPerspective(orig,transform, (width, height))
cv2.imwrite("50-result.jpg", warp)

