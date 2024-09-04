#!/usr/bin/env python3

"""
    Pylele Chamber
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import argparse

from api.pylele_api import Shape, Fidelity
from pylele2.pylele_base import LeleBase, test_loop, main_maker, LeleBodyType


def pylele_chamber_parser(parser = None) -> argparse.ArgumentParser:
    """
    Pylele Chamber Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Chamber Configuration')

    ## Chamber config options ###########################################

    parser.add_argument("-l", "--chamber_lift", help="Chamber Lift [mm], default 1",
                        type=float, default=1)
    parser.add_argument("-r", "--chamber_rotate", help="Chamber Rotation/Pitch [deg], default -.5°",
                        type=float, default=-.5)

    return parser


class LeleChamber(LeleBase):
    """ Pylele Chamber Generator class """

    def gen_extruded_oval(self, x1, x2, y_width, z_thick):
        chm  = self.api.genRodZ(z_thick,rad=y_width/2).mv( x1,0,0)
        chm1 = self.api.genRodZ(z_thick,rad=y_width/2).mv( x2,0,0)
        chm = chm.join(chm1)
        box_len = abs(x1-x2)
        box_pos = (x1+x2)/2
        chm_box = self.api.genBox(box_len,y_width,z_thick).mv(box_pos,0,0)
        chm = chm.join(chm_box)
        return chm

    def gen(self) -> Shape:
        """ Generate Chamber """
        
        origFidel = self.api.fidelity
        self.api.setFidelity(Fidelity.LOW)

        scLen = self.cli.scale_length
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        if True:
            lift = self.cli.chamber_lift # self.cfg.chmLift
            rotY = self.cli.chamber_rotate # self.cfg.chmRot
        else:
            print('# WARNING overriding chamber values for dev!!!')
            lift = 1
            rotY = 0.5
        joinTol = self.api.getJoinCutTol()
        rad = self.cfg.chmWth/2
        frontRat = self.cfg.chmFront/rad
        backRat = self.cfg.chmBack/rad
        topChmRat = topRat * 3/4


        if self.cli.body_type == LeleBodyType.TRAVEL:
            chm_thickness = self.cli.flat_body_thickness + 100 # leave a hole
            chm_front = -self.cfg.chmFront+rad
            chm_back  =  chm_front + self.cfg.chmFront - 2*rad - self.cfg.brdgLen

            chm = self.gen_extruded_oval(chm_front,chm_back,2*rad,chm_thickness)
            chm = chm.mv(joinTol, 0, -self.cli.flat_body_thickness/2)

        else: # if self.cli.body_type == LeleBodyType.GOURD:
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
    
    def gen_parser(self, parser=None):
        parser=pylele_chamber_parser(parser=parser)
        return super().gen_parser(parser=parser)

def main(args = None):
    """ Generate Chamber """
    return main_maker(module_name=__name__,
                    class_name='LeleChamber',
                    args=args)

def test_chamber(self,apis=None):
    """ Test Chamber """

    tests = {
        'default' : [],
        'cut'     : ['-C'],
        'travel'  : ['-bt',LeleBodyType.TRAVEL]
    }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_chamber_mock(self):
    """ Test Chamber """
    test_chamber(self,apis=['mock'])

if __name__ == '__main__':
    main()
