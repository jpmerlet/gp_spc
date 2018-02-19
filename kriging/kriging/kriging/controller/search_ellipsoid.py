# -*- coding: utf-8 -*-
from geometry.controller.ellipsoid import Ellipsoid
import numpy
import math

from kriging.controller.distance import Distance


class SearchEllipsoid(Ellipsoid):

    def __init__(self, major, medium, minor, bearing, plunge, dip,
                 minSamples=None, maxSamples=None, minSamplesByOctant=None, maxSamplesByOctant=None,
                 minOctantWithSamples=None, maxSamplesByDrillhole=None):

        Ellipsoid.__init__(self, major, medium, minor, bearing, plunge, dip)

        self.minSamples = minSamples
        self.maxSamples = maxSamples
        self.minSamplesByOctant = minSamplesByOctant
        self.maxSamplesByOctant = maxSamplesByOctant
        self.minOctantWithSamples = minOctantWithSamples
        self.maxSamplesByDrillhole = maxSamplesByDrillhole if maxSamplesByDrillhole is not None else 0

    def selectSamples(self, samples):
        """
        Selecciona los compositos segun los parametros que se le entreguen
        @param octants:
        @param samples: Lista con tuplas composito, distancia (ordenado), pto rotado, hole_id
        @param max_samp_dh: Entero maxima cantidad de muestras por sondaje
        @param minSamples: Minima cantidad de muestras para estimar
        @param maxSamples: Maxima cantidad de muestras para estimar
        @param oct_param_t: Tupla, parametros para la busqueda por octantes
                            [0] : maximo de muestras por octante
                            [1] : minimo de muestras por octante
                            [2] : minimo numero de octantes con muestras ( opcional )
        @param flag: 0 -> no imprime, 1 -> imprime
        """

        if self.minSamples > len(samples):
            return []

        dhid_d = {}
        octant_s = [0] * 8  # cantidad de muestras por octante
        filled_oct = 0  # cantidad de octantes llenos
        result = []  # lista con los compositos para estimar

        maxSamplesByOct = self.maxSamplesByOctant if self.maxSamplesByOctant is not None else self.maxSamples
        minSamplesByOct = self.minSamplesByOctant if self.minSamplesByOctant is not None else 0

        minOctWithSamples = self.minOctantWithSamples if self.minOctantWithSamples is not None else 0

        for distance, composite, octant in samples:
            holeid = composite.holeid
        # for sample in samples:

            # distance, holeid, x, y, z, value = sample[:6]
            # octant = self.getOctant((x, y, z))
            # if not octants:
            #     pass
            # else:
            #     distance, holeid, x, y, z, value, octant = sample

            # se revisa que el octante no este lleno
            if octant_s[octant - 1] < maxSamplesByOct:

                # se revisa la cantidad de muestras por sondaje
                if self.maxSamplesByDrillhole > 0:
                    if holeid in dhid_d:

                        dhid_d[holeid] += 1
                        if dhid_d[holeid] > self.maxSamplesByDrillhole:
                            dhid_d[holeid] -= 1
                            continue
                    else:
                        dhid_d[holeid] = 1

                octant_s[octant - 1] += 1
                result.append((distance, composite, octant))  # se agrega el vecino a la lista resultado

                # se actualiza el numero de muestras en ese octante
                if octant_s[octant - 1] == minSamplesByOct:
                    filled_oct += 1

            # Si se supera el numero maximo de muestras por estimacion
            # se interrumpe el ciclo

            if sum(octant_s) == self.maxSamples:
                break

        # Si se cumple la condicion principal, se envia la lista de vecinos
        # notar que esta ordenada segun distancia y con el centro original
        if filled_oct >= minOctWithSamples and len(result) >= self.minSamples:
            return result

        else:
            return []

    def getOctant(self, point):
        """
        Se revisa a que octante pertenece la muestra y se retorna el numero del octante.
        @param p0: punto al que se le quiere determinar el octante
        @return: int con el id del octante
        """
        x, y, z = point

        if x > 0 and y >= 0:
            octant = 6 if z >= 0 else 5

        elif x <= 0 < y:
            octant = 8 if z >= 0 else 7

        elif x < 0 and y <= 0:
            octant = 4 if z >= 0 else 3

        elif x >= 0 > y:
            octant = 2 if z >= 0 else 1

        else:
            octant = 8  # caso en que x = y = 0

        return octant

    def searchPointsInDiscretizedPoints(self, point, discretizedPoints, distanceType='CARTESIAN'):

        stepx = self.major
        stepy = self.medium
        stepz = self.minor
        # stepx = self.major / 2
        # stepy = self.medium / 2
        # stepz = self.minor / 2

        px = math.floor(point[0] / stepx) * stepx
        py = math.floor(point[1] / stepy) * stepy
        pz = math.floor(point[2] / stepz) * stepz

        def movePoint(point0, point1):
            px, py, pz = point0
            x, y, z = point1
            return tuple(numpy.array((x-px, y-py, z-pz)))

        rotatePoints = []
        # for x_, y_, z_ in [(x, y, z) for x in [px - 2 * stepx, px - stepx, px, px + stepx, px + 2 * stepx]
        #                              for y in [py - 2 * stepy, py - stepy, py, py + stepy, py + 2 * stepy]
        #                              for z in [pz - 2 * stepz, pz - stepz, pz, pz + stepz, pz + 2 * stepz]]:
        for x_, y_, z_ in [(x, y, z) for x in [px - stepx, px, px + stepx]
                                     for y in [py - stepy, py, py + stepy]
                                     for z in [pz - stepz, pz, pz + stepz]]:
            key = (x_, y_, z_)
            if key in discretizedPoints:
                rotatePoints.extend(discretizedPoints[key])

        points = []
        for rotatedPoint in rotatePoints:
            movedPoint = movePoint(point, rotatedPoint)
            x, y, z = movedPoint
            if abs(x) <= self.major and abs(y) <= self.medium and abs(z) <= self.minor:
                points.append((rotatedPoint, movedPoint))
            # samples = [ ]

        result = []
        for rotatedPoint, movedPoint in points:
            anisotropicDistance, cartesianDistance = Distance.distanceToOrigin(movedPoint, self.anisotropyMatrix)
            if anisotropicDistance < self.major:
                result.append((cartesianDistance if distanceType == 'CARTESIAN' else anisotropicDistance,
                               rotatedPoint, movedPoint, self.getOctant(movedPoint)))

        return result

    # def distance(self, point):
    #     px, py, pz = point
    #     xani, yani, zani = numpy.array((px, py, pz)).dot(self.anisotropyMatrix)
    #     anisotropicDistance = math.sqrt(xani ** 2 + yani ** 2 + zani ** 2)
    #     cartesianDistance = math.sqrt(px ** 2 + py ** 2 + pz ** 2)
    #     return anisotropicDistance, cartesianDistance

    # def searchSamplesInDiscretizedSamples(self, point, discretizedSamples, distanceType=Distance.CARTESIAN):
    #     stepx = self.major
    #     stepy = self.medium
    #     stepz = self.minor
    #
    #     px, py, pz = point
    #     px = math.floor(px / stepx) * stepx
    #     py = math.floor(py / stepy) * stepy
    #     pz = math.floor(pz / stepz) * stepz
    #
    #     def moveSample(point, sample):
    #         px, py, pz = point
    #         holeid, x, y, z, value = sample
    #         return numpy.array((holeid, x-px, y-py, z-pz, value))
    #
    #     aux = []
    #     for x_, y_, z_ in [(x, y, z) for x in [px - stepx, px, px + stepx]
    #                                  for y in [py - stepy, py, py + stepy]
    #                                  for z in [pz - stepz, pz, pz + stepz]]:
    #         key = (x_, y_, z_)
    #         if key in discretizedSamples:
    #             aux.extend(discretizedSamples[key])
    #
    #     samples = [moveSample(point, sample) for sample in aux]
    #
    #     result = []
    #     for holeid, x, y, z, value in samples:
    #         anisotropicDistance, cartesianDistance = self.distance((x, y, z))
    #         if anisotropicDistance < self.major:
    #             if distanceType == Distance.CARTESIAN:
    #                 result.append((cartesianDistance, holeid, x, y, z, value))
    #             else:
    #                 result.append((anisotropicDistance, holeid, x, y, z, value))
    #
    #     return result
    #
    # def searchSamplesInDiscretizedSamples(self, point, discretizedSamples, distanceType=Distance.CARTESIAN):
    #     stepx = self.major
    #     stepy = self.medium
    #     stepz = self.minor
    #
    #     px, py, pz = point
    #     px = math.floor(px / stepx) * stepx
    #     py = math.floor(py / stepy) * stepy
    #     pz = math.floor(pz / stepz) * stepz
    #
    #     def moveSample(point, sample):
    #         px, py, pz = point
    #         holeid, x, y, z, value = sample
    #         return numpy.array((holeid, x-px, y-py, z-pz, value))
    #
    #     aux = []
    #     for x_, y_, z_ in [(x, y, z) for x in [px - stepx, px, px + stepx]
    #                                  for y in [py - stepy, py, py + stepy]
    #                                  for z in [pz - stepz, pz, pz + stepz]]:
    #         key = (x_, y_, z_)
    #         if key in discretizedSamples:
    #             aux.extend(discretizedSamples[key])
    #
    #     samples = [moveSample(point, sample) for sample in aux]
    #
    #     result = []
    #     for holeid, x, y, z, value in samples:
    #         anisotropicDistance, cartesianDistance = self.distance((x, y, z))
    #         if anisotropicDistance < self.major:
    #             if distanceType == Distance.CARTESIAN:
    #                 result.append((cartesianDistance, holeid, x, y, z, value))
    #             else:
    #                 result.append((anisotropicDistance, holeid, x, y, z, value))
    #
    #     return result
    #
    #
    #
    #
    #
    # def __derotationMatrix(self):
    #     """
    #     Calcula la matriz de rotacion del punto
    #     @param angle_s: angulos de rotacion del elipsoide (bearing, plunge, dip)
    #     @return: Lista[][] con la matriz de rotacion
    #     """
    #     # bearing, plunge, dip = angles
    #     cosa = numpy.cos(float(self.bearing) * numpy.pi / 180)
    #     sina = - numpy.sin(float(self.bearing) * numpy.pi / 180)
    #     cosb = numpy.cos(float(self.plunge) * numpy.pi / 180)
    #     sinb = - numpy.sin(float(self.plunge) * numpy.pi / 180)
    #     cosc = numpy.cos(float(self.dip) * numpy.pi / 180)
    #     sinc = - numpy.sin(float(self.dip) * numpy.pi / 180)
    #
    #     # se crean las matrices de rotacion
    #     M1 = numpy.matrix([[cosa, sina, 0.], [-sina, cosa, 0.], [0., 0., 1.]])
    #     M2 = numpy.matrix([[1., 0., 0.], [0., cosb, -sinb], [0., sinb, cosb]])
    #     M3 = numpy.matrix([[cosc, 0., -sinc], [0., 1., 0.], [sinc, 0., cosc]])
    #
    #     # se multiplican las matrices para tener el efecto combinado de las rotaciones
    #     MT = M3 * (M2 * M1)
    #     return MT.getA()

    def selectSamplesSimulation(self, samples):

        if self.minSamples > len(samples):
            return []

        result = []

        for distance, composite, octant in samples:

            if len(result) < self.maxSamples:
                result.append((distance, composite, octant))

        if len(result) >= self.minSamples:
            return result

        else:
            return []
