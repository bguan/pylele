#!/usr/bin/env python3

"""
    Pylele Neck 
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker

class LeleNeck(LeleBase):
    """ Pylele Neck Generator class """

    def gen(self) -> Shape:
        """ Generate Neck """
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.neckPath
        joinTol = self.api.getJoinCutTol()
        neck = None
        if midTck > 0:
            neck = self.api.genPolyExtrusionZ(path, midTck).mv(0, 0, -midTck)
        neckCone = self.api.genConeX(nkLen, ntWth/2, nkWth/2)
        if False:
            coneCut = self.api.genBox(2*nkLen, 2*nkWth, 2*nkWth).mv(nkLen, 0, nkWth)
        else:
            coneCut = self.api.genBox(nkLen, nkWth, nkWth).mv(nkLen/2, 0, nkWth/2)
        neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, joinTol -midTck)
        neck = neckCone if neck is None else neck.join(neckCone)

        self.shape = neck
        return neck

def main(args = None):
    """ Generate Neck """
    return main_maker(module_name=__name__,
                    class_name='LeleNeck',
                    args=args)

def test_neck(self,apis=None):
    """ Test Neck """
    test_loop(module=__name__,apis=apis)

def test_neck_mock(self):
    """ Test Neck """
    test_neck(self,apis=['mock'])

if __name__ == '__main__':
    main()
