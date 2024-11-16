#!/usr/bin/env python3

"""
    Pylele Peg
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_api_constants import FIT_TOL
from api.pylele_solid import main_maker, test_loop
from pylele_config_common import PegConfig, TunerType
from pylele2.pylele_base import LeleBase


class LelePeg(LeleBase):
    """Pylele Peg Generator class"""

    def gen(self) -> Shape:
        """Generate Peg"""
        cutAdj = FIT_TOL if self.isCut else 0
        assert TunerType[self.cli.tuner_type].value.is_peg()
        cfg: PegConfig = TunerType[self.cli.tuner_type].value
        joinTol = 2 * self.cfg.tolerance
        strRad = self.cfg.STR_RAD + cutAdj
        holeHt = cfg.holeHt
        majRad = cfg.majRad + cutAdj
        minRad = cfg.minRad + cutAdj
        midTck = cfg.midTck
        botLen = cfg.botLen
        btnRad = cfg.btnRad + cutAdj
        topCutTck = 100 if self.isCut else 2  # big value for cutting
        botCutTck = botLen - midTck / 3 if self.isCut else 2

        top = self.api.cylinder_z(topCutTck + joinTol, majRad).mv(0, 0, topCutTck / 2)

        if not self.isCut:
            stemHt = holeHt + 4 * strRad
            stem = self.api.cylinder_z(stemHt + joinTol, minRad / 2).mv(0, 0, stemHt / 2)
            hole = self.api.cylinder_x(2 * minRad, strRad).mv(0, 0, holeHt)
            stem = stem.cut(hole)
            top = top.join(stem)

        mid = self.api.cylinder_z(midTck + joinTol, minRad).mv(0, 0, -midTck / 2)

        if self.isCut:
            btnConeTck = botLen - midTck - 2 * cutAdj
            btn = self.api.cone_z(btnConeTck + joinTol, btnRad, majRad).mv(
                0, 0, -midTck - btnConeTck
            )
            bot = self.api.cylinder_z(botCutTck + joinTol, btnRad).mv(
                0, 0, -botLen - botCutTck / 2 + 2 * cutAdj
            )
            botEnd = (
                self.api.sphere(btnRad)
                .scale(1, 1, 0.5 if self.cli.separate_end else 1)
                .mv(0, 0, -botLen - botCutTck)
            )
            bot = bot.join(botEnd)
        else:
            bot = self.api.cylinder_z(botCutTck + joinTol, majRad).mv(
                0, 0, -midTck - botCutTck / 2
            )
            stem = self.api.cylinder_z(botLen + joinTol, minRad / 2).mv(
                0, 0, -midTck - botLen / 2
            )
            bot = bot.join(stem)
            btn = self.api.box(btnRad * 2, btnRad / 2, btnRad).mv(
                0, 0, -midTck - botLen - botCutTck / 2 + btnRad / 2
            )

        peg = top.join(mid).join(btn).join(bot)

        return peg


def main(args=None):
    """Generate Peg"""
    return main_maker(module_name=__name__, class_name="LelePeg", args=args)


def test_peg(self, apis=None):
    """Test Peg"""

    tests = {
        "cut": ["-C","-refv","30799"],
        "gotoh": ["-t", "gotoh","-refv","2658"],
    }
    test_loop(module=__name__, tests=tests, apis=apis)


def test_peg_mock(self):
    """Test Peg"""
    test_peg(self, apis=["mock"])


if __name__ == "__main__":
    main()
