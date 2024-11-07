#!/usr/bin/env python3

"""
    Pylele Brace
"""

import os
import sys

from api.pylele_solid import main_maker, test_loop

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase


class LeleBrace(LeleBase):
    """Pylele Brace Generator class"""

    def gen(self) -> Shape:
        """Generate Brace"""

        scLen = float(self.cli.scale_length)
        brdgZ = self.cfg.brdgZ
        chmFr = self.cfg.chmFront
        chmBk = self.cfg.chmBack
        chmWth = self.cfg.chmWth
        topRat = self.cfg.TOP_RATIO

        brace = (
            self.api.genRndRodX(0.5 * (chmFr + chmBk), 0.4 * chmWth * topRat, 1)
            .scale(1, 0.25, 1)
            .mv(scLen - 0.25 * chmBk, 0, brdgZ)
        )

        cut_thick = 100
        cutter = self.api.genBox(2 * scLen, chmWth, cut_thick).mv(
            scLen, 0, brdgZ + cut_thick / 2
        )

        # generate top cut
        brace = brace.cut(cutter).mv(0, 0, self.api.getJoinCutTol())

        return brace


def main(args=None):
    """Generate Brace"""
    return main_maker(module_name=__name__, class_name="LeleBrace", args=args)


def test_brace(self, apis=None):
    """Test Brace"""
    tests = {'default':['-refv','1496']}
    test_loop(module=__name__, apis=apis, tests=tests)


def test_brace_mock(self):
    """Test Brace"""
    test_brace(self, apis=["mock"])


if __name__ == "__main__":
    main()
