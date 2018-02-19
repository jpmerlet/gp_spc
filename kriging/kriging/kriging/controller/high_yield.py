# -*- coding: utf-8 -*-
from kriging.controller.distance import Distance
import numpy


class HighYield:

    def __init__(self, value, ellipsoid):
        self.value = value
        self.ellipsoid = ellipsoid

    def apply(self, sample, distanceType=Distance.CARTESIAN):
        distance, holeid, x, y, z, value = sample

        if value >= self.value:
            anisotropicDistance, cartesianDistance = self.ellipsoid.distance((x, y, z))

            if anisotropicDistance <= self.ellipsoid.major:
                if distanceType == Distance.CARTESIAN:
                    return numpy.array((cartesianDistance, holeid, x, y, z, value))
                else:
                    return numpy.array((anisotropicDistance, holeid, x, y, z, value))
        return sample
