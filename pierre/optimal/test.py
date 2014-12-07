#!/bin/env python
import geo
from math import pi

g = geo.Line(pi/2, [1,0])
h = geo.Line(0, [0,1])
m = g.intercept(h)
print "%s intercept %s in %s" % (g,h,m)

g = geo.Line(pi/4, [1,0])
h = geo.Line(3*pi/4, [-1,0])
m = g.intercept(h)
print "%s intercept %s in %s" % (g,h,m)


line = geo.Line(pi/4, [0,0])
segment = geo.Segment(line, x=[0,1])
print segment

line = geo.Line(pi/2, [1,0])
segment = geo.Segment(line, y=[0,1])
print segment


line = geo.Line(0, [0,0])
segment = geo.Segment(line, x=[0,2])
ray = geo.Line(pi/2, [1,0])
rays = segment.getOutRays(ray, 1, 1.9)
print "Segment: %s, Ray: %s\n * Reflected: %s\n * Refracted: %s" % (segment, ray, rays['reflected'], rays['refracted'])

line = geo.Line(0, [0,0])
segment = geo.Segment(line, x=[0,2])
ray = geo.Line(3*pi/4, [1,0])
rays = segment.getOutRays(ray, 1, 1.9)
print "Segment: %s, Ray: %s\n * Reflected: %s\n * Refracted: %s" % (segment, ray, rays['reflected'], rays['refracted'])


