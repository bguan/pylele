#!/usr/bin/env python3

"""
    Pylele Neck Joint
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from api.pylele_api import Shape
from pylele2.pylele_base import LeleBase, test_loop, main_maker, FIT_TOL

class LeleNeckJoint(LeleBase):
    """ Pylele Neck Joint Generator class """

    def gen(self) -> Shape:
        """ Generate Neck Joint """
        cutAdj = (FIT_TOL + self.api.getJoinCutTol()) if self.isCut else 0
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj
        jntTck = self.cfg.neckJntTck + 2*FIT_TOL + 2*self.api.getJoinCutTol() # to match cut grooves for spines
        jnt = self.api.genBox(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, -jntTck/2)

        self.shape = jnt
        return jnt

def main(args = None):
    """ Generate Neck Joint """
    return main_maker(module_name=__name__,
                    class_name='LeleNeckJoint',
                    args=args)

def test_neck_joint(self,apis=None):
    """ Test neck_joint """
    test_loop(module=__name__,apis=apis)

def test_neck_joint_mock(self):
    """ Test neck_joint """
    test_neck_joint(self,apis=['mock'])

if __name__ == '__main__':
    main()
