#!/usr/bin/env python3

"""
    Pylele Fretboard
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
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
        riseAng = self.cfg.fretbdRiseAng

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
            fretbd = fretbd.cut(topCut)
            fretbd = fretbd.filletByNearestEdges([(fbLen, 0, fbHt)], fbTck / 2)

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
