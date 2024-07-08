from __future__ import annotations

import bpy_api
import cq_api
import math
from abc import ABC, abstractmethod
from pylele_api import ShapeAPI, Shape
from pylele_config import Fidelity, Implementation, LeleConfig, WormConfig, PegConfig, \
    FIT_TOL, SEMI_RATIO, CARBON, GRAY, LITE_GRAY,DARK_GRAY, ORANGE, WHITE, accumDiv
from pylele_utils import radians
from random import randint

_cq_api: ShapeAPI = None
_blender_api: ShapeAPI = None
_trimesh_api: ShapeAPI = None
def getShapeAPI(impl: Implementation, fidelity: Fidelity) -> ShapeAPI:
    global _cq_api, _blender_api, _trimesh_api
    match impl:
        case Implementation.CAD_QUERY:
            if _cq_api == None:
                _cq_api = cq_api.CQShapeAPI(fidelity.exportTol())
            return _cq_api
        case Implementation.BLENDER:
            if _blender_api == None:
                _blender_api = bpy_api.BlenderShapeAPI(fidelity.smoothingSegments())
            return _blender_api
        case Implementation.TRIMESH:
            return None

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
        self.fileNameBase = self.__class__.__name__
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.api = getShapeAPI(cfg.impl, cfg.fidelity)

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

    def exportSTL(self, path: str) -> None:
        self.api.exportSTL(self.shape, path)
    
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
        self.color = WHITE

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
        self.color = DARK_GRAY

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
        self.color = WHITE

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
        self.color = DARK_GRAY

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        fbLen = self.cfg.fretbdLen + 2*cutAdj
        fbWth = self.cfg.fretbdWth + 2*cutAdj
        fbTck = self.cfg.FRETBD_TCK + 2*cutAdj
        fbHt = self.cfg.fretbdHt + 2*cutAdj
        riseAng = self.cfg.fretbdRiseAng

        path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        fretbd = self.api.genPolyExtrusionZ(path, fbHt)

        if not self.isCut:
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
        self.color = DARK_GRAY

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        fspTck = self.cfg.FRETBD_SPINE_TCK
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spWth = self.cfg.SPINE_WTH + 2*cutAdj # to align with spine cuts
        fspLen = self.cfg.fbSpineLen + 2*cutAdj
        fspX = self.cfg.fbSpX

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
        self.color = DARK_GRAY

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
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
        self.color = ORANGE

    def gen(self) -> Shape:
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.neckPath
        neck = None
        if midTck > 0:
            neck = self.api.genPolyExtrusionZ(path, midTck).mv(0, 0, -midTck)
        neckCone = self.api.genConeX(nkLen, ntWth/2, nkWth/2)
        coneCut = self.api.genBox(nkLen, nkWth, nkWth).mv(nkLen/2, 0, nkWth/2)
        neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, -midTck)
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
        self.color = ORANGE

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj
        jntTck = self.cfg.neckJntTck + 2*fitTol # to match cut grooves for spines
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
        self.color = ORANGE

    def gen(self) -> Shape:
        hdWth = self.cfg.headWth
        hdLen = self.cfg.HEAD_LEN
        ntHt = self.cfg.NUT_HT
        fbTck = self.cfg.FRETBD_TCK
        spHt = self.cfg.SPINE_HT
        fspTck = self.cfg.FRETBD_SPINE_TCK
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.headOrig
        path = self.cfg.headPath

        hd = self.api.genLineSplineRevolveX(orig, path, 180)\
            .scale(1, 1, botRat).mv(0, 0, -midTck)

        if topRat > 0:
            top = self.api.genLineSplineRevolveX(orig, path, -180)\
                .scale(1, 1, topRat)
            hd = hd.join(top)

        if midTck > 0:
            midL = self.api.genLineSplineExtrusionZ(orig, path, midTck)\
                .mv(0, 0, -midTck)
            midR = midL.mirrorXZ()
            hd = hd.join(midL).join(midR)

        topCut = self.api.genRndRodY(2*hdWth, hdLen, 1)\
            .mv(-ntHt, 0, .75*hdLen + fbTck + ntHt)
        frontCut = self.api.genRndRodY(2*hdWth, .65*spHt, 1)\
            .scale(.5, 1, 1).mv(-hdLen, 0, -fspTck - .6*spHt)
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
        self.color = WHITE

    def gen(self) -> Shape:
        fitTol = FIT_TOL
        joinTol = self.cfg.joinCutTol
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.EXT_MID_TOP_TCK
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyCutPath if self.isCut else self.cfg.bodyPath

        top = self.api.genLineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, topRat)
        if midTck > 0 or self.isCut:
            top = top.mv(0, 0, (midTck+fitTol if self.isCut else midTck) -joinTol)
            midL = self.api.genLineSplineExtrusionZ(
                bOrig, bPath, midTck+fitTol if self.isCut else midTck)
            midR = midL.mirrorXZ()
            top = top.join(midL.mv(0, joinTol/2, 0)).join(midR.mv(0, -joinTol/2, 0))
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
        self.color = ORANGE

    def gen(self):
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.extMidBotTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath
        joinTol = self.cfg.joinCutTol

        bot = self.api.genLineSplineRevolveX(bOrig, bPath, 180).scale(1, 1, botRat)
        if midTck > 0:
            bot = bot.mv(0, 0, -midTck + joinTol)
            midL = self.api.genLineSplineExtrusionZ(bOrig, bPath, midTck)
            midR = midL.mirrorXZ()
            bot = bot.join(midL.mv(0, joinTol/2, 0)).join(midR.mv(0, -joinTol/2, 0))
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
        self.color = WHITE
        
    def gen(self):
        cutAdj = FIT_TOL if self.isCut else 0
        orig = self.cfg.rimCutOrig if self.isCut else self.cfg.rimOrig
        path = self.cfg.rimCutPath if self.isCut else self.cfg.rimPath
        tck = self.cfg.RIM_TCK + 2*cutAdj

        rimL = self.api.genLineSplineExtrusionZ(orig, path, tck)\
            .mv(0, 0, -tck)
        rimR = rimL.mirrorXZ()
        return rimL.join(rimR)
    
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
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.chmOrig
        path = self.cfg.chmPath
        lift = self.cfg.chmLift
        rotY = self.cfg.chmRot
        joinTol = self.cfg.joinCutTol

        top = self.api.genLineSplineRevolveX(orig, path, -180).scale(1, 1, topRat/2)
        bot = self.api.genLineSplineRevolveX(orig, path, 180).scale(1, 1, botRat)
        chm = top.join(bot.mv(0, 0, joinTol))

        if rotY != 0:
            chm = chm.mv(-orig[0], -orig[1], 0)
            chm = chm.rotateY(rotY)
            chm = chm.mv(orig[0], orig[1], 0)

        if lift != 0:
            chm = chm.mv(0, 0, lift)

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
        midTck = self.cfg.EXT_MID_TOP_TCK
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
        self.color = DARK_GRAY

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
        self.color = DARK_GRAY

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
        self.color = GRAY

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
        self.color = GRAY

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
        self.color = GRAY

    def gen(self) -> Shape:
        tailX = self.cfg.tailX
        txyzs = self.cfg.tnrXYZs
        wcfg: WormConfig = self.cfg.tnrCfg
        cutAdj = FIT_TOL if self.isCut else 0
        btnHt =wcfg.buttonHt + 2*cutAdj
        btnWth = wcfg.buttonWth + 2*cutAdj
        btnTck = wcfg.buttonTck + 2*cutAdj
        kbHt = wcfg.buttonKeybaseHt + 2*cutAdj
        kbRad = wcfg.buttonKeybaseRad + cutAdj
        kyRad = wcfg.buttonKeyRad + cutAdj
        kyLen = wcfg.buttonKeyLen + 2*cutAdj

        key = self.api.genRodX(kyLen, kyRad).mv(-kyLen/2 -kbHt -btnHt, 0, 0)
        base = self.api.genRodX(kbHt, kbRad).mv(-kbHt/2 -btnHt, 0, 0)
        btn = self.api.genBox(100 if self.isCut else btnHt, btnTck, btnWth)\
            .mv(50 -btnHt if self.isCut else -btnHt/2, 0, 0)
        if self.isCut:
            btnExtCut = self.api.genRodX(100 if self.isCut else btnHt, btnWth/2)\
                .scale(1, .5, 1)\
                .mv(50 -btnHt if self.isCut else -btnHt/2, btnTck/2, 0)
            btn = btn.join(btnExtCut)
        btn = btn.join(base).join(key)
        maxTnrY = max([y for _, y, _ in txyzs])
        btn = btn.mv(tailX, maxTnrY + btnTck, -1 -btnWth/2)
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
        isPeg = isinstance(self.cfg.tnrCfg, PegConfig)
        isWorm = isinstance(self.cfg.tnrCfg, WormConfig)
        tnrs = None
        for txyz in tXYZs:
            tnr = Peg(self.cfg, isCut=self.isCut) if isPeg \
                else Worm(self.cfg, isCut=self.isCut) if isWorm \
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
        self.color = CARBON

    def gen(self) -> Shape:
        cutAdj = FIT_TOL if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen+ 2*cutAdj
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spHt = self.cfg.SPINE_HT + 2*cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK

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
        self.color = LITE_GRAY

    def gen(self) -> Shape:
        cutAdj = FIT_TOL if self.isCut else 0
        srad = self.cfg.STR_RAD + cutAdj
        paths = self.cfg.stringPaths

        strs = None
        for p in paths:
            str = self.api.genCirclePolySweep(srad, p)
            strs = str if strs == None else strs.join(str)
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
        scLen = self.cfg.scaleLen
        backRat = self.cfg.CHM_BACK_RATIO
        dep = self.cfg.EMBOSS_DEP
        tsf = self.cfg.txtSzFonts
        txtTck = self.cfg.TEXT_TCK
        bodyWth = self.cfg.bodyWth
        botRat = self.cfg.BOT_RATIO
        midBotTck = self.cfg.extMidBotTck

        txtZ = -botRat * bodyWth/2 - midBotTck - 1
        allHt = sum([1.2*size for _, size, _ in tsf])
        tx = scLen - allHt/(1+backRat)
        ls: Shape = None
        for txt, sz, fnt in tsf:
            if not txt is None and not fnt is None:
                l = self.api.genTextZ(txt, sz, txtTck, fnt) \
                    .rotateZ(90).mirrorXZ().mv(tx + sz/2, 0, txtZ)
                ls = l if ls is None else ls.join(l)
            tx += sz
        botCut = Body(self.cfg, isCut=True)
        return ls.cut(botCut.shape).mv(0, 0, dep)

class TailEnd(LelePart):
    def __init__(self, 
        cfg: LeleConfig, 
        isCut: bool = True, 
        joiners: list[LelePart] = [], 
        cutters: list[LelePart] = [],
        fillets: dict[tuple[float, float, float], float] = {},
    ):
        super().__init__(cfg, isCut, joiners, cutters, fillets)
        self.color = DARK_GRAY

    def gen(self) -> Shape:
        cfg = self.cfg
        cutAdj = FIT_TOL if self.isCut else 0
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