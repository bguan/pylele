#!/usr/bin/env python3

"""
    Pylele Soundhole
"""

import os
import sys
from math import atan

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FILLET_RAD
from b13d.api.solid import main_maker, test_loop
from b13d.api.utils import degrees
from pylele.pylele2.base import LeleBase
from pylele.pylele2.config import AttrDict

def soundhole_config(scaleLen: float,
                     chmFront: float,
                     chmWth: float,
                     neckWth: float) -> AttrDict:
    """ Soundhole Configuration """
    cfg = AttrDict()

    cfg.sndholeMaxRad = chmFront/3
    cfg.sndholeMinRad = cfg.sndholeMaxRad/4
    cfg.sndholeAng = degrees(
        atan(2 * chmFront/(chmWth - neckWth))
    )

    cfg.sndholeX = scaleLen - .5*chmFront
    cfg.sndholeY = -(chmWth/2 - 2.7*cfg.sndholeMinRad) # not too close to edge

    return cfg

class LeleSoundhole(LeleBase):
    """Pylele Soundhole Generator class"""

    def configure(self):
        LeleBase.configure(self)
        self.cfg.sh_cfg = soundhole_config(
                     scaleLen = self.cli.scale_length,
                     chmFront = self.cfg.chmFront,
                     chmWth = self.cfg.chmWth,
                     neckWth = self.cfg.neckWth)

    def gen(self) -> Shape:
        """Generate Soundhole"""

        x = self.cfg.sh_cfg.sndholeX
        y = self.cfg.sh_cfg.sndholeY
        midTck = self.cfg.extMidTopTck
        minRad = self.cfg.sh_cfg.sndholeMinRad
        maxRad = self.cfg.sh_cfg.sndholeMaxRad
        ang = self.cfg.sh_cfg.sndholeAng
        bodyWth = self.cfg.bodyWth

        hole = self.api.cylinder_z(bodyWth + midTck, minRad)\
            .scale(1, maxRad/minRad, 1)\
            .rotate_z(ang).mv(x, y, -midTck)

        return hole

    def fillet(self, top:LeleBase):
        """ Fillet soundhole """

        # soundhole fillet
        sh_cfg = self.cfg.sh_cfg

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
