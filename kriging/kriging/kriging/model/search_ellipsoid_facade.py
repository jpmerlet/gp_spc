# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, SubElement


class SearchEllipsoidFacade:

    @staticmethod
    def toXML(ellipsoid):
        element = Element('SEARCH_ELLIPSOID')

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

        if ellipsoid.minSamples is not None:
            subelement = SubElement(element, 'MINIMUM_SAMPLES')
            subelement.text = str(ellipsoid.minSamples)

        if ellipsoid.maxSamples is not None:
            subelement = SubElement(element, 'MAXIMUM_SAMPLES')
            subelement.text = str(ellipsoid.maxSamples)

        if ellipsoid.minSamplesByOctant is not None:
            subelement = SubElement(element, 'MINIMUM_SAMPLES_BY_OCTANT')
            subelement.text = str(ellipsoid.minSamplesByOctant)

        if ellipsoid.maxSamplesByOctant is not None:
            subelement = SubElement(element, 'MAXIMUM_SAMPLES_BY_OCTANT')
            subelement.text = str(ellipsoid.maxSamplesByOctant)

        if ellipsoid.minOctantWithSamples is not None:
            subelement = SubElement(element, 'MINIMUM_OCTANT_WITH_SAMPLES')
            subelement.text = str(ellipsoid.minOctantWithSamples)

        if ellipsoid.maxSamplesByDrillhole is not None:
            subelement = SubElement(element, 'MAXIMUM_SAMPLES_BY_DRILL_HOLE')
            subelement.text = str(ellipsoid.maxSamplesByDrillhole)

        return element