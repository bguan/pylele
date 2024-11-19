#!/usr/bin/env python3

"""
    Use Solidpython scad import
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from pylele.api.solid import Solid, test_loop, main_maker, Implementation, DEFAULT_TEST_DIR
from pylele.api.core import Shape
from pylele.api.utils import gen_scad_foo
from solid2 import import_scad
from solid2.extensions.bosl2.gears import worm_gear

class ScadExample(Solid):
    """ Import solid object from file """
    def gen(self) -> Shape:
        assert self.cli.implementation in [Implementation.SOLID2]

        ## import a scad module from a custom scad file
        fname = os.path.join(DEFAULT_TEST_DIR,'box.scad')
        mod = import_scad(gen_scad_foo(fname))
        shape = self.api.genShape(solid=mod.box(8,8,80))
        
        ## import a scad module from bosl2 included in solidpython2
        shape += self.api.genShape(
                solid=worm_gear(circ_pitch=5, teeth=36, worm_diam=30, worm_starts=1)
            )
            
        return shape

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='ScadExample',
                args=args)

def test_scad_example(self,apis=['solid2']):
    """ Test Import 3d geometry """
    test_loop(module=__name__,apis=apis)

if __name__ == '__main__':
    main()
