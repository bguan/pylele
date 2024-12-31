#!/usr/bin/env python3

"""
    Pylele Top
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.body import LeleBody
from pylele.pylele2.body import genBodyPath, gen_body_origin

class LeleTop(LeleBody):
    """Pylele Top Generator class"""

    def gen(self) -> Shape:
        """Generate Top"""

        fitTol = FIT_TOL
        joinTol = self.api.tolerance()
        cutAdj = (fitTol + joinTol) if self.isCut else 0
        midTck = self.cfg.extMidTopTck + cutAdj

        top = self.gourd_shape()

        if midTck > 0:
            top = top.mv(0, 0, midTck - joinTol)
            top += self.gourd_flat_extrusion(thickness=midTck)

        return top


def main(args=None):
    """Generate Top"""
    return main_maker(module_name=__name__, class_name="LeleTop", args=args)

tests = {"cut": ["-C"]}


def test_top(self):
    """Test Top"""
    test_loop(module=__name__, tests=tests)


def test_top_mock(self):
    """Test Top"""
    test_loop(module=__name__, tests=tests, apis=["mock"])


if __name__ == "__main__":
    main()
