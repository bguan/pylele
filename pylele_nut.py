#!/usr/bin/env python3

"""
    Pylele Nut
"""

import os
import math

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import accumDiv, FIT_TOL, SEMI_RATIO, Implementation
from pylele_utils import radians

class LeleNut(LeleBase):
    """ Pylele Nut Generator class """

    def gen(self) -> Shape:
        """ Generate Nut """

        fitTol = FIT_TOL
        fbTck = self.cfg.FRETBD_TCK
        ntHt = self.cfg.NUT_HT
        ntWth = self.cfg.nutWth + fbTck/4 + .5  # to be wider than fretbd
        fWth = self.cfg.nutWth - 1  # to be narrower than fretbd
        f0X = -fitTol if self.isCut else 0

        f0Top = self.api.genRndRodY(ntWth, ntHt, 1/4)
        f0TopCut = self.api.genBox(2*ntHt, 2*ntWth, fbTck).mv(0, 0, -fbTck/2)
        f0Top = f0Top.cut(f0TopCut).mv(f0X, 0, fbTck)
        f0Bot = self.api.genRndRodY(ntWth, ntHt, 1/4)
        f0BotCut = self.api.genBox(2*ntHt, 2*ntWth, fbTck).mv(0, 0, fbTck/2)
        f0Bot = f0Bot.cut(f0BotCut).scale(1, 1, fbTck/ntHt).mv(f0X, 0, fbTck)
        nut = f0Top.join(f0Bot)

        self.shape = nut

        return nut

def nut_main(args = None):
    """ Generate Nut """
    solid = LeleNut(args=args)
    solid.export_args() # from cli
    
    solid.export_configuration()
    
    solid.exportSTL()
    return solid

def test_nut():
    """ Test Nut """

    component = 'nut'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        nut_main(args=args)

if __name__ == '__main__':
    nut_main()