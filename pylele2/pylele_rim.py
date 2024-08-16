#!/usr/bin/env python3

"""
    Pylele Rim
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL

class LeleRim(LeleBase):
    """ Pylele Rim Generator class """

    def gen(self) -> Shape:
        """ Generate Rim """
        joinTol = self.cfg.joinCutTol
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        scLen = self.cfg.scaleLen
        rad = self.cfg.chmWth/2 + self.cfg.rimWth
        tck = self.cfg.RIM_TCK + 2*cutAdj
        frontWthRatio = (self.cfg.chmFront + self.cfg.rimWth)/rad
        backWthRatio = (self.cfg.chmBack + self.cfg.rimWth)/rad
        rimFront = self.api.genHalfDisc(rad, True, tck).scale(frontWthRatio, 1, 1)
        rimBack = self.api.genHalfDisc(rad, False, tck).scale(backWthRatio, 1, 1)
        rimFront.mv(scLen, 0, joinTol-tck/2).join(rimBack.mv(scLen-joinTol, 0, joinTol-tck/2))

        self.shape = rimFront
        return rimFront

def main(args=None):
    """ Generate Rim """
    return main_maker(module_name=__name__,
                    class_name='LeleRim',
                    args=args)

def test_rim():
    """ Test Rim """

    tests = {
        'cut'     : ['-C']
    }
    test_loop(module=__name__,tests=tests)

if __name__ == '__main__':
    main()
