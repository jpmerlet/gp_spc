# -*- coding: utf-8 -*-
from dxf import DXF


class Solid:

    def __init__(self, triangles=None):
        self.triangles = triangles or []

class SolidFacade:

    @staticmethod
    def fromDXF(path):
        lines = DXF.read(path)

        aux = None
        triangles = []
        for type_, value in lines:
            if type_ == '0':
                if value == '3DFACE':
                    aux = []
            elif type_ == '10' and aux is not None:
                aux.append(float(value))
            elif type_ == '20' and aux is not None:
                aux.append(float(value))
            elif type_ == '30' and aux is not None:
                aux.append(float(value))
            elif type_ == '11' and aux is not None:
                aux.append(float(value))
            elif type_ == '21' and aux is not None:
                aux.append(float(value))
            elif type_ == '31' and aux is not None:
                aux.append(float(value))
            elif type_ == '12' and aux is not None:
                aux.append(float(value))
            elif type_ == '22' and aux is not None:
                aux.append(float(value))
            elif type_ == '32' and aux is not None:
                aux.append(float(value))
                triangles.append((tuple(aux[:3]),
                                  tuple(aux[3:6]),
                                  tuple(aux[6:])))
                aux = None

        print(len(triangles))

        aux = {}
        for triangle in triangles:
            (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = triangle
            for (x11, y11, z11), (x22, y22, z22) in [((x1, y1, z1), (x2, y2, z2)),
                                                     ((x2, y2, z2), (x3, y3, z3)),
                                                     ((x3, y3, z3), (x1, y1, z1))]:
                key = (x11 + x22, y11 + y22, z11 + z22)
                if key in aux:
                    aux[key].append(triangle)
                else:
                    aux[key] = [triangle]

        for key in [key for key in aux]:
            if len(aux[key]) != 2:
                del(aux[key])


        def search(solid, triangle, dictionary):
            search = [triangle]
            while len(search) > 0:
                triangle = search.pop()
                solid.triangles.append(triangle)
                (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = triangle
                for (x11, y11, z11), (x22, y22, z22) in [((x1, y1, z1), (x2, y2, z2)),
                                                         ((x2, y2, z2), (x3, y3, z3)),
                                                         ((x3, y3, z3), (x1, y1, z1))]:

                    key = (x11 + x22, y11 + y22, z11 + z22)
                    if key in dictionary:
                        p1 = (x11, y11, z11)
                        p2 = (x22, y22, z22)

                        t1, t2 = dictionary[key]
                        p3, = [p for p in t1 if p != p1 and p != p2]
                        p4, = [p for p in t2 if p != p1 and p != p2]
                        point = p3 if p3 not in triangle else p4
                        search.append((p2, p1, point))

                        del(dictionary[key])

        solids = []
        
        while len(aux.values()) > 0:
            triangle = list(aux.values())[0][0]
            solid = Solid()
            search(solid, triangle, aux)
            solids.append(solid)

        return solids