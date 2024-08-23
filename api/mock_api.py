#!/usr/bin/env python3

from __future__ import annotations
from typing import Union

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import ShapeAPI, Shape, Fidelity, Implementation
from api.pylele_api_constants import DEFAULT_BUILD_DIR


class MockShapeAPI(ShapeAPI):
    """
    Mock Pylele API implementation for test
    """

    def __init__(self, fidel: Fidelity):
        self.fidelity = fidel

    def setFidelity(self, fidel: Fidelity) -> None:
        self.fidelity = fidel

    def exportSTL(self, shape: MockShape, path: str) -> None:
        stlstr="""
        solid dart
        facet normal 0.00000E+000 0.00000E+000 -1.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 1.00000E+000 2.50000E-001 1.00000E+000
            endloop
        endfacet
        facet normal 0.00000E+000 0.00000E+000 -1.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
            endloop
        endfacet
        facet normal 8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 6.10000E+001 2.50000E-001 1.00000E+000
            endloop
        endfacet
        facet normal 8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
            endloop
        endfacet
        facet normal -8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
            endloop
        endfacet
        facet normal -8.09000E-001 5.87800E-001 0.00000E+000
            outer loop
                vertex 1.00000E+000 2.50000E-001 1.00000E+000
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 1.00000E+000
            endloop
        endfacet
        facet normal 3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
                vertex 1.00000E+000 2.50000E-001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
            endloop
        endfacet
        facet normal 3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
            endloop
        endfacet
        facet normal -3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
            endloop
        endfacet
        facet normal -3.09000E-001 -9.51100E-001 0.00000E+000
            outer loop
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 1.00000E+001 1.00000E+000
                vertex 6.10000E+001 2.50000E-001 1.00000E+000
            endloop
        endfacet
        facet normal 0.00000E+000 0.00000E+000 1.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
                vertex 1.00000E+000 2.50000E-001 6.00000E+000
            endloop
        endfacet
        facet normal 0.00000E+000 0.00000E+000 1.00000E+000
            outer loop
                vertex 3.10000E+001 1.00000E+001 6.00000E+000
                vertex 6.10000E+001 2.50000E-001 6.00000E+000
                vertex 3.10000E+001 4.15500E+001 6.00000E+000
            endloop
        endfacet
        endsolid dart
        """
        with open(path, 'w', encoding='UTF8') as f:
            f.write(stlstr)
        assert os.path.isfile(path)

    def genBall(self, rad: float) -> MockShape:
        return MockShape()

    def genBox(self, ln: float, wth: float, ht: float) -> MockShape:
        return MockShape()

    def genConeX(self, ln: float, r1: float, r2: float) -> MockShape:
        return MockShape()

    def genConeY(self, ln: float, r1: float, r2: float) -> MockShape:
        return MockShape()

    def genConeZ(self, ln: float, r1: float, r2: float) -> MockShape:
        return MockShape()

    def genPolyRodX(self, ln: float, rad: float, sides: int) -> MockShape:
        return MockShape()

    def genPolyRodY(self, ln: float, rad: float, sides: int) -> MockShape:
        return MockShape()

    def genPolyRodZ(self, ln: float, rad: float, sides: int) -> MockShape:
        return MockShape()

    def genRodX(self, ln: float, rad: float) -> MockShape:
        return MockShape()

    def genRodY(self, ln: float, rad: float) -> MockShape:
        return MockShape()

    def genRodZ(self, ln: float, rad: float) -> MockShape:
        return MockShape()

    def genRndRodX(self, ln: float, rad: float, domeRatio: float = 1) -> MockShape:
        return MockShape()

    def genRndRodY(self, ln: float, rad: float, domeRatio: float = 1) -> MockShape:
        return MockShape()

    def genRndRodZ(self, ln: float, rad: float, domeRatio: float = 1) -> MockShape:
        return MockShape()

    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> MockShape:
        return MockShape()

    def genLineSplineExtrusionZ(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]], 
            ht: float,
        ) -> MockShape:
        return MockShape()
    
    def genLineSplineRevolveX(self, 
            start: tuple[float, float], 
            path: list[tuple[float, float] | list[tuple[float, float, float, float]]], 
            deg: float,
        ) -> MockShape:
        return MockShape()
    
    def genCirclePolySweep(self, rad: float, path: list[tuple[float, float, float]]) -> MockShape:
        return MockShape()

    def genTextZ(self, txt: str, fontSize: float, tck: float, font: str) -> MockShape:
        return MockShape()

    def genQuarterBall(self, radius: float, pickTop: bool, pickFront: bool) -> MockShape:
        return MockShape()
        
    def genHalfDisc(self, radius: float, pickFront: bool, tck: float) -> MockShape:
        return MockShape()
    
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

    def __init__(self):
        self.solid = None

    def cut(self, cutter: MockShape) -> MockShape:
        self.solid = None
        return self

    def filletByNearestEdges(self, 
        nearestPts: list[tuple[float, float, float]], 
        rad: float,
    ) -> MockShape:
        return self

    def half(self) -> MockShape:
        return self

    def join(self, joiner: MockShape) -> MockShape:
        return self

    # draw mix of straight lines from pt to pt, draw spline when given list of (x,y,dx,dy)
    def lineSplineXY(
        self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
    ):
        return MockSolid()

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

if __name__ == '__main__':
    MockShapeAPI(Fidelity.LOW).test(os.path.join(DEFAULT_BUILD_DIR,"mock-all.stl"))