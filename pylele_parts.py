import math
import cq_api as api
from typing import Union

"""
    Global Constants and Util Functions
"""

SEMI_RATIO = 2**(1/12)
SOPRANO_SCALE_LEN = 330


def radians(deg):
    return deg * math.pi / 180


def degrees(rad):
    return rad*180 / math.pi


def accumDiv(x: float, n: int, div: float):
    return 0 if n <= 0 else x + accumDiv(x / div, n - 1, div)


"""
    Classes
"""

class PegConfig:
    def __init__(
        self,
        majRad: float = 8,
        minRad: float = 4,
        botLen: float = 15,
        btnRad: float = 12,
        midTck: float = 10,
        holeHt: float = 8,
    ):
        self.majRad = majRad
        self.minRad = minRad
        self.botLen = botLen
        self.btnRad = btnRad
        self.midTck = midTck
        self.holeHt = holeHt
        self.maxRad = max(majRad, btnRad)


FRICTION_PEG_CFG = PegConfig()


class LeleConfig:
    BOT_RATIO = .65
    BRIDGE_HT = 8
    CHM_BACK_RATIO = .5  # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EXT_MID_TOP_TCK = .5
    EXT_MID_BOT_TCK = 3
    FIT_TOL = .1
    FILLET_RAD = .4
    FRET_HT = 1
    FRETBD_RATIO = 0.65  # to scaleLen
    FRETBD_SPINE_TCK = 1.5
    FRETBD_TCK = 2
    FRETBD_RISE_ANG = 1.2
    GUIDE_RAD = 1.5
    GUIDE_SET = 2
    HEAD_WTH_RATIO = 1.15  # to nutWth
    HEAD_LEN_RATIO = .35  # to nutWth
    NECK_JNT_RATIO = .8  # to fretbdlen - necklen
    NECK_RATIO = .55  # to scaleLen
    NECK_WIDE_ANG = 1
    NUT_HT = 1.5
    SPINE_HT = 10
    SPINE_WTH = 2
    STR_RAD = 0.5
    TOP_RATIO = .1

    def __init__(
        self,
        scaleLen: float,
        sepTop: bool = False,
        sepNeck: bool = False,
        sepFretbd: bool = False,
        sepBrdg: bool = False,
        sepGuide: bool = False,
        chmTck: float = 4,
        chmLift: float = 1.5,
        flatWth: float = 0,
        numStrs: int = 4,
        strGap: float = 9,
        action: float = 3,
        pegCfg: PegConfig = FRICTION_PEG_CFG,
    ):
        # General configs
        self.scaleLen = scaleLen
        self.sepTop = sepTop
        self.sepNeck = sepNeck
        self.sepFretbd = sepFretbd
        self.sepBrdg = sepBrdg
        self.sepGuide = sepGuide
        self.numStrs = numStrs
        self.isOddStrs = numStrs % 2 == 1
        self.flatWth = flatWth
        self.strGap = strGap
        self.action = action
        self.nutWth = numStrs * strGap
        self.pegCfg = pegCfg
        self.brdgWth = self.nutWth + \
            2 * math.tan(radians(self.NECK_WIDE_ANG)) * self.scaleLen
        self.neckLen = scaleLen * self.NECK_RATIO
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        
        # Neck configs
        self.neckWth = self.nutWth + \
            2 * math.tan(radians(self.NECK_WIDE_ANG)) * self.neckLen
        self.neckPath = [
            (0, -self.nutWth/2), (self.neckLen, -self.neckWth/2),
            (self.neckLen, self.neckWth/2), (0, self.nutWth/2)
        ]
        self.neckJntLen = self.NECK_JNT_RATIO*(self.fretbdLen -self.neckLen)
        neckDX = self.FIT_TOL
        neckDY = neckDX * math.tan(radians(self.NECK_WIDE_ANG))

        # Fretboard configs
        self.fretbdWth = self.nutWth + \
            2 * math.tan(radians(self.NECK_WIDE_ANG)) * self.fretbdLen
        self.fretbdHt = self.FRETBD_TCK + \
            math.tan(radians(self.FRETBD_RISE_ANG)) * self.fretbdLen
        
        def genFbPath(isCut: bool = False) -> list[tuple[float, float]]:
            cutAdj = self.FIT_TOL if isCut else 0
            return [
                (-cutAdj, -self.nutWth/2 - cutAdj),
                (self.fretbdLen + 2*cutAdj, -self.fretbdWth/2 - cutAdj),
                (self.fretbdLen + 2*cutAdj, self.fretbdWth/2 + cutAdj),
                (-cutAdj, self.nutWth/2 + cutAdj),
            ]

        self.fbPath = genFbPath()
        self.fbCutPath = genFbPath(isCut=True)
        self.fbSpX = self.NUT_HT
        self.fbSpineLen = self.neckLen - self.NUT_HT + self.neckJntLen

        # Chamber Configs 
        self.chmTck = chmTck
        self.chmLift = chmLift
        self.chmFront = scaleLen - self.fretbdLen - chmTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        self.chmWth = self.brdgWth * 3
        self.chmPath = [
            [
                (scaleLen - self.chmFront, 0, 0, -1),
                (scaleLen - .6*self.chmFront, -.4*self.chmWth, 1, -.4),
                (scaleLen, -self.chmWth/2, 1, 0),
                (scaleLen + self.chmBack, 0, 0, 1),
            ]
        ]
        
        # Head configs
        self.headWth = self.nutWth * self.HEAD_WTH_RATIO
        self.headLen = self.nutWth * self.HEAD_LEN_RATIO
        self.headPath = [
            (0, -self.nutWth/2),
            (-neckDX, -self.nutWth/2 + neckDY),
            [
                (-neckDX, -self.nutWth/2 + neckDY, -neckDX, neckDY),
                (-self.headLen/2, -self.headWth/2, -1, 0),
                (-self.headLen, 0, 0, 1),
            ],
            (0, 0)
        ]

        # Body Configs 
        self.bodyWth = self.chmWth + 2 * chmTck
        self.bodyFrontLen = scaleLen - self.neckLen
        self.bodyBackLen = self.chmBack + chmTck + 2 * self.pegCfg.majRad
        self.bodyLen = self.bodyFrontLen + self.bodyBackLen
        self.fullLen = self.headLen + self.bodyLen
        
        def genBodyPath(isCut: bool = False) -> list[tuple[float, float]]:
            cutAdj = self.FIT_TOL if isCut else 0
            nkLen = self.neckLen - cutAdj
            nkWth = self.neckWth +2*cutAdj
            bWth = self.bodyWth +2*cutAdj
            bFrLen = self.bodyFrontLen +cutAdj
            bBkLen = self.bodyBackLen +cutAdj
            fWth = self.flatWth +2*cutAdj if flatWth > 0 else 0
            bodySpline = [
                (nkLen + neckDX, -nkWth/2 - neckDY, neckDX, -neckDY),
                (nkLen + .49*bFrLen, -.39*bWth, 1, -.41),
                (scaleLen, -bWth/2, 1, 0),
                (scaleLen + bBkLen, -fWth/2, 0, 1),
            ]
            if fWth > 0:
                bodySpline.append((scaleLen + bBkLen, 0, 0, 1))
            bodyPath = [
                (nkLen, -nkWth/2),
                (nkLen + neckDX, -nkWth/2 - neckDY),
                bodySpline,
                (nkLen, 0)
            ]
            return bodyPath
        
        self.bodyPath = genBodyPath()
        self.bodyCutPath = genBodyPath(isCut=True)
        
        # Soundhole Config
        self.sndholeX = scaleLen - .5*self.chmFront
        self.sndholeY = -(self.chmWth - self.fretbdWth)/2
        self.sndholeMaxRad = self.chmFront/3
        self.sndholeMinRad = self.sndholeMaxRad/4
        self.sndholeAng = degrees(
            math.atan(2 * self.bodyFrontLen/(self.chmWth - self.neckWth))
        )

        # Bridge configs
        f12Len = scaleLen/2
        f12Ht = self.FRETBD_TCK + \
            math.tan(radians(self.FRETBD_RISE_ANG)) * f12Len + \
            self.FRET_HT
        self.brdgZ = .5*self.bodyWth * self.TOP_RATIO + self.EXT_MID_TOP_TCK - 1
        self.brdgHt = f12Ht*2 - self.brdgZ
        self.brdgLen = strGap

        # Spine configs
        self.spineX = -self.headLen
        self.spineLen = self.headLen +self.scaleLen +self.chmBack +self.chmTck -1
        self.spineGap = strGap if self.isOddStrs else 2*strGap
        self.spineY1 = -self.spineGap/2
        self.spineY2 = self.spineGap/2
        self.spineCutFilletPts = [
            (0, self.spineY1, 0),
            (0, self.spineY2, 0),
        ]

        # Guide config
        self.guideX = self.scaleLen + self.chmBack
        self.guideZ = -self.GUIDE_SET + self.TOP_RATIO \
            * math.sqrt(self.bodyBackLen**2 - self.chmBack**2)
        self.guideHt = 10 * self.STR_RAD +self.GUIDE_SET
        self.guideWth = self.nutWth \
            + 2*math.tan(radians(self.NECK_WIDE_ANG))*self.guideX
        self.guidePostGap = self.guideWth/numStrs
        r0Y = -self.guideWth/2 +self.guidePostGap/2
        self.guideYs = []
        for r in range(numStrs):
            self.guideYs.append(r0Y +r*self.guidePostGap \
                + (-1 if r < numStrs/2 else 1)*(self.GUIDE_RAD + self.STR_RAD)
            )



# Base class for all Gugulele parts
class LelePart:

    def gen(self) -> api.Shape:
        pass

    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        self.cfg = cfg
        self.isCut = isCut
        self.shape = self.gen()

    def cut(self, cutter):
        self.shape = self.shape.cut(cutter.shape)
        return self

    def exportSTL(self, path: str, tolerance: float = 0.0001):
        self.shape.exportSTL(path, tolerance)

    def fillet(self, nearestPts: list[tuple[float, float, float]], rad: float):
        self.shape = self.shape.fillet(nearestPts, rad)
        return self

    def join(self, joiner):
        self.shape = self.shape.join(joiner.shape)
        return self

    def mirrorXZ(self):
        mirror = self.shape.mirrorXZ()
        return mirror

    def mv(self, x: float, y: float, z: float):
        self.shape = self.shape.mv(x, y, z)
        return self

    def show(self):
        return self.shape.show()


class Brace(LelePart):
    MAX_FRETS = 24

    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        scLen = self.cfg.scaleLen
        brdgZ = self.cfg.brdgZ
        chmFr = self.cfg.chmFront
        chmBk = self.cfg.chmBack
        chmWth = self.cfg.chmWth
        topRat = self.cfg.TOP_RATIO
        brace = api.RndRodX(.5*(chmFr+chmBk), .4*chmWth*topRat)\
            .scale(1, .25, 1)\
            .mv(scLen -.25*chmBk, 0, brdgZ)
        return brace


class Frets(LelePart):
    MAX_FRETS = 24

    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        ntWth = self.cfg.nutWth + 1  # to be wider than fretbd
        fWth = self.cfg.nutWth - 1  # to be narrower than fretbd
        ntHt = self.cfg.NUT_HT
        fbTck = self.cfg.FRETBD_TCK
        scLen = self.cfg.scaleLen
        fbLen = self.cfg.fretbdLen
        fHt = self.cfg.FRET_HT
        wideAng = self.cfg.NECK_WIDE_ANG
        riseAng = self.cfg.FRETBD_RISE_ANG
        f0X = -fitTol if self.isCut else 0

        f0Top = api.RodY(ntWth, ntHt).mv(f0X, 0, fbTck)
        f0Bot = api.RodY(ntWth, ntHt).scale(1, 1, fbTck/ntHt)
        f0BotCut = api.Box(2*ntHt, ntWth, fbTck).mv(0, 0, fbTck/2)
        f0Bot = f0Bot.cut(f0BotCut).mv(f0X, 0, fbTck)
        frets = f0Top.join(f0Bot)

        if not self.isCut:
            fx = 0
            gap = (scLen / 2) / accumDiv(1, 12, SEMI_RATIO)
            count = 0
            while (fx < (fbLen - gap - 2 * fHt)):
                fx = fx + gap
                fy = fWth / 2 + math.tan(radians(wideAng)) * fx
                fz = fbTck + math.tan(radians(riseAng)) * fx
                fret = api.RodY(2 * fy, fHt).mv(fx, 0, fz)
                frets = frets.join(fret)
                gap = gap / SEMI_RATIO
                count += 1
                if (count > self.MAX_FRETS):  # prevent runaway loop
                    break

        return frets


class Fretboard(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        scLen = self.cfg.scaleLen
        cutAdj = fitTol if self.isCut else 0
        fbLen = self.cfg.fretbdLen
        fbWth = self.cfg.fretbdWth
        fbTck = self.cfg.FRETBD_TCK
        fbHt = self.cfg.fretbdHt
        riseAng = self.cfg.FRETBD_RISE_ANG
        fspTck = self.cfg.FRETBD_SPINE_TCK
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spWth = self.cfg.SPINE_WTH +2*cutAdj
        fspLen = self.cfg.fbSpineLen +2*cutAdj
        fspX = self.cfg.fbSpX

        path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        fretbd = api.PolyExtrusionZ(path, fbHt)
        if self.cfg.sepFretbd:
            fsp1 = api.Box(fspLen, spWth, fspTck).mv(fspX +fspLen/2, spY1, -fspTck/2)
            fsp2 = api.Box(fspLen, spWth, fspTck).mv(fspX +fspLen/2, spY2, -fspTck/2)
            fretbd = fretbd.join(fsp1).join(fsp2)

        if not self.isCut:
            topCut = api.Box(fbLen * 2, fbWth, fbHt)\
                .rotateY(-riseAng).mv(0, 0, fbTck + fbHt/2)
            fretbd = fretbd.cut(topCut)
            fretbd = fretbd.fillet([(fbLen, 0, fbHt)], fbTck)

        return fretbd


class Neck(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        ntWth = self.cfg.nutWth
        fbLen = self.cfg.fretbdLen
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.EXT_MID_BOT_TCK
        botRat = self.cfg.BOT_RATIO
        spGap = self.cfg.spineGap
        spWth = self.cfg.SPINE_WTH
        spHt = self.cfg.SPINE_HT
        fspHt = self.cfg.FRETBD_SPINE_TCK
        path = self.cfg.neckPath
        neckMid = api.PolyExtrusionZ(path, midTck).mv(0, 0, -midTck)
        neckCone = api.ConeX(nkLen, ntWth/2, nkWth/2)
        coneCut = api.Box(nkLen, nkWth, nkWth).mv(nkLen/2, 0, nkWth/2)
        neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, -midTck)
        neck = neckMid.join(neckCone)
        if self.cfg.sepNeck:
            jntLen = self.cfg.neckJntLen
            jntWth = spGap -spWth
            jntTck = spHt +fspHt +fitTol
            jnt = api.Box(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, -jntTck/2)
            neck = neck.join(jnt)

        return neck


class Head(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.EXT_MID_BOT_TCK
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.headPath
        hd = api.SplineRevolveX((0, 0), path, 180)\
            .scale(1, 1, botRat).mv(0, 0, -midTck)

        if topRat > 0:
            top = api.SplineRevolveX((0, 0), path, -180).scale(1, 1, topRat)
            hd = hd.join(top)

        if midTck > 0:
            midL = api.SplineExtrusionZ(
                (0, 0), path, midTck).mv(0, 0, -midTck)
            midR = midL.mirrorXZ()
            hd = hd.join(midL).join(midR)

        return hd


class Top(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        fbLen = self.cfg.fretbdLen
        nkLen = self.cfg.neckLen
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.EXT_MID_TOP_TCK
        spGap = self.cfg.spineGap
        spWth = self.cfg.SPINE_WTH
        path = self.cfg.bodyCutPath if self.isCut else self.cfg.bodyPath
        jntLen = self.cfg.neckJntLen + (0 if self.isCut else 2*fitTol)
        jntWth = spGap + spWth + (0 if self.isCut else 2*fitTol)
        jntTck = 100 # arbitrary large value for cut
        
        top = api.SplineRevolveX((nkLen, 0), path, -180).scale(1, 1, topRat)
        if midTck > 0 or self.isCut:
            top = top.mv(0, 0, midTck)
            midL = api.SplineExtrusionZ(
                (nkLen, 0), 
                path, 
                midTck if midTck > 0 else fitTol,
            )
            midR = midL.mirrorXZ()
            top = top.join(midL).join(midR)

        notch = api.Box(jntLen, jntWth, jntTck)\
            .mv(nkLen +jntLen/2, 0, jntTck/2)
        top = top.cut(notch)

        return top


class Bottom(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self):
        fitTol = self.cfg.FIT_TOL
        nkLen = self.cfg.neckLen
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.EXT_MID_BOT_TCK
        spGap = self.cfg.spineGap
        spWth = self.cfg.SPINE_WTH
        spHt = self.cfg.SPINE_HT
        fspHt = self.cfg.FRETBD_SPINE_TCK
        path = self.cfg.bodyPath
        bot = api.SplineRevolveX((nkLen, 0), path, 180).scale(1, 1, botRat)
        if midTck > 0:
            bot = bot.mv(0, 0, -midTck)
            midL = api.SplineExtrusionZ((nkLen, 0), path, -midTck)
            midR = midL.mirrorXZ()
            bot = bot.join(midL).join(midR)

        if self.cfg.sepNeck:
            jntLen = self.cfg.neckJntLen + 2*fitTol
            jntWth = spGap -spWth
            jntTck = spHt +fspHt +fitTol
            jnt = api.Box(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, -jntTck/2)
            bot = bot.cut(jnt)

        return bot


class Chamber(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        sLen = self.cfg.scaleLen
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        chmFront = self.cfg.chmFront
        path = self.cfg.chmPath
        lift = self.cfg.chmLift
        top = api.SplineRevolveX((sLen - chmFront, 0), path, -180)\
            .scale(1, 1, topRat/2)
        bot = api.SplineRevolveX((sLen - chmFront, 0), path, 180)\
            .scale(1, 1, botRat)
        chm = top.join(bot)
        if lift != 0:
            chm.mv(0, 0, lift)
        return chm


class Soundhole(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        x = self.cfg.sndholeX
        y = self.cfg.sndholeY
        midTck = self.cfg.EXT_MID_TOP_TCK
        minRad = self.cfg.sndholeMinRad
        maxRad = self.cfg.sndholeMaxRad
        ang = self.cfg.sndholeAng
        bodyWth = self.cfg.bodyWth
        hole = api.RodZ(bodyWth +midTck, minRad)\
            .scale(1, maxRad/minRad, 1)\
            .rotateZ(ang).mv(x, y, -midTck)
        return hole


class Bridge(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        scLen = self.cfg.scaleLen
        strRad = self.cfg.STR_RAD
        brdgWth = self.cfg.brdgWth + (2*fitTol if self.isCut else 0)
        brdgLen = self.cfg.brdgLen + (2*fitTol if self.isCut else 0)
        brdgHt = self.cfg.brdgHt
        brdgZ = self.cfg.brdgZ
        brdg = api.Box(brdgLen, brdgWth, brdgHt).mv(
            scLen, 0, brdgZ + brdgHt/2)
        if not self.isCut:
            cutRad = brdgLen/2 - strRad
            cutHt = brdgHt - 2
            cutScaleZ = cutHt/cutRad
            frontCut = api.RodY(brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen - cutRad - strRad, 0, brdgZ + brdgHt)
            backCut = api.RodY(brdgWth, cutRad)\
                .scale(1, 1, cutScaleZ)\
                .mv(scLen + cutRad + strRad, 0, brdgZ + brdgHt)
            brdgTop = api.RodY(brdgWth, strRad).mv(scLen, 0, brdgZ + brdgHt)
            brdg = brdg.cut(frontCut).cut(backCut).join(brdgTop)
        return brdg


class Guide(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        sR  = self.cfg.STR_RAD
        gdR = self.cfg.GUIDE_RAD + cutAdj
        gdX = self.cfg.guideX
        gdZ = self.cfg.guideZ
        gdHt = self.cfg.guideHt
        gdWth = self.cfg.guideWth
        gdGap = self.cfg.guidePostGap
        guide = api.RndRodY(gdWth -gdR -sR, gdR).mv(gdX, 0, gdZ +gdHt)
        for y in self.cfg.guideYs:
            post = api.RodZ(gdHt, gdR).mv(gdX, y, gdZ +gdHt/2)
            guide = guide.join(post)
        return guide


class Peg(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        cfg = self.cfg.pegCfg
        majRad = cfg.majRad
        minRad = cfg.minRad
        midTck = cfg.midTck
        botLen = cfg.botLen
        btnRad = cfg.btnRad
        topCutTck = 100 # big value for cutting
        botCutTck = 100 # big value for cutting
        top = api.RodZ(topCutTck, majRad).mv(0, 0, topCutTck/2)
        mid = api.RodZ(midTck, minRad).mv(0, 0, -midTck/2)
        btnConeTck = botLen - midTck
        btn = api.ConeZ(btnConeTck, btnRad, majRad).mv(0, 0, -midTck -btnConeTck)
        bot = api.RodZ(botCutTck, btnRad).mv(0, 0, -botLen -botCutTck/2)
        peg = top.join(mid).join(btn).join(bot)   
        return peg


class Spines(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spHt = self.cfg.SPINE_HT +cutAdj
        spWth = self.cfg.SPINE_WTH +2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK
        sp1 = api.Box(spLen, spWth, spHt).mv(spX +spLen/2, spY1, -fspTck -spHt/2)
        sp2 = api.Box(spLen, spWth, spHt).mv(spX +spLen/2, spY2, -fspTck -spHt/2)
        return sp1.join(sp2)