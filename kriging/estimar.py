from block_model.controller.block_model import BlockModel
from drillhole.controller.composites import Composites
from geometry.controller.ellipsoid import Ellipsoid
from kriging.controller.search_ellipsoid import SearchEllipsoid
from kriging.controller.point_kriging import PointKriging
from variogram.controller.model import Model
from variogram.controller.structure import Structure
from common.discretize import *
from common.rotation import *

# se carga el modelo de bloques, compósitos y script de categoría
# blockPath = '../../GP_Data/cy17_spc_assays_pvo_entry.csv'
blockPath = '../../GP_Data/test_kriging.csv'
blockModel = BlockModel(path=blockPath, x='midx', y='midy', z='midz', readBlocks=True)

compPath = '../../GP_Data/cy17_spc_assays_rl6_entry.csv'
# compPath = '../../GP_Data/cy17_spc_au_rl6_entry.csv'
var = 'cut'
compColumns = [(var, float)]
# composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
#                        from_='from', to_='to', columns=compColumns, readComposites=True)
composites = Composites(path=compPath, holeid='dhid', middlex='midx', middley='midy', middlez='midz',
                        columns=compColumns, readComposites=True)

major, medium, minor = 500, 500, 500
bearing, plunge, dip = 0, 0, 0
minSamples, maxSamples = 1, 100
minSamplesByOctant, maxSamplesByOctant = 1, 100
minOctantWithSamples, maxSamplesByDrillhole = 1, 100
ellipsoid = SearchEllipsoid(major=major, medium=medium, minor=minor, bearing=bearing, plunge=plunge, dip=dip,
                            minSamples=minSamples, maxSamples=maxSamples,
                            minSamplesByOctant=minSamplesByOctant, maxSamplesByOctant=maxSamplesByOctant,
                            minOctantWithSamples=minOctantWithSamples, maxSamplesByDrillhole=maxSamplesByDrillhole)

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

# modelo de variograma
#
nugget = 0.14
s1 = Structure(Structure.SPHERIC, 0.39, Ellipsoid(100, 50, 30, 10, 10, 10))
s2 = Structure(Structure.SPHERIC, 0.47, Ellipsoid(200, 100, 50, -10, 10, -10))
structures = [s1, s2]
model = Model(nugget, structures)
kriging = PointKriging(ellipsoid, model)

cap = 2

print('Estimando modelo de bloques:')
for block in blockModel:

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

                value = gradeComp * weights[i]

            block.grade = value

# Exportación modelo de bloques
outfile = 'modelo_estimado_sondaje.csv'
outfile = open(outfile, 'w')
outfile.write('x,y,z,grade\n')

for block in blockModel:
    if hasattr(block, 'grade'):
        line = block.x, block.y, block.z, block.grade
    else:
        line = block.x, block.y, block.z, -99
    outfile.write("%f,%f,%f,%f\n" % line)
outfile.close()
