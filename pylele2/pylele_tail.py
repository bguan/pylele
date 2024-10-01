#!/usr/bin/env python3

"""
    Pylele Tail
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase
from pylele2.pylele_chamber import LeleChamber, pylele_chamber_parser
from pylele2.pylele_rim import LeleRim
from pylele2.pylele_spines import LeleSpines
from pylele2.pylele_tuners import LeleTuners, pylele_worm_parser
from pylele2.pylele_config import WORM, BIGWORM, LeleBodyType


class LeleTail(LeleBase):
    """Pylele Tail Generator class"""

    def gen(self) -> Shape:
        """Generate Tail"""
        assert self.cli.separate_end or self.cli.body_type == LeleBodyType.HOLLOW

        cfg = self.cfg
        joinTol = self.api.getJoinCutTol()  # cfg.joinCutTol
        cutAdj = (FIT_TOL + 2 * joinTol) if self.isCut else 0

        # this assertion should be verified
        assert (
            self.cli.end_flat_width > 4.0 + 2 * cutAdj
        ), "end_flat_width too small! %f, should be larger than %f" % (
            self.cli.end_flat_width,
            4 + 2 * cutAdj,
        )

        tailX = cfg.tailX
        chmBackX = float(self.cli.scale_length) + cfg.chmBack
        tailLen = tailX - chmBackX + 2 * cutAdj
        endWth = self.cli.end_flat_width + 2 * cutAdj
        botRat = cfg.BOT_RATIO
        if self.cli.body_type in [
            LeleBodyType.FLAT,
            LeleBodyType.HOLLOW,
            LeleBodyType.TRAVEL,
        ]:
            midBotTck = self.cli.flat_body_thickness
        else:
            midBotTck = cfg.extMidBotTck + 2 * cutAdj
        rimWth = cfg.rimWth + 2 * cutAdj
        topCut = self.api.genBox(2000, 2000, 2000).mv(0, 0, 1000)

        top = None
        if midBotTck > 0:
            extTop = self.api.genBox(
                10 if self.isCut else rimWth, endWth, midBotTck
            ).mv(tailX + (5 - rimWth if self.isCut else -rimWth / 2), 0, -midBotTck / 2)
            inrTop = self.api.genBox(2 * tailLen, endWth - 2 * rimWth, midBotTck).mv(
                tailX - rimWth - tailLen, 0, -midBotTck / 2
            )
            top = extTop.join(inrTop)

        if self.cli.body_type in [
            LeleBodyType.FLAT,
            LeleBodyType.HOLLOW,
            LeleBodyType.TRAVEL,
        ]:
            extBot = None
            inrBot = None
            if self.cli.body_type in [LeleBodyType.TRAVEL]:
                top = top.mv(5, 0, 0)  # for whatever reason...
        else:
            extBot = (
                self.api.genRodX(10 if self.isCut else rimWth, endWth / 2)
                .scale(1, 1, botRat)
                .mv(tailX + (5 - rimWth if self.isCut else -rimWth / 2), 0, -midBotTck)
            )
            inrBot = (
                self.api.genRodX(2 * tailLen, endWth / 2 - rimWth)
                .scale(1, 1, botRat)
                .mv(tailX - rimWth - tailLen, 0, -midBotTck)
            )

        if inrBot is None and extBot is None:
            bot = None
        else:
            if extBot is None:
                bot = inrBot
            else:
                bot = extBot.join(inrBot).cut(topCut)

        if top is None:
            tail = bot
        else:
            if bot is None:
                tail = top
            else:
                tail = top.join(bot)
            # tail = top

        # Tuners
        if not self.isCut:
            tuners_cut = LeleTuners(cli=self.cli, isCut=True)
            tuners_cut.gen_full()
            tail = tail.cut(tuners_cut.shape)

        # Spines
        if not self.isCut:
            spine_cut = LeleSpines(cli=self.cli, isCut=True)
            spine_cut.gen_full()
            tail = tail.cut(spine_cut.shape)

        # Chamber
        if not self.isCut and self.cli.body_type == LeleBodyType.GOURD:
            chm_cut = LeleChamber(cli=self.cli, isCut=True)
            chm_cut.gen_full()
            tail = tail.cut(chm_cut.shape)

        # Rim
        if not self.isCut and self.cli.separate_top:
            rim_cut = LeleRim(cli=self.cli, isCut=True)
            rim_cut.gen_full()
            tail = tail.cut(rim_cut.shape)

        return tail

    def gen_parser(self, parser=None):
        """Tail Parser"""
        parser = pylele_chamber_parser(parser=parser)
        return super().gen_parser(parser=pylele_worm_parser(parser=parser))


def main(args=None):
    """Generate tail"""
    return main_maker(module_name=__name__, class_name="LeleTail", args=args)


def test_tail(self, apis=None):
    """Test Tail"""

    tests = {
        "cut": ["-t", "worm", "-E", "-e", "90", "-C"],
        "separate_tail": ["-t", "worm", "-E", "-e", "90"],
        "worm": WORM,
        "bigworm": BIGWORM,
    }

    test_body = {}
    for body in [LeleBodyType.FLAT, LeleBodyType.HOLLOW, LeleBodyType.TRAVEL]:
        test_body[body] = WORM + ["-bt", body]

    test_loop(module=__name__, tests=tests | test_body, apis=apis)


def test_tail_mock(self):
    """Test Tail"""
    test_tail(self, apis=["mock"])


if __name__ == "__main__":
    main()
