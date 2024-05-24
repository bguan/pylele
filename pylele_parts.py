import math
import cq_api as api
from pylele_config import *

"""
    Base class for all Gugulele parts
"""

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

    def splitXZ(self):
        return self.shape.splitXZ()


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
            .mv(scLen - .25*chmBk, 0, brdgZ)
        return brace


class Frets(LelePart):
    MAX_FRETS = 24

    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        fbTck = self.cfg.FRETBD_TCK
        ntHt = self.cfg.NUT_HT
        ntWth = self.cfg.nutWth + fbTck/4 +.5 # to be wider than fretbd
        fWth = self.cfg.nutWth - 1  # to be narrower than fretbd
        scLen = self.cfg.scaleLen
        fbLen = self.cfg.fretbdLen
        fHt = self.cfg.FRET_HT
        wideAng = self.cfg.NECK_WIDE_ANG
        riseAng = self.cfg.FRETBD_RISE_ANG
        f0X = -fitTol if self.isCut else 0

        f0Top = api.RndRodY(ntWth, ntHt, domeRatio=1/4)
        f0TopCut = api.Box(2*ntHt, ntWth, fbTck).mv(0, 0, -fbTck/2)
        f0Top = f0Top.cut(f0TopCut).mv(f0X, 0, fbTck)
        f0Bot = api.RndRodY(ntWth, ntHt, domeRatio=1/4).scale(1, 1, fbTck/ntHt)
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
                fret = api.RndRodY(2 * fy, fHt).mv(fx, 0, fz)
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
        cutAdj = fitTol if self.isCut else 0
        fbLen = self.cfg.fretbdLen
        fbWth = self.cfg.fretbdWth
        fbTck = self.cfg.FRETBD_TCK
        fbHt = self.cfg.fretbdHt
        riseAng = self.cfg.FRETBD_RISE_ANG
        fspTck = self.cfg.FRETBD_SPINE_TCK
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        joinToNeck = not self.isCut and self.cfg.sepNeck and not self.cfg.sepFretbd
        spWth = self.cfg.SPINE_WTH + 2*cutAdj +(4*fitTol if joinToNeck else 0)
        fspLen = self.cfg.fbSpineLen + 4*cutAdj
        fspX = self.cfg.fbSpX

        path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        fretbd = api.PolyExtrusionZ(path, fbHt)
        if self.cfg.sepFretbd or self.cfg.sepNeck or self.cfg.sepTop:
            fsp1 = api.Box(fspLen, spWth, fspTck).mv(
                fspX + fspLen/2 -2*cutAdj, spY1 +(fitTol if joinToNeck else 0), -fspTck/2)
            fsp2 = api.Box(fspLen, spWth, fspTck).mv(
                fspX + fspLen/2 -2*cutAdj, spY2 -(fitTol if joinToNeck else 0), -fspTck/2)
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
        spGap = self.cfg.spineGap if self.cfg.spineGap > 0 else 2*self.cfg.nutStrGap
        spWth = self.cfg.SPINE_WTH
        spHt = self.cfg.SPINE_HT
        fspHt = self.cfg.FRETBD_SPINE_TCK
        jntLen = self.cfg.neckJntLen 
        jntWth = spGap - spWth -fitTol
        jntTck = spHt + fspHt +fitTol
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.EXT_MID_BOT_TCK
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.neckPath
        neckMid = api.PolyExtrusionZ(path, midTck).mv(0, 0, -midTck)
        neckCone = api.ConeX(nkLen, ntWth/2, nkWth/2)
        coneCut = api.Box(nkLen, nkWth, nkWth).mv(nkLen/2, 0, nkWth/2)
        neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, -midTck)
        neck = neckMid.join(neckCone)

        if self.cfg.sepNeck:
            jnt = api.Box(jntLen, jntWth, jntTck)\
                .mv(nkLen+jntLen/2, 0, -jntTck/2)
            neck = neck.join(jnt)
        return neck


class Head(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        hdWth = self.cfg.headWth
        hdLen = self.cfg.headLen
        ntHt = self.cfg.NUT_HT
        fbTck = self.cfg.FRETBD_TCK
        spHt = self.cfg.SPINE_HT
        botTck = self.cfg.EXT_MID_BOT_TCK
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.EXT_MID_BOT_TCK
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.headOrig
        path = self.cfg.headPath
        hd = api.SplineRevolveX(orig, path, 180).scale(1, 1, botRat).mv(0, 0, -midTck)

        if topRat > 0:
            top = api.SplineRevolveX(orig, path, -180).scale(1, 1, topRat)
            hd = hd.join(top)

        if midTck > 0:
            midL = api.SplineExtrusionZ(orig, path, midTck).mv(0, 0, -midTck)
            midR = midL.mirrorXZ()
            hd = hd.join(midL).join(midR)

        topCut = api.RndRodY(2*hdWth, hdLen).mv(-ntHt, 0, .8*hdLen +fbTck +ntHt)
        frontCut = api.RndRodY(2*hdWth, .7*spHt).scale(.5, 1, 1).mv(-hdLen, 0, -botTck -.35*spHt)
        hd = hd.cut(frontCut).cut(topCut)
        return hd


class Top(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = self.cfg.FIT_TOL
        rOrig = self.cfg.rimOrig
        rPath = self.cfg.rimPath
        rTck = self.cfg.rimTck
        topRat = self.cfg.TOP_RATIO
        midTck = self.cfg.EXT_MID_TOP_TCK
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyCutPath if self.isCut else self.cfg.bodyPath
        nkLen = self.cfg.neckLen
        spGap = self.cfg.spineGap if self.cfg.spineGap > 0 else 2*self.cfg.nutStrGap
        spWth = self.cfg.SPINE_WTH
        fbJoinNeck = self.isCut and self.cfg.sepNeck and not self.cfg.sepFretbd
        jntLen = self.cfg.neckJntLen +(2*fitTol if not self.isCut else 0)
        jntWth = spGap +spWth +(2*fitTol if not self.isCut and fbJoinNeck else 0) \
            +(2*fitTol if fbJoinNeck else 0)
        jntTck = self.cfg.fretbdHt

        top = api.SplineRevolveX(bOrig, bPath, -180).scale(1, 1, topRat)
        if midTck > 0 or self.isCut:
            top = top.mv(0, 0, midTck+fitTol if self.isCut else midTck)
            midL = api.SplineExtrusionZ(bOrig, bPath, midTck+fitTol if self.isCut else midTck)
            midR = midL.mirrorXZ()
            top = top.join(midL).join(midR)
        
        if self.cfg.sepTop:
            rimL = api.SplineExtrusionZ(rOrig, rPath, rTck).mv(0, 0, -rTck)
            rimR = rimL.mirrorXZ()
            top = top.join(rimL).join(rimR)

        if self.cfg.sepNeck or self.cfg.sepFretbd:
            jnt = api.Box(jntLen, jntWth, jntTck)\
                .mv(nkLen+jntLen/2, 0, jntTck/2)
            top = top.cut(jnt)
        return top


class Bottom(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self):
        fitTol = self.cfg.FIT_TOL
        nkLen = self.cfg.neckLen
        botRat = self.cfg.BOT_RATIO
        midTck = self.cfg.EXT_MID_BOT_TCK
        rcOrig = self.cfg.rimCutOrig
        rcPath = self.cfg.rimCutPath
        rcTck = self.cfg.rimTck
        bOrig = self.cfg.bodyOrig
        bPath = self.cfg.bodyPath
        spGap = self.cfg.spineGap if self.cfg.spineGap > 0 else 2*self.cfg.nutStrGap
        spWth = self.cfg.SPINE_WTH
        spHt = self.cfg.SPINE_HT
        fspHt = self.cfg.FRETBD_SPINE_TCK
        jntLen = self.cfg.neckJntLen +2*fitTol
        jntWth = spGap - spWth +2*fitTol
        jntTck = spHt + fspHt +fitTol
        bot = api.SplineRevolveX(bOrig, bPath, 180).scale(1, 1, botRat)
        if midTck > 0:
            bot = bot.mv(0, 0, -midTck)
            midL = api.SplineExtrusionZ(bOrig, bPath, -midTck)
            midR = midL.mirrorXZ()
            bot = bot.join(midL).join(midR)

        if self.cfg.sepTop:
            rimCutL = api.SplineExtrusionZ(rcOrig, rcPath, rcTck).mv(0, 0, -rcTck)
            rimCutR = rimCutL.mirrorXZ()
            bot = bot.cut(rimCutL).cut(rimCutR)

        if self.cfg.sepNeck:
            jnt = api.Box(jntLen, jntWth, jntTck)\
                .mv(nkLen+jntLen/2, 0, -jntTck/2)
            bot = bot.cut(jnt)
        return bot


class Chamber(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        scLen = self.cfg.scaleLen
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.chmOrig
        path = self.cfg.chmPath
        lift = self.cfg.chmLift
        tilt = self.cfg.chmTilt
        top = api.SplineRevolveX(orig, path, -180).scale(1, 1, topRat/2)
        bot = api.SplineRevolveX(orig, path, 180).scale(1, 1, botRat)
        chm = top.join(bot)

        if tilt != 0:
            chm = chm.rotateY(tilt)
        chm = chm.mv(scLen, 0, 0)
        if lift != 0:
            chm = chm.mv(0, 0, lift)
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
        hole = api.RodZ(bodyWth + midTck, minRad)\
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
        isOdd = self.cfg.isOddStrs
        fitTol = self.cfg.FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        sR = self.cfg.STR_RAD
        gdR = self.cfg.GUIDE_RAD + cutAdj
        gdX = self.cfg.guideX
        gdZ = self.cfg.guideZ
        gdHt = self.cfg.GUIDE_HT
        gdWth = self.cfg.guideWth
        gdGap = self.cfg.guidePostGap
        guide = None if self.isCut else \
            api.RndRodY(gdWth - .5*gdGap -sR +2*gdR, 1.1*gdR)\
            .mv(gdX, 0, gdZ + gdHt)
        for y in self.cfg.guideYs:
            post = api.RodZ(gdHt, gdR)
            post = post.mv(gdX, y, gdZ + gdHt/2)
            guide = post if guide == None else guide.join(post)
        return guide


class Peg(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        cutAdj = self.cfg.FIT_TOL if self.isCut else 0
        cfg = self.cfg.pegCfg
        majRad = cfg.majRad + cutAdj
        minRad = cfg.minRad + cutAdj
        midTck = cfg.midTck
        botLen = cfg.botLen
        btnRad = cfg.btnRad + cutAdj
        topCutTck = 100  # big value for cutting
        botCutTck = 100  # big value for cutting
        top = api.RodZ(topCutTck, majRad).mv(0, 0, topCutTck/2)
        mid = api.RodZ(midTck, minRad).mv(0, 0, -midTck/2)
        btnConeTck = botLen - midTck
        btn = api.ConeZ(btnConeTck, btnRad, majRad).mv(
            0, 0, -midTck - btnConeTck)
        bot = api.RodZ(botCutTck, btnRad).mv(0, 0, -botLen - botCutTck/2)
        peg = top.join(mid).join(btn).join(bot)
        return peg


class Pegs(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        pXYZs = self.cfg.pegsXYZ
        pegs = None
        for pxyz in pXYZs:
            peg = Peg(self.cfg, isCut=self.isCut).mv(pxyz[0], pxyz[1], pxyz[2]).shape
            pegs = peg if pegs == None else pegs.join(peg)
        return pegs


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
        spHt = self.cfg.SPINE_HT + cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK
        sp1 = api.Box(spLen, spWth, spHt).mv(
            spX + spLen/2, spY1, -fspTck - spHt/2)
        sp2 = api.Box(spLen, spWth, spHt).mv(
            spX + spLen/2, spY2, -fspTck - spHt/2)
        return sp1.join(sp2)


class Strings(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        srad = self.cfg.STR_RAD
        paths = self.cfg.stringPaths
        strs = None
        for p in paths:
            str = api.CircleXPolySweep(srad, p)
            strs = str if strs == None else strs.join(str)
        return strs