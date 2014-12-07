#!/bin/env python
import geo
import math
import unittest
import random

class TestLine(unittest.TestCase):
    def testInterceptWithSameOrigin(self):
        for i in range(0,50):
            point = [random.random() * 1000 - 500, random.random() * 1000 - 500]
            angle1 = 2 * math.pi * random.random()
            angle2 = 2 * math.pi * random.random()
            if angle1 % math.pi == angle2 % math.pi:
                continue

            g = geo.Line(angle1, point)
            h = geo.Line(angle2, point)
            m = g.intercept(h)
            self.assertEqual(m, point)


class SegLine(unittest.TestCase):
    def testGetOutRays(self):
        line = geo.Line(0, [0,0])
        segment = geo.Segment(line, x=[0,2])
        i1 = 1
        for i in range(0,50):
            i2 = 0.5 + random.random()
            angle = random.random() * 2 * math.pi

            ray = geo.Line(angle, [1,0])
            rays = segment.getOutRays(ray, i1, i2)
            
            incident_angle = math.fabs(angle - math.pi / 2) % math.pi
            incident_quarter = angle // ( math.pi / 2 )

            reflected = rays['reflected']
            reflected_angle = math.fabs(reflected.angle - math.pi / 2) % math.pi
            reflected_quarter = reflected.angle // ( math.pi / 2 )
            self.assertAlmostEqual(incident_angle, reflected_angle,
                                   msg="Bad reflected angle")
            # Check that the reflected ray is on the right quarter of the trigo circle
            self.assertNotEqual(incident_quarter % 2, reflected_quarter % 2,
                                msg="Reflected ray is the same as incident ray (%s)" % {'angle': angle, 'i2': i2})

            if 'refracted' in rays:
                refracted = rays['refracted']
                refracted_angle = math.fabs(refracted.angle - math.pi / 2) % math.pi
                refracted_quarter = refracted.angle // ( math.pi / 2 )
                self.assertAlmostEqual(i1 * math.sin(incident_angle), i2 * math.sin(refracted_angle))
                self.assertTrue( math.fabs( refracted_quarter - incident_quarter ) == 2,
                                 msg="Refracted ray is not on the right quarter (%r)" % {'angle': angle, 'i2': i2, 'ray': ray, 'rays': rays})

    

if __name__ == '__main__':
    unittest.main()

