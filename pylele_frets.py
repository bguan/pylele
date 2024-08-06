#!/usr/bin/env python3

"""
    Pylele Frets
"""

import os
import math

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import accumDiv, FIT_TOL, SEMI_RATIO, Implementation
from pylele_utils import radians

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

def frets_main(args = None):
    """ Generate Frets """
    solid = LeleFrets(args=args)
    solid.export_args() # from cli
    
    solid.export_configuration()
    
    solid.exportSTL()
    return solid

def test_frets():
    """ Test Frets """

    component = 'frets'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        frets_main(args=args)

if __name__ == '__main__':
    frets_main()
