# -*- coding: utf-8 -*-
from .block import Block


class BlockModel(object):

    def __init__(self, path=None, x=None, y=None, z=None,\
                 lengthx=None, lengthy=None, lengthz=None,\
                 lengths=None, density=None, columns=None,\
                 readBlocks=False):
        
        self.path = path
        
        self.x = x
        self.y = y
        self.z = z
        self.lengthx = lengthx
        self.lengthy = lengthy
        self.lengthz = lengthz
        self.lengths = lengths
        self.density = density

        self.__columns = []
        if self.x is not None: self.__columns.append((self.x, float))
        if self.y is not None: self.__columns.append((self.y, float))
        if self.z is not None: self.__columns.append((self.z, float))
        if self.lengthx is not None: self.__columns.append((self.lengthx, float))
        if self.lengthy is not None: self.__columns.append((self.lengthy, float))
        if self.lengthz is not None: self.__columns.append((self.lengthz, float))
        if self.density is not None: self.__columns.append((self.density, float))
        if columns is not None: self.__columns.extend(columns)
        
        self.positions = dict([(self.__columns[i][0], i) for i in range(len(self.__columns))])
        
        self.blocks = []
        if readBlocks is True:
            self.readBlocks()
    
    def __iter__(self):
        return iter(self.blocks)

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, i):
        return self.blocks[i]

    def copy(self):
        return BlockModel(path=self.path, x=self.x, y=self.y, z=self.z,\
                          lengthx=self.lengthz, lengthy=self.lengthy, lengthz=self.lengthz,\
                          lengths=self.lengths, density=self.density, columns=self.columns)

    def append(self, block):
        self.blocks.append(block)

    @property
    def columns(self):
        features = []
        if self.x is not None: features.append(self.x)
        if self.y is not None: features.append(self.y)
        if self.z is not None: features.append(self.z)
        if self.lengthx is not None: features.append(self.lengthx)
        if self.lengthy is not None: features.append(self.lengthy)
        if self.lengthz is not None: features.append(self.lengthz)
        if self.density is not None: features.append(self.density)

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
            filter = filter.replace('"%s"' % name, 'block["%s"]' % name)
        filter = compile(filter, '', 'eval')
        return [block for block in self.blocks if eval(filter)]

    def splitBlocksByFilter(self, filter):
        for name, _type in self.__columns:
            filter = filter.replace('"%s"' % name, 'block["%s"]' % name)
        in_, out_ = [], []
        filter = compile(filter, '', 'eval')
        for block in self:
            if eval(filter):
                in_.append(block)
            else:
                out_.append(block)
        return in_, out_
    
    def numericalColumns(self):
        return [name for name, _type in self.__columns if _type is float]

    def categoricalColumns(self):
        return [name for name, _type in self.__columns if _type is str or _type is int]

    def readBlocks(self):
        infile = open(self.path, 'r')
        headers = infile.readline().replace('\n', '').replace('\r', '').split(',')
        for line in infile:
            line = line.replace('\n', '').replace('\r', '').split(',')
            values = [_type(line[headers.index(column)]) for column, _type in self.__columns]
            self.blocks.append(Block(values, self))
        infile.close()