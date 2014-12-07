#!/bin/env python
import math

class Line():
    def __init__(self, angle, point):
        self.angle = angle
        self.point = point

    def intercept(self, line):
        coef = [[math.cos(line.angle), -math.cos(self.angle),
                 -1.0 * (line.point[0] - self.point[0])],
                [math.sin(line.angle), -math.sin(self.angle),
                 -1.0 * (line.point[1] - self.point[1])]]

        if coef[0][0] == 0:
            dself = coef[0][2] / coef[0][1]

        elif coef[1][0] == 0:
            dself = coef[1][2] / coef[1][1]

        else:
            # On effectue une combinaison lineaire pour enlever le premier coef
            # Il ne reste que coef[0][1] et coef[0][2]
            coef01 = coef[0][1] / coef[0][0] - coef[1][1] / coef[1][0]
            coef02 = coef[0][2] / coef[0][0] - coef[1][2] / coef[1][0]
            dself = coef02 / coef01
            
        # On the 3 cases, we get dself
        return [ self.point[0] + dself * math.cos(self.angle),
                 self.point[1] + dself * math.sin(self.angle)]


    def __repr__(self):
        return "<Line: %f, (%f,%f)>" % (self.angle, self.point[0], self.point[1])


class Segment():
    def __init__(self, line, x=False, y=False):
        self.line = line
        
        if x:
            # TODO: gerer le cas ou angle = pi/2

            # da = (x-xa)/cos(alpha)
            # y = ya + da * sin(alpha)
            y = [False, False]
            for i in range(0,2):
                d = ( x[i] - line.point[0]) / math.cos(line.angle)
                y[i] = line.point[1] + d * math.sin(line.angle)

        elif y:
            # TODO: cas ou angle = 0
            x = [False, False]
            for i in range(0,2):
                d = ( y[i] - line.point[1] ) / math.sin(line.angle)
                x[i] = line.point[0] + d * math.cos(line.angle)

        p0 = [x[0], y[0]]
        p1 = [x[1], y[1]]
        
        if x[0] > x[1]:
            self.A = p1
            self.B = p0
        else:
            self.A = p0
            self.B = p1


    def __str__(self):
        return "<Segment: (%f,%f) (%f,%f)>" % (self.A[0], self.A[1], self.B[0], self.B[1])

    def getYSymetric(self):
        line = self.line
        sline = Line(math.pi-line.angle, [-line.point[0], line.point[1]])
        return Segment(sline, x=[-self.A[0], -self.B[0]])

    def interceptLine(self, line):
        m = self.line.intercept(line)
        
        if not m:
            return False

        if IsPointBetween(m, self.A, self.B):
            return m

    def getOutRays(self, line, ni, nr, M=False):
        """ Suppose line is a light ray, ns the indice of the incident
        material and nr the indice of the refracted material. This
        function return the live wich represent the refracted light
        ray """
        result = {}

        if not M:
            M = self.interceptLine(line)
            if not M:
                return False

        incident_angle = math.pi/2 + self.line.angle - line.angle

        # Refracted #
        try:
            refract_angle = math.asin(ni / nr * math.sin(incident_angle))
            refract_abs_angle = math.pi/2 + self.line.angle - refract_angle + math.pi
            result['refracted'] = Line(refract_abs_angle, M)
        except:
            pass

        # Reflected #
        reflect_abs_angle = math.pi / 2 + self.line.angle + incident_angle
        result['reflected'] = Line(reflect_abs_angle, M)

        return result
                 
        

def IsPointBetween(M, A, B):
    """ Return True if M is in the rectangle defined by the two points
    A and B."""
    return (A[0] <= M[0] <= B[0] or B[0] <= M[0] <= A[0]) and (A[1] <= M[1] <= B[1] or B[1] <= M[1] <= A[1])
