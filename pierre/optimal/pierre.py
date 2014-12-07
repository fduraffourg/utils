#!/bin/env python
import geo
import math

class Pierre():
    def __init__(self, plat_line, hauteur, culasse, ior):
        self.Faces = []
        self.ior = ior
        
        table_line = geo.Line(0, [0, hauteur])
        
        # interception entre plat et table
        inter_plat_table = table_line.intercept(plat_line)
        if not inter_plat_table:
            return

        table_hsize = max(inter_plat_table[0], 0)
        table = geo.Segment(table_line, x=[-table_hsize, table_hsize])
        plat = geo.Segment(plat_line, x=[1, table_hsize])

        self.addFace("table", table, True)
        self.addFace("platG", plat, True)
        self.addFace("platD", plat.getYSymetric(), True)

        # Culasse
        xstart = 1
        for i,line in enumerate(culasse):
            if i+1 < len(culasse):
                nline = culasse[i+1]
                intercept = line.intercept(nline)
                xend = intercept[0]
            else:
                xend = 0
            
            s = geo.Segment(line, x=[xstart, xend])
            self.addFace("cplat" + str(i) + "G", s, False)
            self.addFace("cplat" + str(i) + "D", s.getYSymetric(), False)
            xstart = xend


    def addFace(self, name, seg, top):
        """ Add a face to the stone"""
        face = {'name': name,
                'seg': seg,
                'top': top}
        self.Faces.append(face)

    def getgTopFaces(self):
        """ Generator returning every face of the top of the stone"""
        for face in self.Faces:
            if face['top']:
                yield face

    def getgBottomFaces(self):
        """ Generator returning every face of the bottom of the stone"""
        for face in self.Faces:
            if not face['top']:
                yield face

    def getgAllFacesButOne(self, exclude):
        """ Generator returning every face of the stone excluding the
        one specified."""
        for face in self.Faces:
            if face != exclude:
                yield face

    def getgAllFaces(self):
        """ Generator returning every face of the stone"""
        for face in self.Faces:
            yield face

    def getRay(self, line):
        """ Get the path of the light inside the stone. We suppose
        that the incident ray comes from the top of the stone."""

        rays = []

        # Search for the face on wich come the ray
        for face in self.getgTopFaces():
            M = face['seg'].interceptLine(line)
            if M:
                break

        seg_in_ray = geo.Segment(line, y=[M[1],1])
        rays.append(seg_in_ray)

        out_rays = face['seg'].getOutRays(line, 1, 1.9, M)
        old_face = face
        old_M = M

        rays.append(geo.Segment(out_rays['refracted'], y=[M[1], 1]))
        reflected_ray = out_rays['reflected']

        for face in self.getgAllFacesButOne(old_face):
            M = face['seg'].interceptLine(reflected_ray)
            if M:
                break

        seg_ray = geo.Segment(reflected_ray, y=[old_M[1], M[1]])
        rays.append(seg_ray)

        return rays

    def getLightPath(self, line):
        # Contains every light rays
        rays = []

        ray = line
        prev_face = False
        prev_intercept = False
        
        for iteration in range(0,4):
            FacesGenerator = self.getgAllFacesButOne(prev_face)
            if iteration == 0:
                FacesGenerator = self.getgTopFaces()

            # For every face in the generator, search if the ray of
            # light intercept it
            for face in FacesGenerator:
                face_seg = face['seg']
                intercept = face_seg.interceptLine(ray)
                if intercept:
                    break

            if not intercept:
                # No face was found, nothing else to do
                break

            # We can delimit the previous ray and add it to the list
            if prev_intercept:
                rays.append({'inside': True,
                             'seg': geo.Segment(ray, y=[prev_intercept[1], intercept[1]])
                            })
            else:
                rays.append({'inside': False,
                             'line': ray})

            # Indice of refraction: First is the stone, then the air,
            # but for the first iteration
            n1, n2 = self.ior, 1
            if iteration == 0:
                n1, n2 = 1, self.ior

            new_rays = face_seg.getOutRays(ray, n1, n2, intercept)

            if iteration == 0:
                inside_ray = new_rays['refracted']
                outside_ray = new_rays['reflected']
            else:
                inside_ray = new_rays['reflected']
                outside_ray = new_rays['refracted']
            
            # Put the outside ray in the list
            rays.append({'inside': False,
                         'line': outside_ray})

            # the inside ray become the new ray and we start again
            ray = inside_ray
            prev_face = face
            prev_intercept = intercept

        return rays
