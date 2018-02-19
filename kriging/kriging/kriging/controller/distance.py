# -*- coding: utf-8 -*-
import numpy
import math

class Distance:

    CARTESIAN = 1
    ANISOTROPIC = 0

    @staticmethod
    def distanceToOrigin(point, anisotropyMatrix):
        # px, py, pz = point
        x, y, z = point
        xani, yani, zani = numpy.array((x, y, z)).dot(anisotropyMatrix)
        anisotropicDistance = math.sqrt(xani ** 2 + yani ** 2 + zani ** 2)
        cartesianDistance = math.sqrt(x ** 2 + y ** 2 + z ** 2)
        return anisotropicDistance, cartesianDistance
