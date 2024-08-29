from __future__ import annotations
import copy
import math
import os
from pathlib import Path
import sys

from nptyping import NDArray
import numpy as np
import trimesh as tm
from PIL import Image, ImageDraw, ImageFont
from pylele_api import ShapeAPI, Shape
from pylele_config import Fidelity, Implementation
from pylele_utils import descreteBezierChain, dimXY, encureClosed2DPath, ensureFileExtn, pathBounds, pathLen, radians, superGradient
from shapely.geometry import Polygon
from typing import Union


"""
    Encapsulate Trimesh implementation specific calls
"""
class TMShapeAPI(ShapeAPI):

    rotZtoX: NDArray = tm.transformations.rotation_matrix(angle=radians(90), direction=(0, 1, 0))
    rotZtoY: NDArray = tm.transformations.rotation_matrix(angle=radians(-90), direction=(1, 0, 0))

    def __init__(self, fidel: Fidelity):
        super().__init__()
        self.fidelity = fidel

    def getFidelity(self) -> Fidelity:
        return self.fidelity
    
    def getImplementation(self) -> Implementation:
        return Implementation.TRIMESH

    def setFidelity(self, fidel: Fidelity) -> None:
        self.fidelity = fidel

    def exportSTL(self, shape: TMShape, path: Union[str, Path]) -> None:
       shape.solid.export(ensureFileExtn(path,'.stl'))

    def exportBest(self, shape: TMShape, path: Union[str, Path]) -> None:
       shape.solid.export(ensureFileExtn(path,'.glb'))

    def genBall(self, rad: float) -> TMShape:
        return TMBall(rad, self)

    def genBox(self, l: float, wth: float, ht: float) -> TMShape:
        return TMBox(l, wth, ht, self)

    def genConeX(self, l: float, r1: float, r2: float) -> TMShape:
        return TMCone(l, r1, r2, None, self.rotZtoX, self)

    def genConeY(self, l: float, r1: float, r2: float) -> TMShape:
        return TMCone(l, r1, r2, None, self.rotZtoY, self)

    def genConeZ(self, l: float, r1: float, r2: float) -> TMShape:
        return TMCone(l, r1, r2, None, None, self)

    def genPolyRodX(self, l: float, rad: float, sides: int) -> TMShape:
        return TMRod(l, rad, sides, self.rotZtoX, self)

    def genPolyRodY(self, l: float, rad: float, sides: int) -> TMShape:
        return TMRod(l, rad, sides, self.rotZtoY, self)

    def genPolyRodZ(self, l: float, rad: float, sides: int) -> TMShape:
        return TMRod(l, rad, sides, None, self)

    def genRodX(self, l: float, rad: float) -> TMShape:
        return TMRod(l, rad, None, self.rotZtoX, self)

    def genRodY(self, l: float, rad: float) -> TMShape:
        return TMRod(l, rad, None, self.rotZtoY, self)

    def genRodZ(self, l: float, rad: float) -> TMShape:
        return TMRod(l, rad, None, None, self)

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> TMShape:
        return TMPolyExtrusionZ(path, ht, self)

    def genLineSplineExtrusionZ(self, 
        start: tuple[float, float], 
        path: list[tuple[float, float] | list[tuple[float, float, float, float, float]]], 
        ht: float,
    ) -> TMShape:
        return TMLineSplineExtrusionZ(start, path, ht, self)
    
    def genLineSplineRevolveX(self, 
        start: tuple[float, float], 
        path: list[tuple[float, float] | list[tuple[float, float, float, float, float]]], 
        deg: float,
    ) -> TMShape:
        return TMLineSplineRevolveX(start, path, deg, self)
    
    def genCirclePolySweep(self, rad: float, path: list[tuple[float, float, float]]) -> TMShape:
        return TMCirclePolySweep(rad, path, self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> TMShape:
        return TMTextZ(txt, fontSize, tck, font, self)
        
    def getJoinCutTol(self) -> float:
        return Implementation.TRIMESH.joinCutTol()
        


class TMShape(Shape):
    
    X_AXIS = (1, 0, 0)
    Y_AXIS = (0, 1, 0)
    Z_AXIS = (0, 0, 1)

    def __init__(self, api: TMShapeAPI):
        super().__init__()
        self.api:TMShapeAPI = api
        self.solid:tm.Trimesh = None

    def ensureVolume(self) -> None:
        if self.solid.is_volume:
            return
        else:
            print("warning: solid is NOT a valid volume, attempt minor repair...", file=sys.stderr)
            self.solid.update_faces(self.solid.nondegenerate_faces())
            self.solid.update_faces(self.solid.unique_faces())
            self.solid.remove_infinite_values()
            self.solid.remove_unreferenced_vertices()

        if self.solid.is_volume:
            return
        else:
            print("warning: solid is NOT a valid volume, attempt major repair...", file=sys.stderr)
            tm.repair.fill_holes(self.solid)
            tm.repair.fix_normals(self.solid)
            tm.repair.fix_winding(self.solid)
            tm.repair.fix_inversion(self.solid)
        
        if self.solid.is_volume:
            return
        else:
            print("warning: repaired mesh is still NOT a valid volume, make a convex hull as last resort...", file=sys.stderr)
            self.solid = self.solid.convex_hull


    def getAPI(self) -> TMShapeAPI:
        return self.api

    def getImplSolid(self) -> tm.Trimesh:
        return self.solid
    
    def segsByDim(self, dim: float) -> int:
        return math.ceil(math.sqrt(abs(dim)) * self.api.fidelity.smoothingSegments())
    
    def cut(self, cutter: TMShape) -> TMShape:
        if cutter is None or cutter.solid is None:
            return self
        self.ensureVolume()
        cutter.ensureVolume()
        self.solid = tm.boolean.difference([self.solid, cutter.solid])
        return self

    def dup(self) -> TMShape:
        duplicate = copy.copy(self)
        duplicate.solid = self.solid.copy()
        return duplicate
    
    def filletByNearestEdges(self, 
        nearestPts: list[tuple[float, float, float]], 
        rad: float,
    ) -> TMShape:
                
        def nearest_edge_to_point(mesh, point):
            edges = mesh.edges
            vertices = mesh.vertices

            min_distance = float('inf')
            nearest_edge = None

            for edge in edges:
                v0, v1 = vertices[edge]
                distance = point_to_edge_distance(point, v0, v1)
                if distance < min_distance:
                    min_distance = distance
                    nearest_edge = edge

            return nearest_edge, min_distance

        def point_to_edge_distance(point, v0, v1):
            # Vector from v0 to point
            v0_to_point = point - v0
            # Vector from v0 to v1
            v0_to_v1 = v1 - v0
            # Project point onto the line defined by v0 and v1
            projection_length = np.dot(v0_to_point, v0_to_v1) / np.dot(v0_to_v1, v0_to_v1)
            projection = v0 + projection_length * v0_to_v1

            # Clamp the projection to the segment [v0, v1]
            if projection_length < 0:
                projection = v0
            elif projection_length > 1:
                projection = v1

            # Distance from point to the projection
            distance = np.linalg.norm(point - projection)
            return distance

        print("Trimesh: filletByNearestEdges(...) not implemented yet.", file=sys.stderr)

        return self

    def join(self, joiner: TMShape) -> TMShape:
        if joiner is None or joiner.solid is None:
            return self
        
        self.ensureVolume()
        joiner.ensureVolume()
        self.solid = tm.boolean.union([self.solid, joiner.solid])
        return self

    # draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
    def lineSplineXY(
        self,
        start: tuple[float, float],
        lineSpline: list[Union[tuple[float, float], list[tuple[float, float, float, float, float]]]],
    ) -> list[tuple[float, float]]:
        
        lastX, lastY = start
        result = [start]
        for p_or_s in lineSpline:
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

    def mirrorXZ(self) -> TMShape:
        dup = copy.copy(self)
        reflectXZ = tm.transformations.reflection_matrix([0, 0, 0], [0, 1, 0])
        dup.solid = self.solid.copy().apply_transform(reflectXZ)
        return dup

    def mv(self, x: float, y: float, z: float) -> TMShape:
        if x == 0 and y == 0 and z == 0:
            return self
        self.solid = self.solid.apply_translation((x, y, z))
        return self

    def remove(self):
        pass

    def rotate(self, ang: float, dir: tuple[float, float, float]) -> TMShape:
        if ang == 0:
            return self
        rotMat = tm.transformations.rotation_matrix(angle=radians(ang), direction=dir)
        self.solid = self.solid.apply_transform(rotMat)
        return self
    
    def rotateX(self, ang: float) -> TMShape:
        return self.rotate(ang, self.X_AXIS)

    def rotateY(self, ang: float) -> TMShape:
        return self.rotate(ang, self.Y_AXIS)

    def rotateZ(self, ang: float) -> TMShape:
        return self.rotate(ang, self.Z_AXIS)

    def scale(self, x: float, y: float, z: float) -> TMShape:
        if x == 1 and y == 1 and z == 1:
            return self
        self.solid = self.solid.apply_scale((x, y, z))
        return self

    def show(self):
        pass


class TMBall(TMShape):
    def __init__(self, rad: float, api: TMShapeAPI):
        super().__init__(api)
        segs = self.segsByDim(rad)
        self.solid = tm.creation.uv_sphere(radius=rad, count=(segs,segs), validate=True)


class TMBox(TMShape):
    def __init__(self, l: float, wth: float, ht: float, api: TMShapeAPI):
        super().__init__(api)
        self.ln = l
        self.wth = wth
        self.ht = ht
        self.solid = tm.creation.box(extents=(l, wth, ht), validate=True)



class TMCone(TMShape):
    def __init__(self, l: float, r1: float, r2: float, sides: float, rotMat: NDArray, api: TMShapeAPI):
        super().__init__(api)
        sects = self.segsByDim(max(r1, r2)) if sides is None else sides
        linestring = [[0, 0], [r1, 0], [r2, l], [0, l]]
        self.solid = tm.creation.revolve(linestring=linestring, sections=sects, transform=rotMat, validate=True)


class TMPolyExtrusionZ(TMShape):
    def __init__(self, path: list[tuple[float, float]], tck: float, api: TMShapeAPI):
        super().__init__(api)
        path = encureClosed2DPath(path)
        polygon = Polygon(path)
        self.solid = tm.creation.extrude_polygon(polygon, tck, cap_base=True, cap_top=True, tolerance=1e-5, validate=True)
        self.ensureVolume()

class TMRod(TMShape):
    def __init__(self, l: float, rad: float, sides: float, rotMat: NDArray, api: TMShapeAPI):
        super().__init__(api)
        segs = self.segsByDim(rad) if sides is None else sides
        self.solid = tm.creation.cylinder(radius=rad, height=l, sections=segs, transform=rotMat, validate=True)


# draw mix of straight lines from pt to pt, or draw spline with [(x,y,dx,dy), ...], then extrude on Z-axis
class TMLineSplineExtrusionZ(TMShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float, float]]]],
        ht: float, 
        api: TMShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.ht = ht
        polygon = Polygon(self.lineSplineXY(start, path))
        self.solid = tm.creation.extrude_polygon(polygon, ht) #, validate=True)

class TMLineSplineRevolveX(TMShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float, float]]]],
        deg: float, 
        api: TMShapeAPI,
    ):
        super().__init__(api)
        _, dimY = dimXY(start, path)
        segsY = self.segsByDim(dimY)
        self.path = path
        self.deg = deg
        linestring = self.lineSplineXY(start, path)
        stringSwapXY = [ (y, x) for x, y in linestring ]

        # revolve by 360 then cut away wedge to get valid volume as work around for
        # https://github.com/mikedh/trimesh/issues/2269
        self.solid = tm.creation.revolve(stringSwapXY, radians(360), segsY, validate=True)

        if abs(deg) < 360:

            maxDim = Shape.MAX_DIM
            if deg >= 0:
                cut = tm.creation.box([2*maxDim, 2*maxDim, 2*maxDim]).apply_translation((0, -maxDim, 0))
                if deg < 180:
                    cut2 = cut.copy()
                    rotMat = tm.transformations.rotation_matrix(angle=-radians(180-deg), direction=(0, 0, 1))
                    cut = tm.boolean.union([cut, cut2.apply_transform(rotMat)])
                elif deg > 180:
                    cut2 = cut.copy().apply_translation((0, 2*maxDim, 0))
                    rotMat = tm.transformations.rotation_matrix(angle=radians(deg-180), direction=(0, 0, 1))
                    cut = tm.boolean.difference([cut, cut2.apply_transform(rotMat)])
            else:
                cut = tm.creation.box([2*maxDim, 2*maxDim, 2*maxDim]).apply_translation((0, maxDim, 0))
                if abs(deg) < 180:
                    cut2 = cut.copy()
                    rotMat = tm.transformations.rotation_matrix(angle=radians(180-abs(deg)), direction=(0, 0, 1))
                    cut = tm.boolean.union([cut, cut2.apply_transform(rotMat)])
                elif abs(deg) > 180:
                    cut2 = cut.copy().apply_translation((0, -2*maxDim, 0))
                    rotMat = tm.transformations.rotation_matrix(angle=-radians(abs(deg)-180), direction=(0, 0, 1))
                    cut = tm.boolean.difference([cut, cut2.apply_transform(rotMat)])

            self.ensureVolume()
            self.solid = tm.boolean.difference([self.solid, cut])

        self.rotateZ(90).rotateY(90)
        

class TMCirclePolySweep(TMShape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
        api: TMShapeAPI,
    ):
        super().__init__(api)

        def circle_polygon_points(n, r):
            points = []
            for i in range(n):
                angle = 2 * math.pi * i / n
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                points.append((x, y))
            return points

        self.path = path
        self.rad = rad
        segs = self.segsByDim(rad)
        polygon = Polygon(circle_polygon_points(segs, rad))
        self.solid = tm.creation.sweep_polygon(polygon, path, validate=True)


class TMTextZ(TMShape):

    def __init__(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        font: str, 
        api: TMShapeAPI,
    ):
        super().__init__(api)

        print("Trimesh: TMTextZ(...) not implemented yet.", file=sys.stderr)

        self.txt = txt
        self.fontSize = fontSize
        self.tck = tck
        self.font = font
        self.solid = tm.creation.box(extents=(.5*fontSize*len(txt), fontSize, tck), validate=True)
        self.mv(0, 0, tck/2)


if __name__ == '__main__':
    TMShapeAPI(Fidelity.LOW).test(Path.cwd()  / 'test' / 'trimesh_api')