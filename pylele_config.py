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
    BOT_RATIO = .7
    BRIDGE_HT = 8
    CHM_BACK_RATIO = .5  # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EXT_MID_TOP_TCK = 1
    EXT_MID_BOT_TCK = 4
    FIT_TOL = .1
    FILLET_RAD = .4
    FRET_HT = 1
    FRETBD_RATIO = 0.675  # to scaleLen
    FRETBD_SPINE_TCK = 2
    FRETBD_TCK = 2
    FRETBD_RISE_ANG = 1.5
    GUIDE_HT = 7
    GUIDE_RAD = 1.5
    GUIDE_SET = .5
    HEAD_WTH_RATIO = 1.15  # to nutWth
    HEAD_LEN_RATIO = .4  # to nutWth
    NECK_JNT_RATIO = .8  # to fretbdlen - necklen
    NECK_RATIO = .55  # to scaleLen
    NECK_WIDE_ANG = 1
    NUT_HT = 1.5
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
        chmLift: float = 2,
        chmTilt: float = -.53,
        flatWth: float = 0,
        numStrs: int = 4,
        nutStrGap: float = 9,
        action: float = 3,
        pegCfg: PegConfig = FRICTION_PEG_CFG,
        split: bool = False,
    ):
        # General configs
        self.split = split
        self.scaleLen = scaleLen
        self.sepTop = sepTop
        self.sepNeck = sepNeck
        self.sepFretbd = sepFretbd
        self.sepBrdg = sepBrdg
        self.sepGuide = sepGuide
        self.numStrs = numStrs
        self.isOddStrs = numStrs % 2 == 1
        self.flatWth = flatWth
        self.nutStrGap = nutStrGap
        self.action = action
        self.nutWth = numStrs * nutStrGap
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
        neckDX = 1
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
        self.chmTilt = chmTilt
        self.chmFront = scaleLen - self.fretbdLen - chmTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        self.chmWth = self.brdgWth * 3
        self.chmPath = [
            [
                (-self.chmFront, 0, 0, -1),
                (-.65*self.chmFront, -.4*self.chmWth, 1, -.4),
                (0, -self.chmWth/2, 1, 0),
                (self.chmBack, 0, 0, 1),
            ]
        ]
        self.chmOrig = (0, 0)
        self.rimWth = chmTck/2
        self.rimTck = 1
        def genRimPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = self.FIT_TOL if isCut else 0
            return [
                [
                    (scaleLen - self.chmFront -self.rimWth -cutAdj, 0, 0, -1),
                    (
                        scaleLen - .65*self.chmFront -.5*self.rimWth -.5*cutAdj,
                        -.4*self.chmWth -.5*self.rimWth -.5*cutAdj, 
                        1, -.4,
                    ),
                    (scaleLen, -self.chmWth/2  -self.rimWth -cutAdj, 1, 0),
                    (scaleLen + self.chmBack +self.rimWth +cutAdj, 0, 0, 1),
                ]
            ]
        self.rimOrig = (scaleLen - self.chmFront -self.rimWth,0)
        self.rimPath = genRimPath()
        self.rimCutOrig = (scaleLen - self.chmFront -self.rimWth -self.FIT_TOL,0)
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
            nkLen = self.neckLen
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
        self.brdgLen = nutStrGap
        self.brdgStrGap = self.brdgWth / numStrs

        # Spine configs
        self.spineX = -self.headLen
        self.spineLen = self.headLen + scaleLen + self.chmBack +self.rimWth
        self.spineGap = nutStrGap if self.isOddStrs else 2*nutStrGap
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
        gY = self.GUIDE_RAD + \
            (2*self.STR_RAD if self.isOddStrs else (self.guidePostGap/2 +self.STR_RAD))
        self.guideYs = [gY, -gY]
        for r in range((numStrs-1)//2):
            gY += self.guidePostGap
            self.guideYs.extend([gY, -gY])

        # Pegs config
        self.pegSetback = (pegCfg.majRad + pegCfg.btnRad)/2 -2
        # approx spline bout curve with ellipse but 'fatter'
        pXMax = self.bodyBackLen - self.pegSetback
        fatRat = .65 if flatWth == 0 else .505 + (flatWth/self.bodyWth)**1.05
        pYMax = fatRat*self.bodyWth -self.pegSetback 
        pDist = 2*pegCfg.btnRad + 1
        pX = pXMax
        pY = 0 if self.isOddStrs else pegCfg.btnRad + .5
        pZBase = self.EXT_MID_TOP_TCK + 1.5
        pMidZ = pZBase + (math.sqrt((flatWth/2)**2 -pY**2) *self.TOP_RATIO if pY < flatWth/2 else 0)
        pZ = pMidZ
        # start calc from middle out
        self.pegsXYZ = [(scaleLen + pX, 0, pZ)] if self.isOddStrs \
            else [(scaleLen + pX, pY, pZ), (scaleLen + pX, -pY, pZ)]
        for p in range((numStrs-1)//2):
            if pY + pDist < flatWth/2:
                pY += pDist
                # pX remain same
                pZ = pZBase +math.sqrt((flatWth/2)**2 -pY**2) *self.TOP_RATIO
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
                pY = pY + pDist / math.sqrt(1 + pXMax**2 * pY**2 / (pYMax**2 *(pYMax**2 - pY**2)))
                pX = pXMax * math.sqrt(1 - pY**2/pYMax**2)
                pZ = pZBase
            self.pegsXYZ.extend([(scaleLen + pX, pY, pZ), (scaleLen + pX, -pY, pZ)])
        
        # Strings config
        strOddMidPath = [
            (-self.headLen, 0, -self.FRETBD_SPINE_TCK - .5*self.SPINE_HT),
            (0, 0, self.FRETBD_TCK +self.NUT_HT +self.STR_RAD/2),
            (scaleLen, 0, self.brdgZ +self.brdgHt +1.5*self.STR_RAD),
            (self.guideX , 0, self.guideZ +self.GUIDE_HT -self.GUIDE_RAD -self.STR_RAD),
            (scaleLen +self.bodyBackLen - self.pegSetback, 0, pMidZ +self.pegCfg.holeHt)
        ]
        strEvenMidPathR = []
        strEvenMidPathL = []
        strEvenMidBrdgDY = self.brdgStrGap/2 - nutStrGap/2
        strEvenMidAng = math.atan(strEvenMidBrdgDY/scaleLen)

        # even middle string pair points is just odd middle string points with DY 
        # following same widening angle except ending point uing pegY and pegZ + peg hole height
        for pt in strOddMidPath:
            strY = (pegCfg.btnRad + .5) if pt == strOddMidPath[-1] else \
                nutStrGap/2 + pt[0]*math.tan(strEvenMidAng)
            strZ = (pZBase + pegCfg.holeHt) if pt == strOddMidPath[-1] else pt[2]
            strEvenMidPathR.append((pt[0], strY, strZ))
            strEvenMidPathL.append((pt[0],-strY, strZ))

        # add initial middle string if odd else middle string pairs
        self.stringPaths = [strOddMidPath] if self.isOddStrs \
            else [ strEvenMidPathR, strEvenMidPathL ]
        
        # add strings from middle out
        for si in range((numStrs-1)//2):
            strCnt = si+1
            strLastPath = self.stringPaths[-1]
            strPathR = []
            strPathL = []
            for pt in strLastPath:
                if pt == strLastPath[-1]:
                    strPegXYZ = self.pegsXYZ[2*si +(1 if self.isOddStrs else 2)]
                    strX = strPegXYZ[0]
                    strY = strPegXYZ[1]
                    strZ = strPegXYZ[2] + pegCfg.holeHt
                else:
                    strBrdgDY = (strCnt + (0 if self.isOddStrs else .5))*(self.brdgStrGap -nutStrGap)
                    strEvenAng = math.atan(strBrdgDY/scaleLen)
                    strX = pt[0]
                    strY = (strCnt + (0 if self.isOddStrs else .5))*nutStrGap + strX*math.tan(strEvenAng)
                    strZ = pt[2]
                strPathR.append((strX, strY, strZ))
                strPathL.append((strX,-strY, strZ))
            self.stringPaths.append(strPathR)
            self.stringPaths.append(strPathL)