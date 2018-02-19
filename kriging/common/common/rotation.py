# -*- coding: utf-8 -*-ç
import numpy

def rotateBlock(block, rotationMatrix):
    return numpy.dot(rotationMatrix, (block.x, block.y, block.z))

def rotateBlocks(blocks, rotationMatrix):
    return [rotateBlock(block, rotationMatrix) for block in blocks]

def rotateComposite(composite, rotationMatrix):
    return numpy.dot(rotationMatrix, (composite.middlex, composite.middley, composite.middlez))

def rotateComposites(composites, rotationMatrix):
    return [rotateComposite(composite, rotationMatrix) for composite in composites]

def rotatePoint(point, rotationMatrix):
    return numpy.dot(rotationMatrix, (point[0], point[1], point[2]))

# def rotateSample(sample, rotationMatrix):
#     return numpy.dot(rotationMatrix, (sample.x, sample.y, sample.z))
#
# def rotateSamples(samples, rotationMatrix):
#     return [rotateSample(sample, rotationMatrix) for sample in samples]
#
# def rotatePoint(punto, rotationMatrix):
#
#     x,y,z = numpy.dot(rotationMatrix, punto)
#     return (x,y,z)
#
# def rotateBlocks(blocks, rotationMatrix):
#     return [rotatePoint(block, rotationMatrix) for block in blocks]
#
# # def rotateBlock(block):
# #     return
#
# def rotateSamples(samples, rotationMatrix):
#     result = []
#     # print(len(samples[0]))
#     for holeid, x, y, z, value in samples:
#         x, y, z = rotatePoint((x, y, z), rotationMatrix)
#         result.append(numpy.array([holeid, x, y, z, value]))
#     return result