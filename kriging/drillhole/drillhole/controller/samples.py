# -*- coding: utf-8 -*-
from drillhole.controller.sample import Sample


class Samples(object):

    def __init__(self, path=None, holeid=None, from_=None, to_=None, columns=None, readSamples=False):
        self.path = path

        self.holeid = holeid
        self.from_ = from_
        self.to_ = to_
        
        self.__columns = []
        if self.holeid is not None: self.__columns.append((self.holeid, str))
        if self.from_ is not None: self.__columns.append((self.from_, float))
        if self.to_ is not None: self.__columns.append((self.to_, float))
        if columns is not None: self.__columns.extend(columns)
        
        self.positions = dict([(self.__columns[i][0], i) for i in range(len(self.__columns))])

        self.samples = []
        if readSamples is True:
            self.readSamples()

    def __iter__(self):
        return iter(self.samples)

    def __len__(self):
        return len(self.samples)

    def append(self, sample):
        self.samples.append(sample)

    @property
    def columns(self):
        features = []
        if self.holeid is not None: features.append(self.holeid)
        if self.from_ is not None: features.append(self.from_)
        if self.to_ is not None: features.append(self.to_)

        result = []
        for column, _type in self.__columns:
            if column not in features:
                result.append((column, _type))
        return result

    def applyFilter(self, filter):
        for name, _type in self.__columns:
            filter = filter.replace('"%s"' % name, \
                                    'sample["%s"]' % name)
        filter = compile(filter, '', 'eval')
        return [sample for sample in self.samples if eval(filter)]

    def numericalColumns(self):
        return [name for name, _type in self.__columns if _type is float]

    def categoricalColumns(self):
        return [name for name, _type in self.__columns if _type is str or _type is int]

    def readSamples(self):
        infile = open(self.path, 'r')
        headers = infile.readline().replace('\n', '').replace('\r', '').split(',')
        for line in infile:
            line = line.replace('\n', '').replace('\r', '').split(',')
            values = [_type(line[headers.index(column)]) for column, _type in self.__columns]
            self.samples.append(Sample(values, self))
        infile.close()