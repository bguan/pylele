#!/usr/bin/env python3

"""
    Pylele Fretboard Joint
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from b13d.api.core import Shape
from b13d.api.constants import FIT_TOL
from b13d.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase


class LeleFretboardJoint(LeleBase):
    """Pylele Fretboard Joint Generator class"""

    def gen(self) -> Shape:
        """Generate Fretboard Joint"""

        cutAdj = (FIT_TOL + self.api.tolerance()) if self.isCut else 0
        fbHt = self.cfg.fretbdHt
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2*cutAdj
        jntWth = self.cfg.neckJntWth + 2*cutAdj # to align with spine cuts
        jntTck = .8*fbHt + 2*cutAdj
        jnt = self.api.box(jntLen, jntWth, jntTck).mv(nkLen+jntLen/2, 0, jntTck/2)
        jntLen = self.cfg.neckJntLen + 2 * cutAdj
        jntWth = self.cfg.neckJntWth + 2 * cutAdj  # to align with spine cuts
        jntTck = 0.8 * fbHt + 2 * cutAdj
        jnt = self.api.box(jntLen, jntWth, jntTck).mv(
            nkLen + jntLen / 2, 0, jntTck / 2
        )
        self.shape = jnt
        return jnt


def main(args=None):
    """Generate Fretboard Joint"""
    return main_maker(module_name=__name__, class_name="LeleFretboardJoint", args=args)


def test_fretboard_joint(self, apis=None):
    """Test Fretoard Joint"""
    tests = {"default":["-refv","2556"]}
    test_loop(module=__name__, apis=apis, tests=tests)


def test_fretboard_joint_mock(self):
    """Test Fretoard Joint"""
    test_fretboard_joint(self, apis=["mock"])


if __name__ == "__main__":
    main()
