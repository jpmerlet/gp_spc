# -*- coding: utf-8 -*-
import math
#
# import numpy
#
# # from drillhole.controller import Distance
# # from drilling_target.controller.distance import Distance
# from kriging.controller.distance import Distance


def discretizePoints(points, stepx, stepy, stepz):
    result = {}
    for x, y, z in points:
        x_ = math.floor(x / stepx) * stepx
        y_ = math.floor(y / stepy) * stepy
        z_ = math.floor(z / stepz) * stepz
        key = (x_, y_, z_)

        if key in result:
            result[key].append((x, y, z))
        else:
            result[key] = [(x, y, z)]

    return result

#
#
# def distancePointInDiscretizedPoints(point, discretizedPoints, ellipsoid, distanceType=Distance.CARTESIAN):
#
#         stepx = ellipsoid.major
#         stepy = ellipsoid.medium
#         stepz = ellipsoid.minor
#         anisotropyMatrix = ellipsoid.anisotropyMatrix
#         maximumDistance = ellipsoid.major
#
#         # px, py, pz = point
#         # px = math.floor(px / stepx) * stepx
#         # py = math.floor(py / stepy) * stepy
#         # pz = math.floor(pz / stepz) * stepz
#
#         # rotatePoints = []
#         # for x_, y_, z_ in [(x, y, z) for x in [px - stepx, px, px + stepx]
#         #                              for y in [py - stepy, py, py + stepy]
#         #                              for z in [pz - stepz, pz, pz + stepz]]:
#         #     key = (x_, y_, z_)
#         #     if key in discretizedPoints:
#         #         rotatePoints.extend(discretizedPoints[key])
#
#         # def movePoint(point, rotatedPoint):
#         #     px, py, pz = point
#         #     dx, dy, dz = rotatedPoint
#         #     return tuple(numpy.array((dx-px, dy-py, dz-pz)))
#
#         # movePoints = [movePoint(point, discretizedPoint) for discretizedPoint in rotatePoints]
#         # points = []
#         # for rotatedPoint in rotatePoints:
#         #     movedPoint = movePoint(point, rotatedPoint)
#         #     x,y,z = movedPoint
#         #     if abs(x) <= ellipsoid.major and abs(y) <= ellipsoid.medium and abs(z) <= ellipsoid.minor:
#         #         points.append((rotatedPoint, movedPoint))
#
#         result = []
#         for rotatedPoint, movedPoint in points:
#         # for i in range(len(movePoints)):
#             anisotropic, cartesian = Distance.distanceToOrigin(movedPoint, anisotropyMatrix)
#             if anisotropic < maximumDistance:
#                 # rotatePoint = rotatePoints[i]
#                 # movePoint = movePoints[i]
#                 octant = ellipsoid.getOctant(movedPoint)
#                 if distanceType == Distance.CARTESIAN:
#                     result.append((cartesian, rotatedPoint, movedPoint, octant))
#                 else:
#                     result.append((anisotropic, rotatedPoint, movedPoint, octant))
#
#         return result