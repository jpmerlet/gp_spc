# -*- coding: utf-8 -*-
import numpy


class Ellipsoid:

    def __init__(self, major, medium, minor, bearing, plunge, dip):
        self.major = major
        self.medium = medium
        self.minor = minor
        self.bearing = bearing
        self.plunge = plunge
        self.dip = dip

        self.anisotropyMatrix = self.__anisotropyMatrix()
        self.rotationMatrix = self.__rotationMatrix()

    def __anisotropyMatrix(self):
        """
        Calcula la matriz de anisotropia
        """
        afac1 = self.major / self.medium
        afac2 = self.major / self.minor

        return numpy.array([[afac1, 0., 0.], [0., 1., 0.], [0., 0., afac2]])

    def __rotationMatrix(self):
        """
        Calcula la matriz de rotacion del punto
        """
        # bearing, plunge, dip = angles
        cosa = numpy.cos(float(self.bearing) * numpy.pi / 180)
        sina = numpy.sin(float(self.bearing) * numpy.pi / 180)
        cosb = numpy.cos(float(self.plunge) * numpy.pi / 180)
        sinb = numpy.sin(float(self.plunge) * numpy.pi / 180)
        cosc = numpy.cos(float(self.dip) * numpy.pi / 180)
        sinc = numpy.sin(float(self.dip) * numpy.pi / 180)

        # se crean las matrices de rotacion
        M1 = numpy.matrix([[cosa, sina, 0.], [-sina, cosa, 0.], [0., 0., 1.]])
        M2 = numpy.matrix([[1., 0., 0.], [0., cosb, -sinb], [0., sinb, cosb]])
        M3 = numpy.matrix([[cosc, 0., -sinc], [0., 1., 0.], [sinc, 0., cosc]])

        # se multiplican las matrices para tener el efecto combinado de las rotaciones
        MT = M1 * (M2 * M3)
        return MT.getA()
