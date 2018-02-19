# -*- coding: utf-8 -*-
import numpy

from dxf import DXF
from geometry.controller.polyline import Polyline
from geometry.controller.polylines import Polylines


class PolylinesFacade:

    @staticmethod
    def fromDXF(path):
        lines = DXF.read(path)

        # i = 0
        # lines = []
        # infile = open(path, 'r')
        # for line in infile:
        #     line = line.replace('\n', '')
        #     line = line.strip()
        #     if i%2 == 0: type_ = line
        #     else: lines.append((type_, line))
        #     i += 1
        # infile.close()

        vertex = None
        polylines = []
        for type_, value in lines:
            if type_ == '0':
                if value == 'POLYLINE':
                    polylines.append(Polyline())
                elif value == 'VERTEX':
                    vertex = []
            elif type_ == '10' and vertex is not None:
                vertex.append(float(value))
            elif type_ == '20' and vertex is not None:
                vertex.append(float(value))
            elif type_ == '30' and vertex is not None:
                vertex.append(float(value))
                polylines[-1].vertexs.append(vertex)
                vertex = None

        for polyline in polylines:
            polyline.vertexs = numpy.array(polyline.vertexs)

        return Polylines(polylines)

if __name__ == '__main__':
    path = 'polylines.dxf'
    polylines = PolylinesFacade.fromDXF(path)
    for polyline in polylines:
        print(type(polyline.vertexs))
        print(polyline.vertexs)