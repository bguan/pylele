#!/usr/bin/env python3

"""
    Pylele Top
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape, Fidelity
from pylele2.pylele_base import LeleBase, test_loop
from pylele1.pylele_config import FIT_TOL

class LeleTop(LeleBase):
    """ Pylele Top Generator class """

    def gen(self) -> Shape:
        """ Generate Top """

        if self.isCut:
            origFidel = self.cfg.fidelity
            self.api.setFidelity(Fidelity.LOW)

        fitTol = FIT_TOL
        joinTol = self.cfg.joinCutTol
        cutAdj = (fitTol + joinTol) if self.isCut else 0
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.extMidTopTck + cutAdj
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyCutPath if self.isCut else self.cfg.bodyPath
        top = self.api.genLineSplineRevolveX(bOrig, bPath, 180).scale(1, 1, topRat)
        if midTck > 0:
            top = top.mv(0, 0, midTck)
            midR = self.api.genLineSplineExtrusionZ(
                bOrig, bPath, midTck if self.isCut else midTck)
            midL = midR.mirrorXZ()
            top = top.join(midL).join(midR)

        if self.isCut:
            self.api.setFidelity(origFidel)

        self.shape = top
        return top

def main(args=None):
    """ Generate Top """
    solid = LeleTop(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_top():
    """ Test Top """
    tests = {
        'cut'     : ['-C']
    }
    test_loop(module=__name__,tests=tests)

if __name__ == '__main__':
    main()
