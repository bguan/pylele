#!/usr/bin/env python3

"""
    Pylele Soundhole
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase
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


def soundhole_main(args=None):
    """ Generate Soundhole """
    solid = LeleSoundhole(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_soundhole():
    """ Test Soundhole """

    component = 'soundhole'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        soundhole_main(args=args)


if __name__ == '__main__':
    soundhole_main()