import copy
import cadquery as cq
from typing import Union

"""
    Encapsulate CAD Query implementation specific calls
"""

class Shape:
    def __init__(self):
        self.solid = None

    def cut(self, cutter):
        self.solid = self.solid.cut(cutter.solid)
        return self

    def exportSTL(self, path: str, tol: float = 0.0001):
        cq.exporters.export(
            self.solid,
            path,
            cq.exporters.ExportTypes.STL,
            tolerance=tol,
        )

    def fillet(self, nearestPts: list[tuple[float, float, float]], rad: float):
        for p in nearestPts:
            self.solid = self.solid.edges(
                cq.selectors.NearestToPointSelector(p),
            ).fillet(rad)
        return self

    def join(self, joiner):
        self.solid = self.solid.union(joiner.solid)
        return self

    def mirrorXZ(self):
        mirror = self.solid.mirror("XZ")
        dup = copy.copy(self)
        dup.solid = mirror
        return dup

    def mv(self, x: float, y: float, z: float):
        self.solid = self.solid.translate((x, y, z))
        return self

    def rotateY(self, ang: float):
        self.solid = self.solid.rotate((0, -1, 0), (0, 1, 0), ang)
        return self

    def rotateZ(self, ang: float):
        self.solid = self.solid.rotate((0, 0, -1), (0, 0, 1), ang)
        return self

    def scale(self, x: float, y: float, z: float):
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

    # draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
    def lineSplineXY(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    ):
        trace = cq.Workplane("XY").moveTo(start[0], start[1])
        for p_or_s in path:
            if isinstance(p_or_s, tuple):
                # a point so draw line
                trace = trace.lineTo(p_or_s[0], p_or_s[1])
            elif isinstance(p_or_s, list):
                # a list of points and gradients/tangents to trace spline thru
                splinePts = [(p[0], p[1]) for p in p_or_s]
                tangents = [cq.Vector(p[2],p[3]) for p in p_or_s]
                # [tangents[0], tangents[-1]])
                trace = trace.spline(splinePts, tangents)
        trace = trace.close()
        return trace


class ConeZ(Shape):
    def __init__(self, ln: float, r1: float, r2: float):
        self.ln = ln
        self.r1 = r1
        self.r2 = r2
        self.solid = cq.Workplane("XY").add(
            cq.Solid.makeCone(r1, r2, ln, dir=(0, 0, 1)))


class ConeX(Shape):
    def __init__(self, ln: float, r1: float, r2: float):
        self.ln = ln
        self.r1 = r1
        self.r2 = r2
        self.solid = cq.Workplane("YZ").add(
            cq.Solid.makeCone(r1, r2, ln, dir=(1, 0, 0)))


class RndRodX(Shape):
    def __init__(self, ln: float, rad: float):
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane("YZ").cylinder(ln, rad).edges().fillet(rad)


class RndRodY(Shape):
    def __init__(self, ln: float, rad: float):
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane("XZ").cylinder(ln, rad).edges().fillet(rad)


class RodZ(Shape):
    def __init__(self, ln: float, rad: float):
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane("XY").cylinder(ln, rad)


class RodY(Shape):
    def __init__(self, ln: float, rad: float):
        self.ln = ln
        self.rad = rad
        self.solid = cq.Workplane("XZ").cylinder(ln, rad)


class Box(Shape):
    def __init__(self, ln: float, wth: float, ht: float):
        self.ln = ln
        self.wth = wth
        self.ht = ht
        self.solid = cq.Workplane("XY").box(ln, wth, ht)


# draw straight lines from pt to pt then extrude
class PolyExtrusionZ(Shape):
    def __init__(self, path: list[tuple[float, float]], ht: float):
        self.path = path
        self.ht = ht
        self.solid = cq.Workplane("XY").sketch().polygon(
            path).finalize().extrude(ht)


# draw mix of straight lines from pt to pt, or draw spline with [(x,y,dx,dy), ...], then extrude on Z-axis
class SplineExtrusionZ(Shape):
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
class SplineRevolveX(Shape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        deg: float,
    ):
        self.path = path
        self.deg = deg if deg > 0 else -deg
        self.solid = self.lineSplineXY(start, path).revolve(
            self.deg, (0, 0, 0), (1 if deg > 0 else -1, 0, 0))


# sweep circle on XY plane along polyline path on YZ plane from origin
class CirclePolySweepYZ(Shape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float]],
    ):
        self.path = path
        self.rad = rad
        sweepAlong = cq.Workplane("YZ").polyline(path)
        self.solid = cq.Workplane("XY").circle(rad).sweep(sweepAlong)