# -*- coding: utf-8 -*-

import numpy


class Cube:

    def __init__(self, center, dx, dy, dz):

        self.centerx, self.centery, self.centerz = center
        self.dx = dx
        self.dy = dy
        self.dz = dz

        xcoord = numpy.array([-1, 1, 1, -1, -1, 1, 1, -1]) * dx / 2 + self.centerx
        ycoord = numpy.array([-1, -1, -1, -1, 1, 1, 1, 1]) * dy / 2 + self.centery
        zcoord = numpy.array([-1, -1, 1, 1, -1, -1, 1, 1]) * dz / 2 + self.centerz

        self.points = list(zip(xcoord, ycoord, zcoord))
        self.faces = self.getFaces()
        # print(self.points)

    def getFaces(self):
        faces = []
        p1, p2, p3, p4, p5, p6, p7, p8 = self.points
        faces.append(Face("FRONT", [p4, p3, p2, p1]))
        faces.append(Face("BACK", [p5, p6, p7, p8]))
        faces.append(Face("LEFT", [p4, p1, p5, p8]))
        faces.append(Face("RIGHT", [p2, p3, p7, p6]))
        faces.append(Face("UP", [p3, p4, p8, p7]))
        faces.append(Face("DOWN", [p1, p2, p6, p5]))

        # faces["FRONT"] = Face("FRONT", [p4, p3, p2, p1])
        # faces["BACK"] = Face("BACK", [p5, p6, p7, p8])
        # faces["LEFT"] = Face("LEFT", [p4, p1, p5, p8])
        # faces["RIGHT"] = Face("RIGHT", [p2, p3, p7, p6])
        # faces["UP"] = Face("UP", [p3, p4, p8, p7])
        # faces["DOWN"] = Face("DOWN", [p1, p2, p6, p5])
        return faces

    def getIntersection(self, solid):
        # La idea del algoritmo es encontrar los puntos de intersección de los lados del triángulo con los planos
        # donde están contenidas cada una de las 6 caras del bloque. Si un triángulo intercepta una cara, lo va a hacer
        # por lo menos dos veces (a menos que uno de los vértices caiga justo en la cara), con esos dos puntos se puede
        # calcular la recta que los unes y se puede determinar si esa recta se intersecta con la cara, lo que significa
        # que el triángulo corta esa cara y hay que considerarlo para el sólido resultante.

        # Aquí se van a guardar los triángulos que formarían el sólido contenido en el cubo
        newTriangles = []

        potentialTriangles = []
        # Se toman todos los triángulos que podrían estar intersectando con el cubo
        for triangle in solid.triangles:
            if triangle.minx <= self.centerx + self.dx / 2 and triangle.maxx >= self.centerx - self.dx / 2 and \
               triangle.miny <= self.centery + self.dy / 2 and triangle.maxy >= self.centery - self.dy / 2 and \
               triangle.minz <= self.centerz + self.dz / 2 and triangle.maxz >= self.centerz - self.dz / 2:

                potentialTriangles.append(triangle)
                # print('en rango', triangle.points)
            # else:
            #     # TODO: Este caso no sirve, es para ver qué triángulo no iba solamente, borrar luego
            #     print('fuera de rango', triangle.points)

        # El cubo está completamente fuera del triángulo
        if len(potentialTriangles) == 0:
            return None

        for triangle in potentialTriangles:
            print(triangle.points)
            print(triangle.normal)
            print(triangle.intercept)
            print(self.centerx, self.centery, self.centerz)

            for face in self.faces:

                intersections = []
                # vector paralelo a la recta de intersección
                line = numpy.cross(triangle.normal, face.normal)
                print(face.name)
                print(face.points)
                print(face.normal, face.intercept)
                print(line)

                for i in range(len(triangle)):
                    p1 = triangle[i - 1]
                    p2 = triangle[i]
                    t = p2 - p1

                    # Caso en que no hay puntos de intersección con el plano
                    if face.fixValue < p1[face.fixCoord] and face.fixValue < p2[face.fixCoord] or \
                       face.fixValue > p1[face.fixCoord] and face.fixValue > p2[face.fixCoord]:
                        # Este caso no me sirve, TODO borrar cuando algoritmo esté listo
                        pass

                    # Caso en que hay un punto de intersección con el plano de la cara
                    elif face.fixValue != p1[face.fixCoord] and face.fixValue != p2[face.fixCoord]:
                        if face.fixCoord == 0:
                            x = face.fixValue
                            y = t[1] / t[0] * (face.fixValue - p1[0]) + p1[1]
                            z = t[2] / t[0] * (face.fixValue - p1[0]) + p1[2]
                        elif face.fixCoord == 1:
                            x = t[0] / t[1] * (face.fixValue - p1[1]) + p1[0]
                            y = face.fixValue
                            z = t[2] / t[1] * (face.fixValue - p1[1]) + p1[2]
                        else:
                            x = t[0] / t[2] * (face.fixValue - p1[2]) + p1[0]
                            y = t[1] / t[2] * (face.fixValue - p1[2]) + p1[1]
                            z = face.fixValue
                        # punto de intersección del lado del triángulo con el plano
                        # este punto es unico para este lado por las condiciones del caso
                        # tiene que haber otro u otros al hacer lo mismo con los otros lados
                        auxpoint = numpy.array([x, y, z])

                        if not any(all(auxpoint == aux) for aux in intersections):
                            intersections.append(auxpoint)

                    # caso en que el segundo punto está en el plano y el primero no
                    elif face.fixValue != p1[face.fixCoord] and face.fixValue == p2[face.fixCoord]:
                        if not any(all(p2 == aux) for aux in intersections):
                            intersections.append(p2)

                    # caso en que el primer punto está en el plano y el segundo no
                    elif face.fixValue == p1[face.fixCoord] and face.fixValue != p2[face.fixCoord]:
                        if not any(all(p1 == aux) for aux in intersections):
                            intersections.append(p1)

                    # caso en que ambos puntos están en el plano (caos)
                    elif face.fixValue == p1[face.fixCoord] and face.fixValue == p2[face.fixCoord]:
                        if not any(all(p1 == aux) for aux in intersections):
                            intersections.append(p1)
                        if not any(all(p2 == aux) for aux in intersections):
                            intersections.append(p2)

                # Después de terminar de revisar los 3 lados del triángulo puedo tener 3 opciones:
                # CASO 1: no hay punto de intersección
                # CASO 2: hay un punto de interesección
                # CASO 3: hay dos puntos de intersección
                # CASO 4: hay tres puntos de intersección

                # Análisis de casos
                # CASO 1: No hacer nada
                # CASO 2: Significa que...
                # CASO 3: Lo usual. Se debe crear una recta que una los dos puntos, listar los triángulos que contienen
                #         a esa recta
                # CASO 4: Triángulo completo está dentro del plano. Aplicar algoritmo de intersección de polígonos 2D

                print('intersections: ', intersections)
                print()


class Face:

        def __init__(self, name, points):

            self.name = name
            self.points = points
            if self.name == "FRONT":
                self.normal = numpy.array([0, -1, 0])
                self.fixValue = points[0][1]
                self.fixCoord = 1
            elif self.name == "BACK":
                self.normal = numpy.array([0, 1, 0])
                self.fixValue = points[0][1]
                self.fixCoord = 1
            elif self.name == "LEFT":
                self.normal = numpy.array([-1, 0, 0])
                self.fixValue = points[0][0]
                self.fixCoord = 0
            elif self.name == "RIGHT":
                self.normal = numpy.array([1, 0, 0])
                self.fixValue = points[0][0]
                self.fixCoord = 0
            elif self.name == "UP":
                self.normal = numpy.array([0, 0, 1])
                self.fixValue = points[0][2]
                self.fixCoord = 2
            else:
                self.normal = numpy.array([0, 0, -1])
                self.fixValue = points[0][2]
                self.fixCoord = 2
            self.intercept = -numpy.dot(self.normal, self.points[0])
