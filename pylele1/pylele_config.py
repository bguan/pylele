
""" Pylele Configuration Module """

import datetime
import math

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from enum import IntEnum, Enum
from ast import literal_eval
from api.pylele_api import Fidelity, Implementation, LeleStrEnum
from api.pylele_utils import radians, degrees, accumDiv
from api.pylele_api_constants import FIT_TOL, FILLET_RAD, ColorEnum
from pylele_config_common import SEMI_RATIO, LeleScaleEnum, type_scale_len, TunerConfig, PegConfig, WormConfig, TunerType

"""
    Global Constants, Config classes
"""

DEFAULT_LABEL_SIZE = 9
DEFAULT_LABEL_SIZE_BIG = 24
DEFAULT_LABEL_SIZE_SMALL = 6
DEFAULT_LABEL_FONT = 'Verdana'

class ModelLabel(LeleStrEnum):
    """ Model Label """
    NONE = 'none'
    SHORT = 'short' # without date
    LONG = 'long' # with date

class LeleConfig:
    """ Pylele Configuration Class """
    TOP_RATIO = 1/8
    BOT_RATIO = 2/3
    CHM_BACK_RATIO = 1/2 # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EMBOSS_DEP = .5
    FRET_HT = 1
    FRETBD_RATIO = 0.635  # to scaleLen
    FRETBD_SPINE_TCK = 2 # need to be > 1mm more than RIM_TCK for fillets
    FRETBD_TCK = 2
    GUIDE_RAD = 1.55
    GUIDE_SET = 0
    HEAD_WTH_RATIO = 1.1  # to nutWth
    HEAD_LEN = 12
    MIN_NECK_WIDE_ANG = 1.2
    NECK_JNT_RATIO = .8  # to fretbdlen - necklen
    NECK_RATIO = .55  # to scaleLen
    MAX_FRETS = 24
    NUT_HT = 1.5
    RIM_TCK = 1
    SPINE_HT = 10
    SPINE_WTH = 2
    STR_RAD = .5
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
        chmRot: float = -.5,
        endWth: float = 0,
        numStrs: int = 4,
        nutStrGap: float = 9,
        action: float = 2,
        extMidTopTck: float = .5,
        tnrType: TunerType = TunerType.FRICTION.value,
        half: bool = False,
        txtSzFonts: list[tuple[str, float, str]] = [
            ('PYLELE', DEFAULT_LABEL_SIZE_BIG, DEFAULT_LABEL_FONT), 
            ('', DEFAULT_LABEL_SIZE_SMALL, None), # for empty line
            ('mind2form.com © 2024', DEFAULT_LABEL_SIZE, DEFAULT_LABEL_FONT),
        ],
        modelLbl: ModelLabel = ModelLabel.SHORT,
        dotRad: float = 1.5,
        fret2Dots: dict[int, int] =
            {3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1},
        fidelity: Fidelity = Fidelity.LOW,
        impl: Implementation = Implementation.CAD_QUERY,
    ):
        # Engine Implementation Config
        self.impl = impl
        self.fidelity = fidelity
        self.joinCutTol = impl.joinCutTol()
        self.tnrCfg = tnrType
        
        # Length based configs
        self.scaleLen = scaleLen
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        self.fretbdRiseAng = 1 + numStrs/10
        self.wallTck = wallTck
        self.chmFront = scaleLen - self.fretbdLen - wallTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        self.bodyBackLen = self.chmBack + wallTck + self.tnrCfg.tailAllow()
        self.tailX = scaleLen + self.bodyBackLen
        # self.isPeg = isinstance(self.tnrCfg, PegConfig)
        # self.isWorm = isinstance(self.tnrCfg, WormConfig)
        self.numStrs = numStrs
        self.nutStrGap = nutStrGap
        self.nutWth = max(2,numStrs) * nutStrGap
        if self.tnrCfg.is_peg():
            self.tnrSetback = self.tnrCfg.tailAllow()/2 - 2
            self.neckWideAng = self.MIN_NECK_WIDE_ANG
            self.tnrGap = self.tnrCfg.minGap()
        else:
            self.tnrSetback = self.tnrCfg.tailAllow()/2 + 1
            tnrX = scaleLen + self.bodyBackLen - self.tnrSetback
            tnrW = self.tnrCfg.minGap() * numStrs
            tnrNeckWideAng = degrees(math.atan((tnrW - self.nutWth)/2/tnrX))
            self.neckWideAng = max(self.MIN_NECK_WIDE_ANG, tnrNeckWideAng)
            tnrsWth = self.nutWth + 2*tnrX*math.tan(radians(self.neckWideAng))
            self.tnrGap = tnrsWth / numStrs

        self.half = half
        self.sepTop = sepTop
        self.sepNeck = sepNeck
        self.sepFretbd = sepFretbd
        self.sepBrdg = sepBrdg
        self.sepEnd = sepEnd
        self.modelLbl = modelLbl
        self.isOddStrs = numStrs % 2 == 1
        self.endWth = endWth
        self.action = action
        self.brdgWth = nutStrGap*(max(2,numStrs)-.5) + \
            2 * math.tan(radians(self.neckWideAng)) * self.scaleLen
        self.brdgStrGap = self.brdgWth / (numStrs-.5)
        self.neckLen = scaleLen * self.NECK_RATIO
        self.dotRad = dotRad
        self.fret2Dots = fret2Dots
        self.extMidTopTck = extMidTopTck
        self.extMidBotTck = max(0, 10 - numStrs**1.25)

        # Neck configs
        self.neckWth = self.nutWth + \
            2 * math.tan(radians(self.neckWideAng)) * self.neckLen
        self.neckOrig = (0, 0)
        self.neckPath = [
            (0, -self.nutWth/2), (self.neckLen, -self.neckWth/2),
            (self.neckLen, self.neckWth/2), (0, self.nutWth/2)
        ]
        self.neckJntLen = self.NECK_JNT_RATIO*(self.fretbdLen - self.neckLen)
        self.neckJntTck = self.FRETBD_SPINE_TCK + self.SPINE_HT
        self.neckJntWth = (1 if self.isOddStrs else 2)*nutStrGap + self.SPINE_WTH
        neckDX = 1
        neckDY = neckDX * math.tan(radians(self.neckWideAng))

        # Fretboard configs
        self.fretbdWth = self.nutWth + \
            2 * math.tan(radians(self.neckWideAng)) * self.fretbdLen
        self.fretbdHt = self.FRETBD_TCK + \
            math.tan(radians(self.fretbdRiseAng)) * self.fretbdLen

        def genFbPath(isCut: bool = False) -> list[tuple[float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            return [
                (-cutAdj, -self.nutWth/2 - cutAdj),
                (self.fretbdLen + 2*cutAdj, -self.fretbdWth/2 - cutAdj),
                (self.fretbdLen + 2*cutAdj, self.fretbdWth/2 + cutAdj),
                (-cutAdj, self.nutWth/2 + cutAdj),
            ]
        self.fbOrig = (0, 0)
        self.fbPath = genFbPath()
        self.fbCutOrig = (-FIT_TOL, 0)
        self.fbCutPath = genFbPath(isCut=True)
        self.fbSpX = self.NUT_HT
        self.fbSpineLen = self.neckLen - self.NUT_HT + self.neckJntLen

        # Chamber Configs
        self.chmLift = chmLift
        self.chmRot = chmRot
        self.chmWth = self.brdgWth * 3
        self.rimWth = wallTck/2

        # Head configs
        self.headWth = self.nutWth * self.HEAD_WTH_RATIO
        headDX = 1
        headDY = headDX * math.tan(radians(self.neckWideAng))
        self.headOrig = (0, 0)
        self.headPath = [
            (0, self.nutWth/2),
            [
                (-headDX, self.nutWth/2 + headDY, -headDX, -headDY),
                (-self.HEAD_LEN/2, self.headWth/2, -1.5, -.1),
                (-self.HEAD_LEN +.1, self.headWth/6, -.1, -1.5),
            ],
            (-self.HEAD_LEN, 0),
        ]

        # Body Configs
        self.bodyWth = self.chmWth + 2*wallTck
        self.bodyFrontLen = scaleLen - self.neckLen
        self.bodyLen = self.bodyFrontLen + self.bodyBackLen
        self.fullLen = self.HEAD_LEN + scaleLen + self.bodyLen
        self.bodyOrig = (self.neckLen, 0)
        def genBodyPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            nkLen = self.neckLen
            nkWth = self.neckWth + 2*cutAdj
            bWth = self.bodyWth + 2*cutAdj
            bFrLen = self.bodyFrontLen + cutAdj
            bBkLen = self.bodyBackLen + cutAdj
            eWth = min(bWth, endWth) + (2*cutAdj if endWth > 0 else 0)
            endFactor = math.sqrt(endWth/bWth)
            bodySpline = [
                (nkLen + neckDX, nkWth/2 + neckDY, 2*neckDX, 2*neckDY),
                (scaleLen - .63*bFrLen, .32*bWth, 10, 8),
                (scaleLen, bWth/2, 15, 0),
                (scaleLen + bBkLen, eWth/2 +.1, 6*endFactor, -33*(1-endFactor)),
            ]
            bodyPath = [
                (nkLen, nkWth/2),
                bodySpline,
                (scaleLen + bBkLen, eWth/2),
            ]
            if eWth > 0:
                bodyPath.insert(3,(scaleLen + bBkLen, 0))
            return bodyPath
        self.bodyPath = genBodyPath()
        self.bodyCutOrig = (self.neckLen - FIT_TOL, 0)
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
        f12Ht = self.FRETBD_TCK \
            + math.tan(radians(self.fretbdRiseAng)) * f12Len \
            + self.FRET_HT
        self.brdgZ = self.bodyWth/2 * self.TOP_RATIO + self.extMidTopTck - 1
        self.brdgHt = 2*(f12Ht + action - self.NUT_HT - self.STR_RAD/2) \
            - self.brdgZ
        self.brdgLen = nutStrGap

        # Spine configs
        self.spineX = -self.HEAD_LEN
        self.spineLen = self.HEAD_LEN + scaleLen + self.chmBack + self.rimWth
        self.spineGap = 0 if numStrs == 2 else (1 if self.isOddStrs else 2)*nutStrGap
        self.spineY1 = -self.spineGap/2
        self.spineY2 = self.spineGap/2

        # Guide config (Only for Pegs)
        self.guideHt = 6 + numStrs/2
        self.guideX = self.scaleLen + .95*self.chmBack
        self.guideZ = -self.GUIDE_SET \
            + self.TOP_RATIO * math.sqrt(self.bodyBackLen**2 - self.chmBack**2)
        self.guideWth = self.nutWth \
            + 2*math.tan(radians(self.neckWideAng))*self.guideX
        gGap = self.guideWth/numStrs
        self.guidePostGap = gGap
        gGapAdj = self.GUIDE_RAD

        # start calc from middle out
        gY = gGapAdj if self.isOddStrs else gGap/2 + gGapAdj
        self.guideYs = [gGapAdj +2*self.STR_RAD, -gGapAdj -2*self.STR_RAD] \
            if self.isOddStrs else [gY + self.STR_RAD, -gY - self.STR_RAD]
        for _ in range((numStrs-1)//2):
            gY += gGap
            self.guideYs.extend([gY + gGapAdj, -gY -gGapAdj])

        # Tuner config
        # approx spline bout curve with ellipse but 'fatter'
        tXMax = self.bodyBackLen - self.tnrSetback
        fatRat = .65 if endWth == 0 else .505 + (endWth/self.bodyWth)**1.05
        tYMax = fatRat*self.bodyWth - self.tnrSetback
        tX = tXMax
        tY = 0
        wCfg: WormConfig = None if self.tnrCfg.is_peg() else self.tnrCfg
        tZBase = (self.extMidTopTck + 2) if self.tnrCfg.is_peg() \
            else (-wCfg.driveRad - wCfg.diskRad - wCfg.axleRad)

        def tzAdj(tY: float) -> float:
            return 0 if self.tnrCfg.is_worm() or tY > endWth/2 else \
                 ((endWth/2)**2 - tY**2)**.5 * self.TOP_RATIO

        tMidZ = tZBase + tzAdj(tY)
        tZ = tMidZ
        tDist = self.tnrGap
        # start calc from middle out
        self.tnrXYZs = [(scaleLen + tX, 0, tZ)] if self.isOddStrs else []
        for p in range(numStrs//2):
            if tY + tDist < endWth/2:
                tY += tDist if self.isOddStrs or p > 0 else tDist/2
                # tX remain same
                tZ = tZBase + tzAdj(tY)
            else:
                """
                Note: Ellipse points seperated by arc distance calc taken from
                https://gamedev.stackexchange.com/questions/1692/what-is-a-simple-algorithm-for-calculating-evenly-distributed-points-on-an-ellip

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
                tY = tY + (tDist if self.isOddStrs or p > 0 else tDist/2) \
                    / math.sqrt(1 + tXMax**2 * tY**2 / (tYMax**2 * (tYMax**2 - tY**2)))
                tX = tXMax * math.sqrt(1 - tY**2/tYMax**2)
                tZ = tZBase

            self.tnrXYZs.extend(
                [(scaleLen + tX, tY, tZ), (scaleLen + tX, -tY, tZ)],
            )

        # Strings config
        strOddMidPath = [
            (-self.HEAD_LEN, 0, -self.FRETBD_SPINE_TCK - .5*self.SPINE_HT),
            (0, 0, self.FRETBD_TCK + self.NUT_HT + self.STR_RAD/2),
            (scaleLen, 0, self.brdgZ + self.brdgHt + 1.5*self.STR_RAD),
        ]

        if self.tnrCfg.is_peg():  # Worm drives has no string guide
            strOddMidPath.append(
                (self.guideX, 0,
                 self.guideZ + self.guideHt - self.GUIDE_RAD - self.STR_RAD)
            )

        strOddMidPath.append(
            (scaleLen + self.bodyBackLen - self.tnrSetback, 0,
             tMidZ + self.tnrCfg.holeHt)
        )

        strEvenMidPathR = []
        strEvenMidPathL = []
        strEvenMidBrdgDY = self.brdgStrGap/2 - nutStrGap/2
        strEvenMidAng = math.atan(strEvenMidBrdgDY/scaleLen)

        # even middle string pair points is just odd middle string points with DY
        # following same widening angle except ending point uing pegY and pegZ + peg hole height
        for pt in strOddMidPath:
            strY = (self.tnrGap/2) if pt == strOddMidPath[-1] \
                else nutStrGap/2 + pt[0]*math.tan(strEvenMidAng)
            strZ = (
                tZBase + self.tnrCfg.holeHt) if pt == strOddMidPath[-1] else pt[2]
            strEvenMidPathR.append((pt[0], strY, strZ))
            strEvenMidPathL.append((pt[0], -strY, strZ))

        # add initial middle string if odd else middle string pairs
        self.stringPaths = [strOddMidPath] if self.isOddStrs \
            else [strEvenMidPathR, strEvenMidPathL]

        # add strings from middle out
        for si in range((numStrs-1)//2):
            strCnt = si+1
            strLastPath = self.stringPaths[-1]
            strPathR = []
            strPathL = []
            for pt in strLastPath:
                if pt == strLastPath[-1]:
                    strPegXYZ = self.tnrXYZs[
                        2*si + (1 if self.isOddStrs else 2)
                    ]
                    strX = strPegXYZ[0]
                    strY = strPegXYZ[1]
                    strZ = strPegXYZ[2] + self.tnrCfg.holeHt
                else:
                    strBrdgDY = (strCnt + (0 if self.isOddStrs else .5))\
                        * (self.brdgStrGap - nutStrGap)
                    strEvenAng = math.atan(strBrdgDY/scaleLen)
                    strX = pt[0]
                    strY = nutStrGap*(strCnt + (0 if self.isOddStrs else .5))\
                        + strX*math.tan(strEvenAng)
                    strZ = pt[2]
                strPathR.append((strX, strY, strZ))
                strPathL.append((strX, -strY, strZ))
            self.stringPaths.append(strPathR)
            self.stringPaths.append(strPathL)

        # Text Config
        self.txtSzFonts = txtSzFonts
        if modelLbl != ModelLabel.NONE:
            lbl = self.genModelStr(modelLbl == ModelLabel.LONG)
            self.txtSzFonts.append((None, DEFAULT_LABEL_SIZE_SMALL, None))
            self.txtSzFonts.append((None, DEFAULT_LABEL_SIZE_SMALL, None))
            self.txtSzFonts.append((lbl, DEFAULT_LABEL_SIZE, DEFAULT_LABEL_FONT))

    def genModelStr(self, inclDate: bool = False) -> str:
        model = f"{self.scaleLen}{self.tnrCfg.code}{self.numStrs}"
        if self.sepTop:
            model += 'T'
        if self.sepNeck:
            model += 'N'
        if self.sepFretbd:
            model += 'F'
        if self.sepBrdg:
            model += 'B'
        if self.sepEnd:
            model += 'E'
        
        model += f"-{self.endWth:.0f}" + self.impl.code() + self.fidelity.code()

        if inclDate:
            model += "-" + datetime.date.today().strftime("%m%d")
        return model

    def __repr__(self):
        properties = '\n'.join(f"{key}={value!r}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}\n\n{properties}"
