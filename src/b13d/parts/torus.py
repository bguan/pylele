#!/usr/bin/env python3

"""
    Torus Solid
"""

from math import sin, cos
from numpy import arange

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker
from b13d.api.core import Shape
from b13d.api.utils import radians

class Torus(Solid):
    """ Generate a Torus """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-ar", "--angles_range", help="Angles range [deg]", type=float, default=360)
        parser.add_argument("-as", "--angles_step", help="Angles step [deg]", type=float, default=10)
        parser.add_argument("-r1", "--r1", help="R1 [mm]", type=float, default=2.0)
        parser.add_argument("-r2", "--r2", help="R2 [mm]", type=float, default=20)
        return parser

    def gen(self) -> Shape:
        """ generate torue """
        
        tpath = []
        for angle in [*arange(0,                                           # start
                              self.cli.angles_range + self.cli.angles_step # stop
                              ,self.cli.angles_step                        # step
                              )
                              ]:
            tpath.append(
                (self.cli.r2*cos(radians(angle)),self.cli.r2*sin(radians(angle)),0)
                )
        return self.api.regpoly_sweep(rad=self.cli.r1,path=tpath)

def main(args=None):
    """ Generate a Torus """
    return main_maker(module_name=__name__,
                class_name='Torus',
                args=args)

def test_torus(self,apis=None):
    """ Test Torus """
    tests={"default":[]}
    test_loop(module=__name__,tests=tests,apis=apis)

def test_torus_mock(self):
    """ Test Torus Mock """
    ## Cadquery and Blender
    test_torus(self, apis=['mock'])

if __name__ == '__main__':
    main()
