#!/usr/bin/env python3

"""
    Pylele Neck Joint
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from pylele.api.core import Shape
from pylele.api.constants import FIT_TOL
from pylele.api.solid import main_maker, test_loop
from pylele.pylele2.base import LeleBase


class LeleNeckJoint(LeleBase):
    """Pylele Neck Joint Generator class"""

    def gen(self) -> Shape:
        """Generate Neck Joint"""
        cutAdj = (FIT_TOL + self.api.tolerance()) if self.isCut else 0
        nkLen = self.cfg.neckLen
        jntLen = self.cfg.neckJntLen + 2 * cutAdj
        jntWth = self.cfg.neckJntWth + 2 * cutAdj
        jntTck = (
            self.cfg.neckJntTck + 2 * FIT_TOL + 2 * self.api.tolerance()
        )  # to match cut grooves for spines
        jnt = self.api.box(jntLen, jntWth, jntTck).mv(
            nkLen + jntLen / 2, 0, -jntTck / 2
        )

        return jnt


def main(args=None):
    """Generate Neck Joint"""
    return main_maker(module_name=__name__, class_name="LeleNeckJoint", args=args)


def test_neck_joint(self, apis=None):
    """Test neck_joint"""
    test_loop(module=__name__, apis=apis)


def test_neck_joint_mock(self):
    """Test neck_joint"""
    test_neck_joint(self, apis=["mock"])


if __name__ == "__main__":
    main()
