#!/usr/bin/env python3

"""
    Pencil Solid
"""

from math import sqrt, sin, pi, degrees

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker
from b13d.api.core import Shape

class Pencil(Solid):
    """ Generate a Pencil """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-s", "--faces", help="Distance between parallel faces [mm]", type=float, default=6.85)
        parser.add_argument("-d", "--core_diameter", help="Core diameter [mm]", type=float, default=3)
        parser.add_argument("-H", "--heigth", help="Heigth [mm]", type=float, default=150)
        parser.add_argument("-fh", "--ferrule_heigth", help="Ferrule Heigth [mm]", type=float, default=5)
        parser.add_argument("-n", "--nsides", help="Number of polygon sides", type=float, default=6)
        return parser

    def gen(self) -> Shape:
        alpha_rad = pi/self.cli.nsides
        rad = self.cli.faces/2 * sqrt(1 + sin(alpha_rad)**2)
        stem = self.api.regpoly_extrusion_x(self.cli.heigth, rad=rad, sides=self.cli.nsides).rotate_x(degrees(alpha_rad))
        core = self.api.cylinder_x(self.cli.heigth, rad=self.cli.core_diameter/2)
        ferrule = self.api.cylinder_x(self.cli.ferrule_heigth, rad=rad)
        ferrule <<= ( (self.cli.heigth - self.cli.ferrule_heigth)/2,0,0)
        return stem + ferrule - core

def main(args=None):
    """ Generate a Pencil """
    return main_maker(module_name=__name__,
                class_name='Pencil',
                args=args)

def test_pencil(self,apis=None):
    """ Test Pencil """
    ## Cadquery and Blender
    tests={
        # 'volume': ['-refv','62.8']
        'default': []
           }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_pencil_mock(self):
    """ Test Pencil Mock """
    ## Cadquery and Blender
    test_pencil(self, apis=['mock'])

if __name__ == '__main__':
    main()
