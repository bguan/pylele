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
from pylele.pylele2.fretboard import fretboard_path


class LeleNeck(LeleBase):
    """Pylele Neck Generator class"""

    def gen(self) -> Shape:
        """Generate Neck"""
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        joinTol = self.api.tolerance()

        neckPath = fretboard_path(self.cfg.neckLen, self.cfg.nutWth, self.cfg.neckWth, half=True)

        # rounded section
        neck = self.api.spline_revolve((0, 0), neckPath, -180)
        neck = neck.scale(1, 1, botRat).mv(0, 0, -midTck + joinTol)

        # flat mid section
        if midTck > 0:
            path = fretboard_path(self.cfg.neckLen, self.cfg.nutWth, self.cfg.neckWth)
            neck += self.api.polygon_extrusion(path, midTck).mv(0, 0, -midTck)

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
