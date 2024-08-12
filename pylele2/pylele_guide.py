#!/usr/bin/env python3

"""
    Pylele Guide
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase
from pylele1.pylele_config import FIT_TOL

class LeleGuide(LeleBase):
    """ Pylele Guide Generator class """

    def gen(self) -> Shape:
        """ Generate Guide """
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        nStrs = self.cfg.numStrs
        sR = self.cfg.STR_RAD
        gdR = self.cfg.GUIDE_RAD + cutAdj
        gdX = self.cfg.guideX
        gdZ = self.cfg.guideZ
        gdHt = self.cfg.guideHt
        gdWth = self.cfg.guideWth
        gdGap = self.cfg.guidePostGap

        guide = None if self.isCut else \
            self.api.genRndRodY(
                (gdWth - .5*gdGap + sR + 2*gdR) if nStrs > 1 else 6*gdR, 
                1.1*gdR, 1,
            ).mv(gdX, 0, gdZ + gdHt)
        
        for y in self.cfg.guideYs:
            post = self.api.genRodZ(gdHt, gdR)
            post = post.mv(gdX, y, gdZ + gdHt/2)
            guide = post if guide == None else guide.join(post)

        self.shape = guide
        return guide

def guide_main(args = None):
    """ Generate Guide """
    solid = LeleGuide(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_guide():
    """ Test Guide """

    component = 'guide'
    tests = {
        'cut'     : ['-C'],
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        guide_main(args=args)

if __name__ == '__main__':
    guide_main()
