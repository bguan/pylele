from __future__ import annotations
from pathlib import Path
import bpy
import copy
import bmesh
import math
from fontTools.ttLib import TTFont
from mathutils import Vector
import numpy as np
from pylele_api import Shape, ShapeAPI, Fidelity, Implementation
from pylele_utils import descreteBezierChain, dimXY, ensureFileExtn, isPathCounterClockwise, radians, simplifyLineSpline, superGradient
from typing import Any, Union

class BlenderShapeAPI(ShapeAPI):

    def __init__(self, fidel: Fidelity):
        super().__init__()
        self.fidelity = fidel

    def getFidelity(self) -> Fidelity:
        return self.fidelity
    
    def getImplementation(self) -> Implementation:
        return Implementation.BLENDER

    def setFidelity(self, fidel: Fidelity) -> None:
        self.fidelity = fidel

    def exportSTL(self, shape: BlenderShape, path: Union[str, Path]) -> None:
        bpy.ops.object.select_all(action='DESELECT')
        shape.solid.select_set(True)
        bpy.context.view_layer.objects.active = shape.solid
        bpy.ops.export_mesh.stl(filepath=ensureFileExtn(path,'.stl'), use_selection=True)

    def exportBest(self, shape: BlenderShape, path: Union[str, Path]) -> None:
        bpy.ops.object.select_all(action='DESELECT')
        shape.solid.select_set(True)
        bpy.context.view_layer.objects.active = shape.solid
        bpy.ops.export_scene.gltf(filepath=ensureFileExtn(path,'.glb'), use_selection=True)

    def genBall(self, rad: float) -> BlenderShape:
        return BlenderBall(rad, self)

    def genBox(self, ln: float, wth: float, ht: float) -> BlenderShape:
        return BlenderBox(ln, wth, ht, self)

    def genConeX(self, ln: float, r1: float, r2: float) -> BlenderShape:
        return BlenderConeX(ln, r1, r2, self).mv(ln/2, 0, 0)

    def genConeY(self, ln: float, r1: float, r2: float) -> BlenderShape:
        return BlenderConeY(ln, r1, r2, self).mv(0, ln/2, 0)

    def genConeZ(self, ln: float, r1: float, r2: float) -> BlenderShape:
        return BlenderConeZ(ln, r1, r2, self).mv(0, 0, ln/2)

    def genPolyRodX(self, ln: float, rad: float, sides: int) -> BlenderShape:
        return BlenderPolyRodX(ln, rad, sides, self)

    def genPolyRodY(self, ln: float, rad: float, sides: int) -> BlenderShape:
        return BlenderPolyRodY(ln, rad, sides, self)

    def genPolyRodZ(self, ln: float, rad: float, sides: int) -> BlenderShape:
        return BlenderPolyRodZ(ln, rad, sides, self)

    def genRodX(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodX(ln, rad, self)

    def genRodY(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodY(ln, rad, self)

    def genRodZ(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodZ(ln, rad, self)

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> BlenderShape:
        return BlenderPolyExtrusionZ(path, ht, self)

    def genLineSplineExtrusionZ(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, ...]]], 
            ht: float,
        ) -> BlenderShape:
        return BlenderLineSplineExtrusionZ(start, path, ht, self)
    
    def genLineSplineRevolveX(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, ...]]], 
            deg: float,
        ) -> BlenderShape:
        return BlenderLineSplineRevolveX(start, path, deg, self)
    
    def genCirclePolySweep(self, rad: float, path: list[tuple[float, float, float]]) -> BlenderShape:
        return BlenderCirclePolySweep(rad, path, self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> BlenderShape:
        return BlenderTextZ(txt, fontSize, tck, font, self)

    def getJoinCutTol(self) -> float:
        return Implementation.BLENDER.joinCutTol()

class BlenderShape(Shape):

    REPAIR_MIN_REZ = 0.0001
    REPAIR_LOOPS = 2
    
    def __init__(self, api: BlenderShapeAPI):
        super().__init__()
        self.api = api
        self.solid = None

    def getAPI(self) -> BlenderShapeAPI:
        return self.api

    def getImplSolid(self) -> Any:
        return self.solid
    
    def cut(self, cutter: BlenderShape) -> BlenderShape:
        if cutter is None:
            return self
        bpy.context.view_layer.objects.active = self.solid
        mod = self.solid.modifiers.new(name="Diff", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter.solid
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        return self.repairMesh()

    def dup(self) -> BlenderShape:
        duplicate = copy.copy(self)
        self.solid.select_set(True)
        bpy.context.view_layer.objects.active = self.solid
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action='DESELECT')
        duplicate.solid = bpy.context.object
        duplicate.solid.select_set(True)
        return duplicate
    
    def extrudeZ(self, tck: float) -> BlenderShape:
        if tck <= 0:
            return self
        bpy.ops.object.select_all(action='DESELECT')
        self.solid.select_set(True)
        # origin = self.solid.location
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.solidify(thickness=tck)
        bpy.ops.object.mode_set(mode='OBJECT')
        # self.solid.location.z = tck
        return self.repairMesh()

    def findNearestEdgeIndex(self, point: tuple[float, float, float]) -> int:
        mesh = self.solid.data
        nearestIdx = -1
        minDist = float('inf')
        pv = Vector(point)
        for edge in mesh.edges:
            v1 = self.solid.matrix_world @ mesh.vertices[edge.vertices[0]].co
            v2 = self.solid.matrix_world @ mesh.vertices[edge.vertices[1]].co
            diff = v2 - v1
            if diff.length == 0:
                continue
            closestPtOnEdge = v1 \
                + diff.normalized() * ((pv - v1).dot(diff) / diff.length_squared)
            distance = (pv - closestPtOnEdge).length
            if distance < minDist:
                minDist = distance
                nearestIdx = edge.index
        return nearestIdx

    def filletByNearestEdges(self, 
        nearestPts: list[tuple[float, float, float]], 
        rad: float,
    ) -> BlenderShape:
        if rad <= 0:
            return self
        segs = self.segsByDim(rad/4)
        bpy.context.view_layer.objects.active = self.solid
        if nearestPts is None or len(nearestPts) == 0:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bevel(offset=rad/4, segments=segs)
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            for p in nearestPts:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(type="EDGE")
                bpy.ops.object.mode_set(mode='OBJECT')
                idx = self.findNearestEdgeIndex(p)
                if idx >= 0:
                    self.solid.data.edges[idx].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.bevel(offset=rad/4, segments=segs)
                    bpy.ops.object.mode_set(mode='OBJECT')
        return self.repairMesh()

    def join(self, joiner: BlenderShape) -> BlenderShape:
        if joiner is None:
            return self
        bpy.context.view_layer.objects.active = self.solid
        bpy.ops.object.mode_set(mode='OBJECT')
        mod = self.solid.modifiers.new(name="Union", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.object = joiner.solid
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        joiner.remove()
        return self.repairMesh()
    

    # draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
    def lineSplineXY(
        self,
        start: tuple[float, float],
        lineSpline: list[tuple[float, float] | list[tuple[float, ...]]],
    ) -> list[tuple[float, float]]:
        
        lastX, lastY = start
        polyPath = [start]
        for p_or_s in lineSpline:
            if isinstance(p_or_s, tuple):
                # a point so draw line
                x, y = p_or_s
                polyPath.append((x, y))
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
                polyPath.extend(curvePts)
                lastX, lastY = spline[-1][0:2]

        return polyPath


    def mirror(self, plane: tuple[bool, bool, bool]) -> BlenderShape:

        cp = copy.copy(self)
        cp.solid.select_set(True)
        bpy.context.view_layer.objects.active = cp.solid
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action='DESELECT')
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
        mod = dup.modifiers.new(name="Mirror", type='MIRROR')
        mod.mirror_object = mirror
        mod.use_axis = plane
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        cp.solid = dup

        cp = cp.halfByPlane(plane) # cut out the original half

        # recover from shift
        # cp.solid.location = cp.solid.location + shift
        dup.select_set(True)
        bpy.ops.transform.translate(
            value=shift,
            use_accurate=True,
            use_automerge_and_split=True,
        )
        return cp.repairMesh()

    def mirrorXZ(self) -> BlenderShape:
        return self.mirror((False, True, False))

    
    def mv(self, x: float, y: float, z: float) -> BlenderShape:
        if x == 0 and y == 0 and z == 0:
            return self
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.translate(
            value=(x, y, z),
            use_accurate=True,
            use_automerge_and_split=True,
        )
        return self

    def remove(self) -> None:
        bpy.ops.object.select_all(action='DESELECT')
        self.solid.select_set(True)
        bpy.ops.object.delete()
        
    def repairMesh(self) -> BlenderShape:
        minRez = self.REPAIR_MIN_REZ
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bm = bmesh.from_edit_mesh(self.solid.data)
        non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
        loop = 0
        while non_manifold_edges and loop < self.REPAIR_LOOPS:
            print(f"Loop {loop}: found {len(non_manifold_edges)} non-manifold edges. Attempting to fix...")
            bpy.ops.mesh.select_all(action='DESELECT')
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
        bpy.ops.object.mode_set(mode='OBJECT')
        return self
        
    def rotateX(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.rotate(
            value=math.radians(ang),     # Rotation angle in radians
            orient_axis='X',             # Rotation axis
            constraint_axis=(True, False, False),  # Constrain to X-axis
            orient_type='GLOBAL',        # Orientation type
            use_accurate=True,
        )
        return self

    def rotateY(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.rotate(
            value=math.radians(ang),     # Rotation angle in radians
            orient_axis='Y',             # Rotation axis
            constraint_axis=(False, True, False),  # Constrain to Y-axis
            orient_type='GLOBAL',        # Orientation type
            use_accurate=True,
        )
        return self

    def rotateZ(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.transform.rotate(
            value=math.radians(ang),     # Rotation angle in radians
            orient_axis='Z',             # Rotation axis
            constraint_axis=(False, False, True),  # Constrain to Z-axis
            orient_type='GLOBAL',        # Orientation type
            use_accurate=True,
        )
        return self

    def scale(self, x: float, y: float, z: float) -> BlenderShape:
        if x == 1 and y == 1 and z == 1:
            return self
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.context.scene.cursor.location = (0,0,0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
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
        return math.ceil(math.sqrt(abs(dim)) * self.api.fidelity.smoothingSegments())

class BlenderBall(BlenderShape):
    def __init__(self, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        segs = self.segsByDim(rad)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=segs, ring_count=segs)
        self.solid = bpy.context.object

class BlenderBox(BlenderShape):
    def __init__(self, ln: float, wth: float, ht: float, api: BlenderShapeAPI):
        super().__init__(api)
        bpy.ops.mesh.primitive_cube_add(size=1)
        self.solid = bpy.context.object
        self.scale(ln, wth, ht)


class BlenderConeZ(BlenderShape):
    def __init__(self, ln: float, r1: float, r2: float, api: BlenderShapeAPI):
        super().__init__(api)
        verts = self.segsByDim(max(r1, r2))
        bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=ln, vertices=verts)
        self.solid = bpy.context.object


class BlenderConeX(BlenderShape):
    def __init__(self, ln: float, r1: float, r2: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.solid = BlenderConeZ(ln, r1, r2, api).rotateY(90).solid


class BlenderConeY(BlenderShape):
    def __init__(self, ln: float, r1: float, r2: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.solid = BlenderConeZ(ln, r1, r2, api).rotateX(90).solid


class BlenderPolyRodZ(BlenderShape):
    def __init__(self, ln: float, rad: float, sides: int, api: BlenderShapeAPI):
        super().__init__(api)
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=ln, vertices=sides)
        self.solid = bpy.context.object


class BlenderPolyRodX(BlenderShape):
    def __init__(self, ln: float, rad: float, sides:int, api: BlenderShapeAPI):
        super().__init__(api)
        self.solid = BlenderPolyRodZ(ln, rad, sides, api).rotateY(90).solid


class BlenderPolyRodY(BlenderShape):
    def __init__(self, ln: float, rad: float, sides: int, api: BlenderShapeAPI):
        super().__init__(api)
        self.solid = BlenderPolyRodZ(ln, rad, sides, api).rotateX(90).solid


class BlenderRodZ(BlenderShape):
    def __init__(self, ln: float, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        verts = self.segsByDim(rad)
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=ln, vertices=verts)
        self.solid = bpy.context.object


class BlenderRodX(BlenderShape):
    def __init__(self, ln: float, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.solid = BlenderRodZ(ln, rad, api).rotateY(90).solid


class BlenderRodY(BlenderShape):
    def __init__(self, ln: float, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.solid = BlenderRodZ(ln, rad, api).rotateX(90).solid


class BlenderRod3D(BlenderShape):
    def __init__(self, 
        start: tuple[float, float, float], 
        stop: tuple[float, float, float],
        rad: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        segs = self.segsByDim(rad)
        startPt = Vector(start)
        endPt = Vector(stop)
        vec = endPt - startPt
        length = vec.length
        midpoint = (startPt + endPt) / 2
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=length, location=midpoint, vertices=segs)
        cylinder = bpy.context.object
        z_axis = Vector((0, 0, 1))
        rotation_quat = z_axis.rotation_difference(vec)
        cylinder.rotation_mode = 'QUATERNION'
        cylinder.rotation_quaternion = rotation_quat
        bpy.context.view_layer.update()
        self.solid = cylinder

class BlenderPolyExtrusionZ(BlenderShape):
    def __init__(self, path: list[tuple[float, float]], ht: float, api: BlenderShapeAPI, checkWinding: bool = True):
        super().__init__(api)
        if checkWinding and not isPathCounterClockwise(path):
            path.reverse()
        
        mesh = bpy.data.meshes.new(name="Polygon")
        bpy.ops.object.select_all(action='DESELECT')
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
        polyPath = self.lineSplineXY(start, path)
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
        polyPath = self.lineSplineXY(start, path)

        mesh = bpy.data.meshes.new(name="Polygon")
        bpy.ops.object.select_all(action='DESELECT')
        bm = bmesh.new()
        for v in polyPath:
            bm.verts.new((v[0], v[1], 0))
        bm.faces.new(bm.verts)
        bm.to_mesh(mesh)
        polyObj = bpy.data.objects.new(name="Polygon_Object", object_data=mesh)

        _, dimY = dimXY(start, path)
        segs = self.segsByDim(abs(dimY * min(abs(deg), 360)/360))
        bpy.ops.object.select_all(action='DESELECT')
        self.solid = polyObj
        bpy.context.collection.objects.link(self.solid)
        bpy.context.view_layer.objects.active = self.solid
        self.solid.select_set(True)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        # HACK: spin only produce correct mesh when axis and deg are opposite sign, so forcing it here
        bpy.ops.mesh.spin(axis=(1, 0, 0), angle=radians(-abs(deg)), steps=segs)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        if deg < 0: # HACK: since spin hack above, mirror if deg is negative
            self.solid = self.mirror((False, False, True)).solid

        self.repairMesh()

class BlenderCirclePolySweep(BlenderShape):
    def __init__(self, rad: float, path: list[tuple[float, float, float]], api: BlenderShapeAPI):
        super().__init__(api)
        sweepShape = None
        if len(path) >= 2:
            start = path[0]
            sweepShape = BlenderBall(rad, api).mv(start[0], start[1], start[2])
            for p in path[1:]:
                stop = p
                rod = BlenderRod3D(start, stop, rad, api)
                endBall = BlenderBall(rad, api).mv(stop[0], stop[1], stop[2])
                sweepShape = sweepShape.join(rod).join(endBall)
                start = stop
        self.solid = sweepShape.solid


class BlenderTextZ(BlenderShape):
    def __init__(self, txt: str, fontSize: float, tck: float, fontName: str, api: BlenderShapeAPI):
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
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
        self.solid.location = (0, 0, tck/2)


if __name__ == '__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Set the desired origin location
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    BlenderShapeAPI(Fidelity.LOW).test(Path.cwd() / 'test' / 'blender_api')