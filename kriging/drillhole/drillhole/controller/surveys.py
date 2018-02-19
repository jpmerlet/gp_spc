# -*- coding: utf-8 -*-
from drillhole.controller.survey import Survey


class Surveys(object):

    def __init__(self, path=None, holeid=None, depth=None, azimuth=None,\
                 dip=None, columns=None, readSurveys=False):
        self.path = path

        self.holeid = holeid
        self.depth = depth
        self.azimuth = azimuth
        self.dip = dip

        self.__columns = []
        if self.holeid is not None: self.__columns.append((self.holeid, str))
        if self.depth is not None: self.__columns.append((self.depth, float))
        if self.azimuth is not None: self.__columns.append((self.azimuth, float))
        if self.dip is not None: self.__columns.append((self.dip, float))
        if columns is not None: self.__columns.extend(columns)

        self.positions = dict([(self.__columns[i][0], i) for i in range(len(self.__columns))])

        self.surveys = []
        if readSurveys is True:
            self.readSurveys()

    def __iter__(self):
        return iter(self.surveys)

    def __len__(self):
        return len(self.surveys)

    def append(self, survey):
        self.surveys.append(survey)

    @property
    def columns(self):
        features = []
        if self.holeid not in features: features.append(self.holeid)
        if self.depth not in features: features.append(self.depth)
        if self.azimuth not in features: features.append(self.azimuth)
        if self.dip not in features: features.append(self.dip)

        result = []
        for column, _type in self.__columns:
            if column not in features:
                result.append((column, _type))
        return result

    def applyFilter(self, filter):
        for name, _type in self.__columns:
            filter = filter.replace('"%s"' % name, \
                                    'survey["%s"]' % name)
        filter = compile(filter, '', 'eval')
        return [survey for survey in self.surveys if eval(filter)]

    def numericalColumns(self):
        return [name for name, _type in self.__columns if _type is float]

    def categoricalColumns(self):
        return [name for name, _type in self.__columns if _type is str or _type is int]

    def readSurveys(self):
        infile = open(self.path, 'r')
        headers = infile.readline().replace('\n', '').replace('\r', '').split(',')
        for line in infile:
            line = line.replace('\n', '').replace('\r', '').split(',')
            values = [_type(line[headers.index(column)]) for column, _type in self.__columns]
            self.surveys.append(Survey(values, self))
        infile.close()