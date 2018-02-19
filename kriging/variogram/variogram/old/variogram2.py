# import numpy
# import math
#
# PI = numpy.pi
#
#
# class Variogram:
#     def __init__(self, lagSize, lagCount, lagOffset, lagTolerance, vartype, direction, column, directions=None):
#
#         self.variogramData = {}
#         self.size = lagSize
#         self.lagOffset = lagOffset
#         self.lagCount = lagCount
#         self.lags = [self.lagOffset + i * lagSize for i in range(lagCount + 1)]
#         self.lagTolerance = lagTolerance * self.size if lagTolerance > 0 else self.size / 2
#         self.vartype = vartype
#         self.column = column
#         self.direction = direction
#         self.distanceToSamples = {}
#         self.semivariogram = {}
#         self.variogramData = {}
#         self.distanceLimit = self.size * (self.lagCount + 1) + self.lagTolerance
#         self.listas = []
#
#         if direction == 'DIRECTIONAL':
#             self.azimuth = directions[0] * PI / 180
#             self.dip = directions[1] * PI / 180
#             self.angleTol = round(directions[2] * PI / 180, 5)
#             self.horizontalTolerance = directions[3]
#             self.verticalTolerance = directions[4]
#
#     def calculateDistances(self, samples, samplesBySample, discretizedSamples):
#
#         for tail in samples:
#             neighbors = self.getDiscretizedSamplesBySample(tail, discretizedSamples)
#             samplesBySample[tail] = [head for head in neighbors if (tail, head) not in self.distanceToSamples]
#             self.getDistances(tail, samplesBySample[tail])
#             self.listas.append((len(neighbors), len(samplesBySample[tail])))
#
#     def getLag(self, hvector):
#
#         # Se calcula la distancia entre las muestras y los potenciales lags al que pertenece el par
#         lagante = math.floor(hvector / self.size) * self.size + self.lagOffset
#         lagpost = lagante + self.size
#
#         # Se determina el lag al que pertenece el par
#         if lagpost - self.lagTolerance <= hvector <= lagpost:
#             return lagpost
#         elif lagante <= hvector <= lagante + self.lagTolerance:
#             return lagante
#         else:
#             return None
#
#     def applyVariogram(self, lag, tail, head, hvector):
#
#         # Si el lag corresponde a alguno de los del variograma se guarda la información del par
#         if lag in self.lags:
#             if lag in self.variogramData:
#                 data = self.variogramData[lag]
#                 data[0] += 1
#                 data[1] += self.computeVariogram(tail, head)
#                 data[2] += hvector
#             else:
#                 self.variogramData[lag] = [1, self.computeVariogram(tail, head), hvector]
#
#     def getUnitVector(self, azimuthOffset, dipOffset):
#
#         # Se calcula un vector de norma unitaria con las rotaciones determinadas por el dip y el azimuth más un offset
#         x = round(numpy.cos(self.dip + dipOffset) * numpy.sin(self.azimuth + azimuthOffset), 5)
#         y = round(numpy.cos(self.dip + dipOffset) * numpy.cos(self.azimuth + azimuthOffset), 5)
#         z = round(numpy.sin(self.dip + dipOffset), 5)
#         return numpy.array([x, y, z])
#
#     def createVariogram(self, samples, discretizedSamples):
#
#         # CASO OMNIDIRECCIONAL
#         if self.direction == 'OMNIDIRECTIONAL':
#
#             samplesBySample = {}
#             self.calculateDistances(samples, samplesBySample, discretizedSamples)
#
#             for tail in samples:
#
#                 heads = [head for head in samplesBySample[tail] if self.distanceToSamples[(head, tail)] < self.distanceLimit]
#
#                 for head in heads:
#                     if head is not tail:
#                         # Se obtiene la distancia entre las muestras y se calcula el variograma
#                         hvector = self.distanceToSamples[(tail, head)]
#                         lag = self.getLag(hvector)
#                         self.applyVariogram(lag, tail, head, hvector)
#
#         # CASO DIRECCIONAL
#         elif self.direction == 'DIRECTIONAL':
#
#             samplesBySample = {}
#             self.calculateDistances(samples, samplesBySample, discretizedSamples)
#
#             # Vector unitario que representa la dirección en que se calcula el lag
#             lagVectorUnit = self.getUnitVector(0, 0)
#
#             for tail in samples:
#
#                 heads = [head for head in samplesBySample[tail] if self.distanceToSamples[(head, tail)] < self.distanceLimit]
#                 tailVector = numpy.array([tail.x, tail.y, tail.z])
#
#                 for head in heads:
#                     if head is not tail:
#
#                         # Se obtiene el vector unitario que va desde la cola a la cabeza (tail-head)
#                         headVector = numpy.array([head.x, head.y, head.z])
#                         headVectorTr = headVector - tailVector
#                         headVectorUnit = headVectorTr / numpy.linalg.norm(headVectorTr)
#
#                         # Se calcula el ángulo entre el vector del lag y el vector tail-head
#                         angleBetweenVectors = round(
#                             numpy.arccos(numpy.clip(numpy.dot(lagVectorUnit, headVectorUnit), -1.0, 1.0)), 5)
#
#                         # Control del ángulo de tolerancia (se prueba la dirección head-tail y tail-head)
#                         if angleBetweenVectors >= self.angleTol and PI - angleBetweenVectors >= self.angleTol:
#                             continue
#
#                         # Se obtiene la distancia entre las muestras
#                         distanceTailHead = self.distanceToSamples[(tail, head)]
#
#                         # Se chequea que se cumpla la restricción de la distancia horizontal y vertical
#                         if self.checkTolerance(distanceTailHead, headVectorTr, PI / 2, -self.dip,
#                                                 self.horizontalTolerance) and self.checkTolerance(distanceTailHead,
#                                                 headVectorTr, 0, PI / 2, self.verticalTolerance):
#
#                             lag = self.getLag(distanceTailHead)
#                             self.applyVariogram(lag, tail, head, distanceTailHead)
#
#         # Caso DOWN HOLE (vector de lag igual al vector del sondaje)
#         elif self.direction == 'DOWNHOLE':
#
#             samplesByDrillHole = {}
#
#             for sample in samples:
#
#                 if sample.holeid in samplesByDrillHole:
#                     samplesByDrillHole[sample.holeid].append(sample)
#                 else:
#                     samplesByDrillHole[sample.holeid] = [sample]
#
#             for holeid in samplesByDrillHole:
#
#                 samplesInDh = samplesByDrillHole[holeid]
#
#                 for i in range(len(samplesInDh)):
#                     for j in range(i + 1, len(samplesInDh)):
#
#                         tail = samplesInDh[i]
#                         head = samplesInDh[j]
#
#                         distance = numpy.sqrt((tail.x - head.x) ** 2 + (tail.y - head.y) ** 2 + (tail.z - head.z) ** 2)
#                         self.distanceToSamples[(tail, head)] = distance
#                         self.distanceToSamples[(head, tail)] = distance
#
#                         lag = self.getLag(distance)
#                         self.applyVariogram(lag, tail, head, distance)
#
#         # Se completa el cálculo de las distancas y variogramas
#         for lag in self.variogramData:
#             pairs = self.variogramData[lag][0]
#             self.variogramData[lag][1] /= (2 * pairs)
#             self.variogramData[lag][2] /= pairs
#
#     def checkTolerance(self, distance, headVector, azimuthOffset, dipOffset, tolerance):
#
#         if tolerance is not None:
#
#             # Se calcula la distancia a la cual una muestra puede verse afectada por las bandas
#             criticalDistance = tolerance / numpy.tan(self.angleTol)
#
#             if distance > criticalDistance:
#
#                 # Se hace la distinción con el caso más simple cuando dip = 0°
#                 if dipOffset == PI / 2 and self.dip == 0:
#                     projectedDistance = numpy.abs(headVector[2])
#                 else:
#                     normalVector = self.getUnitVector(azimuthOffset, dipOffset)
#                     projectedDistance = numpy.abs(numpy.dot(normalVector, headVector))
#
#                 if projectedDistance > tolerance:
#                     return False
#
#         return True
#
#     def getCoordinates(self, xCenter, yCenter, zCenter):
#
#         xs = []
#         ys = []
#         zs = []
#
#         step = self.size * (self.lagCount + 1)
#
#         for i in [-1, 0, 1]:
#             xs.append(xCenter + step * i)
#             ys.append(yCenter + step * i)
#             zs.append(zCenter + step * i)
#
#         return [(x, y, z) for x in xs for y in ys for z in zs]
#
#     def getDiscretizedSamplesBySample(self, sample, discretizedSamples):
#
#         step = self.size * (self.lagCount + 1)
#
#         result = []
#         px = math.floor(sample.x / step) * step
#         py = math.floor(sample.y / step) * step
#         pz = math.floor(sample.z / step) * step
#
#         sampleCoordinates = self.getCoordinates(px, py, pz)
#
#         for key in sampleCoordinates:
#             if key in discretizedSamples:
#                 result.extend(discretizedSamples[key])
#
#         return result
#
#     # @timer.timeit
#     def computeVariogram(self, tail, head):
#
#         if self.vartype == 'SEMIVARIOGRAM':
#             return (tail.values[tail.samples.positions[self.column]] - head.values[head.samples.positions[self.column]]) ** 2
#
#     # @timer.timeit
#     def getDistances(self, tail, samples):
#
#         self.distanceToSamples[(tail, tail)] = 0
#         selectedSamples = samples[:]
#
#         for head in samples:
#             if (tail, head) in self.distanceToSamples:
#                 i = selectedSamples.index(head)
#                 del (selectedSamples[i])
#
#         arraydim = len(selectedSamples)
#
#         if arraydim == 0:
#             return
#
#         xtail = numpy.array(arraydim * [tail.x])
#         ytail = numpy.array(arraydim * [tail.y])
#         ztail = numpy.array(arraydim * [tail.z])
#
#         heads = [(head.x, head.y, head.z) for head in selectedSamples]
#         xhead, yhead, zhead = zip(*heads)
#         xhead = numpy.array(xhead)
#         yhead = numpy.array(yhead)
#         zhead = numpy.array(zhead)
#
#         xdif = xhead - xtail
#         ydif = yhead - ytail
#         zdif = zhead - ztail
#
#         xsq = xdif * xdif
#         ysq = ydif * ydif
#         zsq = zdif * zdif
#
#         sqdist = xsq + ysq + zsq
#         dist = numpy.sqrt(sqdist)
#
#         for i in range(len(dist)):
#             self.distanceToSamples[(tail, selectedSamples[i])] = dist[i]
#             self.distanceToSamples[(selectedSamples[i], tail)] = dist[i]
