#!/usr/bin/env python3

from __future__ import annotations
import cadquery as cq
import copy
import math
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import ShapeAPI, Shape, Fidelity, Implementation
from api.pylele_utils import ensureFileExtn, lineSplineXY
from api.pylele_api_constants import DEFAULT_TEST_DIR

"""
def lineSplineXY_cq0(
    start: tuple[float, float],
    lineSpline: list[tuple[float, float] | list[tuple[float, ...]]],
    segsByDim: int
) -> cq.Workplane:
    
    lastX, lastY = start
    trace = cq.Workplane("XY").moveTo(lastX, lastY)
                    
    pts = lineSplineXY(start, lineSpline, segsByDim)

    for ptx, pty in pts:
        if ptx!=lastX or pty!=lastY:
            trace = trace.lineTo(ptx, pty)
            lastX, lastY = ptx, pty

    trace = trace.close()
    return trace
"""

# draw mix of straight lines from pt to pt, and draw spline when given 
# list of (x,y,grad, pre ctrlLenRatio, post ctrlLenRatio)
def lineSplineXY_cq(
    start: tuple[float, float],
    lineSpline: list[tuple[float, float] | list[tuple[float, ...]]],
    segsByDim: int
) -> cq.Workplane:
    
    lastX, lastY = start
    trace = cq.Workplane("XY").moveTo(lastX, lastY)
    
    for p_or_s in lineSpline:
        if isinstance(p_or_s, tuple):
            # a point so draw line
            lastX, lastY = p_or_s
            trace = trace.lineTo(lastX, lastY)
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
            curvePts = descreteBezierChain(spline, segsByDim)
            trace = trace.spline(curvePts)
            lastX, lastY = spline[-1][0:2]

    trace = trace.close()
    return trace

"""
    Encapsulate CAD Query implementation specific calls
"""


class CQShapeAPI(ShapeAPI):
    def __init__(self, fidel: Fidelity):
        super().__init__()
        self.fidelity = fidel

    def exportSTL(self, shape: CQShape, path: Union[str, Path]) -> None:
        cq.exporters.export(
            shape.solid,
            ensureFileExtn(path, ".stl"),
            cq.exporters.ExportTypes.STL,
            tolerance=self.fidelity.exportTol(),
        )

    def exportBest(self, shape: CQShape, path: Union[str, Path]) -> None:
        cq.exporters.export(
            shape.solid,
            ensureFileExtn(path, ".step"),
            cq.exporters.ExportTypes.STEP,
            tolerance=self.fidelity.exportTol(),
        )

    def genBall(self, rad: float) -> CQShape:
        return CQBall(rad, self)

    def genBox(self, ln: float, wth: float, ht: float) -> CQShape:
        return CQBox(ln, wth, ht, self)

    def genConeX(self, ln: float, r1: float, r2: float) -> CQShape:
        return CQCone(ln, r1, r2, (1, 0, 0), self)

    def genConeY(self, ln: float, r1: float, r2: float) -> CQShape:
        return CQCone(ln, r1, r2, (0, 1, 0), self)

    def genConeZ(self, ln: float, r1: float, r2: float) -> CQShape:
        return CQCone(ln, r1, r2, (0, 0, 1), self)

    def genPolyRodX(self, ln: float, rad: float, sides: int) -> CQShape:
        return CQPolyRod(ln, rad, sides, "YZ", self)

    def genPolyRodY(self, ln: float, rad: float, sides: int) -> CQShape:
        return CQPolyRod(ln, rad, sides, "XZ", self)

    def genPolyRodZ(self, ln: float, rad: float, sides: int) -> CQShape:
        return CQPolyRod(ln, rad, sides, "XY", self)

    def genRodX(self, ln: float, rad: float) -> CQShape:
        return CQRod(ln, rad, "YZ", self)

    def genRodY(self, ln: float, rad: float) -> CQShape:
        return CQRod(ln, rad, "XZ", self)

    def genRodZ(self, ln: float, rad: float) -> CQShape:
        return CQRod(ln, rad, "XY", self)

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> CQShape:
        return CQPolyExtrusionZ(path, ht, self)

    def genLineSplineExtrusionZ(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        ht: float,
    ) -> CQShape:
        return CQLineSplineExtrusionZ(start, path, ht, self)

    def genLineSplineRevolveX(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        deg: float,
    ) -> CQShape:
        return CQLineSplineRevolveX(start, path, deg, self)

    def genCirclePolySweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> CQShape:
        return CQCirclePolySweep(rad, path, self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> CQShape:
        return CQTextZ(txt, fontSize, tck, font, self)

class CQShape(Shape):

    def __init__(self, api: CQShapeAPI):
        self.api: CQShapeAPI = api
        self.solid: cq.Workplane = None

    def getAPI(self) -> CQShapeAPI:
        return self.api

    def cut(self, cutter: CQShape) -> CQShape:
        self.solid = self.solid.cut(cutter.solid)
        return self

    def dup(self) -> CQShape:
        duplicate = copy.copy(self)
        duplicate.solid = self.solid.val().copy()
        return duplicate

    def filletByNearestEdges(
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

    def segsByDim(self, dim: float) -> int:
        # Since CadQuery isusing Spline to connect pts for curves so use less segments
        return math.ceil(abs(dim) ** 0.25 * self.api.fidelity.smoothingSegments())

    def mirrorXZ(self) -> CQShape:
        mirror = self.solid.mirror("XZ")
        dup = copy.copy(self)
        dup.solid = mirror
        return dup

    def mv(self, x: float, y: float, z: float) -> CQShape:
        if x == 0 and y == 0 and z == 0:
            return self
        self.solid = self.solid.translate((x, y, z))
        return self

    def remove(self):
        pass

    def rotateX(self, ang: float) -> CQShape:
        if ang == 0:
            return self
        self.solid = self.solid.rotate((-1, 0, 0), (1, 0, 0), ang)
        return self

    def rotateY(self, ang: float) -> CQShape:
        if ang == 0:
            return self
        self.solid = self.solid.rotate((0, -1, 0), (0, 1, 0), ang)
        return self

    def rotateZ(self, ang: float) -> CQShape:
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

    def show(self):
        return self.solid


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
            self.segsByDim,
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
            self.segsByDim,
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


if __name__ == "__main__":
    CQShapeAPI(Fidelity.LOW).test(os.path.join(DEFAULT_TEST_DIR, "cq-all.stl"))
