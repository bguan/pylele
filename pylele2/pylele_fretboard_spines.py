#!/usr/bin/env python3

"""
    Pylele Fretboard Spines
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase


class LeleFretboardSpines(LeleBase):
    """Pylele Fretboard Spines Generator class"""

    def gen(self) -> Shape:
        """Generate Fretboard Spines"""

        cutAdj = FIT_TOL if self.isCut else 0
        fspTck = self.cfg.FRETBD_SPINE_TCK + 2 * (
            self.api.getJoinCutTol() if self.isCut else 0
        )

        spWth = self.cfg.SPINE_WTH + 2 * cutAdj  # to align with spine cuts
        fspLen = (
            self.cfg.fbSpineLen()
            + 2 * cutAdj
            + 2 * (self.api.getJoinCutTol() if self.isCut else 0)
        )
        fspX = self.cfg.NUT_HT

        shape = None
        for y_spine in self.cfg.spineY:
            spine = self.api.genBox(fspLen, spWth, fspTck)
            spine <<= (fspX + fspLen/2 - 2*cutAdj, y_spine, -fspTck/2)
            
            shape = spine + shape

        return shape


def main(args=None):
    """Generate Fretboard Spines"""
    return main_maker(module_name=__name__, class_name="LeleFretboardSpines", args=args)


def test_fretboard_spines(self, apis=None):
    """Test Fretoard Spines"""
    test_loop(module=__name__, apis=apis)


def test_fretboard_spines_mock(self):
    """Test Fretoard Spines"""
    test_fretboard_spines(self, apis=["mock"])


if __name__ == "__main__":
    main()
