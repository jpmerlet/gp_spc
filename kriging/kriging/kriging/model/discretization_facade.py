# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, SubElement


class DiscretizationFacade:

    @staticmethod
    def toXML(discretization):
        element = Element('DISCRETIZATION')

        subelement = SubElement(element, 'SIZE_X')
        subelement.text = str(discretization.sizex)

        subelement = SubElement(element, 'SIZE_Y')
        subelement.text = str(discretization.sizey)

        subelement = SubElement(element, 'SIZE_Z')
        subelement.text = str(discretization.sizez)

        return element