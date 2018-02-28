from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from geometry.controller.ellipsoid import Ellipsoid
from kriging.controller.search_ellipsoid import SearchEllipsoid
from kriging.controller.point_kriging import PointKriging
from variogram.controller.model import Model
from variogram.controller.structure import Structure
from common.discretize import *
from common.rotation import *


blockPath = '../GP_Data/cy17_spc_assays_pvo_entry_ug.csv'
ugVarBlock = 'ugcut'
blockColumns = [(ugVarBlock, int), ('f1', str), ('cut', str)]

var = 'cut'
ugVarComp = 'ugcut'  # columna que contiene ug de los datos de sondaje
compColumns = [(var, float), (ugVarComp, float)]
compPath = '../GP_Data/cy17_spc_assays_rl6_entry.csv'

outpath = 'modelo_estimado_ok.csv'


def run():

    blockModel, composites, ellipsoid = getObjects()
    print("bloques: ", len(blockModel))
    ugs = [10, 20, 30, 40, 50, 51, 60, 70, 71, 80]  # Notar que en el archivo de pozos existe tambien ug 61 y 0

    for ug in ugs:
        print("ug = %s" % ug)
        model = getModel(ug)
        if model is not None:
            blocks = blockModel.applyFilter('"%s" == %d' % (ugVarBlock, ug))
            comps = composites.applyFilter('"%s" == %d' % (ugVarComp, ug))
            print("len blocks: %d\nlen samples: %d" % (len(blocks), len(comps)))
            estimate(blocks, comps, ellipsoid, model)

    exportBlockModel(blockModel)


def getModel(ug):
    # modelo de variograma
    if ug == 10:
        nugget = 0.250
        s1 = Structure(Structure.EXPONENTIAL, 0.480, Ellipsoid(19, 19, 19, 0, 0, 0))
        s2 = Structure(Structure.EXPONENTIAL, 0.270, Ellipsoid(436, 436, 436, 0, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 20:
        nugget = 0.250
        s1 = Structure(Structure.EXPONENTIAL, 0.370, Ellipsoid(16, 22, 5, 20, 0, 0))
        s2 = Structure(Structure.EXPONENTIAL, 0.380, Ellipsoid(177, 97, 27, 20, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 30:
        nugget = 0.290
        s1 = Structure(Structure.SPHERIC, 0.320, Ellipsoid(47, 103, 20, 30, 0, 0))
        s2 = Structure(Structure.SPHERIC, 0.390, Ellipsoid(601, 500, 32, 30, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 40:
        nugget = 0.220
        s1 = Structure(Structure.SPHERIC, 0.420, Ellipsoid(55, 20, 11, 40, 0, 0))
        s2 = Structure(Structure.SPHERIC, 0.360, Ellipsoid(447, 183, 26, 40, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 50:
        nugget = 0.180
        s1 = Structure(Structure.SPHERIC, 0.390, Ellipsoid(16, 29, 11, 40, 0, 0))
        s2 = Structure(Structure.SPHERIC, 0.430, Ellipsoid(144, 93, 145, 40, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 51:
        nugget = 0.140
        s1 = Structure(Structure.SPHERIC, 0.390, Ellipsoid(14, 37, 28, 35, 0, 0))
        s2 = Structure(Structure.SPHERIC, 0.470, Ellipsoid(343, 183, 125, 35, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 60:
        nugget = 0.150
        s1 = Structure(Structure.SPHERIC, 0.550, Ellipsoid(14.8, 10.3, 11.9, 10, 0, 0))
        s2 = Structure(Structure.SPHERIC, 0.300, Ellipsoid(954.5, 98.9, 16337.9, 10, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 70:
        nugget = 0.150
        s1 = Structure(Structure.EXPONENTIAL, 0.444, Ellipsoid(18.6, 15.1, 18.1, 10, 0, 0))
        s2 = Structure(Structure.EXPONENTIAL, 0.406, Ellipsoid(18.8, 14.9, 208.9, 10, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    elif ug == 71:
        nugget = 0.200
        s1 = Structure(Structure.EXPONENTIAL, 0.441, Ellipsoid(11.1, 7.9, 9.8, 20, 0, 0))
        s2 = Structure(Structure.EXPONENTIAL, 0.359, Ellipsoid(143.7, 161.0, 3777.8, 20, 0, 0))
        structures = [s1, s2]
        return Model(nugget, structures)
    return None


def estimate(blocks, composites, ellipsoid, model):

    # se rotan los compósitos
    rotatedPoints = rotateComposites(composites, ellipsoid.rotationMatrix)

    # se crea un diccionario para acceder a las muestras según su coordenada rotada
    compositesByRotatedPoint = dict([(tuple(rotatedPoints[i]), composites[i])
                                     for i in range(len(rotatedPoints))])

    # se discretiza el espacio
    discretizedPoints = discretizePoints(rotatedPoints,
                                         ellipsoid.major,
                                         ellipsoid.medium,
                                         ellipsoid.minor)

    kriging = PointKriging(ellipsoid, model)

    cap = 2

    print('Estimando modelo de bloques:')
    for block in blocks:

        # se rota el punto que se quiere estimar
        rx, ry, rz = rotateBlock(block, ellipsoid.rotationMatrix)

        # se obtienen los compósitos cercanos al centro del bloque
        points = ellipsoid.searchPointsInDiscretizedPoints((rx, ry, rz),  discretizedPoints)
        if len(points) > 0:
            # se ordenan los puntos por distancia al bloque
            points = sorted(points, key=lambda point: point[0])
            inEllipsoid = []
            for distance, rotatedPoint, movedPoint, octant in points:
                composite = compositesByRotatedPoint[rotatedPoint]
                inEllipsoid.append((distance, composite, octant))

            # se seleccionan las muestras que cumplen con los criterios pedidos
            selectedSamples = ellipsoid.selectSamples(inEllipsoid)
            if len(selectedSamples) > 0:
                blockpoint = (block.x, block.y, block.z)
                weights, variance = kriging.ordinary(selectedSamples, blockpoint)

                value = 0
                for i in range(len(selectedSamples)):
                    _, comp, _ = selectedSamples[i]

                    # capping
                    gradeComp = comp[var] if comp[var] <= cap else cap

                    value += gradeComp * weights[i]

                block.grade = value


def exportBlockModel(blockModel):
    # Exportación modelo de bloques
    outfile = open(outpath, 'w')
    outfile.write('xcentre,ycentre,zcentre,cut,f1,cut_poz\n')

    for block in blockModel:
        if hasattr(block, 'grade'):
            line = block.x, block.y, block.z, block.grade, block['f1'], block['cut']
        else:
            line = block.x, block.y, block.z, -99, block['f1'], block['cut']
        outfile.write("%f,%f,%f,%f,%s,%s\n" % line)
    outfile.close()


def getObjects():
    # se carga el modelo de bloques, compósitos y script de categoría
    blockModel = BlockModel(path=blockPath, x='midx', y='midy', z='midz', columns=blockColumns, readBlocks=True)

    # composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
    #                        from_='from', to_='to', columns=compColumns, readComposites=True)
    composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
                            columns=compColumns, readComposites=True)

    major, medium, minor = 100, 100, 100
    bearing, plunge, dip = 0, 0, 0
    minSamples, maxSamples = 10, 25
    minSamplesByOctant, maxSamplesByOctant = 1, 100
    minOctantWithSamples, maxSamplesByDrillhole = 1, 100
    ellipsoid = SearchEllipsoid(major=major, medium=medium, minor=minor, bearing=bearing, plunge=plunge, dip=dip,
                                minSamples=minSamples, maxSamples=maxSamples,
                                minSamplesByOctant=minSamplesByOctant, maxSamplesByOctant=maxSamplesByOctant,
                                minOctantWithSamples=minOctantWithSamples, maxSamplesByDrillhole=maxSamplesByDrillhole)

    return blockModel, composites, ellipsoid


if __name__ == '__main__':
    run()
