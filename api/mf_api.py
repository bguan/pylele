#!/usr/bin/env python3

from __future__ import annotations
import copy
from math import pi, ceil
from manifold3d import Manifold, CrossSection, FillRule
import numpy as np
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import ShapeAPI, Shape, test_api
from api.pylele_utils import dimXY, ensureFileExtn, lineSplineXY


"""
    Encapsulate Manifold3d implementation specific calls
"""


class MFShapeAPI(ShapeAPI):

    def exportSTL(self, shape: MFShape, path: Union[str, Path]) -> None:

        def calculate_normals(vertices, faces):
            # Vertices shape: (vn, 3), Faces shape: (fn, 3)

            # Get the vertices for each face using the face indices
            v1 = vertices[faces[:, 0]]
            v2 = vertices[faces[:, 1]]
            v3 = vertices[faces[:, 2]]

            # Calculate two edge vectors for each triangle
            edge1 = v2 - v1
            edge2 = v3 - v1

            # Compute the cross product (normal) of each triangle's edge vectors
            normals = np.cross(edge1, edge2)

            # Normalize the resulting normals
            normal_magnitudes = np.linalg.norm(normals, axis=1).reshape(-1, 1)
            normalized_normals = normals / np.where(
                normal_magnitudes == 0, 1, normal_magnitudes
            )  # Avoid divide by zero
            return normalized_normals

        def face_idxs_to_vertices(vertices, faces):
            """
            Translate face indices to face vertices.

            Parameters:
            - vertices: numpy array of shape (vn, 3), representing vertex coordinates.
            - faces: numpy array of shape (fn, 3), representing indices of the vertices that form each triangular face.

            Returns:
            - face_vertices: numpy array of shape (fn, 3, 3) where each face is represented by its corresponding vertex coordinates.
            """
            # Use numpy advanced indexing to map face indices to actual vertex coordinates
            face_vertices = vertices[faces]
            return face_vertices

        # define a numpy datatype for the data section of a binary STL file
        # everything in STL is always Little Endian
        # this works natively on Little Endian systems, but blows up on Big Endians
        # so we always specify byteorder
        stl_dtype = np.dtype(
            [
                ("normals", "<f4", (3)),
                ("vertices", "<f4", (3, 3)),
                ("attributes", "<u2"),
            ]
        )
        # define a numpy datatype for the header of a binary STL file
        stl_dtype_header = np.dtype([("header", np.void, 80), ("face_count", "<u4")])

        obj_mesh = shape.getImplSolid().to_mesh()
        vertices = obj_mesh.vert_properties
        face_tri_idxs = obj_mesh.tri_verts
        face_normals = calculate_normals(vertices, face_tri_idxs)

        header = np.zeros(1, dtype=stl_dtype_header)
        header["face_count"] = len(face_tri_idxs)
        export = header.tobytes()
        packed = np.zeros(len(face_tri_idxs), dtype=stl_dtype)
        packed["normals"] = face_normals
        packed["vertices"] = face_idxs_to_vertices(vertices, face_tri_idxs)
        export += packed.tobytes()

        # Open a file in binary write mode and write the data to it
        with open(ensureFileExtn(path, ".stl"), "wb") as file:
            file.write(export)

    def exportBest(self, shape: MFShape, path: Union[str, Path]) -> None:
        self.exportSTL(shape, path)

    def genBall(self, rad: float) -> MFShape:
        return MFBall(rad, self)

    def genBox(self, l: float, wth: float, ht: float) -> MFShape:
        return MFBox(l, wth, ht, self)

    def genConeX(self, l: float, r1: float, r2: float) -> MFShape:
        return MFConeZ(l, r1, r2, None, self).rotateY(90)

    def genConeY(self, l: float, r1: float, r2: float) -> MFShape:
        return MFConeZ(l, r1, r2, None, self).rotateX(-90)

    def genConeZ(self, l: float, r1: float, r2: float) -> MFShape:
        return MFConeZ(l, r1, r2, None, self)

    def genPolyRodX(self, l: float, rad: float, sides: int) -> MFShape:
        return MFRodZ(l, rad, sides, self).rotateY(90)

    def genPolyRodY(self, l: float, rad: float, sides: int) -> MFShape:
        return MFRodZ(l, rad, sides, self).rotateX(90)

    def genPolyRodZ(self, l: float, rad: float, sides: int) -> MFShape:
        return MFRodZ(l, rad, sides, self)

    def genRodX(self, l: float, rad: float) -> MFShape:
        return MFRodZ(l, rad, None, self).rotateY(90)

    def genRodY(self, l: float, rad: float) -> MFShape:
        return MFRodZ(l, rad, None, self).rotateX(90)

    def genRodZ(self, l: float, rad: float) -> MFShape:
        return MFRodZ(l, rad, None, self)

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> MFShape:
        return MFPolyExtrusionZ(path, ht, self)

    def genLineSplineExtrusionZ(
        self,
        start: tuple[float, float],
        path: list[
            tuple[float, float] | list[tuple[float, float, float, float, float]]
        ],
        ht: float,
    ) -> MFShape:
        if ht < 0:
            return MFLineSplineExtrusionZ(start, path, abs(ht), self).mv(0, 0, -abs(ht))
        return MFLineSplineExtrusionZ(start, path, ht, self)

    def genLineSplineRevolveX(
        self,
        start: tuple[float, float],
        path: list[
            tuple[float, float] | list[tuple[float, float, float, float, float]]
        ],
        deg: float,
    ) -> MFShape:
        return MFLineSplineRevolveX(start, path, deg, self)

    def genCirclePolySweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> MFShape:
        return MFCirclePolySweep(rad, path, self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> MFShape:
        return MFTextZ(txt, fontSize, tck, font, self)

    def getJoinCutTol(self) -> float:
        return self.implementation.joinCutTol()


class MFShape(Shape):

    def getAPI(self) -> MFShapeAPI:
        return self.api

    def getImplSolid(self) -> Manifold:
        return self.solid

    def segsByDim(self, dim: float) -> int:
        return ceil(abs(dim) ** 0.5 * self.api.fidelity.smoothingSegments())

    def cut(self, cutter: MFShape) -> MFShape:
        if cutter is None or cutter.solid is None:
            return self
        self.solid = self.solid - cutter.solid
        return self

    def dup(self) -> MFShape:
        duplicate = copy.copy(self)
        duplicate.solid = Manifold.compose(
            self.solid.decompose()
        )  # TODO find better impl
        return duplicate

    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> MFShape:
        print(
            "Manifold: filletByNearestEdges(...) not implemented yet.", file=sys.stderr
        )
        return self

    def join(self, joiner: MFShape) -> MFShape:
        if joiner is None or joiner.solid is None:
            return self
        self.solid = self.solid + joiner.solid
        return self

    def mirrorXZ(self) -> MFShape:
        dup = copy.copy(self)
        dup.solid = self.solid.mirror((0, 1, 0))
        return dup

    def mv(self, x: float, y: float, z: float) -> MFShape:
        if x == 0 and y == 0 and z == 0:
            return self
        self.solid = self.solid.translate((x, y, z))
        return self

    def remove(self):
        pass

    def rotateX(self, ang: float) -> MFShape:
        self.solid = self.solid.rotate((ang, 0, 0))
        return self

    def rotateY(self, ang: float) -> MFShape:
        self.solid = self.solid.rotate((0, ang, 0))
        return self

    def rotateZ(self, ang: float) -> MFShape:
        self.solid = self.solid.rotate((0, 0, ang))
        return self

    def scale(self, x: float, y: float, z: float) -> MFShape:
        if x == 1 and y == 1 and z == 1:
            return self
        self.solid = self.solid.scale((x, y, z))
        return self

    def show(self):
        pass


class MFBall(MFShape):
    def __init__(self, rad: float, api: MFShapeAPI):
        super().__init__(api)
        segs = self.segsByDim(2 * pi * rad)
        self.solid = Manifold.sphere(rad, circular_segments=segs)


class MFBox(MFShape):
    def __init__(self, l: float, wth: float, ht: float, api: MFShapeAPI):
        super().__init__(api)
        self.ln = l
        self.wth = wth
        self.ht = ht
        self.solid = Manifold.cube((l, wth, ht)).translate((-l / 2, -wth / 2, -ht / 2))


class MFConeZ(MFShape):
    def __init__(
        self,
        l: float,
        r1: float,
        r2: float,
        sides: float,
        api: MFShapeAPI,
    ):
        super().__init__(api)
        segs = sides if sides is not None else self.segsByDim(2 * pi * max(r1, r2))
        self.solid = Manifold.cylinder(l, r1, r2, circular_segments=segs)


class MFPolyExtrusionZ(MFShape):
    def __init__(self, path: list[tuple[float, float]], tck: float, api: MFShapeAPI):
        super().__init__(api)
        polygon = CrossSection([path], FillRule.EvenOdd)
        self.solid = Manifold.extrude(polygon, tck)


class MFRodZ(MFShape):
    def __init__(self, l: float, rad: float, sides: float, api: MFShapeAPI):
        super().__init__(api)
        segs = sides if sides is not None else self.segsByDim(2 * pi * rad)
        self.solid = Manifold.cylinder(l, rad, circular_segments=segs).translate(
            (0, 0, -l / 2)
        )


# draw mix of straight lines from pt to pt, or draw spline with [(x,y,dx,dy), ...], then extrude on Z-axis
class MFLineSplineExtrusionZ(MFShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[
            tuple[float, float] | list[tuple[float, float, float, float, float]]
        ],
        ht: float,
        api: MFShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.ht = ht
        approx_curve_path = lineSplineXY(start, path, self.segsByDim)
        polygon = CrossSection([approx_curve_path], FillRule.EvenOdd)
        self.solid = Manifold.extrude(polygon, ht)


class MFLineSplineRevolveX(MFShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[
            Union[tuple[float, float], list[tuple[float, float, float, float, float]]]
        ],
        deg: float,
        api: MFShapeAPI,
    ):
        super().__init__(api)
        _, dimY = dimXY(start, path)
        neg_deg = deg < 0
        deg = -deg if neg_deg else deg
        segs = ceil(self.segsByDim(2 * pi * dimY) * deg / 360.0)
        self.path = path
        self.deg = deg
        approx_curve_path = lineSplineXY(start, path, self.segsByDim)
        approx_curve_path = [(y, x) for x, y in approx_curve_path]  # swap X, Y
        polygon = CrossSection([approx_curve_path], FillRule.EvenOdd)
        solid = Manifold.revolve(polygon, revolve_degrees=deg, circular_segments=segs)
        solid = solid.rotate((0, 0, 90)).rotate((0, 90, 0))
        if neg_deg:
            solid = solid.mirror((0, 0, 1))
        self.solid = solid


class MFCirclePolySweep(MFShape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
        api: MFShapeAPI,
    ):
        super().__init__(api)
        self.path = path
        self.rad = rad
        segs = self.segsByDim(2 * pi * rad)
        sweep_shape = None
        for i, (x, y, z) in enumerate(path):
            if i == 0:
                last_ball = Manifold.sphere(rad, circular_segments=segs).translate(
                    (x, y, z)
                )
                sweep_shape = last_ball
            else:
                ball = Manifold.sphere(rad, circular_segments=segs).translate((x, y, z))
                hull2balls = (last_ball + ball).hull()
                sweep_shape += hull2balls
                last_ball = ball
        self.solid = sweep_shape


class MFTextZ(MFShape):

    def __init__(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        font: str,
        api: MFShapeAPI,
    ):
        print("Manifold: MFTextZ(...) not implemented yet.", file=sys.stderr)

        super().__init__(api)

        self.txt = txt
        self.fontSize = fontSize
        self.tck = tck
        self.font = font
        l = 0.5 * fontSize * len(txt)
        wth = fontSize
        ht = tck
        self.solid = Manifold.cube((l, wth, ht)).translate((-l / 2, -wth / 2, 0))


if __name__ == "__main__":
    test_api("manifold")
