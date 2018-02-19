# -*- coding: utf-8 -*-
import math


class Drillhole:

    def __init__(self, holeid, collar=None, surveys=None, samples=None, composites=None):
        self.holeid = holeid
        self.collar = collar
        self.surveys = surveys
        self.samples = samples
        self.composites = composites

        if collar is not None and surveys is not None and samples is not None:
            self.build()

    def build(self):
        survey = self.surveys[0]
        sample = self.samples[0]

        dip = survey.dip            #* math.pi / 180
        azimuth = survey.azimuth    #* math.pi / 180
        length = sample.to_ - sample.from_

        sample.topx = self.collar.x
        sample.topy = self.collar.y
        sample.topz = self.collar.z
        sample.bottomx = sample.topx + length * math.cos(dip) * math.sin(azimuth)
        sample.bottomy = sample.topy + length * math.cos(dip) * math.cos(azimuth)
        sample.bottomz = sample.topz + length * math.sin(dip)