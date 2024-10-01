#!/usr/bin/env python3

"""
    Pylele Fretboard Dots
"""

import argparse
import os
import math
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_utils import accumDiv, radians
from api.pylele_solid import main_maker, test_loop
from pylele_config_common import SEMI_RATIO
from pylele2.pylele_base import LeleBase


def pylele_dots_parser(parser=None):
    """
    Pylele Dots Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Configuration")

    parser.add_argument(
        "-d",
        "--dot_frets",
        help="Comma-separated fret[:dots] pairs, default 3,5:2,7,10,12:3,15,17:2,19,22",
        type=lambda d: {
            int(l[0]): 1 if len(l) < 2 else int(l[1])
            for l in (fns.split(":") for fns in d.split(","))
        },
        default={3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1},
    )

    parser.add_argument(
        "-fdr", "--dots_radius", help="Dots Radius [mm]", type=float, default=1.5
    )

    return parser


class LeleFretboardDots(LeleBase):
    """Pylele Fretboard Dots Generator class"""

    def gen(self) -> Shape:
        """Generate Fretboard Dots"""

        cutAdj = FIT_TOL if self.isCut else 0
        scLen = float(self.cli.scale_length)
        fbLen = self.cfg.fretbdLen
        fbTck = self.cfg.FRETBD_TCK
        maxFrets = self.cfg.MAX_FRETS
        dep = self.cfg.EMBOSS_DEP + cutAdj
        wideAng = self.cfg.neckWideAng
        riseAng = self.cfg.fretbdRiseAng
        nutSGap = self.cli.nut_string_gap
        dotRad = self.cli.dots_radius + cutAdj
        fret2Dots = self.cli.dot_frets

        dots = None
        sgap = nutSGap
        # half length of fret 1
        flen = 0.5 * scLen / accumDiv(1, 12, SEMI_RATIO)
        n = 1
        acclen = flen
        while acclen < fbLen and n <= maxFrets:
            if n in fret2Dots:
                ht = fbTck + math.tan(radians(riseAng)) * acclen
                pos = (
                    [0]
                    if fret2Dots[n] == 1
                    else [-0.5, 0.5] if fret2Dots[n] == 2 else [-1, 0, 1]
                )
                for p in pos:
                    dot = self.api.genRodZ(dep, dotRad).mv(
                        acclen - 0.5 * flen, p * sgap, ht
                    )
                    dots = dot if dots is None else dots.join(dot)

            sgap = 0.5 * acclen * math.tan(radians(wideAng)) + nutSGap
            flen /= SEMI_RATIO
            acclen += flen
            n += 1
    
        return dots

    def gen_parser(self, parser=None):
        """
        pylele Command Line Interface
        """
        parser = pylele_dots_parser(parser=parser)
        return super().gen_parser(parser=parser)


def main(args=None):
    """Generate Fretboard"""
    return main_maker(module_name=__name__, class_name="LeleFretboardDots", args=args)


tests = {
    "dots_position": ["-d", "1,2,3:2,4,5"],
    "dots_radius": ["-fdr", "3"],
}


def test_fretboard_dots(self, apis=None):
    """Test Fretoard dots"""
    test_loop(module=__name__, tests=tests, apis=apis)


def test_fretboard_dots_mock(self):
    """Test Fretoard dots"""
    test_fretboard_dots(self, apis=["mock"])


if __name__ == "__main__":
    main()
