import math
import numpy


class Triangle:

    def __init__(self, points):

        self.points = points
        self.area = self.getArea()
        self.orientation = 'CLOCKWISE' if self.area > 0 else 'COUNTERCLOCKWISE'
        self.area = math.fabs(self.area)
        self.normal = self.getNormalVector()
        self.intercept = -numpy.dot(self.points[0], self.normal)
        print(self.normal, self.intercept)
        self.minx, self.miny, self.minz, self.maxx, self.maxy, self.maxz = self.getExtremeCoords()

    def __getitem__(self, item):
        return self.points[item]

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def getNormalVector(self):
        # El vector normal está definido hacia afuera del sólido cuando los puntos están clockwise
        p1, p2, p3 = self.points
        v1 = p3 - p1
        v2 = p2 - p1
        return numpy.cross(v1, v2)

    def getExtremeCoords(self):

        minx = min(point[0] for point in self.points)
        miny = min(point[1] for point in self.points)
        minz = min(point[2] for point in self.points)
        maxx = max(point[0] for point in self.points)
        maxy = max(point[1] for point in self.points)
        maxz = max(point[2] for point in self.points)

        return minx, miny, minz, maxx, maxy, maxz

    def getArea(self):

        area = 0

        for i in range(len(self.points)):
            x1, y1, _ = self.points[i - 1]
            x2, y2, _ = self.points[i]

            area += x2 * y1 - x1 * y2

        return area / 2
