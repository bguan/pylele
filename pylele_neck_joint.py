#!/usr/bin/env python3

"""
    Pylele Neck Joint
"""

import os

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

class LeleNeckJoint(LeleBase):
    """ Pylele Neck Joint Generator class """

    def gen(self) -> Shape:
        """ Generate Neck Joint """
        cutAdj = (FIT_TOL + self.cfg.joinCutTol) if self.isCut else 0
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj
        jntTck = self.cfg.neckJntTck + 2*FIT_TOL + 2*self.cfg.joinCutTol # to match cut grooves for spines
        jnt = self.api.genBox(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, -jntTck/2)

        self.shape = jnt
        return jnt

def neck_joint_main(args = None):
    """ Generate Neck Joint """
    solid = LeleNeckJoint(args=args)
    solid.export_args() # from cli    
    solid.export_configuration()    
    solid.exportSTL()
    return solid

def test_neck_joint():
    """ Test neck_joint """

    component = 'neck_joint'
    tests = {
        'cadquery': ['-i','cadquery'],
        'blender' : ['-i','blender']
    }

    for test,args in tests.items():
        print(f'# Test {component} {test}')
        outdir = os.path.join('./test',component,test)
        args += ['-o', outdir]
        neck_joint_main(args=args)

if __name__ == '__main__':
    neck_joint_main()
