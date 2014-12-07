#!/bin/env python

from pierre import Pierre
from geo import Line, Segment
from math import pi
from matplotlib import pyplot

p = Pierre(Line(2.4485734704807562, [1,0]),
           0.3188,
           [Line(1.012532492680377,[1,0]),
            Line(0.6213319750943451, [0.77405, -0.36179]),
            Line(0.44198323099897213, [0, -0.82387])],
           1.9
           )

ray = Line(1.8*pi/4, [0.9, 0])
rays = p.getLightPath(ray)

for ray in rays:
    if ray['inside']:
        seg = ray['seg']
        pyplot.plot([seg.A[0],seg.B[0]], [seg.A[1], seg.B[1]], color="blue")
    else:
        pass

#seg_ray = Segment(ray, y=[-1, 1])
#seg_oray = Segment(oray, y=[-1, 1])
#print seg_ray, seg_oray
#pyplot.plot([seg_ray.A[0],seg_ray.B[0]], [seg_ray.A[1], seg_ray.B[1]], color="red")
#pyplot.plot([seg_oray.A[0],seg_oray.B[0]], [seg_oray.A[1], seg_oray.B[1]], color="red")

for face in p.getgAllFaces():
    s = face['seg']
    pyplot.plot([s.A[0],s.B[0]], [s.A[1], s.B[1]], color="black")
pyplot.show()
