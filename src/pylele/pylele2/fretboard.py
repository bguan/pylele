#!/usr/bin/env python3

"""
    Pylele Fretboard
"""
import os
import sys
import math

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.api.core import Shape
from pylele.api.constants import FIT_TOL
from pylele.api.utils import degrees
from pylele.api.solid import test_loop, main_maker, Implementation
from pylele.pylele2.base import LeleBase

def fretboard_path(fretbdLen,
              nutWth,
              fretbdWth,
              isCut: bool = False,
              half: bool = False) -> list[tuple[float, float]]:
    """ Generate Fretboard Path """
    cutAdj = FIT_TOL if isCut else 0

    half_path = [
        (-cutAdj             , nutWth/2    + cutAdj),
        (fretbdLen + 2*cutAdj, fretbdWth/2 + cutAdj),
    ]

    full_path = half_path + [
        (fretbdLen + 2*cutAdj, -fretbdWth/2 - cutAdj),
        (             -cutAdj, -nutWth/2    - cutAdj),
    ]

    if half:
        return half_path + [
            (fretbdLen + 2*cutAdj,  cutAdj),
            (             -cutAdj,  cutAdj),
                            ]
    
    return full_path

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
        path = fretboard_path(fretbdLen=self.cfg.fretbdLen,
                         nutWth=nut_width,
                         fretbdWth=self.cfg.fretbdWth,
                         isCut=self.isCut)
        fretbd = self.api.polygon_extrusion(path, fbHt)

        if self.isCut:
            fretbd = fretbd.mv(0, 0, -self.api.tolerance())
        else:
            topCut = (
                self.api.box(fbLen * 2, fbWth, fbHt)
                .rotate_y(-riseAng)
                .mv(0, 0, fbTck + fbHt / 2)
            )
            fretbd -= topCut
            frad = fbTck / 2

            if self.cli.implementation in [
                Implementation.CADQUERY,
                Implementation.BLENDER,
            ]:
                ## fillet the end of the fretboard
                fretbd = fretbd.fillet([(fbTck / 2, 0, fbTck / 2)], frad)

                ## fillet the start of the fretboard
                fretbd = fretbd.fillet([(fbLen, 0, fbHt)], frad)

                ## fillet the fretboard sides
                fretbd = fretbd.fillet(
                    [(fbLen / 2, fbWth / 2, fbHt / 2)], frad
                )
                fretbd = fretbd.fillet(
                    [(fbLen / 2, -fbWth / 2, fbHt / 2)], frad
                )

            else:
                extra_len = 10

                ## fillet the end of the fretboard
                fretbd -= self.api.rounded_edge_mask(
                    direction="y", l=fbWth + extra_len, rad=frad, rot=270
                ).mv(frad, 0, frad)

                ## fillet the fretboard sides
                fretbd -= (
                    self.api.rounded_edge_mask(
                        direction="x", l=fbLen + extra_len, rad=frad, rot=0
                    )
                    .rotate_y(-riseAng)
                    .rotate_z(wide_angle)
                    .mv(fbLen / 2, fbWth / 2 - fbTck - frad, fbHt / 2)
                )

                ## fillet the fretboard sides
                fretbd -= (
                    self.api.rounded_edge_mask(
                        direction="x", l=fbLen + extra_len, rad=frad, rot=90
                    )
                    .rotate_y(-riseAng)
                    .rotate_z(-wide_angle)
                    .mv(fbLen / 2, -fbWth / 2 + fbTck + frad, fbHt / 2)
                )

                ## fillet the start of the fretboard
                fretbd -= self.api.rounded_edge_mask(
                    direction="y", l=fbWth + extra_len, rad=frad, rot=0
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
    tests = {
        "default": ["-refv", "39353"],
        "cut": ["-C", "-refv", "62360"],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_fretboard_mock(self):
    """Test Fretboard"""
    test_fretboard(self, apis=["mock"])


if __name__ == "__main__":
    main()
