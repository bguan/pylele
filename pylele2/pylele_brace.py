#!/usr/bin/env python3

"""
    Pylele Brace
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker
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

def main(args = None):
    """ Generate Brace """
    return main_maker(module_name=__name__,
                    class_name='LeleBrace',
                    args=args)

def test_brace():
    """ Test Brace """
    test_loop(module=__name__)
    
if __name__ == '__main__':
    main()
