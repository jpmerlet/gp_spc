# -*- coding: utf-8 -*-
from geometry.model.ellipsoid_facade import EllipsoidFacade
from xml.etree.ElementTree import Element, SubElement


class StructureFacade:

    @staticmethod
    def toXML(structure):
        element = Element('STRUCTURE')

        subelement = SubElement(element, 'NAME')
        subelement.text = structure.name

        subelement = SubElement(element, 'SILL')
        subelement.text = str(structure.sill)

        subelement = EllipsoidFacade.toXML(structure.ellipsoid)
        element.append(subelement)

        return element