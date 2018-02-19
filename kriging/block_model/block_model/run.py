# -*- coding: utf-8 -*-
from block_model.controller.block_model import BlockModel

if __name__ == '__main__':
    blockModel = BlockModel('model.csv', 'xcentre', 'ycentre', 'zcentre',\
                            'xlength', 'ylength', 'zlength', 'densidad',
                            columns=[('cut', float)], readBlocks=True)

    # for block in blockModel.blocks:
    #     print(block['cut'])
    
    for block in blockModel:
        print(block, block['cut'], block.x)