#!/usr/bin/env python3

"""
    Tube Solid
"""

import os
from pylele_solid import LeleSolid
from pylele_api import Shape

class Tube(LeleSolid):
    """ Generate a Tube """

    out_diameter = 5
    in_diameter = 3
    heigth = 5
    dome_ratio = 0.01

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-out", "--out_diameter", help="Outer diameter [mm]", type=float, default=5)
        parser.add_argument("-in", "--in_diameter", help="Inner diameter [mm]", type=float, default=3)
        parser.add_argument("-H", "--heigth", help="Height [mm]", type=float, default=5)
        return parser

    def gen(self) -> Shape:
        # outer = self.api.genRndRodX(self.cli.heigth, self.cli.out_diameter, domeRatio=self.dome_ratio)
        # inner = self.api.genRndRodX(self.cli.heigth+1, self.cli.in_diameter, domeRatio=self.dome_ratio)
        outer = self.api.genRodX(self.cli.heigth, self.cli.out_diameter)
        inner = self.api.genRodX(self.cli.heigth+1, self.cli.in_diameter)
        solid = outer.cut(inner)
        self.shape = solid
        return self.shape

def tube_main(args=None):
    """ Generate a Tube """
    solid = Tube(args=args)
    solid.export_args()
    solid.exportSTL()
    return solid

def test_tube():
    """ Test Rim """

    component = 'tube'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        tube_main(args=args)


if __name__ == '__main__':
    tube_main()
