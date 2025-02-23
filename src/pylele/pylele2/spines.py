#!/usr/bin/env python3

"""
    Pylele Spines
"""

from math import floor

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase
from pylele.pylele2.config import LeleBodyType


class LeleSpines(LeleBase):
    """Pylele Spines Generator class"""

    def configure(self):
        LeleBase.configure(self)
        self.configure_spines()

    def configure_spines(self):
        """ Spine Configuration """
        # Spine configs
        self.cfg.spineX = -self.cfg.headLen
        self.cfg.spineLen = self.cfg.headLen + float(self.cli.scale_length)
        if not self.cli.body_type in [LeleBodyType.TRAVEL]:
            self.cfg.spineLen += self.cfg.chmBack + self.cfg.rimWth
        self.cfg.spineGap = (1 if self.cfg.is_odd_strs() else 2)*self.cli.nut_string_gap
        self.cfg.spineY = []
        if (self.cli.num_spines % 2) != 0:
            self.cfg.spineY.append(0)
        for i in range(1,floor(self.cli.num_spines/2)+1):
            self.cfg.spineY += [-i*self.cfg.spineGap/2, i*self.cfg.spineGap/2]

    def gen(self) -> Shape:
        """Generate Spines"""

        cutAdj = (FIT_TOL + self.api.tolerance()) if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen+ 2*cutAdj
        spHt = self.cfg.SPINE_HT + 2*cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK  + 2*self.api.tolerance()

        shape = None
        for y_spine in self.cfg.spineY:
            spine = self.api.box(spLen, spWth, spHt)
            spine <<= (spX + spLen/2, y_spine, -fspTck - spHt/2)
            
            shape = spine + shape
        
        return shape


def main(args=None):
    """Generate Spines"""
    return main_maker(module_name=__name__, class_name="LeleSpines", args=args)


def test_spines(self):
    """Test Spines"""
    test_loop(module=__name__)


def test_spines_mock(self):
    """Test Spines"""
    test_loop(module=__name__, apis=["mock"])


if __name__ == "__main__":
    main()
