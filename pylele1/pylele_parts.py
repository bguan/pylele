from __future__ import annotations

import math
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import ShapeAPI, Shape, Fidelity, Implementation
from api.pylele_utils import radians, accumDiv
from api.pylele_api_constants import FIT_TOL, FILLET_RAD, ColorEnum
from pylele1.pylele_config import LeleConfig, WormConfig, PegConfig, \
    SEMI_RATIO

from random import randint

"""
    Abstract Base and Concrete Classes for all Gugulele parts
"""

class LelePart(ABC):
    @abstractmethod
    def gen(self) -> Shape:
        pass

    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[float, list[tuple[float, float, float]]] = {},
    ):
        self.cfg = cfg
        self.isCut = isCut
        self.joiners = joiners
        self.cutters = cutters
        self.fileNameBase = self.__class__.__name__ + ('_cut' if self.isCut else '')
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.api = ShapeAPI.get(cfg.impl, cfg.fidelity)

        self.shape = self.gen()
        
        for j in self.joiners:
            self.shape = self.shape.join(j.shape)
        for c in self.cutters:
            self.shape = self.shape.cut(c.shape)
        for rad in fillets:
            self.shape = self.shape.filletByNearestEdges(fillets[rad], rad)

    def cut(self, cutter: LelePart) -> LelePart:
        self.shape = self.shape.cut(cutter.shape)
        return self

    def exportSTL(self, path: Union[str, Path] ) -> None:
        self.api.exportSTL(self.shape, str(path))

    def exportBest(self, path: Union[str, Path] ) -> None:
        self.api.exportBest(self.shape, str(path))
    
    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> LelePart:
        self.shape = self.shape.filletByNearestEdges(nearestPts, rad)
        return self

    def half(self) -> LelePart:
        self.shape = self.shape.half()
        return self

    def join(self, joiner: LelePart) -> LelePart:
        self.shape = self.shape.join(joiner.shape)
        return self

    def mirrorXZ(self) -> LelePart:
        mirror = self.shape.mirrorXZ()
        return mirror

    def mv(self, x: float, y: float, z: float) -> LelePart:
        self.shape = self.shape.mv(x, y, z)
        return self

    def show(self):
        return self.shape.show()


class Brace(LelePart):
    MAX_FRETS = 24

    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.WHITE

    def gen(self) -> Shape:
        scLen = self.cfg.scaleLen
        brdgZ = self.cfg.brdgZ
        chmFr = self.cfg.chmFront
        chmBk = self.cfg.chmBack
        chmWth = self.cfg.chmWth
        topRat = self.cfg.TOP_RATIO
        brace = self.api.genRndRodX(.5*(chmFr+chmBk), .4*chmWth*topRat, 1)\
            .scale(1, .25, 1)\
            .mv(scLen - .25*chmBk, 0, brdgZ)
        return brace


class Frets(LelePart):

    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        fbTck = self.cfg.FRETBD_TCK
        ntHt = self.cfg.NUT_HT
        ntWth = self.cfg.nutWth + fbTck/4 + .5  # to be wider than fretbd
        fWth = self.cfg.nutWth - 1  # to be narrower than fretbd
        scLen = self.cfg.scaleLen
        fbLen = self.cfg.fretbdLen
        fHt = self.cfg.FRET_HT
        maxFrets = self.cfg.MAX_FRETS
        wideAng = self.cfg.neckWideAng
        riseAng = self.cfg.fretbdRiseAng
        f0X = -fitTol if self.isCut else 0

        f0Top = self.api.genRndRodY(ntWth, ntHt, 1/4)
        f0TopCut = self.api.genBox(2*ntHt, 2*ntWth, fbTck).mv(0, 0, -fbTck/2)
        f0Top = f0Top.cut(f0TopCut).mv(f0X, 0, fbTck)
        f0Bot = self.api.genRndRodY(ntWth, ntHt, 1/4)
        f0BotCut = self.api.genBox(2*ntHt, 2*ntWth, fbTck).mv(0, 0, fbTck/2)
        f0Bot = f0Bot.cut(f0BotCut).scale(1, 1, fbTck/ntHt).mv(f0X, 0, fbTck)
        frets = f0Top.join(f0Bot)

        if not self.isCut:
            fx = 0
            gap = (scLen / 2) / accumDiv(1, 12, SEMI_RATIO)
            count = 0
            while (fx < (fbLen - gap - 2 * fHt)):
                fx = fx + gap
                fy = fWth / 2 + math.tan(radians(wideAng)) * fx
                fz = fbTck + math.tan(radians(riseAng)) * fx
                fret = self.api.genRodY(2 * fy, fHt).mv(fx, 0, fz)
                frets = frets.join(fret)
                gap = gap / SEMI_RATIO
                count += 1
                if (count > maxFrets):  # prevent runaway loop
                    break

        return frets


class FretboardDots(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = True, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.WHITE

    def gen(self) -> Shape:
        scLen = self.cfg.scaleLen
        fbLen = self.cfg.fretbdLen
        fbTck = self.cfg.FRETBD_TCK
        maxFrets = self.cfg.MAX_FRETS
        dep = self.cfg.EMBOSS_DEP
        wideAng = self.cfg.neckWideAng
        riseAng = self.cfg.fretbdRiseAng
        nutSGap = self.cfg.nutStrGap
        dotRad = self.cfg.dotRad
        fret2Dots = self.cfg.fret2Dots

        dots = None
        sgap = nutSGap
        # half length of fret 1
        flen = .5 * scLen / accumDiv(1, 12, SEMI_RATIO)
        n = 1
        acclen = flen
        while acclen < fbLen and n <= maxFrets:
            if n in fret2Dots:
                ht = fbTck + math.tan(radians(riseAng))*acclen
                pos = [0] if fret2Dots[n] == 1 \
                    else [-.5, .5] if fret2Dots[n] == 2 \
                    else [-1, 0, 1]
                for p in pos:
                    dot = self.api.genRodZ(
                        2 * dep, dotRad).mv(acclen - .5*flen, p*sgap, ht)
                    dots = dot if dots == None else dots.join(dot)

            sgap = .5 * acclen * math.tan(radians(wideAng)) + nutSGap
            flen /= SEMI_RATIO
            acclen += flen
            n += 1
        return dots


class Fretboard(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        cutAdj = FIT_TOL if self.isCut else 0
        fbLen = self.cfg.fretbdLen + 2*cutAdj
        fbWth = self.cfg.fretbdWth + 2*cutAdj
        fbTck = self.cfg.FRETBD_TCK + 2*cutAdj
        fbHt = self.cfg.fretbdHt + 2*cutAdj
        riseAng = self.cfg.fretbdRiseAng

        path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        fretbd = self.api.genPolyExtrusionZ(path, fbHt)

        if self.isCut:
            fretbd = fretbd.mv(0, 0, -self.cfg.joinCutTol)
        else:
            topCut = self.api.genBox(fbLen * 2, fbWth, fbHt)\
                .rotateY(-riseAng)\
                .mv(0, 0, fbTck + fbHt/2)
            fretbd = fretbd.cut(topCut)
            fretbd = fretbd.filletByNearestEdges([(fbLen, 0, fbHt)], fbTck/2)

        return fretbd

class FretboardSpines(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = True, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        cutAdj = FIT_TOL if self.isCut else 0
        fspTck = self.cfg.FRETBD_SPINE_TCK + 2*(self.cfg.joinCutTol if self.isCut else 0)
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spWth = self.cfg.SPINE_WTH + 2*cutAdj # to align with spine cuts
        fspLen = self.cfg.fbSpineLen + 2*cutAdj + 2*(self.cfg.joinCutTol if self.isCut else 0)
        # fspX = self.cfg.fbSpX
        fspX = self.cfg.NUT_HT

        fsp1 = self.api.genBox(fspLen, spWth, fspTck)\
            .mv(fspX + fspLen/2 - 2*cutAdj, spY1, -fspTck/2)
        fsp2 = self.api.genBox(fspLen, spWth, fspTck)\
            .mv(fspX + fspLen/2 - 2*cutAdj, spY2, -fspTck/2)
        return fsp1.join(fsp2)

class FretbdJoint(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        cutAdj = (FIT_TOL + self.cfg.joinCutTol) if self.isCut else 0
        fbHt = self.cfg.fretbdHt
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj # to align with spine cuts
        jntTck = .8*fbHt + 2*cutAdj
        jnt = self.api.genBox(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, jntTck/2)
        return jnt

class Neck(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = False,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.ORANGE

    def gen(self) -> Shape:
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.neckPath
        joinTol = self.cfg.joinCutTol
        neck = None
        if midTck > 0:
            neck = self.api.genPolyExtrusionZ(path, midTck).mv(0, 0, -midTck)
        
        neckCone = self.api.genConeX(nkLen, ntWth/2, nkWth/2)
        if True:
            coneCut = self.api.genBox(2*nkLen, 2*nkWth, 2*nkWth).mv(nkLen, 0, nkWth)
            neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, -midTck)
        else:
            coneCut = self.api.genBox(nkLen, nkWth, nkWth).mv(nkLen, 0, nkWth/2)
            neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, joinTol-midTck)
        neck = neckCone if neck == None else neck.join(neckCone)
        return neck


class NeckJoint(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.ORANGE

    def gen(self) -> Shape:
        cutAdj = (FIT_TOL + self.cfg.joinCutTol) if self.isCut else 0
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj
        jntTck = self.cfg.neckJntTck + 2*FIT_TOL + 2*self.cfg.joinCutTol # to match cut grooves for spines
        jnt = self.api.genBox(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, -jntTck/2)
        return jnt


class Head(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.ORANGE

    def gen(self) -> Shape:
        hdWth = self.cfg.headWth
        hdLen = self.cfg.headLen
        ntHt = self.cfg.NUT_HT
        fbTck = self.cfg.FRETBD_TCK
        spHt = self.cfg.SPINE_HT
        fspTck = self.cfg.FRETBD_SPINE_TCK
        topRat = self.cfg.HEAD_TOP_RATIO
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.headOrig
        path = self.cfg.headPath
        joinTol = self.cfg.joinCutTol

        hd = self.api.genLineSplineRevolveX(orig, path, -180)\
            .scale(1, 1, botRat).mv(0, 0, joinTol -midTck)
        
        if midTck > 0:
            midR = self.api.genLineSplineExtrusionZ(orig, path, midTck).mv(0, 0, -midTck)
            hd = hd.join(midR.mirrorXZ_and_join())

        if topRat > 0:
            top = self.api.genLineSplineRevolveX(orig, path, 180)\
                .scale(1, 1, topRat).mv(0, 0, -joinTol/2)
            hd = hd.join(top)

        topCut = self.api.genRodY(2*hdWth, hdLen)\
            .mv(-ntHt, 0, .8*hdLen + fbTck + ntHt)
        frontCut = self.api.genRodY(2*hdWth, .7*spHt)\
            .scale(.5, 1, 1).mv(-hdLen, 0, -fspTck - .65*spHt)
        hd = hd.cut(frontCut).cut(topCut)
        return hd


class Top(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.WHITE

    def gen(self) -> Shape:
        if self.isCut:
            origFidel = self.cfg.fidelity
            self.api.setFidelity(Fidelity.LOW)

        fitTol = FIT_TOL
        joinTol = self.cfg.joinCutTol
        cutAdj = (fitTol + joinTol) if self.isCut else 0
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.extMidTopTck + cutAdj
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyCutPath if self.isCut else self.cfg.bodyPath
        top = self.api.genLineSplineRevolveX(bOrig, bPath, 180).scale(1, 1, topRat)
        if midTck > 0:
            top = top.mv(0, 0, midTck -joinTol)
            midR = self.api.genLineSplineExtrusionZ( bOrig, bPath, midTck )
            midR = midR.mv(0,0,-midTck)
            top = top.join(midR.mirrorXZ_and_join())

        if self.isCut:
            self.api.setFidelity(origFidel)

        return top


class Body(LelePart):
    def __init__(self,
        cfg: LeleConfig, 
        isCut: bool = False,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.ORANGE

    def gen(self):
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath
        joinTol = self.cfg.joinCutTol

        bot = self.api.genLineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, botRat)
        if midTck > 0:
            bot = bot.mv(0, 0, -midTck +joinTol)
            midR = self.api.genLineSplineExtrusionZ(bOrig, bPath, midTck)
            midR = midR.mv(0,0,-midTck)
            bot = bot.join(midR.mirrorXZ_and_join())
        return bot

    
class Rim(LelePart):
    def __init__(self,
        cfg: LeleConfig, 
        isCut: bool = False, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.WHITE
        
    def gen(self):
        joinTol = self.cfg.joinCutTol
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        scLen = self.cfg.scaleLen
        rad = self.cfg.chmWth/2 + self.cfg.rimWth
        tck = self.cfg.RIM_TCK + 2*cutAdj
        frontWthRatio = (self.cfg.chmFront + self.cfg.rimWth)/rad
        backWthRatio = (self.cfg.chmBack + self.cfg.rimWth)/rad
        rimFront = self.api.genHalfDisc(rad, True, tck).scale(frontWthRatio, 1, 1)
        rimBack = self.api.genHalfDisc(rad, False, tck).scale(backWthRatio, 1, 1)
        return rimFront.mv(scLen, 0, joinTol-tck/2).join(rimBack.mv(scLen-joinTol, 0, joinTol-tck/2))
    

    
class Chamber(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)

    def gen(self) -> Shape:

        origFidel = self.api.fidelity
        self.api.setFidelity(Fidelity.LOW)

        scLen = self.cfg.scaleLen
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        lift = self.cfg.chmLift
        rotY = self.cfg.chmRot
        joinTol = self.cfg.joinCutTol
        rad = self.cfg.chmWth/2
        frontRat = self.cfg.chmFront/rad
        backRat = self.cfg.chmBack/rad
        topChmRat = topRat * 3/4

        topFront = self.api.genQuarterBall(rad, True, True)\
            .scale(frontRat, 1, topChmRat).mv(joinTol, 0, -joinTol)
        topBack = self.api.genQuarterBall(rad, True, False)\
            .scale(backRat, 1, topChmRat).mv(0, 0, -joinTol)
        botFront = self.api.genQuarterBall(rad, False, True)\
            .scale(frontRat, 1, botRat).mv(joinTol, 0, 0)
        botBack = self.api.genQuarterBall(rad, False, False)\
            .scale(backRat, 1, botRat)
        chm = topFront.join(topBack).join(botFront).join(botBack)

        if rotY != 0:
            chm = chm.rotateY(rotY)

        if lift != 0:
            chm = chm.mv(0, 0, lift)

        chm = chm.mv(scLen, 0, 0)

        self.api.setFidelity(origFidel)

        return chm



class Soundhole(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = True, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)

    def gen(self) -> Shape:
        x = self.cfg.sndholeX
        y = self.cfg.sndholeY
        midTck = self.cfg.extMidTopTck
        minRad = self.cfg.sndholeMinRad
        maxRad = self.cfg.sndholeMaxRad
        ang = self.cfg.sndholeAng
        bodyWth = self.cfg.bodyWth

        hole = self.api.genRodZ(bodyWth + midTck, minRad)\
            .scale(1, maxRad/minRad, 1)\
            .rotateZ(ang).mv(x, y, -midTck)
        return hole


class Bridge(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = False,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        scLen = self.cfg.scaleLen
        strRad = self.cfg.STR_RAD
        brdgWth = self.cfg.brdgWth + (2*fitTol if self.isCut else 0)
        brdgLen = self.cfg.brdgLen + (2*fitTol if self.isCut else 0)
        brdgHt = self.cfg.brdgHt
        brdgZ = self.cfg.brdgZ

        brdg = self.api.genBox(brdgLen, brdgWth, brdgHt).mv(
            scLen, 0, brdgZ + brdgHt/2)
        if not self.isCut:
            cutRad = brdgLen/2 - strRad
            cutHt = brdgHt - 2
            cutScaleZ = cutHt/cutRad
            frontCut = self.api.genRodY(2*brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen - cutRad - strRad, 0, brdgZ + brdgHt)
            backCut = self.api.genRodY(2*brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen + cutRad + strRad, 0, brdgZ + brdgHt)
            brdgTop = self.api.genRodY(brdgWth, strRad).mv(scLen, 0, brdgZ + brdgHt)
            brdg = brdg.cut(frontCut).cut(backCut).join(brdgTop)
        return brdg


class Guide(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = False,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        nStrs = self.cfg.numStrs
        sR = self.cfg.STR_RAD
        gdR = self.cfg.GUIDE_RAD + cutAdj
        gdX = self.cfg.guideX
        gdZ = self.cfg.guideZ
        gdHt = self.cfg.guideHt
        gdWth = self.cfg.guideWth
        gdGap = self.cfg.guidePostGap

        guide = None if self.isCut else \
            self.api.genRndRodY(
                (gdWth - .5*gdGap + sR + 2*gdR) if nStrs > 1 else 6*gdR,
                1.1*gdR, 1,
            ).mv(gdX, 0, gdZ + gdHt)
        for y in self.cfg.guideYs:
            post = self.api.genRodZ(gdHt, gdR)
            post = post.mv(gdX, y, gdZ + gdHt/2)
            guide = post if guide == None else guide.join(post)
        return guide


class Peg(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.GRAY

    def gen(self) -> Shape:
        cutAdj = FIT_TOL if self.isCut else 0
        cfg: PegConfig = self.cfg.tnrCfg
        strRad = self.cfg.STR_RAD + cutAdj
        holeHt = cfg.holeHt
        majRad = cfg.majRad + cutAdj
        minRad = cfg.minRad + cutAdj
        midTck = cfg.midTck
        botLen = cfg.botLen
        btnRad = cfg.btnRad + cutAdj
        topCutTck = 100 if self.isCut else 2  # big value for cutting
        botCutTck = botLen - midTck/3 if self.isCut else 2

        top = self.api.genRodZ(topCutTck, majRad).mv(0, 0, topCutTck/2)

        if not self.isCut:
            stemHt = holeHt + 4*strRad
            stem = self.api.genRodZ(stemHt, minRad/2).mv(0, 0, stemHt/2)
            hole = self.api.genRodX(2*minRad, strRad).mv(0, 0, holeHt)
            stem = stem.cut(hole)
            top = top.join(stem)

        mid = self.api.genRodZ(midTck, minRad).mv(0, 0, -midTck/2)

        if self.isCut:
            btnConeTck = botLen - midTck - 2*cutAdj
            btn = self.api.genConeZ(btnConeTck, btnRad, majRad)\
                .mv(0, 0, -midTck - btnConeTck)
            bot = self.api.genRodZ(botCutTck, btnRad)\
                .mv(0, 0, -botLen - botCutTck/2 + 2*cutAdj)
            botEnd = self.api.genBall(btnRad)\
                .scale(1, 1, .5 if self.cfg.sepEnd else 1)\
                .mv(0, 0, -botLen - botCutTck)
            bot = bot.join(botEnd)
        else:
            bot = self.api.genRodZ(botCutTck, majRad)\
                .mv(0, 0, -midTck - botCutTck/2)
            stem = self.api.genRodZ(botLen, minRad/2)\
                .mv(0, 0, -midTck - botLen/2)
            bot = bot.join(stem)
            btn = self.api.genBox(btnRad*2, btnRad/2, btnRad)\
                .mv(0, 0, -midTck - botLen - botCutTck/2 + btnRad/2)

        peg = top.join(mid).join(btn).join(bot)

        return peg


class Worm(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.GRAY

    def gen(self) -> Shape:
        cutAdj = FIT_TOL if self.isCut else 0
        cfg: WormConfig = self.cfg.tnrCfg
        sltLen = cfg.slitLen
        sltWth = cfg.slitWth
        drvRad = cfg.driveRad + cutAdj
        dskRad = cfg.diskRad + cutAdj
        dskTck = cfg.diskTck + 2*cutAdj
        axlRad = cfg.axleRad + cutAdj
        axlLen = cfg.axleLen + 2*cutAdj
        offset = cfg.driveOffset
        drvLen = cfg.driveLen + 2*cutAdj

        # Note: Origin is middle of slit, near tip of axle
        axlX = 0
        axlY = -.5  # sltWth/2 -axlLen/2
        axlZ = 0
        axl = self.api.genRodY(axlLen, axlRad).mv(axlX, axlY, axlZ)
        if self.isCut:
            axlExtCut = self.api.genBox(
                100, axlLen, 2*axlRad).mv(50 + axlX, axlY, axlZ)
            axl = axl.join(axlExtCut)

        dskX = axlX
        dskY = axlY - axlLen/2 - dskTck/2
        dskZ = axlZ
        dsk = self.api.genRodY(dskTck, dskRad).mv(dskX, dskY, dskZ)
        if self.isCut:
            dskExtCut = self.api.genBox(
                100, dskTck, 2*dskRad).mv(50 + dskX, dskY, dskZ)
            dsk = dsk.join(dskExtCut)

        drvX = dskX
        drvY = dskY
        drvZ = dskZ + offset
        drv = self.api.genRodX(drvLen, drvRad).mv(drvX, drvY, drvZ)
        if self.isCut:
            drvExtCut = self.api.genRodX(100, drvRad).mv(50 + drvX, drvY, drvZ)
            drv = drv.join(drvExtCut)

        worm = axl.join(dsk).join(drv)

        if self.isCut:
            slit = self.api.genBox(sltLen, sltWth, 100).mv(0, 0, 50 - 2*axlRad)
            worm = worm.join(slit)

        return worm

class WormKey(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.GRAY

    def gen(self) -> Shape:
        isBlender = self.cfg.impl == Implementation.BLENDER
        joinTol = self.cfg.joinCutTol
        tailX = self.cfg.tailX
        txyzs = self.cfg.tnrXYZs
        wcfg: WormConfig = self.cfg.tnrCfg
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        btnHt = wcfg.buttonHt + 2*cutAdj
        btnWth = wcfg.buttonWth + 2*cutAdj
        btnTck = wcfg.buttonTck + 2*cutAdj
        kbHt = wcfg.buttonKeybaseHt + 2*cutAdj
        kbRad = wcfg.buttonKeybaseRad + cutAdj
        kyRad = wcfg.buttonKeyRad + cutAdj
        kyLen = wcfg.buttonKeyLen + 2*cutAdj

        key = self.api.genPolyRodX(kyLen, kyRad, 6).mv(joinTol -kyLen/2 -kbHt -btnHt, 0, 0)
        base = self.api.genPolyRodX(kbHt, kbRad, 36) if isBlender else self.api.genRodX(kbHt, kbRad)
        base = base.mv(-kbHt/2 -btnHt, 0, 0)
        btn = self.api.genBox(100 if self.isCut else btnHt, btnTck, btnWth)\
            .mv(50 -btnHt if self.isCut else -btnHt/2, 0, 0)
        
        if self.isCut:
            btnExtCut = self.api.genRodX(100 if self.isCut else btnHt, btnWth/2)\
                .scale(1, .5, 1)\
                .mv(50 -btnHt if self.isCut else -btnHt/2, btnTck/2, 0)
            btn = btn.join(btnExtCut)
        else:
            btn = btn.filletByNearestEdges([], FILLET_RAD)

        btn = btn.join(base).join(key)
        maxTnrY = max([y for _, y, _ in txyzs])
        btn = btn.mv(tailX - joinTol, maxTnrY + btnTck -1, -1 -btnWth/2)
        return btn


class Tuners(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = (128, 128, 128)

    def gen(self) -> Shape:

        tXYZs = self.cfg.tnrXYZs
        # isPeg = self.cfg.tnrCfg.is_peg()
        # isWorm = self.cfg.tnrCfg.is_worm()
        tnrs = None
        for txyz in tXYZs:
            tnr = Peg(self.cfg, isCut=self.isCut) if self.cfg.tnrCfg.is_peg() \
                else Worm(self.cfg, isCut=self.isCut) if self.cfg.tnrCfg.is_worm() \
                else None
            if tnr != None:
                tnr = tnr.mv(txyz[0], txyz[1], txyz[2]).shape
                tnrs = tnr if tnrs == None else tnrs.join(tnr)

        return tnrs


class Spines(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.CARBON

    def gen(self) -> Shape:
        cutAdj = (FIT_TOL + self.cfg.joinCutTol) if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen+ 2*cutAdj
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spHt = self.cfg.SPINE_HT + 2*cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK  + 2*self.cfg.joinCutTol

        sp1 = self.api.genBox(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY1, -fspTck - spHt/2)
        sp2 = self.api.genBox(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY2, -fspTck - spHt/2)
        return sp1.join(sp2)


class Strings(LelePart):
    def __init__(self,
        cfg: LeleConfig, 
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.LITE_GRAY

    def gen(self) -> Shape:
        if self.isCut:
            origFidel = self.cfg.fidelity
            self.api.setFidelity(Fidelity.MEDIUM)

        cutAdj = FIT_TOL if self.isCut else 0
        srad = self.cfg.STR_RAD + cutAdj
        paths = self.cfg.stringPaths

        strs = None
        for p in paths:
            str = self.api.genCirclePolySweep(srad, p)
            strs = str if strs == None else strs.join(str)

        if self.isCut:
            self.api.setFidelity(origFidel)

        return strs


class Texts(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)

    def gen(self) -> Shape:
        if self.isCut:
            origFidel = self.api.fidelity
            self.api.setFidelity(Fidelity.LOW)

        scLen = self.cfg.scaleLen
        backRat = self.cfg.CHM_BACK_RATIO
        # dep = self.cfg.EMBOSS_DEP
        tsf = self.cfg.txtSzFonts
        # txtTck = self.cfg.TEXT_TCK
        bodyWth = self.cfg.bodyWth
        botRat = self.cfg.BOT_RATIO
        midBotTck = self.cfg.extMidBotTck
        # cutTol = self.cfg.joinCutTol
        txtTck = botRat * bodyWth/2 + midBotTck + 2

        allHt = sum([1.2*size for _, size, _ in tsf])
        tx = 1.05*scLen - allHt/(1+backRat)
        ls: Shape = None
        for txt, sz, fnt in tsf:
            if not txt is None and not fnt is None:
                l = self.api.genTextZ(txt, sz, txtTck, fnt) \
                    .rotateZ(90).mv(tx + sz/2, 0, 0) #txtTck/2)
                ls = l if ls is None else ls.join(l)
            tx += sz

        if self.isCut:
            # Orig impl is ls = ls.mirrorXZ() but Blender text mirroring can lead to invalid meshes
            ls = ls.rotateX(180) 
            if self.api.getImplementation() != Implementation.CAD_QUERY:
                ls = ls.mv(0, 0, -txtTck) # HACK: Blender Text rotation is wonky
            bodyCut = Body(self.cfg, isCut=True).mv(0, 0, self.cfg.EMBOSS_DEP)
            ls = ls.cut(bodyCut.shape)
            self.api.setFidelity(origFidel)
        return ls

class TailEnd(LelePart):
    def __init__(self,
        cfg: LeleConfig,
        isCut: bool = True,
        joiners: list[LelePart] = [],
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = ColorEnum.DARK_GRAY

    def gen(self) -> Shape:
        cfg = self.cfg
        joinTol = cfg.joinCutTol
        cutAdj = (FIT_TOL + 2*joinTol) if self.isCut else 0
        tailX = cfg.tailX
        chmBackX = cfg.scaleLen + cfg.chmBack
        tailLen = tailX - chmBackX + 2*cutAdj
        endWth = cfg.endWth + 2*cutAdj
        botRat = cfg.BOT_RATIO
        midBotTck = cfg.extMidBotTck + 2*cutAdj
        rimWth = cfg.rimWth+ 2*cutAdj
        
        top = None
        if midBotTck > 0:
            extTop = self.api.genBox(10 if self.isCut else rimWth, endWth, midBotTck)\
                .mv(tailX + (5 - rimWth if self.isCut else -rimWth/2), 0, -midBotTck/2)
            inrTop = self.api.genBox(2*tailLen, endWth -2*rimWth, midBotTck)\
                .mv(tailX -rimWth -tailLen, 0, -midBotTck/2)
            top = extTop.join(inrTop)
        
        extBot = self.api.genRodX(10 if self.isCut else rimWth, endWth/2).scale(1, 1, botRat)\
            .mv(tailX + (5 - rimWth if self.isCut else -rimWth/2), 0, -midBotTck)
        inrBot = self.api.genRodX(2*tailLen, endWth/2 - rimWth).scale(1, 1, botRat)\
            .mv(tailX - rimWth -tailLen, 0, -midBotTck)
        topCut = self.api.genBox(2000, 2000, 2000).mv(0,0,1000)
        bot = extBot.join(inrBot).cut(topCut)
        if top is None:
            tail = bot
        else:
            tail = top.join(bot)
        return tail