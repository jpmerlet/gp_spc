import numpy
from sys import float_info


class Solid:

    def __init__(self, triangles):

        self.triangles = triangles
        self.volume = self.getVolume()
        self.trianglesByPoints = self.getPoints()
        # self.edges = self.getEdges()
        self.minx, self.miny, self.minz, self.maxx, self.maxy, self.maxz = self.getExtremeCoords()

    def __getitem__(self, item):
        return self.triangles[item]

    def __iter__(self):
        return iter(self.triangles)

    def __len__(self):
        return len(self.triangles)

    def getVolume(self):

        volume = 0

        for triangle in self.triangles:

            trimatrix = numpy.matrix(triangle.points)
            volume += numpy.linalg.det(trimatrix)
            # print(triangle.points, numpy.linalg.det(trimatrix))

        # TODO revisar por qué hay qye dividir por 6 el volumen pa que de bien xD (buscar otra fórmula a lo mejor)
        return volume / 6

    def getPoints(self):

        result = {}

        for triangle in self.triangles:
            for point in triangle.points:
                if tuple(point) in result:
                    result[tuple(point)].append(triangle)
                else:
                    result[tuple(point)] = [triangle]

        return result

    def getEdges(self):

        result = []

        for triangle in self.triangles:

            p1, p2, p3 = triangle.points
            if (p1, p2) not in result:
                result.append((p1, p2))
                result.append((p2, p1))
            if (p2, p3) not in result:
                result.append((p2, p3))
                result.append((p3, p2))
            if (p3, p1) not in result:
                result.append((p3, p1))
                result.append((p1, p3))

        return result

    def getExtremeCoords(self):

        minx = float_info.max
        miny = float_info.max
        minz = float_info.max
        maxx = float_info.min
        maxy = float_info.min
        maxz = float_info.min

        for triangle in self.triangles:

            minx = min(min([point[0] for point in triangle.points]), minx)
            miny = min(min([point[1] for point in triangle.points]), miny)
            minz = min(min([point[2] for point in triangle.points]), minz)
            maxx = max(max([point[0] for point in triangle.points]), maxx)
            maxy = max(max([point[1] for point in triangle.points]), maxy)
            maxz = max(max([point[2] for point in triangle.points]), maxz)

        return minx, miny, minz, maxx, maxy, maxz
