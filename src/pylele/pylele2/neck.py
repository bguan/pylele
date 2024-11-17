#!/usr/bin/env python3

"""
    Pylele Neck
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.api.core import Shape
from pylele.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase


class LeleNeck(LeleBase):
    """Pylele Neck Generator class"""

    def gen(self) -> Shape:
        """Generate Neck"""
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.neckPath
        joinTol = self.api.tolerance()
        neck = None
        if midTck > 0:
            neck = self.api.polygon_extrusion(path, midTck).mv(0, 0, -midTck)

        neckPath = [(nkLen, 0), (nkLen, nkWth / 2), (0, ntWth / 2)]
        neckCone = self.api.spline_revolve((0, 0), neckPath, -180)
        neckCone = neckCone.scale(1, 1, botRat).mv(0, 0, -midTck + joinTol)

        neck = neckCone + neck

        return neck


def main(args=None):
    """Generate Neck"""
    return main_maker(module_name=__name__, class_name="LeleNeck", args=args)


def test_neck(self, apis=None):
    """Test Neck"""
    tests = {'default':['-refv','106424']}
    test_loop(module=__name__, apis=apis,tests=tests)


def test_neck_mock(self):
    """Test Neck"""
    test_neck(self, apis=["mock"])


if __name__ == "__main__":
    main()
