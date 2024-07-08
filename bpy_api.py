from __future__ import annotations
import bpy
import copy
import bmesh
import math
from mathutils import Vector
from pylele_api import Shape, ShapeAPI
from pylele_config import Fidelity
from pylele_utils import radians
from typing import Union

class BlenderShapeAPI(ShapeAPI):
    def __init__(self, smoothSegs: int):
        self.smoothSegs = smoothSegs

    def exportSTL(self, shape: BlenderShape, path: str) -> None:
        bpy.ops.object.select_all(action='DESELECT')
        shape.obj.select_set(True)
        bpy.context.view_layer.objects.active = shape.obj
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True)

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

    def genRodX(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodX(ln, rad, self)

    def genRodY(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodY(ln, rad, self)

    def genRodZ(self, ln: float, rad: float) -> BlenderShape:
        return BlenderRodZ(ln, rad, self)

    def genRndRodX(self, ln: float, rad: float, domeRatio: float = 1) -> BlenderShape:
        return BlenderRndRodX(ln, rad, domeRatio, self)

    def genRndRodY(self, ln: float, rad: float, domeRatio: float = 1) -> BlenderShape:
        return BlenderRndRodY(ln, rad, domeRatio, self)

    def genRndRodZ(self, ln: float, rad: float = 1, domeRatio: float = 1) -> BlenderShape:
        return BlenderRndRodZ(ln, rad, domeRatio, self)

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> BlenderShape:
        return BlenderPolyExtrusionZ(path, ht, self)

    def genLineSplineExtrusionZ(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]], 
            ht: float,
        ) -> BlenderShape:
        return BlenderLineSplineExtrusionZ(start, path, ht, self)
    
    def genLineSplineRevolveX(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]], 
            deg: float,
        ) -> BlenderShape:
        return BlenderLineSplineRevolveX(start, path, deg, self)
    def genCirclePolySweep(self, rad: float, path: list[tuple[float, float, float]]) -> BlenderShape:
        return BlenderCirclePolySweep(rad, path, self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> BlenderShape:
        return BlenderTextZ(txt, fontSize, tck, font, self)


class BlenderShape(Shape):

    MAX_DIM = 10000 # for max and min dimensions
    REPAIR_MIN_REZ = 0.00005
    
    def __init__(self, api: BlenderShapeAPI):
        super().__init__()
        self.api = api
        self.obj = None

    def cut(self, cutter: BlenderShape) -> BlenderShape:
        if cutter is None:
            return self
        bpy.context.view_layer.objects.active = self.obj
        mod = self.obj.modifiers.new(name="Diff", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter.obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        return self.repairMesh()

    def extrudeZ(self, tck: float) -> BlenderShape:
        if tck <= 0:
            return self
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        origin = self.obj.location
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.solidify(thickness=tck)
        bpy.ops.object.mode_set(mode='OBJECT')
        self.obj.location.z = tck
        return self.repairMesh()

    def findNearestEdgeIndex(self, point: tuple[float, float, float]) -> int:
        mesh = self.obj.data
        nearestIdx = -1
        minDist = float('inf')
        pv = Vector(point)
        for edge in mesh.edges:
            v1 = self.obj.matrix_world @ mesh.vertices[edge.vertices[0]].co
            v2 = self.obj.matrix_world @ mesh.vertices[edge.vertices[1]].co
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
        if rad <= 0 or nearestPts is None or len(nearestPts) == 0:
            return self
        segs = self.segsByDim(rad)
        wth = rad/2
        bpy.context.view_layer.objects.active = self.obj
        for p in nearestPts:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_mode(type="EDGE")
            bpy.ops.object.mode_set(mode='OBJECT')
            idx = self.findNearestEdgeIndex(p)
            self.obj.data.edges[idx].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.bevel(offset=wth, segments=segs)
            bpy.ops.object.mode_set(mode='OBJECT')
        return self.repairMesh()
    
    def half(self) -> BlenderShape:
        bpy.context.view_layer.objects.active = self.obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_no=(0, 1, 0), use_fill=True, clear_outer=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        return self.repairMesh()

    def join(self, joiner: BlenderShape) -> BlenderShape:
        if joiner is None:
            return self
        bpy.context.view_layer.objects.active = self.obj
        bpy.ops.object.mode_set(mode='OBJECT')
        mod = self.obj.modifiers.new(name="Union", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.object = joiner.obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        joiner.remove()
        return self.repairMesh()
    
    @classmethod
    def dimXY(
        cls,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    ) -> tuple[float, float]:
        # Initialize min and max values
        min_x = max_x = start[0]
        min_y = max_y = start[1]
        for p in path:
            if isinstance(p, tuple) or len(p) == 1:
                x, y = p
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
            elif isinstance(p, list):
                for x, y, _, _ in p:
                    min_x, max_x = min(min_x, x), max(max_x, x)
                    min_y, max_y = min(min_y, y), max(max_y, y)
        # Calculate spans and returns
        span_x = max_x - min_x
        span_y = max_y - min_y
        return (span_x, span_y)


    def lineSplineXY(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    ) -> bpy.types.Object:
        lastX, lastY = start
        dimX, dimY = BlenderShape.dimXY(start, path)
        segsX, segsY = self.segsByDim(dimX), self.segsByDim(dimY)
        lineData = bpy.data.curves.new('LineSpline', type='CURVE')
        lineData.dimensions = '2D'
        lineData.fill_mode = 'BOTH'
        spline = lineData.splines.new('BEZIER')
        # spline.bezier_points.add(1)
        bp = spline.bezier_points[-1]
        bp.co = (lastX, lastY, 0)
        bp.handle_left_type = 'VECTOR'
        bp.handle_right_type = 'VECTOR'
        for pi, p in enumerate(path):
            if isinstance(p, tuple) or len(p) == 1:
                x, y = p
                nextX, nextY = start if pi == len(path)-1 else \
                    (path[pi+1] if isinstance(path[pi+1], tuple) else (path[pi+1][0][0], path[pi+1][0][1]))
                spline.bezier_points.add(1)
                bp = spline.bezier_points[-1]
                bp.co = (x, y, 0)
                bp.handle_left_type = 'VECTOR'
                bp.handle_left = (lastX, lastY, 0)
                bp.handle_right_type = 'VECTOR'
                bp.handle_right = (nextX, nextY, 0)
                lastX, lastY = p
            elif isinstance(p, list):
                for i, (x, y, dx, dy) in enumerate(p):
                    spline.bezier_points.add(1)
                    bp = spline.bezier_points[-1]
                    bp.co = (x, y, 0)
                    length = math.sqrt(dx**2 + dy**2)
                    if length != 0:
                        direction_x, direction_y = dx / length, dy / length
                    else:
                        direction_x, direction_y = 1, 0  # Default direction if no gradient
                    
                    # Calculate handle positions
                    handle_length = 2 * length  # Adjust handle length as needed
                    handle_left = (x - direction_x * handle_length, y - direction_y * handle_length, 0)
                    handle_right = (x + direction_x * handle_length, y + direction_y * handle_length, 0)
                    
                    nextX, nextY = start if pi == len(path)-1 else \
                        (path[pi+1] if isinstance(path[pi+1], tuple) else (path[pi+1][0][0], path[pi+1][0][1]))
                    # Set handles
                    bp.handle_left_type = 'VECTOR' if i == 0 else 'ALIGNED'
                    bp.handle_right_type = 'VECTOR' if i == len(p)-1 else 'ALIGNED'
                    bp.handle_left = (lastX, lastY, 0) if i == 0 else handle_left
                    bp.handle_right = (nextX, nextY, 0) if i == len(p)-1 else handle_right
                    lastX, lastY = (x, y)
        
        spline.bezier_points.add(1)
        bp = spline.bezier_points[-1]
        bp.co = (nextX, nextY, 0)
        spline.use_cyclic_u = True
        spline.use_endpoint_u = True
        lineData.resolution_u = segsX
        lineData.resolution_v = segsY
        obj = bpy.data.objects.new('LineSplineObj', lineData)
        return obj

    def mirrorXZ(self) -> BlenderShape:
        cp = copy.copy(self)
        cp.obj.select_set(True)
        bpy.context.view_layer.objects.active = cp.obj
        bpy.ops.object.duplicate()
        bpy.ops.object.select_all(action='DESELECT')
        dup = bpy.context.object
        dup.select_set(True)

        # shift to extreme right to avoid cross mirroring
        dup.location.y = dup.location.y + self.MAX_DIM

        bpy.context.view_layer.objects.active = dup
        mirror = bpy.data.objects.new("MirrorAtOrigin", None)
        mirror.location = (0, 0, 0)
        mod = dup.modifiers.new(name="Mirror", type='MIRROR')
        mod.mirror_object = mirror
        mod.use_axis[0] = False
        mod.use_axis[1] = True
        mod.use_axis[2] = False
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        cp.obj = dup

        cp = cp.half() # cut out the original half

        # recover from extreme right shift
        cp.obj.location.y = cp.obj.location.y + self.MAX_DIM
        return cp

    def mv(self, x: float, y: float, z: float) -> BlenderShape:
        if x == 0 and y == 0 and z == 0:
            return self
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.transform.translate(value=(x, y, z))
        return self

    def remove(self) -> None:
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        bpy.ops.object.delete()
        
    def repairMesh(self) -> BlenderShape:
        minRez = self.REPAIR_MIN_REZ
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bm = bmesh.from_edit_mesh(self.obj.data)
        non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
        loop = 0
        while non_manifold_edges and loop < 3:
            print(f"Loop {loop}: found {len(non_manifold_edges)} non-manifold edges. Attempting to fix...")
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.remove_doubles(
                threshold=minRez, 
                # use_sharp_edge_from_normals=True,
                # use_unselected=True,
            ) 
            bpy.ops.mesh.fill_holes(sides=0)  # 'sides=0' fills all holes
            bpy.ops.mesh.dissolve_degenerate() #threshold=minRez)
            bpy.ops.mesh.delete_loose() #use_faces=True, use_edges=True, use_verts=True)
            bpy.ops.mesh.normals_make_consistent() #inside=False)
            bm = bmesh.from_edit_mesh(self.obj.data)
            non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
            minRez *= 2
            loop += 1
            
        bpy.ops.object.mode_set(mode='OBJECT')
        return self
        
    def rotateX(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.transform.rotate(
            value=math.radians(ang),     # Rotation angle in radians
            orient_axis='X',             # Rotation axis
            constraint_axis=(True, False, False),  # Constrain to Z-axis
            orient_type='GLOBAL',        # Orientation type
        )
        return self #.repairMesh()

    def rotateY(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.transform.rotate(
            value=math.radians(ang),     # Rotation angle in radians
            orient_axis='Y',             # Rotation axis
            constraint_axis=(False, True, False),  # Constrain to Z-axis
            orient_type='GLOBAL',        # Orientation type
        )
        return self #.repairMesh()

    def rotateZ(self, ang: float) -> BlenderShape:
        if ang == 0:
            return self
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        bpy.ops.transform.rotate(
            value=math.radians(ang),     # Rotation angle in radians
            orient_axis='Z',             # Rotation axis
            constraint_axis=(False, False, True),  # Constrain to Z-axis
            use_accurate=True,
        )
        return self #.repairMesh()

    def scale(self, x: float, y: float, z: float) -> BlenderShape:
        if x == 1 and y == 1 and z == 1:
            return self
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
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
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)

    def segsByDim(self, dim: float) -> int:
        return math.ceil(dim**.5 * self.api.smoothSegs)

class BlenderBall(BlenderShape):
    def __init__(self, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        segs = self.segsByDim(rad)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, segments=segs, ring_count=segs)
        self.obj = bpy.context.object

class BlenderBox(BlenderShape):
    def __init__(self, ln: float, wth: float, ht: float, api: BlenderShapeAPI):
        super().__init__(api)
        bpy.ops.mesh.primitive_cube_add(size=1)
        self.obj = bpy.context.object
        self.scale(ln, wth, ht)


class BlenderConeZ(BlenderShape):
    def __init__(self, ln: float, r1: float, r2: float, api: BlenderShapeAPI):
        super().__init__(api)
        verts = self.segsByDim(max(r1, r2))
        bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=ln, vertices=verts)
        self.obj = bpy.context.object


class BlenderConeX(BlenderShape):
    def __init__(self, ln: float, r1: float, r2: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.obj = BlenderConeZ(ln, r1, r2, api).rotateY(90).obj


class BlenderConeY(BlenderShape):
    def __init__(self, ln: float, r1: float, r2: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.obj = BlenderConeZ(ln, r1, r2, api).rotateX(90).obj


class BlenderRndRodZ(BlenderShape):
    def __init__(self, ln: float, rad: float, domeRatio: float, api: BlenderShapeAPI):
        super().__init__(api)
        rLen = ln - 2*rad*domeRatio
        rod = BlenderRodZ(rLen, rad, api)
        for bz in [rLen/2, -rLen/2]:
            ball = BlenderBall(rad, api).scale(1, 1, domeRatio).mv(0, 0, bz)
            rod = rod.join(ball)
        self.obj = rod.obj


class BlenderRndRodX(BlenderShape):
    def __init__(self, ln: float, rad: float, domeRatio: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.obj = BlenderRndRodZ(ln, rad, domeRatio, api).rotateY(90).obj


class BlenderRndRodY(BlenderShape):
    def __init__(self, ln: float, rad: float, domeRatio: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.obj = BlenderRndRodZ(ln, rad, domeRatio, api).rotateX(90).obj


class BlenderRodZ(BlenderShape):
    def __init__(self, ln: float, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        verts = self.segsByDim(rad)
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=ln, vertices=verts)
        self.obj = bpy.context.object


class BlenderRodX(BlenderShape):
    def __init__(self, ln: float, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.obj = BlenderRodZ(ln, rad, api).rotateY(90).obj


class BlenderRodY(BlenderShape):
    def __init__(self, ln: float, rad: float, api: BlenderShapeAPI):
        super().__init__(api)
        self.obj = BlenderRodZ(ln, rad, api).rotateX(90).obj


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
        self.obj = cylinder

class BlenderPolyExtrusionZ(BlenderShape):
    def __init__(self, path: list[tuple[float, float]], ht: float, api: BlenderShapeAPI):
        super().__init__(api)
        mesh = bpy.data.meshes.new(name="Polygon")
        bpy.ops.object.select_all(action='DESELECT')
        bm = bmesh.new()
        for v in path:
            bm.verts.new((v[0], v[1], 0))
        bm.faces.new(bm.verts)
        bm.to_mesh(mesh)
        self.obj = bpy.data.objects.new(name="Polygon_Object", object_data=mesh)
        bpy.context.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.extrudeZ(ht)
        self.obj = self.obj


class BlenderLineSplineExtrusionZ(BlenderShape):
    def __init__(
        self, 
        start: tuple[float, float], 
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        ht: float,
        api: BlenderShapeAPI,
    ):
        super().__init__(api)
        bpy.ops.object.select_all(action='DESELECT')
        self.obj = self.lineSplineXY(start, path)
        bpy.context.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        self.extrudeZ(ht)
        # Set the desired origin location
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

class BlenderLineSplineRevolveX(BlenderShape):
    def __init__(
        self, 
        start: tuple[float, float], 
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        deg: float,
        api: BlenderShapeAPI,
    ):
        def adjustX(
            path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]], 
            x: float,
        ) -> list[Union[tuple[float, float], list[tuple[float, float, float, float]]]]:
            if x == 0:
                return path
            
            newPath = []
            for p in path:
                if isinstance(p, tuple):
                    newPath.append((p[0] + x, p[1]))
                else:
                    newSpline = [(px + x, py, dx, dy) for px, py, dx, dy in p]
                    newPath.append(newSpline)
            return newPath
        
        super().__init__(api)

        origX, origY = start
        _, dimY = BlenderShape.dimXY(start, path)
        segs = self.segsByDim(dimY)
        path = adjustX(path, -origX)
        bpy.ops.object.select_all(action='DESELECT')
        self.obj = self.lineSplineXY((0, origY), path)
        bpy.context.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        # self.extrudeZ(10)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.spin(axis=(1,0,0), angle=radians(-deg), steps=segs)
        self.obj.location.x = origX
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.cursor.location = (0, 0, 0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
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
        self.obj = sweepShape.obj


class BlenderTextZ(BlenderShape):
    def __init__(self, txt: str, fontSize: float, tck: float, font: str, api: BlenderShapeAPI):
        super().__init__(api)
        bpy.ops.object.text_add()
        self.obj = bpy.context.object
        self.obj.data.body = txt
        self.obj.data.size = fontSize
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
        self.obj.location = (0, 0, 0)
        self.extrudeZ(tck)

if __name__ == '__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action='DESELECT')
    segs = Fidelity.LOW.smoothingSegments()
    api = BlenderShapeAPI(segs)
    api.test("build/bpy-all.stl")