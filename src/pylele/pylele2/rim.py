#!/usr/bin/env python3

"""
    Pylele Rim
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase
from pylele.pylele2.config import LeleBodyType
from pylele.pylele2.chamber import gen_extruded_oval

class LeleRim(LeleBase):
    """Pylele Rim Generator class"""
    RIM_TCK = 1

    def gen_gourd(self) -> Shape:
        """Generate Rim"""
        joinTol = self.api.tolerance()
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        scLen = float(self.cli.scale_length)
        rad = self.cfg.chmWth / 2 + self.cfg.rimWth
        tck = self.RIM_TCK + 2 * cutAdj

        frontWthRatio = (self.cfg.chmFront + self.cfg.rimWth) / rad
        backWthRatio  = (self.cfg.chmBack  + self.cfg.rimWth) / rad

        rimFront = self.api.cylinder_half(rad,  True, tck).scale(frontWthRatio, 1, 1)
        rimBack  = self.api.cylinder_half(rad, False, tck).scale(backWthRatio , 1, 1)

        rimFront <<= (scLen          , 0, joinTol - tck / 2)
        rimBack  <<= (scLen - joinTol, 0, joinTol - tck / 2)

        return rimFront + rimBack
    
    def gen_travel(self):
        joinTol = self.api.tolerance()
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        rad = self.cfg.chmWth / 2 + self.cfg.rimWth
        tck = self.RIM_TCK + 2 * cutAdj

        rim_front = -self.cfg.chmFront + rad - self.cfg.rimWth
        rim_back  = rim_front + self.cfg.chmFront - 2 * rad - self.cfg.brdgLen + 2*self.cfg.rimWth

        return gen_extruded_oval(self.api, rim_front, rim_back, 2 * rad - self.cli.travel_body_width, tck)\
            .mv(float(self.cli.scale_length), 0, 0)

    def gen(self) -> Shape:
        """Generate Rim"""
        if self.cli.body_type == LeleBodyType.TRAVEL:
            return self.gen_travel()
        else:
            return self.gen_gourd()

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
