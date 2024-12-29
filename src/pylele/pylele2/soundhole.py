#!/usr/bin/env python3

"""
    Pylele Soundhole
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FILLET_RAD
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase


class LeleSoundhole(LeleBase):
    """Pylele Soundhole Generator class"""

    def soundhole_config(self):
        """ soundhoole configuration """
        return self.cfg.soundhole_config(scaleLen=self.cli.scale_length)

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

        hole = self.api.cylinder_z(bodyWth + midTck, minRad)\
            .scale(1, maxRad/minRad, 1)\
            .rotate_z(ang).mv(x, y, -midTck)

        return hole

    def fillet(self, top:LeleBase):
        """ Fillet soundhole """

        # soundhole fillet
        sh_cfg = self.soundhole_config()

        top = top.fillet(
            nearestPts=[(sh_cfg.sndholeX, sh_cfg.sndholeY, self.cfg.fretbdHt)],
            rad = FILLET_RAD
        )

        return top


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
