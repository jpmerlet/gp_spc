# -*- coding: utf-8 -*-
from xml_.controller.element_facade import ElementFacade
from drillhole.controller.composites import Composites
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree


class CompositesFacade:

    @staticmethod
    def toXML(composites):
        element = Element('COMPOSITES')

        if composites.path is not None:
            subelement = SubElement(element, 'PATH')
            subelement.text = composites.path

        if composites.holeid is not None:
            subelement = SubElement(element, 'HOLEID')
            subelement.text = composites.holeid

        if composites.bottomx is not None:
            subelement = SubElement(element, 'BOTTOM_X')
            subelement.text = composites.bottomx

        if composites.bottomy is not None:
            subelement = SubElement(element, 'BOTTOM_Y')
            subelement.text = composites.bottomy

        if composites.bottomz is not None:
            subelement = SubElement(element, 'BOTTOM_Z')
            subelement.text = composites.bottomz

        if composites.middlex is not None:
            subelement = SubElement(element, 'MIDDLE_X')
            subelement.text = composites.middlex

        if composites.middley is not None:
            subelement = SubElement(element, 'MIDDLE_Y')
            subelement.text = composites.middley

        if composites.middlez is not None:
            subelement = SubElement(element, 'MIDDLE_Z')
            subelement.text = composites.middlez

        if composites.topx is not None:
            subelement = SubElement(element, 'TOP_X')
            subelement.text = composites.topx

        if composites.topy is not None:
            subelement = SubElement(element, 'TOP_Y')
            subelement.text = composites.topy

        if composites.topz is not None:
            subelement = SubElement(element, 'TOP_Z')
            subelement.text = composites.topz

        integerElement = SubElement(element, 'COLUMNS_INTEGER')
        floatElement = SubElement(element, 'COLUMNS_FLOAT')
        textElement = SubElement(element, 'COLUMNS_TEXT')

        for column, _type in composites.columns:
            if _type is int:
                parent = integerElement
            if _type is float:
                parent = floatElement
            if _type is str:
                parent = textElement
            subelement = SubElement(parent, 'COLUMN')
            subelement.text = column

        return element

    @staticmethod
    def saveXML(composites, path):
        element = CompositesFacade.toXML(composites)
        ElementFacade.writeXML(path, element)

    @staticmethod
    def fromXML(path, readComposites=False):
        tree = ElementTree.parse(path)
        root = tree.getroot()

        path = None
        holeid = None
        bottomx = None
        bottomy = None
        bottomz = None
        middlex = None
        middley = None
        middlez = None
        topx = None
        topy = None
        topz = None
        from_ = None
        to_ = None
        columns = []

        for s1 in root.getchildren():
            if s1.tag == 'PATH': path = s1.text
            elif s1.tag == 'HOLEID': holeid = s1.text
            elif s1.tag == 'BOTTOM_X': bottomx = s1.text
            elif s1.tag == 'BOTTOM_Y': bottomy = s1.text
            elif s1.tag == 'BOTTOM_Z': bottomz = s1.text
            elif s1.tag == 'MIDDLE_X': middlex = s1.text
            elif s1.tag == 'MIDDLE_Y': middley = s1.text
            elif s1.tag == 'MIDDLE_Z': middlez = s1.text
            elif s1.tag == 'TOP_X': topx = s1.text
            elif s1.tag == 'TOP_Y': topy = s1.text
            elif s1.tag == 'TOP_Z': topz = s1.text
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
        print('obtienendo compósitos de {}'.format(path))
        composites = Composites(path=path, holeid=holeid, bottomx=bottomx, bottomy=bottomy, bottomz=bottomz,\
                                middlex=middlex, middley=middley, middlez=middlez,topx=topx, topy=topy, topz=topz,\
                                from_=from_, to_=to_, columns=columns, readComposites=readComposites)

        return composites
#
# if __name__ == '__main__':
#     print(CompositesFacade)