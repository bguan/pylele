#!/usr/bin/env python3

"""
    Pylele Fretboard Spines
"""

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

class LeleFretboardSpines(LeleBase):
    """ Pylele Fretboard Spines Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard Spines """

        cutAdj = FIT_TOL if self.isCut else 0
        fspTck = self.cfg.FRETBD_SPINE_TCK + 2*(self.cfg.joinCutTol if self.isCut else 0)
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spWth = self.cfg.SPINE_WTH + 2*cutAdj # to align with spine cuts
        fspLen = self.cfg.fbSpineLen + 2*cutAdj + 2*(self.cfg.joinCutTol if self.isCut else 0)
        fspX = self.cfg.fbSpX

        fsp1 = self.api.genBox(fspLen, spWth, fspTck)\
            .mv(fspX + fspLen/2 - 2*cutAdj, spY1, -fspTck/2)
        fsp2 = self.api.genBox(fspLen, spWth, fspTck)\
            .mv(fspX + fspLen/2 - 2*cutAdj, spY2, -fspTck/2)
        
        self.shape = fsp1.join(fsp2)
        return self.shape

def top_fretboard_spines():
    """ Generate Fretboard Spines """
    solid = LeleFretboardSpines()
    solid.export_configuration()
    solid.exportSTL()
    return solid

if __name__ == '__main__':
    top_fretboard_spines()
