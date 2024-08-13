#!/usr/bin/env python3

"""
    Pylele Head
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker

class LeleHead(LeleBase):
    """ Pylele Head Generator class """

    def gen(self) -> Shape:
        """ Generate Head """

        hdWth = self.cfg.headWth
        hdLen = self.cfg.HEAD_LEN
        ntHt = self.cfg.NUT_HT
        fbTck = self.cfg.FRETBD_TCK
        spHt = self.cfg.SPINE_HT
        fspTck = self.cfg.FRETBD_SPINE_TCK
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.headOrig
        path = self.cfg.headPath
        joinTol = self.cfg.joinCutTol

        hd = self.api.genLineSplineRevolveX(orig, path, -180)\
            .scale(1, 1, botRat).mv(0, 0, joinTol -midTck)
        
        if midTck > 0:
            midR = self.api.genLineSplineExtrusionZ(orig, path, midTck)\
                .mv(0, 0, -midTck)
            midL = midR.mirrorXZ()
            hd = hd.join(midL).join(midR)

        if topRat > 0:
            top = self.api.genLineSplineRevolveX(orig, path, 180)\
                .scale(1, 1, topRat).mv(0, 0, -joinTol)
            hd = hd.join(top)

        topCut = self.api.genRodY(2*hdWth, hdLen)\
            .mv(-ntHt, 0, .75*hdLen + fbTck + ntHt)
        frontCut = self.api.genRodY(2*hdWth, .65*spHt)\
            .scale(.5, 1, 1).mv(-hdLen, 0, -fspTck - .6*spHt)
        hd = hd.cut(frontCut).cut(topCut)

        self.shape = hd
        return hd

def main(args = None):
    """ Generate Head """
    return main_maker(module_name=__name__,
                    class_name='LeleHead',
                    args=args)

def test_head():
    """ Test Head """
    test_loop(module=__name__)

if __name__ == '__main__':
    main()
