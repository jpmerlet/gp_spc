# -*- coding: utf-8 -*-
from drillhole.controller.collars import Collars
from drillhole.controller.composites import Composites
from drillhole.controller.drillholes import Drillholes
from drillhole.controller.samples import Samples
from drillhole.controller.surveys import Surveys

if __name__ == '__main__':
    # path = 'C:/Users/sbarr_000/Desktop/geol_drilling_test/composites.csv'
    # composites = Composites(path, holeid='dhid', middlex='midx', middley='midy', middlez='midz', readComposites=True)
    #
    # for composite in composites:
    #     print(composite.middlex, composite.middley, composite.middlez)
    #

    collars = Collars(path='collar.csv', holeid='holeid', x='x', y='y', z='z', readCollars=True)
    surveys = Surveys(path='survey.csv', holeid='holeid', depth='from', azimuth='azimuth', dip='dip', readSurveys=True)
    samples = Samples(path='assay.csv', holeid='holeid', from_='from', to_='to', readSamples=True)

    drillholes = Drillholes.makeDrillholes(collars=collars, surveys=surveys, samples=samples)

    for drillhole in drillholes:
        for sample in drillhole.samples:
            print(sample.bottomx, sample.bottomy, sample.bottomz)
            print(sample.topx, sample.topy, sample.topz)