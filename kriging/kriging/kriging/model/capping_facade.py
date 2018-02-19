# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, SubElement


class CappingFacade:

    @staticmethod
    def toXML(capping):
        element = Element('CAPPING')

        if capping.minimum is not None:
            subelement = SubElement(element, 'MINIMUM')
            subelement.text = str(capping.minimum)

        if capping.maximum is not None:
            subelement = SubElement(element, 'MAXIMUM')
            subelement.text = str(capping.maximum)

        return element