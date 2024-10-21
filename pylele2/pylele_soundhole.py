#!/usr/bin/env python3

"""
    Pylele Soundhole
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape
from api.pylele_solid import main_maker, test_loop
from pylele2.pylele_base import LeleBase


class LeleSoundhole(LeleBase):
    """Pylele Soundhole Generator class"""

    def gen(self) -> Shape:
        """Generate Soundhole"""
        sh_cfg = self.cfg.soundhole_config(scaleLen=self.cli.scale_length)

        x = sh_cfg.sndholeX
        y = sh_cfg.sndholeY
        midTck = self.cfg.extMidTopTck
        minRad = sh_cfg.sndholeMinRad
        maxRad = sh_cfg.sndholeMaxRad
        ang = sh_cfg.sndholeAng
        bodyWth = self.cfg.bodyWth

        hole = (
            self.api.genRodZ(bodyWth + midTck, minRad)
            .scale(1, maxRad / minRad, 1)
            .rotateZ(ang)
            .mv(x, y, -midTck)
        )
        self.shape = hole
        return hole


def main(args=None):
    """Generate Soundhole"""
    return main_maker(module_name=__name__, class_name="LeleSoundhole", args=args)


def test_soundhole(self, apis=None):
    """Test Soundhole"""
    test_loop(module=__name__, apis=apis)


def test_soundhole_mock(self):
    """Test Soundhole"""
    test_soundhole(self, apis=["mock"])


if __name__ == "__main__":
    main()
