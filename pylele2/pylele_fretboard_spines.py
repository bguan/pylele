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
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spWth = self.cfg.SPINE_WTH + 2 * cutAdj  # to align with spine cuts
        fspLen = (
            self.cfg.fbSpineLen()
            + 2 * cutAdj
            + 2 * (self.api.getJoinCutTol() if self.isCut else 0)
        )
        fspX = self.cfg.NUT_HT

        fsp = self.api.genBox(fspLen, spWth, fspTck).mv(
            fspX + fspLen / 2 - 2 * cutAdj, spY1, -fspTck / 2
        )

        if spY1 != spY2:
            fsp2 = self.api.genBox(fspLen, spWth, fspTck).mv(
                fspX + fspLen / 2 - 2 * cutAdj, spY2, -fspTck / 2
            )
            fsp = fsp.join(fsp2)

        self.shape = fsp
        return self.shape


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
