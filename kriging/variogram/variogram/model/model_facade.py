# -*- coding: utf-8 -*-
from variogram.model.structure_facade import StructureFacade
from xml.etree.ElementTree import Element, SubElement


class ModelFacade:

    @staticmethod
    def toXML(variogram):
        element = Element('MODEL')

        subelement = SubElement(element, 'NUGGET')
        subelement.text = str(variogram.nugget)

        for structure in variogram.structures:
            subelement = StructureFacade.toXML(structure)
            element.append(subelement)

        return element