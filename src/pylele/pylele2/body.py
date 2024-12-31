#!/usr/bin/env python3

"""
    Pylele Body
"""

import argparse
import os
import sys
from math import tan, inf

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.solid import main_maker, test_loop, FIT_TOL
from b13d.api.utils import radians
from pylele.config_common import TunerType
from pylele.pylele2.config import LeleBodyType
from pylele.pylele2.base import LeleBase

def genBodyPath(
                 scaleLen: float,
                 neckLen: float,
                 neckWth: float,
                 bodyWth: float,
                 bodyBackLen: float,
                 endWth: float,
                 neckWideAng: float,
                 isCut: bool = False,
                ) -> list[tuple[float, float, float, float]]:
    
    cutAdj = FIT_TOL if isCut else 0
    nkLen = neckLen
    nkWth = neckWth + 2*cutAdj
    bWth = bodyWth + 2*cutAdj
    bBkLen = bodyBackLen + cutAdj
    eWth = min(bWth, endWth) + (2*cutAdj if endWth > 0 else 0)
    
    neckDX = 1
    neckDY = neckDX * tan(radians(neckWideAng))

    bodySpline = [
        (nkLen + neckDX, nkWth/2 + neckDY, neckDY/neckDX, .5, .3),
        (scaleLen, bWth/2, 0, .6),
        (scaleLen + bBkLen, eWth/2 +.1, -inf, (1-eWth/bWth)/2),
    ]

    bodyPath = [
        (nkLen, nkWth/2),
        bodySpline,
        (scaleLen + bBkLen, eWth/2),
    ]

    if eWth > 0:
        bodyPath.insert(3,(scaleLen + bBkLen, 0))

    return bodyPath

def gen_body_origin(neckLen: float):
    return (neckLen, 0)

def pylele_body_parser(parser=None):
    """
    Pylele Body Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Configuration")

    return parser

class LeleBody(LeleBase):
    """Pylele Body Generator class"""

    def flat_body_bottom(self, body_origin, body_path):
        """generate the bottom of a flat body"""
        bot_below = (
            self.api.spline_revolve(body_origin, body_path, -180)
            .scale(1, 1, self.cfg.TOP_RATIO)
            .mv(0, 0, -self.cli.flat_body_thickness)
        )
        return bot_below

    def gen(self) -> Shape:
        """Generate Body"""
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = gen_body_origin(self.cfg.neckLen)

        bPath = genBodyPath(
                 scaleLen = float(self.cli.scale_length),
                 neckLen = self.cfg.neckLen,
                 neckWth = self.cfg.neckWth,
                 bodyWth = self.cfg.bodyWth,
                 bodyBackLen = self.cfg.bodyBackLen,
                 endWth = self.cli.end_flat_width,
                 neckWideAng = self.cfg.neckWideAng,
                 isCut = self.isCut)
        
        joinTol = self.api.tolerance()

        if self.cli.body_type == LeleBodyType.GOURD:
            # Gourd body
            bot = self.api.spline_revolve(bOrig, bPath, -180).scale(1, 1, botRat)

            if midTck > 0:
                # Generates flat middle section of body
                bot <<= (0, 0, joinTol - midTck)
                midR = self.api.spline_extrusion(bOrig, bPath, -midTck)
                bot += midR.mirror_and_join()

        elif self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.TRAVEL]:

            bot_below = self.flat_body_bottom(body_origin=bOrig,
                                              body_path=bPath
                                              ).mv(0, 0, joinTol)

            # Flat body
            midR = self.api.spline_extrusion(
                bOrig, bPath, -self.cli.flat_body_thickness
            )
            bot = midR.mirror_and_join()
            bot += bot_below

        elif self.cli.body_type == LeleBodyType.HOLLOW:

            bot_below = self.flat_body_bottom(body_origin=bOrig,
                                              body_path=bPath
                                              ).mv(0, 0, joinTol)

            # Flat body
            # outer wall
            midR = self.api.spline_extrusion(
                bOrig, bPath, -self.cli.flat_body_thickness
            )
            # inner wall
            midR2 = midR.dup().mv(0,-self.cli.wall_thickness,0)
            midR -= midR2
            bot = midR.mirror_and_join()
            bot += bot_below

        else:
            assert (
                self.cli.body_type in LeleBodyType.list()
            ), f"Unsupported Body Type {self.cli.body_type}"

        return bot

    def gen_parser(self, parser=None):
        """
        pylele Command Line Interface
        """
        parser = pylele_body_parser(parser=parser)
        return super().gen_parser(parser=parser)


def main(args=None):
    """Generate body"""
    return main_maker(module_name=__name__, class_name="LeleBody", args=args)


def test_body(self, apis=None):
    """Test body"""

    ## Cadquery and blender
    tests = {
        "tail_end": ["-t", TunerType.WORM.name, "-e", "90", "-E","-refv","934731"],
        "flat": ["-bt", str(LeleBodyType.FLAT), "-fbt", "50", "-refv", "1405935"],
        "flat_worm": [
            "-bt",
            str(LeleBodyType.FLAT),
            "-t",
            TunerType.WORM.name,
            "-e",
            "90",
            "-E",
            "-refv", "794710"
        ],
        "hollow": ["-bt", str(LeleBodyType.HOLLOW),"-refv","194714"],
    }

    test_loop(module=__name__, apis=apis, tests=tests)


def test_body_mock(self):
    """Test body"""
    test_body(self, apis=["mock"])


if __name__ == "__main__":
    main()
