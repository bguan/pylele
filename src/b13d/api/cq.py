#!/usr/bin/env python3

from __future__ import annotations
import cadquery as cq
import copy
import math
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import ShapeAPI, Shape, test_api
from b13d.api.utils import file_ensure_extension, lineSplineXY
from b13d.conversion.svg2dxf import svg2dxf_wrapper


"""
    Encapsulate CAD Query implementation specific calls
"""

CQ_EXPORTERS = {
    ".stl": cq.exporters.ExportTypes.STL,
    ".step": cq.exporters.ExportTypes.STEP,
    ".svg": cq.exporters.ExportTypes.SVG,
    ".dxf": cq.exporters.ExportTypes.DXF,
    ".tjs": cq.exporters.ExportTypes.TJS,
    ".vrml": cq.exporters.ExportTypes.VRML,
}

class CQShapeAPI(ShapeAPI):

    def export(self, shape: CQShape, path: Union[str, Path], fmt=".stl") -> None:
        cq.exporters.export(
            shape.solid,
            file_ensure_extension(path, fmt),
            CQ_EXPORTERS[fmt],
            tolerance=self.fidelity.tolerance(),
            opt={
                "showAxes": False,
                "projectionDir": (0, 0, 1),
                #"strokeWidth": 0.25,
                #"strokeColor": (255, 0, 0),
                #"hiddenColor": (0, 0, 255),
                "showHidden": False,
                "showOrigin": False,
                },
        )

    def export_best(self, shape: CQShape, path: Union[str, Path]) -> None:
        self.export(shape=shape,path=path,fmt=".step")

    def export_stl(self, shape: CQShape, path: Union[str, Path]) -> None:
        self.export(shape=shape,path=path,fmt=".stl")

    def export_best_multishapes(
        self,
        shapes: list[Shape],
        assembly_name: str,
        path: Union[str, Path],
    ) -> None:
        # Create an assembly
        assembly = cq.Assembly(name=assembly_name)

        # Add shapes to the assembly with assigned colors
        for i, s in enumerate(shapes):
            assembly.add(
                s.solid,
                name=f"Part {i+1} of {len(shapes)}: {s.name}",
                color=cq.Color(s.color[0]/255., s.color[1]/255., s.color[2]/255.),
            )

        # Export the assembly to a STEP file
        assembly.save(file_ensure_extension(path, ".step"))

    def sphere(self, rad: float) -> CQShape:
        return CQBall(rad, self)

    def box(self, ln: float, wth: float, ht: float, center: bool = True) -> CQShape:
        retval = CQBox(ln, wth, ht, self)
        if center:
            return retval
        return retval.mv(ln/2,wth/2,ht/2)

    def cone_x(self, h: float, r1: float, r2: float) -> CQShape:
        return CQCone(h, r1, r2, (1, 0, 0), self)

    def cone_y(self, h: float, r1: float, r2: float) -> CQShape:
        return CQCone(h, r1, r2, (0, 1, 0), self)

    def cone_z(self, h: float, r1: float, r2: float) -> CQShape:
        return CQCone(h, r1, r2, (0, 0, 1), self)

    def regpoly_extrusion_x(self, ln: float, rad: float, sides: int) -> CQShape:
        return CQPolyRod(ln, rad, sides, "YZ", self)

    def regpoly_extrusion_y(self, ln: float, rad: float, sides: int) -> CQShape:
        return CQPolyRod(ln, rad, sides, "XZ", self)

    def regpoly_extrusion_z(self, ln: float, rad: float, sides: int) -> CQShape:
        return CQPolyRod(ln, rad, sides, "XY", self)

    def cylinder_x(self, l: float, rad: float) -> CQShape:
        return CQRod(l, rad, "YZ", self)

    def cylinder_y(self, l: float, rad: float) -> CQShape:
        return CQRod(l, rad, "XZ", self)

    def cylinder_z(self, l: float, rad: float) -> CQShape:
        return CQRod(l, rad, "XY", self)

    def polygon_extrusion(self, path: list[tuple[float, float]], ht: float) -> CQShape:
        return CQPolyExtrusionZ(path, ht, self)

    def spline_extrusion(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        ht: float,
    ) -> CQShape:
        return CQLineSplineExtrusionZ(start, path, ht, self)

    def spline_revolve(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        deg: float,
    ) -> CQShape:
        return CQLineSplineRevolveX(start, path, deg, self)

    def regpoly_sweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> CQShape:
        return CQCirclePolySweep(rad, path, self)

    def text(self, txt: str, fontSize: float, tck: float, font: str) -> CQShape:
        return CQTextZ(txt, fontSize, tck, font, self)

    def genImport(self, infile: str, extrude: float = None) -> CQShape:
        return CQImport(infile, extrude=extrude)

class CQShape(Shape):

    def __init__(self, api: CQShapeAPI):
        super().__init__(api)
        self.solid: cq.Workplane = None

    def cut(self, cutter: CQShape) -> CQShape:
        self.solid = self.solid.cut(cutter.solid)
        return self

    def dup(self) -> CQShape:
        duplicate = copy.copy(self)
        duplicate.solid = self.solid.val().copy()
        return duplicate

    def fillet(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> CQShape:
        if nearestPts != None and len(nearestPts) > 0:
            for p in nearestPts:
                self.solid = self.solid.edges(
                    cq.selectors.NearestToPointSelector(p),
                ).fillet(rad)
        else:
            self.solid = self.solid.edges().fillet(rad)

        return self

    def join(self, joiner: CQShape) -> CQShape:
        self.solid = self.solid.union(joiner.solid)
        return self

    def intersection(self, intersector: CQShape) -> CQShape:
        self.solid = self.solid.intersect(intersector.solid)
        return self

    def _smoothing_segments(self, dim: float) -> int:
        # Since CadQuery isusing Spline to connect pts for curves so use less segments
        return math.ceil(abs(dim) ** 0.25 * self.api.fidelity.smoothing_segments())

    def mirror(self) -> CQShape:
        mirror = self.solid.mirror("XZ")
        dup = copy.copy(self)
        dup.solid = mirror
        return dup

    def mv(self, x: float, y: float, z: float) -> CQShape:
        if x == 0 and y == 0 and z == 0:
            return self
        self.solid = self.solid.translate((x, y, z))
        return self

    def rotate_x(self, ang: float) -> CQShape:
        if ang == 0:
            return self
        self.solid = self.solid.rotate((-1, 0, 0), (1, 0, 0), ang)
        return self

    def rotate_y(self, ang: float) -> CQShape:
        if ang == 0:
            return self
        self.solid = self.solid.rotate((0, -1, 0), (0, 1, 0), ang)
        return self

    def rotate_z(self, ang: float) -> CQShape:
        if ang == 0:
            return self
        self.solid = self.solid.rotate((0, 0, -1), (0, 0, 1), ang)
        return self

    def scale(self, x: float, y: float, z: float) -> CQShape:
        if x == 1 and y == 1 and z == 1:
            return self

        t = cq.Matrix(
            [
                [x, 0, 0, 0],
                [0, y, 0, 0],
                [0, 0, z, 0],
                [0, 0, 0, 1],
            ]
        )
        self.solid = self.solid.newObject(
            [
                o.transformGeometry(t) if isinstance(o, cq.Shape) else o
                for o in self.solid.objects
            ]
        )
        return self


class CQBall(CQShape):
    def __init__(self, rad: float, api: CQShapeAPI):
        super().__init__(api)
        self.rad = rad
        self.solid = cq.Workplane("XY").sphere(rad)


class CQCone(CQShape):
    def __init__(
        self,
        ln: float,
        r1: float,
        r2: float,
        dir: tuple[float, float, float],
        api: CQShapeAPI,
    ):
        super().__init__(api)
        self.ln = ln
        self.r1 = r1
        self.r2 = r2
        self.solid = cq.Workplane("YZ").add(cq.Solid.makeCone(r1, r2, ln, dir=dir))


class CQPolyRod(CQShape):
    def __init__(self, ln: float, rad: float, sides: int, plane: str, api: CQShapeAPI):
        super().__init__(api)
        self.ln = ln
        self.rad = rad
        sideLen = 4 * math.sin(math.pi / sides) * rad
        polygon = cq.Workplane(plane).polygon(sides, sideLen)
        self.solid = polygon.extrude(ln).translate(
            (
                -ln / 2 if plane == "YZ" else 0,
                ln / 2 if plane == "XZ" else 0,
                -ln / 2 if plane == "XY" else 0,
            )
        )


class CQRod(CQShape):
    def __init__(self, ln: float, rad: float, plane: str, api: CQShapeAPI):
        super().__init__(api)
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane(plane).cylinder(ln, rad)


class CQBox(CQShape):
    def __init__(self, ln: float, wth: float, ht: float, api: CQShapeAPI):
        super().__init__(api)
        self.ln = ln
        self.wth = wth
        self.ht = ht
        self.solid = cq.Workplane("XY").box(ln, wth, ht)


# draw straight lines from pt to pt then extrude
class CQPolyExtrusionZ(CQShape):
    def __init__(self, path: list[tuple[float, float]], ht: float, api: CQShapeAPI):
        super().__init__(api)
        self.path = path
        self.ht = ht
        self.solid = cq.Workplane("XY").sketch().polygon(path).finalize().extrude(ht)


# draw mix of straight lines from pt to pt, or draw spline with
# [(x,y,grad,prev Ctl ratio, post Ctl ratio), ...], then extrude on Z-axis
class CQLineSplineExtrusionZ(CQShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        ht: float,
        api: CQShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.ht = ht
        self.solid = lineSplineXY(
            start,
            path,
            self._smoothing_segments,
            lambda pt: cq.Workplane("XY").moveTo(pt[0], pt[1]),
            lambda trace, pt: trace.lineTo(pt[0], pt[1]),
            lambda trace, pts: trace.spline(pts),
            lambda trace: trace.close(),
        ).extrude(ht)


# draw mix of straight lines from pt to pt, or draw spline with
# [(x,y,grad, pre ctrl ratio, post ctl ratio), ...], then revolve on X-axis
class CQLineSplineRevolveX(CQShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        deg: float,
        api: CQShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.deg = deg if deg > 0 else -deg
        self.solid = lineSplineXY(
            start,
            path,
            self._smoothing_segments,
            lambda pt: cq.Workplane("XY").moveTo(pt[0], pt[1]),
            lambda trace, pt: trace.lineTo(pt[0], pt[1]),
            lambda trace, pts: trace.spline(pts),
            lambda trace: trace.close(),
        ).revolve(self.deg, (0, 0, 0), (1 if deg > 0 else -1, 0, 0))


# sweep circle along polyline path
class CQCirclePolySweep(CQShape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
        api: CQShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.rad = rad
        path0 = [
            (p[0] - path[0][0], p[1] - path[0][1], p[2] - path[0][2]) for p in path
        ]
        sweepPath = cq.Wire.makePolygon(path0)
        self.solid = (
            cq.Workplane("YZ")
            .circle(rad)
            .sweep(sweepPath, transition="round", sweepAlongWires=True)
        )
        self.solid = self.solid.translate(path[0])


# Text
class CQTextZ(CQShape):
    def __init__(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        font: str,
        api: CQShapeAPI,
    ):
        super().__init__(api)
        self.txt = txt
        self.fontSize = fontSize
        self.tck = tck
        self.font = font
        self.solid = cq.Workplane("XY").text(txt, fontSize, tck, font=font)

class CQImport(CQShape):
    def __init__(
        self,
        infile: str,
        extrude: float = None,
        api: CQShapeAPI = CQShapeAPI,
    ):
        super().__init__(api)
        assert os.path.isfile(infile) or os.path.isdir(
            infile
        ), f"ERROR: file/directory {infile} does not exist!"
        self.infile = infile

        _, fext = os.path.splitext(infile)

        cadquery_import_filetypes = [".step", ".svg", ".dxf"]
        assert (
            fext in cadquery_import_filetypes
        ), f"ERROR: file extension {fext} not supported!"

        if fext == ".svg":
            outfile = svg2dxf_wrapper(infile)
            self.solid = cq.importers.importDXF(outfile).wires().toPending().extrude(extrude)
        elif fext == ".dxf" or fext == ".svg":
            self.solid = cq.importers.importDXF(infile).wires().toPending().extrude(extrude)
        elif fext == ".step":
            self.solid = cq.importers.importStep(infile).toPending()


if __name__ == "__main__":
    test_api("cadquery")
