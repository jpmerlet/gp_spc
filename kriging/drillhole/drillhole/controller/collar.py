# -*- coding: utf-8 -*-
class Collar:
    
    def __init__(self, values, collars):
        self.values = values
        self.collars = collars
    
    @property
    def holeid(self):
        if self.collars.holeid is not None:
            return self[self.collars.holeid]

    @property
    def x(self):
        if self.collars.x is not None:
            return self[self.collars.x]

    @property
    def y(self):
        if self.collars.y is not None:
            return self[self.collars.y]

    @property
    def z(self):
        if self.collars.z is not None:
            return self[self.collars.z]

    @property
    def depth(self):
        if self.collars.depth is not None:
            return self[self.collars.depth]

    def __getitem__(self, column):
        i = self.collars.positions[column]
        return self.values[i]