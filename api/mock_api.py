#!/usr/bin/env python3

from __future__ import annotations
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import ShapeAPI, Shape, Fidelity, Implementation
from api.pylele_api_constants import DEFAULT_BUILD_DIR
from api.pylele_utils import gen_stl_foo


class MockShapeAPI(ShapeAPI):
    """
    Mock Pylele API implementation for test
    """

    def __init__(self, fidel: Fidelity):
        self.fidelity = fidel

    def getFidelity(self) -> Fidelity:
        return self.fidelity

    def getImplementation(self) -> Implementation:
        return Implementation.MOCK

    def setFidelity(self, fidel: Fidelity) -> None:
        self.fidelity = fidel

    def exportSTL(self, shape: MockShape, path: str) -> None:
        gen_stl_foo(path)

    def exportBest(self, shape: MockShape, path: Union[str, Path]) -> None:
        return self.exportSTL(shape=shape, path=path)

    def genBall(self, rad: float) -> MockShape:
        return MockShape(self)

    def genBox(self, l: float, wth: float, ht: float) -> MockShape:
        return MockShape(self)

    def genConeX(self, l: float, r1: float, r2: float) -> MockShape:
        return MockShape(self)

    def genConeY(self, l: float, r1: float, r2: float) -> MockShape:
        return MockShape(self)

    def genConeZ(self, l: float, r1: float, r2: float) -> MockShape:
        return MockShape(self)

    def genPolyRodX(self, l: float, rad: float, sides: int) -> MockShape:
        return MockShape(self)

    def genPolyRodY(self, l: float, rad: float, sides: int) -> MockShape:
        return MockShape(self)

    def genPolyRodZ(self, l: float, rad: float, sides: int) -> MockShape:
        return MockShape(self)

    def genRodX(self, l: float, rad: float) -> MockShape:
        return MockShape(self)

    def genRodY(self, l: float, rad: float) -> MockShape:
        return MockShape(self)

    def genRodZ(self, l: float, rad: float) -> MockShape:
        return MockShape(self)

    def genPolyExtrusionZ(
        self, path: list[tuple[float, float]], ht: float
    ) -> MockShape:
        return MockShape(self)

    def genLineSplineExtrusionZ(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        ht: float,
    ) -> MockShape:
        return MockShape(self)

    def genLineSplineRevolveX(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        deg: float,
    ) -> MockShape:
        return MockShape(self)

    def genCirclePolySweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> MockShape:
        return MockShape(self)

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> MockShape:
        return MockShape(self)

    def getJoinCutTol(self):
        return Implementation.MOCK.joinCutTol()


class MockSolid(object):
    """
    Mock Solid for test
    """

    pass


class MockShape(Shape):
    """
    Mock Pylele Shape implementation for test
    """

    def __init__(self, api: MockShapeAPI):
        self.api: MockShapeAPI = api
        self.solid = None

    def getAPI(self) -> MockShapeAPI:
        return self.api

    def getImplSolid(self):
        return self.solid

    def cut(self, cutter: MockShape) -> MockShape:
        self.solid = None
        return self

    def dup(self) -> MockShape:
        return self

    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> MockShape:
        return self

    def join(self, joiner: MockShape) -> MockShape:
        return self

    def mirrorXZ(self) -> MockShape:
        return self

    def mv(self, x: float, y: float, z: float) -> MockShape:
        return self

    def remove(self):
        pass

    def rotateX(self, ang: float) -> MockShape:
        return self

    def rotateY(self, ang: float) -> MockShape:
        return self

    def rotateZ(self, ang: float) -> MockShape:
        return self

    def scale(self, x: float, y: float, z: float) -> MockShape:
        return self

    def show(self):
        return self.solid


if __name__ == "__main__":
    MockShapeAPI(Fidelity.LOW).test(os.path.join(DEFAULT_BUILD_DIR, "mock-all.stl"))
