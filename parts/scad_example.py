#!/usr/bin/env python3

"""
    Use Solidpython scad import
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_solid import LeleSolid, test_loop, main_maker, Implementation, DEFAULT_TEST_DIR
from api.pylele_api import Shape
from api.pylele_utils import gen_scad_foo
from api.sp2_api import Sp2Shape
from solid2 import import_scad
from solid2.extensions.bosl2.gears import worm_gear

class ScadExample(LeleSolid):
    """ Import solid object from file """
    def gen(self) -> Shape:
        assert self.cli.implementation in [Implementation.SOLID2]

        ## import a scad module from a custom scad file
        fname = os.path.join(DEFAULT_TEST_DIR,'box.scad')
        mod = import_scad(gen_scad_foo(fname))
        self.shape = Sp2Shape(solid=mod.box(8,8,80))
        
        ## import a scad module from bosl2 included in solidpython2
        self.shape = self.shape.join(
            Sp2Shape(
                solid=worm_gear(circ_pitch=5, teeth=36, worm_diam=30, worm_starts=1)
                )
            )
            
        return self.shape

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
