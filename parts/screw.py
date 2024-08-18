#!/usr/bin/env python3

"""
    Screw Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_solid import LeleSolid, test_loop, main_maker
from api.pylele_api import Shape

class Screw(LeleSolid):
    """ Generate a Screw """

    head_diameter = 5
    in_diameter = 3
    heigth = 5

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-sd", "--screw_diameter", help="Screw diameter [mm]", type=float, default=3)
        parser.add_argument("-sh", "--screw_heigth", help="Screw Height [mm]", type=float, default=5)
        parser.add_argument("-hd", "--head_diameter", help="Head diameter [mm]", type=float, default=5)
        parser.add_argument("-hh", "--head_heigth", help="Head Height [mm]", type=float, default=2)
        return parser

    def gen(self) -> Shape:
        solid = self.api.genRodZ(self.cli.screw_heigth, self.cli.screw_diameter/2)
        head = self.api.genConeZ(self.cli.head_heigth,r1=self.cli.screw_diameter/2,r2=self.cli.head_diameter/2).mv(0,0,self.cli.screw_heigth/2)
        solid = solid.join(head)
        self.shape = solid
        return self.shape

def main(args=None):
    """ Generate a Screw """
    return main_maker(module_name=__name__,
                class_name='Screw',
                args=args)

def test_screw():
    """ Test Rim """

    ## Cadquery and Blender
    test_loop(module=__name__)

if __name__ == '__main__':
    main()
