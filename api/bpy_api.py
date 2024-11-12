#!/usr/bin/env python3

from __future__ import annotations
import bpy
import bmesh
import copy
from math import ceil, pi
from mathutils import Vector
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Shape, ShapeAPI, test_api
from api.pylele_utils import (
    dimXY,
    ensureFileExtn,
    isPathCounterClockwise,
    lineSplineXY,
    radians,
    simplifyLineSpline,
)


"""
    Encapsulate Blender implementation specific calls
"""


class BlenderShapeAPI(ShapeAPI):

    def export_stl(self, shape: BlenderShape, path: Union[str, Path]) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        shape.solid.select_set(True)
        bpy.context.view_layer.objects.active = shape.solid
        bpy.ops.export_mesh.stl(
            filepath=ensureFileExtn(path, ".stl"), use_selection=True
        )

    def export_best(self, shape: BlenderShape, path: Union[str, Path]) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        shape.solid.select_set(True)
        bpy.context.view_layer.objects.active = shape.solid
        bpy.ops.export_scene.gltf(
            filepath=ensureFileExtn(path, ".glb"), use_selection=True
        )

    def sphere(self, rad: float) -> BlenderShape:
        return BlenderBall(rad, self)

    def box(self, ln: float, wth: float, ht: float) -> BlenderShape:
        return BlenderBox(ln, wth, ht, self)

    def cone_x(self, ln: float, r1: float, r2: float) -> BlenderShape:
        return BlenderConeX(ln, r1, r2, self).mv(ln / 2, 0, 0)

    def cone_y(self, ln: float, r1: float, r2: float) -> BlenderShape:
        return BlenderConeY(ln, r1, r2, self).mv(0, ln / 2, 0)

    def cone_z(self, ln: float, r1: float, r2: float) -> BlenderShape:
        return BlenderConeZ(ln, r1, r2, self).mv(0, 0, ln / 2)

    def regpoly_extrusion_x(self, ln: float, rad: float, sides: int) -> BlenderShape:
        return BlenderPolyRodX(ln, rad, sides, self)

    def regpoly_extrusion_y(self, ln: float, rad: float, sides: int) -> BlenderShape:
        return BlenderPolyRodY(ln, rad, sides, self)

    def regpoly_extrusion_z(self, ln: float, rad: float, sides: int) -> BlenderShape:
        return BlenderPolyRodZ(ln, rad, sides, self)

    def cylinder_x(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodX(ln, rad, self)

    def cylinder_y(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodY(ln, rad, self)

    def cylinder_z(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodZ(ln, rad, self)

    def polygon_extrusion(
        self, path: list[tuple[float, float]], ht: float
    ) -> BlenderShape:
        return BlenderPolyExtrusionZ(path, ht, self)

    def spline_extrusion(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        ht: float,
    ) -> BlenderShape:
        if ht < 0:
            return BlenderLineSplineExtrusionZ(start, path, abs(ht), self).mv(
                0, 0, -abs(ht)
            )
        return BlenderLineSplineExtrusionZ(start, path, ht, self)

    def spline_revolve(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        deg: float,
    ) -> BlenderShape:
        return BlenderLineSplineRevolveX(start, path, deg, self)

    def regpoly_sweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> BlenderShape:
        return BlenderCirclePolySweep(rad, path, self)

    def text(
        self, txt: str, fontSize: float, tck: float, font: str
    ) -> BlenderShape:
        return BlenderTextZ(txt, fontSize, tck, font, self)


class BlenderShape(Shape):

    # MAX_DIM = 10000 # for max and min dimensions
    REPAIR_MIN_REZ = 0.005
    REPAIR_LOOPS = 2

    def findBounds(self) -> tuple[float, float, float, float, float, float]:
        """
        Returns the bounding box of a Blender object in world space as a tuple:
        (minX, maxX, minY, maxY, minZ, maxZ)

        Parameters:
        obj (bpy.types.Object): The Blender object.

        Returns:
        tuple: A tuple with the bounding box limits (minX, maxX, minY, maxY, minZ, maxZ).
        """
        if self.solid.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
            raise ValueError(
                f"Object type {self.solid.type} does not support bounding boxes."
            )

        # Get the bounding box in local space
        bbox = self.solid.bound_box

        # Convert to world space by applying the object's transformation matrix
        bbox_world = [self.solid.matrix_world @ Vector(corner) for corner in bbox]

        # Extract the min/max values from the bounding box in world space
        min_x = min([v[0] for v in bbox_world])
        max_x = max([v[0] for v in bbox_world])
        min_y = min([v[1] for v in bbox_world])
        max_y = max([v[1] for v in bbox_world])
        min_z = min([v[2] for v in bbox_world])
        max_z = max([v[2] for v in bbox_world])

        return (min_x, max_x, min_y, max_y, min_z, max_z)

    def cut(self, cutter: BlenderShape) -> BlenderShape:
        if cutter is None:
            return self
        bpy.context.view_layer.objects.active = self.solid
        mod = self.solid.modifiers.new(name="Diff", type="BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter.solid
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        return self.repairMesh()

    def dup(self) -> BlenderShape:
        duplicate = copy.copy(self)
        self.solid.select_set(True)
        bpy.context.view_layer.objects.active = self.solid
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action="DESELECT")
        duplicate.solid = bpy.context.object
        duplicate.solid.select_set(True)
        return duplicate

    def extrudeZ(self, tck: float) -> BlenderShape:
        if tck <= 0:
            return self
        bpy.ops.object.select_all(action="DESELECT")
        self.solid.select_set(True)
        # origin = self.solid.location
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.solidify(thickness=tck)
        bpy.ops.object.mode_set(mode="OBJECT")
        # self.solid.location.z = tck
        return self.repairMesh()

    def findNearestEdgeIndex(self, point: tuple[float, float, float]) -> int:
        mesh = self.solid.data
        nearestIdx = -1
        minDist = float("inf")
        pv = Vector(point)
        for edge in mesh.edges:
            v1 = self.solid.matrix_world @ mesh.vertices[edge.vertices[0]].co
            v2 = self.solid.matrix_world @ mesh.vertices[edge.vertices[1]].co
            diff = v2 - v1
            if diff.length == 0:
                continue
            closestPtOnEdge = v1 + diff.normalized() * (
                (pv - v1).dot(diff) / diff.length_squared
            )
            distance = (pv - closestPtOnEdge).length
            if distance < minDist:
                minDist = distance
                nearestIdx = edge.index
        return nearestIdx

    def fillet(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> BlenderShape:
        if rad <= 0:
            return self
        segs = self.segsByDim(rad / 4)
        bpy.context.view_layer.objects.active = self.solid
        if nearestPts is None or len(nearestPts) == 0:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(type="EDGE")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.bevel(offset=rad / 4, segments=segs)
            bpy.ops.object.mode_set(mode="OBJECT")
        else:
            for p in nearestPts:
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(type="EDGE")
                bpy.ops.object.mode_set(mode="OBJECT")
                idx = self.findNearestEdgeIndex(p)
                if idx >= 0:
                    self.solid.data.edges[idx].select = True
                    bpy.ops.object.mode_set(mode="EDIT")
                    bpy.ops.mesh.bevel(offset=rad / 4, segments=segs)
                    bpy.ops.object.mode_set(mode="OBJECT")
        return self.repairMesh()

    def join(self, joiner: BlenderShape) -> BlenderShape:
        if joiner is None:
            return self
        bpy.context.view_layer.objects.active = self.solid
        bpy.ops.object.mode_set(mode="OBJECT")
        mod = self.solid.modifiers.new(name="Union", type="BOOLEAN")
        mod.operation = "UNION"
        mod.object = joiner.solid
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        joiner.remove()
        return self.repairMesh()

    def mirror(self, plane: tuple[bool, bool, bool]) -> BlenderShape:

        cp = copy.copy(self)
        cp.solid.select_set(True)
        bpy.context.view_layer.objects.active = cp.solid
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action="DESELECT")
        dup = bpy.context.object
        dup.select_set(True)

        # shift to one side to avoid cross mirroring
        shift = (
            self.solid.dimensions.x if plane[0] else 0,
            self.solid.dimensions.y if plane[1] else 0,
            self.solid.dimensions.z if plane[2] else 0,
        )
        # dup.location = dup.location + shift
        bpy.ops.transform.translate(
            value=shift,
            use_accurate=True,
            use_automerge_and_split=True,
        )

        bpy.context.view_layer.objects.active = dup
        mirror = bpy.data.objects.new("MirrorAtOrigin", None)
        mirror.location = (0, 0, 0)
        mod = dup.modifiers.new(name="Mirror", type="MIRROR")
        mod.mirror_object = mirror
        mod.use_axis = plane
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        cp.solid = dup

        cp = cp.halfByPlane(plane)  # cut out the original half

        # recover from shift
        # cp.solid.location = cp.solid.location + shift
        dup.select_set(True)
        bpy.ops.transform.translate(
            value=shift,
            use_accurate=True,
            use_automerge_and_split=True,
        )
        return cp.repairMesh()

    def mirror(self) -> BlenderShape:
        return self.mirror((False, True, False))

    def mv(self, x: float, y: float, z: float) -> BlenderShape:
        if x == 0 and y == 0 and z == 0:
            return self
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.translate(
            value=(x, y, z),
            use_accurate=True,
            use_automerge_and_split=True,
        )
        return self

    def remove(self) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        self.solid.select_set(True)
        bpy.ops.object.delete()

    def repairMesh(self) -> BlenderShape:
        minRez = self.REPAIR_MIN_REZ
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bm = bmesh.from_edit_mesh(self.solid.data)
        non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
        loop = 0
        while non_manifold_edges and loop < self.REPAIR_LOOPS:
            print(
                f"Loop {loop}: found {len(non_manifold_edges)} non-manifold edges. Attempting to fix..."
            )
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.remove_doubles(
                threshold=minRez,
                use_sharp_edge_from_normals=True,
                use_unselected=True,
            )
            bpy.ops.mesh.fill_holes(sides=0)  # 'sides=0' fills all holes
            bpy.ops.mesh.dissolve_degenerate(threshold=minRez)
            bpy.ops.mesh.delete_loose(use_faces=True, use_edges=True, use_verts=True)
            bpy.ops.mesh.normals_make_consistent(inside=True)
            bm = bmesh.from_edit_mesh(self.solid.data)
            non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
            minRez *= 1.4
            loop += 1
        bpy.ops.object.mode_set(mode="OBJECT")
        return self

    def rotate_x(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.rotate(
            value=radians(ang),  # Rotation angle in radians
            orient_axis="X",  # Rotation axis
            constraint_axis=(True, False, False),  # Constrain to X-axis
            orient_type="GLOBAL",  # Orientation type
            use_accurate=True,
        )
        return self

    def rotate_y(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.rotate(
            value=radians(ang),  # Rotation angle in radians
            orient_axis="Y",  # Rotation axis
            constraint_axis=(False, True, False),  # Constrain to Y-axis
            orient_type="GLOBAL",  # Orientation type
            use_accurate=True,
        )
        return self

    def rotate_z(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.rotate(
            value=radians(ang),  # Rotation angle in radians
            orient_axis="Z",  # Rotation axis
            constraint_axis=(False, False, True),  # Constrain to Z-axis
            orient_type="GLOBAL",  # Orientation type
            use_accurate=True,
        )
        return self

    def scale(self, x: float, y: float, z: float) -> BlenderShape:
        if x == 1 and y == 1 and z == 1:
            return self
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.context.scene.tool_settings.transform_pivot_point = "CURSOR"
        bpy.ops.transform.resize(
            value=(x, y, z),
            constraint_axis=(True, True, True),
            use_accurate=True,
        )
        return self.repairMesh()

    def show(self):
        self.updateMesh()
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)

    def segsByDim(self, dim: float) -> int:
        return ceil(abs(dim) ** 0.5 * self.api.fidelity.smoothing_segments())


class BlenderBall(BlenderShape):
    def __init__(
        self,
        rad: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        segs = self.segsByDim(2 * pi * rad)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=segs, ring_count=segs)
        self.solid = bpy.context.object


class BlenderBox(BlenderShape):
    def __init__(
        self,
        ln: float,
        wth: float,
        ht: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        bpy.ops.mesh.primitive_cube_add(size=1)
        self.solid = bpy.context.object
        self.scale(ln, wth, ht)


class BlenderConeZ(BlenderShape):
    def __init__(
        self,
        ln: float,
        r1: float,
        r2: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        verts = self.segsByDim(2 * pi * max(r1, r2))
        bpy.ops.mesh.primitive_cone_add(
            radius1=r1, radius2=r2, depth=ln, vertices=verts
        )
        self.solid = bpy.context.object


class BlenderConeX(BlenderShape):
    def __init__(
        self,
        ln: float,
        r1: float,
        r2: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        self.solid = BlenderConeZ(ln, r1, r2, api).rotate_y(90).solid


class BlenderConeY(BlenderShape):
    def __init__(
        self,
        ln: float,
        r1: float,
        r2: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        self.solid = BlenderConeZ(ln, r1, r2, api).rotate_x(90).solid


class BlenderPolyRodZ(BlenderShape):
    def __init__(
        self,
        ln: float,
        rad: float,
        sides: int,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=ln, vertices=sides)
        self.solid = bpy.context.object


class BlenderPolyRodX(BlenderShape):
    def __init__(
        self,
        ln: float,
        rad: float,
        sides: int,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        self.solid = BlenderPolyRodZ(ln, rad, sides, api).rotate_y(90).solid


class BlenderPolyRodY(BlenderShape):
    def __init__(
        self,
        ln: float,
        rad: float,
        sides: int,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        self.solid = BlenderPolyRodZ(ln, rad, sides, api).rotate_x(90).solid


class BlenderRodZ(BlenderShape):
    def __init__(
        self,
        ln: float,
        rad: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        verts = self.segsByDim(2 * pi * rad)
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=ln, vertices=verts)
        self.solid = bpy.context.object


class BlenderRodX(BlenderShape):
    def __init__(
        self,
        ln: float,
        rad: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        self.solid = BlenderRodZ(ln, rad, api).rotate_y(90).solid


class BlenderRodY(BlenderShape):
    def __init__(
        self,
        ln: float,
        rad: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        self.solid = BlenderRodZ(ln, rad, api).rotate_x(90).solid


class BlenderRod3D(BlenderShape):
    def __init__(
        self,
        start: tuple[float, float, float],
        stop: tuple[float, float, float],
        rad: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        segs = self.segsByDim(2 * pi * rad)
        startPt = Vector(start)
        endPt = Vector(stop)
        vec = endPt - startPt
        length = vec.length
        midpoint = (startPt + endPt) / 2
        bpy.ops.mesh.primitive_cylinder_add(
            radius=rad, depth=length, location=midpoint, vertices=segs
        )
        cylinder = bpy.context.object
        z_axis = Vector((0, 0, 1))
        rotation_quat = z_axis.rotation_difference(vec)
        cylinder.rotation_mode = "QUATERNION"
        cylinder.rotation_quaternion = rotation_quat
        bpy.context.view_layer.update()
        self.solid = cylinder


class BlenderPolyExtrusionZ(BlenderShape):
    def __init__(
        self,
        path: list[tuple[float, float]],
        ht: float,
        api: BlenderShapeAPI,
        checkWinding: bool = True,
    ):
        super().__init__(api)
        if checkWinding and not isPathCounterClockwise(path):
            path.reverse()

        mesh = bpy.data.meshes.new(name="Polygon")
        bpy.ops.object.select_all(action="DESELECT")
        bm = bmesh.new()
        for v in path:
            bm.verts.new((v[0], v[1], 0))
        bm.faces.new(bm.verts)
        bm.to_mesh(mesh)
        self.solid = bpy.data.objects.new(name="Polygon_Object", object_data=mesh)
        bpy.context.collection.objects.link(self.solid)
        mesh.update()

        bpy.context.view_layer.objects.active = self.solid
        self.extrudeZ(ht)


class BlenderLineSplineExtrusionZ(BlenderShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        ht: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        # optimization:instead of detecting winding direction of polypath, detect the winding direction of input line-spline
        polyPath = lineSplineXY(start, path, self.segsByDim)
        if not isPathCounterClockwise(simplifyLineSpline(start, path)):
            polyPath.reverse()
        polyExt = BlenderPolyExtrusionZ(polyPath, ht, api, checkWinding=False)
        self.solid = polyExt.solid


class BlenderLineSplineRevolveX(BlenderShape):
    def __init__(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, ...]]],
        deg: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        polyPath = lineSplineXY(start, path, self.segsByDim)

        mesh = bpy.data.meshes.new(name="Polygon")
        bpy.ops.object.select_all(action="DESELECT")
        bm = bmesh.new()
        for v in polyPath:
            bm.verts.new((v[0], v[1], 0))
        bm.faces.new(bm.verts)
        bm.to_mesh(mesh)
        polyObj = bpy.data.objects.new(name="Polygon_Object", object_data=mesh)

        _, dimY = dimXY(start, path)
        segs = self.segsByDim(abs(2 * pi * dimY * min(abs(deg), 360) / 360))
        bpy.ops.object.select_all(action="DESELECT")
        self.solid = polyObj
        bpy.context.collection.objects.link(self.solid)
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        # HACK: spin only produce correct mesh when axis and deg are opposite sign, so forcing it here
        bpy.ops.mesh.spin(axis=(1, 0, 0), angle=radians(-abs(deg)), steps=segs)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        if deg < 0:  # HACK: since spin hack above, mirror if deg is negative
            self.solid = self.mirror((False, False, True)).solid

        self.repairMesh()


class BlenderCirclePolySweep(BlenderShape):
    def __init__(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
        api: BlenderShapeAPI,
    ):
        super().__init__(api)

        # Deselect all existing objects
        bpy.ops.object.select_all(action="DESELECT")

        if len(path) >= 2:

            # Create a curve object for the path
            curve_data = bpy.data.curves.new("sweep_path", type="CURVE")
            curve_data.dimensions = "3D"
            spline = curve_data.splines.new(type="POLY")
            spline.points.add(len(path) - 1)

            # Set the path points
            for i, (x, y, z) in enumerate(path):
                spline.points[i].co = (x, y, z, 1)

            # Create a curve object in the scene
            path_obj = bpy.data.objects.new("SweepPath", curve_data)
            bpy.context.collection.objects.link(path_obj)

            # Create a circle to be used as the profile (bevel object)
            bpy.ops.curve.primitive_bezier_circle_add(radius=rad)
            circle_obj = bpy.context.object
            circle_obj.name = "CircleProfile"

            # Assign the circle as the bevel object for the path
            path_obj.data.bevel_object = circle_obj
            path_obj.data.use_fill_caps = True  # To cap the ends

            # Set the resolution of the circle and the path
            path_obj.data.bevel_resolution = self.segsByDim(2 * pi * rad)
            path_obj.data.resolution_u = 1

            # Important: Set curve bevel mode and size
            path_obj.data.bevel_mode = "OBJECT"  # Use the object (circle) as a bevel
            path_obj.data.bevel_depth = 0.0  # Disable default bevel depth

            # Optionally, hide the profile object (Circle)
            circle_obj.hide_set(True)

            bpy.ops.object.mode_set(mode="OBJECT")
            # Make the path object active and selected for conversion
            bpy.context.view_layer.objects.active = path_obj
            path_obj.select_set(True)
            bpy.ops.object.convert(target="MESH")

            # Update the scene to show the result
            bpy.context.view_layer.update()

        self.solid = path_obj
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

        self.repairMesh()


class BlenderTextZ(BlenderShape):
    def __init__(
        self, txt: str, fontSize: float, tck: float, fontName: str, api: BlenderShapeAPI
    ):
        super().__init__(api)
        bpy.ops.object.text_add()
        self.solid = bpy.context.object
        self.solid.data.body = txt
        self.solid.data.size = fontSize
        fontPath = api.getFontPath(fontName)
        if fontPath is not None:
            font = bpy.data.fonts.load(filepath=fontPath)
            self.solid.data.font = font
        else:
            print("WARN: font ${fontName} not found, use blender default")
        self.extrudeZ(tck)
        (minX, maxX, minY, maxY, _, _) = self.findBounds()
        self.mv(-(minX + maxX) / 2, -(minY + maxY) / 2, tck)
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")


if __name__ == "__main__":
    test_api("blender")
