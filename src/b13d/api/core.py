from __future__ import annotations

import os
import sys
import importlib
from math import inf
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from b13d.api.constants import DEFAULT_TEST_DIR
from b13d.api.utils import getFontname2FilepathMap

APIS_INFO = {
    "mock": {"module": "b13d.api.mock", "class": "MockShapeAPI"},
    "cadquery": {"module": "b13d.api.cq", "class": "CQShapeAPI"},
    "blender": {"module": "b13d.api.bpy", "class": "BlenderShapeAPI"},
    "trimesh": {"module": "b13d.api.tm", "class": "TMShapeAPI"},
    "solid2": {"module": "b13d.api.sp2", "class": "Sp2ShapeAPI"},
    "manifold": {"module": "b13d.api.mf", "class": "MFShapeAPI"},
}


# consider update to StrEnum for python 3.11 and above
# https://tsak.dev/posts/python-enum/
class StringEnum(str, Enum):
    """ Enumerator for String Types"""

    def __str__(self):
        return self.value

    def list(self):
        return list(self)


class Fidelity(StringEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __repr__(self):
        return f"Fidelity({self.value} tol={self.tolerance()}, seg={self.smoothing_segments()})"

    def tolerance(self) -> float:
        match self:
            case Fidelity.LOW:
                return 0.001
            case Fidelity.MEDIUM:
                return 0.0005
            case Fidelity.HIGH:
                return 0.00025

    def smoothing_segments(self) -> float:
        match self:
            case Fidelity.LOW:
                return 6
            case Fidelity.MEDIUM:
                return 12
            case Fidelity.HIGH:
                return 17 # 18 causes weird chamber for blender, also too slow

    def code(self) -> str:
        return str(self)[0].upper()

class Implementation(StringEnum):
    """Pylele API implementations"""

    MOCK = "mock"
    CADQUERY = "cadquery"
    BLENDER = "blender"
    TRIMESH = "trimesh"
    SOLID2 = "solid2"
    MANIFOLD = "manifold"

    def __repr__(self):
        return f"Implementation({self.value})"

    def code(self) -> str:
        """ Return Code that identifies Implementation """
        return str(self)[0].upper()

    def module_name(self):
        """Returns the module name of the API"""
        return APIS_INFO[self]["module"]

    def class_name(self):
        """Returns the class name of the API"""
        return APIS_INFO[self]["class"]

    def tolerance(self) -> float:
        """ Tolerance for joins to have a little overlap """
        return 0 if self == Implementation.CADQUERY else 0.02

    def get_api(self, fidelity: Fidelity = Fidelity.LOW) -> ShapeAPI:
        """ Get the handler to the selected implementation API """
        mod = importlib.import_module(self.module_name())
        api = getattr(mod, self.class_name())
        return api(implementation = self, fidelity=fidelity)


def supported_apis() -> list:
    """Returns the list of supported apis"""
    ver = sys.version_info
    assert ver[0] == 3

    apis = ["trimesh", "cadquery", "solid2", "manifold"]

    if ver[1] < 12:
        # blender bpy package currently not supported with python 3.12
        apis.append("blender")

    return apis

def make_test_path(api_name,test_path=DEFAULT_TEST_DIR):
    """ Makes Test folder """
    out_path = os.path.join(Path.cwd(), test_path, api_name)

    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    assert os.path.isdir(out_path)

    return out_path

def test_api(api):
    """ Test a Shape API """
    if api in supported_apis()+['mock']:
        impl = Implementation(api)
        sapi = impl.get_api(fidelity = Fidelity.LOW)
        outfname = make_test_path(impl.module_name())
        sapi.test(outfname)
    else:
        print(f'WARNING: Skipping test of {api} api, because unsupported with python version {sys.version}!')

def default_or_alternate(def_val, alt_val=None):
    """ Override default value with alternate value, if available"""
    if alt_val is None:
        return def_val
    return alt_val
    # return def_val if alt_val is None else al

DIRECTION_TO_TUPLE = {
    'X' : (1,0,0),
    'Y' : (0,1,0),
    'Z' : (0,0,1),
}

class Direction(StringEnum):
    """ A class to represent direction vectors """
    X = 'X'
    Y = 'Y'
    Z = 'Z'

    def eval(self):
        return DIRECTION_TO_TUPLE[self.value]

    def __add__(self, operand):
        return map(lambda x: operand * x, self.eval() )

    def __mul__(self, operand):
        retval = map(lambda x: operand * x if x == 1 else 1, self.eval() )
        return retval

class Shape(ABC):

    MAX_DIM = 2000  # for max and min dimensions

    def __init__(self, api: ShapeAPI, solid=None):
        self.api: ShapeAPI = api
        self.solid = solid
        self.color:tuple[int, int, int] = None
        self.name: str = None

    @abstractmethod
    def cut(self, cutter: Shape) -> Shape: ...

    @abstractmethod
    def dup(self) -> Shape: ...

    def fillet(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> Shape:
        print(f"Warning! Fillet not implemented yet for {self.api.implementation} api!")
        return self

    def half(self, plane: tuple[bool, bool, bool] = (False, True, False)) -> Shape:
        halfCutter = (
            self.api
            .box(self.MAX_DIM, self.MAX_DIM, self.MAX_DIM)
            .mv(
                self.MAX_DIM / 2 if plane[0] else 0,
                self.MAX_DIM / 2 if plane[1] else 0,
                self.MAX_DIM / 2 if plane[2] else 0,
            )
        )
        return self.cut(halfCutter)

    @abstractmethod
    def join(self, joiner: Shape) -> Shape: ...

    @abstractmethod
    def mirror(self) -> Shape: ...

    def mirror_and_join(self) -> Shape:
        """mirror midR and joins the two parts"""
        joinTol = self.api.tolerance()
        midL = self.mirror()
        return midL.mv(0, joinTol / 2, 0).join(self.mv(0, -joinTol / 2, 0))

    @abstractmethod
    def mv(self, x: float, y: float, z: float) -> Shape: ...

    @abstractmethod
    def rotate_x(self, ang: float) -> Shape: ...

    @abstractmethod
    def rotate_y(self, ang: float) -> Shape: ...

    @abstractmethod
    def rotate_z(self, ang: float) -> Shape: ...

    def rotate(self,  ang: float | tuple[float,float,float], direction: Direction = Direction.Z) -> Shape:
        """ Generate a cone, with direction as parameter """

        if direction.upper() == Direction.X:
            return self.rotate_x(ang)
        if direction.upper() == Direction.Y:
            return self.rotate_y(ang)
        if direction.upper() == Direction.Z:
            return self.rotate_z(ang)

        # default implemntation, if not available
        return self.rotate_x(ang[0]).rotate_y(ang[1]).rotate_z(ang[2])

    @abstractmethod
    def scale(self, x: float, y: float, z: float) -> Shape: ...

    def set_color(self, rgb: tuple[int, int, int]) -> Shape:
        self.color = rgb
        return self

    def set_name(self, name: str) -> Shape:
        self.name = name
        return self

    def show(self):
        print(f"Warning! show not implemented yet for {self.api.implementation} api!")

    def __add__(self, operand) -> Shape:
        """ Join using + """
        if operand is None:
            return self
        assert isinstance(operand,Shape)
        return self.join(operand)

    def __sub__(self, operand) -> Shape:
        """ cut using - """
        if operand is None:
            return self
        assert isinstance(operand,Shape)
        return self.cut(operand)

    def __mul__(self, operand: tuple[float, float, float] = (1,1,1)) -> Shape:
        """ scale using * """
        if operand is None:
            return self
        return self.scale(*operand)

    def __lshift__(self, operand: tuple[float, float, float] = (0,0,0)) -> Shape:
        """ move using << """
        if operand is None:
            return self
        return self.mv(*operand)


class ShapeAPI(ABC):
    """ Prototype for Implementation API """

    implementation = None
    fidelity = None
    font2path = getFontname2FilepathMap()

    def __init__(
        self,
        implementation : Implementation,
        fidelity: Fidelity = Fidelity.LOW,
    ):
        self.implementation = implementation
        self.fidelity = fidelity

    def getFontPath(self, fontName: str) -> str:
        """
            given fontName return path to font file.
            If fontName is None, find the shortest name font to serve as default
        """
        if fontName is None:
            font_names = list(self.font2path.keys())
            font_names.sort(key=len)
            font_path = self.font2path[font_names[0]]
        else:
            font_path = self.font2path[fontName] if fontName in self.font2path else None

        return font_path

    @abstractmethod
    def export(self, shape: Shape, path: Union[str, Path], fmt: str) -> None: ...

    @abstractmethod
    def export_stl(self, shape: Shape, path: Union[str, Path]) -> None: ...

    @abstractmethod
    def export_best(self, shape: Shape, path: Union[str, Path]) -> None: ...

    def export_best_multishapes(
        self,
        shapes: list[Shape],
        assembly_name: str,
        path: Union[str, Path],
    ) -> None:
        joined: Shape = None
        for s in shapes:
            joined = s if joined is None else joined.join(s)
        self.export_stl(shape=joined, path=path)

    @abstractmethod
    def sphere(self, r: float) -> Shape: ...

    @abstractmethod
    def box(self, l: float, wth: float, ht: float) -> Shape: ...

    def cube(self, l: float) -> Shape:
        return self.box(l=l,wth=l,ht=l)

    @abstractmethod
    def cone_x(self, h: float, r1: float, r2: float) -> Shape: ...

    @abstractmethod
    def cone_y(self, h: float, r1: float, r2: float) -> Shape: ...

    @abstractmethod
    def cone_z(self, h: float, r1: float, r2: float) -> Shape: ...

    def cone(self,  h: float, r1: float, r2: float, direction: Direction = Direction.Z) -> Shape:
        """ Generate a cone, with direction as parameter """
        if direction == Direction.X:
            return self.cone_x(h=h,r1=r1,r2=r2)
        if direction == Direction.Y:
            return self.cone_y(h=h,r1=r1,r2=r2)
        if direction == Direction.Z:
            return self.cone_z(h=h,r1=r1,r2=r2)
        assert False

    @abstractmethod
    def regpoly_extrusion_x(self, l: float, rad: float, sides: int) -> Shape: ...

    @abstractmethod
    def regpoly_extrusion_y(self, l: float, rad: float, sides: int) -> Shape: ...

    @abstractmethod
    def regpoly_extrusion_z(self, l: float, rad: float, sides: int) -> Shape: ...

    def cylinder(self,  l: float, rad: float, r2: float = None,
                 sides: int = None, direction: Direction = Direction.Z,
                 dome_ratio: float = None) -> Shape:
        """ Generate a cylinder, with direction as parameter """

        if not r2 is None:
            assert sides is None, 'Parameters sides and r2 cannot be both None!'
            return self.cone(h=l,r1=rad,r2=r2,direction=direction)

        if direction.upper() == Direction.X:
            if sides is None:
                if not dome_ratio is None:
                    return self.cylinder_rounded_x(l=l,rad=rad,domeRatio=dome_ratio)
                else:
                    return self.cylinder_x(h=l,rad=rad)
            else:
                return self.regpoly_extrusion_x(l=l,rad=rad, sides=sides)

        if direction.upper() == Direction.Y:
            if sides is None:
                if not dome_ratio is None:
                    return self.cylinder_rounded_y(l=l,rad=rad,domeRatio=dome_ratio)
                else:
                    return self.cylinder_y(h=l,rad=rad)
            else:
                return self.regpoly_extrusion_y(l=l,rad=rad, sides=sides)

        if direction.upper() == Direction.Z:
            if sides is None:
                if not dome_ratio is None:
                    return self.cylinder_rounded_z(l=l,rad=rad,domeRatio=dome_ratio)
                else:
                    return self.cylinder_z(h=l,rad=rad)
            else:
                return self.regpoly_extrusion_z(l=l,rad=rad, sides=sides)

        assert False

    @abstractmethod
    def cylinder_x(self, l: float, rad: float) -> Shape: ...

    @abstractmethod
    def cylinder_y(self, l: float, rad: float) -> Shape: ...

    @abstractmethod
    def cylinder_z(self, l: float, rad: float) -> Shape:
        ...

    def rounded_edge_mask(self, l, rad, direction: Direction = Direction.Z, rot=0, tol = 0.1) -> Shape:
        """ generate a mask to round an edge """

        radi = rad + tol
        if direction.upper() == Direction.X:
            mask  = self.box(l,radi,radi).mv(0,radi/2,radi/2)
        elif direction.upper() == Direction.Y:
            mask  = self.box(radi,l,radi).mv(radi/2,0,radi/2)
        elif direction.upper() == Direction.Z:
            mask  = self.box(radi,radi,l).mv(radi/2,radi/2,0)
        else:
            assert False

        mask -= self.cylinder(l,rad=radi,direction=direction)
        mask  = mask.rotate(rot,direction=direction)

        return mask

    def cylinder_rounded_x(self, l: float, rad: float, domeRatio: float = 1) -> Shape:
        rndRodZ = self.cylinder_rounded_z(l, rad, domeRatio)
        return rndRodZ.rotate_y(90)

    def cylinder_rounded_y(self, l: float, rad: float, domeRatio: float = 1) -> Shape:
        rndRodX = self.cylinder_rounded_x(l, rad, domeRatio)
        return rndRodX.rotate_z(90)

    def cylinder_rounded_z(self, l: float, rad: float, domeRatio: float = 1) -> Shape:
        stemLen = l - 2 * rad * domeRatio
        rod = self.cylinder_z(stemLen, rad)
        for bz in [stemLen / 2, -stemLen / 2]:
            ball = self.sphere(rad).scale(1, 1, domeRatio).mv(0, 0, bz)
            rod = rod.join(ball)
        return rod

    @abstractmethod
    def polygon_extrusion(
        self, path: list[tuple[float, float]], ht: float
    ) -> Shape: ...

    @abstractmethod
    def spline_extrusion(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        ht: float,
    ) -> Shape: ...

    @abstractmethod
    def spline_revolve(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        deg: float,
    ) -> Shape: ...

    @abstractmethod
    def regpoly_sweep(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
    ) -> Shape: ...

    @abstractmethod
    def text(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        font: str,
    ): ...

    def sphere_quadrant(self, rad: float, pickTop: bool, pickFront: bool):
        maxDim = Shape.MAX_DIM
        ball = self.sphere(rad)
        topCut = self.box(maxDim, maxDim, maxDim).mv(
            0, 0, -maxDim / 2 if pickTop else maxDim / 2
        )
        frontCut = self.box(maxDim, maxDim, maxDim).mv(
            maxDim / 2 if pickFront else -maxDim / 2, 0, 0
        )
        return ball.cut(topCut).cut(frontCut)

    def cylinder_half(self, rad: float, pickFront: bool, tck: float):
        maxDim = Shape.MAX_DIM
        rod = self.cylinder_z(tck, rad)
        cutter = self.box(maxDim, maxDim, maxDim).mv(
            maxDim / 2 if pickFront else -maxDim / 2, 0, 0
        )
        return rod.cut(cutter)

    def tolerance(self):
        return self.implementation.tolerance()

    def test(self, outpath: str | Path) -> None:

        expDir = outpath if isinstance(outpath, Path) else Path(outpath)
        if not expDir.exists():
            os.makedirs(expDir)
        elif not expDir.is_dir():
            print("Cannot export to non directory: %s" % expDir, file=sys.stderr)
            sys.exit(os.EX_SOFTWARE)

        implCode = self.implementation.code()

        # Simple Tests

        ball = self.sphere(10)
        self.export_stl(ball, expDir / f"{implCode}-ball")

        box = self.box(10, 20, 30)
        self.export_stl(box, expDir / f"{implCode}-box")

        xRod = self.cylinder_x(30, 5)
        self.export_stl(xRod, expDir / f"{implCode}-xrod")

        yRod = self.cylinder_y(30, 5)
        self.export_stl(yRod, expDir / f"{implCode}-yrod")

        zRod = self.cylinder_z(30, 5)
        self.export_stl(zRod, expDir / f"{implCode}-zrod")

        xCone = self.cone_x(30, 5, 2)
        self.export_stl(xCone, expDir / f"{implCode}-xcone")

        xCone2 = self.cone(30, 5, 2, 'X')
        self.export_stl(xCone2, expDir / f"{implCode}-xcone2")

        yCone = self.cone_y(30, 5, 2)
        self.export_stl(yCone, expDir / f"{implCode}-ycone")

        zCone = self.cone_z(30, 5, 2)
        self.export_stl(zCone, expDir / f"{implCode}-zcone")

        xSqRod = self.regpoly_extrusion_x(30, 5, 4)
        self.export_stl(xSqRod, expDir / f"{implCode}-xsqrod")

        ySqRod = self.regpoly_extrusion_y(30, 5, 4)
        self.export_stl(ySqRod, expDir / f"{implCode}-ysqrod")

        zSqRod = self.regpoly_extrusion_z(30, 5, 4)
        self.export_stl(zSqRod, expDir / f"{implCode}-zsqrod")

        xRndRod = self.cylinder_rounded_x(30, 5, 1 / 2)
        self.export_stl(xRndRod, expDir / f"{implCode}-xrndrod")

        yRndRod = self.cylinder_rounded_y(30, 5, 1 / 2)
        self.export_stl(yRndRod, expDir / f"{implCode}-yrndrod")

        zRndRod = self.cylinder_rounded_z(30, 5, 1 / 2)
        self.export_stl(zRndRod, expDir / f"{implCode}-zrndrod")

        zPolyExt = self.polygon_extrusion([(0, 0), (10, 0), (0, 10)], 5)
        self.export_stl(zPolyExt, expDir / f"{implCode}-zpolyext")

        zTxt = self.text("ABC", 30, 10, "Courier New")
        self.export_stl(zTxt, expDir / f"{implCode}-ztxt")

        zTxt = zTxt.rotate_x(180)
        self.export_stl(zTxt, expDir / f"{implCode}-ztxt-z180")

        qBall = self.sphere_quadrant(10, True, True)
        self.export_stl(qBall, expDir / f"{implCode}-qball")

        hDisc = self.cylinder_half(10, True, 2)
        self.export_stl(hDisc, expDir / f"{implCode}-hdisc")

        body = self.spline_extrusion(
            start=(215, 0),
            path=[
                (215, 23),
                [
                    (216, 23, 0.01, 0.5, 0.3),
                    (390, 76, 0, 0.6),
                    (481, 1, -inf),
                ],
                (481, 0),
            ],
            ht=5,
        )
        self.export_stl(body, expDir / f"{implCode}-body")

        dome = self.spline_extrusion(
            start=(0, 0),
            path=[
                (-5, 0),
                (-5, 10),
                (0, 10),
                [
                    (1, 10, 0),
                    (5, 8, -inf),
                    (2.5, 5, -inf),
                    (5, 2, -inf),
                    (1, 0, 0),
                ],
                (0, 0),
            ],
            ht=5,
        )
        self.export_stl(dome, expDir / f"{implCode}-splineext")

        donut = self.spline_revolve(
            start=(0, 1),
            path=[
                (-5, 1),
                (-5, 9),
                (0, 9),
                [
                    (1, 9, 0),
                    (5, 7, -inf),
                    (2.5, 5, -inf),
                    (5, 3, -inf),
                    (1, 1, 0),
                ],
                (0, 1),
            ],
            deg=-225,
        )
        self.export_stl(donut, expDir / f"{implCode}-splinerev")

        sweep = self.regpoly_sweep(
            1, [(-20, 0, 0), (20, 0, 40), (40, 20, 40), (60, 20, 0)]
        )
        self.export_stl(sweep, expDir / f"{implCode}-sweep")

        edgex = self.rounded_edge_mask(direction='x',l=30, rad = 10)
        self.export_stl(edgex, expDir / f"{implCode}-edgex")

        edgey = self.rounded_edge_mask(direction='y',l=30, rad = 10)
        self.export_stl(edgey, expDir / f"{implCode}-edgey")

        edgez = self.rounded_edge_mask(direction='z',l=30, rad = 10)
        self.export_stl(edgez, expDir / f"{implCode}-edgez")

        # More complex tests

        box = self.box(10, 10, 2).mv(0, 0, -10)
        ball = self.sphere(5).scale(1, 2, 1)
        coneZ = self.cone_z(10, 10, 5).mv(0, 0, 10)
        coneX = self.cone_x(10, 1, 2)
        rod = self.cylinder_z(20, 1)
        obj1 = box + ball + coneZ + rod - coneX
        obj1 = obj1.mv(10, 10, 11)
        joined = obj1

        rx = self.cylinder_x(10, 3)
        ry = self.cylinder_y(10, 3)
        rz = self.cylinder_z(10, 3)
        obj2 = rx.join(ry).join(rz).mv(10, -10, 5)
        joined += obj2

        rr1 = self.cylinder_rounded_x(10, 3).scale(0.5, 1, 1).mv(0, -20, 0)
        rr2 = self.cylinder_rounded_x(10, 3).scale(1, 0.5, 1).mv(0, 0, 0)
        rr3 = self.cylinder_rounded_x(10, 3).scale(1, 1, 0.5).mv(0, 20, 0)
        rr4 = self.cylinder_rounded_y(50, 1)
        obj3 = rr1.join(rr2).join(rr3).join(rr4).mv(0, 0, -20)
        joined += obj3

        rrx = self.cylinder_rounded_x(10, 3, 0.25)
        rry = self.cylinder_rounded_y(10, 3, 0.5)
        rrz = self.cylinder_rounded_z(10, 3)
        obj4 = rrx.join(rry).join(rrz).half().mv(-10, 10, 5)
        joined += obj4

        pe = self.polygon_extrusion([(-10, 30), (10, 30), (10, -30), (-10, -30)], 10)
        tz = self.text("Hello World", 10, 5, "Arial").rotate_z(90).mv(0, 0, 10)
        obj5 = pe.join(tz).mv(30, -30, 0)
        mirror = obj5.mirror().mv(10, 0, 0)
        obj5 = obj5.join(mirror)
        joined += obj5

        rndBox = self.box(10, 10, 10).fillet([(5, 0, 5)], 1)
        obj6 = rndBox.mv(-10, -10, 5)
        joined += obj6

        dome = self.spline_extrusion(
            start=(0, 0),
            path=[
                (-5, 0),
                (-5, 10),
                (0, 10),
                [
                    (1, 10, 0),
                    (5, 8, -inf),
                    (3, 5, -inf),
                    (5, 2, -inf),
                    (1, 0, 0),
                ],
                (0, 0),
            ],
            ht=5,
        )
        obj7 = dome.rotate_y(-45).mv(-10, 15, 0)
        joined += obj7

        donutStart = (60, 0.1)
        donutPath = [
            (60, 10),
            (61, 10),
            [
                (62, 10, 0),
                (65, 5, -inf),
                (62, 0.1, 0),
            ],
            (60, 0.1),
        ]
        dome2 = self.spline_revolve(donutStart, donutPath, 45).scale(1, 1, 0.5)
        dome3 = self.spline_revolve(donutStart, donutPath, -270).mv(
            0, 0, self.tolerance()
        )
        obj8 = dome2.join(dome3).mv(0, 0, -10)
        joined += obj8

        obj9 = self.regpoly_sweep(
            1, [(-20, 0, 0), (20, 0, 40), (40, 20, 40), (60, 20, 0)]
        )
        joined += obj9

        obj10 = self.sphere_quadrant(10, True, True).scale(2, 1, 0.5).mv(-30, -20, 0)
        joined += obj10

        obj11 = self.cylinder_half(10, True, 10).scale(1.5, 1, 1).mv(-30, 20, 0)
        joined += obj11

        # move operator shortcut
        obj12 = self.sphere(5) << (Direction.X + 2)
        obj13 = self.sphere(5) << (Direction.Y + 2)
        obj14 = self.sphere(5) << (Direction.Z + 2)
        obj15 = self.sphere(5) << (0,1,2)

        # scale operator shortcut
        obj16 = self.sphere(5) * (Direction.X * 2)
        obj17 = self.sphere(5) * (Direction.Y * 2)
        obj18 = self.sphere(5) * (Direction.Z * 2)
        obj19 = self.sphere(5) * (1,2,3)

        self.export_stl(joined, expDir / f"{implCode}-all")
