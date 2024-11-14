#!/usr/bin/env python3

import datetime
from math import atan, inf, sqrt, tan
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from api.pylele_api import Fidelity, Implementation, StringEnum, ShapeAPI
from api.pylele_api_constants import FIT_TOL
from api.pylele_utils import radians, degrees
from pylele_config_common import LeleScaleEnum, WormConfig, TunerType

"""
    Global Constants, Config classes
"""

DEFAULT_LABEL_SIZE = 8
DEFAULT_LABEL_SIZE_BIG = 24
DEFAULT_LABEL_SIZE_SMALL = 6
DEFAULT_LABEL_FONT = "Verdana"


class ModelLabel(StringEnum):
    """Model Label"""

    NONE = "none"
    SHORT = "short"  # without date
    LONG = "long"  # with date


class LeleConfig:
    """Pylele Configuration Class"""

    TOP_RATIO = 1 / 8
    BOT_RATIO = 2 / 3
    HEAD_TOP_RATIO = 1 / 6
    CHM_BACK_RATIO = 1 / 2  # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EMBOSS_DEP = 0.5
    FRET_HT = 1
    FRETBD_RATIO = 0.635  # to scaleLen
    FRETBD_SPINE_TCK = 2
    FRETBD_TCK = 2
    GUIDE_RAD = 1.55
    GUIDE_SET = 0
    HEAD_WTH_RATIO = 1.1  # to nutWth
    MIN_NECK_WIDE_ANG = 1.2
    NECK_JNT_RATIO = 0.8  # to fretbdlen - necklen
    NECK_RATIO = 0.55  # to scaleLen
    MAX_FRETS = 24
    NUT_HT = 1.5
    RIM_TCK = 1
    SPINE_HT = 10
    SPINE_WTH = 2
    STR_RAD = 0.65
    TEXT_TCK = 30

    def __init__(
        self,
        scaleLen: float = LeleScaleEnum.SOPRANO,
        sepTop: bool = False,
        sepNeck: bool = False,
        sepFretbd: bool = False,
        sepBrdg: bool = False,
        sepEnd: bool = False,
        wallTck: float = 4,
        chmLift: float = 1,
        chmRot: float = -0.5,
        endWth: float = 0,
        numStrs: int = 4,
        nutStrGap: float = 9,
        action: float = 2,
        extMidTopTck: float = 0.5,
        tnrType: TunerType = TunerType.FRICTION,
        split: bool = False,
        noTxt: bool = False,
        txtSzFonts: list[tuple[str, float, str]] = [
            ("PYLELE", DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_FONT),
            ("", DEFAULT_LABEL_SIZE_SMALL, None),  # for empty line
            ("mind2form.com © 2024", DEFAULT_LABEL_SIZE, DEFAULT_LABEL_FONT),
        ],
        modelLbl: ModelLabel = ModelLabel.SHORT,
        dotRad: float = 1.5,
        fret2Dots: dict[int, int] = {
            3: 1,
            5: 2,
            7: 1,
            10: 1,
            12: 3,
            15: 1,
            17: 2,
            19: 1,
            22: 1,
        },
        fidelity: Fidelity = Fidelity.LOW,
        impl: Implementation = Implementation.CADQUERY,
    ):
        # Primary Configs: that others depends on
        self.impl = impl
        self.fidelity = fidelity
        self.tolerance = impl.tolerance()
        self.tnrCfg = tnrType.value

        self.scaleLen = scaleLen
        self.headLen = 2 * numStrs + scaleLen / 60
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        self.fretbdRiseAng = 1 + numStrs / 10
        self.wallTck = wallTck
        self.chmFront = scaleLen - self.fretbdLen - wallTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        (tnrFront, tnrBack, _, _, _, _) = self.tnrCfg.dims()
        bodyBackLen = self.chmBack + wallTck + tnrFront + tnrBack
        self.bodyBackLen = bodyBackLen
        self.tailX = scaleLen + bodyBackLen
        self.numStrs = numStrs
        self.nutStrGap = nutStrGap
        self.nutWth = max(2, numStrs) * nutStrGap
        tnrSetback = self.tnrCfg.tailAllow()
        if self.tnrCfg.is_peg():
            self.neckWideAng = self.MIN_NECK_WIDE_ANG
            self.tnrGap = self.tnrCfg.minGap()
        else:
            tnrX = scaleLen + bodyBackLen - tnrSetback
            tnrW = self.tnrCfg.minGap() * numStrs
            tnrNeckWideAng = degrees(atan((tnrW - self.nutWth) / 2 / tnrX))
            self.neckWideAng = max(self.MIN_NECK_WIDE_ANG, tnrNeckWideAng)
            tnrsWth = self.nutWth + 2 * tnrX * tan(radians(self.neckWideAng))
            self.tnrGap = tnrsWth / numStrs

        self.split = split
        self.sepTop = sepTop
        self.sepNeck = sepNeck
        self.sepFretbd = sepFretbd
        self.sepBrdg = sepBrdg
        self.sepEnd = sepEnd
        self.modelLbl = modelLbl
        self.isOddStrs = numStrs % 2 == 1
        self.endWth = endWth
        self.action = action
        self.brdgWth = (
            nutStrGap * (max(2, numStrs) - 0.5)
            + 2 * tan(radians(self.neckWideAng)) * self.scaleLen
        )
        self.brdgStrGap = self.brdgWth / (numStrs - 0.5)
        self.neckLen = scaleLen * self.NECK_RATIO
        self.dotRad = dotRad
        self.fret2Dots = fret2Dots
        self.extMidTopTck = extMidTopTck
        self.extMidBotTck = max(0, 10 - numStrs**1.25)

        # Neck configs
        self.neckWth = self.nutWth + 2 * tan(radians(self.neckWideAng)) * self.neckLen

        self.neckPath = [
            (0, self.nutWth / 2),
            (self.neckLen, self.neckWth / 2),
            (self.neckLen, -self.neckWth / 2),
            (0, -self.nutWth / 2),
        ]
        self.neckJntLen = self.NECK_JNT_RATIO * (self.fretbdLen - self.neckLen)
        self.neckJntTck = self.FRETBD_SPINE_TCK + self.SPINE_HT
        self.neckJntWth = self.SPINE_WTH + (1 if self.isOddStrs else 2) * nutStrGap
        neckDX = 1
        neckDY = neckDX * tan(radians(self.neckWideAng))

        # Fretboard configs
        self.fretbdWth = (
            self.nutWth + 2 * tan(radians(self.neckWideAng)) * self.fretbdLen
        )
        self.fretbdHt = (
            self.FRETBD_TCK + tan(radians(self.fretbdRiseAng)) * self.fretbdLen
        )

        def genFbPath(isCut: bool = False) -> list[tuple[float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            return [
                (-cutAdj, self.nutWth / 2 + cutAdj),
                (self.fretbdLen + 2 * cutAdj, self.fretbdWth / 2 + cutAdj),
                (self.fretbdLen + 2 * cutAdj, -self.fretbdWth / 2 - cutAdj),
                (-cutAdj, -self.nutWth / 2 - cutAdj),
            ]

        self.fbPath = genFbPath()
        self.fbCutPath = genFbPath(isCut=True)
        self.fbSpineLen = self.neckLen - self.NUT_HT + self.neckJntLen

        # Chamber Configs
        self.chmLift = chmLift
        self.chmRot = chmRot
        self.chmWth = self.brdgWth * self.CHM_BRDG_RATIO
        self.rimWth = wallTck / 2

        # Head configs
        self.headWth = self.nutWth * self.HEAD_WTH_RATIO
        headDX = 1
        headDY = headDX * tan(radians(self.neckWideAng))
        self.headOrig = (0, 0)
        self.headPath = [
            (0, self.nutWth / 2),
            [
                (-headDX, self.nutWth / 2 + headDY, headDY / headDX),
                (-self.headLen / 2, self.headWth / 2, 0),
                (-self.headLen, self.headWth / 6, -inf),
            ],
            (-self.headLen, 0),
        ]

        # Body Configs
        self.bodyWth = self.chmWth + 2 * wallTck
        self.bodyFrontLen = scaleLen - self.neckLen
        self.bodyOrig = (self.neckLen, 0)

        def genBodyPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            nkLen = self.neckLen
            nkWth = self.neckWth + 2 * cutAdj
            bWth = self.bodyWth + 2 * cutAdj
            bBkLen = bodyBackLen + cutAdj
            eWth = min(bWth, endWth) + (2 * cutAdj if endWth > 0 else 0)
            bodySpline = [
                (nkLen + neckDX, nkWth / 2 + neckDY, neckDY / neckDX, 0.5, 0.3),
                (scaleLen, bWth / 2, 0, 0.6),
                (scaleLen + bBkLen, eWth / 2, -inf, (1 - eWth / bWth) / 2),
            ]
            bodyPath = [(nkLen, nkWth / 2), bodySpline]
            if eWth > 0:
                bodyPath.append((scaleLen + bBkLen, 0))
            return bodyPath

        self.bodyPath = genBodyPath()
        self.bodyCutPath = genBodyPath(isCut=True)

        # Soundhole Config
        self.sndholeMaxRad = self.chmFront / 3
        self.sndholeMinRad = self.sndholeMaxRad / 4
        self.sndholeX = scaleLen - 0.5 * self.chmFront
        self.sndholeY = -(self.chmWth/2 - 2.7*self.sndholeMinRad) # not too close to edge
        self.sndholeAng = degrees(
            atan(2 * self.chmFront / (self.chmWth - self.neckWth))
        )

        # Bridge configs
        f12Len = scaleLen / 2
        f12Ht = (
            self.FRETBD_TCK + tan(radians(self.fretbdRiseAng)) * f12Len + self.FRET_HT
        )
        self.brdgZ = self.bodyWth / 2 * self.TOP_RATIO + self.extMidTopTck - 1.5
        self.brdgHt = 2 * (f12Ht + action - self.NUT_HT - self.STR_RAD / 2) - self.brdgZ
        self.brdgLen = nutStrGap

        # Spine configs
        self.spineX = -self.headLen
        self.spineLen = self.headLen + scaleLen + self.chmBack + 2
        self.spineGap = 0 if numStrs == 2 else (1 if self.isOddStrs else 2) * nutStrGap
        self.spineY1 = -self.spineGap / 2
        self.spineY2 = self.spineGap / 2

        # Guide config (Only for Pegs)
        self.guideHt = 6 + numStrs / 2
        self.guideX = self.scaleLen + 0.95 * self.chmBack
        self.guideZ = -self.GUIDE_SET + self.TOP_RATIO * sqrt(
            bodyBackLen**2 - self.chmBack**2
        )
        self.guideWth = self.nutWth + 2 * tan(radians(self.neckWideAng)) * self.guideX
        gGap = self.guideWth / numStrs
        self.guidePostGap = gGap
        gGapAdj = self.GUIDE_RAD

        # start calc from middle out
        gY = gGapAdj if self.isOddStrs else gGap / 2 + gGapAdj + 0.5 * self.STR_RAD
        self.guideYs = (
            [gGapAdj + 2 * self.STR_RAD, -gGapAdj - 2 * self.STR_RAD]
            if self.isOddStrs
            else [gY + self.STR_RAD, -gY - self.STR_RAD]
        )
        for gi in range((numStrs - 1) // 2):
            gY += gGap
            self.guideYs.extend([gY + gGapAdj, -gY - gGapAdj])

        # Tuner config
        # approx spline bout curve with ellipse but 'fatter'
        tXMax = bodyBackLen - tnrSetback
        fatRat = 0.7 + (endWth / self.bodyWth) / 2
        tYMax = fatRat * self.bodyWth - tnrSetback
        tX = tXMax
        tY = 0
        wCfg: WormConfig = None if self.tnrCfg.is_peg() else self.tnrCfg
        tZBase = (
            (self.extMidTopTck + 2)
            if self.tnrCfg.is_peg()
            else (-wCfg.driveRad - wCfg.diskRad - wCfg.axleRad)
        )

        def tzAdj(tY: float) -> float:
            return (
                0
                if self.tnrCfg.is_worm() or tY > endWth / 2
                else (((endWth / 2) ** 2 - tY**2) ** 0.5 * self.TOP_RATIO / 2 + 0.5)
            )

        tMidZ = tZBase + tzAdj(tY)
        tZ = tMidZ
        tDist = self.tnrGap
        # start calc from middle out
        self.tnrXYZs = [(scaleLen + tX, 0, tZ)] if self.isOddStrs else []
        for p in range(numStrs // 2):
            if tY + tDist < endWth / 2:
                tY += tDist if self.isOddStrs or p > 0 else tDist / 2
                # tX remain same
                tZ = tZBase + tzAdj(tY)
            else:
                """
                Note: Ellipse points seperated by arc distance calc taken from
                https://gamedev.stackexchange.com/questions/1692/\
                    what-is-a-simple-algorithm-for-calculating\
                    -evenly-distributed-points-on-an-ellip

                view as the back of ukulele, which flips XY, diff from convention & post
                  X
                  ^
                  |
                b +-------._  (y,x)
                  |         `@-._
                  |              `-.
                  |                 `.
                  |                   \
                 -+--------------------+---> Y
                 O|                    a

                y' = y + d / sqrt(1 + b²y² / (a²(a²-y²)))
                x' = b sqrt(1 - y'²/a²)
                """
                tY = tY + (tDist if self.isOddStrs or p > 0 else tDist / 2) / sqrt(
                    1 + tXMax**2 * tY**2 / (tYMax**2 * (tYMax**2 - tY**2))
                )
                tX = tXMax * sqrt(1 - tY**2 / tYMax**2)
                tZ = tZBase

            self.tnrXYZs.extend(
                [(scaleLen + tX, tY, tZ), (scaleLen + tX, -tY, tZ)],
            )

        # Strings config
        strOddMidPath = [
            (-self.headLen, 0, -self.FRETBD_SPINE_TCK - 0.2 * self.SPINE_HT),
            (0, 0, self.FRETBD_TCK + self.NUT_HT + self.STR_RAD / 2),
            (scaleLen, 0, self.brdgZ + self.brdgHt + 1.5 * self.STR_RAD),
        ]

        if self.tnrCfg.is_peg():  # Worm drives has no string guide
            strOddMidPath.append(
                (
                    self.guideX,
                    0,
                    self.guideZ + self.guideHt - self.GUIDE_RAD - 1.5 * self.STR_RAD,
                )
            )

        strOddMidPath.append(
            (scaleLen + bodyBackLen - tnrSetback, 0, tMidZ + self.tnrCfg.strHt())
        )

        strEvenMidPathR = []
        strEvenMidPathL = []
        strEvenMidBrdgDY = self.brdgStrGap / 2 - nutStrGap / 2
        strEvenMidAng = atan(strEvenMidBrdgDY / scaleLen)

        # even middle string pair pts is just odd middle string pts with DY
        # following same widening angle except ending point
        # uing pegY and pegZ + peg hole height
        for pt in strOddMidPath:
            strY = (
                (self.tnrGap / 2)
                if pt == strOddMidPath[-1]
                else nutStrGap / 2 + pt[0] * tan(strEvenMidAng)
            )
            strZ = (tZBase + self.tnrCfg.strHt()) if pt == strOddMidPath[-1] else pt[2]
            strEvenMidPathR.append((pt[0], strY, strZ))
            strEvenMidPathL.append((pt[0], -strY, strZ))

        # add initial middle string if odd else middle string pairs
        self.stringPaths = (
            [strOddMidPath] if self.isOddStrs else [strEvenMidPathR, strEvenMidPathL]
        )

        # add strings from middle out
        for si in range((numStrs - 1) // 2):
            strCnt = si + 1
            strLastPath = self.stringPaths[-1]
            strPathR = []
            strPathL = []
            for pt in strLastPath:
                if pt == strLastPath[-1]:
                    strPegXYZ = self.tnrXYZs[2 * si + (1 if self.isOddStrs else 2)]
                    strX = strPegXYZ[0]
                    strY = strPegXYZ[1]
                    strZ = strPegXYZ[2] + self.tnrCfg.strHt()
                else:
                    strBrdgDY = (strCnt + (0 if self.isOddStrs else 0.5)) * (
                        self.brdgStrGap - nutStrGap
                    )
                    strEvenAng = atan(strBrdgDY / scaleLen)
                    strX = pt[0]
                    strY = nutStrGap * (
                        strCnt + (0 if self.isOddStrs else 0.5)
                    ) + strX * tan(strEvenAng)
                    strZ = pt[2]
                strPathR.append((strX, strY, strZ))
                strPathL.append((strX, -strY, strZ))
            self.stringPaths.append(strPathR)
            self.stringPaths.append(strPathL)

        # Text Config
        self.noTxt = noTxt
        self.txtSzFonts = [] if noTxt else txtSzFonts
        self.modelLbl = ModelLabel.NONE if noTxt else modelLbl
        if self.modelLbl != ModelLabel.NONE:
            lbl = self.genModelStr(modelLbl == ModelLabel.LONG)
            if self.txtSzFonts[-1][0] != lbl:  # HACK to prevent infinite append
                self.txtSzFonts.append((None, DEFAULT_LABEL_SIZE_BIG, None))
                self.txtSzFonts.append(
                    (lbl, DEFAULT_LABEL_SIZE_SMALL, DEFAULT_LABEL_FONT)
                )

    def genModelStr(self, inclDate: bool = False) -> str:
        model = f"{self.scaleLen}{self.tnrCfg.code}{self.numStrs}"
        if self.sepTop:
            model += "T"
        if self.sepNeck:
            model += "N"
        if self.sepFretbd:
            model += "F"
        if self.sepBrdg:
            model += "B"
        if self.sepEnd:
            model += "E"

        model += f"-{self.endWth:.0f}" + self.impl.code() + self.fidelity.code()

        if inclDate:
            model += "-" + datetime.date.today().strftime("%m%d")
        return model

    def api(self):
        return self.impl.get_api(fidelity=self.fidelity)

    def __repr__(self):
        class_vars_str = "\n".join(
            f"{key}={value!r}"
            for key, value in self.__class__.__dict__.items()
            if not callable(value) and not key.startswith("__")
        )
        instance_vars_str = "\n".join(
            f"{key}={value!r}" for key, value in vars(self).items()
        )
        return f"{self.__class__.__name__}\n{class_vars_str}\n{instance_vars_str}"
