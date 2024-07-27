#!/usr/bin/env python3

"""
    Tube Solid
"""

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

    def __init__(self):
        cfg = self.parse_args()
        self.out_diameter = cfg.out_diameter
        self.in_diameter = cfg.in_diameter
        self.heigth = cfg.heigth
        super().__init__()

    def gen(self) -> Shape:
        outer = self.api.genRndRodX(self.heigth, self.out_diameter, domeRatio=self.dome_ratio)
        inner = self.api.genRndRodX(self.heigth+1, self.in_diameter, domeRatio=self.dome_ratio)
        solid = outer.cut(inner)
        self.shape = solid
        return self.shape

def tube_main():
    """ Generate a Tube """
    solid = Tube()
    solid.export_configuration()
    solid.exportSTL()
    return solid

if __name__ == '__main__':
    tube_main()
