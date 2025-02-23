#!/usr/bin/env python3

"""
    Torus Solid
"""

from math import sin, cos, inf
from numpy import arange

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker, FIT_TOL
from b13d.api.core import Shape, Implementation
from b13d.api.utils import radians

class Torus(Solid):
    """ Generate a Torus """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-ar", "--angles_range", help="Angles range [deg]", type=float, default=360)
        parser.add_argument("-as", "--angles_step", help="Angles step [deg]", type=float, default=10)
        parser.add_argument("-r1", "--r1", help="R1 [mm]", type=float, default=2)
        parser.add_argument("-r2", "--r2", help="R2 [mm]", type=float, default=20)
        return parser

    def gen_sweep(self) -> Shape:
        """ generate torus using regpoly_sweep """
        
        tpath = []
        for angle in [*arange(0,                                           # start
                              self.cli.angles_range + self.cli.angles_step # stop
                              ,self.cli.angles_step                        # step
                              )
                              ]:
            tpath.append(
                (self.cli.r2*cos(radians(angle)),self.cli.r2*sin(radians(angle)),0)
                )
        return self.api.regpoly_sweep(rad=self.cli.r1,path=tpath).rotate_x(90)


    def gen_revolve(self) -> Shape:
        """ generate torus using spline_revolve """
        
        center = (-self.cli.implementation.tolerance(), self.cli.r2)

        path = [
                # center,
                (center[0],center[1]+self.cli.r1),
                [
                    (center[0]            ,center[1]+self.cli.r1,0),
                    (center[0]+self.cli.r1,center[1]            ,inf),
                    (center[0]            ,center[1]-self.cli.r1,0),
                ],
                #(center[0],center[1]-self.cli.r1),
                center,
            ]

        if self.cli.implementation == Implementation.BLENDER and self.cli.angles_range >= 360:
            deg = 359.9999
        else:
            deg = self.cli.angles_range

        donut = self.api.spline_revolve(
            start=center,
            path=path,
            deg=deg,
        )

        return donut.rotate_z(90).mirror_and_join()

    def gen(self) -> Shape:
        """ generate torus """
        if False:
            return self.gen_sweep()
        else:
            return self.gen_revolve()

        
def main(args=None):
    """ Generate a Torus """
    return main_maker(module_name=__name__,
                class_name='Torus',
                args=args)

def test_torus(self,apis=None):
    """ Test Torus """
    tests={
         "default":["-refv","1660"],
         "rev270" :["-ar", "270","-refv","1239"]
         }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_torus_mock(self):
    """ Test Torus Mock """
    ## Cadquery and Blender
    test_torus(self, apis=['mock'])

if __name__ == '__main__':
    main()
