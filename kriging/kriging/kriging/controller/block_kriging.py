# -*- coding: utf-8 -*-
from block_model.controller.block import Block
import math
import numpy
import warnings
numpy.seterr(over='warn', invalid='warn')

warnings.filterwarnings('error')


class BlockKriging:

    def __init__(self, searchEllipsoid, model, discretization, highYield, capping, blockSize):
        self.searchEllipsoid = searchEllipsoid
        self.discretization = discretization
        self.highYield = highYield
        self.model = model
        self.blockSize = blockSize
        self.capping = capping
        self.centers = []

        sizex, sizey, sizez = self.discretization.sizex, self.discretization.sizey, self.discretization.sizez
        for i in range(0, sizex):
            for j in range(0, sizey):
                for k in range(0, sizez):
                    self.centers += [numpy.array([self.blockSize.lenx * (2 * i - sizex + 1) / 2. / sizex,
                                                  self.blockSize.leny * (2 * j - sizey + 1) / 2. / sizey,
                                                  self.blockSize.lenz * (2 * k - sizez + 1) / 2. / sizez])]

        self.blockCovariance = 0
        discBlocks = len(self.centers)
        for i in range(discBlocks):
            for j in range(discBlocks):
                self.blockCovariance += self.model.apply(self.centers[i], self.centers[j])
                if i == j:
                    self.blockCovariance -= self.model.nugget

        self.blockCovariance /= (discBlocks * discBlocks)

    def ordinary(self, samples, lengthx, lengthy, lengthz, block):
        """
        Calcula los pesos asociados a cada muestra según el método de Block Kriging Ordinario
        @param samples: [(distance,holeid,x,y,z,value,octant)] muestras con las que se estima el bloque
        @param lengthx: largo del bloque en el eje x
        @param lengthy: largo del bloque en el eje y
        @param lengthz: largo del bloque en el eje z
        @return: [w],var lista con los pesos calculados para cada muestra, varianza de kriging
        """

        x, y, z = block.x, block.y, block.z
        sizex = self.discretization.sizex
        sizey = self.discretization.sizey
        sizez = self.discretization.sizez
        disnum = sizex * sizey * sizez

        centers = []
        for i in range(sizex):
            for j in range(sizey):
                for k in range(sizez):
                    centers += [numpy.array([x + lengthx * (2 * i - sizex + 1) / 2. / sizex,
                                             y + lengthy * (2 * j - sizey + 1) / 2. / sizey,
                                             z + lengthz * (2 * k - sizez + 1) / 2. / sizez])]

        n = len(samples)  # cantidad de vecinos

        # Matriz C
        C_cov = numpy.empty([n+1, n+1])
        # C_cov = numpy.array([[0.] * (n + 1)] * (n + 1))
        for i in range(n):

            # distance1, holeid1, x1, y1, z1, octant1 = samples[i]
            distance1, comp1, octant1 = samples[i]
            vecino1 = numpy.array([comp1.middlex, comp1.middley, comp1.middlez])

            for j in range(i, n):
                # distance2, holeid2, x2, y2, z2, octant2 = samples[j]
                distance2, comp2, octant2 = samples[j]
                # v1 = samples[i][0]
                # v2 = samples[j][0]
                # Se rescata la posicion de las muestras

                # vecino1 = numpy.array([x1, y1, z1])

                # vecino2 = numpy.array([x2, y2, z2])
                vecino2 = numpy.array([comp2.middlex, comp2.middley, comp2.middlez])

                # Se aplica el modelo de variograma a los pares de vecinos
                C_cov[i][j] = self.model.apply(vecino1, vecino2)
                C_cov[j][i] = C_cov[i][j]
            # se completa la matriz con los "1" que faltan en la ultima columna y fila
            C_cov[i][n] = 1.
            C_cov[n][i] = 1.

        # Vector D
        D_cov = numpy.empty(n+1)
        # D_cov = numpy.array([0.] * (n + 1))
        for i in range(n):

            distance, comp, octant = samples[i]
            vecino1 = numpy.array([comp.middlex, comp.middley, comp.middlez])

            for j in range(disnum):
                # se aplica el modelo de variograma a uno de los vecinos con respecto al centro del bloque
                b_centro = centers[j]
                aux_t = self.model.apply(vecino1, b_centro)
                D_cov[i] += aux_t

            # se promedia la covarianza de la muestra por todos los sub-bloques
            D_cov[i] = D_cov[i] / disnum

        # se completa la coordenada que falta en la matriz C y vector D
        C_cov[n][n] = 0
        D_cov[n] = 1

        # se invierte C, y se multiplica por D para obtener los pesos W
        C_m = numpy.matrix(C_cov)
        C_inv = C_m.getI().getA()
        W = C_inv.dot(D_cov)

        # if variance:
        kriging_variance = 0

        for i in range(n+1):
            kriging_variance -= W[i]*D_cov[i]

        if disnum == 1:
            kriging_variance += (1 - self.model.nugget)
        else:
            kriging_variance += self.blockCovariance

        return W, kriging_variance

    # @profile
    def simple(self, samples, block, lookUpTable=None):
        """
        Calcula los pesos asociados a cada muestra según el método de Block Kriging Simple
        @param samples: [(distance,holeid,x,y,z,value,octant)] muestras con las que se estima el bloque
        @param block: Block que se quiere krigear
        @param lookUpTable: Dictionary para buscar el valor de la covarianza entre dos bloques
        @return: [w],var lista con los pesos calculados para cada muestra, varianza de kriging
        """

        x, y, z = block.x, block.y, block.z
        sizex = self.discretization.sizex
        sizey = self.discretization.sizey
        sizez = self.discretization.sizez
        disnum = sizex * sizey * sizez

        centers = []
        for i in range(sizex):
            for j in range(sizey):
                for k in range(sizez):
                    centers += [numpy.array([x + self.blockSize.lenx * (2 * i - sizex + 1) / 2. / sizex,
                                             y + self.blockSize.leny * (2 * j - sizey + 1) / 2. / sizey,
                                             z + self.blockSize.lenz * (2 * k - sizez + 1) / 2. / sizez])]

        n = len(samples)  # cantidad de vecinos

        # Matriz C
        C_cov = numpy.empty([n, n])
        for i in range(n):

            distance1, comp1, octant1 = samples[i]
            if isinstance(comp1, Block):
                vecino1 = numpy.array([comp1.x, comp1.y, comp1.z])
            else:
                vecino1 = numpy.array([comp1.middlex, comp1.middley, comp1.middlez])

            for j in range(i, n):

                distance2, comp2, octant2 = samples[j]
                if isinstance(comp2, Block):
                    vecino2 = numpy.array([comp2.x, comp2.y, comp2.z])
                else:
                    vecino2 = numpy.array([comp2.middlex, comp2.middley, comp2.middlez])

                covValue = None
                # se busca el valor de
                if lookUpTable is not None and isinstance(comp1, Block) and isinstance(comp2, Block):
                    distanceVecino = vecino2 - vecino1
                    indx = math.fabs(int(distanceVecino[0] / comp1.blockModel.xLength))
                    indy = math.fabs(int(distanceVecino[1] / comp1.blockModel.yLength))
                    indz = math.fabs(int(distanceVecino[2] / comp1.blockModel.zLength))
                    if (indx, indy, indz) in lookUpTable:
                        covValue = lookUpTable[(indx, indy, indz)]
                        lookUpTable['uso'] += 1

                # Se aplica el modelo de variograma a los pares de vecinos
                if covValue is None:
                    covValue = self.model.apply(vecino1, vecino2)
                    # lookUpTable['no-uso'] += 1

                C_cov[i][j] = covValue
                C_cov[j][i] = C_cov[i][j]

        # Vector D
        D_cov = numpy.zeros(n)

        for i in range(n):

            distance, comp, octant = samples[i]
            if isinstance(comp, Block):
                vecino1 = numpy.array([comp.x, comp.y, comp.z])
            else:
                vecino1 = numpy.array([comp.middlex, comp.middley, comp.middlez])

            for j in range(disnum):

                b_centro = centers[j]
                aux_t = None
                # se busca el valor de
                if lookUpTable is not None and isinstance(comp, Block) and isinstance(b_centro, Block):
                    distanceVecino = b_centro - vecino1
                    indx = math.fabs(int(distanceVecino[0] / comp.blockModel.xLength))
                    indy = math.fabs(int(distanceVecino[1] / comp.blockModel.yLength))
                    indz = math.fabs(int(distanceVecino[2] / comp.blockModel.zLength))
                    if (indx, indy, indz) in lookUpTable:
                        aux_t = lookUpTable[(indx, indy, indz)]
                        lookUpTable['uso'] += 1

                # Se aplica el modelo de variograma a los pares de vecinos
                if aux_t is None:
                    aux_t = self.model.apply(vecino1, b_centro)
                    # lookUpTable['no-uso'] += 1
                    
                # se aplica el modelo de variograma a uno de los vecinos con respecto al centro del bloque
                
                # aux_t = self.model.apply(vecino1, b_centro)
                # print('aux', aux_t)
                D_cov[i] += aux_t
                
            # se promedia la covarianza de la muestra por todos los sub-bloques
            D_cov[i] = D_cov[i] / disnum

        # se invierte C, y se multiplica por D para obtener los pesos W
        C_m = numpy.matrix(C_cov)
        C_inv = C_m.getI().getA()
        W = C_inv.dot(D_cov)

        kriging_variance = 0

        for i in range(n):
            try:
                kriging_variance -= W[i] * D_cov[i]
            except Warning:
                print(D_cov, W, i)

        if disnum == 1:
            kriging_variance += (1 - self.model.nugget)
        else:
            kriging_variance += self.blockCovariance

        return W, kriging_variance
