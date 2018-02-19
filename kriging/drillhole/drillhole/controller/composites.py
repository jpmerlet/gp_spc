# -*- coding: utf-8 -*-
from drillhole.controller.composite import Composite


class Composites(object):

    def __init__(self, path=None, holeid=None, bottomx=None, bottomy=None, bottomz=None,\
                 middlex=None, middley=None, middlez=None, topx=None, topy=None, topz=None,\
                 from_=None, to_=None, columns=None, readComposites=False):

        self.path = path
        
        self.holeid = holeid
        self.bottomx = bottomx
        self.bottomy = bottomy
        self.bottomz = bottomz
        self.middlex = middlex
        self.middley = middley
        self.middlez = middlez
        self.topx = topx
        self.topy = topy
        self.topz = topz
        self.from_ = from_
        self.to_ = to_

        self.__columns = []
        if self.holeid is not None: self.__columns.append((self.holeid, str))
        if self.bottomx is not None: self.__columns.append((self.bottomx, float))
        if self.bottomy is not None: self.__columns.append((self.bottomy, float))
        if self.bottomz is not None: self.__columns.append((self.bottomz, float))
        if self.middlex is not None: self.__columns.append((self.middlex, float))
        if self.middley is not None: self.__columns.append((self.middley, float))
        if self.middlez is not None: self.__columns.append((self.middlez, float))
        if self.topx is not None: self.__columns.append((self.topx, float))
        if self.topy is not None: self.__columns.append((self.topy, float))
        if self.topz is not None: self.__columns.append((self.topz, float))
        if self.from_ is not None: self.__columns.append((self.from_, float))
        if self.to_ is not None: self.__columns.append((self.to_, float))
        if columns is not None: self.__columns.extend(columns)
        
        self.positions = dict([(self.__columns[i][0], i) for i in range(len(self.__columns))])

        self.composites = []
        if readComposites is True:
            self.readComposites()

    def __iter__(self):
        return iter(self.composites)

    def __len__(self):
        return len(self.composites)

    def __getitem__(self, i):
        return self.composites[i]

    def append(self, composite):
        self.composites.append(composite)

    @property
    def columns(self):
        features = []
        if self.holeid is not None: features.append(self.holeid)
        if self.bottomx is not None: features.append(self.bottomx)
        if self.bottomy is not None: features.append(self.bottomy)
        if self.bottomz is not None: features.append(self.bottomz)
        if self.middlex is not None: features.append(self.middlex)
        if self.middley is not None: features.append(self.middley)
        if self.middlez is not None: features.append(self.middlez)
        if self.topx is not None: features.append(self.topx)
        if self.topy is not None: features.append(self.topy)
        if self.topz is not None: features.append(self.topz)
        if self.from_ is not None: features.append(self.from_)
        if self.to_ is not None: features.append(self.to_)

        result = []
        for column, _type in self.__columns:
            if column not in features:
                result.append((column, _type))
        return result

    @property
    def allColumns(self):
        return self.__columns

    def applyFilter(self, filter):
        for name, _type in self.__columns:
            filter = filter.replace('"%s"' % name, \
                                    'composite["%s"]' % name)
        filter = compile(filter, '', 'eval')
        return [composite for composite in self.composites if eval(filter)]

    def numericalColumns(self):
        return [name for name, _type in self.__columns if _type is float]

    def categoricalColumns(self):
        return [name for name, _type in self.__columns if _type is str or _type is int]

    def readComposites(self):
        infile = open(self.path, 'r')
        headers = infile.readline().replace('\n', '').replace('\r', '').split(',')
        for line in infile:
            line = line.replace('\n', '').replace('\r', '').split(',')
            values = [_type(line[headers.index(column)]) for column, _type in self.__columns]
            self.composites.append((Composite(values, self)))
        infile.close()

    def copy(self):
        return Composites(path=self.path, holeid=self.holeid, bottomx=self.bottomx, bottomy=self.bottomy,
                          bottomz=self.bottomz, middlex=self.middlex, middley=self.middley, middlez=self.middlez,
                          topx=self.topx, topy=self.topy, topz=self.topz, from_=self.from_, to_=self.to_,
                          columns=self.__columns)

    def addVariable(self, varName, varType, default=None):
        self.__columns.append((varName, varType))
        self.positions.update({varName: len(self.positions)})

        if default is not None:
            for composite in self.composites:
                composite.values.append(default)
