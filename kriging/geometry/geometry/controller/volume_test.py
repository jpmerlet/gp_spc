from geometry.controller.solid import Solid
from geometry.controller.triangle import Triangle
from geometry.controller.cube import Cube
import numpy
import math


def run():

    # p1 = [10, 10, 10]
    # p2 = [20, 10, 10]
    # p3 = [20, 20, 10]
    # p4 = [10, 20, 10]
    # p5 = [10, 10, 20]
    # p6 = [20, 10, 20]
    # p7 = [20, 20, 20]
    # p8 = [10, 20, 20]
    #
    # t1 = Triangle([p1, p2, p4])
    # t2 = Triangle([p2, p3, p4])
    # t3 = Triangle([p2, p6, p3])
    # t4 = Triangle([p3, p6, p7])
    # t5 = Triangle([p1, p5, p2])
    # t6 = Triangle([p2, p5, p6])
    # t7 = Triangle([p8, p1, p4])
    # t8 = Triangle([p1, p8, p5])
    # t9 = Triangle([p8, p7, p5])
    # t10 = Triangle([p5, p7, p6])
    # t11 = Triangle([p7, p4, p3])
    # t12 = Triangle([p4, p7, p8])
    #
    # solido = Solid([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
    # print(solido.volume)

    p1 = numpy.array([20, 20, 20])
    p2 = numpy.array([20, 0, 20])
    p3 = numpy.array([40, 20, 20])
    p4 = numpy.array([20, 20, 40])

    t1 = Triangle([p1, p4, p2])
    t2 = Triangle([p3, p4, p1])
    t3 = Triangle([p4, p3, p2])
    t4 = Triangle([p1, p2, p3])

    solido = Solid([t1, t2, t3, t4])
    print('volumen', solido.volume)

    cube1 = Cube((20, 20, 20), 10, 10, 10)
    # cube2 = Cube((15, 15, 15), 10, 10, 10)
    # cube3 = Cube((-5, -5, -5), 10, 10, 10)
    # cubes = [cube1, cube2, cube3]

    # Encontrar todos los triángulos que tienen alguna parte dentro del cubo
    cube1.getIntersection(solido)


if __name__ == '__main__':
    run()
