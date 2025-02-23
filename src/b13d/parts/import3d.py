#!/usr/bin/env python3

"""
    Import Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.solid import Solid, test_loop, main_maker, Implementation, DEFAULT_TEST_DIR
from b13d.api.core import Shape, supported_apis
from b13d.api.utils import gen_stl_foo, gen_svg_foo, gen_step_foo
from b13d.conversion.svg2dxf import svg2dxf_wrapper

class Import3d(Solid):
    """ Import solid object from file """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-imp", "--import_file", help="Import file path", type=str)
        parser.add_argument("-eh", "--extrude_heigth", help="Extrude Heigth (applies to 2d filetypes) [mm]", type=float, default=None)
        return parser

    def gen(self) -> Shape:
        return self.api.genImport(self.cli.import_file, extrude=self.cli.extrude_heigth)

def main(args=None):
    return main_maker(module_name=__name__,
                class_name='Import3d',
                args=args)

def test_import3d(self,apis=supported_apis()):
    
    """ Test Import 3d geometry """
    test_fname=os.path.join(DEFAULT_TEST_DIR,'test')
    test_stl  = gen_stl_foo(test_fname)
    test_svg  = gen_svg_foo(test_fname)
    test_step = gen_step_foo(test_fname)
    test_dxf  = svg2dxf_wrapper(test_svg)

    tests = {}
       
    tests[Implementation.SOLID2]={
        'sp2_stl': ['-imp',test_stl],
        'sp2_svg': ['-imp',test_svg, '-eh', '10'],
        }

    tests[Implementation.CADQUERY]={
        'cq_step': ['-imp',test_step],
        'cq_svg' : ['-imp',test_svg, '-eh', '10'],
        'cq_dxf' : ['-imp',test_dxf, '-eh', '10'],
        }
    
    tests[Implementation.TRIMESH]={
        'tm_stl' : ['-imp',test_stl],
        'tm_svg' : ['-imp',test_svg, '-eh', '10'],
        'tm_dxf' : ['-imp',test_dxf, '-eh', '10'],
        }
    
    tests[Implementation.BLENDER]={
        'bpy_stl' : ['-imp',test_stl],
        'bpy_svg' : ['-imp',test_svg, '-eh', '10'],
        }
    
    tests[Implementation.MANIFOLD]={
        'mf_svg': ['-imp',test_svg, '-eh', '10'],
        }
    
    tests[Implementation.MOCK]={
        'mock_svg': ['-imp',test_svg, '-eh', '10'],
        }

    for api in apis:
        if api in supported_apis()+[Implementation.MOCK]:
            test_loop(module=__name__,tests=tests[api],apis=[api])

def test_import3d_mock(self):
    """ Test Mock import 3d geometry """
    test_import3d(self,apis=[Implementation.MOCK])

if __name__ == '__main__':
    main()
