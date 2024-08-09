#!/usr/bin/env python3

"""
    Pylele Fretboard Spines
"""

import os
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

def fretboard_spines_main(args = None):
    """ Generate Fretboard Spines """
    solid = LeleFretboardSpines(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_fretboard_spines():
    """ Test Fretoard Spines """

    component = 'fretboard_spines'

    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        fretboard_spines_main(args=args)

if __name__ == '__main__':
    fretboard_spines_main()
