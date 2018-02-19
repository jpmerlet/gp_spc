# -*- coding: utf-8 -*-
class Structure:

    POWER = 'POWER'
    SPHERIC = 'SPHERIC'
    GAUSSIAN = 'GAUSSIAN'
    EXPONENTIAL = 'EXPONENTIAL'

    def __init__(self, name, sill, ellipsoid):
        self.name = name
        self.sill = sill
        self.ellipsoid = ellipsoid