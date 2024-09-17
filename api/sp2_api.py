#!/usr/bin/env python3

from __future__ import annotations
from typing import Union
from pathlib import Path

import copy
from math import sin, sqrt, ceil
from solid2 import cube, sphere, polygon, text, cylinder, import_, import_scad
from solid2.extensions.bosl2 import circle

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import ShapeAPI, Shape, Fidelity, Implementation
from api.pylele_api_constants import DEFAULT_TEST_DIR
from api.pylele_utils import ensureFileExtn, descreteBezierChain, superGradient, encureClosed2DPath, stl2bin
from api.scad2stl import scad2stl

FIDELITY_K = 4

class Sp2ShapeAPI(ShapeAPI):
    """
    SolidPython2 Pylele API implementation for test
    """

    def __init__(self, fidel: Fidelity):
        self.fidelity = fidel

    def getFidelity(self) -> Fidelity:
        return self.fidelity
    
    def getImplementation(self) -> Implementation:
        return Implementation.SOLID2
    
    def setFidelity(self, fidel: Fidelity) -> None:
        self.fidelity = fidel

    def exportSTL(self, shape: Sp2Shape, path: str) -> None:
        basefname, _ = os.path.splitext(path)
        scad_file = self.exportBest(shape=shape, path=basefname)
        return scad2stl(scad_file)
        
    def exportBest(self, shape: Sp2Shape, path: Union[str, Path]) -> str:
        outdir, fname = os.path.split(path)
        fname = ensureFileExtn(fname,'.scad')
        shape.solid.save_as_scad(filename=fname, outdir=outdir)
        
        fout = os.path.join(outdir,fname)
        assert os.path.isfile(fout), f'ERROR: file {fout} does not exist!'
        return fout

    def genBall(self, rad: float) -> Sp2Shape:
        return Sp2Ball(rad=rad,api=self)

    def genBox(self, l: float, wth: float, ht: float) -> Sp2Shape:
        return Sp2Box(l,wth,ht,api=self).mv(-l/2,-wth/2,-ht/2)
    
    def genConeX(self, l: float, r1: float, r2: float) -> Sp2Shape:
        return Sp2Cone(l,r1=r1,r2=r2,direction='X',api=self).mv(l/2,0,0)

    def genConeY(self, l: float, r1: float, r2: float) -> Sp2Shape:
        return Sp2Cone(l,r1=r2,r2=r1,direction='Y',api=self).mv(0,l/2,0)

    def genConeZ(self, l: float, r1: float, r2: float) -> Sp2Shape:
        return Sp2Cone(l,r1=r1,r2=r2,direction='Z',api=self).mv(0,0,l/2)

    def genPolyRodX(self, l: float, rad: float, sides: int) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, sides=sides, direction="X",api=self)

    def genPolyRodY(self, l: float, rad: float, sides: int) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, sides=sides, direction="Y",api=self)

    def genPolyRodZ(self, l: float, rad: float, sides: int) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, sides=sides, direction="Z",api=self)

    def genRodX(self, l: float, rad: float) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, direction='X',api=self)

    def genRodY(self, l: float, rad: float) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, direction='Y',api=self)

    def genRodZ(self, l: float, rad: float) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, direction='Z',api=self)

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> Sp2Shape:
        return Sp2PolyExtrusionZ(path, ht, self)

    def genLineSplineExtrusionZ(self,
            start: tuple[float, float],
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
            ht: float,
        ) -> Sp2Shape:
        if ht < 0:
            return Sp2LineSplineExtrusionZ(start, path, abs(ht), self).mv(0,0,-abs(ht))
        else:
            return Sp2LineSplineExtrusionZ(start, path, ht, self)
    
    def genLineSplineRevolveX(self,
            start: tuple[float, float],
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
            deg: float,
        ) -> Sp2Shape:
        return Sp2LineSplineRevolveX(start, path, deg, self)
    
    def genCirclePolySweep(self, rad: float, path: list[tuple[float, float, float]]) -> Sp2Shape:
        return Sp2CirclePolySweep(rad, path, self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> Sp2Shape:
        return Sp2TextZ(txt, fontSize, tck, font, self)
    
    def genImport(self, infile: str) -> Sp2Shape:
        return Sp2Import(infile,self)

    def getJoinCutTol(self):
        return Implementation.SOLID2.joinCutTol()

class Sp2Shape(Shape):
    """
    SolidPython2 Pylele Shape implementation for test
    """

    def __init__(self, api: Sp2ShapeAPI):
        self.api:Sp2ShapeAPI = api
        self.solid = None

    def getAPI(self) -> Sp2ShapeAPI:
        return self.api
    
    def getImplSolid(self):
        return self.solid

    def cut(self, cutter: Sp2Shape) -> Sp2Shape:
        self.solid = self.solid - cutter.solid
        return self

    def dup(self) -> Sp2Shape:
        return copy.copy(self)

    def filletByNearestEdges(self, 
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> Sp2Shape:
        print('Warning! Fillet not implemented yet for solidpython2 api!')
        # https://github.com/BelfrySCAD/BOSL2/wiki/rounding.scad#function-round_corners
        return self

    def join(self, joiner: Sp2Shape) -> Sp2Shape:
        self.solid = self.solid + joiner.solid
        return self
    
    def segsByDim(self, dim: float) -> int:
        return ceil((abs(dim)) * self.api.fidelity.smoothingSegments()**.25)

    # draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
    def lineSplineXY(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    ):
    
        # lastX, lastY = start
        result = [start]

        for p_or_s in path:
            if isinstance(p_or_s, tuple):
                # a point so draw line
                x, y = p_or_s
                result.append((x, y))
                lastX, lastY = x, y
            elif isinstance(p_or_s, list):
                # a list of points and gradients/tangents to trace spline thru
                spline: list[tuple[float, ...]] = p_or_s
                x1, y1 = spline[0][0:2]
                # insert first point if diff from last
                if lastX != x1 or lastY != y1:
                    dx0 = x1 - lastX
                    dy0 = y1 - lastY
                    grad0 = superGradient(dy=dy0, dx=dx0)
                    spline.insert(0, (lastX, lastY, grad0, 0, .5))
                curvePts = descreteBezierChain(spline, self.segsByDim)
                result.extend(curvePts)
                lastX, lastY = spline[-1][0:2]
                
        return encureClosed2DPath(result)

    def mirrorXZ(self) -> Sp2Shape:
        cmirror = self.solid.mirror([0,1,0])
        dup = copy.copy(self)
        dup.solid = cmirror
        return dup

    def mv(self, x: float, y: float, z: float) -> Sp2Shape:
        self.solid = self.solid.translate([x,y,z])
        return self

    def remove(self):
        pass
    
    def rotateX(self, ang: float) -> Sp2Shape:
        self.solid = self.solid.rotate([ang,0,0])
        return self

    def rotateY(self, ang: float) -> Sp2Shape:
        self.solid = self.solid.rotate([0,ang,0])
        return self

    def rotateZ(self, ang: float) -> Sp2Shape:
        self.solid = self.solid.rotate([0,0,ang])
        return self

    def scale(self, x: float, y: float, z: float) -> Sp2Shape:
        self.solid = self.solid.scale([x,y,z])
        return self

    def show(self):
        return self.solid

class Sp2Ball(Sp2Shape):
    def __init__(self, rad: float, api: Sp2ShapeAPI):
        super().__init__(api)
        self.rad = rad
        self.solid = sphere(rad, _fn=self.api.fidelity.smoothingSegments()*FIDELITY_K)

class Sp2Box(Sp2Shape):
    def __init__(self, ln: float, wth: float, ht: float, api: Sp2ShapeAPI):
        super().__init__(api)
        self.ln = ln
        self.wth = wth
        self.ht = ht
        self.solid = cube(ln, wth, ht)

class Sp2Cone(Sp2Shape):
    def __init__(self, ln: float, r1: float, r2: float = None, direction: str = 'Z', sides = None, api: Sp2ShapeAPI = Sp2ShapeAPI(fidel=Fidelity.LOW)):
        super().__init__(api)
        self.ln = ln

        if sides is None:
            self.r1 = r1
            self.r2 = r1 if r2 is None else r2
            sects = FIDELITY_K * self.segsByDim(max(self.r1, self.r2))
        else:
            self.r1 = r1*sqrt(2)
            self.r2 = self.r1 if r2 is None else r2*sqrt(2)
            sects = sides

        self.solid = cylinder(h=ln,r1=self.r1,r2=self.r2,_fn=sects).translateZ(-ln/2)
        if direction == 'X':
            self.solid = self.solid.rotateY(90)
        elif direction == 'Y':
            self.solid = self.solid.rotateX(90)

class Sp2PolyExtrusionZ(Sp2Shape):
    def __init__(self, path: list[tuple[float, float]], ht: float, api: Sp2ShapeAPI):
        super().__init__(api)
        self.path = path
        self.ht = ht
        self.solid = polygon(path).linear_extrude(ht)

# draw mix of straight lines from pt to pt, or draw spline with 
# [(x,y,grad,prev Ctl ratio, post Ctl ratio), ...], then extrude on Z-axis
class Sp2LineSplineExtrusionZ(Sp2Shape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        ht: float,
        api: Sp2ShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.ht = ht
        self.solid = polygon(self.lineSplineXY(start, path)).linear_extrude(ht)

# draw mix of straight lines from pt to pt, or draw spline with 
# [(x,y,grad, pre ctrl ratio, post ctl ratio), ...], then revolve on X-axis
class Sp2LineSplineRevolveX(Sp2Shape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        deg: float,
        api: Sp2ShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.deg = deg
        self.solid = polygon(self.lineSplineXY(start, path)).rotateZ(90).rotate_extrude(deg).rotateY(90).rotateX(-90)

class Sp2TextZ(Sp2Shape):
    def __init__(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        font: str,
        api: Sp2ShapeAPI,
    ):
        super().__init__(api)
        self.txt = txt
        self.fontSize = fontSize
        self.tck = tck
        self.font = font

        # text(t, size, font,
        # halign, valign, spacing,
        # direction, language, script)
        self.solid = text(txt,
                          fontSize/sqrt(2),
                          font=font,
                          halign='center',
                          valign='center').linear_extrude(tck)

class Sp2CirclePolySweep(Sp2Shape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
        api: Sp2ShapeAPI = Sp2ShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.rad = rad
        segs = FIDELITY_K * self.segsByDim(rad)
        self.solid = circle(r=rad, _fn=segs).path_extrude(path)

class Sp2Import(Sp2Shape):
    def __init__(
        self,
        infile: str,
        api: Sp2ShapeAPI,
    ):
        super().__init__(api)
        assert os.path.isfile(infile) or os.path.isdir(infile), f'ERROR: file/directory {infile} does not exist!'
        self.infile = infile

        _, fext = os.path.splitext(infile)

        # if os.path.isdir(infile) or fext=='.scad':
        #    self.solid = import_scad(os.path.abspath(infile))
        # else:
        # https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Importing_Geometry#import
        openscad_import_filetypes = ['.stl','.svg','.off','.amf','.3mf']
        assert fext in openscad_import_filetypes, f'ERROR: file extension {fext} not supported!'

        # make sure stl is in binary format
        if fext=='.stl':
            self.infile = stl2bin(infile)

        self.solid = import_(os.path.abspath(self.infile))

if __name__ == '__main__':
    Sp2ShapeAPI(Fidelity.LOW).test(os.path.join(DEFAULT_TEST_DIR,"sp2-all.stl"))