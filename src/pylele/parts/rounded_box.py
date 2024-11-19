#!/usr/bin/env python3

"""
    Rounded Box Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from solid2 import sphere
from pylele.api.solid import Solid, test_loop, main_maker, Implementation
from pylele.api.core import Shape

class RoundedBox(Solid):
    """ Generate a Tube """

    def gen_parser(self, parser=None):
        parser = super().gen_parser(parser=parser)
        parser.add_argument("-x", "--x", help="X [mm]", type=float, default=5)
        parser.add_argument("-y", "--y", help="Y [mm]", type=float, default=6)
        parser.add_argument("-z", "--z", help="Z [mm]", type=float, default=4)
        parser.add_argument("-r", "--r", help="Rounding radius [mm]", type=float, default=1)
        return parser

    def gen_cadquery(self) -> Shape:
        """ cadquery implementation """
        # assert self.cli.implementation in [Implementation.CADQUERY]

        # Main cube
        box = self.api.box(self.cli.x,
                              self.cli.y,
                              self.cli.z)

        return box.fillet([], self.cli.r)

    def _coords(self):
        
        xcoords = [-self.cli.x/2+self.cli.r, self.cli.x/2-self.cli.r]
        ycoords = [-self.cli.y/2+self.cli.r, self.cli.y/2-self.cli.r]
        zcoords = [-self.cli.z/2+self.cli.r, self.cli.z/2-self.cli.r]

        return xcoords,ycoords,zcoords

    def gen_solidpython(self) -> Shape:
        """ solidpython implementation """

        xcoords,ycoords,zcoords = self._coords()

        box = None
        # put spheres on corners
        for x in xcoords:
            for y in ycoords:
                for z in zcoords:
                    corner = self.api.sphere(self.cli.r).mv(x,y,z)
                    if box is None:
                        box = corner
                    else:
                        box += corner
        
        # hull from the corners
        return box.hull()

    def gen_default(self) -> Shape:
        """ default implementation """

        # Main cube
        box = None
        xcoords,ycoords,zcoords = self._coords()

        # lateral faces
        for x in xcoords:
            lbox = self.api.box(             2*self.cli.r,
                                   self.cli.y - 2*self.cli.r,
                                   self.cli.z - 2*self.cli.r)
            lbox <<= (x,0,0)
            box = lbox + box

        for y in ycoords:
            lbox = self.api.box(self.cli.x - 2*self.cli.r,
                                                2*self.cli.r,
                                   self.cli.z - 2*self.cli.r)
            lbox <<= (0,y,0)
            box += lbox

        for z in zcoords:
            lbox = self.api.box(self.cli.x - 2*self.cli.r,
                                   self.cli.y - 2*self.cli.r,
                                                2*self.cli.r)
            lbox <<= (0,0,z)
            box += lbox

        # Add edges (cylinders) to connect the fillets

        # X-direction edges + corner spheres
        for z in zcoords:
            for y in ycoords:
                edge = self.api.cylinder_rounded_x(self.cli.x, rad=self.cli.r)
                edge <<= (0, y, z)
                box += edge

        # Y-direction edges
        for x in xcoords:
            for z in zcoords:
                edge = self.api.cylinder_y(self.cli.y - 2*self.cli.r, rad=self.cli.r)
                edge <<= (x, 0, z)
                box += edge

        # Z-direction edges
        for x in xcoords:
            for y in ycoords:
                edge = self.api.cylinder_z(self.cli.z - 2*self.cli.r, rad=self.cli.r)
                edge <<= (x, y, 0)
                box += edge
                    
        return box

    def gen(self) -> Shape:
        """ generate rounded box """
        
        if self.cli.implementation in [Implementation.CADQUERY, Implementation.BLENDER]:
            # apis that support fillet
            return self.gen_cadquery()
            # apis that support hull
        elif self.cli.implementation in [ Implementation.SOLID2, Implementation.TRIMESH, Implementation.MANIFOLD ]:
            return self.gen_solidpython()
        else:
            # apis not supporting fillet or hull
            return self.gen_default()
        
        assert False

def main(args=None):
    """ Generate a Rounded Box """
    return main_maker(module_name=__name__,
                class_name='RoundedBox',
                args=args)

def test_rounded_box(self,apis=None):
    """ Test Rounded Box """
    tests={'default':['-refv','105','-refvt','15']}
    test_loop(module=__name__,tests=tests,apis=apis)

def test_rounded_box_mock(self):
    """ Test Tube Mock """
    ## Cadquery and Blender
    test_rounded_box(self, apis=['mock'])

if __name__ == '__main__':
    main()
