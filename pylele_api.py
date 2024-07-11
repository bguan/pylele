from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union

class Shape(ABC):
    @abstractmethod
    def cut(self, cutter: Shape) -> Shape:
        ...

    @abstractmethod
    def filletByNearestEdges(self, 
        nearestPts: list[tuple[float, float, float]], 
        rad: float,
    ) -> Shape:
        ...

    @abstractmethod
    def half(self) -> Shape:
        ...

    @abstractmethod
    def join(self, joiner: Shape) -> Shape:
        ...

    @abstractmethod
    def mirrorXZ(self) -> Shape:
        ...

    @abstractmethod
    def mv(self, x: float, y: float, z: float) -> Shape:
        ...

    @abstractmethod
    def remove(self):
        ...
    
    @abstractmethod
    def rotateX(self, ang: float) -> Shape:
        ...

    @abstractmethod
    def rotateY(self, ang: float) -> Shape:
        ...

    @abstractmethod
    def rotateZ(self, ang: float) -> Shape:
        ...

    @abstractmethod
    def scale(self, x: float, y: float, z: float) -> Shape:
        ...

    @abstractmethod
    def show(self):
        ...
class ShapeAPI(ABC):

    @abstractmethod
    def exportSTL(self, shape: Shape, path: str) -> None:
        ...

    @abstractmethod
    def genBall(self, rad: float) -> Shape:
        ...

    @abstractmethod
    def genBox(self, ln: float, wth: float, ht: float) -> Shape:
        ...

    @abstractmethod
    def genConeX(self, ln: float, r1: float, r2: float) -> Shape:
        ...

    @abstractmethod
    def genConeY(self, ln: float, r1: float, r2: float) -> Shape:
        ...

    @abstractmethod
    def genConeZ(self, ln: float, r1: float, r2: float) -> Shape:
        ...

    @abstractmethod
    def genRodX(self, ln: float, rad: float) -> Shape:
        ...

    @abstractmethod
    def genRodY(self, ln: float, rad: float) -> Shape:
        ...

    @abstractmethod
    def genRodZ(self, ln: float, rad: float) -> Shape:
        ...

    @abstractmethod
    def genRndRodX(self, ln: float, rad: float, domeRatio: float = 1) -> Shape:
        ...

    @abstractmethod
    def genRndRodY(self, ln: float, rad: float, domeRatio: float = 1) -> Shape:
        ...

    @abstractmethod
    def genRndRodZ(self, ln: float, rad: float, domeRatio: float = 1) -> Shape:
        ...

    @abstractmethod
    def genPolyExtrusionZ(self, path: list[tuple[float, float]], ht: float) -> Shape:
        ...

    @abstractmethod
    def genLineSplineExtrusionZ(self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        ht: float,
    ) -> Shape:
        ...

    @abstractmethod
    def genLineSplineRevolveX(self,
        start: tuple[float, float],
        path: list[Union[tuple[float, float], list[tuple[float, float, float, float]]]],
        deg: float,
    ) -> Shape:
        ...

    @abstractmethod
    def genCirclePolySweep(
        self,
        rad: float,
        path: list[tuple[float, float, float]],
    ) -> Shape:
        ...

    @abstractmethod
    def genTextZ(
        self,
        txt: str,
        fontSize: float,
        tck: float,
        font: str,
    ):
        ...
        
    @abstractmethod
    def getJoinCutTol(self):
        ...

    def test(self, path: str):
        objs = []

        box = self.genBox(10, 10, 2).mv(0, 0, -10)
        ball = self.genBall(5).scale(1, 2, 1)
        coneZ = self.genConeZ(10, 10, 5).mv(0, 0, 10)
        coneX = self.genConeX(10, 1, 2)
        rod = self.genRodZ(20, 1)
        obj1 = box.join(ball).join(coneZ).join(rod).cut(coneX)
        coneX.remove()
        obj1 = obj1.mv(10, 10, 11)
        objs.append(obj1)

        rx = self.genRodX(10, 3)
        ry = self.genRodY(10, 3)
        rz = self.genRodZ(10, 3)
        obj2 = rx.join(ry).join(rz).mv(10, -10, 5)
        objs.append(obj2)

        rr1 = self.genRndRodX(10, 3).scale(.5, 1, 1).mv(0, -20, 0)
        rr2 = self.genRndRodX(10, 3).scale(1, .5, 1).mv(0, 0, 0)
        rr3 = self.genRndRodX(10, 3).scale(1, 1, .5).mv(0, 20, 0)
        rr4 = self.genRndRodY(50, 1)
        obj3 = rr1.join(rr2).join(rr3).join(rr4).mv(0, 0, -20)
        objs.append(obj3)

        rrx = self.genRndRodX(10, 3, .25)
        rry = self.genRndRodY(10, 3, .5)
        rrz = self.genRndRodZ(10, 3)
        obj4 = rrx.join(rry).join(rrz).half().mv(-10, 10, 5)
        objs.append(obj4)

        pe = self.genPolyExtrusionZ([(-10, -30), (10, -30), (10, 30), (-10, 30)], 10)
        tz = self.genTextZ("Hello World", 10, 5, "Arial").rotateZ(90).mv(0, 0, 10)
        obj5 = pe.join(tz).mv(30, -30, 0)
        mirror = obj5.mirrorXZ().mv(10, 0, 0)
        obj5 = obj5.join(mirror)
        objs.append(obj5)

        rndBox = self.genBox(10, 10, 10).filletByNearestEdges([(5, 0, 5)], 1)
        obj6 = rndBox.mv(-10, -10, 5)
        objs.append(obj6)

        dome = self.genLineSplineExtrusionZ(
            start = (0, 0),
            path = [
                (-5, 0), 
                (-5, 10), 
                (0, 10),
                [
                    (1, 10, 1, 0),
                    (5, 5, 0, -1),
                    (1, 0, -1, 0),
                ],
                (0, 0),
            ],
            ht = 5,
        )
        obj7 = dome.rotateY(-45).mv(-10, 15, 0)
        objs.append(obj7)

        donutStart = (60, .1)
        donutPath = [
            (60, 10), 
            (61, 10),
            [
                (62, 10, 1, 0),
                (65, 5, 0, -1),
                (62, .1, -1, 0),
            ],
            (60, .1),
        ]
        dome2 = self.genLineSplineRevolveX(donutStart, donutPath, 180).scale(1, 1, .5)
        dome3 = self.genLineSplineRevolveX(donutStart, donutPath, -180).mv(0, 0, self.getJoinCutTol())
        obj8 = dome2.join(dome3).mv(0, 0, -10)
        objs.append(obj8)

        obj9 = self.genCirclePolySweep(1, [(-20,0,0), (20,0,40), (40,20,40), (60,20,0)])
        objs.append(obj9)

        joined = None; [joined := obj if joined is None else joined.join(obj) for obj in objs]
        self.exportSTL(joined, path)