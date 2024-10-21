#!/usr/bin/env python3

"""
    Pylele Nut
"""

import os
import argparse
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import LeleStrEnum, Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase
from pylele2.pylele_strings import LeleStrings


class NutType(LeleStrEnum):
    """Nut Type"""

    NUT = "nut"
    ZEROFRET = "zerofret"


def pylele_nut_parser(parser=None):
    """
    Pylele Nut Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description="Pylele Configuration")

    parser.add_argument(
        "-nt",
        "--nut_type",
        help="Nut Type",
        type=NutType,
        choices=list(NutType),
        default=NutType.NUT,
    )
    return parser


class LeleNut(LeleBase):
    """Pylele Nut Generator class"""

    def gen(self) -> Shape:
        """Generate Nut"""

        fitTol = FIT_TOL
        fbTck = self.cfg.FRETBD_TCK
        ntHt = self.cfg.NUT_HT
        ntWth = self.cfg.nutWth + fbTck / 4 + 0.5  # to be wider than fretbd
        f0X = -fitTol if self.isCut else 0

        f0Top = self.api.genRndRodY(ntWth, ntHt, 1 / 4)
        f0TopCut = self.api.genBox(2 * ntHt, 2 * ntWth, fbTck).mv(0, 0, -fbTck / 2)
        f0Top = f0Top.cut(f0TopCut).mv(f0X, 0, fbTck)
        f0Bot = self.api.genRndRodY(ntWth, ntHt, 1 / 4)
        f0BotCut = self.api.genBox(2 * ntHt, 2 * ntWth, fbTck).mv(0, 0, fbTck / 2)
        f0Bot = f0Bot.cut(f0BotCut).scale(1, 1, fbTck / ntHt).mv(f0X, 0, fbTck)
        nut = f0Top.join(f0Bot)

        # Add strings cut
        if not self.cli.nut_type == NutType.ZEROFRET and not self.isCut:
            strings = LeleStrings(isCut=True, cli=self.cli)
            nut = nut.cut(strings.gen_full())

        self.shape = nut

        return nut

    def gen_parser(self, parser=None):
        """
        pylele Command Line Interface
        """
        return super().gen_parser(parser=pylele_nut_parser(parser=parser))


def main(args=None):
    """Generate Nut"""
    return main_maker(module_name=__name__, class_name="LeleNut", args=args)


def test_nut(self, apis=None):
    """Test Nut"""

    tests = {
        "separate_fretboard": ["-F"],
        "zerofret": ["-nt", str(NutType.ZEROFRET)],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_nut_mock(self):
    """Test Nut"""
    test_nut(self, apis=["mock"])


if __name__ == "__main__":
    main()
