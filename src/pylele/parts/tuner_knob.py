#!/usr/bin/env python3

"""
    Tuner Knob
"""

from math import sqrt, cos, sin, pi

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker, Implementation
from b13d.api.core import Shape
from b13d.parts.pencil import Pencil

class TunerKnob(Solid):
    """ Generate a Tunable Saddle """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-d", "--knob_diameter", help="knob diameter [mm]", type=float, default=8.5)
        parser.add_argument("-z", "--knob_height", help="knob height", type=float, default=16)
        parser.add_argument("-bc", "--bottom_cut_height", help="bottom cut height", type=float, default=2)
        parser.add_argument("-rd", "--round_hole_diameter", help="round hole diameter", type=float, default=4.5)
        parser.add_argument("-sd", "--square_hole_diam", help="squared hole size", type=float, default=3.8)
        parser.add_argument("-gd", "--grip_diameter", help="grip hole diameter", type=float, default=1.5)
        parser.add_argument("-ng", "--ngrip", help="number of grip holes", type=int, default=6)
        return parser

    def gen(self) -> Shape:
        """ generate tuner knob """
        tol = self.api.tolerance()

        # main knob
        knob = self.api.cylinder_rounded_z(l=self.cli.knob_height,
                                        rad=self.cli.knob_diameter/2,
                                        domeRatio=0.5)
        
        # knob bottom cut
        bottom_cut = self.api.box(
            self.cli.knob_diameter + 2*tol,
            self.cli.knob_diameter + 2*tol,
            self.cli.bottom_cut_height,
        )
        bottom_cut <<= (0,0,-self.cli.knob_height/2+self.cli.bottom_cut_height/2)
        knob -= bottom_cut
        
        # round hole
        round_hole = self.api.cylinder_z(
            l=self.cli.knob_height + tol,
            rad=self.cli.round_hole_diameter/2
        )
       
        # squared hole
        hole_sides = self.api.cylinder_z(
            l=self.cli.knob_height + tol,
            rad=self.cli.round_hole_diameter/2 + tol
        )
        hole_sides -= self.api.box(
            self.cli.square_hole_diam,
            self.cli.round_hole_diameter + 2*tol,
            self.cli.knob_height + 2*tol,
        )
        hole_sides = hole_sides.intersection(knob.dup())

        # grip
        r = self.cli.knob_diameter/2
        grip = None
        for i in range(self.cli.ngrip):
            grip_hole = self.api.cylinder_z(
                l=self.cli.knob_height + tol,
                rad=self.cli.grip_diameter/2
            )
            # calculate position
            phi = 2*pi*i/self.cli.ngrip
            xg = r * cos( phi )
            yg = r * sin( phi )
            grip_hole <<= (xg,yg,0)
            grip = grip_hole + grip

        return knob - round_hole + hole_sides - grip
        
def main(args=None):
    """ Generate the tunable saddle """
    return main_maker(module_name=__name__,
                class_name='TunerKnob',
                args=args)

def test_tuner_knob(self,apis=None):
    """ Test Tuner Knob """
    tests={'default':[]}
    test_loop(module=__name__,tests=tests,apis=apis)

def test_tuner_knob_mock(self):
    """ Test Tuner KNob Mock """
    test_tuner_knob(self, apis=['mock'])

if __name__ == '__main__':
    main()
