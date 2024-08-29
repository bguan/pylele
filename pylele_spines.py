#!/usr/bin/env python3

"""
    Pylele Spines
"""

import os
from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

class LeleSpines(LeleBase):
    """ Pylele Spines Generator class """

    def gen(self) -> Shape:
        """ Generate Spines """

        cutAdj = (FIT_TOL + self.cfg.joinCutTol) if self.isCut else 0
        spX = self.cfg.spineX
        spLen = self.cfg.spineLen+ 2*cutAdj
        spY1 = self.cfg.spineY1
        spY2 = self.cfg.spineY2
        spHt = self.cfg.SPINE_HT + 2*cutAdj
        spWth = self.cfg.SPINE_WTH + 2*cutAdj
        fspTck = self.cfg.FRETBD_SPINE_TCK  + 2*self.cfg.joinCutTol

        sp1 = self.api.genBox(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY1, -fspTck - spHt/2)
        sp2 = self.api.genBox(spLen, spWth, spHt)\
            .mv(spX + spLen/2, spY2, -fspTck - spHt/2)
        
        self.shape = sp1.join(sp2)
        return self.shape

def spines_main(args = None):
    """ Generate Spines """
    solid = LeleSpines(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_spines():
    """ Test Spines """

    component = 'spines'

    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender'],
        'trimesh' : ['-i','trimesh'],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        spines_main(args=args)

if __name__ == '__main__':
    spines_main()
