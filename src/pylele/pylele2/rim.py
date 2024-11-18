#!/usr/bin/env python3

"""
    Pylele Rim
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.api.core import Shape
from pylele.api.constants import FIT_TOL
from pylele.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase


class LeleRim(LeleBase):
    """Pylele Rim Generator class"""

    def gen(self) -> Shape:
        """Generate Rim"""
        joinTol = self.api.tolerance()
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        scLen = float(self.cli.scale_length)
        rad = self.cfg.chmWth / 2 + self.cfg.rimWth
        tck = self.cfg.RIM_TCK + 2 * cutAdj
        frontWthRatio = (self.cfg.chmFront + self.cfg.rimWth) / rad
        backWthRatio = (self.cfg.chmBack + self.cfg.rimWth) / rad
        rimFront = self.api.cylinder_half(rad, True, tck).scale(frontWthRatio, 1, 1)
        rimBack = self.api.cylinder_half(rad, False, tck).scale(backWthRatio, 1, 1)
        rimFront = rimFront.mv(scLen, 0, joinTol - tck / 2).join(
            rimBack.mv(scLen - joinTol, 0, joinTol - tck / 2)
        )

        return rimFront


def main(args=None):
    """Generate Rim"""
    return main_maker(module_name=__name__, class_name="LeleRim", args=args)


def test_rim(self, apis=None):
    """Test Rim"""

    tests = {"cut": ["-C"]}
    test_loop(module=__name__, tests=tests, apis=apis)


def test_rim_mock(self):
    """Test Rim"""
    test_rim(self, apis=["mock"])


if __name__ == "__main__":
    main()
