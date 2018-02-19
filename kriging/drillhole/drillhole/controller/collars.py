# -*- coding: utf-8 -*-
from drillhole.controller.collar import Collar


class Collars(object):
    
    def __init__(self, path=None, holeid=None, x=None, y=None,\
        z=None, depth=None, columns=None, readCollars=False):

        self.path = path

        self.holeid = holeid
        self.x = x
        self.y = y
        self.z = z
        self.depth = depth
        
        self.__columns = []
        if self.holeid is not None: self.__columns.append((self.holeid, str))
        if self.x is not None: self.__columns.append((self.x, float))
        if self.y is not None: self.__columns.append((self.y, float))
        if self.z is not None: self.__columns.append((self.z, float))
        if self.depth is not None: self.__columns.append((self.depth, float))
        if columns is not None: self.__columns.extend(columns)

        self.positions = dict([(self.__columns[i][0], i) for i in range(len(self.__columns))])

        self.collars = []
        if readCollars is True:
            self.readCollars()

    def __iter__(self):
        return iter(self.collars)

    def __len__(self):
        return len(self.collars)

    def append(self, collar):
        self.collars.append(collar)

    @property
    def columns(self):
        features = []
        if self.holeid is not None: features.append(self.holeid)
        if self.x is not None: features.append(self.x)
        if self.y is not None: features.append(self.y)
        if self.z is not None: features.append(self.z)
        if self.depth is not None: features.append(self.depth)

        result = []
        for column, _type in self.__columns:
            if column not in features:
                result.append((column, _type))
        return result

    def applyFilter(self, filter):
        for name, _type in self.__columns:
            filter = filter.replace('"%s"' % name, \
                                    'collar["%s"]' % name)
        filter = compile(filter, '', 'eval')
        return [collar for collar in self.collars if eval(filter)]

    def numericalColumns(self):
        return [name for name, _type in self.__columns if _type is float]

    def categoricalColumns(self):
        return [name for name, _type in self.__columns if _type is str or _type is int]

    def readCollars(self):
        infile = open(self.path, 'r')
        headers = infile.readline().replace('\n', '').replace('\r', '').split(',')
        for line in infile:
            line = line.replace('\n', '').replace('\r', '').split(',')
            values = [_type(line[headers.index(column)]) for column, _type in self.__columns]
            self.collars.append(Collar(values, self))
        infile.close()