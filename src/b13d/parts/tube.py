#!/usr/bin/env python3

"""
    Tube Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker
from b13d.api.core import Shape, Direction

class Tube(Solid):
    """ Generate a Tube """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-out", "--out_diameter", help="Outer diameter [mm]", type=float, default=5)
        parser.add_argument("-in", "--in_diameter", help="Inner diameter [mm]", type=float, default=3)
        parser.add_argument("-H", "--heigth", help="Height [mm]", type=float, default=5)
        parser.add_argument("-d", "--direction", help="Direction", type=Direction, choices=Direction.list(), default=Direction.X.name)
        parser.add_argument("-rr", "--rounding_ratio", help="Rounding Ratio", type=float, default=None)
        return parser

    def gen(self) -> Shape:
        outer = self.api.cylinder(l=self.cli.heigth,
                                  rad=self.cli.out_diameter/2,
                                  direction=self.cli.direction,
                                  dome_ratio=self.cli.rounding_ratio)
        inner = self.api.cylinder(l=self.cli.heigth+1,
                                  rad=self.cli.in_diameter/2,
                                  direction=self.cli.direction,
                                  dome_ratio=self.cli.rounding_ratio)
        return outer - inner

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='Tube',
                args=args)

def test_tube(self,apis=None):
    """ Test Tube """
    ## Cadquery and Blender
    tests={
        'volume': ['-refv','62.8']
           }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_tube_mock(self):
    """ Test Tube Mock """
    ## Cadquery and Blender
    test_tube(self, apis=['mock'])

if __name__ == '__main__':
    main()
