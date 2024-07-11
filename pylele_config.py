import datetime
import math
from enum import Enum
from pylele_utils import radians, degrees

"""
    Global Constants, Config classes
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
WHITE = (255, 255, 255)
LITE_GRAY = (192, 192, 192)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
CARBON = (32, 32, 32)


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
        buttonKeyLen: float = 6,
        buttonKeyRad: float = 2.25,
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
        self.buttonKeyRad = buttonKeyRad
        self.buttonKeyLen = buttonKeyLen
        self.buttonKeybaseRad = buttonKeybaseRad
        self.buttonKeybaseHt = buttonKeybaseHt

    def minGap(self) -> float:
        return self.diskTck + self.axleLen + self.gapAdj

    def tailAllow(self) -> float:
        return self.driveLen


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


class TunerType(Enum):
    FRICTION_PEG = 'friction'
    GOTOH_PEG = 'gotoh'
    WORM_TUNER = 'worm'
    BIGWORM_TUNER = 'bigWorm'

    def __str__(self):
        return self.value
    
    def config(self) -> TunerConfig:
        match self: 
            case TunerType.FRICTION_PEG:
                return FRICTION_PEG_CFG
            case TunerType.GOTOH_PEG:
                return GOTOH_PEG_CFG
            case TunerType.WORM_TUNER:
                return WORM_TUNER_CFG
            case TunerType.BIGWORM_TUNER:
                return BIGWORM_TUNER_CFG


class Implementation(Enum):
    CAD_QUERY = 'cadquery'
    BLENDER = 'blender' 
    TRIMESH = 'trimesh'

    def __str__(self):
        return self.value

    # for joins to have a little overlap
    def joinCutTol(self) -> float:
        return 0 if self == Implementation.CAD_QUERY else 0.01
    
class Fidelity(Enum):
    LOW = 'low'
    MEDIUM = 'medium' 
    HIGH = 'high' 

    def __str__(self):
        return self.value
    
    def exportTol(self) -> float:
        match self:
            case Fidelity.LOW:
                return 0.0005
            case Fidelity.MEDIUM:
                return 0.0002
            case Fidelity.HIGH:
                return 0.0001
    
    def smoothingSegments(self) -> int:
        match self:
            case Fidelity.LOW:
                return 17
            case Fidelity.MEDIUM:
                return 34
            case Fidelity.HIGH:
                return 51

class ModelLabel(Enum):
    NONE = 'none'
    SHORT = 'short' # without date
    LONG = 'long' # with date

    def __str__(self):
        return self.value

class LeleConfig:
    TOP_RATIO = 1/8 #.1
    BOT_RATIO = 2/3 #.666
    CHM_BACK_RATIO = 1/2  # to chmFront
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
    STR_RAD = 0.5
    TEXT_TCK = 20

    def __init__(
        self,
        scaleLen: float = SOPRANO_SCALE_LEN,
        sepTop: bool = False,
        sepNeck: bool = False,
        sepFretbd: bool = False,
        sepBrdg: bool = False,
        sepEnd: bool = False,
        wallTck: float = 4,
        chmLift: float = 0,
        chmRot: float = 0,
        endWth: float = 0,
        numStrs: int = 4,
        nutStrGap: float = 9,
        action: float = 2,
        tnrType: TunerType = TunerType.FRICTION_PEG, 
        half: bool = False,
        txtSzFonts: list[tuple[str, float, str]] =
            [('PYLELE', 28, 'Arial'), ('mind2form.com © 2024', 10, 'Arial')],
        modelLbl: ModelLabel = ModelLabel.LONG,
        dotRad: float = 1.5,
        fret2Dots: dict[int, int] =
            {3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1, 24: 3},
        fidelity: Fidelity = Fidelity.LOW,
        impl: Implementation = Implementation.CAD_QUERY,
    ):
        # Engine Implementation Config
        self.impl = impl
        self.fidelity = fidelity
        self.joinCutTol = impl.joinCutTol()
        self.tnrCfg = tnrType.config()
        
        # Length based configs
        self.scaleLen = scaleLen
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        self.fretbdRiseAng = 1 + numStrs/10
        self.wallTck = wallTck
        self.chmFront = scaleLen - self.fretbdLen - wallTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        self.bodyBackLen = self.chmBack + wallTck + self.tnrCfg.tailAllow()
        self.tailX = scaleLen + self.bodyBackLen
        self.isPeg = isinstance(self.tnrCfg, PegConfig)
        self.isWorm = isinstance(self.tnrCfg, WormConfig)
        self.numStrs = numStrs
        self.nutStrGap = nutStrGap
        self.nutWth = max(2,numStrs) * nutStrGap
        if self.isPeg:
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
        self.extMidTopTck = 1
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
        neckDX = 3
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
        self.chmOrig = (scaleLen, 0)
        self.chmPath = [
            (scaleLen - self.chmFront, 0),
            [
                (scaleLen - self.chmFront, .1, 0, 15),
                (scaleLen-.5*self.chmFront, .45*self.chmWth, 10, 2),
                (scaleLen, self.chmWth/2, 20, 0),
                (scaleLen + self.chmBack, .1, 0, -20),
            ],
            (scaleLen + self.chmBack, 0),
        ]
        self.rimWth = wallTck/2

        def genRimPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            cp1 = self.chmPath[1]  # using chamber path as basis
            rp = [
                (self.chmPath[0][0] - self.rimWth - cutAdj, self.chmPath[0][1]),
                [],
                (self.chmPath[2][0] + self.rimWth - cutAdj, self.chmPath[2][1]),
            ]
            pi = 0
            rp[1].append((
                cp1[pi][0] - self.rimWth - cutAdj, 
                cp1[pi][1], cp1[pi][2], cp1[pi][3],
            ))
            pi = 1
            rp[1].append((
                cp1[pi][0], cp1[pi][1] + self.rimWth + cutAdj, 
                cp1[pi][2], cp1[pi][3],
            ))
            pi = 2
            rp[1].append((
                cp1[pi][0], cp1[pi][1] + self.rimWth + cutAdj, 
                cp1[pi][2], cp1[pi][3],
            ))
            pi = 3
            rp[1].append((
                cp1[pi][0] + self.rimWth + cutAdj, 
                cp1[pi][1], cp1[pi][2], cp1[pi][3],
            ))
            return rp

        self.rimOrig = self.chmOrig
        self.rimPath = genRimPath()
        self.rimCutOrig = self.rimOrig
        self.rimCutPath = genRimPath(isCut=True)

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
            bodySpline = [
                (nkLen + neckDX, nkWth/2 - neckDY, 2*neckDX, 2*neckDY),
                (scaleLen - .7*bFrLen, .33*bWth, 10, 8),
                (scaleLen, bWth/2, 15, 0),
                (scaleLen + bBkLen, eWth/2 +.1, 
                 0 if endWth < self.tnrGap * numStrs else 5, 
                 -30 if endWth < self.tnrGap * numStrs else -15), 
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
        self.guideX = self.scaleLen + .9*self.chmBack
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
        wCfg: WormConfig = None if self.isPeg else self.tnrCfg
        tZBase = (self.extMidTopTck + .5) if self.isPeg \
            else (-wCfg.driveRad - wCfg.diskRad - wCfg.axleRad)

        def tzAdj(tY: float) -> float:
            return 0 if self.isWorm or tY > endWth/2 else \
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

        if self.isPeg:  # Worm drives has no string guide
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
            model += "-" + datetime.date.today().strftime("%m%d")
        return model
