#!/usr/bin/env python3

""" Pylele Configuration Module """

import argparse
from math import atan, inf, sqrt, tan

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Fidelity, Implementation, LeleStrEnum
from api.pylele_utils import radians, degrees, accumDiv
from api.pylele_api_constants import FIT_TOL, FILLET_RAD, ColorEnum
from pylele_config_common import SEMI_RATIO, LeleScaleEnum, TunerConfig, PegConfig, WormConfig, TunerType

DEFAULT_FLAT_BODY_THICKNESS=25

class LeleBodyType(LeleStrEnum):
    """ Body Type """
    GOURD = 'gourd'
    FLAT  = 'flat'
    HOLLOW = 'hollow'
    TRAVEL = 'travel'

WORM    = ['-t','worm'   ,'-e','60','-E','-wah','-wsl','35','-whk']
BIGWORM = ['-t','bigworm','-e','85','-E','-wah','-wsl','45','-whk','-fbt','35']

CONFIGURATIONS = {
        'default'        : [],
        'gourd_worm'     : WORM,
        'flat'           : WORM    + ['-bt', LeleBodyType.FLAT],
        'flat_bigworm'   : BIGWORM + ['-bt', LeleBodyType.FLAT],
        'hollow_bigworm' : BIGWORM + ['-bt', LeleBodyType.HOLLOW],
        'travel_bigworm' : BIGWORM + ['-bt', LeleBodyType.TRAVEL,'-w','25']
    }

class AttrDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

def tzAdj(tY: float, tnrType: TunerType, endWth: float, top_ratio: float) -> float:
    """ Adjust Tuner Z """
    return 0 if tnrType.is_worm() or tY > endWth/2 else \
            ((endWth/2)**2 - tY**2)**.5 * top_ratio - 1

def pylele_config_parser(parser = None):
    """
    Pylele Base Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    ## config overrides ###########################################

    parser.add_argument("-cfg", "--configuration",
                        help="Configuration",
                        type=str,choices=CONFIGURATIONS.keys(),
                        default=None)
    
    ## Numeric config options ###########################################
    parser.add_argument("-s", "--scale_length", 
                        help=f"Scale Length [mm], or {LeleScaleEnum.list()}, default: {LeleScaleEnum.SOPRANO.name}={LeleScaleEnum.SOPRANO.value}",
                        type=LeleScaleEnum.type, default=LeleScaleEnum.SOPRANO)
    parser.add_argument("-n", "--num_strings", help="Number of strings, default 4",
                        type=int, default=4)
    parser.add_argument("-a", "--action", help="Strings action [mm], default 2",
                        type=float, default=2)
    parser.add_argument("-g", "--nut_string_gap", help="Nut to String gap [mm], default 9",
                        type=float, default=9)
    parser.add_argument("-e", "--end_flat_width", help="Flat width at tail end [mm], default 0",
                        type=float, default=0)

    ## Body Type config options ###########################################

    parser.add_argument("-bt", "--body_type",
                    help="Body Type",
                    type=LeleBodyType,
                    choices=list(LeleBodyType),
                    default=LeleBodyType.GOURD
                    )
    
    parser.add_argument("-fbt", "--flat_body_thickness", help=f"Body thickness [mm] when flat body, default {DEFAULT_FLAT_BODY_THICKNESS}",
                        type=float, default=DEFAULT_FLAT_BODY_THICKNESS)

    ## Chamber config options ###########################################

    parser.add_argument("-w", "--wall_thickness", help="Chamber Wall Thickness [mm], default 4",
                        type=float, default=4)

    ## Non-Numeric config options #######################################

    parser.add_argument("-t", "--tuner_type", help=f"Type of tuners, default; {TunerType.FRICTION.name}",
                        type=str.upper, choices=TunerType.list(), default=TunerType.FRICTION.name)

    ## Cut options ######################################################

    parser.add_argument("-T", "--separate_top",
                        help="Split body top from body back.",
                        action='store_true')
    parser.add_argument("-N", "--separate_neck",
                        help="Split neck from body.",
                        action='store_true')
    parser.add_argument("-F", "--separate_fretboard",
                        help="Split fretboard from neck back.",
                        action='store_true')
    parser.add_argument("-B", "--separate_bridge",
                        help="Split bridge from body.",
                        action='store_true')
    parser.add_argument("-G", "--separate_guide",
                        help="Split guide from body.",
                        action='store_true')
    parser.add_argument("-E", "--separate_end",
                        help="Split end block from body.",
                        action='store_true')
    parser.add_argument("-H", "--half",
                        help="Half Split",
                        action='store_true')

    return parser


class LeleConfig:
    """ Pylele Configuration Class """
    TOP_HEAD_RATIO = 1/4
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
    # HEAD_LEN = 12
    MIN_NECK_WIDE_ANG = 1.2
    NECK_JNT_RATIO = .8  # to fretbdlen - necklen
    NECK_RATIO = .55  # to scaleLen
    MAX_FRETS = 24
    NUT_HT = 1.5
    RIM_TCK = 1
    SPINE_HT = 10
    SPINE_WTH = 2
    STR_RAD = .6
    TEXT_TCK = 30
    extMidTopTck = .5

    def gen_parser(self,parser=None):
        """
        LeleSolid Command Line Interface
        """
        return pylele_config_parser(parser=parser)

    def parse_args(self, args=None):
        """ Parse Command Line Arguments """
        return self.gen_parser().parse_args(args=args)

    def genFbPath(self, isCut: bool = False) -> list[tuple[float, float]]:
        """ Generate Fretboard Path """
        cutAdj = FIT_TOL if isCut else 0
        return [
               (-cutAdj, self.nutWth/2 + cutAdj),
                (self.fretbdLen + 2*cutAdj, self.fretbdWth/2 + cutAdj),
                (self.fretbdLen + 2*cutAdj, -self.fretbdWth/2 - cutAdj),
                (-cutAdj, -self.nutWth/2 - cutAdj),
            ]
    
    def soundhole_config(self, scaleLen: float) -> float:
        """ Soundhole Configuration """
        cfg = AttrDict()
        cfg.sndholeX = scaleLen - .5*self.chmFront
        cfg.sndholeY = -(self.chmWth - self.fretbdWth)/2
        cfg.sndholeMaxRad = self.chmFront/3
        cfg.sndholeMinRad = cfg.sndholeMaxRad/4
        cfg.sndholeAng = degrees(
            atan(2 * self.bodyFrontLen/(self.chmWth - self.neckWth))
        )
        return cfg
    
    def fbSpineLen(self) -> float:
        """ Spine Length """
        return self.neckLen - self.NUT_HT + self.neckJntLen

    def __init__(
        self,
        args = None,
        cli = None
    ):
        if cli is None:
            self.cli = self.parse_args(args=args)
        else:
            self.cli = cli

        scaleLen=float(self.cli.scale_length)        
        action=self.cli.action
        numStrs=self.cli.num_strings
        nutStrGap=self.cli.nut_string_gap
        endWth=self.cli.end_flat_width
        wallTck=self.cli.wall_thickness
        tnrType=TunerType[self.cli.tuner_type].value
            
        # Engine Implementation Config
        # self.impl = impl
        # self.fidelity = fidelity
        # self.joinCutTol = impl.joinCutTol()
        # self.tnrCfg = tnrType
        # self.body_type = body_type
        
        # Length based configs
        # self.scaleLen = scaleLen
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        self.fretbdRiseAng = 1 + numStrs/10
        self.chmFront = scaleLen - self.fretbdLen - wallTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        bodyBackLen = self.chmBack + wallTck + tnrType.tailAllow()
        self.tailX = scaleLen + bodyBackLen
        # tnrType.is_peg() = isinstance(tnrType, PegConfig)
        # self.isWorm = isinstance(tnrType, WormConfig)
        # self.numStrs = numStrs
        # self.nutStrGap = nutStrGap
        self.nutWth = max(2,numStrs) * nutStrGap
        if tnrType.is_peg():
            tnrSetback = tnrType.tailAllow()/2 - 3.1
            self.neckWideAng = self.MIN_NECK_WIDE_ANG
            self.tnrGap = tnrType.minGap()
        else:
            tnrSetback = tnrType.tailAllow()/2 + 1
            tnrX = scaleLen + bodyBackLen - tnrSetback
            tnrW = tnrType.minGap() * numStrs
            tnrNeckWideAng = degrees(atan((tnrW - self.nutWth)/2/tnrX))
            self.neckWideAng = max(self.MIN_NECK_WIDE_ANG, tnrNeckWideAng)
            tnrsWth = self.nutWth + 2*tnrX*tan(radians(self.neckWideAng))
            self.tnrGap = tnrsWth / numStrs

        # self.half = half
        # self.sepTop = sepTop
        # self.sepNeck = sepNeck
        # self.sepFretbd = sepFretbd
        # self.sepBrdg = sepBrdg
        # self.sepEnd = sepEnd
        # self.modelLbl = modelLbl
        isOddStrs = numStrs % 2 == 1
        # self.endWth = endWth
        # self.action = action
        self.brdgWth = nutStrGap*(max(2,numStrs)-.5) + \
            2 * tan(radians(self.neckWideAng)) * scaleLen
        brdgStrGap = self.brdgWth / (numStrs-.5)

        self.neckLen = scaleLen * self.NECK_RATIO
        # self.dotRad = dotRad
        # self.fret2Dots = fret2Dots
        # self.extMidTopTck = self.extMidTopTck
        self.extMidBotTck = max(0, 10 - numStrs**1.25)

        # Neck configs
        self.neckWth = self.nutWth + \
            2 * tan(radians(self.neckWideAng)) * self.neckLen
        # self.neckOrig = (0, 0)
        self.neckPath = [
            (0, self.nutWth/2), 
            (self.neckLen, self.neckWth/2),
            (self.neckLen, -self.neckWth/2), 
            (0, -self.nutWth/2)
        ]
        self.neckJntLen = self.NECK_JNT_RATIO*(self.fretbdLen - self.neckLen)
        self.neckJntTck = self.FRETBD_SPINE_TCK + self.SPINE_HT
        self.neckJntWth = (1 if isOddStrs else 2)*nutStrGap + self.SPINE_WTH
        neckDX = 1
        neckDY = neckDX * tan(radians(self.neckWideAng))

        # Fretboard configs
        self.fretbdWth = self.nutWth + \
            2 * tan(radians(self.neckWideAng)) * self.fretbdLen
        self.fretbdHt = self.FRETBD_TCK + \
            tan(radians(self.fretbdRiseAng)) * self.fretbdLen

        # self.fbOrig = (0, 0)
        # self.fbPath = genFbPath()
        # self.fbCutOrig = (-FIT_TOL, 0)
        # self.fbCutPath = genFbPath(isCut=True)
        # self.fbSpX = self.NUT_HT
        # self.fbSpineLen = self.neckLen - self.NUT_HT + self.neckJntLen

        # Chamber Configs
        # self.chmLift = chmLift
        # self.chmRot = chmRot
        # self.chmWth = self.brdgWth * 3
        self.chmWth = self.brdgWth if self.cli.body_type==LeleBodyType.TRAVEL else self.brdgWth * self.CHM_BRDG_RATIO
        self.rimWth = wallTck/2

        # Head configs
        self.headLen = 2 * numStrs + scaleLen / 60 #12
        self.headWth = self.nutWth * self.HEAD_WTH_RATIO
        headDX = 1
        headDY = headDX * tan(radians(self.neckWideAng))
        self.headOrig = (0, 0)
        self.headPath = [
            (0, self.nutWth/2),
            [
                (-headDX, self.nutWth/2 + headDY, headDY/headDX),
                (-self.headLen/2, self.headWth/2, 0),
                (-self.headLen, self.headWth/6, -inf),
            ],
            (-self.headLen, 0),
        ]

        # Body Configs
        self.bodyWth = self.chmWth + 2*wallTck
        self.bodyFrontLen = scaleLen - self.neckLen
        # bodyLen = bodyFrontLen + bodyBackLen
        # self.fullLen = self.HEAD_LEN + scaleLen + bodyLen
        self.bodyOrig = (self.neckLen, 0)
        def genBodyPath(isCut: bool = False) -> list[tuple[float, float, float, float]]:
            cutAdj = FIT_TOL if isCut else 0
            nkLen = self.neckLen
            nkWth = self.neckWth + 2*cutAdj
            bWth = self.bodyWth + 2*cutAdj
            bFrLen = self.bodyFrontLen + cutAdj
            bBkLen = bodyBackLen + cutAdj
            eWth = min(bWth, endWth) + (2*cutAdj if endWth > 0 else 0)
            endFactor = sqrt(endWth/bWth)
            bodySpline = [
                (nkLen + neckDX, nkWth/2 + neckDY, neckDY/neckDX, .5, .3),
                (scaleLen, bWth/2, 0, .6),
                (scaleLen + bBkLen, eWth/2 +.1, -inf, (1-eWth/bWth)/2),
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
        # self.bodyCutOrig = (self.neckLen - FIT_TOL, 0)
        self.bodyCutPath = genBodyPath(isCut=True)

        # Bridge configs
        f12Len = scaleLen/2
        f12Ht = self.FRETBD_TCK \
            + tan(radians(self.fretbdRiseAng)) * f12Len \
            + self.FRET_HT
        self.brdgZ = self.bodyWth/2 * self.TOP_RATIO + self.extMidTopTck - 1.5
        self.brdgHt = 2*(f12Ht + action - self.NUT_HT - self.STR_RAD/2) \
            - self.brdgZ
        self.brdgLen = nutStrGap

        # Spine configs
        self.spineX = self.headLen
        self.spineLen = self.headLen + scaleLen + self.chmBack + self.rimWth
        self.spineGap = 0 if numStrs == 2 else (1 if isOddStrs else 2)*nutStrGap
        self.spineY1 = -self.spineGap/2
        self.spineY2 = self.spineGap/2

        # Guide config (Only for Pegs)
        self.guideHt = 6 + numStrs/2
        self.guideX = scaleLen + .95*self.chmBack
        self.guideZ = -self.GUIDE_SET \
            + self.TOP_RATIO * sqrt(bodyBackLen**2 - self.chmBack**2)
        self.guideWth = self.nutWth \
            + 2*tan(radians(self.neckWideAng))*self.guideX
        gGap = self.guideWth/numStrs
        self.guidePostGap = gGap
        gGapAdj = self.GUIDE_RAD

        # start calc from middle out
        gY = gGapAdj if isOddStrs else gGap/2 + gGapAdj
        self.guideYs = [gGapAdj +2*self.STR_RAD, -gGapAdj -2*self.STR_RAD] \
            if isOddStrs else [gY + self.STR_RAD, -gY - self.STR_RAD]
        for _ in range((numStrs-1)//2):
            gY += gGap
            self.guideYs.extend([gY + gGapAdj, -gY -gGapAdj])

        # Tuner config
        # approx spline bout curve with ellipse but 'fatter'
        tXMax = bodyBackLen - tnrSetback
        fatRat = .65 if endWth == 0 else .505 + (endWth/self.bodyWth)**1.05
        tYMax = fatRat*self.bodyWth - tnrSetback
        tX = tXMax
        tY = 0

        if tnrType.is_peg():
            tZBase = (self.extMidTopTck + 2)
        elif tnrType.is_worm():
            tZBase = (-tnrType.driveRad - tnrType.diskRad - tnrType.axleRad)
        else:
            assert False, f'Unsupported Tuner Type {tnrType}'

        tMidZ = tZBase + tzAdj(tY, tnrType=tnrType, endWth=endWth, top_ratio=self.TOP_RATIO)
        tZ = tMidZ
        tDist = self.tnrGap
        # start calc from middle out
        self.tnrXYZs = [(scaleLen + tX, 0, tZ)] if isOddStrs else []
        for p in range(numStrs//2):
            if tY + tDist < endWth/2:
                tY += tDist if isOddStrs or p > 0 else tDist/2
                # tX remain same
                tZ = tZBase + tzAdj(tY, tnrType=tnrType, endWth=endWth, top_ratio=self.TOP_RATIO)
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
                tY = tY + (tDist if isOddStrs or p > 0 else tDist/2) \
                    / sqrt(1 + tXMax**2 * tY**2 / (tYMax**2 * (tYMax**2 - tY**2)))
                tX = tXMax * sqrt(1 - tY**2/tYMax**2)
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

        if tnrType.is_peg():  # Worm drives has no string guide
            strOddMidPath.append(
                (self.guideX, 0,
                 self.guideZ + self.guideHt - self.GUIDE_RAD - self.STR_RAD)
            )

        strOddMidPath.append(
            (scaleLen + bodyBackLen - tnrSetback, 0,
             tMidZ + tnrType.holeHt)
        )

        strEvenMidPathR = []
        strEvenMidPathL = []
        strEvenMidBrdgDY = brdgStrGap/2 - nutStrGap/2
        strEvenMidAng = atan(strEvenMidBrdgDY/scaleLen)

        # even middle string pair points is just odd middle string points with DY
        # following same widening angle except ending point uing pegY and pegZ + peg hole height
        for pt in strOddMidPath:
            strY = (self.tnrGap/2) if pt == strOddMidPath[-1] \
                else nutStrGap/2 + pt[0]*tan(strEvenMidAng)
            strZ = (
                tZBase + tnrType.holeHt) if pt == strOddMidPath[-1] else pt[2]
            strEvenMidPathR.append((pt[0], strY, strZ))
            strEvenMidPathL.append((pt[0], -strY, strZ))

        # add initial middle string if odd else middle string pairs
        self.stringPaths = [strOddMidPath] if isOddStrs \
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
                        2*si + (1 if isOddStrs else 2)
                    ]
                    strX = strPegXYZ[0]
                    strY = strPegXYZ[1]
                    strZ = strPegXYZ[2] + tnrType.holeHt
                else:
                    strBrdgDY = (strCnt + (0 if isOddStrs else .5))\
                        * (brdgStrGap - nutStrGap)
                    strEvenAng = atan(strBrdgDY/scaleLen)
                    strX = pt[0]
                    strY = nutStrGap*(strCnt + (0 if isOddStrs else .5))\
                        + strX*tan(strEvenAng)
                    strZ = pt[2]
                strPathR.append((strX, strY, strZ))
                strPathL.append((strX, -strY, strZ))
            self.stringPaths.append(strPathR)
            self.stringPaths.append(strPathL)

    """
    def genModelStr(self, inclDate: bool = False) -> str:
        model = f"{self.scaleLen}{tnrType.code}{self.numStrs}"
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
    """

    def __repr__(self):
        class_vars_str = '\n'.join(f"{key}={value!r}" for key, value in self.__class__.__dict__.items() \
                if not callable(value) and not key.startswith("__"))
        instance_vars_str = '\n'.join(f"{key}={value!r}" for key, value in vars(self).items())
        return f"{self.__class__.__name__}\n{class_vars_str}\n{instance_vars_str}"

def main():
    """ Pylele Configuration """
    parser = pylele_config_parser()
    cli = parser.parse_args()

    if not cli.configuration is None:
        # print(AttrDict(vars(cli)))
        cli = parser.parse_args(args=CONFIGURATIONS[cli.configuration])

    print(AttrDict(vars(cli)))
    cfg = LeleConfig(cli=cli)
    # print(cfg)
    return cfg

if __name__ == '__main__':
    main()
