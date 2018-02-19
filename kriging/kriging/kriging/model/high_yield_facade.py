# -*- coding: utf-8 -*-
from kriging.model.search_ellipsoid_facade import SearchEllipsoidFacade
from xml.etree.ElementTree import Element, SubElement


class HighYieldFacade:
    @staticmethod
    def toXML(highYield):
        element = Element('HIGH_YIELD')

        subelement = SubElement(element, 'VALUE')
        subelement.text = str(highYield.value)

        subelement = SearchEllipsoidFacade.toXML(highYield.ellipsoid)
        element.append(subelement)

        return element
