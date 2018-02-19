# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, SubElement


class BlockSizeFacade:

    @staticmethod
    def toXML(blockSize):
        element = Element('BLOCK_SIZE')

        subelement = SubElement(element, 'LENGTH_X')
        subelement.text = str(blockSize.lenx)

        subelement = SubElement(element, 'LENGTH_Y')
        subelement.text = str(blockSize.leny)

        subelement = SubElement(element, 'LENGTH_Z')
        subelement.text = str(blockSize.lenz)

        return element