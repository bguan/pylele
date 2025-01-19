#!/usr/bin/env python3

"""
    Pylele Brace
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.solid import main_maker, test_loop, ColorEnum
from b13d.api.core import Shape
from pylele.pylele2.base import LeleBase


class LeleBrace(LeleBase):
    """Pylele Brace Generator class"""

    def gen(self) -> Shape:
        """Generate Brace"""

        scLen = float(self.cli.scale_length)
        brdgZ = self.cfg.brdgZ
        chmFr = self.cfg.chmFront
        chmBk = self.cfg.chmBack
        chmWth = self.cfg.chmWth
        # topRat = self.cfg.TOP_RATIO
        brace = (
            self.api.cylinder_rounded_x(0.5 * (chmFr + chmBk), 0.05 * chmWth, 1)
            .scale(1, 0.3, 1)
            .mv(scLen - 0.25 * chmBk, 0, brdgZ)
        )
        return brace.set_color(ColorEnum.WHITE)


def main(args=None):
    """Generate Brace"""
    return main_maker(module_name=__name__, class_name="LeleBrace", args=args)


def test_brace(self, apis=None):
    """Test Brace"""
    tests = {'default':['-refv','3570']}
    test_loop(module=__name__, apis=apis, tests=tests)


def test_brace_mock(self):
    """Test Brace"""
    test_brace(self, apis=["mock"])


if __name__ == "__main__":
    main()
