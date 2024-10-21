#!/usr/bin/env python3

"""
    Pylele Head
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase


class LeleHead(LeleBase):
    """Pylele Head Generator class"""

    def gen(self) -> Shape:
        """Generate Head"""

        hdWth = self.cfg.headWth
        hdLen = self.cfg.headLen
        ntHt = self.cfg.NUT_HT
        fbTck = self.cfg.FRETBD_TCK
        spHt = self.cfg.SPINE_HT
        fspTck = self.cfg.FRETBD_SPINE_TCK
        topRat = self.cfg.TOP_HEAD_RATIO
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.headOrig
        path = self.cfg.headPath
        joinTol = self.api.getJoinCutTol()

        hd = (
            self.api.genLineSplineRevolveX(orig, path, -180)
            .scale(1, 1, botRat)
            .mv(0, 0, joinTol - midTck)
        )

        if midTck > 0:
            midR = self.api.genLineSplineExtrusionZ(orig, path, midTck).mv(
                0, 0, -midTck
            )
            hd = hd.join(midR.mirrorXZ_and_join())

        if topRat > 0:
            top = (
                self.api.genLineSplineRevolveX(orig, path, 180)
                .scale(1, 1, topRat)
                .mv(0, 0, -joinTol)
            )
            hd = hd.join(top)

        topCut = self.api.genRodY(2 * hdWth, hdLen).mv(
            -ntHt, 0, 0.8 * hdLen + fbTck + ntHt
        )
        frontCut = (
            self.api.genRodY(2 * hdWth, 0.7 * spHt)
            .scale(0.5, 1, 1)
            .mv(-hdLen, 0, -fspTck - 0.65 * spHt)
        )
        hd = hd.cut(frontCut).cut(topCut)

        self.shape = hd
        return hd


def main(args=None):
    """Generate Head"""
    return main_maker(module_name=__name__, class_name="LeleHead", args=args)


def test_head(self, apis=None):
    """Test Head"""
    test_loop(module=__name__, apis=apis)


def test_head_mock(self):
    """Test Head"""
    test_head(self, apis=["mock"])


if __name__ == "__main__":
    main()
