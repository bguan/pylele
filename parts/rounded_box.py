#!/usr/bin/env python3

"""
    Rounded Box Solid
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from solid2 import sphere
from api.pylele_solid import LeleSolid, test_loop, main_maker, Implementation
from api.pylele_api import Shape

class RoundedBox(LeleSolid):
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
        assert self.cli.implementation in [Implementation.CAD_QUERY]

        # Main cube
        box = self.api.genBox(self.cli.x,
                              self.cli.y,
                              self.cli.z)

        return box.filletByNearestEdges([], self.cli.r)

    def _coords(self):
        
        xcoords = [-self.cli.x/2+self.cli.r, self.cli.x/2-self.cli.r]
        ycoords = [-self.cli.y/2+self.cli.r, self.cli.y/2-self.cli.r]
        zcoords = [-self.cli.z/2+self.cli.r, self.cli.z/2-self.cli.r]

        return xcoords,ycoords,zcoords

    def gen_solidpython(self) -> Shape:
        """ solidpython implementation """
        assert self.cli.implementation in [Implementation.SOLID2]
        fn = self.api.fidelity.smoothingSegments()*4

        xcoords,ycoords,zcoords = self._coords()

        box = None
        # put spheres on corners
        for x in xcoords:
            for y in ycoords:
                for z in zcoords:
                    corner = sphere(self.cli.r, _fn=fn).translate(x,y,z)
                    if box is None:
                        box = corner
                    else:
                        box += corner
        
        # hull from the corners
        return self.api.genShape( box.hull() )

    def gen_default(self) -> Shape:
        """ default implementation """

        # Main cube
        box = None
        xcoords,ycoords,zcoords = self._coords()

        # lateral faces
        for x in xcoords:
            lbox = self.api.genBox(             2*self.cli.r,
                                   self.cli.y - 2*self.cli.r,
                                   self.cli.z - 2*self.cli.r)
            lbox <<= (x,0,0)
            box = lbox + box

        for y in ycoords:
            lbox = self.api.genBox(self.cli.x - 2*self.cli.r,
                                                2*self.cli.r,
                                   self.cli.z - 2*self.cli.r)
            lbox <<= (0,y,0)
            box += lbox

        for z in zcoords:
            lbox = self.api.genBox(self.cli.x - 2*self.cli.r,
                                   self.cli.y - 2*self.cli.r,
                                                2*self.cli.r)
            lbox <<= (0,0,z)
            box += lbox

        # Add edges (cylinders) to connect the fillets

        # X-direction edges + corner spheres
        for z in zcoords:
            for y in ycoords:
                edge = self.api.genRndRodX(self.cli.x, rad=self.cli.r)
                edge <<= (0, y, z)
                box += edge

        # Y-direction edges
        for x in xcoords:
            for z in zcoords:
                edge = self.api.genRodY(self.cli.y - 2*self.cli.r, rad=self.cli.r)
                edge <<= (x, 0, z)
                box += edge

        # Z-direction edges
        for x in xcoords:
            for y in ycoords:
                edge = self.api.genRodZ(self.cli.z - 2*self.cli.r, rad=self.cli.r)
                edge <<= (x, y, 0)
                box += edge
                    
        return box

    def gen(self) -> Shape:
        """ generate rounded box """
        
        if self.cli.implementation == Implementation.CAD_QUERY:
            return self.gen_cadquery()
        elif self.cli.implementation == Implementation.SOLID2:
            return self.gen_solidpython()
        else:
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
