#!/usr/bin/env python3

from __future__ import annotations
import copy
from math import pi, sqrt, ceil
import os
from pathlib import Path
import sys
from typing import Union

try:
    from solid2 import cube, sphere, polygon, text, cylinder, import_
    from solid2.extensions.bosl2 import circle
except:
    # only a subset allowed when using implicitcad
    from solid2 import cube, sphere, polygon, cylinder

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import ShapeAPI, Shape, Fidelity, Implementation
from api.pylele_api_constants import DEFAULT_TEST_DIR
from api.pylele_utils import dimXY, ensureFileExtn, lineSplineXY
from conversion.stlascii2stlbin import stlascii2stlbin
from conversion.scad2stl import scad2stl, OPENSCAD


class Sp2ShapeAPI(ShapeAPI):
    """
    SolidPython2 Pylele API implementation for test
    """

    command = OPENSCAD
    implicit = False

    def exportSTL(self, shape: Sp2Shape, path: str) -> None:
        basefname, _ = os.path.splitext(path)
        scad_file = self.exportBest(shape=shape, path=basefname)
        return scad2stl(scad_file, command=self.command, implicit=self.implicit)

    def exportBest(self, shape: Sp2Shape, path: Union[str, Path]) -> str:
        outdir, fname = os.path.split(path)
        fname = ensureFileExtn(fname, ".scad")
        shape.solid.save_as_scad(filename=fname, outdir=outdir)

        fout = os.path.join(outdir, fname)
        assert os.path.isfile(fout), f"ERROR: file {fout} does not exist!"
        return fout

    def genBall(self, rad: float) -> Sp2Shape:
        return Sp2Ball(rad, self)

    def genBox(self, l: float, wth: float, ht: float) -> Sp2Shape:
        return Sp2Box(l, wth, ht, self).mv(-l / 2, -wth / 2, -ht / 2)

    def genConeX(self, l: float, r1: float, r2: float) -> Sp2Shape:
        return Sp2Cone(l, r1, r2, direction="X", sides=None, api=self).mv(l / 2, 0, 0)

    def genConeY(self, l: float, r1: float, r2: float) -> Sp2Shape:
        return Sp2Cone(l, r1, r2, direction="Y", sides=None, api=self).mv(0, l / 2, 0)

    def genConeZ(self, l: float, r1: float, r2: float) -> Sp2Shape:
        return Sp2Cone(l, r1, r2, direction="Z", sides=None, api=self).mv(0, 0, l / 2)

    def genPolyRodX(self, l: float, rad: float, sides: int) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, r2=rad, sides=sides, direction="X", api=self)

    def genPolyRodY(self, l: float, rad: float, sides: int) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, r2=rad, sides=sides, direction="Y", api=self)

    def genPolyRodZ(self, l: float, rad: float, sides: int) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, r2=rad, sides=sides, direction="Z", api=self)

    def genRodX(self, l: float, rad: float) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, r2=rad, direction="X", sides=None, api=self)

    def genRodY(self, l: float, rad: float) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, r2=rad, direction="Y", sides=None, api=self)

    def genRodZ(self, l: float, rad: float) -> Sp2Shape:
        return Sp2Cone(l, r1=rad, r2=rad, direction="Z", sides=None, api=self)
    
    def genRndRodZ(self, l: float, rad: float, domeRatio: float = 1) -> Shape:
        stem_len = l - 2*rad*domeRatio
        rod = None
        for bz in [stem_len/2, -stem_len/2]:
            ball = sphere(rad,_fn=self.fidelity.smoothingSegments())\
                .scale([1, 1, domeRatio]).translate([0, 0, bz])
            if rod is None:
                rod = ball
            else:
                rod += ball
        return self.genShape(rod.hull())

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> Sp2Shape:
        return Sp2PolyExtrusionZ(path, ht, api=self)

    def genLineSplineExtrusionZ(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        ht: float,
    ) -> Sp2Shape:
        if ht < 0:
            return Sp2LineSplineExtrusionZ(start, path, abs(ht), api=self).mv(
                0, 0, -abs(ht)
            )
        else:
            return Sp2LineSplineExtrusionZ(start, path, ht, api=self)

    def genLineSplineRevolveX(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        deg: float,
    ) -> Sp2Shape:
        return Sp2LineSplineRevolveX(start, path, deg, api=self)

    def genCirclePolySweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> Sp2Shape:
        return Sp2CirclePolySweep(rad, path, api=self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> Sp2Shape:
        return Sp2TextZ(txt, fontSize, tck, font, api=self)

    def genImport(self, infile: str, extrude: float = None) -> Sp2Shape:
        return Sp2Import(infile, extrude=extrude)

    def genShape(self, solid=None) -> Sp2Shape:
        return Sp2Shape(solid=solid, api=self)

    def setCommand(self, command=OPENSCAD) -> None:
        self.command = command

    def setImplicit(self, implicit=False) -> None:
        self.implicit = implicit


class Sp2Shape(Shape):
    """
    SolidPython2 Pylele Shape implementation for test
    """

    def cut(self, cutter: Sp2Shape) -> Sp2Shape:
        self.solid = self.solid - cutter.solid
        return self

    def dup(self) -> Sp2Shape:
        return copy.copy(self)

    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> Sp2Shape:
        print("Warning! Fillet not implemented yet for solidpython2 api!")
        # https://github.com/BelfrySCAD/BOSL2/wiki/rounding.scad#function-round_corners
        return self

    def join(self, joiner: Sp2Shape) -> Sp2Shape:
        self.solid = self.solid + joiner.solid
        return self

    def segsByDim(self, dim: float) -> int:
        return ceil(abs(dim) ** 0.5 * self.api.fidelity.smoothingSegments())

    def mirrorXZ(self) -> Sp2Shape:
        cmirror = self.solid.mirror([0, 1, 0])
        dup = copy.copy(self)
        dup.solid = cmirror
        return dup

    def mv(self, x: float, y: float, z: float) -> Sp2Shape:
        self.solid = self.solid.translate([x, y, z])
        return self

    def remove(self):
        pass

    def rotateX(self, ang: float) -> Sp2Shape:
        self.solid = self.solid.rotate([ang, 0, 0])
        return self

    def rotateY(self, ang: float) -> Sp2Shape:
        self.solid = self.solid.rotate([0, ang, 0])
        return self

    def rotateZ(self, ang: float) -> Sp2Shape:
        self.solid = self.solid.rotate([0, 0, ang])
        return self

    def scale(self, x: float, y: float, z: float) -> Sp2Shape:
        self.solid = self.solid.scale([x, y, z])
        return self

    def show(self):
        return self.solid


class Sp2Ball(Sp2Shape):
    def __init__(self, rad: float, api: Sp2ShapeAPI):
        super().__init__(api)
        self.rad = rad
        self.solid = sphere(rad, _fn=self.segsByDim(2 * pi * rad))


class Sp2Box(Sp2Shape):
    def __init__(self, ln: float, wth: float, ht: float, api: Sp2ShapeAPI):
        super().__init__(api)
        self.ln = ln
        self.wth = wth
        self.ht = ht
        self.solid = cube(ln, wth, ht)


class Sp2Cone(Sp2Shape):
    def __init__(
        self, ln: float, r1: float, r2: float, direction: str, sides, api: Sp2ShapeAPI
    ):
        super().__init__(api)
        self.ln = ln

        if sides is None:
            self.r1 = r1
            self.r2 = r1 if r2 is None else r2
            sects = self.segsByDim(2 * pi * max(self.r1, self.r2))
        else:
            self.r1 = r1 * sqrt(2)
            self.r2 = self.r1 if r2 is None else r2 * sqrt(2)
            sects = sides

        self.solid = cylinder(h=ln, r1=self.r1, r2=self.r2, _fn=sects).translateZ(
            -ln / 2
        )
        if direction == "X":
            self.solid = self.solid.rotateY(90)
        elif direction == "Y":
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
        self.solid = polygon(lineSplineXY(start, path, self.segsByDim)).linear_extrude(
            ht
        )


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
        _, dimY = dimXY(start, path)
        segs = ceil(self.segsByDim(2 * pi * dimY) * abs(deg) / 360)
        self.solid = (
            polygon(lineSplineXY(start, path, self.segsByDim))
            .rotateZ(90)
            .rotate_extrude(deg, _fn=segs)
            .rotateY(90)
            .rotateX(-90)
        )


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

        self.solid = text(
            txt, fontSize / sqrt(2), font=font, halign="center", valign="center"
        ).linear_extrude(tck)


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
        segs = self.segsByDim(2 * pi * rad)
        self.solid = circle(r=rad, _fn=segs).path_extrude(path)


class Sp2Import(Sp2Shape):
    def __init__(
        self,
        infile: str,
        extrude: float = None,
        api: Sp2ShapeAPI = Sp2ShapeAPI,
    ):
        super().__init__(api)
        assert os.path.isfile(infile) or os.path.isdir(
            infile
        ), f"ERROR: file/directory {infile} does not exist!"
        self.infile = infile

        _, fext = os.path.splitext(infile)

        # https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Importing_Geometry#import
        openscad_import_filetypes = [".stl", ".svg", ".off", ".amf", ".3mf"]
        assert (
            fext in openscad_import_filetypes
        ), f"ERROR: file extension {fext} not supported!"

        # make sure stl is in binary format
        if fext == ".stl":
            self.infile = stlascii2stlbin(infile)

        self.solid = import_(os.path.abspath(self.infile))
        if isinstance(extrude, float):
            self.solid = self.solid.linear_extrude(extrude)


if __name__ == "__main__":
    Sp2ShapeAPI(Fidelity.LOW).test(Path.cwd() / DEFAULT_TEST_DIR / "sp2_api")
