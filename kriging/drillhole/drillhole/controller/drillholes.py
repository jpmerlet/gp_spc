# -*- coding: utf-8 -*-
from .drillhole import Drillhole


class Drillholes:

    def __init__(self, drillholes):
        self.drillholes = drillholes

    def __iter__(self):
        return iter(self.drillholes)

    def __len__(self):
        return len(self.drillholes)

    @staticmethod
    def makeDrillholes(collars=None, surveys=None, samples=None, composites=None):
        collarsByHoleid = {}
        surveysByHoleid = {}
        samplesByHoleid = {}
        compositesByHoleid = {}

        holeids = set()

        if collars is not None:
            for collar in collars:
                collarsByHoleid[collar.holeid] = collar
                holeids.add(collar.holeid)
        if surveys is not None:
            for survey in surveys:
                if survey.holeid in surveysByHoleid:
                    surveysByHoleid[survey.holeid].append(survey)
                else:
                    surveysByHoleid[survey.holeid] = [survey]
                    holeids.add(survey.holeid)
            for holeid, _surveys in surveysByHoleid.items():
                surveysByHoleid[holeid] = sorted(_surveys, key=lambda survey: survey.depth)
        if samples is not None:
            for sample in samples:
                if sample.holeid in samplesByHoleid:
                    samplesByHoleid[sample.holeid].append(sample)
                else:
                    samplesByHoleid[sample.holeid] = [sample]
                    holeids.add(sample.holeid)
            for holeid, _samples in samplesByHoleid.items():
                samplesByHoleid[holeid] = sorted(_samples, key=lambda sample: sample.from_)
        if composites is not None:
            for composite in composites:
                if composite.holeid in compositesByHoleid:
                    compositesByHoleid[composite.holeid].append(composite)
                else:
                    compositesByHoleid[composite.holeid] = [composite]
                    holeids.add(composite.holeid)
            if composites.from_ is not None:
                for holeid, _composites in compositesByHoleid.items():
                    compositesByHoleid[holeid] = sorted(_composites, key=lambda composite: composite.from_)

        drillholes = []
        for holeid in holeids:
            collar = None
            surveys = None
            samples = None
            composites = None

            if holeid in collarsByHoleid:
                collar = collarsByHoleid[holeid]
            if holeid in surveysByHoleid:
                surveys = surveysByHoleid[holeid]
            if holeid in samplesByHoleid:
                samples = samplesByHoleid[holeid]
            if holeid in compositesByHoleid:
                composites = compositesByHoleid[holeid]

            drillholes.append(Drillhole(holeid, collar=collar, surveys=surveys,\
                                        samples=samples, composites=composites))
        return Drillholes(drillholes)
