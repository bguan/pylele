#!/usr/bin/env python3

"""
    Pylele Spines
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL

class LeleSpines(LeleBase):
    """ Pylele Spines Generator class """

    def gen(self) -> Shape:
        """ Generate Spines """

        cutAdj = (FIT_TOL + self.api.getJoinCutTol()) if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen+ 2*cutAdj
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spHt = self.cfg.SPINE_HT + 2*cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK  + 2*self.api.getJoinCutTol()

        sp1 = self.api.genBox(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY1, -fspTck - spHt/2)
        sp2 = self.api.genBox(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY2, -fspTck - spHt/2)
        
        self.shape = sp1.join(sp2)
        return self.shape

def main(args = None):
    """ Generate Spines """
    return main_maker(module_name=__name__,
                    class_name='LeleSpines',
                    args=args)

def test_spines(self):
    """ Test Spines """
    test_loop(module=__name__)
    
def test_spines_mock(self):
    """ Test Spines """
    test_loop(module=__name__, apis=['mock'])

if __name__ == '__main__':
    main()
