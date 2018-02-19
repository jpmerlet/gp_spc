# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, SubElement

class EllipsoidFacade:

    @staticmethod
    def toXML(ellipsoid):
        element = Element('ELLIPSOID')

        subelement = SubElement(element, 'MAJOR')
        subelement.text = str(ellipsoid.major)

        subelement = SubElement(element, 'MEDIUM')
        subelement.text = str(ellipsoid.medium)

        subelement = SubElement(element, 'MINOR')
        subelement.text = str(ellipsoid.minor)

        subelement = SubElement(element, 'BEARING')
        subelement.text = str(ellipsoid.bearing)

        subelement = SubElement(element, 'PLUNGE')
        subelement.text = str(ellipsoid.plunge)

        subelement  = SubElement(element, 'DIP')
        subelement.text = str(ellipsoid.dip)

        return element