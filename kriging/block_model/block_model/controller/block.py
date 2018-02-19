# -*- coding: utf-8 -*-
class Block:

    def __init__(self, values, blockModel):
        self.values = values
        self.blockModel = blockModel

    @property
    def x(self):
        if self.blockModel.x is not None:
            return self[self.blockModel.x]

    @property
    def y(self):
        if self.blockModel.y is not None:
            return self[self.blockModel.y]

    @property
    def z(self):
        if self.blockModel.z is not None:
            return self[self.blockModel.z]

    @property
    def lengthx(self):
        if self.blockModel.lengthx is not None:
            return self[self.blockModel.lengthx]

    @lengthx.deleter
    def lengthx(self):
        del(self.lengthx)

    @property
    def lengthy(self):
        if self.blockModel.lengthy is not None:
            return self[self.blockModel.lengthy]

    @property
    def lengthz(self):
        if self.blockModel.lengthz is not None:
            return self[self.blockModel.lengthz]

    @property
    def density(self):
        if self.blockModel.density is not None:
            return self[self.blockModel.density]

    @property
    def tonnage(self):
        if self.blockModel.lengths is not None and self.density is not None:
            lengthx, lengthy, lengthz = self.blockModel.lengths
            return lengthx*lengthy*lengthz*self.density

    def __getitem__(self, column):
        i = self.blockModel.positions[column]
        return self.values[i]