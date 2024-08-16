#!/usr/bin/env python3

"""
    Pylele Frets
"""

import os
import math
import sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, LeleStrEnum, FIT_TOL, SEMI_RATIO
from api.pylele_utils import radians, accumDiv

FRET_WIRE_WIDTH=0.5

class FretType(LeleStrEnum):
    """ Pylele Fret Type """
    PRINT = 'print'
    NAIL = 'nail'
    WIRE = 'wire'

def pylele_frets_parser(parser = None):
    """
    Pylele Fret Assembly Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Fret Configuration')

    parser.add_argument("-ft", "--fret_type",
                    help="Fret Type",
                    type=FretType,
                    choices=list(FretType),
                    default=FretType.PRINT
                    )
    return parser

class LeleFrets(LeleBase):
    """ Pylele Frets Generator class """

    def gen(self) -> Shape:
        """ Generate Frets """

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
        riseAng = self.cfg.fretbdRiseAng
        f0X = -fitTol if self.isCut else 0

        if False:
            # zero-fret
            f0Top = self.api.genRndRodY(ntWth, ntHt, 1/4)
            f0TopCut = self.api.genBox(2*ntHt, 2*ntWth, fbTck).mv(0, 0, -fbTck/2)
            f0Top = f0Top.cut(f0TopCut).mv(f0X, 0, fbTck)
            f0Bot = self.api.genRndRodY(ntWth, ntHt, 1/4)
            f0BotCut = self.api.genBox(2*ntHt, 2*ntWth, fbTck).mv(0, 0, fbTck/2)
            f0Bot = f0Bot.cut(f0BotCut).scale(1, 1, fbTck/ntHt).mv(f0X, 0, fbTck)
            frets = f0Top.join(f0Bot)
        else:
            frets =  None

        # Not generating frets, if they are cut ?
        fx = 0
        gap = (scLen / 2) / accumDiv(1, 12, SEMI_RATIO)
        count = 0
        while (fx < (fbLen - gap - 2 * fHt)):
            fx = fx + gap
            fy = fWth / 2 + math.tan(radians(wideAng)) * fx
            fz = fbTck + math.tan(radians(riseAng)) * fx
            if self.cli.fret_type == FretType.WIRE:
                fret = self.api.genBox(FRET_WIRE_WIDTH, 2*fy, fHt).mv(fx, 0, fz)
            else:
                fret = self.api.genRodY(2 * fy, fHt).mv(fx, 0, fz)
            if frets is None:
                frets = fret
            else:
                frets = frets.join(fret)
            gap = gap / SEMI_RATIO
            count += 1
            if (count > maxFrets):  # prevent runaway loop
                break

        self.shape = frets
        return frets

    def gen_parser(self, parser=None):
        """  Generate Fret Parser """
        parser=pylele_frets_parser(parser=parser)
        return super().gen_parser(parser=parser)

def main(args = None):
    """ Generate Frets """
    return main_maker(module_name=__name__,
                    class_name='LeleFrets',
                    args=args)

def test_frets():
    """ Test Frets """
    tests = {
        'wire' : ['-ft','wire']
    }
    test_loop(module=__name__)

if __name__ == '__main__':
    main()