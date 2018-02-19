import math
import numpy
# import timer
from drillhole.controller import composites
from block_model.model.block_model_facade import BlockModelFacade
# from variogram import Variogram
# from variogram import Variogram
import pickle
from sys import float_info


def run(samples=None, category=None):

    # parámetros del variograma
    azimuth = 0             # valor en [0 360)
    dip = 0                 # valor en [0 -90]
    angletolerance = 22.5   # valor en (0 90]
    widthtolerance = 60     # valor >0 o None
    heighttolerance = 60    # valor >0 o None

    size = 20               # valor >0
    count = 10               # valor >0
    offset = 0              # valor >=0
    tolerance = 0.5         # valor en [0 0.5]

    if category is not None:
        column = 'indicator_minty_' + str(category)
    else:
        column = 'cutcap'

    vartype = 'SEMIVARIOGRAM'

    direction = 'OMNIDIRECTIONAL'
    directions = azimuth, dip, angletolerance, widthtolerance, heighttolerance
    # variograma = Variogram(size, count, offset, tolerance, vartype, direction, column, directions)
    variograma = Variogram(size, count, offset, tolerance, vartype, direction, column, directions)

    # parámetros de las muestras
    if samples is None:
        columns = [('from', float), ('to', float), ('ugcut', int), ('minty', int)]
        samples = SamplesFacade.fromCSV('../drilling_qt5/test/samples.csv', 'dhid', 'midx', 'midy', 'midz', 'cutcap', columns, separator=';')

    print("\nnumber of points read     : %s" % len(samples.samples))
    samples.samples = [sample for sample in samples.samples if sample.values[samples.positions['ugcut']] == 5]
    print("number of points selected : %s\n" % len(samples.samples))
    limits = obtainLimits(samples.samples)
    print("x range: %.2f %.2f\ny range: %.2f %.2f\nz range: %.2f %.2f\n" % limits)
    statistics = obtainStatistics(samples.samples)
    print("number   : %.0f\naverage  : %.5f\nvariance : %.5f\nminimum  : %.5f\nmaximum  : %.5f\n" % statistics)

    discretizedSamples = discretizeSamplesByLag(samples.samples, variograma.size)
    variograma.createVariogram(samples.samples, discretizedSamples)

    variogramInfo = []
    variogramData = variograma.variogramData

    for key in variogramData:
        variogramInfo.append((key, variogramData[key][1], variogramData[key][0], variogramData[key][2]))

    variogramInfo.sort(key=lambda data: data[0])

    print('\nlag\tvalue\tpairs\tdistance')
    for data in variogramInfo:
        print('%d\t%.5f\t%d\t%.4f' % data)

    modelar(variograma)

# def discretizeSamplesByLag(samples, size, lagcount):
#     """
#     Discretiza las muestras según el tamaño del lag elegido
#     :param samples: [Sample] -> lista con las muestras con las que se evaluará el variograma experimental
#     :param size: float -> tamaño del lag
#     :param lagcount: int -> número de lags
#     :return: {(x,y,z):[Sample]} -> diccionario con las listas de muestras
#     """
#     discretizedSamples = {}
#     step = size * (lagcount + 1)
#     # step = size
#     for sample in samples:
#         x = numpy.floor(sample.x / step) * step
#         y = numpy.floor(sample.y / step) * step
#         z = numpy.floor(sample.z / step) * step
#         key = x, y, z
#
#         if key in discretizedSamples:
#             discretizedSamples[key].append(sample)
#         else:
#             discretizedSamples[key] = [sample]
#
#     return discretizedSamples


def obtainLimits(samples):
    """
    Obtiene los límites de las coordenadas x, y, z de las muestras
    :param samples: [Sample] -> lista de las muestras con las que se calculará el variograma
    :return: (xmin, xmax, ymin, ymax, zmin, zmax)
    """
    xmin, ymin, zmin = 3 * [float_info.max]
    xmax, ymax, zmax = 3 * [float_info.min]

    for sample in samples:
        xmin = sample.x if sample.x < xmin else xmin
        ymin = sample.y if sample.y < ymin else ymin
        zmin = sample.z if sample.z < zmin else zmin

        xmax = sample.x if sample.x > xmax else xmax
        ymax = sample.y if sample.y > ymax else ymax
        zmax = sample.z if sample.z > zmax else zmax

    return xmin, xmax, ymin, ymax, zmin, zmax


def obtainStatistics(samples):
    """
    Obtiene estadísticas de las leyes de las muestras
    :param samples: [Sample] -> lista de samples con las que se calculará el variograma
    :return: (número de muestras, promedio, varianza, mínimo, máximo)
    """
    cuts = [sample.value for sample in samples]
    return len(cuts), numpy.mean(cuts), numpy.var(cuts), min(cuts), max(cuts)


def discretizeSamplesByLag(samples, size):
    """
    Discretiza las muestras según el tamaño del lag elegido
    :param samples: [Sample] -> lista con las muestras con las que se evaluará el variograma experimental
    :param size: float -> tamaño del lag
    :param lagcount: int -> número de lags
    :return: {(x,y,z):[Sample]} -> diccionario con las listas de muestras
    """
    discretizedSamples = {}
    # step = size * lagcount + 1
    step = size
    for sample in samples:
        x = numpy.floor(sample.x / step) * step
        y = numpy.floor(sample.y / step) * step
        z = numpy.floor(sample.z / step) * step
        key = x, y, z

        if key in discretizedSamples:
            discretizedSamples[key].append(sample)
        else:
            discretizedSamples[key] = [sample]

    return discretizedSamples


# @timer.timeit
def createCategories(samples, variable):

    if variable not in samples.positions:
        print('la variable "', variable, '" no se encuentra en la base de datos de compósitos')
        return

    index = samples.positions[variable]
    categories = []

    for sample in samples.samples:

        category = sample.values[index]
        if category not in categories:
            categories.append(category)

    for category in categories:

        indicatorName = 'indicator_' + variable + '_' + str(category)
        samples.positions[indicatorName] = len(samples.positions)

        for sample in samples.samples:

            if sample.values[index] == category:
                sample.values.append(1)
            else:
                sample.values.append(0)

    return categories


def modelar(variograma):

    variogramInfo = []
    movingAverage = []
    movDerivative = []

    # Se ordena la información del variograma experimental
    variogramData = variograma.variogramData

    for key in variogramData:
        variogramInfo.append((key, variogramData[key][1], variogramData[key][0], variogramData[key][2]))

    variogramInfo.sort(key=lambda data: data[0])

    if len(variogramInfo) < 3:
        print('Hay muy pocos lags para estimar.')
        return

    lags, values, pairs, distances = zip(*variogramInfo)

    # Se calcula la media móvil del variograma experimental y su derivada
    movingAverage.append(values[0])

    for i in range(len(variogramInfo) - 2):
        movingAverage.append((values[i] + values[i + 1] + values[i + 2]) / 3)
        movDerivative.append((movingAverage[-1] - movingAverage[-2]) / (distances[i + 1] - distances[i]))

    movingAverage.append((values[-1] + values[-2]) / 2)
    movDerivative.append((movingAverage[-1] - movingAverage[-2]) / (distances[-1] - distances[-2]))

    # Para imprimir (borar después)
    print('\nmaverage derivative')
    print('%.4f' % movingAverage[0])
    for i in range(1, len(movingAverage)):
        print('%.4f %.4f' % (movingAverage[i], movDerivative[i - 1]))

    # Se obtiene los parámetros del variograma y se cortan los datos hasta ese punto
    index = 0
    dif = max(movingAverage) - min(movingAverage)
    for i in range(len(movDerivative)):
        if movDerivative[i] / dif < 0.0015:
            index = i
            break

    if index == 0:
        return

    movingAverage = movingAverage[:index + 1]
    movDerivative = movDerivative[:index]

    rangev = distances[len(movingAverage) - 1]
    nugget = values[0] - abs(distances[0] * movDerivative[0])
    sill = values[len(movingAverage) - 1] - nugget

    # spheric = []
    # gaussian = []
    # exponential = []

    # Se generan los modelos de variograma esférico, gaussiano y exponencial
    spheric = [nugget + sill * (1.5 * (distance / rangev) - 0.5 * (distance / rangev) ** 3) if distance < rangev else nugget + sill for distance in distances]
    gaussian = [nugget + sill * (1 - math.exp(-(distance / rangev) ** 2)) for distance in distances]
    exponential = [nugget + sill * (1 - math.exp(-distance / rangev)) for distance in distances]

    # for distance in distances:
    #     if distance < rangev:
    #         spheric.append(nugget + sill * (1.5 * (distance / rangev) - 0.5 * (distance / rangev) ** 3))
    #     else:
    #         spheric.append(nugget + sill)
    #     gaussian.append(nugget + sill * (1 - math.exp(-(distance / rangev) ** 2)))
    #     exponential.append(nugget + sill * (1 - math.exp(-distance / rangev)))

    # Se selecciona el modelo que mejor se ajusta a los datos

    errorspheric = [(values[i] - spheric[i]) ** 2 for i in range(len(values))]
    errorgaussian = [(values[i] - gaussian[i]) ** 2 for i in range(len(values))]
    errorexponen = [(values[i] - exponential[i]) ** 2 for i in range(len(values))]

    if sum(errorspheric) <= sum(errorgaussian) and sum(errorspheric) <= sum(errorexponen):
        model = 'SPHERIC'
    elif sum(errorgaussian) <= sum(errorexponen) and sum(errorgaussian) <= sum(errorspheric):
        model = 'GAUSSIAN'
    else:
        model = 'EXPONENTIAL'

    return model, nugget, rangev, sill










if __name__ == '__main__':

    columns = [('from', float), ('to', float), ('ugcut', int), ('minty', int)]
    samples = SamplesFacade.fromCSV('../drilling_qt5/test/samples.csv', 'dhid', 'midx', 'midy', 'midz', 'cutcap', columns, separator=';')
    categories = createCategories(samples, 'minty')

    # for category in categories:
    #     run(samples, category)

    run()


