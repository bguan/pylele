#!/usr/bin/env python3

"""
    Pylele Fretboard Joint
"""

from pylele_api import Shape
from pylele_base import LeleBase
from pylele_config import FIT_TOL

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

def fretboard_joint_main():
    """ Generate Fretboard Joint """
    solid = LeleFretboardJoint()
    solid.export_configuration()
    solid.exportSTL()
    return solid

if __name__ == '__main__':
    fretboard_joint_main()
