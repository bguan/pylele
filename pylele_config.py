import math

"""
    Global Constants, Util Functions, Config classes
"""

SEMI_RATIO = 2**(1/12)
SOPRANO_SCALE_LEN = 330


def radians(deg):
    return deg * math.pi / 180


def degrees(rad):
    return rad*180 / math.pi


def accumDiv(x: float, n: int, div: float):
    return 0 if n <= 0 else x + accumDiv(x / div, n - 1, div)


# Peg config
class PegConfig:
    def __init__(
        self,
        majRad: float = 8,
        minRad: float = 4,
        botLen: float = 15,
        btnRad: float = 11.5,
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

# Parts config
#
# Note: Ellipse points seperated by arc distance calc taken from
# https://gamedev.stackexchange.com/questions/1692/what-is-a-simple-algorithm-for-calculating-evenly-distributed-points-on-an-ellip

class LeleConfig:
    BOT_RATIO = .65
    BRIDGE_HT = 8
    CHM_BACK_RATIO = .333  # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EXT_MID_TOP_TCK = .5
    EXT_MID_BOT_TCK = 3
    FIT_TOL = .1
    FILLET_RAD = .4
    FRET_HT = 1
    FRETBD_RATIO = 0.675  # to scaleLen
    FRETBD_SPINE_TCK = 1.5
    FRETBD_TCK = 2
    FRETBD_RISE_ANG = 1.2
    GUIDE_HT = 8
    GUIDE_RAD = 1.5
    GUIDE_SET = 1
    HEAD_WTH_RATIO = 1.15  # to nutWth
    HEAD_LEN_RATIO = .35  # to nutWth
    NECK_JNT_RATIO = .8  # to fretbdlen - necklen
    NECK_RATIO = .55  # to scaleLen
    NECK_WIDE_ANG = 1
    NUT_HT = 1.5
    RIM_WTH = 1.5
    RIM_TCK = 1.5
    SPINE_HT = 10.2  # give extra height to spine
    SPINE_WTH = 2.2  # give extra width to spine
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
        chmLift: float = 1,
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
        self.neckOrig = (0,0)
        self.neckPath = [
            (0, -self.nutWth/2), (self.neckLen, -self.neckWth/2),
            (self.neckLen, self.neckWth/2), (0, self.nutWth/2)
        ]
        self.neckJntLen = self.NECK_JNT_RATIO*(self.fretbdLen - self.neckLen)
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
        self.fbOrig = (0,0)
        self.fbPath = genFbPath()
        self.fbCutOrig = (-self.FIT_TOL, 0)
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
                (scaleLen - .65*self.chmFront, -.4*self.chmWth, 1, -.4),
                (scaleLen, -self.chmWth/2, 1, 0),
                (scaleLen + self.chmBack, 0, 0, 1),
            ]
        ]
        self.chmOrig = (scaleLen - self.chmFront, 0)
        def genRimPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = self.FIT_TOL if isCut else 0
            return [
                [
                    (scaleLen - self.chmFront -self.RIM_WTH -cutAdj, 0, 0, -1),
                    (
                        scaleLen - .65*self.chmFront -.5*self.RIM_WTH -.5*cutAdj,
                        -.4*self.chmWth -.5*self.RIM_WTH -.5*cutAdj, 
                        1, -.4,
                    ),
                    (scaleLen, -self.chmWth/2  -self.RIM_WTH -cutAdj, 1, 0),
                    (scaleLen + self.chmBack +self.RIM_WTH +cutAdj, 0, 0, 1),
                ]
            ]
        self.rimOrig = (scaleLen - self.chmFront -self.RIM_WTH,0)
        self.rimPath = genRimPath()
        self.rimCutOrig = (scaleLen - self.chmFront -self.RIM_WTH -self.FIT_TOL,0)
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
        self.headOrig = (0,0)

        # Body Configs
        self.bodyWth = self.chmWth + 2*chmTck
        self.bodyFrontLen = scaleLen - self.neckLen
        self.bodyBackLen = self.chmBack + chmTck + pegCfg.majRad + pegCfg.btnRad
        self.bodyLen = self.bodyFrontLen + self.bodyBackLen
        self.fullLen = self.headLen + self.bodyLen

        def genBodyPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = self.FIT_TOL if isCut else 0
            nkLen = self.neckLen - cutAdj
            nkWth = self.neckWth + 2*cutAdj
            bWth = self.bodyWth + 2*cutAdj
            bFrLen = self.bodyFrontLen + cutAdj
            bBkLen = self.bodyBackLen + cutAdj
            fWth = self.flatWth + 2*cutAdj if flatWth > 0 else 0
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

        self.bodyOrig = (self.neckLen, 0)
        self.bodyPath = genBodyPath()
        self.bodyCutOrig = (self.neckLen -self.FIT_TOL, 0)
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
        self.spineLen = self.headLen + self.scaleLen + self.chmBack + self.chmTck - 1
        self.spineGap = strGap if self.isOddStrs else 2*strGap
        self.spineY1 = -self.spineGap/2
        self.spineY2 = self.spineGap/2
        self.spineCutFilletPts = [
            (0, self.spineY1, 0),
            (0, self.spineY2, 0),
        ]

        # Guide config
        self.guideX = self.scaleLen + .9*self.chmBack
        self.guideZ = -self.GUIDE_SET + self.TOP_RATIO \
            * math.sqrt(self.bodyBackLen**2 - self.chmBack**2)
        self.guideWth = self.nutWth \
            + 2*math.tan(radians(self.NECK_WIDE_ANG))*self.guideX
        self.guidePostGap = self.guideWth/numStrs
        gY = self.GUIDE_RAD + 2*self.STR_RAD if self.isOddStrs else self.guidePostGap/2
        self.guideYs = [gY, -gY]
        for r in range((numStrs-1)//2):
            gY += self.guidePostGap
            self.guideYs.extend([gY, -gY])

        # Pegs config
        self.pegSetback = (pegCfg.majRad + pegCfg.btnRad)/2 -2
        # approx spline bout curve with ellipse but 'fatter'
        xmax = self.bodyBackLen - self.pegSetback
        ymax = .58*self.bodyWth + (.05*flatWth)**4 - self.pegSetback
        pDist = 2*pegCfg.btnRad + 1
        pX = xmax
        pY = 0 if self.isOddStrs else pegCfg.btnRad + .5
        zBase = self.EXT_MID_TOP_TCK + 1.5
        pZ = zBase + (math.sqrt((flatWth/2)**2 -pY**2) *self.TOP_RATIO if pY < flatWth/2 else 0)
        # start calc from middle out
        self.pegsXYZ = [(scaleLen + pX, 0, pZ)] if self.isOddStrs \
            else [(scaleLen + pX, pY, pZ), (scaleLen + pX, -pY, pZ)]
        for p in range((numStrs-1)//2):
            if pY + pDist < flatWth/2:
                pY += pDist
                # pX remain same
                pZ = zBase +math.sqrt((flatWth/2)**2 -pY**2) *self.TOP_RATIO
            else:
                """
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
                pY = pY + pDist / math.sqrt(1 + xmax**2 * pY**2 / (ymax**2 *(ymax**2 - pY**2)))
                pX = xmax * math.sqrt(1 - pY**2/ymax**2)
                pZ = zBase
            self.pegsXYZ.extend([(scaleLen + pX, pY, pZ), (scaleLen + pX, -pY, pZ)])
