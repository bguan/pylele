#!/usr/bin/env python3

""" Pylele Configuration Module """

import argparse
from math import atan, inf, sqrt, tan

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from b13d.api.core import Fidelity, Implementation, StringEnum
from b13d.api.utils import radians, degrees, accumDiv
from b13d.api.constants import FIT_TOL, FILLET_RAD, ColorEnum
from pylele.config_common import SEMI_RATIO, LeleScaleEnum, TunerConfig, PegConfig, WormConfig, TunerType

DEFAULT_FLAT_BODY_THICKNESS=25

class LeleBodyType(StringEnum):
    """ Body Type """
    GOURD = 'gourd'
    FLAT  = 'flat'
    HOLLOW = 'hollow'
    TRAVEL = 'travel'

WORM    = ['-t','worm'   ,'-e','90','-wah','-wsl','35']
BIGWORM = ['-t','bigworm','-e','125','-wah','-wsl','35','-fbt','35']

CONFIGURATIONS = {
        'default'        : [],
        'worm'           : WORM    , # gourd
        'flat'           : WORM    + ['-bt', LeleBodyType.FLAT],
        'hollow'         : BIGWORM + ['-bt', LeleBodyType.HOLLOW],
        'travel'         : BIGWORM + ['-bt', LeleBodyType.TRAVEL,'-wt','25']
    }

class AttrDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

def tzAdj(tY: float, tnrType: TunerType, endWth: float, top_ratio: float) -> float:
    """ Adjust Tuner Z """
    return 0 if tnrType.is_worm() or tY > endWth/2 \
        else (((endWth/2)**2 - tY**2)**.5 * top_ratio/2 + .5)

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
    parser.add_argument("-g", "--nut_string_gap", help="Strings gap at nut [mm], default 9",
                        type=float, default=9)
    parser.add_argument("-e", "--end_flat_width", help="Flat width at tail end [mm], default 0",
                        type=float, default=0)
    parser.add_argument("-nsp", "--num_spines", help="Number of neck spines",
                        type=int, default=3, choices=[*range(4)])
    parser.add_argument("-mnwa", "--min_neck_wide_angle", help="Minimum Neck Widening angle [deg]",
                        type=float, default=1.2)

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

    parser.add_argument("-wt", "--wall_thickness", help="Chamber Wall Thickness [mm], default 4",
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

    return parser


class LeleConfig:
    """ Pylele Configuration Class """
    TOP_HEAD_RATIO = 1/6
    TOP_RATIO = 1/8
    BOT_RATIO = 2/3
    CHM_BACK_RATIO = 1/2 # to chmFront
    CHM_BRDG_RATIO = 3  # to chmWth
    EMBOSS_DEP = .5
    FRET_HT = 1
    FRETBD_RATIO = 0.635  # to scaleLen
    FRETBD_SPINE_TCK = 2
    FRETBD_TCK = 2
    GUIDE_RAD = 1.55
    GUIDE_SET = 0
    HEAD_WTH_RATIO = 1.1  # to nutWth
    # MIN_NECK_WIDE_ANG = 1.2
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
        Solid Command Line Interface
        """
        return pylele_config_parser(parser=parser)

    def parse_args(self, args=None):
        """ Parse Command Line Arguments """
        return self.gen_parser().parse_args(args=args)

    def is_odd_strs(self) -> bool:
        return self.cli.num_strings % 2 == 1

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
        self.tolerance = self.cli.implementation.tolerance()
        tnrType=TunerType[self.cli.tuner_type].value

        # Length based configs
        self.fretbdLen = scaleLen * self.FRETBD_RATIO
        self.fretbdRiseAng = 1 + numStrs/10
        self.chmFront = scaleLen - self.fretbdLen - wallTck
        self.chmBack = self.CHM_BACK_RATIO * self.chmFront
        (tnrFront, tnrBack, _, _, _, _) = tnrType.dims()
        bodyBackLen = self.chmBack + wallTck + tnrFront + tnrBack
        self.bodyBackLen = bodyBackLen
        self.tailX = scaleLen + bodyBackLen
        self.nutWth = max(2,numStrs) * nutStrGap
        tnrSetback = tnrType.tailAllow()
        if tnrType.is_peg():
            self.neckWideAng = self.cli.min_neck_wide_angle
            self.tnrGap = tnrType.minGap()
        else:
            tnrX = scaleLen + bodyBackLen - tnrSetback
            tnrW = tnrType.minGap() * numStrs
            tnrNeckWideAng = degrees(atan((tnrW - self.nutWth)/2/tnrX))
            self.neckWideAng = max(self.cli.min_neck_wide_angle, tnrNeckWideAng)
            tnrsWth = self.nutWth + 2*tnrX*tan(radians(self.neckWideAng))
            self.tnrGap = tnrsWth / numStrs

        self.brdgWth = nutStrGap*(max(2,numStrs)-.5) + \
            2 * tan(radians(self.neckWideAng)) * scaleLen
        brdgStrGap = self.brdgWth / (numStrs-.5)

        self.neckLen = scaleLen * self.NECK_RATIO
        self.extMidBotTck = max(0, 10 - numStrs**1.25)

        # Neck configs
        self.neckWth = self.nutWth + \
            2 * tan(radians(self.neckWideAng)) * self.neckLen

        # Fretboard configs
        self.fretbdWth = self.nutWth + \
            2 * tan(radians(self.neckWideAng)) * self.fretbdLen
        self.fretbdHt = self.FRETBD_TCK + \
            tan(radians(self.fretbdRiseAng)) * self.fretbdLen

        # Chamber Configs
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

        # Bridge configs
        f12Len = scaleLen/2
        f12Ht = self.FRETBD_TCK \
            + tan(radians(self.fretbdRiseAng)) * f12Len \
            + self.FRET_HT
        self.brdgZ = self.bodyWth/2 * self.TOP_RATIO + self.extMidTopTck - 1.5
        self.brdgHt = 2*(f12Ht + action - self.NUT_HT - self.STR_RAD/2) \
            - self.brdgZ
        self.brdgLen = nutStrGap

        # Guide config (Only for Pegs)
        self.guideHt = 6 + numStrs/2
        self.guideX = scaleLen + .95*self.chmBack
        self.guideZ = -self.GUIDE_SET \
            + self.TOP_RATIO * sqrt(bodyBackLen**2 - self.chmBack**2)
        self.guideWth = self.nutWth \
            + 2*tan(radians(self.neckWideAng))*self.guideX+ 2*self.GUIDE_RAD
        gGap = self.guideWth/numStrs
        self.guidePostGap = gGap
        gGapAdj = self.GUIDE_RAD

        # start calc from middle out
        gY = gGapAdj if self.is_odd_strs() else gGap/2 + gGapAdj + .5*self.STR_RAD
        self.guideYs = [gGapAdj +2*self.STR_RAD, -gGapAdj -2*self.STR_RAD] \
            if self.is_odd_strs() else [gY + self.STR_RAD, -gY - self.STR_RAD]
        for _ in range((numStrs-1)//2):
            gY += gGap
            self.guideYs.extend([gY + gGapAdj, -gY -gGapAdj])

        # Tuner config
        # approx spline bout curve with ellipse but 'fatter'
        tXMax = bodyBackLen - tnrSetback
        fatRat = .7 + (endWth/self.bodyWth)/2
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
        self.tnrXYZs = [(scaleLen + tX, 0, tZ)] if self.is_odd_strs() else []
        for p in range(numStrs//2):
            if tY + tDist < endWth/2:
                tY += tDist if self.is_odd_strs() or p > 0 else tDist/2
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
                tY = tY + (tDist if self.is_odd_strs() or p > 0 else tDist/2) \
                    / sqrt(1 + tXMax**2 * tY**2 / (tYMax**2 * (tYMax**2 - tY**2)))
                tX = tXMax * sqrt(1 - tY**2/tYMax**2)
                tZ = tZBase

            self.tnrXYZs.extend(
                [(scaleLen + tX, tY, tZ), (scaleLen + tX, -tY, tZ)],
            )

        # Strings config
        strOddMidPath = [
            (-self.headLen, 0, -self.FRETBD_SPINE_TCK - .2*self.SPINE_HT),
            (0, 0, self.FRETBD_TCK + self.NUT_HT + self.STR_RAD/2),
            (scaleLen, 0, self.brdgZ + self.brdgHt + 1.5*self.STR_RAD),
        ]

        if tnrType.is_peg():  # Worm drives has no string guide
            strOddMidPath.append(
                (self.guideX, 0,
                 self.guideZ + self.guideHt - self.GUIDE_RAD - 1.5*self.STR_RAD)
            )

        strOddMidPath.append(
            (scaleLen + bodyBackLen - tnrSetback, 0,
             tMidZ + tnrType.strHt())
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
                tZBase + tnrType.strHt()) if pt == strOddMidPath[-1] else pt[2]
            strEvenMidPathR.append((pt[0], strY, strZ))
            strEvenMidPathL.append((pt[0], -strY, strZ))

        # add initial middle string if odd else middle string pairs
        self.stringPaths = [strOddMidPath] if self.is_odd_strs() \
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
                        2*si + (1 if self.is_odd_strs() else 2)
                    ]
                    strX = strPegXYZ[0]
                    strY = strPegXYZ[1]
                    strZ = strPegXYZ[2] + tnrType.strHt()
                else:
                    strBrdgDY = (strCnt + (0 if self.is_odd_strs() else .5))\
                        * (brdgStrGap - nutStrGap)
                    strEvenAng = atan(strBrdgDY/scaleLen)
                    strX = pt[0]
                    strY = nutStrGap*(strCnt + (0 if self.is_odd_strs() else .5))\
                        + strX*tan(strEvenAng)
                    strZ = pt[2]
                strPathR.append((strX, strY, strZ))
                strPathL.append((strX, -strY, strZ))
            self.stringPaths.append(strPathR)
            self.stringPaths.append(strPathL)

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
