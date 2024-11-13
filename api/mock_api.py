#!/usr/bin/env python3

from __future__ import annotations
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import ShapeAPI, Shape, test_api
from api.pylele_utils import gen_stl_foo


class MockShapeAPI(ShapeAPI):
    """
    Mock Pylele API implementation for test
    """

    def export(self, shape: MockShape, path: Union[str, Path],fmt=".stl") -> None:
        return self.export_stl(shape=shape, path=path)

    def export_stl(self, shape: MockShape, path: str) -> None:
        gen_stl_foo(path)

    def export_best(self, shape: MockShape, path: Union[str, Path]) -> None:
        return self.export_stl(shape=shape, path=path)

    def sphere(self, rad: float) -> MockShape:
        return MockShape(self)

    def box(self, l: float, wth: float, ht: float) -> MockShape:
        return MockShape(self)

    def cone_x(self, l: float, r1: float, r2: float) -> MockShape:
        return MockShape(self)

    def cone_y(self, l: float, r1: float, r2: float) -> MockShape:
        return MockShape(self)

    def cone_z(self, l: float, r1: float, r2: float) -> MockShape:
        return MockShape(self)

    def regpoly_extrusion_x(self, l: float, rad: float, sides: int) -> MockShape:
        return MockShape(self)

    def regpoly_extrusion_y(self, l: float, rad: float, sides: int) -> MockShape:
        return MockShape(self)

    def regpoly_extrusion_z(self, l: float, rad: float, sides: int) -> MockShape:
        return MockShape(self)

    def cylinder_x(self, l: float, rad: float) -> MockShape:
        return MockShape(self)

    def cylinder_y(self, l: float, rad: float) -> MockShape:
        return MockShape(self)

    def cylinder_z(self, l: float, rad: float) -> MockShape:
        return MockShape(self)

    def polygon_extrusion(
        self, path: list[tuple[float, float]], ht: float
    ) -> MockShape:
        return MockShape(self)

    def spline_extrusion(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        ht: float,
    ) -> MockShape:
        return MockShape(self)

    def spline_revolve(
        self,
        start: tuple[float, float],
        path: list[tuple[float, float] | list[tuple[float, float, float, float]]],
        deg: float,
    ) -> MockShape:
        return MockShape(self)

    def regpoly_sweep(
        self, rad: float, path: list[tuple[float, float, float]]
    ) -> MockShape:
        return MockShape(self)

    def text(self, txt: str, fontSize: float, tck: float, font: str) -> MockShape:
        return MockShape(self)

class MockSolid(object):
    """
    Mock Solid for test
    """

    pass


class MockShape(Shape):
    """
    Mock Pylele Shape implementation for test
    """

    def cut(self, cutter: MockShape) -> MockShape:
        self.solid = None
        return self

    def dup(self) -> MockShape:
        return self

    def join(self, joiner: MockShape) -> MockShape:
        return self

    def mirror(self) -> MockShape:
        return self

    def mv(self, x: float, y: float, z: float) -> MockShape:
        return self

    def rotate_x(self, ang: float) -> MockShape:
        return self

    def rotate_y(self, ang: float) -> MockShape:
        return self

    def rotate_z(self, ang: float) -> MockShape:
        return self

    def scale(self, x: float, y: float, z: float) -> MockShape:
        return self

    def show(self):
        return self.solid


if __name__ == "__main__":
    test_api("mock")
