#!/usr/bin/env python3

"""
    Pylele Top
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape, Fidelity
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL

class LeleTop(LeleBase):
    """ Pylele Top Generator class """

    def gen(self) -> Shape:
        """ Generate Top """

        if self.isCut:
            origFidel = self.cli.fidelity
            self.api.setFidelity(Fidelity.LOW)

        fitTol = FIT_TOL
        joinTol = self.api.getJoinCutTol()
        cutAdj = (fitTol + joinTol) if self.isCut else 0
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.extMidTopTck + cutAdj
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyCutPath if self.isCut else self.cfg.bodyPath
        top = self.api.genLineSplineRevolveX(bOrig, bPath, 180).scale(1, 1, topRat)
        if midTck > 0:
            top = top.mv(0, 0, midTck - joinTol)
            midR = self.api.genLineSplineExtrusionZ(
                bOrig, bPath, midTck if self.isCut else midTck)
            top = top.join(midR.mirrorXZ_and_join())

        if self.isCut:
            self.api.setFidelity(origFidel)

        self.shape = top
        return top

def main(args=None):
    """ Generate Top """
    return main_maker(module_name=__name__,
                    class_name='LeleTop',
                    args=args)

tests = {
    'cut'     : ['-C']
}

def test_top(self):
    """ Test Top """
    test_loop(module=__name__,tests=tests)

def test_top_mock(self):
    """ Test Top """
    test_loop(module=__name__,tests=tests,apis=['mock'])

if __name__ == '__main__':
    main()
