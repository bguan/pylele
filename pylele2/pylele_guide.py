#!/usr/bin/env python3

"""
    Pylele Guide
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase


class LeleGuide(LeleBase):
    """Pylele Guide Generator class"""

    def gen(self) -> Shape:
        """Generate Guide"""
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        nStrs = self.cli.num_strings
        sR = self.cfg.STR_RAD
        gdR = self.cfg.GUIDE_RAD + cutAdj
        gdX = self.cfg.guideX
        gdZ = self.cfg.guideZ
        gdHt = self.cfg.guideHt
        gdWth = self.cfg.guideWth
        gdGap = self.cfg.guidePostGap

        guide = (
            None
            if self.isCut
            else self.api.genRndRodY(
                (gdWth - 0.5 * gdGap + sR + 2 * gdR) if nStrs > 1 else 6 * gdR,
                1.1 * gdR,
                1,
            ).mv(gdX, 0, gdZ + gdHt)
        )

        for y in self.cfg.guideYs:
            post = self.api.genRodZ(gdHt, gdR)
            post = post.mv(gdX, y, gdZ + gdHt/2)
            guide = post + guide

        return guide


def main(args=None):
    """Generate Guide"""
    return main_maker(module_name=__name__, class_name="LeleGuide", args=args)


def test_guide(self,apis=None):
    """ Test Guide """
    tests = {
        'default' : [],
        'cut'     : ['-C']
    }
    test_loop(module=__name__,tests=tests,apis=apis)
    
def test_guide_mock(self):
    """Test Guide"""
    test_guide(self, apis=["mock"])


if __name__ == "__main__":
    main()
