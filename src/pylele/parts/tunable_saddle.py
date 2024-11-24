#!/usr/bin/env python3

"""
    Tunable Bridge Saddle
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from pylele.api.solid import Solid, test_loop, main_maker, Implementation
from pylele.api.core import Shape

from pylele.parts.rounded_rectangle_extrusion import RoundedRectangle

class TunableSaddle(Solid):
    """ Generate a Tunable Saddle """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-x", "--x", help="X [mm]", type=float, default=4)
        parser.add_argument("-y", "--y", help="Y [mm]", type=float, default=6)
        parser.add_argument("-z", "--z", help="Z [mm]", type=float, default=4)
        parser.add_argument("-sh", "--saddle_height", help="saddle height [mm]", type=float, default=5)
        parser.add_argument("-r", "--r", help="String Radius [mm]", type=float, default=1)
        parser.add_argument("-fr", "--fillet_radius", help="Fillet Radius [mm]", type=float, default=0.5)
        parser.add_argument("-t", "--t", help="Fit Tolerance [mm]", type=float, default=0.3)
        return parser

    def gen(self) -> Shape:
        """ generate tunable bridge holder """
        
        cutx = 40
        vgap = 2
        hgap = 2

        # base
        if self.cli.is_cut:
            base = self.api.box(cutx,self.cli.y+self.cli.t,self.cli.z+self.cli.t)
        else:
            base = RoundedRectangle(args=[
                            '-x', f'{self.cli.x}',
                            '-y', f'{self.cli.y - self.cli.t}',
                            '-z', f'{self.cli.z}',
                            '-i', self.cli.implementation,
                            '-r', f'{self.cli.fillet_radius}',
                            '-rx']
                ).gen_full()

        # saddle vertical
        if self.cli.is_cut:
            saddle = self.api.box(cutx, 
                                  self.cli.y - hgap + self.cli.t,
                                  self.cli.saddle_height)
        else:
            saddle = self.api.box(self.cli.x,
                                  self.cli.y - hgap - self.cli.t,
                                  self.cli.saddle_height)
        saddle <<= (0,0,(self.cli.saddle_height)/2)

        # saddle horizontal
        saddleh = None
        if not self.cli.is_cut:
            saddleh = RoundedRectangle(args=[
                '-x', f'{self.cli.x}',
                '-y', f'{self.cli.y - self.cli.t}',
                '-z', f'{self.cli.saddle_height - vgap}',
                '-i', self.cli.implementation,
                '-r', f'{self.cli.fillet_radius}',
                '-rx']).gen_full()
            saddleh <<= (0,0,(self.cli.saddle_height - vgap)/2 + self.cli.z)

        # string hole
        string = self.api.cylinder_x(self.cli.x,rad=self.cli.r)
        
        ztop = 10
        stringtop = self.api.box(self.cli.x,2*self.cli.r,ztop)
        stringtop <<= (0,0,ztop/2)

        string += stringtop
        string <<= (0,0,
                    self.cli.z/2+self.cli.saddle_height - self.cli.r
                    )
        
        return base + saddle + saddleh - string
        
def main(args=None):
    """ Generate the tunable saddle """
    return main_maker(module_name=__name__,
                class_name='TunableSaddle',
                args=args)

def test_tunable_saddle(self,apis=None):
    """ Test Tunable Saddle """
    tests={'default':[]}
    test_loop(module=__name__,tests=tests,apis=apis)

def test_tunable_saddle_mock(self):
    """ Test Tunable Saddle Mock """
    test_tunable_saddle(self, apis=['mock'])

if __name__ == '__main__':
    main()
