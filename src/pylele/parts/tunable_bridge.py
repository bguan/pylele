#!/usr/bin/env python3

"""
    Tunable Bridge for Travelele
"""

from math import floor

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker, Implementation
from b13d.api.core import Shape

from b13d.parts.rounded_box import RoundedBox
from pylele.parts.tunable_saddle import TunableSaddle

DEFAULT_Z = 8
class TunableBridge(Solid):
    """ Generate a Tunable Bridge """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-x", "--x", help="X [mm]", type=float, default=10)
        parser.add_argument("-y", "--y", help="Y [mm]", type=float, default=55)
        parser.add_argument("-z", "--z", help="Z [mm]", type=float, default=DEFAULT_Z)
        parser.add_argument("-ns", "--nstrings", help="number of strings", type=int, default=4)
        parser.add_argument("-ss", "--string_spacing", help="strings spacing [mm]", type=float, default=10)
        parser.add_argument("-a", "--all", help="generate all together for debug", action="store_true")
        parser.add_argument("-t", "--t", help="Fit Tolerance [mm]", type=float, default=0.3)
        return parser

    def gen(self) -> Shape:
        """ generate tunable bridge  """

        if self.isCut:
            return self.api.box(self.cli.x,self.cli.y,self.cli.z)

        # base
        bridge = RoundedBox(args=['-x', f'{self.cli.x - self.cli.t}',
                                  '-y', f'{self.cli.y - self.cli.t}',
                                  '-z', f'{self.cli.z}',
                                  '-i', self.cli.implementation]
                        ).gen_full()

        if self.cli.nstrings % 2 == 0:
            starty = -(self.cli.nstrings/2 - 0.5)
        else:
            starty = -floor(self.cli.nstrings/2)

        zcomp = (self.cli.z - DEFAULT_Z)/2
        saddle = None
        for idx in range(self.cli.nstrings):
            shifty = (0,(starty+idx)*self.cli.string_spacing,zcomp)
            saddle_hole = TunableSaddle(args=['--is_cut','-i', self.cli.implementation]).gen_full()
            saddle_hole <<= shifty
            bridge -= saddle_hole

            saddle = TunableSaddle(args=['-i', self.cli.implementation,
                                         '-t', f'{self.cli.t}'])
            saddle <<= shifty
            
            if self.cli.all:
                # join everything together for debug
                bridge += saddle.gen_full()
            else:
                if not self.has_parts():
                    # add only one saddle as they are all the same
                    self.add_part(saddle)

        return bridge
        
def main(args=None):
    """ Generate the tunable bridge """
    return main_maker(module_name=__name__,
                class_name='TunableBridge',
                args=args)

def test_tunable_bridge(self,apis=None):
    """ Test Tunable Bridge"""
    tests={ 
        'default':[],
        'even'   :['-ns','5'],
        'cut'    :['-C']
        }
    test_loop(module=__name__,tests=tests,apis=apis)

def test_tunable_bridge_mock(self):
    """ Test Tunable Bridge Mock """
    test_tunable_bridge(self, apis=['mock'])

if __name__ == '__main__':
    main()
