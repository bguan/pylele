#!/usr/bin/env python3

"""
    Pylele Bridge
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape, Implementation
from pylele1.pylele_config import FIT_TOL
from pylele2.pylele_base import LeleBase, test_loop, main_maker
from pylele2.pylele_strings import LeleStrings

class LeleBridge(LeleBase):
    """ Pylele Bridge Generator class """

    def gen(self) -> Shape:
        """ Generate Bridge """
        fitTol = FIT_TOL
        scLen = self.cfg.scaleLen
        strRad = self.cfg.STR_RAD
        brdgWth = self.cfg.brdgWth + (2*fitTol if self.isCut else 0)
        brdgLen = self.cfg.brdgLen + (2*fitTol if self.isCut else 0)
        brdgHt = self.cfg.brdgHt
        brdgZ = self.cfg.brdgZ

        if self.cli.implementation == Implementation.BLENDER and not self.isCut:
            # increase overlap when blender backend to force join
            brdgZ -= 1.5

        brdg = self.api.genBox(brdgLen, brdgWth, brdgHt).mv(
            scLen, 0, brdgZ + brdgHt/2)
        if not self.isCut:
            cutRad = brdgLen/2 - strRad
            cutHt = brdgHt - 2
            cutScaleZ = cutHt/cutRad
            frontCut = self.api.genRodY(2*brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen - cutRad - strRad, 0, brdgZ + brdgHt)
            backCut = self.api.genRodY(2*brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen + cutRad + strRad, 0, brdgZ + brdgHt)
            brdgTop = self.api.genRodY(brdgWth, strRad).mv(scLen, 0, brdgZ + brdgHt)
            brdg = brdg.cut(frontCut).cut(backCut).join(brdgTop)

        # strings cut
        strings = LeleStrings(cli=self.cli,isCut=True)
        brdg.cut(strings.gen_full())

        self.shape = brdg
        return brdg

def main(args = None):
    """ Generate Bridge """
    return main_maker(module_name=__name__,
                    class_name='LeleBridge',
                    args=args)

def test_bridge():
    """ Test Bridge """
    tests = {
        'cut'     : ['-C']
    }
    test_loop(module=__name__,tests=tests)

if __name__ == '__main__':
    main()
