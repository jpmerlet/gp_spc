# -*- coding: utf-8 -*-
# from drilling.model.discretization_facade import DiscretizationFacade
# from drilling.model.block_size_facade import BlockSizeFacade
# from drilling.model.ellipsoid_facade import EllipsoidFacade
# from drilling.model.high_yield_facade import HighYieldFacade
# from drilling.model.variogram_facade import VariogramFacade
# from drilling.model.capping_facade import CappingFacade

from kriging.model.search_ellipsoid_facade import SearchEllipsoidFacade
from kriging.model.discretization_facade import DiscretizationFacade
from kriging.model.block_size_facade import BlockSizeFacade
from kriging.model.high_yield_facade import HighYieldFacade
from kriging.model.capping_facade import CappingFacade
from variogram.model.model_facade import ModelFacade
from xml.etree.ElementTree import Element


class BlockKrigingFacade:

    @staticmethod
    def toXML(blockKriging):
        element = Element('BLOCK_KRIGING')

        subelement = SearchEllipsoidFacade.toXML(blockKriging.searchEllipsoid)
        element.append(subelement)

        subelement = DiscretizationFacade.toXML(blockKriging.discretization)
        element.append(subelement)

        subelement = ModelFacade.toXML(blockKriging.variogram)
        element.append(subelement)

        subelement = BlockSizeFacade.toXML(blockKriging.blockSize)
        element.append(subelement)

        if blockKriging.highYield is not None:
            subelement = HighYieldFacade.toXML(blockKriging.highYield)
            element.append(subelement)

        if blockKriging.capping is not None:
            subelement = CappingFacade.toXML(blockKriging.capping)
            element.append(subelement)

        return element