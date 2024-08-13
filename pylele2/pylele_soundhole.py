#!/usr/bin/env python3

"""
    Pylele Soundhole
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker
class LeleSoundhole(LeleBase):
    """ Pylele Soundhole Generator class """

    def gen(self) -> Shape:
        """ Generate Soundhole """
        x = self.cfg.sndholeX
        y = self.cfg.sndholeY
        midTck = self.cfg.extMidTopTck
        minRad = self.cfg.sndholeMinRad
        maxRad = self.cfg.sndholeMaxRad
        ang = self.cfg.sndholeAng
        bodyWth = self.cfg.bodyWth

        hole = self.api.genRodZ(bodyWth + midTck, minRad)\
            .scale(1, maxRad/minRad, 1)\
            .rotateZ(ang).mv(x, y, -midTck)
        self.shape = hole
        return hole

def main(args=None):
    """ Generate Soundhole """
    return main_maker(module_name=__name__,
                    class_name='LeleSoundhole',
                    args=args)

def test_soundhole():
    """ Test Soundhole """
    test_loop(module=__name__)

if __name__ == '__main__':
    main()
