#!/usr/bin/env python3

"""
    Import Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_solid import Solid, test_loop, main_maker, Implementation, DEFAULT_TEST_DIR
from api.pylele_api import Shape
from api.pylele_utils import gen_stl_foo, gen_svg_foo

class Import3d(Solid):
    """ Import solid object from file """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-imp", "--import_file", help="Import file path", type=str)
        parser.add_argument("-eh", "--extrude_heigth", help="Extrude Heigth (applies to 2d filetypes) [mm]", type=float, default=None)
        return parser

    def gen(self) -> Shape:
        assert self.cli.implementation in [Implementation.SOLID2]
        return self.api.genImport(self.cli.import_file, extrude=self.cli.extrude_heigth)

def main(args=None):
    """ Generate a solid from an imported file """
    return main_maker(module_name=__name__,
                class_name='Import3d',
                args=args)

def test_import3d(self,apis=['solid2']):
    """ Test Import 3d geometry """
    test_fname=os.path.join(DEFAULT_TEST_DIR,'test')
    test_stl  = gen_stl_foo(test_fname)
    test_svg  = gen_svg_foo(test_fname)
    tests={
        'stl': ['-imp',test_stl],
        'svg': ['-imp',test_svg, '-eh', '10'],
           }
    test_loop(module=__name__,tests=tests,apis=apis)

if __name__ == '__main__':
    main()
