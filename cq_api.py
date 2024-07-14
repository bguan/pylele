from __future__ import annotations
import copy
import cadquery as cq
from pylele_api import ShapeAPI, Shape
from typing import Union

from pylele_config import Fidelity, Implementation

"""
    Encapsulate CAD Query implementation specific calls
"""
class CQShapeAPI(ShapeAPI):
    def __init__(self, fidel: Fidelity):
        self.fidelity = fidel

    def exportSTL(self, shape: CQShape, path: str) -> None:
        cq.exporters.export(
            shape.solid,
            path,
            cq.exporters.ExportTypes.STL,
            tolerance=self.fidelity.exportTol(),
        )

    def genBall(self, rad: float) -> CQShape:
        return CQBall(rad)

    def genBox(self, ln: float, wth: float, ht: float) -> CQShape:
        return CQBox(ln, wth, ht)

    def genConeX(self, ln: float, r1: float, r2: float) -> CQShape:
        return CQCone(ln, r1, r2, (1,0,0))

    def genConeY(self, ln: float, r1: float, r2: float) -> CQShape:
        return CQCone(ln, r1, r2, (0,1,0))

    def genConeZ(self, ln: float, r1: float, r2: float) -> CQShape:
        return CQCone(ln, r1, r2, (0,0,1))

    def genRodX(self, ln: float, rad: float) -> CQShape:
        return CQRod(ln, rad, "YZ")

    def genRodY(self, ln: float, rad: float) -> CQShape:
        return CQRod(ln, rad, "XZ")

    def genRodZ(self, ln: float, rad: float) -> CQShape:
        return CQRod(ln, rad, "XY")

    def genRndRodX(self, ln: float, rad: float, domeRatio: float = 1) -> CQShape:
        return CQRndRod(ln, rad, domeRatio, "YZ")

    def genRndRodY(self, ln: float, rad: float, domeRatio: float = 1) -> CQShape:
        return CQRndRod(ln, rad, domeRatio, "XZ")

    def genRndRodZ(self, ln: float, rad: float, domeRatio: float = 1) -> CQShape:
        return CQRndRod(ln, rad, domeRatio, "XY")

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> CQShape:
        return CQPolyExtrusionZ(path, ht)

    def genLineSplineExtrusionZ(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]], 
            ht: float,
        ) -> CQShape:
        return CQLineSplineExtrusionZ(start, path, ht)
    
    def genLineSplineRevolveX(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]], 
            deg: float,
        ) -> CQShape:
        return CQLineSplineRevolveX(start, path, deg)
    
    def genCirclePolySweep(self, rad: float, path: list[tuple[float, float, float]]) -> CQShape:
        return CQCirclePolySweep(rad, path)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> CQShape:
        return CQTextZ(txt, fontSize, tck, font)

    def genQuarterBall(self, radius: float, pickTop: bool, pickFront: bool) -> CQShape:
        return CQQuarterBall(radius, pickTop, pickFront)
        
    def genHalfDisc(self, radius: float, pickFront: bool, tck: float) -> CQShape:
        return CQHalfDisc(radius, pickFront, tck)
    
    def getJoinCutTol(self):
        return Implementation.CAD_QUERY.joinCutTol()


class CQShape(Shape):

    def __init__(self):
        self.solid = None

    def cut(self, cutter: CQShape) -> CQShape:
        self.solid = self.solid.cut(cutter.solid)
        return self

    def filletByNearestEdges(self, 
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

    def half(self) -> CQShape:
        halfCutter = CQBox(2000, 2000, 2000).mv(0, 1000, 0)
        self = self.cut(halfCutter)
        return self

    def join(self, joiner: CQShape) -> CQShape:
        self.solid = self.solid.union(joiner.solid)
        return self

    # draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
    def lineSplineXY(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    ) -> cq.Workplane:
        lastX, lastY = start
        trace = cq.Workplane("XY").moveTo(lastX, lastY)
        for p_or_s in path:
            if isinstance(p_or_s, tuple):
                # a point so draw line
                lastX, lastY = p_or_s
                trace = trace.lineTo(lastX, lastY)
            elif isinstance(p_or_s, list):
                # a list of points and gradients/tangents to trace spline thru
                x1, y1, _, _ = p_or_s[0]
                # insert first point if diff from last
                if lastX != x1 or lastY != y1:
                    dx0 = x1 - lastX
                    dy0 = y1 - lastY
                    p_or_s.insert(0, (lastX, lastY, dx0, dy0))
                splinePts = [(p[0], p[1]) for p in p_or_s]
                tangents = [cq.Vector(p[2], p[3]) for p in p_or_s]
                trace = trace.spline(splinePts, tangents, scale=True) 
        trace = trace.close()
        return trace

    def mirrorXZ(self) -> CQShape:
        mirror = self.solid.mirror("XZ")
        dup = copy.copy(self)
        dup.solid = mirror
        return dup

    def mv(self, x: float, y: float, z: float) -> CQShape:
        self.solid = self.solid.translate((x, y, z))
        return self

    def remove(self):
        pass
    
    def rotateX(self, ang: float) -> CQShape:
        self.solid = self.solid.rotate((-1, 0, 0), (1, 0, 1), ang)
        return self

    def rotateY(self, ang: float) -> CQShape:
        self.solid = self.solid.rotate((0, -1, 0), (0, 1, 0), ang)
        return self

    def rotateZ(self, ang: float) -> CQShape:
        self.solid = self.solid.rotate((0, 0, -1), (0, 0, 1), ang)
        return self

    def scale(self, x: float, y: float, z: float) -> CQShape:
        t = cq.Matrix([
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ])
        self.solid = self.solid.newObject([
            o.transformGeometry(t) if isinstance(o, cq.Shape) else o
            for o in self.solid.objects
        ])
        return self

    def show(self):
        return self.solid


class CQBall(CQShape):
    def __init__(self, rad: float):
        self.rad = rad
        self.solid = cq.Workplane("XY").sphere(rad)


class CQCone(CQShape):
    def __init__(self, ln: float, r1: float, r2: float, dir: tuple[float, float, float]):
        self.ln = ln
        self.r1 = r1
        self.r2 = r2
        self.solid = cq.Workplane("YZ")\
            .add(cq.Solid.makeCone(r1, r2, ln, dir=dir))


class CQRndRod(CQShape):
    def __init__(self, ln: float, rad: float, domeRatio: float = 1, plane: str = "YZ"):
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane(plane).cylinder(ln/domeRatio, rad)
        if domeRatio > 0:
            self.solid = self.solid.edges().fillet(rad)
        if domeRatio != 1:
            self = self.scale(
                domeRatio if plane == "YZ" else 1, 
                domeRatio if plane == "XZ" else 1, 
                domeRatio if plane == "XY" else 1,
            )


class CQRod(CQShape):
    def __init__(self, ln: float, rad: float, plane: str = "YZ"):
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane(plane).cylinder(ln, rad)

class CQBox(CQShape):
    def __init__(self, ln: float, wth: float, ht: float):
        self.ln = ln
        self.wth = wth
        self.ht = ht
        self.solid = cq.Workplane("XY").box(ln, wth, ht)


# draw straight lines from pt to pt then extrude
class CQPolyExtrusionZ(CQShape):
    def __init__(self, path: list[tuple[float, float]], ht: float):
        self.path = path
        self.ht = ht
        self.solid = cq.Workplane("XY").sketch()\
            .polygon(path).finalize().extrude(ht)


# draw mix of straight lines from pt to pt, or draw spline with [(x,y,dx,dy), ...], then extrude on Z-axis
class CQLineSplineExtrusionZ(CQShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        ht: float,
    ):
        self.path = path
        self.ht = ht
        self.solid = self.lineSplineXY(start, path).extrude(ht)


# draw mix of straight lines from pt to pt, or draw spline with [(x,y,dx,dy), ...], then revolve on X-axis
class CQLineSplineRevolveX(CQShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        deg: float,
    ):
        self.path = path
        self.deg = deg if deg > 0 else -deg
        self.solid = self.lineSplineXY(start, path)\
            .revolve(self.deg, (0, 0, 0), (1 if deg > 0 else -1, 0, 0))


# sweep circle along polyline path
class CQCirclePolySweep(CQShape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
    ):
        self.path = path
        self.rad = rad
        path0 = [(p[0] - path[0][0], p[1] - path[0][1], p[2] - path[0][2])
                 for p in path]
        sweepPath = cq.Wire.makePolygon(path0)
        self.solid = cq.Workplane("YZ").circle(rad)\
            .sweep(sweepPath, transition='round', sweepAlongWires=True)
        self.solid = self.solid.translate(path[0])


# Text
class CQTextZ(CQShape):
    def __init__(
        self,
        txt: str,
        fontSize: float = 10,
        tck: float = 5,
        font: str = "Arial",
    ):
        self.txt = txt
        self.fontSize = fontSize
        self.tck = tck
        self.font = font
        self.solid = cq.Workplane("XY").text(txt, fontSize, tck, font=font)


class CQQuarterBall(CQShape):
    def __init__(self, rad: float, pickTop: bool, pickFront: bool):
        self.pickTop = pickTop
        self.pickFront = pickFront
        self.rad = rad
        ball = cq.Workplane("XY").sphere(rad)
        topCut = cq.Workplane("XY").box(2000, 2000, 2000).translate((0, 0, -1000 if pickTop else 1000))
        frontCut = cq.Workplane("XY").box(2000, 2000, 2000).translate((1000 if pickFront else -1000, 0, 0))
        self.solid = ball.cut(topCut).cut(frontCut)

class CQHalfDisc(CQShape):
    def __init__(self, rad: float, pickFront: bool, tck: float):
        self.pickFront = pickFront
        self.tck = tck
        self.rad = rad
        rod = cq.Workplane("XY").cylinder(tck, rad)
        cutter = cq.Workplane("XY").box(2000, 2000, 2000).translate((1000 if pickFront else -1000, 0, 0))
        self.solid = rod.cut(cutter)


if __name__ == '__main__':
    CQShapeAPI(Fidelity.LOW).test("build/cq-all.stl")