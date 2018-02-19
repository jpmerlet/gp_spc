# -*- coding: utf-8 -*-
class Survey:

    def __init__(self, values, surveys):
        self.values = values
        self.surveys = surveys

    @property
    def holeid(self):
        if self.surveys.holeid is not None:
            return self[self.surveys.holeid]

    @property
    def depth(self):
        if self.surveys.depth is not None:
            return self[self.surveys.depth]

    @property
    def azimuth(self):
        if self.surveys.azimuth is not None:
            return self[self.surveys.azimuth]

    @property
    def dip(self):
        if self.surveys.dip is not None:
            return self[self.surveys.dip]

    def __getitem__(self, column):
        i = self.surveys.positions[column]
        return self.values[i]