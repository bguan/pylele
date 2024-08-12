#!/usr/bin/env python3

"""
    Pylele Fretboard Joint
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase
from pylele1.pylele_config import FIT_TOL

class LeleFretboardJoint(LeleBase):
    """ Pylele Fretboard Joint Generator class """

    def gen(self) -> Shape:
        """ Generate Fretboard Joint """

        cutAdj = (FIT_TOL + self.cfg.joinCutTol) if self.isCut else 0
        fbHt = self.cfg.fretbdHt
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj # to align with spine cuts
        jntTck = .8*fbHt + 2*cutAdj
        jnt = self.api.genBox(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, jntTck/2)
        self.shape = jnt
        return jnt

def fretboard_joint_main(args=None):
    """ Generate Fretboard Joint """
    solid = LeleFretboardJoint(args=args)
    solid.export_args() # from cli
    solid.export_configuration()
    solid.exportSTL()
    return solid

def test_fretboard_joint():
    """ Test Fretoard Joint """

    component = 'fretboard_joint'
    tests = {
            'cadquery': ['-i','cadquery'],
            'blender' : ['-i','blender']
        }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        fretboard_joint_main(args=args)

if __name__ == '__main__':
    fretboard_joint_main()
