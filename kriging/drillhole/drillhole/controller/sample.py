# -*- coding: utf-8 -*-
class Sample:

    def __init__(self, values, samples):
        self.values = values
        self.samples = samples

    @property
    def holeid(self):
        if self.samples.holeid is not None:
            return self[self.samples.holeid]

    @property
    def from_(self):
        if self.samples.from_ is not None:
            return self[self.samples.from_]

    @property
    def to_(self):
        if self.samples.to_ is not None:
            return self[self.samples.to_]

    def __getitem__(self, column):
        i = self.samples.positions[column]
        return self.values[i]