# -*- coding: utf-8 -*-
from block_model.controller.block_model import BlockModel
from xml_.controller.element_facade import ElementFacade
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree


class BlockModelFacade:

    @staticmethod
    def toXML(blockModel):
        element = Element('BLOCK_MODEL')

        if blockModel.path is not None:
            subelement = SubElement(element, 'PATH')
            subelement.text = blockModel.path

        if blockModel.x is not None:
            subelement = SubElement(element, 'COORDINATE_X')
            subelement.text = blockModel.x

        if blockModel.y is not None:
            subelement = SubElement(element, 'COORDINATE_Y')
            subelement.text = blockModel.y

        if blockModel.z is not None:
            subelement = SubElement(element, 'COORDINATE_Z')
            subelement.text = blockModel.z

        if blockModel.lengthx is not None:
            subelement = SubElement(element, 'LENGTH_X')
            subelement.text = blockModel.lengthx

        if blockModel.lengthy is not None:
            subelement = SubElement(element, 'LENGTH_Y')
            subelement.text = blockModel.lengthy

        if blockModel.lengthz is not None:
            subelement = SubElement(element, 'LENGTH_Z')
            subelement.text = blockModel.lengthz

        if blockModel.density is not None:
            subelement = SubElement(element, 'DENSITY')
            subelement.text = blockModel.density

        integerElement = SubElement(element, 'COLUMNS_INTEGER')
        floatElement = SubElement(element, 'COLUMNS_FLOAT')
        textElement = SubElement(element, 'COLUMNS_TEXT')

        for column, _type in blockModel.columns:
            if _type is int:
                parent = integerElement
            elif _type is float:
                parent = floatElement
            elif _type is str:
                parent= textElement
            subelement = SubElement(parent, 'COLUMN')
            subelement.text = column

        return element

    @staticmethod
    def saveXML(blockModel, path):
        element = BlockModelFacade.toXML(blockModel)
        ElementFacade.writeXML(path, element)

    @staticmethod
    def fromXML(path, readBlocks=False):
        tree = ElementTree.parse(path)
        root = tree.getroot()

        path = None
        x = None
        y = None
        z = None
        lengthx = None
        lengthy = None
        lengthz = None
        density = None
        columns = []

        for s1 in root.getchildren():
            if s1.tag == 'PATH': path = s1.text
            elif s1.tag == 'COORDINATE_X': x = s1.text
            elif s1.tag == 'COORDINATE_Y': y = s1.text
            elif s1.tag == 'COORDINATE_Z': z = s1.text
            elif s1.tag == 'LENGTH_X': lengthx = s1.text
            elif s1.tag == 'LENGTH_Y': lengthy = s1.text
            elif s1.tag == 'LENGTH_Z': lengthz = s1.text
            elif s1.tag == 'DENSITY': density = s1.text
            elif s1.tag == 'COLUMNS_INTEGER':
                for s2 in s1.getchildren():
                    if s2.tag == 'COLUMN':
                        columns.append((s2.text, int))
            elif s1.tag == 'COLUMNS_FLOAT':
                for s2 in s1.getchildren():
                    if s2.tag == 'COLUMN':
                        columns.append((s2.text, float))
            elif s1.tag == 'COLUMNS_TEXT':
                for s2 in s1.getchildren():
                    if s2.tag == 'COLUMN':
                        columns.append((s2.text, str))

        blockModel = BlockModel(path=path, x=x, y=y, z=z, \
                                lengthx=lengthx, lengthy=lengthy, lengthz=lengthz, \
                                density=density, columns=columns, readBlocks=readBlocks)

        return blockModel