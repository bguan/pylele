#!/usr/bin/env python3

"""
    Pylele Fretboard Spines
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL

class LeleFretboardSpines(LeleBase):
    """ Pylele Fretboard Spines Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard Spines """

        cutAdj = FIT_TOL if self.isCut else 0
        fspTck = self.cfg.FRETBD_SPINE_TCK + 2*(self.api.getJoinCutTol() if self.isCut else 0)
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spWth = self.cfg.SPINE_WTH + 2*cutAdj # to align with spine cuts
        fspLen = self.cfg.fbSpineLen + 2*cutAdj + 2*(self.api.getJoinCutTol() if self.isCut else 0)
        # fspX = self.cfg.fbSpX
        fspX = self.cfg.NUT_HT

        fsp1 = self.api.genBox(fspLen, spWth, fspTck)\
            .mv(fspX + fspLen/2 - 2*cutAdj, spY1, -fspTck/2)
        fsp2 = self.api.genBox(fspLen, spWth, fspTck)\
            .mv(fspX + fspLen/2 - 2*cutAdj, spY2, -fspTck/2)
        
        self.shape = fsp1.join(fsp2)
        return self.shape

def main(args = None):
    """ Generate Fretboard Spines """
    return main_maker(module_name=__name__,
                    class_name='LeleFretboardSpines',
                    args=args)

def test_fretboard_spines():
    """ Test Fretoard Spines """
    test_loop(module=__name__)

if __name__ == '__main__':
    main()
