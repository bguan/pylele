#!/usr/bin/env python3

"""
    Pylele Fretboard Spines
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.spines import LeleSpines


class LeleFretboardSpines(LeleSpines):
    """Pylele Fretboard Spines Generator class"""

    def fretboard_spine_len(self) -> float:
        """ Spine Length """
        return self.cfg.neckLen - self.cfg.NUT_HT + self.cfg.neckJntLen

    def gen(self) -> Shape:
        """Generate Fretboard Spines"""

        cutAdj = FIT_TOL if self.isCut else 0
        fspTck = self.cfg.FRETBD_SPINE_TCK + 2 * (
            self.api.tolerance() if self.isCut else 0
        )

        spWth = self.cfg.SPINE_WTH + 2 * cutAdj  # to align with spine cuts
        fspLen = (
            self.fretboard_spine_len()
            + 2 * cutAdj
            + 2 * (self.api.tolerance() if self.isCut else 0)
        )
        fspX = self.cfg.NUT_HT

        shape = None
        for y_spine in self.cfg.spineY:
            spine = self.api.box(fspLen, spWth, fspTck)
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
