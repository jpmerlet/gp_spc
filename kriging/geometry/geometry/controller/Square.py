# -*- coding: utf-8 -*-


class Square:

    def __init__(self, points):

        self.valid = True
        self.points = []

        # Se revisa que el cuadrado tenga 4 puntos (si tiene más se usan los 4 primeros)
        if len(points) < 4:
            print('no se puede crear un cuadrado con menos de 4 puntos')
            self.valid = False

        # se revisa que los puntos estén ordenados correctamente y que los lados sean iguales
        else:
            x1, y1 = points[0]
            x2, y2 = points[1]
            x3, y3 = points[2]
            x4, y4 = points[3]

            if x1 != x4 or x2 != x3 or y1 != y2 or y3 != y4:
                print('las puntos no están ordenados correctamente')
                self.valid = False

            elif not(y4 - y1 == y3 - y2 == x2 - x1 == x3 - x4 > 0):
                print('los lados del cuadrado no son iguales')
                self.valid = False

            else:
                self.points = points[0:4]
                self.center = (x1 + x2) / 2, (y1 + y4) / 2
                self.side = x2 - x1
                self.area = self.side ** 2

    def __getitem__(self, item):
        return self.points[item]
