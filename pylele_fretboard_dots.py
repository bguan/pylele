#!/usr/bin/env python3

"""
    Pylele Fretboard Dots
"""

import os
import math
import argparse

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import accumDiv, radians, SEMI_RATIO

def pylele_dots_parser(parser = None):
    """
    Pylele Dots Element Parser
    """
    if parser is None:
        parser = argparse.ArgumentParser(description='Pylele Configuration')

    parser.add_argument("-d", "--dot_frets",
                    help="Comma-separated fret[:dots] pairs, default 3,5:2,7,10,12:3,15,17:2,19,22",
                    type=lambda d: {
                        int(l[0]): 1 if len(l) < 2 else int(l[1])
                        for l in (fns.split(':') for fns in d.split(','))
                    },
                    default={3: 1, 5: 2, 7: 1, 10: 1, 12: 3, 15: 1, 17: 2, 19: 1, 22: 1})
    return parser

class LeleFretboardDots(LeleBase):
    """ Pylele Fretboard Dots Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard Dots """

        scLen = self.cfg.scaleLen
        fbLen = self.cfg.fretbdLen
        fbTck = self.cfg.FRETBD_TCK
        maxFrets = self.cfg.MAX_FRETS
        dep = self.cfg.EMBOSS_DEP
        wideAng = self.cfg.neckWideAng
        riseAng = self.cfg.fretbdRiseAng
        nutSGap = self.cfg.nutStrGap
        dotRad = self.cfg.dotRad
        fret2Dots = self.cfg.fret2Dots

        dots = None
        sgap = nutSGap
        # half length of fret 1
        flen = .5 * scLen / accumDiv(1, 12, SEMI_RATIO)
        n = 1
        acclen = flen
        while acclen < fbLen and n <= maxFrets:
            if n in fret2Dots:
                ht = fbTck + math.tan(radians(riseAng))*acclen
                pos = [0] if fret2Dots[n] == 1 \
                    else [-.5, .5] if fret2Dots[n] == 2 \
                    else [-1, 0, 1]
                for p in pos:
                    dot = self.api.genRodZ(
                        2 * dep, dotRad).mv(acclen - .5*flen, p*sgap, ht)
                    dots = dot if dots == None else dots.join(dot)

            sgap = .5 * acclen * math.tan(radians(wideAng)) + nutSGap
            flen /= SEMI_RATIO
            acclen += flen
            n += 1
    
        self.shape = dots
        return dots
    
    def gen_parser(self,parser=None):
        """
        pylele Command Line Interface
        """
        parser=pylele_dots_parser( parser=parser )
        return super().gen_parser( parser=parser )

def fretboard_dots_main(args = None):
    """ Generate Fretboard """
    solid = LeleFretboardDots(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_fretboard_dots():
    """ Test Fretoard dots """

    component = 'fretboard_dots'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        fretboard_dots_main(args=args)

if __name__ == '__main__':
    fretboard_dots_main()
