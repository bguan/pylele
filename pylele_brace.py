#!/usr/bin/env python3

"""
    Pylele Brace
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase
class LeleBrace(LeleBase):
    """ Pylele Brace Generator class """

    def gen(self) -> Shape:
        """ Generate Brace """

        scLen = self.cfg.scaleLen
        brdgZ = self.cfg.brdgZ
        chmFr = self.cfg.chmFront
        chmBk = self.cfg.chmBack
        chmWth = self.cfg.chmWth
        topRat = self.cfg.TOP_RATIO
        brace = self.api.genRndRodX(.5*(chmFr+chmBk), .4*chmWth*topRat, 1)\
            .scale(1, .25, 1)\
            .mv(scLen - .25*chmBk, 0, brdgZ)
        
        self.shape = brace

        return brace

def brace_main(args = None):
    """ Generate Brace """
    solid = LeleBrace(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_brace():
    """ Test Brace """

    component = 'brace'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        brace_main(args=args)

if __name__ == '__main__':
    brace_main()
