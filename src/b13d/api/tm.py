#!/usr/bin/env python3

from __future__ import annotations
import copy
from math import pi, cos, sin, ceil
from nptyping import NDArray
import numpy as np
import os
from pathlib import Path
from shapely.geometry import Polygon
import sys
import trimesh as tm
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import ShapeAPI, Shape, test_api
from b13d.api.utils import (
    dimXY,
    ensureClosed2DPath,
    file_ensure_extension,
    isPathCounterClockwise,
    lineSplineXY,
    pathBoundsArea,
    radians,
    textToGlyphsPaths,
)


"""
    Encapsulate Trimesh implementation specific calls
"""


class TMShapeAPI(ShapeAPI):

    rotZtoX: NDArray = tm.transformations.rotation_matrix(
        angle=radians(90),
        direction=(0, 1, 0),
    )
    rotZtoY: NDArray = tm.transformations.rotation_matrix(
        angle=radians(-90),
        direction=(1, 0, 0),
    )

    def export(self, shape: Shape, path: Union[str, Path],fmt=".stl") -> None:
        assert fmt in [".stl",".glb"]
        shape.solid.export(file_ensure_extension(path, fmt))

    def export_best(self, shape: TMShape, path: Union[str, Path]) -> None:
        self.export(shape=shape,path=path,fmt=".glb")

    def export_stl(self, shape: TMShape, path: Union[str, Path]) -> None:
        self.export(shape=shape, path=path, fmt=".stl")

    def export_best_multishapes(
        self,
        shapes: list[Shape],
        assembly_name: str,
        path: Union[str, Path],
    ) -> None:
        # Create a scene
        scene = tm.Scene()

        # Add shapes to the assembly with assigned colors
        for i, s in enumerate(shapes):
            scene.add_geometry(
                s.solid,
                node_name=f"Part {i+1} of {len(shapes)}: {s.name}",
            )

        # Export the assembly to a GLB file
        scene.export(file_ensure_extension(path, ".glb"))

    def sphere(self, r: float) -> TMShape:
        return TMBall(r, self)

    def box(self, l: float, wth: float, ht: float, center: bool = True) -> TMShape:
        retval = TMBox(l, wth, ht, self)
        if center:
            return retval    
        return retval.mv(-l / 2, -wth / 2, -ht / 2)        

    def cone_x(self, h: float, r1: float, r2: float) -> TMShape:
        return TMCone(h, r1, r2, None, self.rotZtoX, self)

    def cone_y(self, h: float, r1: float, r2: float) -> TMShape:
        return TMCone(h, r1, r2, None, self.rotZtoY, self)

    def cone_z(self, h: float, r1: float, r2: float) -> TMShape:
        return TMCone(h, r1, r2, None, None, self)

    def regpoly_extrusion_x(self, l: float, rad: float, sides: int) -> TMShape:
        return TMRod(l, rad, sides, self.rotZtoX, self)

    def regpoly_extrusion_y(self, l: float, rad: float, sides: int) -> TMShape:
        return TMRod(l, rad, sides, self.rotZtoY, self)

    def regpoly_extrusion_z(self, l: float, rad: float, sides: int) -> TMShape:
        return TMRod(l, rad, sides, None, self)

    def cylinder_x(self, h: float, rad: float) -> TMShape:
        return TMRod(h, rad, None, self.rotZtoX, self)

    def cylinder_y(self, h: float, rad: float) -> TMShape:
        return TMRod(h, rad, None, self.rotZtoY, self)

    def cylinder_z(self, h: float, rad: float) -> TMShape:
        return TMRod(h, rad, None, None, self)

    def polygon_extrusion(self, path: list[tuple[float, float]], ht: float) -> TMShape:
        return TMPolyExtrusionZ(path, ht, self)

    def spline_extrusion(
        self,
        start: tuple[float, float],
        path: list[
            tuple[float, float] | list[tuple[float, float, float, float, float]]
        ],
        ht: float,
    ) -> TMShape:
        if ht < 0:
            return TMLineSplineExtrusionZ(start, path, abs(ht), self).mv(0, 0, -abs(ht))
        return TMLineSplineExtrusionZ(start, path, ht, self)

    def spline_revolve(
        self,
        start: tuple[float, float],
        path: list[
            tuple[float, float] | list[tuple[float, float, float, float, float]]
        ],
        deg: float,
    ) -> TMShape:
        return TMLineSplineRevolveX(start, path, deg, self)

    def regpoly_sweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> TMShape:
        return TMCirclePolySweep(rad, path, self)

    def text(self, txt: str, fontSize: float, tck: float, font: str) -> TMShape:
        return TMTextZ(txt, fontSize, tck, font, self)

    def genImport(self, infile: str, extrude: float = None) -> TMShape:
        return TMImport(infile, extrude=extrude)

class TMShape(Shape):

    X_AXIS = (1, 0, 0)
    Y_AXIS = (0, 1, 0)
    Z_AXIS = (0, 0, 1)

    def __init__(self, api: TMShapeAPI):
        super().__init__(api)
        self.solid: tm.Trimesh = None


    def ensureVolume(self) -> None:
        if self.solid.is_volume:
            return
        else:
            print(
                "warning: solid is NOT a valid volume, attempt minor repair...",
                file=sys.stderr,
            )
            jctol = self.api.implementation.tolerance()
            self.solid.update_faces(self.solid.nondegenerate_faces(jctol / 2))
            self.solid.update_faces(self.solid.unique_faces())
            self.solid.remove_infinite_values()
            self.solid.remove_unreferenced_vertices()

        if self.solid.is_volume:
            return
        else:
            print(
                "warning: solid is NOT a valid volume, attempt major repair...",
                file=sys.stderr,
            )
            tm.repair.fill_holes(self.solid)
            tm.repair.fix_normals(self.solid, multibody=True)
            tm.repair.fix_winding(self.solid)
            tm.repair.fix_inversion(self.solid, multibody=True)

        if self.solid.is_volume:
            return
        else:
            print(
                "warning: repaired mesh is still NOT a valid volume, make a convex hull as last resort...",
                file=sys.stderr,
            )
            self.solid = self.solid.convex_hull

    def _smoothing_segments(self, dim: float) -> int:
        return ceil(abs(dim) ** 0.5 * self.api.fidelity.smoothing_segments())

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

    def fillet(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> TMShape:

        def nearest_edge_to_point(mesh, point):
            edges = mesh.edges
            vertices = mesh.vertices

            min_distance = float("inf")
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
            projection_length = np.dot(v0_to_point, v0_to_v1) / np.dot(
                v0_to_v1, v0_to_v1
            )
            projection = v0 + projection_length * v0_to_v1

            # Clamp the projection to the segment [v0, v1]
            if projection_length < 0:
                projection = v0
            elif projection_length > 1:
                projection = v1

            # Distance from point to the projection
            distance = np.linalg.norm(point - projection)
            return distance

        print(
            "Trimesh: fillet(...) not implemented yet.", file=sys.stderr
        )

        return self

    def hull(self):
        self.solid = self.solid.convex_hull
        return self

    def join(self, joiner: TMShape) -> TMShape:
        if joiner is None or joiner.solid is None:
            return self

        self.ensureVolume()
        joiner.ensureVolume()
        self.solid = tm.boolean.union([self.solid, joiner.solid])
        return self

    def mirror(self) -> TMShape:
        dup = copy.copy(self)
        reflectXZ = tm.transformations.reflection_matrix([0, 0, 0], [0, 1, 0])
        dup.solid = self.solid.copy().apply_transform(reflectXZ)
        return dup

    def mv(self, x: float, y: float, z: float) -> TMShape:
        if x == 0 and y == 0 and z == 0:
            return self
        self.solid = self.solid.apply_translation((x, y, z))
        return self

    def _rotate(self, ang: float, dir: tuple[float, float, float]) -> TMShape:
        if ang == 0:
            return self
        rotMat = tm.transformations.rotation_matrix(angle=radians(ang), direction=dir)
        self.solid = self.solid.apply_transform(rotMat)
        return self

    def rotate_x(self, ang: float) -> TMShape:
        return self._rotate(ang, self.X_AXIS)

    def rotate_y(self, ang: float) -> TMShape:
        return self._rotate(ang, self.Y_AXIS)

    def rotate_z(self, ang: float) -> TMShape:
        return self._rotate(ang, self.Z_AXIS)

    def scale(self, x: float, y: float, z: float) -> TMShape:
        if x == 1 and y == 1 and z == 1:
            return self
        self.solid = self.solid.apply_scale((x, y, z))
        return self

    def set_color(self, rgb):
        face_colors = (rgb[0], rgb[1], rgb[2], 255)
        self.solid.visual.face_colors = face_colors
        return self

class TMBall(TMShape):
    def __init__(self, rad: float, api: TMShapeAPI):
        super().__init__(api)
        segs = self._smoothing_segments(2 * pi * rad)
        self.solid = tm.creation.uv_sphere(
            radius=rad, count=(segs, segs), validate=True
        )


class TMBox(TMShape):
    def __init__(self, l: float, wth: float, ht: float, api: TMShapeAPI):
        super().__init__(api)
        self.ln = l
        self.wth = wth
        self.ht = ht
        self.solid = tm.creation.box(extents=(l, wth, ht), validate=True)


class TMCone(TMShape):
    def __init__(
        self,
        l: float,
        r1: float,
        r2: float,
        sides: float,
        rotMat: NDArray,
        api: TMShapeAPI,
    ):
        super().__init__(api)
        sects = self._smoothing_segments(2 * pi * max(r1, r2)) if sides is None else sides
        linestring = [[0, 0], [r1, 0], [r2, l], [0, l]]
        self.solid = tm.creation.revolve(
            linestring=linestring, sections=sects, transform=rotMat, validate=True
        )


class TMPolyExtrusionZ(TMShape):
    def __init__(self, path: list[tuple[float, float]], tck: float, api: TMShapeAPI):
        super().__init__(api)
        path = ensureClosed2DPath(path)
        polygon = Polygon(path)
        self.solid = tm.creation.extrude_polygon(
            polygon, tck, cap_base=True, cap_top=True, tolerance=1e-5, validate=True
        )
        self.ensureVolume()


class TMRod(TMShape):
    def __init__(
        self, l: float, rad: float, sides: float, rotMat: NDArray, api: TMShapeAPI
    ):
        super().__init__(api)
        segs = self._smoothing_segments(2 * pi * rad) if sides is None else sides
        self.solid = tm.creation.cylinder(
            radius=rad, height=l, sections=segs, transform=rotMat, validate=True
        )


# draw mix of straight lines from pt to pt, or draw spline with [(x,y,dx,dy), ...], then extrude on Z-axis
class TMLineSplineExtrusionZ(TMShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[
            Union[tuple[float, float], list[tuple[float, float, float, float, float]]]
        ],
        ht: float,
        api: TMShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.ht = ht
        polygon = Polygon(lineSplineXY(start, path, self._smoothing_segments))
        self.solid = tm.creation.extrude_polygon(polygon, ht)  # , validate=True)


class TMLineSplineRevolveX(TMShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[
            Union[tuple[float, float], list[tuple[float, float, float, float, float]]]
        ],
        deg: float,
        api: TMShapeAPI,
    ):
        super().__init__(api)
        _, dimY = dimXY(start, path)
        segsY = ceil(self._smoothing_segments(2 * pi * dimY) * abs(deg) / 360)
        self.path = path
        self.deg = deg
        linestring = lineSplineXY(start, path, self._smoothing_segments)
        stringSwapXY = [(y, x) for x, y in linestring]

        # revolve by 360 then cut away wedge to get valid volume as work around for
        # https://github.com/mikedh/trimesh/issues/2269
        self.solid = tm.creation.revolve(
            stringSwapXY, radians(360), segsY, validate=True
        )

        if abs(deg) < 360:

            maxDim = Shape.MAX_DIM
            if deg >= 0:
                cut = tm.creation.box(
                    [2 * maxDim, 2 * maxDim, 2 * maxDim]
                ).apply_translation((0, -maxDim, 0))
                if deg < 180:
                    cut2 = cut.copy()
                    rotMat = tm.transformations.rotation_matrix(
                        angle=-radians(180 - deg),
                        direction=(0, 0, 1),
                    )
                    cut = tm.boolean.union([cut, cut2.apply_transform(rotMat)])
                elif deg > 180:
                    cut2 = cut.copy().apply_translation((0, 2 * maxDim, 0))
                    rotMat = tm.transformations.rotation_matrix(
                        angle=radians(deg - 180),
                        direction=(0, 0, 1),
                    )
                    cut = tm.boolean.difference([cut, cut2.apply_transform(rotMat)])
            else:
                cut = tm.creation.box(
                    [2 * maxDim, 2 * maxDim, 2 * maxDim]
                ).apply_translation((0, maxDim, 0))
                if abs(deg) < 180:
                    cut2 = cut.copy()
                    rotMat = tm.transformations.rotation_matrix(
                        angle=radians(180 - abs(deg)),
                        direction=(0, 0, 1),
                    )
                    cut = tm.boolean.union([cut, cut2.apply_transform(rotMat)])
                elif abs(deg) > 180:
                    cut2 = cut.copy().apply_translation((0, -2 * maxDim, 0))
                    rotMat = tm.transformations.rotation_matrix(
                        angle=-radians(abs(deg) - 180),
                        direction=(0, 0, 1),
                    )
                    cut = tm.boolean.difference([cut, cut2.apply_transform(rotMat)])

            self.ensureVolume()
            self.solid = tm.boolean.difference([self.solid, cut])

        self.rotate_z(90).rotate_y(90)


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
                angle = 2 * pi * i / n
                x = r * cos(angle)
                y = r * sin(angle)
                points.append((x, y))
            return points

        self.path = path
        self.rad = rad
        segs = self._smoothing_segments(2 * pi * rad)
        polygon = Polygon(circle_polygon_points(segs, rad))
        self.solid = tm.creation.sweep_polygon(polygon, path, validate=True)


class TMTextZ(TMShape):

    def __init__(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        fontName: str,
        api: TMShapeAPI,
    ):
        super().__init__(api)

        jcTol = self.api.tolerance()

        self.txt = txt
        self.fontSize = fontSize
        self.tck = tck
        self.font = fontName

        fontPath = self.api.getFontPath(fontName)
        if fontPath is None:
            fontPath = self.api.getFontPath(None) # Just get some font, hopefully good
            print(f"Can't find font {fontName}, substitude with {fontPath}")

        glyphs_paths = textToGlyphsPaths(
            fontPath, txt, fontSize, dimToSegs=self._smoothing_segments
        )

        text3d: tm.Trimesh = None
        for glyph_paths in glyphs_paths:

            glyph3d: tm.Trimesh = None

            glyph_paths.sort(key=pathBoundsArea, reverse=True)
            for pi, path in enumerate(glyph_paths):
                polygon = Polygon(path)
                isCut = not isPathCounterClockwise(path)
                cutAdj = jcTol if isCut else 0
                extruded = tm.creation.extrude_polygon(
                    polygon,
                    tck + 2 * cutAdj,
                    cap_base=True,
                    cap_top=True,
                    tolerance=1e-5,
                    validate=True,
                ).apply_translation((0, 0, -cutAdj))

                if pi == 0:
                    glyph3d = extruded
                else:
                    if isCut:
                        glyph3d = tm.boolean.difference([glyph3d, extruded])
                    else:
                        glyph3d = tm.boolean.union([glyph3d, extruded])

            if glyph3d is not None:
                text3d = glyph3d if text3d is None else text3d + glyph3d

        if text3d is not None:
            bounds: np.ndarray = text3d.bounds
            xmax, ymax = bounds[1][0], bounds[1][1]
            self.solid = text3d.apply_translation((-xmax / 2, -ymax / 2, 0))
        else:
            print('# WARNING! Text Generation failed!!! ')
            self.solid = tm.creation.box(extents=(fontSize, fontSize, tck), validate=True)

class TMImport(TMShape):
    def __init__(
        self,
        infile: str,
        extrude: float = None,
        api: TMShapeAPI = TMShapeAPI,
    ):
        super().__init__(api)
        assert os.path.isfile(infile) or os.path.isdir(
            infile
        ), f"ERROR: file/directory {infile} does not exist!"
        self.infile = infile

        _, fext = os.path.splitext(infile)

        # 'off', 'tar.bz2', 'xyz', 'bz2', 'dxf', 'svg', 'stl', 'tar.gz', 'json',
        # 'dict', 'dict64', 'obj', 'glb', 'zip', 'ply', 'stl_ascii', 'gltf'
        assert (
            fext.replace('.','') in tm.available_formats()
        ), f"ERROR: file extension {fext} not supported!"

        if fext in [".stl",".glb",".gltf",".obj"]:
            self.solid = tm.load_mesh(infile)
        if fext in [".dxf"]:
            path = tm.load_path(infile)

            # Ensure the loaded file contains paths
            if not isinstance(path, tm.path.Path2D):
                raise ValueError("DXF file does not contain valid 2D paths")

            # Convert paths to polygons (assumes closed paths)
            polygons = path.polygons_full

            # Extrude each polygon (adjust height as needed)
            extruded_solids = [tm.creation.extrude_polygon(poly, extrude) for poly in polygons]

            # Combine extruded solids into one mesh
            self.solid = tm.util.concatenate(extruded_solids)
        
if __name__ == "__main__":
    test_api("trimesh")
