# -*- coding: utf-8 -*-
import numpy

# from drillhole.controller import Structure
# from drilling.controller.structure import Structure
from variogram.controller.structure import Structure
import math

class Model:

    def __init__(self, nugget, structures):
        """
        Crea un objeto modelo con toda la informacion necesaria para hacer una estimacion
        @param nugget : valor del efecto pepita (nugget effect)
        @param structures: Lista con las estructuras anidadas del variograma
        """

        self.nugget = nugget
        self.structures = structures

    def distance(self, point, strucure):
        """
        Calcula la distancia entre dos puntos teniendo en cuenta la anisotropia
        del variograma

        @param punto: Punto3D que representa el vector que une los dos puntos
        @param strucure: estructura del variograma que se esta usando
        @return: distancia anisotropica entre los dos puntos
        """

        rotation = point.dot(strucure.ellipsoid.rotationMatrix)
        anisotropy = rotation.dot(strucure.ellipsoid.anisotropyMatrix)

        # return numpy.sqrt(anisotropy[0] ** 2 + anisotropy[1] ** 2 + anisotropy[2] ** 2)
        return math.sqrt(sum(anisotropy ** 2))

    def apply(self, point1, point2=None):
        """
        Calcula la covarianza entre los dos puntos3D entregados.
        @param point1: Numpy array desde donde se esta midiendo la distancia
        @param point2: Numpy array hasta el cual se mide la distancia
        @return: Covarianza para la distancia entre los dos puntos
        """

        covariance = 0
        # x1, y1, z1 = point1
        # x2, y2, z2 = point2
        if point2 is not None:
            point = point2 - point1
        else:
            point = point1
        # point = numpy.array([x1 - x2, y1 - y2, z1 - z2])

        for structure in self.structures:

            h = self.distance(point, structure)

            # si es el mismo punto, se entrega la pepita mas las meceta de cada estructura
            if not h:
                meseta = self.nugget
                for s in self.structures:
                    meseta += s.sill
                return meseta

            hr = h / structure.ellipsoid.major

            if structure.name == Structure.SPHERIC:
                if h <= structure.ellipsoid.major:
                    covariance += structure.sill * (1 - hr * (1.5 - 0.5 * hr ** 2))

            elif structure.name == Structure.EXPONENTIAL:
                covariance += structure.sill * (numpy.exp(-3 * hr))

            elif structure.name == Structure.GAUSSIAN:
                covariance += structure.sill * (numpy.exp(- 3 * hr ** 2))

        return covariance