#!/usr/bin/env python3

"""
    Pylele Rim
"""

import os
from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

class LeleRim(LeleBase):
    """ Pylele Rim Generator class """

    def gen(self) -> Shape:
        """ Generate Rim """
        joinTol = self.cfg.joinCutTol
        cutAdj = (FIT_TOL + joinTol) if self.isCut else 0
        scLen = self.cfg.scaleLen
        rad = self.cfg.chmWth/2 + self.cfg.rimWth
        tck = self.cfg.RIM_TCK + 2*cutAdj
        frontWthRatio = (self.cfg.chmFront + self.cfg.rimWth)/rad
        backWthRatio = (self.cfg.chmBack + self.cfg.rimWth)/rad
        rimFront = self.api.genHalfDisc(rad, True, tck).scale(frontWthRatio, 1, 1)
        rimBack = self.api.genHalfDisc(rad, False, tck).scale(backWthRatio, 1, 1)
        rimFront.mv(scLen, 0, joinTol-tck/2).join(rimBack.mv(scLen-joinTol, 0, joinTol-tck/2))

        self.shape = rimFront
        return rimFront

def rim_main(args=None):
    """ Generate Rim """
    solid = LeleRim(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_rim():
    """ Test Rim """

    component = 'rim'
    tests = {
        'cut'     : ['-C'],
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender'],
        'trimesh' : ['-i','trimesh'],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        rim_main(args=args)


if __name__ == '__main__':
    rim_main()
