# -*- coding: utf-8 -*-
import math


from geometry.controller.Square import Square


class Polygon:
    def __init__(self, points):

        self.points = []
        self.valid = True
        self.validatePolygon(points)
        if self.valid:
            xs = [x for x, y in points]
            ys = [y for x, y in points]
            self.minx = min(xs)
            self.miny = min(ys)
            self.maxx = max(xs)
            self.maxy = max(ys)

    def __iter__(self):
        return iter(self.points)

    def __getitem__(self, item):
        return self.points[item]

    def getArea(self):

        area = 0

        for i in range(len(self.points)):

            x1, y1 = self.points[i - 1]
            x2, y2 = self.points[i]

            area += x1 * y2 - x2 * y1

        return math.fabs(area) / 2

    def validatePolygon(self, points):

        # Se valida que ningún punto se repita
        for point in points:
            auxpoint = set(points) - {point}
            if len(auxpoint) < len(points) - 1:
                print('La lista de puntos del polígono tiene elmentos repetidos')
                self.valid = False

        # Se valida que ningún segmento se cruce
        segments = [(points[k - 1], points[k]) for k in range(len(points))]

        for i in range(len(segments)):
            # se define la pendiente y el intercepto del segumento i
            (x1a, y1a), (x1b, y1b) = segments[i]
            m1, c1 = getLine(x1a, y1a, x1b, y1b)
            # m1 = (y1a - y1b) / (x1a - x1b) if x1a != x1b else None
            # c1 = y1b - m1 * x1b if m1 is not None else None

            for j in range(i + 2, len(segments)):
                if i == 0 and j == len(segments) - 1:
                    continue

                # se define la pendiente y el intercepto del segmento j
                (x2a, y2a), (x2b, y2b) = segments[j]
                m2, c2 = getLine(x2a, y2a, x2b, y2b)
                # m2 = (y2a - y2b) / (x2a - x2b) if x2a != x2b else None
                # c2 = y2b - m2 * x2b if m2 is not None else None

                # se elimina el caso en que los segmentos no se cruzan por ejes.
                if max(x1a, x1b) < min(x2a, x2b) or \
                   max(x2a, x2b) < min(x1a, x1b) or \
                   max(y1a, y1b) < min(y2a, y2b) or \
                   max(y2a, y2b) < min(y1a, y1b):
                    continue

                if m1 != m2:
                    # se calcula el punto de intersección entre las líneas
                    if m1 is None:
                        x = x1a
                        y = m2 * x + c2
                    elif m2 is None:
                        x = x2a
                        y = m1 * x + c1
                    else:
                        x = (c2 - c1) / (m1 - m2)
                        y = m1 * x + c1

                    # Se verifica que los distintos segmentes no se intersecten entre sí
                    if min(x1a, x1b) <= x <= max(x1a, x1b) and min(x2a, x2b) <= x <= max(x2a, x2b):
                        if min(y1a, y1b) <= y <= max(y1a, y1b) and min(y2a, y2b) <= y <= max(y2a, y2b):
                            print('Los segmentes del polígono se intersectan')
                            print(segments[i])
                            print(segments[j])
                            print(x, y)
                            self.valid = False

        if self.valid:
            self.points = points

    def isInside(self, point):

        X, Y = point
        epsilon = (self.maxy - self.miny) / 100
        # pout = point[0], self.miny - epsilon
        intersections = 0

        for i in range(len(self.points)):

            p1x, p1y = self.points[i - 1]
            p2x, p2y = self.points[i]

            if min(p1x, p2x) < X < max(p1x, p2x) and min(p1y, p2y) < Y:

                m, c = getLine(p1x, p1y, p2x, p2y)
                if m is not None:
                    y = m * X + c
                    if self.miny - epsilon < y < Y:
                        intersections += 1

        return intersections % 2


def defineGeometry():

    # Definición del polígono
    p1 = 3, 5
    p2 = 0, 6
    p3 = -3, 6
    p4 = -3, 5
    p5 = -1, 2
    p6 = 2, 2
    polipoints = [p1, p2, p3, p4, p5, p6]
    poli = Polygon(polipoints)
    print('Polígono válido: ', poli.valid)

    # Definición de los cuadrados
    xmin = -10
    ymin = -10
    dx, dy = 2, 2
    squares = []
    for i in range(10):
        for j in range(10):
            p1 = xmin + i * dx, ymin + j * dy
            p2 = xmin + (i + 1) * dx, ymin + j * dy
            p3 = xmin + (i + 1) * dx, ymin + (j + 1) * dy
            p4 = xmin + i * dx, ymin + (j + 1) * dy
            squares.append(Square([p1, p2, p3, p4]))
    squaresByCenters = dict([(square.center, square) for square in squares])

    return poli, squaresByCenters


def getLine(x1, y1, x2, y2):

    m = (y1 - y2) / (x1 - x2) if x1 != x2 else None
    c = y2 - m * x2 if m is not None else None

    return m, c


def run():

    polygon, squaresByCenters = defineGeometry()
    xmin = -10
    ymin = -10
    dx, dy = 2, 2

    resx = xmin % dx
    resy = ymin % dy

    minsqx = math.floor((polygon.minx - resx) / dx) * dx + resx + dx / 2
    minsqy = math.floor((polygon.miny - resy) / dy) * dy + resy + dy / 2
    maxsqx = math.floor((polygon.maxx - resx) / dx) * dx + resx + dx / 2
    maxsqy = math.floor((polygon.maxy - resy) / dy) * dy + resy + dy / 2

    # todos los cuadrados que podrían colisionar con el polígono
    squares = []
    xsq = minsqx
    while xsq <= maxsqx:
        ysq = minsqy
        while ysq <= maxsqy:
            if (xsq, ysq) in squaresByCenters:
                squares.append(squaresByCenters[(xsq, ysq)])
            ysq += dy
        xsq += dx
    print([s.center for s in squares])
    print(polygon.points)
    pointsIntercept = []

    for i in range(len(polygon.points)):

        x1, y1 = polygon.points[i - 1]
        x2, y2 = polygon.points[i]
        m, c = getLine(x1, y1, x2, y2)
        pointsIntercept.append((x1, y1))
        newPoints = []

        if x1 < x2:

            vertx = (math.floor((x1 - resx) / dx) + resx + 1) * dx
            while vertx < x2:
                # calcular y para ese x en ese segmento
                y = m * vertx + c if m is not None else y1
                if (vertx, y) not in polygon.points:
                    newPoints.append((vertx, y))
                # agregar (x,y) a una lista con el índice de la lista de puntos del poligono para inscrutarla
                vertx += dx

        elif x1 > x2:

            vertx = (math.floor((x1 - resx) / dx) + resx) * dx
            while vertx > x2:
                # calcular y para ese x en ese segmento
                y = m * vertx + c if m is not None else y1
                if (vertx, y) not in polygon.points:
                    newPoints.append((vertx, y))
                # agregar (x,y) a una lista con el índice de la lista de puntos del poligono para inscrutarla
                vertx -= dx

        if y1 < y2:

            verty = (math.floor((y1 - resy) / dy) + resy + 1) * dy
            while verty < y2:
                # calcular y para ese x en ese segmento
                x = (verty - c) / m if m is not None else x1
                if (x, verty) not in polygon.points:
                    newPoints.append((x, verty))
                # agregar (x,y) a una lista con el índice de la lista de puntos del poligono para incrustarla
                verty += dy

        elif y1 > y2:

            verty = (math.floor((y1 - resy) / dy) + resy) * dy
            while verty > y2:
                # calcular y para ese x en ese segmento
                x = (verty - c) / m if m is not None else x1
                if (x, verty) not in polygon.points:
                    newPoints.append((x, verty))
                # agregar (x,y) a una lista con el índice de la lista de puntos del poligono para incrustarla
                verty -= dy

        # se eliminan los elementos repetidos y se ordena la lista de puntos nuevos
        newPoints = list(set(newPoints))
        if x1 < x2:
            newPoints = sorted(newPoints, key=lambda p: p[0])
        elif x1 > x2:
            newPoints = sorted(newPoints, key=lambda p: p[0], reverse=True)
        elif y1 < y2:
            newPoints = sorted(newPoints, key=lambda p: p[1])
        else:
            newPoints = sorted(newPoints, key=lambda p: p[1], reverse=True)

        # se agregan los puntos nuevos a la lista de puntos del polígono nuevo
        pointsIntercept.extend(newPoints)

    polygonPlus = Polygon(pointsIntercept)
    inSquareBySquare = {}
    print(polygonPlus.points)
    for square in squares:

        centerx, centery = square.center
        halfside = square.side / 2
        inside = False

        # puntos del polígono dentro del cuadrado
        inSquare = []
        auxInSquare = []

        for point in polygonPlus:
            polx, poly = point
            if centerx - halfside <= polx <= centerx + halfside and centery - halfside <= poly <= centery + halfside:
                if not inside:
                    inSquare.append(auxInSquare)
                auxInSquare.append(point)
                inside = True
            else:
                inside = False
                auxInSquare = []

        if len(inSquare) > 1:

            aux_ini = None
            aux_end = None

            if inSquare[0][0] == polygonPlus[0] and inSquare[-1][-1] == polygonPlus[-1]:
                aux_ini = inSquare[0].copy()
                aux_end = inSquare[-1].copy()

            if aux_ini is not None:
                aux_end.extend(aux_ini)
                inSquare[0] = aux_end
                inSquare.pop()

        inSquareBySquare[square] = inSquare
        # print(square.center, inSquare, len(inSquare))
    sumatotal = 0
    for square in squares:
        inSquare = inSquareBySquare[square]

        if len(inSquare) == 0:
            if polygon.isInside(square.center):
                print(square.center, square.points, square.points, square.area)
            else:
                print(square.center, [], [], 0)

        for poly in inSquare:
            # se calcula el área de cada polígono dentro del cuadrado
            aux = None

            if len(poly) == 1:
                if polygon.isInside(square.center):
                    print(square.center, square.points, square.points, square.area)
                else:
                    print(square.center, [], [], 0)
            else:
                aux = poly.copy()
                head = poly[-1]
                hx, hy = head

                if head in square.points:
                    # caso en que termine en una esquina del cuadrado
                    ind = square.points.index(head)

                else:
                    # caso en que termine en un lado del cuadrado
                    if hy == square[0][1] and hx < square[1][0]:
                        ind = 0
                    elif hx == square[1][0] and hy < square[2][1]:
                        ind = 1
                    elif hy == square[2][1] and hx > square[3][0]:
                        ind = 2
                    elif hx == square[3][0] and hy > square[0][1]:
                        ind = 3

                closed = False

                while closed is False:

                    nextpoint = []

                    if ind == 0:
                        # avanzar por las x ascendente
                        nextpoint = [po for po in aux[:-1] if po[1] == hy and po[0] > hx]

                    elif ind == 1:
                        # avanzar por las y ascendente
                        nextpoint = [po for po in aux[:-1] if po[0] == hx and po[1] > hy]

                    elif ind == 2:
                        # avanzar por las x descendiente
                        nextpoint = [po for po in aux[:-1] if po[1] == hy and po[0] < hx]

                    elif ind == 3:
                        # avanzar por las y descendiente
                        nextpoint = [po for po in aux[:-1] if po[0] == hx and po[1] < hy]

                    if len(nextpoint) == 0:
                        if ind == 3:
                            ind = -1
                        aux.append(square.points[ind + 1])
                        hx, hy = aux[-1]
                        ind += 1
                    else:
                        closed = True

            if aux is not None:
                area = Polygon(aux).getArea()
                sumatotal += area
                print(square.center, inSquare, aux, area)

    print('area total: ', polygon.getArea())
    print('suma total: ', sumatotal)

if __name__ == '__main__':

    run()
