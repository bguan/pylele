#!/usr/bin/env python3
from __future__ import annotations

from abc import ABC
import math
import os
from pathlib import Path
import sys
from typing import Union

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.core import Shape, Implementation
from api.constants import FILLET_RAD, FIT_TOL, ColorEnum
from api.utils import radians, accumDiv
from pylele1.pylele_config import LeleConfig, WormConfig
from pylele_config_common import SEMI_RATIO, PegConfig

"""
    Abstract Base and Concrete Classes for all Pylele parts
"""


class LelePart(ABC):

    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = None,
        name: str = None,
    ):
        cfg = cfg
        self.color = color
        self.isCut = isCut
        self.name = name if name is not None else \
            self.__class__.__name__ + ("_cut" if isCut else "")
        self.color = None if isCut else color
        self.shape : Shape = None

    def cut(self, cutter: LelePart) -> LelePart:
        self.shape = self.shape.cut(cutter.shape)
        return self

    def export_stl(self, path: Union[str, Path]) -> None:
        self.shape.api.export_stl(self.shape, str(path))

    def export_best(self, path: Union[str, Path]) -> None:
        self.shape.api.export_best(self.shape, str(path))

    def fillet(
        self,
        nearestPts: list[tuple[float, float, float]],
        rad: float,
    ) -> LelePart:
        self.shape = self.shape.fillet(nearestPts, rad)
        return self

    def half(self) -> LelePart:
        self.shape = self.shape.half()
        return self

    def join(self, joiner: LelePart) -> LelePart:
        self.shape = self.shape.join(joiner.shape)
        return self

    def mirror(self) -> LelePart:
        mirror = self.shape.mirror()
        return mirror

    def mv(self, x: float, y: float, z: float) -> LelePart:
        self.shape = self.shape.mv(x, y, z)
        return self

    def show(self):
        return self.shape.show()


class Brace(LelePart):
    MAX_FRETS = 24

    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.WHITE,
    ):
        super().__init__(cfg, isCut, color)

        scLen = cfg.scaleLen
        brdgZ = cfg.brdgZ
        chmFr = cfg.chmFront
        chmBk = cfg.chmBack
        chmWth = cfg.chmWth
        self.shape = (
            cfg.api()
            .cylinder_rounded_x(0.5 * (chmFr + chmBk), 0.05 * chmWth, 1)
            .scale(1, 0.3, 1)
            .mv(scLen - 0.25 * chmBk, 0, brdgZ)
        )


class Frets(LelePart):

    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.DARK_GRAY,
        upToFret: int = 24,
    ):
        super().__init__(cfg, isCut, color)

        jctol = cfg.tolerance
        fitTol = FIT_TOL
        fbTck = cfg.FRETBD_TCK
        ntHt = cfg.NUT_HT
        ntWth = cfg.nutWth + fbTck / 4 + 0.5  # to be wider than fretbd
        fWth = cfg.nutWth - 1  # to be narrower than fretbd
        scLen = cfg.scaleLen
        fbLen = cfg.fretbdLen
        fHt = cfg.FRET_HT
        maxFrets = cfg.MAX_FRETS if upToFret is None else upToFret
        wideAng = cfg.neckWideAng
        riseAng = cfg.fretbdRiseAng
        f0X = -fitTol if isCut else 0

        f0Top = cfg.api().cylinder_rounded_y(ntWth, ntHt, 1 / 4)
        f0TopCut = cfg.api().box(2 * ntHt, 2 * ntWth, fbTck).mv(0, 0, -fbTck / 2)
        f0Top = f0Top.cut(f0TopCut).mv(f0X, 0, fbTck)
        f0Bot = cfg.api().cylinder_rounded_y(ntWth, ntHt, 1 / 4)
        f0BotCut = cfg.api().box(2 * ntHt, 2 * ntWth, fbTck).mv(0, 0, fbTck / 2)
        f0Bot = f0Bot.cut(f0BotCut).scale(1, 1, fbTck / ntHt).mv(f0X, 0, fbTck)
        frets = f0Top.mv(0, 0, -jctol).join(f0Bot)

        if not isCut:
            fx = 0
            gap = (scLen / 2) / accumDiv(1, 12, SEMI_RATIO)
            count = 0
            while fx < (fbLen - gap - 2 * fHt):
                if count > maxFrets:  # prevent runaway loop
                    break
                fx = fx + gap
                fy = fWth / 2 + math.tan(radians(wideAng)) * fx
                fz = fbTck + math.tan(radians(riseAng)) * fx
                fret = cfg.api().cylinder_y(2 * fy, fHt).mv(fx, 0, fz)
                frets = frets.join(fret)
                gap = gap / SEMI_RATIO
                count += 1

        self.shape = frets


class FretboardDots(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = None,
    ):
        super().__init__(cfg, isCut, color)

        scLen = cfg.scaleLen
        fbLen = cfg.fretbdLen
        fbTck = cfg.FRETBD_TCK
        maxFrets = cfg.MAX_FRETS
        dep = cfg.EMBOSS_DEP
        wideAng = cfg.neckWideAng
        riseAng = cfg.fretbdRiseAng
        nutSGap = cfg.nutStrGap
        dotRad = cfg.dotRad
        fret2Dots = cfg.fret2Dots

        dots = None
        sgap = nutSGap
        # half length of fret 1
        flen = 0.5 * scLen / accumDiv(1, 12, SEMI_RATIO)
        n = 1
        acclen = flen
        while acclen < fbLen and n <= maxFrets:
            if n in fret2Dots:
                ht = fbTck + math.tan(radians(riseAng)) * acclen
                pos = (
                    [0]
                    if fret2Dots[n] == 1
                    else [-0.5, 0.5] if fret2Dots[n] == 2 else [-1, 0, 1]
                )
                for p in pos:
                    dot = (
                        cfg.api()
                        .cylinder_z(2 * dep, dotRad)
                        .mv(acclen - 0.5 * flen, p * sgap, ht)
                    )
                    dots = dot if dots == None else dots.join(dot)

            sgap = 0.5 * acclen * math.tan(radians(wideAng)) + nutSGap
            flen /= SEMI_RATIO
            acclen += flen
            n += 1

        self.shape = dots


class Fretboard(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = FIT_TOL if isCut else 0
        fbLen = cfg.fretbdLen + 2 * cutAdj
        fbWth = cfg.fretbdWth + 2 * cutAdj
        fbTck = cfg.FRETBD_TCK + 2 * cutAdj
        fbHt = cfg.fretbdHt + 2 * cutAdj
        riseAng = cfg.fretbdRiseAng

        path = cfg.fbCutPath if isCut else cfg.fbPath
        fretbd = cfg.api().polygon_extrusion(path, fbHt)

        if isCut:
            fretbd = fretbd.mv(0, 0, -cfg.tolerance)
        else:
            topCut = (
                cfg.api()
                .box(fbLen * 2, fbWth, fbHt)
                .rotate_y(-riseAng)
                .mv(0, 0, fbTck + fbHt / 2)
            )
            fretbd = fretbd.cut(topCut)
            fretbd = fretbd.fillet([(fbLen, 0, fbHt)], fbTck / 2)

        self.shape = fretbd


class FretboardSpines(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = FIT_TOL if isCut else 0
        fspTck = cfg.FRETBD_SPINE_TCK + 2 * (cfg.tolerance if isCut else 0)
        spY1 = cfg.spineY1
        spY2 = cfg.spineY2
        spWth = cfg.SPINE_WTH + 2 * cutAdj  # to align with spine cuts
        fspLen = cfg.fbSpineLen + 2 * cutAdj + 2 * (cfg.tolerance if isCut else 0)

        fspX = cfg.NUT_HT

        sp = (
            cfg.api()
            .box(fspLen, spWth, fspTck)
            .mv(fspX + fspLen / 2, spY1, -fspTck / 2)
        )  # - 2*cutAdj

        if spY2 != spY1:
            sp2 = (
                cfg.api()
                .box(fspLen, spWth, fspTck)
                .mv(fspX + fspLen / 2, spY2, -fspTck / 2)
            )  # - 2*cutAdj
            sp = sp.join(sp2)

        self.shape = sp


class FretbdJoint(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = (FIT_TOL + cfg.tolerance) if isCut else 0
        fbHt = cfg.fretbdHt
        nkLen = cfg.neckLen
        jntLen = cfg.neckJntLen + 2 * cutAdj
        jntWth = cfg.neckJntWth + 2 * cutAdj  # to align with spine cuts
        jntTck = 0.8 * fbHt + 2 * cutAdj
        self.shape = (
            cfg.api()
            .box(jntLen, jntWth, jntTck)
            .mv(nkLen + jntLen / 2, 0, jntTck / 2)
        )


class Neck(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.ORANGE,
    ):
        super().__init__(cfg, isCut, color)

        ntWth = cfg.nutWth
        nkLen = cfg.neckLen
        nkWth = cfg.neckWth
        midTck = cfg.extMidBotTck
        botRat = cfg.BOT_RATIO
        path = cfg.neckPath
        joinTol = cfg.tolerance
        neck = None
        if midTck > 0:
            neck = cfg.api().polygon_extrusion(path, midTck).mv(0, 0, -midTck)

        neckPath = [(nkLen, 0), (nkLen, nkWth / 2), (0, ntWth / 2)]
        neckCone = cfg.api().spline_revolve((0, 0), neckPath, -180)
        neckCone = neckCone.scale(1, 1, botRat).mv(0, 0, -midTck)

        self.shape = neckCone if neck == None else neck.join(neckCone.mv(0, 0, joinTol))


class NeckJoint(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.ORANGE,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = (FIT_TOL + cfg.tolerance) if isCut else 0
        nkLen = cfg.neckLen
        jntLen = cfg.neckJntLen + 2 * cutAdj
        jntWth = cfg.neckJntWth + 2 * cutAdj
        jntTck = (
            cfg.neckJntTck + 2 * FIT_TOL + 2 * cfg.tolerance
        )  # to match cut grooves for spines
        self.shape = (
            cfg.api()
            .box(jntLen, jntWth, jntTck)
            .mv(nkLen + jntLen / 2, 0, -jntTck / 2)
        )


class Head(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.ORANGE,
    ):
        super().__init__(cfg, isCut, color)

        hdWth = cfg.headWth
        hdLen = cfg.headLen
        ntHt = cfg.NUT_HT
        fbTck = cfg.FRETBD_TCK
        spHt = cfg.SPINE_HT
        fspTck = cfg.FRETBD_SPINE_TCK
        topRat = cfg.HEAD_TOP_RATIO
        midTck = cfg.extMidBotTck
        botRat = cfg.BOT_RATIO
        orig = cfg.headOrig
        path = cfg.headPath
        joinTol = cfg.tolerance

        hd = (
            cfg.api()
            .spline_revolve(orig, path, -180)
            .scale(1, 1, botRat)
            .mv(0, 0, joinTol - midTck)
        )

        if midTck > 0:
            midR = (
                cfg.api().spline_extrusion(orig, path, midTck).mv(0, 0, -midTck)
            )
            mid = midR.mirror_and_join()
            hd = hd.join(mid)

        if topRat > 0:
            top = (
                cfg.api()
                .spline_revolve(orig, path, 180)
                .scale(1, 1, topRat)
                .mv(0, 0, -joinTol)
            )
            hd = hd.join(top)

        topCut = (
            cfg.api().cylinder_y(2 * hdWth, hdLen).mv(-ntHt, 0, 0.8 * hdLen + fbTck + ntHt)
        )
        frontCut = (
            cfg.api()
            .cylinder_y(2 * hdWth, 0.7 * spHt)
            .scale(0.5, 1, 1)
            .mv(-hdLen, 0, -fspTck - 0.65 * spHt)
        )

        self.shape = hd.cut(frontCut).cut(topCut)


class Top(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.WHITE,
    ):
        super().__init__(cfg, isCut, color)

        fitTol = FIT_TOL
        joinTol = cfg.tolerance
        cutAdj = (fitTol + joinTol) if isCut else 0
        topRat = cfg.TOP_RATIO
        midTck = cfg.extMidTopTck + cutAdj
        bOrig = cfg.bodyOrig
        bPath = cfg.bodyCutPath if isCut else cfg.bodyPath
        top = cfg.api().spline_revolve(bOrig, bPath, 180).scale(1, 1, topRat)
        if midTck > 0:
            top = top.mv(0, 0, midTck - joinTol)
            midR = cfg.api().spline_extrusion(bOrig, bPath, midTck)
            top = top.join(midR.mirror_and_join())

        self.shape = top


class Body(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.ORANGE,
    ):
        super().__init__(cfg, isCut, color)

        botRat = cfg.BOT_RATIO
        midTck = cfg.extMidBotTck
        bOrig = cfg.bodyOrig
        bPath = cfg.bodyPath
        joinTol = cfg.tolerance

        bot = cfg.api().spline_revolve(bOrig, bPath, -180).scale(1, 1, botRat)
        if midTck > 0:
            bot = bot.mv(0, 0, -midTck + joinTol)
            midR = cfg.api().spline_extrusion(bOrig, bPath, midTck)
            midR = midR.mv(0, 0, -midTck)
            bot = bot.join(midR.mirror_and_join())

        self.shape = bot


class Rim(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.WHITE,
    ):
        super().__init__(cfg, isCut, color)
        joinTol = cfg.tolerance
        cutAdj = (FIT_TOL + joinTol) if isCut else 0
        scLen = cfg.scaleLen
        rad = cfg.chmWth / 2 + cfg.rimWth
        tck = cfg.RIM_TCK + 2 * cutAdj
        frontWthRatio = (cfg.chmFront + cfg.rimWth) / rad
        backWthRatio = (cfg.chmBack + cfg.rimWth) / rad
        rimFront = cfg.api().cylinder_half(rad, True, tck).scale(frontWthRatio, 1, 1)
        rimBack = cfg.api().cylinder_half(rad, False, tck).scale(backWthRatio, 1, 1)
        self.shape = rimFront.mv(scLen, 0, joinTol - tck / 2)\
            .join(rimBack.mv(scLen - joinTol, 0, joinTol - tck / 2))


class Chamber(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = None,
    ):
        super().__init__(cfg, isCut, color)

        scLen = cfg.scaleLen
        topRat = cfg.TOP_RATIO
        botRat = cfg.BOT_RATIO
        lift = cfg.chmLift
        rotY = cfg.chmRot
        jcTol = cfg.tolerance
        rad = cfg.chmWth / 2
        frontRat = cfg.chmFront / rad
        backRat = cfg.chmBack / rad
        topChmRat = topRat * 3 / 4

        topFront = (
            cfg.api()
            .sphere_quadrant(rad, True, True)
            .scale(frontRat, 1, topChmRat)
            .mv(jcTol, 0, -jcTol)
        )
        topBack = (
            cfg.api()
            .sphere_quadrant(rad, True, False)
            .scale(backRat, 1, topChmRat)
            .mv(0, 0, -jcTol)
        )
        botFront = (
            cfg.api()
            .sphere_quadrant(rad, False, True)
            .scale(frontRat, 1, botRat)
            .mv(jcTol, 0, 0)
        )
        botBack = (
            cfg.api()
            .sphere_quadrant(rad, False, False)
            .scale(backRat, 1, botRat)
            .mv(0, 0, 0)
        )
        chm = topFront.join(topBack).join(botFront).join(botBack)

        if rotY != 0:
            chm = chm.rotate_y(rotY)

        if lift != 0:
            chm = chm.mv(0, 0, lift)

        self.shape = chm.mv(scLen, 0, 0)


class Soundhole(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = None,
    ):
        super().__init__(cfg, isCut, color)

        x = cfg.sndholeX
        y = cfg.sndholeY
        midTck = cfg.extMidTopTck
        minRad = cfg.sndholeMinRad
        maxRad = cfg.sndholeMaxRad
        ang = cfg.sndholeAng
        bodyWth = cfg.bodyWth

        self.shape = cfg.api() \
            .cylinder_z(bodyWth + midTck, minRad) \
            .scale(1, maxRad / minRad, 1) \
            .rotate_z(ang) \
            .mv(x, y, -midTck)


class Bridge(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        jctol = cfg.tolerance
        fitTol = FIT_TOL
        scLen = cfg.scaleLen
        strRad = cfg.STR_RAD
        brdgWth = cfg.brdgWth + (2 * fitTol if isCut else 0)
        brdgLen = cfg.brdgLen + (2 * fitTol if isCut else 0)
        brdgHt = cfg.brdgHt
        brdgZ = cfg.brdgZ

        brdg = (
            cfg.api().box(brdgLen, brdgWth, brdgHt).mv(scLen, 0, brdgZ + brdgHt / 2)
        )
        if not isCut:
            cutRad = brdgLen / 2 - strRad
            cutHt = brdgHt - 2
            cutScaleZ = cutHt / cutRad
            frontCut = (
                cfg.api()
                .cylinder_y(2 * brdgWth, cutRad)
                .scale(1, 1, cutScaleZ)
                .mv(scLen - cutRad - strRad + jctol, 0, brdgZ + brdgHt)
            )
            backCut = (
                cfg.api()
                .cylinder_y(2 * brdgWth, cutRad)
                .scale(1, 1, cutScaleZ)
                .mv(scLen + cutRad + strRad - jctol, 0, brdgZ + brdgHt)
            )
            brdgTop = (
                cfg.api().cylinder_y(brdgWth, strRad).mv(scLen, 0, brdgZ + brdgHt - jctol)
            )
            brdg = brdg.join(brdgTop).cut(frontCut).cut(backCut)

        self.shape = brdg


class Guide(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = False,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        fitTol = FIT_TOL
        cutAdj = fitTol if isCut else 0
        nStrs = cfg.numStrs
        sR = cfg.STR_RAD
        gdR = cfg.GUIDE_RAD + cutAdj
        gdX = cfg.guideX
        gdZ = cfg.guideZ
        gdHt = cfg.guideHt
        gdWth = cfg.guideWth
        gdGap = cfg.guidePostGap

        guide = (
            None
            if isCut
            else
                cfg.api()
                .cylinder_rounded_y(
                    (gdWth - 0.5 * gdGap + sR + 2 * gdR) if nStrs > 1 else 6 * gdR,
                    1.1 * gdR,
                    1,
                )
                .mv(gdX, 0, gdZ + gdHt)
        )
        for y in cfg.guideYs:
            post = cfg.api().cylinder_z(gdHt, gdR)
            post = post.mv(gdX, y, gdZ + gdHt / 2)
            guide = post if guide == None else guide.join(post)

        self.shape = guide


class Peg(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.GRAY,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = FIT_TOL if isCut else 0
        joinTol = cfg.tolerance
        pcfg: PegConfig = cfg.tnrCfg
        strRad = LeleConfig.STR_RAD + cutAdj
        holeHt = pcfg.holeHt
        majRad = pcfg.majRad + cutAdj
        minRad = pcfg.minRad + cutAdj
        midTck = pcfg.midTck
        botLen = pcfg.botLen
        btnRad = pcfg.btnRad + cutAdj
        topCutTck = 10 if isCut else 2  # big value for cutting
        botCutTck = botLen - midTck / 3 if isCut else 2

        top = cfg.api().cylinder_z(topCutTck + joinTol, majRad).mv(0, 0, topCutTck / 2)

        if not isCut:
            stemHt = holeHt + 4 * strRad
            stem = cfg.api().cylinder_z(stemHt + joinTol, minRad / 2).mv(0, 0, stemHt / 2)
            hole = cfg.api().cylinder_x(2 * minRad, strRad).mv(0, 0, holeHt)
            stem = stem.cut(hole)
            top = top.join(stem)

        mid = cfg.api().cylinder_z(midTck + joinTol, minRad).mv(0, 0, -midTck / 2)

        if isCut:
            btnConeTck = botLen - midTck - 2 * cutAdj
            btn = (
                cfg.api()
                .cone_z(btnConeTck + joinTol, btnRad, majRad)
                .mv(0, 0, -midTck - btnConeTck)
            )
            bot = (
                cfg.api()
                .cylinder_z(botCutTck + joinTol, btnRad)
                .mv(0, 0, -botLen - botCutTck / 2 + 2 * cutAdj)
            )
            botEnd = (
                cfg.api()
                .sphere(btnRad)
                .scale(1, 1, 0.5 if cfg.sepEnd else 1)
                .mv(0, 0, -botLen - botCutTck)
            )
            bot = bot.join(botEnd)
        else:
            bot = (
                cfg.api()
                .cylinder_z(botCutTck + joinTol, majRad)
                .mv(0, 0, -midTck - botCutTck / 2)
            )
            stem = (
                cfg.api()
                .cylinder_z(botLen + joinTol, minRad / 2)
                .mv(0, 0, -midTck - botLen / 2)
            )
            bot = bot.join(stem)
            btn = (
                cfg.api()
                .box(btnRad * 2, btnRad / 2, btnRad)
                .mv(0, 0, -midTck - botLen + btnRad / 2)
            )

        self.shape = top.join(mid).join(btn).join(bot)


class Worm(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.GRAY,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = FIT_TOL if isCut else 0
        joinTol = cfg.tolerance
        wcfg: WormConfig = cfg.tnrCfg
        (front, _, _, _, _, _) = wcfg.dims()
        sltLen = wcfg.slitLen
        sltWth = wcfg.slitWth
        sltHt = wcfg.slitHt
        drvRad = wcfg.driveRad + cutAdj
        dskRad = wcfg.diskRad + cutAdj
        dskTck = wcfg.diskTck + 2 * cutAdj
        axlRad = wcfg.axleRad + cutAdj
        axlLen = wcfg.axleLen + 2 * cutAdj
        offset = wcfg.driveOffset
        drvLen = wcfg.driveLen + 2 * cutAdj

        # Note: Origin is middle of slit, near tip of axle
        axlX = 0
        axlY = -joinTol
        axlZ = 0
        axl = cfg.api().cylinder_y(axlLen, axlRad).mv(axlX, axlY, axlZ)
        if isCut:
            axlExtCut = (
                cfg.api().box(100, axlLen, 2 * axlRad).mv(50 + axlX, axlY, axlZ)
            )
            axl = axl.join(axlExtCut)

        dskX = axlX
        dskY = axlY - axlLen / 2 - dskTck / 2
        dskZ = axlZ
        dsk = cfg.api().cylinder_y(dskTck, dskRad).mv(dskX, dskY, dskZ)
        if isCut:
            dskExtCut = (
                cfg.api().box(100, dskTck, 2 * dskRad).mv(50 + dskX, dskY, dskZ)
            )
            dsk = dsk.join(dskExtCut)

        drvX = dskX
        drvY = dskY
        drvZ = dskZ + offset
        drv = cfg.api().cylinder_x(drvLen, drvRad).mv(drvX, drvY, drvZ)
        if isCut:
            drvExtCut = cfg.api().cylinder_x(100, drvRad).mv(50 + drvX, drvY, drvZ)
            drv = drv.join(drvExtCut)

        worm = axl.join(dsk).join(drv)

        if isCut:
            slit = cfg.api().box(sltLen, sltWth, sltHt)\
                .mv(0, 0, sltHt/2 - 2*axlRad)
            slope = cfg.api().regpoly_extrusion_y(sltWth, sltWth * 2, 4)\
                .mv(-sltLen/2, 0, sltHt - 2*axlRad)
            worm = worm.join(slit.join(slope))

        worm = worm.mv(wcfg.tailAdj, 0, 0)
        self.shape = worm


class WormKey(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        isBlender = cfg.impl == Implementation.BLENDER
        joinTol = cfg.tolerance
        tailX = cfg.tailX
        txyzs = cfg.tnrXYZs
        wcfg: WormConfig = cfg.tnrCfg
        cutAdj = (FIT_TOL + joinTol) if isCut else 0
        btnHt = wcfg.buttonHt + 2 * cutAdj
        btnWth = wcfg.buttonWth + 2 * cutAdj
        btnTck = wcfg.buttonTck + 2 * cutAdj
        kbHt = wcfg.buttonKeybaseHt + 2 * cutAdj
        kbRad = wcfg.buttonKeybaseRad + cutAdj
        kyRad = wcfg.buttonKeyRad + cutAdj
        kyLen = wcfg.buttonKeyLen + 2 * cutAdj
        gapAdj = wcfg.gapAdj

        key = (
            cfg.api()
            .regpoly_extrusion_x(kyLen, kyRad, 6)
            .mv(joinTol - kyLen / 2 - kbHt - btnHt, 0, 0)
        )
        base = (
            cfg.api().regpoly_extrusion_x(kbHt, kbRad, 36)
            if isBlender
            else cfg.api().cylinder_x(kbHt, kbRad)
        )
        base = base.mv(-kbHt / 2 - btnHt, 0, 0)
        btn = (
            cfg.api()
            .box(100 if isCut else btnHt, btnTck, btnWth)
            .mv(50 - btnHt if isCut else -btnHt / 2, 0, 0)
        )

        if isCut:
            btnExtCut = (
                cfg.api()
                .cylinder_x(100 if isCut else btnHt, btnWth / 2)
                .scale(1, 0.5, 1)
                .mv(50 - btnHt if isCut else -btnHt / 2, btnTck / 2, 0)
            )
            btn = btn.join(btnExtCut)
        else:
            btn = btn.fillet([], FILLET_RAD)

        btn = btn.join(base).join(key)
        maxTnrY = max([y for _, y, _ in txyzs])

        self.shape = btn.mv(tailX - joinTol, maxTnrY + btnTck + gapAdj/2, -1 - btnWth / 2)


class Tuners(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.DARK_GRAY,
    ):
        super().__init__(cfg, isCut, color)

        tXYZs = cfg.tnrXYZs
        tnrs = None
        for txyz in tXYZs:
            tnr = (
                Peg(cfg, isCut=isCut)
                if cfg.tnrCfg.is_peg()
                else Worm(cfg, isCut=isCut) if cfg.tnrCfg.is_worm() else None
            )
            if tnr != None:
                tnr = tnr.mv(txyz[0], txyz[1], txyz[2]).shape
                tnrs = tnr if tnrs == None else tnrs.join(tnr)

        self.shape = tnrs


class Spines(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.BLACK,
    ):
        super().__init__(cfg, isCut, color)

        cutAdj = (FIT_TOL + cfg.tolerance) if isCut else 0
        spX = cfg.spineX
        spLen = cfg.spineLen + 2 * cutAdj
        spY1 = cfg.spineY1
        spY2 = cfg.spineY2
        spHt = cfg.SPINE_HT + 2 * cutAdj
        spWth = cfg.SPINE_WTH + 2 * cutAdj
        fspTck = cfg.FRETBD_SPINE_TCK + 2 * cfg.tolerance

        sp = (
            cfg.api()
            .box(spLen, spWth, spHt)
            .mv(spX + spLen / 2, spY1, -fspTck - spHt / 2)
        )

        if spY2 != spY1:
            sp2 = (
                cfg.api()
                .box(spLen, spWth, spHt)
                .mv(spX + spLen / 2, spY2, -fspTck - spHt / 2)
            )
            sp = sp.join(sp2)

        self.shape = sp


class Strings(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.LITE_GRAY,
    ):
        super().__init__(cfg,isCut, color)

        cutAdj = FIT_TOL if isCut else 0
        srad = cfg.STR_RAD + cutAdj
        paths = cfg.stringPaths

        strs = None
        for p in paths:
            str = cfg.api().regpoly_sweep(srad, p)
            strs = str if strs == None else strs.join(str)

        self.shape = strs


class Texts(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = None,
    ):
        super().__init__(cfg, isCut, color)

        scLen = cfg.scaleLen
        backRat = cfg.CHM_BACK_RATIO
        tsf = cfg.txtSzFonts
        bodyWth = cfg.bodyWth
        botRat = cfg.BOT_RATIO
        midBotTck = cfg.extMidBotTck
        txtTck = botRat * bodyWth / 2 + midBotTck + 2

        allHt = sum([1.2 * size for _, size, _ in tsf])
        tx = 1.05 * scLen - allHt / (1 + backRat)
        lines: Shape = None
        for txt, sz, fnt in tsf:
            if (
                (txt is not None and len(txt.strip()) > 0)
                and not fnt is None
                and sz > 0
            ):
                line = (
                    cfg.api()
                    .text(txt, sz, txtTck, fnt)
                    .rotate_z(90)
                    .mv(tx + sz / 2, 0, 0)
                )
                lines = line if lines is None else lines.join(line)
            tx += sz

        if lines is not None and isCut:
            # Orig impl is ls = ls.mirror() but Blender text mirroring can lead to invalid meshes
            lines = lines.rotate_x(180)

        self.shape = lines


class TailEnd(LelePart):
    def __init__(
        self,
        cfg: LeleConfig,
        isCut: bool = True,
        color: ColorEnum = ColorEnum.CARBON,
    ):
        super().__init__(cfg, isCut, color)

        cfg = cfg
        jcTol = cfg.tolerance
        cutAdj = (FIT_TOL + jcTol) if isCut else 0
        tailX = cfg.tailX
        chmBackX = cfg.scaleLen + cfg.chmBack
        tailLen = tailX - chmBackX + 2 * cutAdj
        endWth = cfg.endWth + 2 * cutAdj
        botRat = cfg.BOT_RATIO
        midBotTck = cfg.extMidBotTck + 2 * cutAdj
        rimWth = cfg.rimWth + 2 * cutAdj

        top = None
        if midBotTck > 0:
            extTop = (
                cfg.api()
                .box(10 if isCut else rimWth, endWth, midBotTck)
                .mv(tailX + (5 - rimWth if isCut else -rimWth / 2), 0, -midBotTck / 2)
            )
            inrTop = (
                cfg.api()
                .box(2 * tailLen, endWth - 2 * rimWth, midBotTck)
                .mv(tailX - rimWth - tailLen, 0, -midBotTck / 2)
            )
            top = extTop.join(inrTop)

        extBot = (
            cfg.api()
            .cylinder_x(10 if isCut else rimWth, endWth / 2)
            .scale(1, 1, botRat)
            .mv(tailX + (5 - rimWth if isCut else -rimWth / 2), 0, -midBotTck)
        )
        inrBot = (
            cfg.api()
            .cylinder_x(2 * tailLen, endWth / 2 - rimWth)
            .scale(1, 1, botRat)
            .mv(tailX - rimWth - tailLen, 0, -midBotTck)
        )
        topCut = cfg.api().box(2000, 2000, 2000).mv(0, 0, 1000)
        bot = extBot.join(inrBot.mv(jcTol, 0, 0)).cut(topCut)
        if top is None:
            tail = bot
        else:
            tail = top.join(bot)

        if isCut:
            tail = tail.mv(0, 0, jcTol)

        self.shape = tail
