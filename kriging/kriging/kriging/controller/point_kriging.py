# -*- coding: utf-8 -*-
import numpy


class PointKriging:

    def __init__(self, searchEllipsoid, model):
        self.searchEllipsoid = searchEllipsoid
        # self.highYield = highYield
        self.model = model
        # self.capping = capping

    def ordinary(self, samples, point):
        """
        Calcula los pesos asociados a cada muestra según el método de Block Kriging Ordinario
        @param samples: [(distance,composite,octant)] muestras con las que se estima el punto
        @param point: (x,y,z) del punto que se quiere estimar
        @return: [w], varianza de kriging
        """

        n = len(samples)  # cantidad de vecinos

        # Se crean la matricez C y vector D
        C_cov = numpy.zeros([n+1, n+1])
        D_cov = numpy.zeros(n+1)

        for i in range(n):

            distance1, comp1, octant1 = samples[i]
            vecino1 = numpy.array([comp1.middlex, comp1.middley, comp1.middlez])

            # se aplica el modelo de variograma con la distnacia entre el punto a estimar y la muestra
            D_cov[i] = self.model.apply(vecino1, point)

            for j in range(i, n):

                distance2, comp2, octant2 = samples[j]
                vecino2 = numpy.array([comp2.middlex, comp2.middley, comp2.middlez])

                # Se aplica el modelo de variograma a los pares de vecinos
                C_cov[i][j] = self.model.apply(vecino1, vecino2)
                C_cov[j][i] = C_cov[i][j]

            # se completa la matriz con los "1" que faltan en la ultima columna y fila
            C_cov[i][n] = 1.
            C_cov[n][i] = 1.

        # se completa la coordenada que falta en la matriz C y vector D
        C_cov[n][n] = 0
        D_cov[n] = 1

        # se invierte C, y se multiplica por D para obtener los pesos W
        C_m = numpy.matrix(C_cov)
        C_inv = C_m.getI().getA()
        W = C_inv.dot(D_cov)

        kriging_variance = 0

        for i in range(n+1):
            kriging_variance -= W[i]*D_cov[i]

        kriging_variance += sum([struct.sill for struct in self.model.structures])

        return W, kriging_variance
