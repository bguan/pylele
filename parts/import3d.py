#!/usr/bin/env python3

"""
    Import Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_solid import LeleSolid, test_loop, main_maker, Implementation, DEFAULT_TEST_DIR
from api.pylele_api import Shape
from api.pylele_utils import gen_stl_foo

class Import3d(LeleSolid):
    """ Import solid object from file """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-imp", "--import_file", help="Import file path", type=str)
        return parser

    def gen(self) -> Shape:
        assert self.cli.implementation in [Implementation.SOLID2]
        self.shape = self.api.genImport(self.cli.import_file)
        return self.shape

def main(args=None):
    """ Generate a Tube """
    return main_maker(module_name=__name__,
                class_name='Import3d',
                args=args)

def test_import3d(self,apis=['solid2']):
    """ Test Import 3d geometry """
    test_stl=os.path.join(DEFAULT_TEST_DIR,'test.stl')
    # test_stl='test.stl'
    gen_stl_foo(test_stl)
    tests={
        'stl': ['-imp',test_stl]
           }
    test_loop(module=__name__,tests=tests,apis=apis)

if __name__ == '__main__':
    main()
