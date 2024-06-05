import datetime
import math
from enum import Enum

"""
    Global Constants, Util Functions, Config classes
"""

SEMI_RATIO = 2**(1/12)
FIT_TOL = .1
FILLET_RAD = .4
SOPRANO_SCALE_LEN = 330
CONCERT_SCALE_LEN = 370
TENOR_SCALE_LEN = 430
DEFAULT_LABEL_SIZE = 12
DEFAULT_LABEL_SIZE_BIG = 28
DEFAULT_LABEL_SIZE_SMALL = 8
DEFAULT_LABEL_FONT = 'Arial'

def radians(deg: float = 0) -> float:
    return deg * math.pi / 180


def degrees(rad: float = 0) -> float:
    return rad*180 / math.pi


def accumDiv(x: float, n: int, div: float) -> float:
    return 0 if n <= 0 else x + accumDiv(x / div, n - 1, div)


# Tuner config

class TunerConfig:
    def __init__(
        self,
        holeHt: float = 8,
        code: str = '?',
    ):
        self.holeHt = holeHt
        self.code = code

    def minGap(self) -> float:
        pass

    def tailAllow(self) -> float:
        pass


class PegConfig(TunerConfig):
    def __init__(
        self,
        majRad: float = 8,
        minRad: float = 4,
        botLen: float = 15,
        btnRad: float = 11.5,
        midTck: float = 10,
        holeHt: float = 8,
        code: str = 'P',
    ):
        super().__init__(holeHt, code = code)
        self.majRad = majRad
        self.minRad = minRad
        self.botLen = botLen
        self.btnRad = btnRad
        self.midTck = midTck

    def minGap(self) -> float:
        return 2*max(self.majRad, self.btnRad) + 1

    def tailAllow(self) -> float:
        return self.majRad + self.btnRad


class WormConfig(TunerConfig):
    def __init__(
        self,
        holeHt: float = 23,
        slitLen: float = 10,
        slitWth: float = 3,
        diskTck: float = 5,
        diskRad: float = 7.7,
        axleRad: float = 3,
        axleLen: float = 6,  # original worm tuner has 8mm axle
        driveRad: float = 4,
        driveLen: float = 14,
        driveOffset: float = 9.75,
        gapAdj: float = 1,
        buttonTck: float = 9.5,
        buttonWth: float = 16,
        buttonHt: float = 8,
        buttonLen: float = 6,
        buttonKeybaseRad: float = 3.8,
        buttonKeybaseHt: float = 3,
        code: str = 'W',
    ):
        super().__init__(holeHt, code = code)
        self.slitLen = slitLen
        self.slitWth = slitWth
        self.diskTck = diskTck
        self.diskRad = diskRad
        self.axleRad = axleRad
        self.axleLen = axleLen
        self.driveRad = driveRad
        self.driveLen = driveLen
        self.driveOffset = driveOffset
        self.gapAdj = gapAdj
        self.buttonTck = buttonTck
        self.buttonWth = buttonWth
        self.buttonHt = buttonHt
        self.buttonLen = buttonLen
        self.buttonKeybaseRad = buttonKeybaseRad
        self.buttonKeybaseHt = buttonKeybaseHt

    def minGap(self) -> float:
        return self.diskTck + self.axleLen + self.gapAdj

    def tailAllow(self) -> float:
        return self.driveLen + 2


FRICTION_PEG_CFG = PegConfig()
GOTOH_PEG_CFG = PegConfig(
    majRad=7.7,
    minRad=4.8,
    botLen=15,
    btnRad=9.5,
    midTck=11,
    holeHt=10,
    code = 'G',
)
WORM_TUNER_CFG = WormConfig()
BIGWORM_TUNER_CFG = WormConfig(
    holeHt=30,
    slitLen=10,
    diskTck=5 * 1.5,
    diskRad=7.7 * 1.5,
    axleRad=3 * 1.5,
    axleLen=7,
    driveRad=4 * 1.5,
    driveLen=14 * 1.5,
    driveOffset=9.75 * 1.5,
    gapAdj=1.5,
    code = 'B',
)


# Parts config

class ModelLabel(Enum):
    NONE = 'none'
    SHORT = 'short' # without date
    LONG = 'long' # with date

    def __str__(self):
        return self.value

class LeleConfig:
    BOT_RATIO = .7
    CHM_BACK_RATIO = .5  # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EMBOSS_DEP = .5
    EXT_MID_TOP_TCK = 1
    EXT_MID_BOT_TCK = 4
    FRET_HT = 1
    FRETBD_RATIO = 0.635  # to scaleLen
    FRETBD_SPINE_TCK = 1
    FRETBD_TCK = 2
    FRETBD_RISE_ANG = 1.35
    GUIDE_HT = 7
    GUIDE_RAD = 1.55
    GUIDE_SET = 0
    HEAD_WTH_RATIO = 1.15  # to nutWth
    HEAD_LEN_RATIO = .4  # to nutWth
    MIN_NECK_WIDE_ANG = 1.2
    NECK_JNT_RATIO = .8  # to fretbdlen - necklen
    NECK_RATIO = .55  # to scaleLen
    MAX_FRETS = 24
    NUT_HT = 1.5
    RIM_TCK = 1
    SPINE_HT = 10.2  # give extra height to spine
    SPINE_WTH = 2.2  # give extra width to spine
    STR_RAD = 0.5
    TEXT_TCK = 20
    TOP_RATIO = .1

    def __init__(
        self,
        scaleLen: float = SOPRANO_SCALE_LEN,
        sepTop: bool = False,
        sepNeck: bool = False,
        sepFretbd: bool = False,
        sepBrdg: bool = False,
        sepEnd: bool = False,
        wallTck: float = 4,
        chmLift: float = 2,
        chmRot: float = -.53,
        endWth: float = 0,
        numStrs: int = 4,
        nutStrGap: float = 9,
        action: float = 2,
        tnrCfg: TunerConfig = FRICTION_PEG_CFG,
        half: bool = False,
        txtSzFonts: list[tuple[str, float, str]] =
            [('PYLELE', 28, 'Arial'), ('mind2form.com © 2024', 10, 'Arial')],
        modelLbl: ModelLabel = ModelLabel.LONG,
        dotRad: float = 1.5,
        fret2Dots: dict[int, int] =
            {3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1, 24: 3}
    ):
        # Length based configs
        self.scaleLen = scaleLen
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        self.wallTck = wallTck
        self.chmFront = scaleLen - self.fretbdLen - wallTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        self.bodyBackLen = self.chmBack + wallTck + tnrCfg.tailAllow()
        self.isPeg = isinstance(tnrCfg, PegConfig)
        self.isWorm = isinstance(tnrCfg, WormConfig)
        self.numStrs = numStrs
        self.nutStrGap = nutStrGap
        self.nutWth = numStrs * nutStrGap
        if self.isPeg:
            self.tnrSetback = tnrCfg.tailAllow()/2 - 2
            self.neckWideAng = self.MIN_NECK_WIDE_ANG
            self.tnrGap = tnrCfg.minGap()
        else:
            self.tnrSetback = tnrCfg.tailAllow()/2 + 2
            tnrX = scaleLen + self.bodyBackLen - self.tnrSetback
            tnrW = tnrCfg.minGap() * numStrs
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
        self.tnrCfg = tnrCfg
        self.brdgWth = nutStrGap*(numStrs-.5) + \
            2 * math.tan(radians(self.neckWideAng)) * self.scaleLen
        self.brdgStrGap = self.brdgWth / (numStrs-.5)
        self.neckLen = scaleLen * self.NECK_RATIO
        self.dotRad = dotRad
        self.fret2Dots = fret2Dots

        # Neck configs
        self.neckWth = self.nutWth + \
            2 * math.tan(radians(self.neckWideAng)) * self.neckLen
        self.neckOrig = (0, 0)
        self.neckPath = [
            (0, -self.nutWth/2), (self.neckLen, -self.neckWth/2),
            (self.neckLen, self.neckWth/2), (0, self.nutWth/2)
        ]
        self.neckJntLen = self.NECK_JNT_RATIO*(self.fretbdLen - self.neckLen)
        neckDX = 1
        neckDY = neckDX * math.tan(radians(self.neckWideAng))

        # Fretboard configs
        self.fretbdWth = self.nutWth + \
            2 * math.tan(radians(self.neckWideAng)) * self.fretbdLen
        self.fretbdHt = self.FRETBD_TCK + \
            math.tan(radians(self.FRETBD_RISE_ANG)) * self.fretbdLen

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
        self.chmPath = [[
            (scaleLen - self.chmFront, 0, 0, -1),
            (scaleLen-.5*self.chmFront, -(5/11) *
             self.chmWth, 1, -(self.chmWth/self.chmFront/6)),
            (scaleLen, -self.chmWth/2, 1, 0),
            (scaleLen + self.chmBack, 0, 0, 1),
        ]]
        self.chmOrig = (scaleLen, 0)
        self.rimWth = wallTck/2

        def genRimPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            cp0 = self.chmPath[0]  # using chamber path as basis
            rp = [[]]
            pi = 0
            rp[0].append((
                cp0[pi][0] - self.rimWth -
                cutAdj, cp0[pi][1], cp0[pi][2], cp0[pi][3]
            ))
            pi = 1
            rp[0].append((
                cp0[pi][0] - .8*self.rimWth - cutAdj,
                cp0[pi][1] - .6*self.rimWth - cutAdj,
                cp0[pi][2],
                cp0[pi][3],
            ))
            pi = 2
            rp[0].append((
                cp0[pi][0], cp0[pi][1] - self.rimWth -
                cutAdj, cp0[pi][2], cp0[pi][3]
            ))
            pi = 3
            rp[0].append((
                cp0[pi][0] + self.rimWth +
                cutAdj, cp0[pi][1], cp0[pi][2], cp0[pi][3]
            ))
            return rp

        self.rimOrig = self.chmOrig
        self.rimPath = genRimPath()
        self.rimCutOrig = self.rimOrig
        self.rimCutPath = genRimPath(isCut=True)

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
        self.headOrig = (0, 0)

        # Body Configs
        self.bodyWth = self.chmWth + 2*wallTck
        self.bodyFrontLen = scaleLen - self.neckLen
        self.bodyLen = self.bodyFrontLen + self.bodyBackLen
        self.fullLen = self.headLen + scaleLen + self.bodyLen

        def genBodyPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            nkLen = self.neckLen
            nkWth = self.neckWth + 2*cutAdj
            bWth = self.bodyWth + 2*cutAdj
            bFrLen = self.bodyFrontLen + cutAdj
            bBkLen = self.bodyBackLen + cutAdj
            fWth = self.endWth + 2*cutAdj if endWth > 0 else 0
            bodySpline = [
                (nkLen + neckDX, -nkWth/2 - neckDY, neckDX, -neckDY),
                (scaleLen - (.7)*bFrLen, -(1/3)*bWth, 1, -(2/3)*(bWth/bFrLen)),
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

        self.bodyOrig = (self.neckLen, 0)
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
            + math.tan(radians(self.FRETBD_RISE_ANG)) * f12Len \
            + self.FRET_HT
        self.brdgZ = self.bodyWth/2 * self.TOP_RATIO + self.EXT_MID_TOP_TCK - 1
        self.brdgHt = 2*(f12Ht + action - self.NUT_HT - self.STR_RAD/2) \
            - self.brdgZ
        self.brdgLen = nutStrGap

        # Spine configs
        self.spineX = -self.headLen
        self.spineLen = self.headLen + scaleLen + self.chmBack + self.rimWth
        self.spineGap = nutStrGap if self.isOddStrs else 2*nutStrGap
        self.spineY1 = -self.spineGap/2
        self.spineY2 = self.spineGap/2
        self.spineCutFilletPts = [
            (0, self.spineY1, 0),
            (0, self.spineY2, 0),
        ]

        # Guide config (Only for Pegs)
        self.guideX = self.scaleLen + .9*self.chmBack
        self.guideZ = -self.GUIDE_SET \
            + self.TOP_RATIO * math.sqrt(self.bodyBackLen**2 - self.chmBack**2)
        self.guideWth = self.nutWth \
            + 2*math.tan(radians(self.neckWideAng))*self.guideX
        self.guidePostGap = self.guideWth/numStrs
        gY = self.GUIDE_RAD \
            + (2*self.STR_RAD if self.isOddStrs else (self.guidePostGap/2 + self.STR_RAD))
        self.guideYs = [gY, -gY]
        for r in range((numStrs-1)//2):
            gY += self.guidePostGap
            self.guideYs.extend([gY, -gY])

        # Tuner config
        # approx spline bout curve with ellipse but 'fatter'
        tXMax = self.bodyBackLen - self.tnrSetback
        fatRat = .65 if endWth == 0 else .505 + (endWth/self.bodyWth)**1.05
        tYMax = fatRat*self.bodyWth - self.tnrSetback
        tDist = self.tnrGap
        tX = tXMax
        tY = 0
        wCfg: WormConfig = None if self.isPeg else tnrCfg
        tZBase = (self.EXT_MID_TOP_TCK + 2.5) if self.isPeg \
            else (-wCfg.driveRad - wCfg.diskRad - wCfg.axleRad - 1)

        def tzAdj(tY: float) -> float:
            return 0 if self.isWorm or tY > endWth/2 else \
                ((endWth/2)**2 - tY**2)**.4 * self.TOP_RATIO

        tMidZ = tZBase + tzAdj(tY)
        tZ = tMidZ
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
            (-self.headLen, 0, -self.FRETBD_SPINE_TCK - .5*self.SPINE_HT),
            (0, 0, self.FRETBD_TCK + self.NUT_HT + self.STR_RAD/2),
            (scaleLen, 0, self.brdgZ + self.brdgHt + 1.5*self.STR_RAD),
        ]

        if self.isPeg:  # Worm drives has no string guide
            strOddMidPath.append(
                (self.guideX, 0,
                 self.guideZ + self.GUIDE_HT - self.GUIDE_RAD - self.STR_RAD)
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
                tZBase + tnrCfg.holeHt) if pt == strOddMidPath[-1] else pt[2]
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
                    strZ = strPegXYZ[2] + tnrCfg.holeHt
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
            self.txtSzFonts.append((None, DEFAULT_LABEL_SIZE, None))
            self.txtSzFonts.append((lbl, DEFAULT_LABEL_SIZE, DEFAULT_LABEL_FONT))

    def genModelStr(self, inclDate: bool = True) -> str:
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
        if inclDate:
            model += "-" + datetime.date.today().strftime("%y%m%d")
        return model
