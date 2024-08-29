#!/usr/bin/env python3

"""
    Pylele Neck 
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase

class LeleNeck(LeleBase):
    """ Pylele Neck Generator class """

    def gen(self) -> Shape:
        """ Generate Neck """
        ntWth = self.cfg.nutWth
        nkLen = self.cfg.neckLen
        nkWth = self.cfg.neckWth
        midTck = self.cfg.extMidBotTck
        botRat = self.cfg.BOT_RATIO
        path = self.cfg.neckPath
        joinTol = self.cfg.joinCutTol
        neck = None
        if midTck > 0:
            neck = self.api.genPolyExtrusionZ(path, midTck).mv(0, 0, -midTck)
        neckCone = self.api.genConeX(nkLen, ntWth/2, nkWth/2)
        coneCut = self.api.genBox(2*nkLen, 2*nkWth, 2*nkWth).mv(nkLen, 0, nkWth)
        neckCone = neckCone.cut(coneCut).scale(1, 1, botRat).mv(0, 0, -midTck)
        neck = neckCone if neck == None else neck.join(neckCone)

        self.shape = neck
        return neck

def neck_main(args = None):
    """ Generate Neck """
    solid = LeleNeck(args=args)
    solid.export_args() # from cli
    solid.export_configuration()  
    solid.exportSTL()
    return solid

def test_neck():
    """ Test Neck """

    component = 'neck'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender'],
        'trimesh' : ['-i','trimesh'],
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        neck_main(args=args)

if __name__ == '__main__':
    neck_main()
