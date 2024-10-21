#!/usr/bin/env python3

"""
    Pylele Body
"""

import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_solid import main_maker, test_loop
from pylele_config_common import TunerType
from pylele2.pylele_config import LeleBodyType
from pylele2.pylele_base import LeleBase
from pylele2.pylele_chamber import LeleChamber


def pylele_body_parser(parser=None):
    """
    Pylele Body Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Configuration")

    return parser


class LeleBody(LeleBase):
    """Pylele Body Generator class"""

    def flat_body_bottom(self):
        """generate the bottom of a flat body"""
        bot_below = (
            self.api.genLineSplineRevolveX(self.cfg.bodyOrig, self.cfg.bodyPath, -180)
            .scale(1, 1, self.cfg.TOP_RATIO)
            .mv(0, 0, -self.cli.flat_body_thickness)
        )
        return bot_below

    def gen(self) -> Shape:
        """Generate Body"""
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath
        joinTol = self.api.getJoinCutTol()

        if self.cli.body_type == LeleBodyType.GOURD:
            # Gourd body
            bot = self.api.genLineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, botRat)

            if midTck > 0:
                # Generates flat middle section of body
                bot = bot.mv(0, 0, -midTck)
                midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, -midTck)
                bot = bot.join(midR.mirrorXZ_and_join())

        elif self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.TRAVEL]:

            bot_below = self.flat_body_bottom().mv(0, 0, joinTol)

            # Flat body
            midR = self.api.genLineSplineExtrusionZ(
                bOrig, bPath, -self.cli.flat_body_thickness
            )
            bot = midR.mirrorXZ_and_join()
            bot = bot.join(bot_below)

            if self.cli.body_type in [LeleBodyType.TRAVEL]:
                # just for development
                chamber = LeleChamber(cli=self.cli, isCut=True)
                chamber.gen_full()
                bot = bot.cut(chamber.shape)

        elif self.cli.body_type == LeleBodyType.HOLLOW:

            bot_below = self.flat_body_bottom().mv(0, 0, joinTol)

            # Flat body
            # outer wall
            midR = self.api.genLineSplineExtrusionZ(
                bOrig, bPath, -self.cli.flat_body_thickness
            )
            # inner wall
            midR2 = midR.dup().mv(0, -self.cli.wall_thickness, 0)
            midR = midR.cut(midR2)
            bot = midR.mirrorXZ_and_join()
            bot = bot.join(bot_below)

        else:
            assert (
                self.cli.body_type in LeleBodyType.list()
            ), f"Unsupported Body Type {self.cli.body_type}"

        self.shape = bot
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
        "tail_end": ["-t", TunerType.WORM.name, "-e", "90", "-E"],
        "flat": ["-bt", str(LeleBodyType.FLAT), "-fbt", "50", "-refv", "1405935"],
        "flat_worm": [
            "-bt",
            str(LeleBodyType.FLAT),
            "-t",
            TunerType.WORM.name,
            "-e",
            "90",
            "-E",
        ],
        "hollow": ["-bt", str(LeleBodyType.HOLLOW)],
    }

    test_loop(module=__name__, apis=apis, tests=tests)


def test_body_mock(self):
    """Test body"""
    test_body(self, apis=["mock"])


if __name__ == "__main__":
    main()
