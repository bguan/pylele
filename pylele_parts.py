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

    def filletByNearestEdges(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ):
        self.shape = self.shape.filletByNearestEdges(nearestPts, rad)
        return self

    def filletByNearestFaces(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ):
        self.shape = self.shape.filletByNearestFaces(nearestPts, rad)
        return self

    def half(self):
        return self.shape.half()

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
            .mv(scLen - .25*chmBk, 0, brdgZ)
        return brace


class Frets(LelePart):

    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
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
                if (count > maxFrets):  # prevent runaway loop
                    break

        return frets


class FretboardDots(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        scLen = self.cfg.scaleLen
        fbLen = self.cfg.fretbdLen
        fbTck = self.cfg.FRETBD_TCK
        maxFrets = self.cfg.MAX_FRETS
        dep = self.cfg.EMBOSS_DEP
        wideAng = self.cfg.neckWideAng
        riseAng = self.cfg.FRETBD_RISE_ANG
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
                    dot = api.RodZ(
                        2 * dep, dotRad).mv(acclen - .5*flen, p*sgap, ht)
                    dots = dot if dots == None else dots.join(dot)

            sgap = .5 * acclen * math.tan(radians(wideAng)) + nutSGap
            flen /= SEMI_RATIO
            acclen += flen
            n += 1
        return dots


class Fretboard(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = FIT_TOL
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
        spWth = self.cfg.SPINE_WTH + 2*cutAdj + (4*fitTol if joinToNeck else 0)
        fspLen = self.cfg.fbSpineLen + 4*cutAdj
        fspX = self.cfg.fbSpX

        path = self.cfg.fbCutPath if self.isCut else self.cfg.fbPath
        fretbd = api.PolyExtrusionZ(path, fbHt)
        if self.cfg.sepFretbd or self.cfg.sepNeck or self.cfg.sepTop:
            fsp1 = api.Box(fspLen, spWth, fspTck)\
                .mv(fspX + fspLen/2 - 2*cutAdj, spY1 + (fitTol if joinToNeck else 0), -fspTck/2)
            fsp2 = api.Box(fspLen, spWth, fspTck)\
                .mv(fspX + fspLen/2 - 2*cutAdj, spY2 - (fitTol if joinToNeck else 0), -fspTck/2)
            fretbd = fretbd.join(fsp1).join(fsp2)

        if not self.isCut:
            topCut = api.Box(fbLen * 2, fbWth, fbHt)\
                .rotateY(-riseAng)\
                .mv(0, 0, fbTck + fbHt/2)
            fretbd = fretbd.cut(topCut)
            fretbd = fretbd.filletByNearestEdges([(fbLen, 0, fbHt)], fbTck)

        return fretbd


class Neck(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = FIT_TOL
        spGap = self.cfg.spineGap if self.cfg.spineGap > 0 else 2*self.cfg.nutStrGap
        spWth = self.cfg.SPINE_WTH
        spHt = self.cfg.SPINE_HT
        fspHt = self.cfg.FRETBD_SPINE_TCK
        jntLen = self.cfg.neckJntLen
        jntWth = spGap - spWth - fitTol
        jntTck = spHt + fspHt + fitTol
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
        hd = api.LineSplineRevolveX(orig, path, 180)\
            .scale(1, 1, botRat).mv(0, 0, -midTck)

        if topRat > 0:
            top = api.LineSplineRevolveX(orig, path, -180).scale(1, 1, topRat)
            hd = hd.join(top)

        if midTck > 0:
            midL = api.LineSplineExtrusionZ(orig, path, midTck)\
                .mv(0, 0, -midTck)
            midR = midL.mirrorXZ()
            hd = hd.join(midL).join(midR)

        topCut = api.RndRodY(2*hdWth, hdLen)\
            .mv(-ntHt, 0, .8*hdLen + fbTck + ntHt)
        frontCut = api.RndRodY(2*hdWth, .7*spHt)\
            .scale(.5, 1, 1).mv(-hdLen, 0, -botTck - .35*spHt)
        hd = hd.cut(frontCut).cut(topCut)
        return hd


class Top(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = False):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = FIT_TOL
        scLen = self.cfg.scaleLen
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
        jntLen = self.cfg.neckJntLen + (2*fitTol if not self.isCut else 0)
        jntWth = spGap + spWth \
            + (2*fitTol if not self.isCut and fbJoinNeck else 0) \
            + (2*fitTol if fbJoinNeck else 0)
        jntTck = self.cfg.fretbdHt

        top = api.LineSplineRevolveX(bOrig, bPath, -180).scale(1, 1, topRat)
        if midTck > 0 or self.isCut:
            top = top.mv(0, 0, midTck+fitTol if self.isCut else midTck)
            midL = api.LineSplineExtrusionZ(
                bOrig, bPath, midTck+fitTol if self.isCut else midTck)
            midR = midL.mirrorXZ()
            top = top.join(midL).join(midR)

        if self.cfg.sepTop:
            rimL = api.LineSplineExtrusionZ(rOrig, rPath, rTck).mv(0, 0, -rTck)
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
        fitTol = FIT_TOL
        scLen = self.cfg.scaleLen
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
        jntLen = self.cfg.neckJntLen + 2*fitTol
        jntWth = spGap - spWth + 2*fitTol
        jntTck = spHt + fspHt + fitTol
        bot = api.LineSplineRevolveX(bOrig, bPath, 180).scale(1, 1, botRat)
        if midTck > 0:
            bot = bot.mv(0, 0, -midTck)
            midL = api.LineSplineExtrusionZ(bOrig, bPath, -midTck)
            midR = midL.mirrorXZ()
            bot = bot.join(midL).join(midR)

        if self.cfg.sepTop:
            rimCutL = api.LineSplineExtrusionZ(rcOrig, rcPath, rcTck)\
                .mv(0, 0, -rcTck)
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
        topRat = self.cfg.TOP_RATIO
        botRat = self.cfg.BOT_RATIO
        orig = self.cfg.chmOrig
        path = self.cfg.chmPath
        lift = self.cfg.chmLift
        rotY = self.cfg.chmRot
        top = api.LineSplineRevolveX(orig, path, -180).scale(1, 1, topRat/2)
        bot = api.LineSplineRevolveX(orig, path, 180).scale(1, 1, botRat)
        chm = top.join(bot)

        if rotY != 0:
            chm = chm.mv(-orig[0], -orig[1], 0)
            chm = chm.rotateY(rotY)
            chm = chm.mv(orig[0], orig[1], 0)

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
        fitTol = FIT_TOL
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
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        sR = self.cfg.STR_RAD
        gdR = self.cfg.GUIDE_RAD + cutAdj
        gdX = self.cfg.guideX
        gdZ = self.cfg.guideZ
        gdHt = self.cfg.GUIDE_HT
        gdWth = self.cfg.guideWth
        gdGap = self.cfg.guidePostGap
        guide = None if self.isCut else \
            api.RndRodY(gdWth - .5*gdGap - sR + 2*gdR, 1.1*gdR)\
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
        botCutTck = 100 if self.isCut else 2  # big value for cutting
        top = api.RodZ(topCutTck, majRad).mv(0, 0, topCutTck/2)

        if not self.isCut:
            stemHt = holeHt + 4*strRad
            stem = api.RodZ(stemHt, minRad/2).mv(0, 0, stemHt/2)
            hole = api.RodX(2*minRad, strRad).mv(0, 0, holeHt)
            stem = stem.cut(hole)
            top = top.join(stem)

        mid = api.RodZ(midTck, minRad).mv(0, 0, -midTck/2)

        if self.isCut:
            btnConeTck = botLen - midTck - 2*cutAdj
            btn = api.ConeZ(btnConeTck, btnRad, majRad)\
                .mv(0, 0, -midTck - btnConeTck)
            bot = api.RodZ(botCutTck, btnRad)\
                .mv(0, 0, -botLen - botCutTck/2 + 2*cutAdj)
        else:
            bot = api.RodZ(botCutTck, majRad)\
                .mv(0, 0, -midTck - botCutTck/2)
            stem = api.RodZ(botLen, minRad/2)\
                .mv(0, 0, -midTck - botLen/2)
            bot = bot.join(stem)
            btn = api.Box(btnRad*2, btnRad/2, btnRad)\
                .mv(0, 0, -midTck - botLen - botCutTck/2 + btnRad/2)\
                .filletByNearestEdges([], 2)

        peg = top.join(mid).join(btn).join(bot)

        return peg


class Worm(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
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
        axl = api.RodY(axlLen, axlRad).mv(axlX, axlY, axlZ)
        if self.isCut:
            axlExtCut = api.Box(
                100, axlLen, 2*axlRad).mv(50 + axlX, axlY, axlZ)
            axl = axl.join(axlExtCut)

        dskX = axlX
        dskY = axlY - axlLen/2 - dskTck/2
        dskZ = axlZ
        dsk = api.RodY(dskTck, dskRad).mv(dskX, dskY, dskZ)
        if self.isCut:
            dskExtCut = api.Box(
                100, dskTck, 2*dskRad).mv(50 + dskX, dskY, dskZ)
            dsk = dsk.join(dskExtCut)

        drvX = dskX
        drvY = dskY
        drvZ = dskZ + offset
        drv = api.RodX(drvLen, drvRad).mv(drvX, drvY, drvZ)
        if self.isCut:
            drvExtCut = api.RodX(100, drvRad).mv(50 + drvX, drvY, drvZ)
            drv = drv.join(drvExtCut)

        worm = axl.join(dsk).join(drv)

        if self.isCut:
            slit = api.Box(sltLen, sltWth, 100).mv(0, 0, 50 - 2*axlRad)
            worm = worm.join(slit)

        return worm


class Tuners(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
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
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        fitTol = FIT_TOL
        cutAdj = fitTol if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spHt = self.cfg.SPINE_HT + cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK
        sp1 = api.Box(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY1, -fspTck - spHt/2)
        sp2 = api.Box(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY2, -fspTck - spHt/2)
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


class Texts(LelePart):
    def __init__(self, cfg: LeleConfig, isCut: bool = True):
        super().__init__(cfg, isCut)

    def gen(self) -> api.Shape:
        scLen = self.cfg.scaleLen
        backRat = self.cfg.CHM_BACK_RATIO
        dep = self.cfg.EMBOSS_DEP
        tsf = self.cfg.txtSzFonts
        txtTck = self.cfg.TEXT_TCK
        bodyWth = self.cfg.bodyWth
        botRat = self.cfg.BOT_RATIO
        midBotTck = self.cfg.EXT_MID_BOT_TCK
        txtZ = -botRat * bodyWth/2 - midBotTck - 1
        allHt = sum([1.2*size for _, size, _ in tsf])
        tx = scLen - allHt/(1+backRat)
        ls = None
        for txt, sz, fnt in tsf:
            l = api.TextZ(txt, sz, txtTck, fnt) \
                .rotateZ(90).mirrorXZ().mv(tx + sz/2, 0, txtZ)
            ls = l if ls is None else ls.join(l)
            tx += sz
        botCut = Bottom(self.cfg, isCut=True)
        return ls.cut(botCut.shape).mv(0, 0, dep)
