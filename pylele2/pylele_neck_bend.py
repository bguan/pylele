#!/usr/bin/env python3

"""
    Pylele Neck Bend
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, LeleBodyType

class LeleNeckBend(LeleBase):
    """ Pylele Neck Generator class """

    def gen(self) -> Shape:
        """ Generate Neck Bend """
        assert self.cli.body_type in [ LeleBodyType.FLAT, LeleBodyType.HOLLOW]

        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth

        neck_profile = self.api.genRodZ(self.cli.flat_body_thickness,nkWth/2).mv(nkLen,0,-self.cli.flat_body_thickness/2)
        neck_cutter  = self.api.genBox(nkWth/2,nkWth,self.cli.flat_body_thickness).mv(nkLen+nkWth/4,0,-self.cli.flat_body_thickness/2)
        neck_profile = neck_profile.cut(neck_cutter)

        bot = self.api.genQuarterBall(nkWth/2, False, True)\
            .scale(1,1,self.cfg.TOP_RATIO)\
            .mv(nkLen,0,-self.cli.flat_body_thickness+self.api.getJoinCutTol())\
            
        return neck_profile.join(bot)

def main(args = None):
    """ Generate Neck """
    return main_maker(module_name=__name__,
                    class_name='LeleNeckBend',
                    args=args)

def test_neck_bend(self,apis=None):
    """ Test Neck Bend """
    tests = {
        'default': ['-bt',LeleBodyType.FLAT]
    }
    test_loop(module=__name__,apis=apis,tests=tests)

def test_neck_bend_mock(self):
    """ Test Neck """
    test_neck_bend(self,apis=['mock'])

if __name__ == '__main__':
    main()
