#!/usr/bin/env python3

"""
    Pylele Fretboard
"""
import os
import sys
import math

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL, FILLET_RAD
from api.pylele_utils import degrees
from api.pylele_solid import test_loop, main_maker
from pylele2.pylele_base import LeleBase


class LeleFretboard(LeleBase):
    """Pylele Fretboard Generator class"""

    def gen(self) -> Shape:
        """Generate Fretboard"""

        cutAdj = FIT_TOL if self.isCut else 0
        fbLen = self.cfg.fretbdLen + 2 * cutAdj
        fbWth = self.cfg.fretbdWth + 2 * cutAdj
        fbTck = self.cfg.FRETBD_TCK + 2 * cutAdj
        fbHt = self.cfg.fretbdHt + 2 * cutAdj
        nut_width = self.cfg.nutWth
        riseAng = self.cfg.fretbdRiseAng
        wide_angle = degrees(math.atan((fbWth - nut_width) / (2 * fbLen)))

        # path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        path = self.cfg.genFbPath(isCut=self.isCut)
        fretbd = self.api.genPolyExtrusionZ(path, fbHt)

        if self.isCut:
            fretbd = fretbd.mv(0, 0, -self.api.getJoinCutTol())
        else:
            topCut = (
                self.api.genBox(fbLen * 2, fbWth, fbHt)
                .rotateY(-riseAng)
                .mv(0, 0, fbTck + fbHt / 2)
            )
            fretbd -= topCut

            frad = fbTck / 2
            ## fillet the end of the fretboard
            fretbd -= self.api.gen_rounded_edge_mask(
                direction="y", l=fbWth, rad=frad, rot=270
            ).mv(fbTck / 2, 0, fbTck / 2)

            ## fillet the fretboard sides
            fretbd -= (
                self.api.gen_rounded_edge_mask(
                    direction="x", l=fbLen, rad=frad, rot=0
                )
                .rotateY(-riseAng)
                .rotateZ(wide_angle)
                .mv(fbLen / 2, fbWth / 2 - fbTck - frad, fbHt / 2)
            )

            ## fillet the fretboard sides
            fretbd -= (
                self.api.gen_rounded_edge_mask(
                    direction="x", l=fbLen, rad=fbTck / 2, rot=90
                )
                .rotateY(-riseAng)
                .rotateZ(-wide_angle)
                .mv(fbLen / 2, -fbWth / 2 + fbTck + fbTck / 2, fbHt / 2)
            )

            ## fillet the start of the fretboard
            # length of fillet edge needs to be a little longer to go beyond the sides
            fretbd -= self.api.gen_rounded_edge_mask(
                direction="y", l=1.1 * fbWth, rad=frad, rot=0  # FILLET_RAD
            ).mv(fbLen - frad, 0, fbHt - frad)

        return fretbd


def main(args=None):
    """Generate Fretboard"""
    return main_maker(
        module_name=__name__,
        class_name="LeleFretboard",
        args=args,
    )


def test_fretboard(self, apis=None):
    """Test Fretboard"""
    tests = {"cut": ["-C", "-refv", "62360"]}
    test_loop(module=__name__, tests=tests, apis=apis)


def test_fretboard_mock(self):
    """Test Fretboard"""
    test_fretboard(self, apis=["mock"])


if __name__ == "__main__":
    main()
