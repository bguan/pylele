#!/usr/bin/env python3

"""
    Pylele Tail
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase
from pylele.pylele2.chamber import pylele_chamber_parser
from pylele.pylele2.tuners import pylele_worm_parser
from pylele.pylele2.config import WORM, BIGWORM, LeleBodyType


class LeleTail(LeleBase):
    """Pylele Tail Generator class"""

    def gen(self) -> Shape:
        """Generate Tail"""
        assert self.cli.separate_end or self.cli.body_type == LeleBodyType.HOLLOW

        cfg = self.cfg
        jcTol = self.api.tolerance()
        cutAdj = (FIT_TOL + 2 * jcTol) if self.isCut else 0

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
        rimWth = cfg.rimWth+ 2*cutAdj

        ## flat middle section
        if self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW, LeleBodyType.TRAVEL]:
            midBotTck = self.cli.flat_body_thickness
        else:
            midBotTck = cfg.extMidBotTck + 2*cutAdj

        if midBotTck > 0:
            extTop = self.api.box(10 if self.isCut else rimWth, endWth, midBotTck)\
                .mv(tailX + (5 - rimWth if self.isCut else -rimWth/2), 0, -midBotTck/2)
            inrTop = self.api.box(2*tailLen, endWth -2*rimWth, midBotTck)\
                .mv(tailX -rimWth -tailLen, 0, -midBotTck/2)
            tail = extTop + inrTop.mv(jcTol, 0, 0)

        if self.cli.body_type in [LeleBodyType.FLAT, LeleBodyType.HOLLOW, LeleBodyType.TRAVEL]:
            # flat bodies do not have rounded bottom
            if self.cli.body_type in [LeleBodyType.TRAVEL]:
                tail = tail.mv(5,0,0) # for whatever reason...
        else:
            # rounded bottom
            extBot = self.api.cylinder_x(10 if self.isCut else rimWth, endWth/2)\
                .scale(1, 1, botRat)\
                .mv(tailX + (5 - rimWth if self.isCut else -rimWth/2), 0, -midBotTck)
            inrBot = self.api.cylinder_x(2*tailLen, endWth/2 - rimWth)\
                .scale(1, 1, botRat)\
                .mv(tailX - rimWth -tailLen, 0, -midBotTck)
            tail += extBot + inrBot.mv(jcTol, 0, 0)
            # remove upper section of the rounde bodies
            tail -= self.api.box(2000, 2000, 2000).mv(0,0,1000)

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
        # 'worm'         : WORM    + ["-E"], # worm is already tested with body types
        'worm_cut'     : WORM    + ["-E","-C"],
        'bigworm'      : BIGWORM + ["-E"],
    }

    test_body = {}
    for body in list(LeleBodyType):
        test_body[body] = WORM + ["-E","-bt", body]

    test_loop(module=__name__, tests=tests | test_body, apis=apis)


def test_tail_mock(self):
    """Test Tail"""
    test_tail(self, apis=["mock"])


if __name__ == "__main__":
    main()
