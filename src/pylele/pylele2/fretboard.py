#!/usr/bin/env python3

"""
    Pylele Fretboard
"""
import os
import sys
import math

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.utils import degrees, radians
from b13d.api.solid import test_loop, main_maker, Implementation, ColorEnum
from pylele.pylele2.base import LeleBase

def fretboard_path(fretbdLen,
              nutWth,
              fretbdWth,
              isCut: bool = False,
              half: bool = False) -> list[tuple[float, float]]:
    """ Generate Fretboard Path """
    cutAdj = FIT_TOL if isCut else 0

    right_edge = [
        (-cutAdj             , nutWth/2    + cutAdj),
        (fretbdLen + 2*cutAdj, fretbdWth/2 + cutAdj),
        ]

    left_edge  = [
        (fretbdLen + 2*cutAdj, -fretbdWth/2 - cutAdj),
        (             -cutAdj, -nutWth/2    - cutAdj),
        ]

    mid_edge = [
            (fretbdLen + 2*cutAdj,  cutAdj),
            (             -cutAdj,  cutAdj),
            ]

    if half:
        return right_edge + mid_edge
    
    return right_edge + left_edge

def fretboard_path_3d(
                    frad: float,
                    fretbdLen: float,
                    fretbdRiseAng: float,
                    nutWth: float,
                    fretbdWth: float,
                    fbHt: float,
                    top: bool = False,
                    isCut: bool = False) -> list[tuple[float, float, float]]:
    """ Generate Fretboard Path with 3d coordinates """
    cutAdj = FIT_TOL if isCut else 0

    # z axis
    if top:
        # top face
        fbHt0 = fbHt-frad
        fbHt1 = fbHt0 - math.sin(radians(fretbdRiseAng)) * fretbdLen
    else:
        # bottom face
        fbHt0 = fbHt1 = 0

    right_edge = [
        (-cutAdj+frad             , nutWth/2    + cutAdj - frad, fbHt1),
        (fretbdLen + 2*cutAdj-frad, fretbdWth/2 + cutAdj - frad, fbHt0),
        ]

    left_edge  = [
        (fretbdLen + 2*cutAdj-frad, -fretbdWth/2 - cutAdj + frad, fbHt0),
        (             -cutAdj+frad, -nutWth/2    - cutAdj + frad, fbHt1),
    ]

    return right_edge + left_edge

class LeleFretboard(LeleBase):
    """Pylele Fretboard Generator class"""

    def gen_with_fillet(self,
                        frad,
                        fretbdLen,
                        fretbdWth,
                        fbTck,
                        fbHt) -> Shape:
        """Generate Fretboard using fillets"""

        path = fretboard_path(fretbdLen=self.cfg.fretbdLen,
                    nutWth=self.cfg.nutWth,
                    fretbdWth=self.cfg.fretbdWth,
                    isCut=self.isCut)
        fretbd = self.api.polygon_extrusion(path, fbHt)

        if self.isCut:
            return fretbd.mv(0, 0, -self.api.tolerance())

        topCut = (
            self.api.box(fretbdLen * 2, fretbdWth, fbHt)
            .rotate_y(-self.cfg.fretbdRiseAng)
            .mv(0, 0, fbTck + fbHt / 2)
        )
        fretbd -= topCut

        ## fillet the end of the fretboard
        fretbd = fretbd.fillet([(fbTck / 2, 0, fbTck / 2)], frad)

        ## fillet the start of the fretboard
        fretbd = fretbd.fillet([(fretbdLen, 0, fbHt)], frad)

        ## fillet the fretboard sides
        fretbd = fretbd.fillet(
            [(fretbdLen / 2, fretbdWth / 2, fbHt / 2)], frad
        )
        fretbd = fretbd.fillet(
            [(fretbdLen / 2, -fretbdWth / 2, fbHt / 2)], frad
        ) 
        return fretbd

    def gen_with_hull(self,
                        frad,
                        fretbdLen,
                        fretbdWth,
                        fbHt) -> Shape:
        """Generate Fretboard using hull"""

        fretbd = None
        for top in [True, False]:
            face_edges = fretboard_path_3d(
                        frad=frad,
                        fretbdLen=fretbdLen,
                        fretbdRiseAng=self.cfg.fretbdRiseAng,
                        nutWth = self.cfg.nutWth,
                        fretbdWth=fretbdWth,
                        fbHt=fbHt,
                        top=top,
                        isCut=self.isCut)    
            fretbd = self.api.regpoly_sweep(frad, face_edges) + fretbd
        return fretbd.hull()

    def gen(self) -> Shape:
        """Generate Fretboard"""

        cutAdj = FIT_TOL if self.isCut else 0
        fretbdLen = self.cfg.fretbdLen + 2 * cutAdj
        fretbdWth = self.cfg.fretbdWth + 2 * cutAdj
        fbTck = self.cfg.FRETBD_TCK + 2 * cutAdj
        fbHt = self.cfg.fretbdHt + 2 * cutAdj

        # fillet radius
        frad = fbTck / 2

        if self.isCut or (
            self.cli.implementation in [
            Implementation.CADQUERY,
            Implementation.BLENDER,
        ]):
            # backends with fillet support
            fb = self.gen_with_fillet(frad=frad,
                        fretbdLen=fretbdLen,
                        fretbdWth=fretbdWth,
                        fbTck=fbTck,
                        fbHt=fbHt)

        else: 
            # backends that do not support fillet (but support hull)
            fb = self.gen_with_hull(frad=frad,
                        fretbdLen=fretbdLen,
                        fretbdWth=fretbdWth,
                        fbHt=fbHt)

        return fb.set_color(ColorEnum.BLACK)

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
