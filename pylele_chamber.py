#!/usr/bin/env python3

"""
    Pylele Chamber
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL, Fidelity

class Lelechamber(LeleBase):
    """ Pylele Chamber Generator class """

    def gen(self) -> Shape:
        """ Generate Chamber """
        
        origFidel = self.api.fidelity
        self.api.setFidelity(Fidelity.LOW)

        scLen = self.cfg.scaleLen
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        lift = self.cfg.chmLift
        rotY = self.cfg.chmRot
        joinTol = self.cfg.joinCutTol
        rad = self.cfg.chmWth/2
        frontRat = self.cfg.chmFront/rad
        backRat = self.cfg.chmBack/rad
        topChmRat = topRat * 3/4

        topFront = self.api.genQuarterBall(rad, True, True)\
            .scale(frontRat, 1, topChmRat).mv(joinTol, 0, 0)
        topBack = self.api.genQuarterBall(rad, True, False)\
            .scale(backRat, 1, topChmRat)
        botFront = self.api.genQuarterBall(rad, False, True)\
            .scale(frontRat, 1, botRat).mv(joinTol, 0, 0)
        botBack = self.api.genQuarterBall(rad, False, False)\
            .scale(backRat, 1, botRat)
        chm = topFront.join(topBack).join(botFront).join(botBack)

        if rotY != 0:
            chm = chm.rotateY(rotY)

        if lift != 0:
            chm = chm.mv(0, 0, lift)

        chm = chm.mv(scLen, 0, 0)

        self.api.setFidelity(origFidel)

        self.shape = chm
        return chm


def chamber_main(args = None):
    """ Generate Chamber """
    solid = Lelechamber(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_chamber():
    """ Test Chamber """

    component = 'chamber'
    tests = {
        'cut'     : ['-C'],
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        chamber_main(args=args)

if __name__ == '__main__':
    chamber_main()
