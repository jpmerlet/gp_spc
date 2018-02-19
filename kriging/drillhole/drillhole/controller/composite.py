# -*- coding: utf-8 -*-
class Composite:
    
    def __init__(self, values, composites):
        self.values = values
        self.composites = composites

    @property
    def holeid(self):
        if self.composites.holeid is not None:
            return self[self.composites.holeid]

    @property
    def bottomx(self):
        if self.composites.bottomx is not None:
            return self[self.composites.bottomx]

    @property
    def bottomy(self):
        if self.composites.bottomy is not None:
            return self[self.composites.bottomy]

    @property
    def bottomz(self):
        if self.composites.bottomz is not None:
            return self[self.composites.bottomz]

    @property
    def middlex(self):
        if self.composites.middlex is not None:
            return self[self.composites.middlex]

    @property
    def middley(self):
        if self.composites.middley is not None:
            return self[self.composites.middley]

    @property
    def middlez(self):
        if self.composites.middlez is not None:
            return self[self.composites.middlez]

    @property 
    def topx(self):
        if self.composites.topx is not None:
            return self[self.composites.topx]

    @property
    def topy(self):
        if self.composites.topy is not None:
            return self[self.composites.topy]

    @property
    def topz(self):
        if self.composites.topz is not None:
            return self[self.composites.topz]

    @property
    def from_(self):
        if self.composites.from_ is not None:
            return self[self.composites.from_]

    @property
    def to_(self):
        if self.composites.to_ is not None:
            return self[self.composites.to_]
    
    def __getitem__(self, column):
        i = self.composites.positions[column]
        return self.values[i]